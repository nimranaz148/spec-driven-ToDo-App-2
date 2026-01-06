"""Unit tests for conversation service.

Tests cover:
1. get_or_create_conversation - creates new conversation, returns existing one
2. get_conversation_by_id - returns conversation, enforces user isolation
3. append_message - creates message with correct role, truncates long content
4. list_recent_messages - returns limited messages in chronological order
5. get_full_history - returns all messages
6. get_message_count - returns correct count
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models import Conversation, Message, MessageRole
from services.conversation_service import (
    get_or_create_conversation,
    get_conversation_by_id,
    append_message,
    list_recent_messages,
    get_full_history,
    get_message_count,
)


class TestGetOrCreateConversation:
    """Tests for get_or_create_conversation function."""

    @pytest.mark.asyncio
    async def test_returns_existing_conversation(self):
        """Test that existing conversation is returned when found."""
        # Arrange
        user_id = "user-123"
        existing_conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            messages=[],
        )

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_conversation
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_or_create_conversation(mock_session, user_id)

        # Assert
        assert result == existing_conversation
        assert result.id == 1
        assert result.user_id == user_id
        mock_session.execute.assert_called_once()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new_conversation_when_none_exists(self):
        """Test that new conversation is created when none exists."""
        # Arrange
        user_id = "user-456"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Mock the conversation that will be created
        async def mock_refresh(obj):
            obj.id = 2

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            mock_time = datetime(2024, 1, 2, 10, 0, 0)
            mock_now.return_value = mock_time
            result = await get_or_create_conversation(mock_session, user_id)

        # Assert
        assert result.user_id == user_id
        assert result.created_at == mock_time
        assert result.updated_at == mock_time
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_loads_messages_relationship(self):
        """Test that conversation is loaded with messages relationship."""
        # Arrange
        user_id = "user-789"
        message1 = Message(
            id=1,
            user_id=user_id,
            conversation_id=1,
            role=MessageRole.USER,
            content="Hello",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        existing_conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            messages=[message1],
        )

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_conversation
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_or_create_conversation(mock_session, user_id)

        # Assert
        assert len(result.messages) == 1
        assert result.messages[0].content == "Hello"


class TestGetConversationById:
    """Tests for get_conversation_by_id function."""

    @pytest.mark.asyncio
    async def test_returns_conversation_when_user_matches(self):
        """Test that conversation is returned when user_id matches."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
            messages=[],
        )

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = conversation
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_conversation_by_id(mock_session, conversation_id, user_id)

        # Assert
        assert result == conversation
        assert result.id == conversation_id
        assert result.user_id == user_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_user_does_not_match(self):
        """Test that None is returned when user_id does not match (user isolation)."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        wrong_user_id = "user-456"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No match due to user isolation
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_conversation_by_id(mock_session, conversation_id, wrong_user_id)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_conversation_not_found(self):
        """Test that None is returned when conversation doesn't exist."""
        # Arrange
        conversation_id = 999
        user_id = "user-123"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_conversation_by_id(mock_session, conversation_id, user_id)

        # Assert
        assert result is None


