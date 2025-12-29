"""SQLModel database models for Todo application."""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


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
