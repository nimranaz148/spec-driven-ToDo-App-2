"""ChatKit Server implementation that integrates with our existing AI agent.

This server implements the ChatKitServer abstract class to provide:
- Thread management via our Store
- Message processing via our existing OpenAI Agents SDK + MCP integration
- SSE streaming responses compatible with ChatKit React frontend
"""

import logging
from typing import AsyncIterator
from datetime import datetime

from chatkit.server import ChatKitServer, StreamOptions
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    ThreadItemAddedEvent,
    ThreadItemDoneEvent,
    ThreadItemUpdatedEvent,
    AssistantMessageItem,
    AssistantMessageContentPartTextDelta,
    AssistantMessageContentPartAdded,
    AssistantMessageContent,
)
from agents import Agent, Runner, ItemHelpers
from agents.mcp import MCPServerStreamableHttp
from agents.items import MessageOutputItem, ToolCallItem, ToolCallOutputItem
from openai.types.responses import ResponseTextDeltaEvent

from src.chatkit.store import TodoChatKitStore
from src.agent.config import get_gemini_model, get_mcp_server_url
from src.agent.prompts import get_system_prompt

logger = logging.getLogger(__name__)


class TodoChatKitServer(ChatKitServer[dict]):
    """ChatKit Server implementation for Todo AI Chatbot.

    This server:
    1. Uses TodoChatKitStore for thread/item persistence
    2. Integrates with our existing OpenAI Agents SDK agent
    3. Connects to the MCP server for task operations
    4. Streams responses compatible with ChatKit React frontend
    """

    def __init__(self, store: TodoChatKitStore):
        super().__init__(store=store)
        self._store = store

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Process a user message and stream the AI response.

        This method:
        1. Gets the user context (user_id, session)
        2. Loads conversation history
        3. Runs our AI agent with MCP integration
        4. Streams the response as ChatKit events

        Args:
            thread: The thread metadata being responded to
            input_user_message: The user's message (or None for new thread)
            context: Dict containing session and user_id

        Yields:
            ThreadStreamEvent instances for the ChatKit frontend
        """
        user_id: str = context["user_id"]

        logger.info(f"Processing message for user {user_id} in thread {thread.id}")

        # Get user message content
        message_text = ""
        if input_user_message:
            content = input_user_message.content
            if content:
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "input_text":
                            message_text = part.get("text", "")
                            break
                    elif hasattr(part, "text"):
                        message_text = part.text
                        break

        if not message_text:
            logger.warning("No message content found in user message")
            return

        # Load conversation history from store
        items_page = await self._store.load_thread_items(
            thread.id, after=None, limit=100, order="asc", context=context
        )
        history = []
        for item in items_page.data:
            role = "user" if item.type == "user_message" else "assistant"
            content = self._store._extract_content(item)
            if content:
                history.append({"role": role, "content": content})

        logger.info(f"Loaded {len(history)} messages from history")

        # Build agent input - history + current message
        input_messages = history + [{"role": "user", "content": message_text}]

        # Pass user_id in MCP URL for task isolation
        mcp_url = get_mcp_server_url(user_id=user_id)
        logger.debug(f"Connecting to MCP server at {mcp_url}")

        try:
            # Use native MCP integration via async context manager
            async with MCPServerStreamableHttp(
                name="Todo MCP Server",
                params={"url": mcp_url, "timeout": 30},
                client_session_timeout_seconds=30,
                cache_tools_list=True,
            ) as mcp_server:
                # Create agent with MCP server attached
                agent = Agent(
                    name="TodoBot",
                    instructions=get_system_prompt(),
                    model=get_gemini_model(),
                    mcp_servers=[mcp_server],
                )

                # Run agent with streaming
                result = Runner.run_streamed(
                    agent,
                    input=input_messages,
                )

                # Create assistant message item for streaming
                item_id = self._store.generate_item_id("message", thread, context)
                # Create initial content part - use proper typed object
                initial_content = AssistantMessageContent(
                    type="output_text",
                    text="",
                    annotations=[],
                )
                assistant_item = AssistantMessageItem(
                    id=item_id,
                    thread_id=thread.id,
                    created_at=datetime.utcnow(),
                    type="assistant_message",
                    content=[initial_content],
                )

                # Yield initial item added event
                yield ThreadItemAddedEvent(
                    type="thread.item.added",
                    item=assistant_item,
                )

                # Track streamed content
                full_content = ""
                received_streaming_deltas = False  # Track if we got text from streaming
                processed_message_output_ids = set()  # Track processed message_output_item IDs to prevent duplicates

                # Stream events from agent
                async for event in result.stream_events():
                    event_type = event.type
                    logger.debug(f"Stream event type: {event_type}, data type: {type(event.data) if hasattr(event, 'data') else 'N/A'}")

                    # Handle text delta events
                    if event_type == "raw_response_event":
                        logger.debug(f"Raw response event data: {type(event.data)}")
                        if isinstance(event.data, ResponseTextDeltaEvent):
                            delta_text = event.data.delta
                            if delta_text:
                                received_streaming_deltas = True
                                logger.debug(f"Text delta: {delta_text[:50]}...")
                                full_content += delta_text
                                # Update assistant item content - use proper typed object
                                assistant_item.content = [AssistantMessageContent(
                                    type="output_text",
                                    text=full_content,
                                    annotations=[],
                                )]
                                # Yield streaming delta event
                                yield ThreadItemUpdatedEvent(
                                    type="thread.item.updated",
                                    item_id=item_id,
                                    update=AssistantMessageContentPartTextDelta(
                                        type="assistant_message.content_part.text_delta",
                                        content_index=0,
                                        delta=delta_text,
                                    ),
                                )

                    # Handle run item events (tool calls, message outputs)
                    elif event_type == "run_item_stream_event":
                        item = event.item
                        logger.debug(f"Run item stream event: item type = {item.type}")

                        if item.type == "message_output_item":
                            # Get item ID to track if we've already processed this
                            message_item_id = getattr(item, 'id', None) or hash(str(item))

                            # Skip if we already processed this exact message_output_item
                            if message_item_id in processed_message_output_ids:
                                logger.debug(f"Skipping duplicate message_output_item with ID {message_item_id}")
                                continue

                            # Skip if we already received streaming deltas (avoid duplicates)
                            if received_streaming_deltas:
                                logger.debug("Skipping message_output_item - already have streaming content")
                                processed_message_output_ids.add(message_item_id)
                                continue

                            # Mark as processed
                            processed_message_output_ids.add(message_item_id)

                            # Extract text from message (fallback for non-streaming)
                            text = ItemHelpers.text_message_output(item)
                            if text and text != full_content:
                                new_text = text[len(full_content):] if text.startswith(full_content) else text
                                full_content = text
                                # Update content with proper typed object
                                assistant_item.content = [AssistantMessageContent(
                                    type="output_text",
                                    text=full_content,
                                    annotations=[],
                                )]
                                # Yield streaming delta event for non-streamed text
                                if new_text:
                                    yield ThreadItemUpdatedEvent(
                                        type="thread.item.updated",
                                        item_id=item_id,
                                        update=AssistantMessageContentPartTextDelta(
                                            type="assistant_message.content_part.text_delta",
                                            content_index=0,
                                            delta=new_text,
                                        ),
                                    )

                # Log what we collected
                logger.info(f"Stream completed. full_content length: {len(full_content)}, final_output: {result.final_output}")

                # Final content update - if we didn't stream anything, use final_output
                if not full_content and result.final_output:
                    logger.info(f"Using final_output: {str(result.final_output)[:100]}...")
                    full_content = str(result.final_output)
                    # Yield a single delta with the full content
                    yield ThreadItemUpdatedEvent(
                        type="thread.item.updated",
                        item_id=item_id,
                        update=AssistantMessageContentPartTextDelta(
                            type="assistant_message.content_part.text_delta",
                            content_index=0,
                            delta=full_content,
                        ),
                    )

                # Update assistant item content with proper typed objects
                if full_content:
                    assistant_item.content = [AssistantMessageContent(
                        type="output_text",
                        text=full_content,
                        annotations=[],
                    )]
                elif not assistant_item.content or (assistant_item.content and assistant_item.content[0].text == ""):
                    # Fallback message if nothing was generated
                    full_content = "I'm sorry, I wasn't able to generate a response. Please try again."
                    assistant_item.content = [AssistantMessageContent(
                        type="output_text",
                        text=full_content,
                        annotations=[],
                    )]

                # Yield done event
                yield ThreadItemDoneEvent(
                    type="thread.item.done",
                    item=assistant_item,
                )

        except Exception as e:
            logger.error(f"Error in respond: {e}", exc_info=True)
            # Yield an error as a message with proper typed content
            error_content = AssistantMessageContent(
                type="output_text",
                text=f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                annotations=[],
            )
            error_item = AssistantMessageItem(
                id=self._store.generate_item_id("message", thread, context),
                thread_id=thread.id,
                created_at=datetime.utcnow(),
                type="assistant_message",
                content=[error_content],
            )
            yield ThreadItemAddedEvent(type="thread.item.added", item=error_item)
            yield ThreadItemDoneEvent(type="thread.item.done", item=error_item)

    def get_stream_options(
        self,
        thread: ThreadMetadata,
        context: dict,
    ) -> StreamOptions:
        """Return stream options for the server."""
        return StreamOptions(allow_cancel=True)

    async def handle_stream_cancelled(
        self,
        thread: ThreadMetadata,
        context: dict,
    ) -> None:
        """Handle stream cancellation."""
        logger.info(f"Stream cancelled for thread {thread.id}")
        # Default behavior is fine - persist any partial messages
        await super().handle_stream_cancelled(thread, context)
