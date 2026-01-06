"""Conversation management routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from ..db import get_session
from ..auth import get_current_user, verify_user_access
from ..services.conversation_service import (
    create_new_conversation,
    list_user_conversations,
    delete_conversation,
    update_conversation_title,
    get_conversation_by_id,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/{user_id}/conversations", tags=["conversations"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    title: str


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    user_id: str,
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new conversation for the user."""
    verify_user_access(user_id, current_user)
    
    logger.info("create_conversation_request", user_id=user_id, title=request.title)
    
    conversation = await create_new_conversation(
        session=session,
        user_id=user_id,
        title=request.title,
    )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title or f"Chat {conversation.id}",
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
        message_count=0,
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List all conversations for the user."""
    verify_user_access(user_id, current_user)
    
    logger.info("list_conversations_request", user_id=user_id)
    
    conversations = await list_user_conversations(session=session, user_id=user_id)
    
    return [
        ConversationResponse(
            id=conv.id,
            title=conv.title or f"Chat {conv.id}",
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=len(conv.messages) if hasattr(conv, 'messages') and conv.messages else 0,
        )
        for conv in conversations
    ]


@router.delete("/{conversation_id}")
async def delete_conversation_endpoint(
    user_id: str,
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a conversation and all its messages."""
    verify_user_access(user_id, current_user)
    
    logger.info("delete_conversation_request", user_id=user_id, conversation_id=conversation_id)
    
    deleted = await delete_conversation(
        session=session,
        conversation_id=conversation_id,
        user_id=user_id,
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {"message": "Conversation deleted successfully"}


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    user_id: str,
    conversation_id: int,
    request: UpdateConversationRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update conversation title."""
    verify_user_access(user_id, current_user)
    
    logger.info("update_conversation_request", user_id=user_id, conversation_id=conversation_id)
    
    conversation = await update_conversation_title(
        session=session,
        conversation_id=conversation_id,
        user_id=user_id,
        title=request.title,
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )
