"""Conversation service for chat history management."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Conversation, Message, utc_now_naive
from ..utils.logger import get_logger

logger = get_logger(__name__)


async def create_new_conversation(
    session: AsyncSession,
    user_id: str,
    title: str = None,
) -> Conversation:
    """Create a new conversation for a user.
    
    Args:
        session: Database session
        user_id: User ID
        title: Optional conversation title
        
    Returns:
        Created conversation
    """
    conversation = Conversation(
        user_id=user_id,
        title=title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        created_at=utc_now_naive(),
        updated_at=utc_now_naive(),
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    
    logger.info("conversation_created", user_id=user_id, conversation_id=conversation.id)
    return conversation


async def list_user_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 50,
) -> List[Conversation]:
    """List all conversations for a user.
    
    Args:
        session: Database session
        user_id: User ID
        limit: Maximum conversations to return
        
    Returns:
        List of conversations ordered by most recent
    """
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def delete_conversation(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
) -> bool:
    """Delete a conversation and all its messages.
    
    Args:
        session: Database session
        conversation_id: Conversation ID to delete
        user_id: User ID for authorization
        
    Returns:
        True if deleted, False if not found
    """
    # First delete all messages
    await session.execute(
        delete(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
        )
    )
    
    # Then delete the conversation
    result = await session.execute(
        delete(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
    )
    
    await session.commit()
    deleted = result.rowcount > 0
    
    if deleted:
        logger.info("conversation_deleted", user_id=user_id, conversation_id=conversation_id)
    
    return deleted


async def update_conversation_title(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    title: str,
) -> Optional[Conversation]:
    """Update conversation title.
    
    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: User ID for authorization
        title: New title
        
    Returns:
        Updated conversation or None if not found
    """
    result = await session.execute(
        select(Conversation)
        .where(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    
    if conversation:
        conversation.title = title
        conversation.updated_at = utc_now_naive()
        await session.commit()
        await session.refresh(conversation)
        logger.info("conversation_title_updated", user_id=user_id, conversation_id=conversation_id)
    
    return conversation


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
) -> Conversation:
    """Get the user's most recent conversation or create a new one.

    Users can have multiple conversations.
    Returns the most recently updated conversation.
    """
    # Try to find the most recent conversation for the user
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
        .options(selectinload(Conversation.messages))
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            created_at=utc_now_naive(),
            updated_at=utc_now_naive(),
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation


async def get_conversation_by_id(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
) -> Optional[Conversation]:
    """Get a conversation by ID, ensuring it belongs to the user."""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
    )
    return result.scalar_one_or_none()


async def append_message(
    session: AsyncSession,
    conversation: Conversation,
    role: str,
    content: str,
) -> Message:
    """Append a new message to a conversation.

    Args:
        session: Database session
        conversation: The conversation to append to
        role: Message role ("user" or "assistant")
        content: Message content (max 4000 chars)

    Returns:
        The created message
    """
    # Validate content length
    if len(content) > 4000:
        content = content[:4000]  # Truncate if too long

    message = Message(
        user_id=conversation.user_id,
        conversation_id=conversation.id,
        role=role,
        content=content,
        created_at=utc_now_naive(),
    )

    session.add(message)

    # Update conversation's updated_at timestamp
    conversation.updated_at = utc_now_naive()

    await session.commit()
    await session.refresh(message)

    return message


async def list_recent_messages(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    limit: int = 20,
) -> List[Message]:
    """Get the most recent messages from a conversation.

    This is used for the sliding context window sent to Gemini.

    Args:
        session: Database session
        conversation_id: The conversation to fetch messages from
        user_id: Owner of the conversation (for isolation)
        limit: Maximum number of messages to return (default 20)

    Returns:
        List of messages ordered by created_at ASC (oldest first)
    """
    # Get messages ordered by creation time, limited to recent ones
    result = await session.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id,
        )
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())

    # Reverse to get oldest first (chronological order for LLM context)
    messages.reverse()

    return messages


async def get_full_history(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
) -> List[Message]:
    """Get the full message history for a conversation.

    Used for displaying complete history in the UI.

    Args:
        session: Database session
        conversation_id: The conversation to fetch messages from
        user_id: Owner of the conversation (for isolation)

    Returns:
        List of all messages ordered by created_at ASC
    """
    result = await session.execute(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id,
        )
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    return list(result.scalars().all())


async def get_message_count(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
) -> int:
    """Get the total count of messages in a conversation.

    Args:
        session: Database session
        conversation_id: The conversation to count messages for
        user_id: Owner of the conversation (for isolation)

    Returns:
        Number of messages in the conversation
    """
    result = await session.execute(
        select(func.count())
        .select_from(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id,
        )
    )
    return result.scalar_one()
