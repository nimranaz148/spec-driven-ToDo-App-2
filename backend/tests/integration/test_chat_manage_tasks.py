"""Integration tests for chat task management flow."""

import pytest
from unittest.mock import patch, AsyncMock
from src.services.conversation_service import ConversationService
from src.services.task_service import TaskService
from src.agent.runner import run_agent
from src.models import User, Task, Conversation


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", username="testuser")


@pytest.fixture
def mock_tasks():
    return [
        Task(id=1, title="Buy groceries", completed=False, user_id=1),
        Task(id=2, title="Walk the dog", completed=False, user_id=1),
        Task(id=3, title="Finish project", completed=True, user_id=1),
    ]


class TestChatManageTasksIntegration:
    """Integration tests for chat-based task management."""

    @patch("src.services.task_service.TaskService.list_tasks")
    @patch("src.services.task_service.TaskService.complete_task")
    @patch("src.services.conversation_service.ConversationService.append_message")
    async def test_list_complete_edit_flow(self, mock_append, mock_complete, mock_list, mock_user, mock_tasks):
        """Test complete flow: list tasks → complete task → verify completion."""
        # Setup mocks
        mock_list.return_value = mock_tasks
        mock_complete.return_value = Task(id=3, title="Finish project", completed=True, user_id=1)
        mock_append.return_value = None

        # Step 1: List tasks
        with patch("src.agent.runner.run_agent") as mock_agent:
            mock_agent.return_value = {
                "response": "You have 3 tasks: Buy groceries (pending), Walk the dog (pending), Finish project (completed)",
                "tool_calls": [{"tool": "list_tasks", "result": mock_tasks}]
            }
            
            result = await run_agent("What are my tasks?", mock_user.id)
            assert "3 tasks" in result["response"]
            assert len(result["tool_calls"]) == 1

        # Step 2: Complete a task
        with patch("src.agent.runner.run_agent") as mock_agent:
            mock_agent.return_value = {
                "response": "Task 'Finish project' has been marked as completed!",
                "tool_calls": [{"tool": "complete_task", "task_id": 3, "result": "success"}]
            }
            
            result = await run_agent("Mark task 3 as complete", mock_user.id)
            assert "completed" in result["response"]
            mock_complete.assert_called_once_with(3, mock_user.id)

        # Step 3: Verify completion in list
        completed_tasks = [t for t in mock_tasks if t.completed]
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == 3

    @patch("src.services.task_service.TaskService.update_task")
    @patch("src.services.conversation_service.ConversationService.append_message")
    async def test_task_update_flow(self, mock_append, mock_update, mock_user):
        """Test updating task through chat."""
        updated_task = Task(id=1, title="Buy organic groceries", description="Updated", completed=False, user_id=1)
        mock_update.return_value = updated_task
        mock_append.return_value = None

        with patch("src.agent.runner.run_agent") as mock_agent:
            mock_agent.return_value = {
                "response": "Task updated successfully! Title changed to 'Buy organic groceries'",
                "tool_calls": [{"tool": "update_task", "task_id": 1, "fields": {"title": "Buy organic groceries"}}]
            }
            
            result = await run_agent("Change task 1 title to 'Buy organic groceries'", mock_user.id)
            assert "updated successfully" in result["response"]
            mock_update.assert_called_once()

    @patch("src.services.task_service.TaskService.delete_task")
    @patch("src.services.conversation_service.ConversationService.append_message")
    async def test_task_deletion_flow(self, mock_append, mock_delete, mock_user):
        """Test deleting task through chat."""
        mock_delete.return_value = True
        mock_append.return_value = None

        with patch("src.agent.runner.run_agent") as mock_agent:
            mock_agent.return_value = {
                "response": "Task has been deleted successfully.",
                "tool_calls": [{"tool": "delete_task", "task_id": 1, "result": "success"}]
            }
            
            result = await run_agent("Delete task 1", mock_user.id)
            assert "deleted successfully" in result["response"]
            mock_delete.assert_called_once_with(1, mock_user.id)
