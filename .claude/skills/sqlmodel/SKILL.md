---
name: sqlmodel
description: SQLModel ORM patterns for PostgreSQL database operations. Use when defining database models, creating queries, or managing database connections for the Todo backend.
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

# SQLModel Skill

## Quick Reference

SQLModel is a Python ORM built on top of SQLAlchemy and Pydantic for type-safe database operations.

## Basic Model Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for todo items."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Database Connection

```python
from sqlmodel import create_engine, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@host.neon.tech/db?sslmode=require"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

def get_session() -> Session:
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
```

## CRUD Operations

```python
from sqlmodel import Session, select

def create_task(db: Session, title: str, user_id: str) -> Task:
    task = Task(title=title, user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_user_tasks(db: Session, user_id: str) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)
    return list(db.exec(query))

def get_task(db: Session, task_id: int, user_id: str) -> Task | None:
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return db.exec(query).first()

def update_task(db: Session, task_id: int, user_id: str, **kwargs) -> Task | None:
    task = get_task(db, task_id, user_id)
    if task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
    return task

def delete_task(db: Session, task_id: int, user_id: str) -> bool:
    task = get_task(db, task_id, user_id)
    if task:
        db.delete(task)
        db.commit()
        return True
    return False
```

## Pydantic Integration

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    """Schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)

    class Config:
        from_attributes = True

class TaskResponse(TaskCreate):
    """Schema for task responses."""
    id: int
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Indexes

```python
class Task(SQLModel, table=True):
    user_id: str = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

## For Detailed Reference

See [REFERENCE.md](REFERENCE.md) for:
- Advanced relationships
- Complex queries
- Migrations
- Performance optimization
- Testing patterns