class TestAppendMessage:
    """Tests for append_message function."""

    @pytest.mark.asyncio
    async def test_creates_message_with_correct_role_user(self):
        """Test that message is created with USER role."""
        # Arrange
        user_id = "user-123"
        conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        content = "Hello, assistant!"

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            if isinstance(obj, Message):
                obj.id = 1

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            mock_time = datetime(2024, 1, 2, 10, 0, 0)
            mock_now.return_value = mock_time
            result = await append_message(mock_session, conversation, MessageRole.USER, content)

        # Assert
        assert result.role == MessageRole.USER
        assert result.content == content
        assert result.user_id == user_id
        assert result.conversation_id == 1
        assert result.created_at == mock_time
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_message_with_correct_role_assistant(self):
        """Test that message is created with ASSISTANT role."""
        # Arrange
        user_id = "user-123"
        conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        content = "I can help you with that!"

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            if isinstance(obj, Message):
                obj.id = 2

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            mock_time = datetime(2024, 1, 2, 11, 0, 0)
            mock_now.return_value = mock_time
            result = await append_message(mock_session, conversation, MessageRole.ASSISTANT, content)

        # Assert
        assert result.role == MessageRole.ASSISTANT
        assert result.content == content

    @pytest.mark.asyncio
    async def test_truncates_long_content(self):
        """Test that content longer than 4000 chars is truncated."""
        # Arrange
        user_id = "user-123"
        conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        long_content = "x" * 5000  # 5000 characters

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            if isinstance(obj, Message):
                obj.id = 3

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            mock_time = datetime(2024, 1, 2, 12, 0, 0)
            mock_now.return_value = mock_time
            result = await append_message(mock_session, conversation, MessageRole.USER, long_content)

        # Assert
        assert len(result.content) == 4000
        assert result.content == "x" * 4000

    @pytest.mark.asyncio
    async def test_does_not_truncate_content_at_limit(self):
        """Test that content exactly at 4000 chars is not truncated."""
        # Arrange
        user_id = "user-123"
        conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        content_at_limit = "y" * 4000

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            if isinstance(obj, Message):
                obj.id = 4

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            mock_time = datetime(2024, 1, 2, 13, 0, 0)
            mock_now.return_value = mock_time
            result = await append_message(mock_session, conversation, MessageRole.USER, content_at_limit)

        # Assert
        assert len(result.content) == 4000
        assert result.content == content_at_limit

    @pytest.mark.asyncio
    async def test_updates_conversation_timestamp(self):
        """Test that conversation's updated_at is updated when message is added."""
        # Arrange
        user_id = "user-123"
        old_time = datetime(2024, 1, 1, 12, 0, 0)
        conversation = Conversation(
            id=1,
            user_id=user_id,
            created_at=old_time,
            updated_at=old_time,
        )
        content = "Update timestamp test"

        mock_session = AsyncMock(spec=AsyncSession)

        async def mock_refresh(obj):
            if isinstance(obj, Message):
                obj.id = 5

        mock_session.refresh.side_effect = mock_refresh

        # Act
        with patch('services.conversation_service.utc_now_naive') as mock_now:
            new_time = datetime(2024, 1, 2, 14, 0, 0)
            mock_now.return_value = new_time
            await append_message(mock_session, conversation, MessageRole.USER, content)

        # Assert
        assert conversation.updated_at == new_time
        assert conversation.updated_at > old_time


