"""ChatKit API route for the ChatKit Python SDK integration.

This route exposes a single /chatkit endpoint that:
1. Receives requests from ChatKit React frontend
2. Forwards them to our TodoChatKitServer
3. Returns streaming or non-streaming responses

The ChatKit frontend expects a specific request/response format
which the ChatKit Python SDK handles automatically.
"""

import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db import get_session
from src.auth import get_current_user
from src.chatkit import TodoChatKitStore, TodoChatKitServer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatkit", tags=["ChatKit"])

# Create store and server instances (singleton)
_store = TodoChatKitStore()
_server = TodoChatKitServer(store=_store)


@router.post("")
async def chatkit_endpoint(
    request: Request,
    conversation_id: int | None = None,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """ChatKit endpoint - handles all ChatKit protocol requests.

    The ChatKit Python SDK handles request parsing and response formatting.
    We just need to pass the raw body and provide context.

    Context includes:
    - session: Database session for store operations
    - user_id: Current user's ID for task isolation
    - conversation_id: Optional ID to load existing conversation

    The SDK routes requests to appropriate handlers:
    - threads.create: Create new thread with message
    - threads.browse: List threads
    - threads.load: Load a specific thread
    - threads.delete: Delete a thread
    - etc.
    """
    user_id = current_user["user_id"]

    # Build context for store operations
    context = {
        "session": session,
        "user_id": user_id,
        "conversation_id": conversation_id,  # Pass conversation_id for thread mapping
    }

    logger.info(f"ChatKit request from user {user_id}, conversation_id={conversation_id}")

    try:
        # Get raw request body
        body = await request.body()

        # Process through ChatKit server
        result = await _server.process(body, context=context)

        # Check if result is streaming
        if hasattr(result, "__aiter__"):
            # Streaming response
            async def stream_generator():
                async for chunk in result:
                    yield chunk

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )
        else:
            # Non-streaming response (JSON)
            if hasattr(result, "json"):
                return Response(
                    content=result.json,
                    media_type="application/json",
                )
            else:
                return Response(
                    content=str(result),
                    media_type="application/json",
                )

    except Exception as e:
        logger.error(f"ChatKit error: {e}", exc_info=True)
        return Response(
            content=f'{{"error": "{str(e)}"}}',
            status_code=500,
            media_type="application/json",
        )
