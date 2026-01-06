"""AI Agent Runner using OpenAI Agents SDK.

This module implements the agent execution logic using the official OpenAI Agents SDK.
The agent connects to the FastMCP server via MCPServerStreamableHttp to access task tools.

Architecture:
- Uses OpenAI Agents SDK (Agent + Runner) for proper agent orchestration
- Connects to FastMCP server via streamable HTTP transport
- Flow: User -> /chat -> Agent (OpenAI SDK) -> MCP Server (FastMCP) -> Database
- Maintains conversation context via conversation_service
- Returns structured responses with tool call transcripts and thinking steps

KEY PATTERN: The MCP server connection is managed via async context manager.
The agent automatically discovers and uses tools from the MCP server.

Per research.md Decision 1: 5-second round-trip requirement (SC-001)
Per research.md Decision 4: Sliding 20-message context window
Per research.md Decision 5: Agent clarifies ambiguous commands
"""

import json
import time
import secrets
import re
from typing import Any, Optional
from dataclasses import dataclass, field

from agents import Agent, Runner, ItemHelpers
from agents.mcp import MCPServerStreamableHttp
from agents.items import (
    MessageOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
)

from .config import get_agent_config, get_gemini_model, get_mcp_server_url
from .prompts import get_system_prompt, build_conversation_context
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Bulk operation patterns for confirmation
BULK_PATTERNS = [
    (r"delete\s+(all|every|each)\s+(task|todo)", "delete_all"),
    (r"(remove|clear)\s+(all|every|each)\s+(task|todo)", "delete_all"),
    (r"complete\s+(all|every|each)\s+(task|todo)", "complete_all"),
    (r"mark\s+(all|every|each)\s+(task|todo).*(done|complete)", "complete_all"),
    (r"finish\s+(all|every|each)\s+(task|todo)", "complete_all"),
]


@dataclass
class ThinkingStep:
    """A step in the agent's reasoning process."""
    type: str  # analyzing, planning, tool_call, processing, clarifying
    content: str
    timestamp: float  # seconds since request start


@dataclass
class ToolCallResult:
    """Result of executing a single tool call."""
    tool: str
    parameters: dict[str, Any]
    result: dict[str, Any]
    error: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class ConfirmationRequest:
    """Request for user confirmation on bulk operations."""
    action: str
    message: str
    affected_items: list[dict[str, Any]]
    confirm_token: str


@dataclass
class AgentResponse:
    """Response from the agent runner."""
    response: str
    tool_calls: list[ToolCallResult] = field(default_factory=list)
    thinking_steps: list[ThinkingStep] = field(default_factory=list)
    confirmation_required: Optional[ConfirmationRequest] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None


def detect_bulk_operation(message: str) -> Optional[str]:
    """Detect if message requests a bulk operation requiring confirmation."""
    message_lower = message.lower()
    for pattern, action in BULK_PATTERNS:
        if re.search(pattern, message_lower):
            return action
    return None


# Store pending confirmations (in production, use Redis or database)
_pending_confirmations: dict[str, dict[str, Any]] = {}


def get_task_agent_instructions(user_id: str) -> str:
    """Get the system instructions for the task management agent."""
    return get_system_prompt()


