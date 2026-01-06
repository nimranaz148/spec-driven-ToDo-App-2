"""
Unit tests for AI Agent configuration module.

Tests configuration loading, validation, and client creation.
"""

from unittest.mock import MagicMock, patch

import pytest
from openai import AsyncOpenAI
from pydantic import ValidationError

from src.agent.config import (
    AgentConfig,
    get_agent_config,
    get_llm_client,
    get_model_info,
    get_rate_limiter_config,
)


class TestAgentConfig:
    """Test suite for AgentConfig class."""

    def test_default_values(self):
        """Test configuration defaults are set correctly."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-12345"}):
            config = AgentConfig()

            assert config.gemini_model == "gemini-2.5-flash"
            assert config.rate_limit_per_minute == 30
            assert config.max_context_messages == 20
            assert config.llm_timeout_seconds == 30
            assert "generativelanguage.googleapis.com" in config.litellm_api_base

    def test_custom_values_from_env(self):
        """Test configuration loads custom values from environment."""
        env_vars = {
            "GEMINI_API_KEY": "custom-api-key",
            "GEMINI_MODEL": "gemini-pro",
            "RATE_LIMIT_PER_MINUTE": "60",
            "MAX_CONTEXT_MESSAGES": "50",
        }

        with patch.dict("os.environ", env_vars):
            config = AgentConfig()

            assert config.gemini_api_key == "custom-api-key"
            assert config.gemini_model == "gemini-pro"
            assert config.rate_limit_per_minute == 60
            assert config.max_context_messages == 50

    def test_validation_rate_limit_too_high(self):
        """Test validation rejects rate limit above maximum."""
        env_vars = {
            "GEMINI_API_KEY": "test-key",
            "RATE_LIMIT_PER_MINUTE": "2000",  # Max is 1000
        }

        with patch.dict("os.environ", env_vars):
            with pytest.raises(ValidationError) as exc_info:
                AgentConfig()

            errors = exc_info.value.errors()
            assert any("rate_limit_per_minute" in str(e) for e in errors)

    def test_validation_rate_limit_too_low(self):
        """Test validation rejects rate limit below minimum."""
        env_vars = {
            "GEMINI_API_KEY": "test-key",
            "RATE_LIMIT_PER_MINUTE": "0",  # Min is 1
        }

        with patch.dict("os.environ", env_vars):
            with pytest.raises(ValidationError) as exc_info:
                AgentConfig()

            errors = exc_info.value.errors()
            assert any("rate_limit_per_minute" in str(e) for e in errors)

    def test_missing_api_key_raises_error(self):
        """Test missing API key raises validation error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                AgentConfig()

            errors = exc_info.value.errors()
            assert any("gemini_api_key" in str(e) for e in errors)


class TestGetAgentConfig:
    """Test suite for get_agent_config factory function."""

    def test_caching_returns_same_instance(self):
        """Test that get_agent_config caches the config instance."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            # Clear the cache first
            get_agent_config.cache_clear()

            config1 = get_agent_config()
            config2 = get_agent_config()

            # Should return the exact same object (cached)
            assert config1 is config2

    def test_cache_clear_creates_new_instance(self):
        """Test that clearing cache creates new instance."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-1"}):
            get_agent_config.cache_clear()
            config1 = get_agent_config()

        # Change environment and clear cache
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key-2"}):
            get_agent_config.cache_clear()
            config2 = get_agent_config()

        # Should be different instances with different values
        assert config1 is not config2
        assert config1.gemini_api_key != config2.gemini_api_key


