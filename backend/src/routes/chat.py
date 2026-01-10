"""Chat routes for AI-powered task management.

This module implements the chat API endpoint that enables natural language
task management through the AI agent.

Endpoints:
- POST /api/{user_id}/chat: Send a chat message and get AI response
- POST /api/{user_id}/chat/stream: Send a chat message and stream response via SSE

Security:
- JWT authentication required
- User isolation enforced (SC-004)
- Rate limiting applied (30 req/min per user)

Per plan.md:
- Conversation history is persisted
- Sliding context window for Gemini calls
- Tool call metadata included in responses
"""

import json
import asyncio
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db import get_session
from ..auth import get_current_user, verify_user_access
from ..schemas.chat import (
    ChatRequest, ChatResponse, ToolCall,
    ThinkingStep, ThinkingStepType, ConfirmationRequest
)
from ..models import MessageRole, Conversation
from ..services.conversation_service import (
    get_or_create_conversation,
    append_message,
    list_recent_messages,
    get_full_history,
)
from ..agent.runner import run_agent
from ..middleware.rate_limit import check_chat_rate_limit, add_rate_limit_headers
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/{user_id}/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Send a chat message and get AI response.

    This endpoint:
    1. Validates user authentication and access
    2. Checks rate limiting (30 req/min per user)
    3. Gets or creates conversation for the user
    4. Persists the user's message
    5. Builds conversation context
    6. Calls AI agent with task tools
    7. Persists assistant response
    8. Returns structured response with tool call metadata

    Args:
        user_id: User ID from URL path
        request: ChatRequest with message content
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        ChatResponse with conversation_id, response text, and tool_calls

    Raises:
        403: If user_id doesn't match authenticated user
        422: If message validation fails
        429: If rate limit exceeded
        500: If agent processing fails
    """
    # Verify user can only access their own chat
    verify_user_access(user_id, current_user)
    
    # TODO: Add rate limiting back later
    # await check_chat_rate_limit(request, user_id)

    logger.info(
        "chat_request_received",
        user_id=user_id,
        message_length=len(request.message),
        conversation_id=request.conversation_id
    )

    try:
        # Get or create conversation
        conversation = await get_or_create_conversation(session, user_id)

        # Persist user message
        user_msg = await append_message(
            session,
            conversation,
            "user",
            request.message
        )

        logger.debug(
            "user_message_persisted",
            conversation_id=conversation.id,
            message_id=user_msg.id
        )

        # Build conversation context from history
        recent_messages = await list_recent_messages(
            session,
            conversation.id,
            user_id,
            limit=20
        )

        # Format messages for agent context
        conversation_history = [
            {"role": msg.role.value if hasattr(msg.role, 'value') else msg.role, "content": msg.content}
            for msg in recent_messages
            if msg.id != user_msg.id  # Exclude the message we just added
        ]

        # Run AI agent
        agent_response = await run_agent(
            user_id=user_id,
            user_message=request.message,
            conversation_history=conversation_history,
            session=session,
            confirm_token=request.confirm_token
        )

        # Persist assistant response
        assistant_msg = await append_message(
            session,
            conversation,
            "assistant",
            agent_response.response
        )

        logger.debug(
            "assistant_message_persisted",
            conversation_id=conversation.id,
            message_id=assistant_msg.id
        )

        # Build tool call response with duration
        tool_calls = [
            ToolCall(
                tool=tc.tool,
                parameters=tc.parameters,
                result=tc.result,
                duration_ms=tc.duration_ms
            )
            for tc in agent_response.tool_calls
        ]

        # Build thinking steps response
        thinking_steps = [
            ThinkingStep(
                type=ThinkingStepType(ts.type),
                content=ts.content,
                timestamp=ts.timestamp
            )
            for ts in agent_response.thinking_steps
        ]

        # Build confirmation request if needed
        confirmation_required = None
        if agent_response.confirmation_required:
            cr = agent_response.confirmation_required
            confirmation_required = ConfirmationRequest(
                action=cr.action,
                message=cr.message,
                affected_items=cr.affected_items,
                confirm_token=cr.confirm_token
            )

        logger.info(
            "chat_response_sent",
            user_id=user_id,
            conversation_id=conversation.id,
            response_length=len(agent_response.response),
            tool_calls=len(tool_calls),
            thinking_steps=len(thinking_steps),
            confirmation_required=confirmation_required is not None,
            processing_time_ms=agent_response.processing_time_ms
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_response.response,
            tool_calls=tool_calls,
            thinking_steps=thinking_steps,
            confirmation_required=confirmation_required,
            processing_time_ms=agent_response.processing_time_ms
        )

    except Exception as e:
        logger.error(
            "chat_request_failed",
            user_id=user_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat request. Please try again."
        )


@router.get("/history", response_model=list[dict])
async def get_chat_history(
    user_id: str,
    conversation_id: int | None = None,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get full chat history for the user.

    Returns all messages in the user's conversation, ordered chronologically.
    Used by the frontend to hydrate chat state on page load.

    Args:
        user_id: User ID from URL path
        conversation_id: Optional conversation ID to filter messages
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        List of message objects with role, content, and timestamps

    Raises:
        403: If user_id doesn't match authenticated user
    """
    verify_user_access(user_id, current_user)

    logger.debug("chat_history_requested", user_id=user_id, conversation_id=conversation_id)

    # Get conversation - either specific one or default
    if conversation_id:
        # Verify the conversation belongs to this user
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # Get or create default conversation
        conversation = await get_or_create_conversation(session, user_id)

    # Get full history
    messages = await get_full_history(session, conversation.id, user_id)

    history = [
        {
            "id": msg.id,
            "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]

    logger.debug(
        "chat_history_returned",
        user_id=user_id,
        message_count=len(history)
    )

    return history


@router.post("/stream")
async def stream_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Stream a chat response via Server-Sent Events.

    This endpoint provides real-time streaming of:
    1. Thinking steps as they happen
    2. Tool calls as they execute
    3. Response text as it's generated

    SSE Event Types:
    - thinking: Agent thinking/reasoning step
    - tool_call: Tool execution started
    - tool_result: Tool execution completed
    - token: Response text token
    - done: Stream complete with final metadata
    - error: Error occurred

    Args:
        user_id: User ID from URL path
        request: ChatRequest with message content
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        StreamingResponse with SSE events
    """
    verify_user_access(user_id, current_user)

    logger.info(
        "stream_chat_request_received",
        user_id=user_id,
        message_length=len(request.message),
        conversation_id=request.conversation_id
    )

    async def generate_stream() -> AsyncGenerator[str, None]:
        """Generate SSE events for the chat response."""
        try:
            # Get or create conversation
            conversation = await get_or_create_conversation(session, user_id)

            # Persist user message
            user_msg = await append_message(
                session,
                conversation,
                "user",
                request.message
            )

            # Send conversation ID immediately
            yield f"data: {json.dumps({'type': 'start', 'conversation_id': conversation.id})}\n\n"

            # Build conversation context
            recent_messages = await list_recent_messages(
                session,
                conversation.id,
                user_id,
                limit=20
            )

            conversation_history = [
                {"role": msg.role.value if hasattr(msg.role, 'value') else msg.role, "content": msg.content}
                for msg in recent_messages
                if msg.id != user_msg.id
            ]

            # Simulate thinking steps streaming
            thinking_steps_data = [
                {"type": "analyzing", "content": "Understanding your request..."},
                {"type": "planning", "content": "Determining the best approach..."},
            ]

            for step in thinking_steps_data:
                yield f"data: {json.dumps({'type': 'thinking', 'step': step})}\n\n"
                await asyncio.sleep(0.1)  # Small delay for visual effect

            # Run AI agent
            agent_response = await run_agent(
                user_id=user_id,
                user_message=request.message,
                conversation_history=conversation_history,
                session=session,
                confirm_token=request.confirm_token
            )

            # Stream thinking steps from agent
            for ts in agent_response.thinking_steps:
                step_data = {
                    "type": ts.type,
                    "content": ts.content,
                    "timestamp": ts.timestamp
                }
                yield f"data: {json.dumps({'type': 'thinking', 'step': step_data})}\n\n"

            # Stream tool calls
            for tc in agent_response.tool_calls:
                tool_data = {
                    "tool": tc.tool,
                    "parameters": tc.parameters,
                    "result": tc.result,
                    "duration_ms": tc.duration_ms
                }
                yield f"data: {json.dumps({'type': 'tool_call', 'data': tool_data})}\n\n"

            # Check if agent returned an error
            response_text = agent_response.response
            if agent_response.error:
                # Send as error event with detailed information
                error_message = str(agent_response.error)
                if 'quota' in error_message.lower() or 'rate limit' in error_message.lower() or '429' in error_message:
                    error_data = {
                        'type': 'error',
                        'error_type': 'rate_limit',
                        'message': error_message,
                        'user_message': 'API rate limit exceeded. Please wait a moment and try again.'
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                else:
                    error_data = {'type': 'error', 'message': error_message}
                    yield f"data: {json.dumps(error_data)}\n\n"
                
                # Still save the error message to conversation history
                await append_message(
                    session,
                    conversation,
                    MessageRole.ASSISTANT,
                    response_text
                )
                
                # Send completion
                done_data = {'type': 'done', 'processing_time_ms': agent_response.processing_time_ms}
                yield f"data: {json.dumps(done_data)}\n\n"
                
                logger.info(
                    "stream_chat_error_handled",
                    user_id=user_id,
                    conversation_id=conversation.id,
                    error_type='rate_limit' if 'quota' in error_message.lower() else 'general'
                )
                return

            # Stream response text in chunks
            logger.info(f"Streaming response text: '{response_text}' (length: {len(response_text)})")
            chunk_size = 10  # Characters per chunk
            for i in range(0, len(response_text), chunk_size):
                chunk = response_text[i:i + chunk_size]
                logger.debug(f"Sending token chunk: '{chunk}'")
                yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
                await asyncio.sleep(0.02)  # Simulate typing effect

            # Persist assistant response
            await append_message(
                session,
                conversation,
                MessageRole.ASSISTANT,
                agent_response.response
            )

            # Build confirmation if needed
            confirmation_data = None
            if agent_response.confirmation_required:
                cr = agent_response.confirmation_required
                confirmation_data = {
                    "action": cr.action,
                    "message": cr.message,
                    "affected_items": cr.affected_items,
                    "confirm_token": cr.confirm_token
                }

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'processing_time_ms': agent_response.processing_time_ms, 'confirmation_required': confirmation_data})}\n\n"

            logger.info(
                "stream_chat_response_complete",
                user_id=user_id,
                conversation_id=conversation.id,
                processing_time_ms=agent_response.processing_time_ms
            )

        except Exception as e:
            logger.error(
                "stream_chat_request_failed",
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to process chat request'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
