"""AI Agent module for natural language task management.

This module contains:
- config.py: Gemini model configuration using OpenAI-compatible endpoint
- prompts.py: System prompts and conversation context building
- runner.py: Agent execution with native MCP integration

Architecture (Native MCP Integration):
    Chat Endpoint -> Runner -> MCPServerStreamableHttp -> MCP Server -> Database

KEY INSIGHT: The OpenAI Agents SDK has NATIVE MCP support via MCPServerStreamableHttp.
The agent connects directly to the MCP server and discovers tools automatically.
"""

# Config
from .config import (
    AgentConfig,
    get_agent_config,
    get_gemini_client,
    get_gemini_model,
    get_mcp_server_url,
    get_llm_client,
    get_rate_limiter_config,
    get_model_info,
    GEMINI_BASE_URL,
)

# Prompts
from .prompts import (
    get_system_prompt,
    build_conversation_context,
    TASK_MANAGEMENT_SYSTEM_PROMPT,
)

# Runner (main API)
from .runner import (
    AgentResponse,
    ThinkingStep,
    ToolCallResult,
    ConfirmationRequest,
    run_agent,
)

__all__ = [
    # Config
    "AgentConfig",
    "get_agent_config",
    "get_gemini_client",
    "get_gemini_model",
    "get_mcp_server_url",
    "get_llm_client",
    "get_rate_limiter_config",
    "get_model_info",
    "GEMINI_BASE_URL",
    # Prompts
    "get_system_prompt",
    "build_conversation_context",
    "TASK_MANAGEMENT_SYSTEM_PROMPT",
    # Runner (main API - use these!)
    "AgentResponse",
    "ThinkingStep",
    "ToolCallResult",
    "ConfirmationRequest",
    "run_agent",
]
