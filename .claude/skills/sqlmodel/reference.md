# SQLModel Reference Guide

## Table of Contents
1. [Advanced Relationships](#advanced-relationships)
2. [Complex Queries](#complex-queries)
3. [Migrations](#migrations)
4. [Performance Optimization](#performance-optimization)
5. [Testing Patterns](#testing-patterns)

---

## Advanced Relationships

### One-to-Many (User to Tasks)

Since users are managed by Better Auth, we reference but don't define:

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    """Note: Better Auth manages users, this is just for reference."""
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str | None = None

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str
    # Relationship (back_populates optional with SQLModel)
    user: Optional[User] = Relationship()
```

### Self-Referencing for Hierarchical Tasks

```python
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str
    parent_id: int | None = Field(default=None, foreign_key="task.id", index=True)

    parent: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    subtasks: List["Task"] = Relationship()
```

### Many-to-Many with Tags

```python
class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

class TaskTag(SQLModel, table=True):
    task_id: int = Field(foreign_key="task.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    title: str
    tags: List[Tag] = Relationship(
        link_model=TaskTag,
        back_populates="tasks"
    )
```

---

## Complex Queries

### Joins

```python
from sqlmodel import select, join

# Simple join
query = select(Task, Tag).select_from(
    join(Task, TaskTag, Task.id == TaskTag.task_id)
).join(Tag, TaskTag.tag_id == Tag.id).where(Task.user_id == user_id)

# Join with filter
def get_tasks_with_tags(db: Session, user_id: str) -> list[tuple[Task, Tag]]:
    query = (
        select(Task, Tag)
        .select_from(Task)
        .outerjoin(TaskTag, Task.id == TaskTag.task_id)
        .outerjoin(Tag, TaskTag.tag_id == Tag.id)
        .where(Task.user_id == user_id)
    )
    return list(db.exec(query).all())
```

### Aggregations

```python
from sqlalchemy import func

def get_task_stats(db: Session, user_id: str) -> dict:
    # Count total tasks
    total = db.exec(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    ).scalar()

    # Count completed tasks
    completed = db.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == True
        )
    ).scalar()

    # Group by completion status
    from sqlalchemy import case
    status_counts = db.exec(
        select(
            case((Task.completed == True, "completed"), else_="pending").label("status"),
            func.count(Task.id)
        )
        .where(Task.user_id == user_id)
        .group_by("status")
    ).all()

    return {"total": total, "completed": completed, "status_counts": status_counts}
```

### Pagination

```python
def get_paginated_tasks(
    db: Session,
    user_id: str,
    page: int = 1,
    page_size: int = 20
) -> tuple[list[Task], int]:
    offset = (page - 1) * page_size

    tasks = db.exec(
        select(Task)
        .where(Task.user_id == user_id)
        .offset(offset)
        .limit(page_size)
        .order_by(Task.created_at.desc())
    ).all()

    total = db.exec(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    ).scalar()

    return tasks, total
```

### Full-Text Search (PostgreSQL)

```python
from sqlalchemy import text

def search_tasks(db: Session, user_id: str, query: str) -> list[Task]:
    search_query = text(
        "to_tsvector('english', title || ' ' || COALESCE(description, '')) @@ plainto_tsquery('english', :q)"
    )
    return list(
        db.exec(
            select(Task)
            .where(Task.user_id == user_id)
            .where(search_query)
            .params(q=query)
        ).all()
    )
```

---

## Migrations

### Alembic with SQLModel

1. **Install Alembic:**
```bash
pip install alembic
alembic init migrations
```

2. **Configure alembic.ini:**
```ini
sqlalchemy.url = postgresql://user:pass@host.neon.tech/db?sslmode=require
```

3. **Create migration:**
```bash
alembic revision -m "Add tasks table"
```

4. **Migration file (versions/xxx_add_tasks.py):**
```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_task_id"), "task", ["id"], unique=False)
    op.create_index(op.f("ix_task_user_id"), "task", ["user_id"], unique=False)

def downgrade():
    op.drop_index(op.f("ix_task_user_id"), table_name="task")
    op.drop_index(op.f("ix_task_id"), table_name="task")
    op.drop_table("task")
```

5. **Run migrations:**
```bash
alembic upgrade head
```

### Auto-Generate Migrations

```bash
alembic revision --autogenerate -m "Description"
```

---

## Performance Optimization

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # Base connections
    max_overflow=10,      # Extra connections under load
    pool_pre_ping=True,   # Verify connection before use
    pool_recycle=3600,    # Recycle connections every hour
)
```

### Query Optimization

```python
# Bad: N+1 query problem
tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()
for task in tasks:
    print(task.tags)  # Each access triggers a query!

# Good: Eager loading
from sqlmodel import select, joinedload

tasks = db.exec(
    select(Task)
    .options(joinedload(Task.tags))
    .where(Task.user_id == user_id)
).unique().all()

# Now tags are loaded in a single query
for task in tasks:
    print(task.tags)  # No additional queries!
```

### Batch Operations

```python
def bulk_create_tasks(db: Session, tasks_data: list[dict]) -> list[Task]:
    tasks = [Task(**data) for data in tasks_data]
    for task in tasks:
        db.add(task)
    db.commit()
    for task in tasks:
        db.refresh(task)
    return tasks

def bulk_update_completed(db: Session, task_ids: list[int], user_id: str):
    db.exec(
        update(Task)
        .where(Task.id.in_(task_ids), Task.user_id == user_id)
        .values(completed=True)
    )
    db.commit()
```

### Index Strategy

```python
class Task(SQLModel, table=True):
    # Single column indexes for common filters
    user_id: str = Field(foreign_key="user.id", index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Composite index for specific query patterns
    # (requires sa_column_kwargs for SQLModel)
    user_id: str = Field(
        foreign_key="user.id",
        sa_column_kwargs={"index": True}
    )
```

---

## Testing Patterns

### Test Database Setup

```python
# conftest.py
import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool

@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)
```

### Test Fixtures

```python
@pytest.fixture
def sample_task(test_db: Session) -> Task:
    task = Task(
        user_id="user_123",
        title="Test task",
        description="A test description"
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task

@pytest.fixture
def sample_user(test_db: Session) -> User:
    user = User(id="user_123", email="test@example.com", name="Test User")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
```

### Testing CRUD Functions

```python
def test_create_task(test_db: Session):
    task = create_task(test_db, "New task", "user_123")
    assert task.id is not None
    assert task.title == "New task"
    assert task.user_id == "user_123"
    assert task.completed is False

def test_get_user_tasks(test_db: Session, sample_user: User):
    create_task(test_db, "Task 1", "user_123")
    create_task(test_db, "Task 2", "user_123")
    create_task(test_db, "Task 3", "other_user")

    tasks = get_user_tasks(test_db, "user_123")
    assert len(tasks) == 2

def test_update_task(test_db: Session, sample_task: Task):
    updated = update_task(
        test_db,
        sample_task.id,
        "user_123",
        title="Updated title",
        completed=True
    )
    assert updated.title == "Updated title"
    assert updated.completed is True

def test_delete_task(test_db: Session, sample_task: Task):
    result = delete_task(test_db, sample_task.id, "user_123")
    assert result is True

    # Verify deletion
    task = get_task(test_db, sample_task.id, "user_123")
    assert task is None
```

### Mocking with pytest-mock

```python
def test_create_task_with_mock_db(mocker):
    mock_session = mocker.MagicMock()
    mock_db = mocker.MagicMock()
    mock_db.__enter__ = mocker.MagicMock(return_value=mock_db)
    mock_db.__exit__ = mocker.MagicMock(return_value=False)

    # Configure mock behavior
    mock_task = Task(id=1, title="Test", user_id="user")
    mock_db.add = mocker.MagicMock()
    mock_db.commit = mocker.MagicMock()
    mock_db.refresh = mocker.MagicMock(return_value=mock_task)

    result = create_task(mock_db, "Test", "user")
    assert result.title == "Test"
```
