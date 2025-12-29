"""Tests for SQLModel User and Task serialization."""
import pytest
from datetime import datetime
from pydantic import ValidationError

import sys
sys.path.insert(0, 'backend/src')

from models import User, Task
from schemas.auth import UserCreate, UserResponse, LoginRequest
from schemas.task import TaskCreate, TaskUpdate, TaskResponse


class TestUserModel:
    """Tests for User model."""

    def test_user_model_creation(self):
        """Test creating a User instance."""
        user = User(
            id="test-uuid-123",
            email="test@example.com",
            name="Test User",
            created_at=datetime.utcnow(),
        )

        assert user.id == "test-uuid-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.created_at is not None
        assert user.tasks == []

    def test_user_model_with_custom_id(self):
        """Test User with UUID-style ID."""
        user = User(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="uuid@example.com",
            name="UUID User",
        )

        assert len(user.id) == 36  # UUID format
        assert user.id == "550e8400-e29b-41d4-a716-446655440000"

    def test_user_email_validation(self):
        """Test User email validation."""
        # Valid email
        user = User(
            id="user-1",
            email="valid@example.com",
            name="Valid User",
        )
        assert user.email == "valid@example.com"

    def test_user_name_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            User(
                id="user-1",
                email="test@example.com",
                # name is missing
            )

    def test_user_timestamps(self):
        """Test User timestamp fields."""
        now = datetime.utcnow()
        user = User(
            id="user-1",
            email="test@example.com",
            name="Test",
            created_at=now,
        )

        assert user.created_at == now
        assert isinstance(user.created_at, datetime)

    def test_user_relationship_initialized(self):
        """Test that tasks relationship is initialized as empty list."""
        user = User(
            id="user-1",
            email="test@example.com",
            name="Test",
        )

        assert user.tasks == []
        assert isinstance(user.tasks, list)


