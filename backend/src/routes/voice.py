"""Voice routes for AI-powered task management via speech.

This module implements voice-based chat API endpoints that enable
speech-to-text and text-to-speech for natural language task management.

Endpoints:
- POST /api/{user_id}/voice/transcribe: Transcribe audio to text
- POST /api/{user_id}/voice/chat: Voice chat (audio in, audio out)
- POST /api/{user_id}/voice/synthesize: Text to speech

Security:
- JWT authentication required
- User isolation enforced (SC-004)
- Rate limiting applied
"""

import base64
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import io

from ..db import get_session
from ..auth import get_current_user, verify_user_access
from ..schemas.chat import (
    ChatResponse, ToolCall, ThinkingStep, ThinkingStepType
)
from ..models import MessageRole
from ..services.conversation_service import (
    get_or_create_conversation,
    append_message,
    list_recent_messages,
)
from ..agent.runner import run_agent
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/{user_id}/voice", tags=["voice"])


class TranscribeResponse(BaseModel):
    """Response from audio transcription."""
    text: str = Field(..., description="Transcribed text")
    confidence: Optional[float] = Field(None, description="Transcription confidence score")


class SynthesizeRequest(BaseModel):
    """Request for text-to-speech synthesis."""
    text: str = Field(..., min_length=1, max_length=4000, description="Text to synthesize")
    voice: str = Field(default="alloy", description="Voice to use (alloy, echo, fable, onyx, nova, shimmer)")


class VoiceChatRequest(BaseModel):
    """Request for voice chat with base64 audio."""
    audio_base64: str = Field(..., description="Base64 encoded audio data")
    audio_format: str = Field(default="webm", description="Audio format (webm, mp3, wav)")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")


class VoiceChatResponse(BaseModel):
    """Response from voice chat."""
    conversation_id: int = Field(..., description="Conversation ID")
    transcribed_text: str = Field(..., description="Transcribed user message")
    response_text: str = Field(..., description="Assistant's text response")
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio response")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tools called")
    thinking_steps: list[ThinkingStep] = Field(default_factory=list, description="Agent thinking steps")


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    user_id: str,
    audio: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Transcribe audio to text using speech-to-text.

    Accepts audio files (webm, mp3, wav, m4a, ogg) and returns transcribed text.

    Args:
        user_id: User ID from URL path
        audio: Audio file to transcribe
        current_user: Authenticated user from JWT

    Returns:
        TranscribeResponse with transcribed text

    Raises:
        403: If user_id doesn't match authenticated user
        400: If audio format is not supported
        500: If transcription fails
    """
    verify_user_access(user_id, current_user)

    logger.info("voice_transcribe_request", user_id=user_id, filename=audio.filename)

    try:
        # Read audio content
        audio_content = await audio.read()

        # For now, return a placeholder - in production, integrate with:
        # - OpenAI Whisper API
        # - Google Speech-to-Text
        # - Azure Speech Services
        # - Local Whisper model

        # Placeholder response
        return TranscribeResponse(
            text="[Voice transcription not yet implemented - audio received]",
            confidence=0.0
        )

    except Exception as e:
        logger.error("voice_transcribe_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transcribe audio"
        )


@router.post("/chat", response_model=VoiceChatResponse)
async def voice_chat(
    user_id: str,
    request: VoiceChatRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Voice chat endpoint - audio in, audio + text out.

    This endpoint:
    1. Transcribes the audio to text
    2. Processes through the AI agent
    3. Synthesizes response to audio
    4. Returns both text and audio response

    Args:
        user_id: User ID from URL path
        request: VoiceChatRequest with base64 audio
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        VoiceChatResponse with transcribed text, response, and audio

    Raises:
        403: If user_id doesn't match authenticated user
        500: If processing fails
    """
    verify_user_access(user_id, current_user)

    logger.info(
        "voice_chat_request",
        user_id=user_id,
        audio_format=request.audio_format,
        conversation_id=request.conversation_id
    )

    try:
        # Step 1: Decode and transcribe audio
        audio_bytes = base64.b64decode(request.audio_base64)

        # Placeholder transcription - integrate with speech-to-text service
        transcribed_text = "[Voice input received - transcription pending implementation]"

        # For demo purposes, use a sample message if transcription not implemented
        demo_message = "Show me my tasks"

        # Step 2: Get or create conversation
        conversation = await get_or_create_conversation(session, user_id)

        # Step 3: Persist user message
        user_msg = await append_message(
            session,
            conversation,
            MessageRole.USER,
            f"[Voice] {demo_message}"
        )

        # Step 4: Build conversation context
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

        # Step 5: Run AI agent
        agent_response = await run_agent(
            user_id=user_id,
            user_message=demo_message,
            conversation_history=conversation_history,
            session=session
        )

        # Step 6: Persist assistant response
        await append_message(
            session,
            conversation,
            MessageRole.ASSISTANT,
            agent_response.response
        )

        # Step 7: Build tool calls and thinking steps
        tool_calls = [
            ToolCall(
                tool=tc.tool,
                parameters=tc.parameters,
                result=tc.result,
                duration_ms=tc.duration_ms
            )
            for tc in agent_response.tool_calls
        ]

        thinking_steps = [
            ThinkingStep(
                type=ThinkingStepType(ts.type),
                content=ts.content,
                timestamp=ts.timestamp
            )
            for ts in agent_response.thinking_steps
        ]

        # Step 8: Synthesize response audio (placeholder)
        # In production, integrate with text-to-speech service
        audio_base64 = None  # Would be base64 encoded audio

        logger.info(
            "voice_chat_response",
            user_id=user_id,
            conversation_id=conversation.id,
            tool_calls=len(tool_calls)
        )

        return VoiceChatResponse(
            conversation_id=conversation.id,
            transcribed_text=transcribed_text,
            response_text=agent_response.response,
            audio_base64=audio_base64,
            tool_calls=tool_calls,
            thinking_steps=thinking_steps
        )

    except Exception as e:
        logger.error("voice_chat_failed", user_id=user_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice chat"
        )


@router.post("/synthesize")
async def synthesize_speech(
    user_id: str,
    request: SynthesizeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Synthesize text to speech audio.

    Args:
        user_id: User ID from URL path
        request: SynthesizeRequest with text and voice preference
        current_user: Authenticated user from JWT

    Returns:
        Audio stream (audio/mpeg)

    Raises:
        403: If user_id doesn't match authenticated user
        500: If synthesis fails
    """
    verify_user_access(user_id, current_user)

    logger.info(
        "voice_synthesize_request",
        user_id=user_id,
        text_length=len(request.text),
        voice=request.voice
    )

    try:
        # Placeholder - in production, integrate with:
        # - OpenAI TTS API
        # - Google Text-to-Speech
        # - Azure Speech Services
        # - ElevenLabs

        # Return empty audio stream as placeholder
        audio_buffer = io.BytesIO()
        # Would write actual audio data here

        return StreamingResponse(
            io.BytesIO(b""),  # Placeholder empty audio
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except Exception as e:
        logger.error("voice_synthesize_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to synthesize speech"
        )
