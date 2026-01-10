"""ChatKit Store implementation backed by SQLModel/PostgreSQL.

This store uses our existing Conversation and Message models to persist
ChatKit threads and items. Thread = Conversation, Item = Message.
"""

import logging
from datetime import datetime
from typing import Union, Annotated, Literal

from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata,
    Page,
    UserMessageItem,
    AssistantMessageItem,
    HiddenContextItem,
    ActiveStatus,
    FileAttachment,
    ImageAttachment,
    AssistantMessageContent,
    UserMessageTextContent,
    InferenceOptions,
)
from pydantic import Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from src.models import Conversation, Message

logger = logging.getLogger(__name__)

# Type alias for thread items (subset we support)
ThreadItem = Annotated[
    Union[
        UserMessageItem,
        AssistantMessageItem,
        HiddenContextItem,
    ],
    Field(discriminator='type')
]

# Type alias for attachments
Attachment = Annotated[
    Union[FileAttachment, ImageAttachment],
    Field(discriminator='type')
]


class TodoChatKitStore(Store[dict]):
    """ChatKit Store implementation using our existing database models.

    Maps ChatKit concepts to our models:
    - Thread -> Conversation
    - ThreadItem -> Message

    Context dict contains:
    - session: AsyncSession
    - user_id: str
    - conversation_id: Optional[int] - from URL param
    """

    def __init__(self):
        super().__init__()
        # Track mapping of temporary thread IDs to real DB IDs
        # This prevents duplicate conversation creation
        self._thread_id_map: dict[str, int] = {}

    # =====================================================
    # ID Generation
    # =====================================================

    def generate_thread_id(self, context: dict) -> str:
        """Generate a new thread ID."""
        import uuid
        return f"thread_{uuid.uuid4().hex[:12]}"

    def generate_item_id(
        self,
        item_type: Literal['thread', 'message', 'tool_call', 'task', 'workflow', 'attachment', 'sdk_hidden_context'],
        thread: ThreadMetadata,
        context: dict,
    ) -> str:
        """Generate a new item ID."""
        import uuid
        return f"{item_type}_{uuid.uuid4().hex[:12]}"

    # =====================================================
    # Thread Operations
    # =====================================================

    async def load_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> ThreadMetadata | None:
        """Load a thread by ID."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            conv_id = int(thread_id)
        except ValueError:
            # Check if we have a cached mapping for this temp ID
            if thread_id in self._thread_id_map:
                conv_id = self._thread_id_map[thread_id]
                logger.debug(f"Using cached conversation ID {conv_id} for thread {thread_id}")
            else:
                logger.warning(f"Invalid thread_id format and no mapping found: {thread_id}")
                return None

        conversation = await session.get(Conversation, conv_id)
        if not conversation or conversation.user_id != user_id:
            return None

        return ThreadMetadata(
            id=str(conversation.id),
            title=conversation.title,
            created_at=conversation.created_at,
            status=ActiveStatus(),
            metadata={
                "updated_at": conversation.updated_at.isoformat(),
            },
        )

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: dict,
    ) -> None:
        """Save/update a thread."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]
        existing_conv_id: int | None = context.get("conversation_id")  # From URL param
        original_thread_id = thread.id

        try:
            conv_id = int(thread.id)
            conversation = await session.get(Conversation, conv_id)
            if conversation and conversation.user_id == user_id:
                # Update existing
                if thread.title:
                    conversation.title = thread.title
                conversation.updated_at = datetime.utcnow()
                await session.commit()
        except ValueError:
            # Check if we already have a mapping for this temp ID
            if original_thread_id in self._thread_id_map:
                # Already created, just update the thread ID
                conv_id = self._thread_id_map[original_thread_id]
                thread.id = str(conv_id)
                logger.debug(f"Using cached conversation ID {conv_id} for thread {original_thread_id}")
                return

            # Check if we have an existing conversation from URL param
            if existing_conv_id:
                conversation = await session.get(Conversation, existing_conv_id)
                if conversation and conversation.user_id == user_id:
                    # Use existing conversation - map temp thread ID to it
                    self._thread_id_map[original_thread_id] = conversation.id
                    thread.id = str(conversation.id)
                    logger.info(f"Mapped thread {original_thread_id} to existing conversation {conversation.id}")
                    return

            # New thread with temporary ID - create conversation
            conversation = Conversation(
                user_id=user_id,
                title=thread.title,
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)

            # Store the mapping and update thread ID
            self._thread_id_map[original_thread_id] = conversation.id
            thread.id = str(conversation.id)
            logger.info(f"Created conversation {conversation.id} for thread {original_thread_id}")

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        order: str,
        context: dict,
    ) -> Page[ThreadMetadata]:
        """Load threads with pagination."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        # Base query
        query = select(Conversation).where(Conversation.user_id == user_id)

        # Apply order
        if order == "desc":
            query = query.order_by(Conversation.updated_at.desc())
        else:
            query = query.order_by(Conversation.updated_at.asc())

        # Get total count
        count_query = select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
        total = (await session.execute(count_query)).scalar_one()

        # Apply cursor-based pagination
        offset = 0
        if after:
            try:
                offset = int(after) + 1
            except ValueError:
                pass

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        conversations = result.scalars().all()

        threads = [
            ThreadMetadata(
                id=str(c.id),
                title=c.title,
                created_at=c.created_at,
                status=ActiveStatus(),
                metadata={"updated_at": c.updated_at.isoformat()},
            )
            for c in conversations
        ]

        has_more = offset + len(conversations) < total

        return Page(
            data=threads,
            has_more=has_more,
            first_id=threads[0].id if threads else None,
            last_id=threads[-1].id if threads else None,
        )

    async def delete_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> None:
        """Delete a thread and all its items."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            conv_id = int(thread_id)
        except ValueError:
            # Check if we have a cached mapping for this temp ID
            if thread_id in self._thread_id_map:
                conv_id = self._thread_id_map[thread_id]
            else:
                return

        conversation = await session.get(Conversation, conv_id)
        if conversation and conversation.user_id == user_id:
            # Delete all messages first
            msg_query = select(Message).where(Message.conversation_id == conv_id)
            messages = (await session.execute(msg_query)).scalars().all()
            for msg in messages:
                await session.delete(msg)

            # Delete conversation
            await session.delete(conversation)
            await session.commit()

            # Clean up the thread ID mapping
            keys_to_remove = [k for k, v in self._thread_id_map.items() if v == conv_id]
            for key in keys_to_remove:
                del self._thread_id_map[key]
            logger.info(f"Deleted conversation {conv_id}")

    # =====================================================
    # Thread Item Operations
    # =====================================================

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        """Load thread items with pagination."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            conv_id = int(thread_id)
        except ValueError:
            # Check if we have a cached mapping for this temp ID
            if thread_id in self._thread_id_map:
                conv_id = self._thread_id_map[thread_id]
                logger.debug(f"Using cached conversation ID {conv_id} for thread {thread_id}")
            else:
                return Page(data=[], has_more=False)

        # Verify access
        conversation = await session.get(Conversation, conv_id)
        if not conversation or conversation.user_id != user_id:
            return Page(data=[], has_more=False, first_id=None, last_id=None)

        # Query messages
        query = select(Message).where(Message.conversation_id == conv_id)

        # Apply order
        if order == "desc":
            query = query.order_by(Message.created_at.desc())
        else:
            query = query.order_by(Message.created_at.asc())

        # Get total
        count_query = select(func.count(Message.id)).where(Message.conversation_id == conv_id)
        total = (await session.execute(count_query)).scalar_one()

        # Apply pagination
        offset = 0
        if after:
            try:
                offset = int(after) + 1
            except ValueError:
                pass

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        messages = result.scalars().all()

        items = [self._message_to_thread_item(m, thread_id) for m in messages]
        has_more = offset + len(messages) < total

        return Page(
            data=items,
            has_more=has_more,
            first_id=items[0].id if items else None,
            last_id=items[-1].id if items else None,
        )

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Add an item to a thread."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]
        existing_conv_id: int | None = context.get("conversation_id")  # From URL param

        try:
            conv_id = int(thread_id)
        except ValueError:
            # Check if we have a cached mapping for this temp ID
            if thread_id in self._thread_id_map:
                conv_id = self._thread_id_map[thread_id]
                logger.debug(f"Using cached conversation ID {conv_id} for thread {thread_id}")
            elif existing_conv_id:
                # Use existing conversation from URL param
                conversation = await session.get(Conversation, existing_conv_id)
                if conversation and conversation.user_id == user_id:
                    conv_id = conversation.id
                    self._thread_id_map[thread_id] = conv_id
                    logger.info(f"Mapped thread {thread_id} to existing conversation {conv_id} in add_thread_item")
                else:
                    # Conversation not found or wrong user - create new
                    conversation = Conversation(user_id=user_id)
                    session.add(conversation)
                    await session.commit()
                    await session.refresh(conversation)
                    conv_id = conversation.id
                    self._thread_id_map[thread_id] = conv_id
                    logger.info(f"Created new conversation {conv_id} for thread {thread_id}")
            else:
                # No mapping found - create new conversation
                conversation = Conversation(user_id=user_id)
                session.add(conversation)
                await session.commit()
                await session.refresh(conversation)
                conv_id = conversation.id
                # Store the mapping
                self._thread_id_map[thread_id] = conv_id
                logger.info(f"Created new conversation {conv_id} for thread {thread_id} in add_thread_item")

        # Verify access
        conversation = await session.get(Conversation, conv_id)
        if not conversation or conversation.user_id != user_id:
            logger.warning(f"Access denied to conversation {conv_id} for user {user_id}")
            return

        # Create message from thread item
        message = self._thread_item_to_message(conv_id, user_id, item)
        session.add(message)
        await session.commit()
        await session.refresh(message)

        # Update item ID to real DB ID
        item.id = str(message.id)

        # Update conversation title from first user message
        if not conversation.title and message.role == "user":
            # Use first 100 chars of message as title
            conversation.title = message.content[:100]
            logger.info(f"Set conversation {conv_id} title from first message: {conversation.title}")

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        await session.commit()

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Upsert a thread item."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            msg_id = int(item.id)
            message = await session.get(Message, msg_id)
            if message:
                # Verify access via conversation
                conversation = await session.get(Conversation, message.conversation_id)
                if conversation and conversation.user_id == user_id:
                    # Update message
                    message.content = self._extract_content(item)
                    await session.commit()
                    return
        except ValueError:
            pass

        # Item doesn't exist - add it
        await self.add_thread_item(thread_id, item, context)

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> ThreadItem | None:
        """Load a single thread item."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            msg_id = int(item_id)
        except ValueError:
            return None

        message = await session.get(Message, msg_id)
        if not message:
            return None

        # Verify access via conversation
        conversation = await session.get(Conversation, message.conversation_id)
        if not conversation or conversation.user_id != user_id:
            return None

        return self._message_to_thread_item(message, thread_id)

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> None:
        """Delete a thread item."""
        session: AsyncSession = context["session"]
        user_id: str = context["user_id"]

        try:
            msg_id = int(item_id)
        except ValueError:
            return

        message = await session.get(Message, msg_id)
        if not message:
            return

        # Verify access via conversation
        conversation = await session.get(Conversation, message.conversation_id)
        if not conversation or conversation.user_id != user_id:
            return

        await session.delete(message)
        await session.commit()

    # =====================================================
    # Attachment Operations (not used but required)
    # =====================================================

    async def save_attachment(
        self,
        attachment: Attachment,
        context: dict,
    ) -> None:
        """Save attachment metadata. Not implemented."""
        pass

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict,
    ) -> Attachment | None:
        """Load attachment. Not implemented."""
        return None

    async def delete_attachment(
        self,
        attachment_id: str,
        context: dict,
    ) -> None:
        """Delete attachment. Not implemented."""
        pass

    # =====================================================
    # Helper Methods
    # =====================================================

    def _message_to_thread_item(self, message: Message, thread_id: str) -> ThreadItem:
        """Convert our Message model to ChatKit ThreadItem."""
        if message.role == "user":
            return UserMessageItem(
                id=str(message.id),
                thread_id=thread_id,
                created_at=message.created_at,
                type="user_message",
                content=[UserMessageTextContent(type="input_text", text=message.content)],
                attachments=[],
                quoted_text=None,
                inference_options=InferenceOptions(),
            )
        else:
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=thread_id,
                created_at=message.created_at,
                type="assistant_message",
                content=[AssistantMessageContent(type="output_text", text=message.content, annotations=[])],
            )

    def _thread_item_to_message(self, conversation_id: int, user_id: str, item: ThreadItem) -> Message:
        """Convert ChatKit ThreadItem to our Message model."""
        # Determine role from item type
        if hasattr(item, 'type'):
            role = "user" if item.type == "user_message" else "assistant"
        else:
            role = "user"

        content = self._extract_content(item)

        return Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
        )

    def _extract_content(self, item: ThreadItem) -> str:
        """Extract text content from a ThreadItem."""
        content = getattr(item, "content", None)
        if not content:
            return ""

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            texts = []
            for part in content:
                if isinstance(part, dict):
                    # Handle both input_text and output_text types
                    if part.get("type") in ("input_text", "output_text", "text"):
                        texts.append(part.get("text", ""))
                elif hasattr(part, "text"):
                    texts.append(part.text)
            return "".join(texts)

        return str(content)
