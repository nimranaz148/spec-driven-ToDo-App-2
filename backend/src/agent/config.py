"""
AI Agent Configuration Module

Configures the AI agent using OpenAI Agents SDK with MCP tools.

Per research.md Decision 1:
- Uses OpenAI Agents SDK for agent orchestration
- Connects to FastMCP server for task management tools
- Supports 5-second round-trip requirement (SC-001)

Architecture:
- Uses OpenAI Agents SDK (Agent + Runner) with native MCP support
- Gemini accessed via OpenAI-compatible endpoint
- OpenAIChatCompletionsModel wraps the Gemini client

Environment Variables:
- GEMINI_API_KEY: API key for Google Gemini (required)
- RATE_LIMIT_PER_MINUTE: Rate limit per user (default: 30)
- MCP_SERVER_URL: URL of the MCP server (default: http://localhost:8001)
"""

from functools import lru_cache
from typing import Any

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Gemini's OpenAI-compatible endpoint
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class AgentConfig(BaseSettings):
    """
    Type-safe configuration for AI agent using pydantic-settings.

    Loads from environment variables with validation.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Gemini API Configuration (required)
    gemini_api_key: str = Field(
        default="",
        description="Google Gemini API key for LLM access",
    )

    gemini_model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model identifier (default: gemini-2.5-flash)",
    )

    # MCP Server Configuration
    # MCP server runs on port 8001 with /mcp path for streamable HTTP transport
    mcp_server_url: str = Field(
        default="http://localhost:8001/mcp",
        description="URL of the MCP server endpoint (FastMCP HTTP transport on separate port)",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=30,
        ge=1,
        le=1000,
        description="Maximum requests per user per minute",
    )

    # Conversation Context Window
    max_context_messages: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Maximum messages to send in sliding context window",
    )

    # Timeout Configuration
    llm_timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for LLM API calls in seconds",
    )


@lru_cache
def get_agent_config() -> AgentConfig:
    """
    Get cached agent configuration.

    Returns:
        AgentConfig: Validated configuration instance

    Raises:
        ValidationError: If required environment variables are missing or invalid
    """
    return AgentConfig()


def get_gemini_client() -> AsyncOpenAI:
    """
    Create AsyncOpenAI client configured for Gemini API.

    Uses Gemini's OpenAI-compatible endpoint which works
    with the OpenAI Agents SDK.

    Returns:
        AsyncOpenAI: Client configured for Gemini's OpenAI-compatible endpoint

    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    config = get_agent_config()

    # Validate API key exists
    if not config.gemini_api_key or config.gemini_api_key == "your-gemini-api-key-here":
        raise ValueError(
            "GEMINI_API_KEY environment variable must be set to a valid API key. "
            "Get your key from https://makersuite.google.com/app/apikey"
        )

    return AsyncOpenAI(
        api_key=config.gemini_api_key,
        base_url=GEMINI_BASE_URL,
    )


def get_gemini_model(model_name: str | None = None) -> OpenAIChatCompletionsModel:
    """
    Create OpenAIChatCompletionsModel wrapper for Gemini.

    This uses Gemini's OpenAI-compatible endpoint which works
    with the OpenAI Agents SDK's OpenAIChatCompletionsModel wrapper.

    Args:
        model_name: Optional model name override. Defaults to settings.gemini_model

    Returns:
        OpenAIChatCompletionsModel: Model configured for Gemini
    """
    config = get_agent_config()
    client = get_gemini_client()
    model = model_name or config.gemini_model

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=client,
    )


def get_mcp_server_url(user_id: str | None = None) -> str:
    """
    Get the MCP server URL from settings.

    Args:
        user_id: Optional user ID to include in the URL for per-user context.
                 When provided, appended as query parameter for task isolation.

    Returns:
        str: MCP server URL for Streamable HTTP transport.
              FastMCP HTTP transport serves at the root when no path specified.
    """
    config = get_agent_config()
    base_url = config.mcp_server_url.rstrip("/")
    if user_id:
        # Include user_id as query parameter for task isolation
        return f"{base_url}?user_id={user_id}"
    return base_url


# Alias for backward compatibility
def get_llm_client() -> AsyncOpenAI:
    """Alias for get_gemini_client for backward compatibility."""
    return get_gemini_client()


def get_rate_limiter_config() -> dict[str, Any]:
    """
    Get rate limiter configuration for agent endpoints.

    Returns:
        dict: Configuration for rate limiting middleware

    Example:
        >>> config = get_rate_limiter_config()
        >>> print(config["requests_per_minute"])
        30
    """
    config = get_agent_config()

    return {
        "requests_per_minute": config.rate_limit_per_minute,
        "burst_size": config.rate_limit_per_minute + 5,
        "scope": "user",  # Rate limit per authenticated user
    }


def get_model_info() -> dict[str, Any]:
    """
    Get information about the configured LLM model.

    Returns:
        dict: Model configuration details

    Example:
        >>> info = get_model_info()
        >>> print(f"Using model: {info['model_name']}")
        Using model: gemini-2.5-flash
    """
    config = get_agent_config()

    return {
        "model_name": config.gemini_model,
        "provider": "google",
        "transport": "openai_compatible",
        "max_context_messages": config.max_context_messages,
        "timeout_seconds": config.llm_timeout_seconds,
        "rate_limit_per_minute": config.rate_limit_per_minute,
    }


__all__ = [
    "AgentConfig",
    "get_agent_config",
    "get_gemini_client",
    "get_gemini_model",
    "get_mcp_server_url",
    "get_llm_client",
    "get_rate_limiter_config",
    "get_model_info",
    "GEMINI_BASE_URL",
]