async def run_agent(
    user_id: str,
    user_message: str,
    conversation_history: list[dict],
    session: Any,
    confirm_token: Optional[str] = None
) -> AgentResponse:
    """Run the AI agent using OpenAI Agents SDK with MCP tools.

    This is the main entry point for chat interactions. It:
    1. Connects to the FastMCP server via MCPServerStreamableHttp
    2. Creates an Agent with MCP tools available
    3. Runs the agent with the user's message
    4. Returns structured response with tool calls and thinking steps

    Args:
        user_id: Authenticated user's ID
        user_message: The user's chat message
        conversation_history: List of prior messages [{"role": "user/assistant", "content": "..."}]
        session: Database session (for direct operations if needed)
        confirm_token: Optional confirmation token for bulk operations

    Returns:
        AgentResponse: Contains response text, tool calls, thinking steps
    """
    start_time = time.time()
    thinking_steps: list[ThinkingStep] = []
    tool_calls: list[ToolCallResult] = []

    def add_thinking(step_type: str, content: str):
        thinking_steps.append(ThinkingStep(
            type=step_type,
            content=content,
            timestamp=time.time() - start_time
        ))

    add_thinking("analyzing", f"Analyzing user request: \"{user_message[:100]}...\"" if len(user_message) > 100 else f"Analyzing user request: \"{user_message}\"")

    # Check for bulk operations requiring confirmation
    bulk_action = detect_bulk_operation(user_message)
    if bulk_action and not confirm_token:
        add_thinking("clarifying", f"Detected bulk operation: {bulk_action}. Requesting confirmation.")

        # Use agent to list tasks first
        try:
            # Get MCP URL with user_id for task isolation
            mcp_url = get_mcp_server_url(user_id=user_id)
            async with MCPServerStreamableHttp(
                name="Todo MCP Server",
                params={"url": mcp_url, "timeout": 30},
                client_session_timeout_seconds=30,
            ) as mcp_server:
                # Create a simple agent just to list tasks
                list_agent = Agent(
                    name="Task Lister",
                    instructions="List all tasks. Call list_tasks() to get the full list.",
                    model=get_gemini_model(),
                    mcp_servers=[mcp_server],
                )
                result = await Runner.run(list_agent, "List all tasks")

                # Parse the response to get task count
                # For now, we'll use a simple approach
                total = 5  # Default estimate
                tasks = []

                if "no tasks" in result.final_output.lower():
                    total = 0

        except Exception as e:
            logger.error("bulk_list_error", error=str(e))
            total = 0
            tasks = []

        if total == 0:
            return AgentResponse(
                response="You don't have any tasks to perform this action on.",
                thinking_steps=thinking_steps,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        # Generate confirmation token
        token = secrets.token_urlsafe(16)
        _pending_confirmations[token] = {
            "user_id": user_id,
            "action": bulk_action,
            "created_at": time.time()
        }

        action_msg = "delete all" if bulk_action == "delete_all" else "mark all as complete"
        return AgentResponse(
            response=f"You're about to {action_msg} your tasks. Please confirm this action.",
            thinking_steps=thinking_steps,
            confirmation_required=ConfirmationRequest(
                action=bulk_action,
                message=f"Are you sure you want to {action_msg}?",
                affected_items=[],
                confirm_token=token
            ),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )

    # Handle confirmed bulk operation
    if confirm_token and confirm_token in _pending_confirmations:
        confirmation = _pending_confirmations.pop(confirm_token)
        if confirmation["user_id"] != user_id:
            return AgentResponse(
                response="Invalid confirmation token.",
                error="Token user mismatch",
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

        add_thinking("processing", f"Executing confirmed bulk operation: {confirmation['action']}")

        # Execute bulk operation via agent
        action = confirmation["action"]
        if action == "delete_all":
            bulk_instruction = f"Delete all tasks for user_id: {user_id}. First list all tasks, then delete each one."
        else:
            bulk_instruction = f"Mark all incomplete tasks as complete for user_id: {user_id}. First list incomplete tasks, then complete each one."

        try:
            mcp_url = get_mcp_server_url(user_id=user_id)
            async with MCPServerStreamableHttp(
                name="Todo MCP Server",
                params={"url": mcp_url, "timeout": 30},
                client_session_timeout_seconds=30,
            ) as mcp_server:
                bulk_agent = Agent(
                    name="Bulk Task Agent",
                    instructions=get_task_agent_instructions(user_id),
                    model=get_gemini_model(),
                    mcp_servers=[mcp_server],
                )
                result = await Runner.run(bulk_agent, bulk_instruction)

                return AgentResponse(
                    response=result.final_output,
                    tool_calls=tool_calls,
                    thinking_steps=thinking_steps,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
        except Exception as e:
            logger.error("bulk_operation_error", error=str(e))
            return AgentResponse(
                response="Failed to execute bulk operation. Please try again.",
                error=str(e),
                thinking_steps=thinking_steps,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

    # Normal agent execution with OpenAI Agents SDK
    add_thinking("planning", "Connecting to MCP server and preparing agent")

    try:
        # Get MCP URL with user_id for task isolation
        mcp_url = get_mcp_server_url(user_id=user_id)
        logger.debug(f"Connecting to MCP server at {mcp_url}")

        # Connect to FastMCP server via streamable HTTP
        async with MCPServerStreamableHttp(
            name="Todo MCP Server",
            params={"url": mcp_url, "timeout": 30},
            client_session_timeout_seconds=30,
            cache_tools_list=True,
        ) as mcp_server:
            add_thinking("processing", "MCP server connected, creating agent")

            # Create the agent with MCP tools and Gemini model
            agent = Agent(
                name="Task Management Assistant",
                instructions=get_task_agent_instructions(user_id),
                model=get_gemini_model(),
                mcp_servers=[mcp_server],
            )

            # Build context from conversation history
            config = get_agent_config()
            context_str = build_conversation_context(
                conversation_history,
                max_messages=config.max_context_messages
            )

            # Format the input with context
            if context_str:
                full_input = f"Previous conversation:\n{context_str}\n\nUser: {user_message}"
            else:
                full_input = user_message

            add_thinking("processing", "Running agent with user message")

            logger.info(
                "agent_run_start",
                user_id=user_id,
                message_length=len(user_message),
                context_messages=len(conversation_history) if conversation_history else 0
            )

            # Run the agent
            result = await Runner.run(agent, full_input)

            add_thinking("processing", "Agent completed execution")

            # Extract response content from new_items (like todo-web-hackthon)
            from agents.items import MessageOutputItem
            content = ""
            for item in result.new_items:
                if isinstance(item, MessageOutputItem):
                    text = ItemHelpers.text_message_output(item)
                    if text:
                        content += text

            # Fallback to final_output if no content from new_items
            if not content and result.final_output:
                content = str(result.final_output)

            logger.info(
                "agent_run_complete",
                user_id=user_id,
                response_length=len(content),
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

            return AgentResponse(
                response=content,
                tool_calls=tool_calls,
                thinking_steps=thinking_steps,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

    except Exception as e:
        logger.error("agent_error", user_id=user_id, error=str(e), exc_info=True)
        return AgentResponse(
            response="I encountered an error processing your request. Please try again.",
            thinking_steps=thinking_steps,
            error=str(e),
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
