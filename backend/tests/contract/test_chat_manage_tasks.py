"""Contract tests for chat task management endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import app
from src.models import User, Task


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", username="testuser")


@pytest.fixture
def mock_tasks():
    return [
        Task(id=1, title="Task 1", description="Description 1", completed=False, user_id=1),
        Task(id=2, title="Task 2", description="Description 2", completed=True, user_id=1),
    ]


class TestChatManageTasks:
    """Test chat endpoints for task management operations."""

    @patch("src.routes.chat.get_current_user")
    @patch("src.agent.runner.run_agent")
    def test_list_tasks_intent(self, mock_agent, mock_user_auth, client, mock_user, mock_tasks):
        """Test listing tasks through chat."""
        mock_user_auth.return_value = mock_user
        mock_agent.return_value = {
            "response": "Here are your tasks: Task 1 (pending), Task 2 (completed)",
            "tool_calls": [{"tool": "list_tasks", "result": mock_tasks}]
        }

        response = client.post(
            f"/api/{mock_user.id}/chat",
            json={"message": "What tasks do I have?"},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data["response"].lower()
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool"] == "list_tasks"

    @patch("src.routes.chat.get_current_user")
    @patch("src.agent.runner.run_agent")
    def test_complete_task_intent(self, mock_agent, mock_user_auth, client, mock_user):
        """Test completing a task through chat."""
        mock_user_auth.return_value = mock_user
        mock_agent.return_value = {
            "response": "Task 1 has been marked as completed!",
            "tool_calls": [{"tool": "complete_task", "task_id": 1, "result": "success"}]
        }

        response = client.post(
            f"/api/{mock_user.id}/chat",
            json={"message": "Mark task 1 as complete"},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "completed" in data["response"].lower()
        assert data["tool_calls"][0]["tool"] == "complete_task"

    @patch("src.routes.chat.get_current_user")
    @patch("src.agent.runner.run_agent")
    def test_delete_task_intent(self, mock_agent, mock_user_auth, client, mock_user):
        """Test deleting a task through chat."""
        mock_user_auth.return_value = mock_user
        mock_agent.return_value = {
            "response": "Task 1 has been deleted successfully.",
            "tool_calls": [{"tool": "delete_task", "task_id": 1, "result": "success"}]
        }

        response = client.post(
            f"/api/{mock_user.id}/chat",
            json={"message": "Delete task 1"},
            headers={"Authorization": "Bearer fake-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["response"].lower()
        assert data["tool_calls"][0]["tool"] == "delete_task"