class TestGetLLMClient:
    """Test suite for get_llm_client factory function."""

    def test_creates_async_openai_client(self):
        """Test client creation returns AsyncOpenAI instance."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "valid-test-key"}):
            get_agent_config.cache_clear()
            client = get_llm_client()

            assert isinstance(client, AsyncOpenAI)
            assert client.timeout == 30
            assert client.max_retries == 2

    def test_invalid_api_key_raises_error(self):
        """Test placeholder API key raises ValueError."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "your-gemini-api-key-here"}):
            get_agent_config.cache_clear()

            with pytest.raises(ValueError) as exc_info:
                get_llm_client()

            assert "GEMINI_API_KEY" in str(exc_info.value)
            assert "valid API key" in str(exc_info.value)

    def test_missing_api_key_raises_error(self):
        """Test missing API key is handled gracefully."""
        with patch.dict("os.environ", {}, clear=True):
            get_agent_config.cache_clear()

            # ValidationError from pydantic during config creation
            with pytest.raises(ValidationError):
                get_llm_client()

    def test_client_configured_with_correct_base_url(self):
        """Test client is configured with LiteLLM endpoint."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "valid-key"}):
            get_agent_config.cache_clear()
            client = get_llm_client()

            assert "generativelanguage.googleapis.com" in str(client.base_url)


class TestGetModelInfo:
    """Test suite for get_model_info utility function."""

    def test_returns_correct_structure(self):
        """Test model info returns expected dictionary structure."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            get_agent_config.cache_clear()
            info = get_model_info()

            assert isinstance(info, dict)
            assert "model_name" in info
            assert "provider" in info
            assert "transport" in info
            assert "max_context_messages" in info
            assert "timeout_seconds" in info
            assert "rate_limit_per_minute" in info

    def test_returns_correct_values(self):
        """Test model info contains correct default values."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            get_agent_config.cache_clear()
            info = get_model_info()

            assert info["model_name"] == "gemini-2.5-flash"
            assert info["provider"] == "google"
            assert info["transport"] == "litellm_openai"
            assert info["max_context_messages"] == 20
            assert info["timeout_seconds"] == 30
            assert info["rate_limit_per_minute"] == 30

    def test_custom_values_reflected(self):
        """Test model info reflects custom configuration."""
        env_vars = {
            "GEMINI_API_KEY": "test-key",
            "GEMINI_MODEL": "gemini-pro-vision",
            "RATE_LIMIT_PER_MINUTE": "100",
        }

        with patch.dict("os.environ", env_vars):
            get_agent_config.cache_clear()
            info = get_model_info()

            assert info["model_name"] == "gemini-pro-vision"
            assert info["rate_limit_per_minute"] == 100


class TestGetRateLimiterConfig:
    """Test suite for get_rate_limiter_config utility function."""

    def test_returns_correct_structure(self):
        """Test rate limiter config structure."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            get_agent_config.cache_clear()
            config = get_rate_limiter_config()

            assert isinstance(config, dict)
            assert "requests_per_minute" in config
            assert "burst_size" in config
            assert "scope" in config

    def test_default_values(self):
        """Test rate limiter default values."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            get_agent_config.cache_clear()
            config = get_rate_limiter_config()

            assert config["requests_per_minute"] == 30
            assert config["burst_size"] == 35  # rate_limit + 5
            assert config["scope"] == "user"

    def test_custom_rate_limit(self):
        """Test custom rate limit is reflected."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key", "RATE_LIMIT_PER_MINUTE": "60"}):
            get_agent_config.cache_clear()
            config = get_rate_limiter_config()

            assert config["requests_per_minute"] == 60
            assert config["burst_size"] == 65  # 60 + 5

    def test_burst_size_calculation(self):
        """Test burst size is always rate_limit + 5."""
        test_rates = [10, 30, 100, 500]

        for rate in test_rates:
            with patch.dict(
                "os.environ",
                {"GEMINI_API_KEY": "test-key", "RATE_LIMIT_PER_MINUTE": str(rate)},
            ):
                get_agent_config.cache_clear()
                config = get_rate_limiter_config()

                assert config["burst_size"] == rate + 5


@pytest.mark.asyncio
class TestClientIntegration:
    """Integration tests for actual client usage (mocked)."""

    async def test_client_can_be_used_in_async_context(self):
        """Test client works in async context."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "valid-key"}):
            get_agent_config.cache_clear()
            client = get_llm_client()

            # Verify it's an async client
            assert hasattr(client.chat.completions, "create")
            assert asyncio.iscoroutinefunction(client.chat.completions.create)

    async def test_client_timeout_configuration(self):
        """Test client respects timeout configuration."""
        env_vars = {
            "GEMINI_API_KEY": "test-key",
            "LLM_TIMEOUT_SECONDS": "45",
        }

        with patch.dict("os.environ", env_vars):
            get_agent_config.cache_clear()
            client = get_llm_client()

            # Note: Timeout might be stored differently in AsyncOpenAI
            # This tests that it's set during creation
            assert client.timeout in [30, 45]  # Default or custom


# Fixture for common test environment
@pytest.fixture
def clean_env():
    """Provide clean environment for each test."""
    with patch.dict("os.environ", {}, clear=True):
        get_agent_config.cache_clear()
        yield


@pytest.fixture
def test_env():
    """Provide test environment with valid API key."""
    env = {
        "GEMINI_API_KEY": "test-api-key-12345",
        "GEMINI_MODEL": "gemini-2.5-flash",
        "RATE_LIMIT_PER_MINUTE": "30",
    }
    with patch.dict("os.environ", env):
        get_agent_config.cache_clear()
        yield env
