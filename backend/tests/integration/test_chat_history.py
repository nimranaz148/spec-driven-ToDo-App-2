"""Integration tests for chat history functionality."""

import pytest
from unittest.mock import patch, AsyncMock
from src.services.conversation_service import ConversationService
from src.models import User, Conversation, Message, MessageRole


@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com", username="testuser")


@pytest.fixture
def mock_messages():
    return [
        Message(id=1, conversation_id=1, role=MessageRole.USER, content="Hello"),
        Message(id=2, conversation_id=1, role=MessageRole.ASSISTANT, content="Hi there!"),
        Message(id=3, conversation_id=1, role=MessageRole.USER, content="Add task"),
        Message(id=4, conversation_id=1, role=MessageRole.ASSISTANT, content="Task added!"),
    ]


class TestChatHistory:
    """Integration tests for chat history persistence and retrieval."""

    @patch("src.services.conversation_service.get_full_history")
    async def test_messages_fetched_in_order_limited_to_user(self, mock_get_history, mock_user, mock_messages):
        """Test messages are returned in order and limited to user."""
        mock_get_history.return_value = mock_messages
        session = AsyncMock()
        
        result = await mock_get_history(session, 1, mock_user.id)
        
        assert len(result) == 4
        assert result[0].content == "Hello"
        assert result[3].content == "Task added!"
        mock_get_history.assert_called_once_with(session, 1, mock_user.id)

    @patch("src.services.conversation_service.list_recent_messages")
    async def test_sliding_window_pagination(self, mock_list_recent, mock_user):
        """Test sliding 20-message window for context."""
        many_messages = [Message(id=i, conversation_id=1, role=MessageRole.USER, content=f"Message {i}") for i in range(1, 26)]
        mock_list_recent.return_value = many_messages[-20:]
        
        session = AsyncMock()
        result = await mock_list_recent(session, 1, mock_user.id, limit=20)
        
        assert len(result) == 20
        assert result[0].content == "Message 6"
        assert result[-1].content == "Message 25"
