"""SQLModel database models for Todo application."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .models import Message  # Forward reference for type hints


class MessageRole(str, Enum):
    """Enum for message roles in conversations."""
    USER = "user"
    ASSISTANT = "assistant"


def utc_now_naive() -> datetime:
    """Return current UTC time as timezone-naive datetime for PostgreSQL."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# NOTE: User model removed - Better Auth creates and manages the 'user' table.
# The 'user' table is created by Better Auth with fields:
# - id: text (UUID)
# - email: text
# - name: text
# - emailVerified: text (timestamp)
# - image: text
# - createdAt: text (timestamp)
# - updatedAt: text (timestamp)
#
# Task model references 'user' table via user_id foreign key.


class Task(SQLModel, table=True):
    """Task model for todo items."""

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique task identifier")
    # NOTE: user_id references Better Auth's 'user' table via database FK constraint
    # We don't use SQLModel's foreign_key param since Better Auth creates the table separately
    # The FK constraint (tasks_user_id_fkey -> user.id) is managed at the database level
    user_id: str = Field(index=True, description="Owner of task (FK to user.id)")
    title: str = Field(max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task details")
    completed: bool = Field(default=False, description="Completion status")
    created_at: datetime = Field(default_factory=utc_now_naive, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now_naive, description="Last modification timestamp")


class Conversation(SQLModel, table=True):
    """Conversation model for chat sessions.

    Each user can have multiple conversations.
    Conversations never cross users - strict isolation enforced.
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique conversation identifier")
    user_id: str = Field(index=True, description="Owner of conversation (FK to user.id)")
    title: Optional[str] = Field(default=None, max_length=200, description="Conversation title")
    created_at: datetime = Field(default_factory=utc_now_naive, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=utc_now_naive, description="Last message timestamp")

    # Relationship to messages
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"}
    )


class Message(SQLModel, table=True):
    """Message model for conversation history.

    Messages are immutable once created (no updates).
    Ordered by created_at, id for deterministic ordering.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True, description="Unique message identifier")
    user_id: str = Field(index=True, description="Owner for fast filtering (matches conversation user)")
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        description="Reference to parent conversation"
    )
    role: str = Field(max_length=20, description="Message sender role (user or assistant)")
    content: str = Field(max_length=4000, description="Message content (max 4000 chars)")
    created_at: datetime = Field(default_factory=utc_now_naive, description="Creation timestamp")

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