class TestListRecentMessages:
    """Tests for list_recent_messages function."""

    @pytest.mark.asyncio
    async def test_returns_limited_messages(self):
        """Test that only the specified limit of messages is returned."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        limit = 5

        # Create 10 messages, but only expect 5
        messages = [
            Message(
                id=i,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=datetime(2024, 1, 1, 12, i, 0),
            )
            for i in range(10, 0, -1)  # Reverse order (newest first)
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages[:limit]  # Only first 5
        mock_session.execute.return_value = mock_result

        # Act
        result = await list_recent_messages(mock_session, conversation_id, user_id, limit=limit)

        # Assert
        assert len(result) == limit
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_messages_in_chronological_order(self):
        """Test that messages are returned in chronological order (oldest first)."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        # Messages returned from DB in DESC order (newest first)
        messages_from_db = [
            Message(
                id=3,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Latest message",
                created_at=datetime(2024, 1, 1, 12, 3, 0),
            ),
            Message(
                id=2,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Middle message",
                created_at=datetime(2024, 1, 1, 12, 2, 0),
            ),
            Message(
                id=1,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Oldest message",
                created_at=datetime(2024, 1, 1, 12, 1, 0),
            ),
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages_from_db
        mock_session.execute.return_value = mock_result

        # Act
        result = await list_recent_messages(mock_session, conversation_id, user_id, limit=20)

        # Assert
        assert len(result) == 3
        # Should be in chronological order after reversal
        assert result[0].content == "Oldest message"
        assert result[1].content == "Middle message"
        assert result[2].content == "Latest message"
        assert result[0].created_at < result[1].created_at < result[2].created_at

    @pytest.mark.asyncio
    async def test_default_limit_is_20(self):
        """Test that default limit is 20 messages."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        messages = [
            Message(
                id=i,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=f"Message {i}",
                created_at=datetime(2024, 1, 1, 12, i, 0),
            )
            for i in range(25, 0, -1)  # 25 messages
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages[:20]  # Default limit
        mock_session.execute.return_value = mock_result

        # Act - call without explicit limit
        result = await list_recent_messages(mock_session, conversation_id, user_id)

        # Assert
        assert len(result) == 20

    @pytest.mark.asyncio
    async def test_enforces_user_isolation(self):
        """Test that only messages for the specified user are returned."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        # Only messages for user-123 should be returned
        messages = [
            Message(
                id=1,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="User 123 message",
                created_at=datetime(2024, 1, 1, 12, 1, 0),
            ),
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages
        mock_session.execute.return_value = mock_result

        # Act
        result = await list_recent_messages(mock_session, conversation_id, user_id, limit=20)

        # Assert
        assert len(result) == 1
        assert all(msg.user_id == user_id for msg in result)

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_messages(self):
        """Test that empty list is returned when conversation has no messages."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Act
        result = await list_recent_messages(mock_session, conversation_id, user_id, limit=20)

        # Assert
        assert result == []
        assert isinstance(result, list)


class TestGetFullHistory:
    """Tests for get_full_history function."""

    @pytest.mark.asyncio
    async def test_returns_all_messages(self):
        """Test that all messages are returned regardless of count."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        messages = [
            Message(
                id=i,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i}",
                created_at=datetime(2024, 1, 1, 12, i, 0),
            )
            for i in range(1, 51)  # 50 messages
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_full_history(mock_session, conversation_id, user_id)

        # Assert
        assert len(result) == 50
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_messages_in_chronological_order(self):
        """Test that messages are returned in chronological order (ASC)."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        messages = [
            Message(
                id=1,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="First",
                created_at=datetime(2024, 1, 1, 12, 1, 0),
            ),
            Message(
                id=2,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Second",
                created_at=datetime(2024, 1, 1, 12, 2, 0),
            ),
            Message(
                id=3,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Third",
                created_at=datetime(2024, 1, 1, 12, 3, 0),
            ),
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_full_history(mock_session, conversation_id, user_id)

        # Assert
        assert result[0].content == "First"
        assert result[1].content == "Second"
        assert result[2].content == "Third"
        assert result[0].created_at < result[1].created_at < result[2].created_at

    @pytest.mark.asyncio
    async def test_enforces_user_isolation(self):
        """Test that only messages for the specified user are returned."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        messages = [
            Message(
                id=1,
                user_id=user_id,
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="User 123 message",
                created_at=datetime(2024, 1, 1, 12, 1, 0),
            ),
        ]

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = messages
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_full_history(mock_session, conversation_id, user_id)

        # Assert
        assert all(msg.user_id == user_id for msg in result)

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_messages(self):
        """Test that empty list is returned when conversation has no messages."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_full_history(mock_session, conversation_id, user_id)

        # Assert
        assert result == []
        assert isinstance(result, list)


class TestGetMessageCount:
    """Tests for get_message_count function."""

    @pytest.mark.asyncio
    async def test_returns_correct_count(self):
        """Test that correct message count is returned."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        expected_count = 42

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_message_count(mock_session, conversation_id, user_id)

        # Assert
        assert result == expected_count
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_zero_when_no_messages(self):
        """Test that 0 is returned when conversation has no messages."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_message_count(mock_session, conversation_id, user_id)

        # Assert
        assert result == 0
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_enforces_user_isolation(self):
        """Test that count only includes messages for the specified user."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        expected_count = 5  # Only messages for user-123

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_message_count(mock_session, conversation_id, user_id)

        # Assert
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_counts_all_message_roles(self):
        """Test that count includes both user and assistant messages."""
        # Arrange
        conversation_id = 1
        user_id = "user-123"
        expected_count = 10  # Mix of user and assistant messages

        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = expected_count
        mock_session.execute.return_value = mock_result

        # Act
        result = await get_message_count(mock_session, conversation_id, user_id)

        # Assert
        assert result == expected_count
