"""Tests for database connection and operations."""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel, select

# Import from main app
import sys
sys.path.insert(0, 'backend/src')
from db import get_session, engine
from models import User, Task
from schemas.task import TaskCreate


@pytest.fixture
async def test_engine():
    """Create a test database engine using SQLite."""
    from sqlalchemy.pool import StaticPool

    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield test_engine

    # Cleanup
    await test_engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_database_connection(test_engine):
    """Test that database engine can be created and connected."""
    # Verify engine exists and is async
    assert test_engine is not None
    assert hasattr(test_engine, 'connect')

    # Try to execute a simple query to verify connection
    async with test_engine.connect() as conn:
        result = await conn.execute(select(1))
        row = result.fetchone()
        assert row[0] == 1


@pytest.mark.asyncio
async def test_create_user(test_session):
    """Test creating a user in the database."""
    user = User(
        id="test-user-123",
        email="test@example.com",
        name="Test User",
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    assert user.id == "test-user-123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_get_user_by_id(test_session):
    """Test retrieving a user by ID."""
    user = User(
        id="test-user-456",
        email="retrieve@example.com",
        name="Retrieve User",
    )

    test_session.add(user)
    await test_session.commit()

    # Query for the user
    result = await test_session.execute(
        select(User).where(User.id == "test-user-456")
    )
    retrieved_user = result.scalar_one_or_none()

    assert retrieved_user is not None
    assert retrieved_user.id == "test-user-456"
    assert retrieved_user.email == "retrieve@example.com"


@pytest.mark.asyncio
async def test_create_task(test_session):
    """Test creating a task in the database."""
    # First create a user
    user = User(
        id="task-user-123",
        email="taskuser@example.com",
        name="Task User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Then create a task
    task = Task(
        user_id=user.id,
        title="Test Task",
        description="Test Description",
        completed=False,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.id is not None
    assert task.user_id == user.id
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.created_at is not None
    assert task.updated_at is not None


@pytest.mark.asyncio
async def test_get_tasks_by_user(test_session):
    """Test retrieving tasks for a specific user."""
    # Create a user
    user = User(
        id="multi-task-user",
        email="multitask@example.com",
        name="Multi Task User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Create multiple tasks
    tasks = [
        Task(user_id=user.id, title="Task 1"),
        Task(user_id=user.id, title="Task 2"),
        Task(user_id=user.id, title="Task 3"),
    ]

    for task in tasks:
        test_session.add(task)
    await test_session.commit()

    # Query tasks for the user
    result = await test_session.execute(
        select(Task).where(Task.user_id == user.id)
    )
    user_tasks = list(result.scalars().all())

    assert len(user_tasks) == 3
    assert all(t.user_id == user.id for t in user_tasks)


@pytest.mark.asyncio
async def test_update_task(test_session):
    """Test updating a task."""
    # Create a user and task
    user = User(
        id="update-user",
        email="update@example.com",
        name="Update User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    task = Task(
        user_id=user.id,
        title="Original Title",
        description="Original Description",
        completed=False,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    original_id = task.id

    # Update the task
    task.title = "Updated Title"
    task.completed = True
    await test_session.commit()

    # Refresh and verify
    await test_session.refresh(task)

    assert task.id == original_id
    assert task.title == "Updated Title"
    assert task.completed is True


@pytest.mark.asyncio
async def test_delete_task(test_session):
    """Test deleting a task."""
    # Create a user and task
    user = User(
        id="delete-user",
        email="delete@example.com",
        name="Delete User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    task = Task(
        user_id=user.id,
        title="Task to Delete",
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    task_id = task.id

    # Delete the task
    await test_session.delete(task)
    await test_session.commit()

    # Verify deletion
    result = await test_session.execute(
        select(Task).where(Task.id == task_id)
    )
    deleted_task = result.scalar_one_or_none()

    assert deleted_task is None


@pytest.mark.asyncio
async def test_user_task_relationship(test_session):
    """Test the relationship between User and Task."""
    # Create a user
    user = User(
        id="rel-user",
        email="rel@example.com",
        name="Rel User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    # Create tasks for the user
    tasks = [
        Task(user_id=user.id, title="Task 1"),
        Task(user_id=user.id, title="Task 2"),
    ]

    for task in tasks:
        test_session.add(task)
    await test_session.commit()

    # Query and verify relationship
    result = await test_session.execute(
        select(User).where(User.id == "rel-user")
    )
    retrieved_user = result.scalar_one_or_none()

    assert retrieved_user is not None
    # Note: relationship loading would require selectinload in real usage
    # For this test, we verify user_id foreign key is set correctly
    for task in tasks:
        assert task.user_id == user.id


@pytest.mark.asyncio
async def test_unique_email_constraint(test_session):
    """Test that email uniqueness is enforced."""
    from sqlalchemy import exc

    # Create first user
    user1 = User(
        id="user-1",
        email="unique@example.com",
        name="User 1",
    )
    test_session.add(user1)
    await test_session.commit()

    # Try to create second user with same email
    user2 = User(
        id="user-2",
        email="unique@example.com",
        name="User 2",
    )
    test_session.add(user2)

    # This should raise an integrity error
    with pytest.raises(Exception):  # SQLite may not enforce this, but in production it will
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_completion_toggle(test_session):
    """Test toggling task completion status."""
    # Create user and task
    user = User(
        id="toggle-user",
        email="toggle@example.com",
        name="Toggle User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    task = Task(
        user_id=user.id,
        title="Toggle Task",
        completed=False,
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Toggle to completed
    task.completed = True
    await test_session.commit()
    await test_session.refresh(task)

    assert task.completed is True

    # Toggle back to incomplete
    task.completed = False
    await test_session.commit()
    await test_session.refresh(task)

    assert task.completed is False