class TestTaskModel:
    """Tests for Task model."""

    def test_task_model_creation(self):
        """Test creating a Task instance."""
        task = Task(
            id=1,
            user_id="user-123",
            title="Test Task",
            description="Test Description",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        assert task.id == 1
        assert task.user_id == "user-123"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False

    def test_task_default_values(self):
        """Test Task default values."""
        task = Task(
            user_id="user-123",
            title="Default Test",
        )

        assert task.id is None  # Auto-increment, not set on creation
        assert task.completed is False
        assert task.description is None

    def test_task_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            Task(
                user_id="user-123",
                # title is missing
            )

    def test_task_user_id_required(self):
        """Test that user_id is required."""
        with pytest.raises(ValidationError):
            Task(
                title="Test Task",
                # user_id is missing
            )

    def test_task_with_optional_description(self):
        """Test Task with optional description."""
        task = Task(
            user_id="user-123",
            title="No Description",
        )

        assert task.description is None

    def test_task_timestamps(self):
        """Test Task timestamp fields."""
        now = datetime.utcnow()
        task = Task(
            user_id="user-123",
            title="Timestamp Test",
            created_at=now,
            updated_at=now,
        )

        assert task.created_at == now
        assert task.updated_at == now
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_completion_toggle(self):
        """Test toggling task completion."""
        task = Task(
            user_id="user-123",
            title="Toggle Test",
            completed=False,
        )

        assert task.completed is False

        task.completed = True
        assert task.completed is True

    def test_task_user_relationship(self):
        """Test Task to User relationship."""
        user = User(
            id="user-123",
            email="test@example.com",
            name="Test",
        )

        task = Task(
            user_id=user.id,
            title="Relationship Test",
        )

        # Relationship is set via foreign key, not direct object reference
        assert task.user_id == user.id


class TestPydanticSchemas:
    """Tests for Pydantic validation schemas."""

    def test_user_create_valid(self):
        """Test valid UserCreate schema."""
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="securepassword123",
        )

        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
        assert user_data.password == "securepassword123"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                name="Test",
                password="password123",
            )

    def test_user_create_short_password(self):
        """Test UserCreate with short password."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                name="Test",
                password="short",  # Less than 8 characters
            )

    def test_user_create_missing_fields(self):
        """Test UserCreate with missing required fields."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                # name and password missing
            )

    def test_login_request_valid(self):
        """Test valid LoginRequest schema."""
        login_data = LoginRequest(
            email="login@example.com",
            password="password123",
        )

        assert login_data.email == "login@example.com"
        assert login_data.password == "password123"

    def test_login_request_invalid_email(self):
        """Test LoginRequest with invalid email."""
        with pytest.raises(ValidationError):
            LoginRequest(
                email="not-an-email",
                password="password123",
            )

    def test_task_create_valid(self):
        """Test valid TaskCreate schema."""
        task_data = TaskCreate(
            title="New Task",
            description="Task description",
        )

        assert task_data.title == "New Task"
        assert task_data.description == "Task description"

    def test_task_create_minimal(self):
        """Test TaskCreate with minimal data."""
        task_data = TaskCreate(
            title="Minimal Task",
        )

        assert task_data.title == "Minimal Task"
        assert task_data.description is None

    def test_task_create_title_required(self):
        """Test TaskCreate requires title."""
        with pytest.raises(ValidationError):
            TaskCreate(
                # title missing
                description="No title",
            )

    def test_task_create_title_max_length(self):
        """Test TaskCreate title max length."""
        with pytest.raises(ValidationError):
            TaskCreate(
                title="x" * 201,  # Exceeds 200 character limit
            )

    def test_task_update_partial(self):
        """Test TaskUpdate with partial data."""
        update_data = TaskUpdate(
            title="Updated Title",
        )

        assert update_data.title == "Updated Title"
        assert update_data.description is None
        assert update_data.completed is None

    def test_task_update_all_fields(self):
        """Test TaskUpdate with all fields."""
        update_data = TaskUpdate(
            title="Full Update",
            description="New description",
            completed=True,
        )

        assert update_data.title == "Full Update"
        assert update_data.description == "New description"
        assert update_data.completed is True

    def test_user_response_from_model(self):
        """Test UserResponse creation from User model."""
        user = User(
            id="user-123",
            email="response@example.com",
            name="Response User",
            created_at=datetime.utcnow(),
        )

        response = UserResponse.model_validate(user)

        assert response.id == user.id
        assert response.email == user.email
        assert response.name == user.name
        assert response.created_at == user.created_at

    def test_task_response_from_model(self):
        """Test TaskResponse creation from Task model."""
        now = datetime.utcnow()
        task = Task(
            id=1,
            user_id="user-123",
            title="Response Task",
            description="Task for response",
            completed=False,
            created_at=now,
            updated_at=now,
        )

        response = TaskResponse.model_validate(task)

        assert response.id == task.id
        assert response.user_id == task.user_id
        assert response.title == task.title
        assert response.description == task.description
        assert response.completed == task.completed
        assert response.created_at == task.created_at
        assert response.updated_at == task.updated_at

    def test_task_response_from_dict(self):
        """Test TaskResponse creation from dictionary."""
        data = {
            "id": 2,
            "user_id": "user-456",
            "title": "Dict Task",
            "description": None,
            "completed": True,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        }

        response = TaskResponse(**data)

        assert response.id == 2
        assert response.user_id == "user-456"
        assert response.title == "Dict Task"
        assert response.completed is True


class TestModelSerialization:
    """Tests for model serialization and deserialization."""

    def test_user_to_dict(self):
        """Test User model to dictionary conversion."""
        user = User(
            id="user-123",
            email="dict@example.com",
            name="Dict User",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        user_dict = user.model_dump()

        assert user_dict["id"] == "user-123"
        assert user_dict["email"] == "dict@example.com"
        assert user_dict["name"] == "Dict User"
        assert user_dict["created_at"] == datetime(2025, 1, 1, 12, 0, 0)

    def test_task_to_dict(self):
        """Test Task model to dictionary conversion."""
        task = Task(
            id=1,
            user_id="user-123",
            title="Dict Task",
            description="Description",
            completed=True,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        task_dict = task.model_dump()

        assert task_dict["id"] == 1
        assert task_dict["user_id"] == "user-123"
        assert task_dict["title"] == "Dict Task"
        assert task_dict["completed"] is True

    def test_user_json_serialization(self):
        """Test User model JSON serialization."""
        user = User(
            id="user-123",
            email="json@example.com",
            name="JSON User",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        user_json = user.model_dump_json()

        assert "user-123" in user_json
        assert "json@example.com" in user_json
        assert "JSON User" in user_json

    def test_task_json_serialization(self):
        """Test Task model JSON serialization."""
        task = Task(
            id=1,
            user_id="user-123",
            title="JSON Task",
            completed=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        task_json = task.model_dump_json()

        assert "1" in task_json
        assert "JSON Task" in task_json
        assert "false" in task_json
