# AI Agent Module

This module provides the configuration and client setup for the AI-powered chatbot using Google Gemini via AsyncOpenAI transport.

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent Config   │ ◄── Environment Variables
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AsyncOpenAI    │
│    (Client)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    LiteLLM      │ ◄── OpenAI-compatible shim
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini API     │
│ (2.5-flash)     │
└─────────────────┘
```

## Files

### `config.py`
Main configuration module that:
- Loads settings from environment variables using `pydantic-settings`
- Validates configuration with type safety
- Provides factory functions for LLM client creation
- Exports rate limiter configuration

### `__init__.py`
Module exports for convenient imports:
```python
from agent import get_llm_client, AgentConfig
```

## Environment Variables

Required in `.env` file:

```bash
# Gemini API Key (REQUIRED)
GEMINI_API_KEY=your-gemini-api-key-here

# Model Configuration
GEMINI_MODEL=gemini-2.5-flash

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## Usage

### Basic Client Setup

```python
from agent import get_llm_client

# Get configured AsyncOpenAI client
client = get_llm_client()

# Use with async/await
async def chat_with_ai(user_message: str):
    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful task assistant."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content
```

### Configuration Access

```python
from agent.config import get_agent_config, get_model_info

# Get configuration
config = get_agent_config()
print(f"Using model: {config.gemini_model}")
print(f"Rate limit: {config.rate_limit_per_minute} req/min")

# Get model info
info = get_model_info()
print(info)
# {
#   "model_name": "gemini-2.5-flash",
#   "provider": "google",
#   "transport": "litellm_openai",
#   "max_context_messages": 20,
#   "timeout_seconds": 30,
#   "rate_limit_per_minute": 30
# }
```

### Rate Limiter Configuration

```python
from agent.config import get_rate_limiter_config

# Get rate limiting settings for middleware
rate_config = get_rate_limiter_config()
# {
#   "requests_per_minute": 30,
#   "burst_size": 35,
#   "scope": "user"
# }
```

## Configuration Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `gemini_api_key` | str | *required* | Google Gemini API key |
| `gemini_model` | str | `gemini-2.5-flash` | Model identifier |
| `rate_limit_per_minute` | int | `30` | Max requests/user/minute |
| `litellm_api_base` | str | *(auto)* | LiteLLM OpenAI endpoint |
| `max_context_messages` | int | `20` | Sliding window size |
| `llm_timeout_seconds` | int | `30` | API call timeout |

## Error Handling

### Missing API Key

```python
from agent import get_llm_client

try:
    client = get_llm_client()
except ValueError as e:
    print(f"Configuration error: {e}")
    # "GEMINI_API_KEY environment variable must be set..."
```

### Validation Errors

```python
from pydantic import ValidationError
from agent.config import AgentConfig

try:
    config = AgentConfig(rate_limit_per_minute=5000)  # Too high
except ValidationError as e:
    print(e.errors())
    # [{'loc': ('rate_limit_per_minute',), 'msg': 'ensure this value is less than or equal to 1000', ...}]
```

## Design Decisions

### Decision 1: AsyncOpenAI Transport (per research.md)

**Why**: Spec requires Gemini via AsyncOpenAI to maintain SDK compatibility while leveraging Gemini's speed.

**Benefits**:
- Familiar OpenAI interface
- Works with existing tools (FastMCP, Agents SDK)
- Easy migration if switching providers
- Type-safe with modern Python async

### Decision 2: LiteLLM as Compatibility Layer

**Why**: Provides OpenAI-compatible endpoint for Gemini without custom HTTP clients.

**Benefits**:
- Handles authentication differences
- Normalizes response formats
- Provides retry logic
- Supports multiple providers (future-proofing)

### Decision 3: Pydantic Settings for Configuration

**Why**: Type-safe configuration with validation at startup.

**Benefits**:
- Catches misconfiguration early
- IDE autocomplete support
- Auto-loads from .env files
- Built-in validation rules

### Decision 4: Sliding Context Window (20 messages)

**Why**: Balance between context retention and token limits.

**Benefits**:
- Keeps prompts under Gemini limits
- Maintains conversation coherence
- Reduces latency (smaller payloads)
- Meets SC-001 (5-second response time)

## Testing

### Unit Test Example

```python
import pytest
from unittest.mock import patch
from agent.config import get_agent_config, get_llm_client

def test_agent_config_defaults():
    """Test configuration defaults."""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        config = get_agent_config()
        assert config.gemini_model == "gemini-2.5-flash"
        assert config.rate_limit_per_minute == 30
        assert config.max_context_messages == 20

def test_llm_client_creation():
    """Test LLM client factory."""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
        client = get_llm_client()
        assert client is not None
        assert client.timeout == 30
        assert client.max_retries == 2

def test_missing_api_key():
    """Test error handling for missing API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            get_llm_client()
```

### Integration Test Example

```python
import pytest
from agent import get_llm_client

@pytest.mark.asyncio
async def test_gemini_chat_completion():
    """Test actual Gemini API call (requires valid API key)."""
    client = get_llm_client()

    response = await client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "user", "content": "Say 'hello' and nothing else"}
        ],
        max_tokens=10
    )

    assert response.choices[0].message.content
    assert len(response.choices[0].message.content) > 0
```

## Performance Considerations

### Caching
- `get_agent_config()` uses `@lru_cache` to avoid re-parsing environment variables
- Client instances should be reused across requests

### Timeouts
- Default 30-second timeout for LLM calls
- 2 automatic retries on transient failures
- Adjust via `LLM_TIMEOUT_SECONDS` environment variable

### Rate Limiting
- Per-user rate limiting prevents abuse
- Burst allowance (+5) handles legitimate spikes
- Configurable via `RATE_LIMIT_PER_MINUTE`

## Future Enhancements

1. **Multi-model Support**: Add fallback to other Gemini models or providers
2. **Streaming Responses**: Implement SSE for real-time message streaming
3. **Caching Layer**: Redis cache for common queries
4. **Metrics**: Integrate with observability stack for latency tracking
5. **Cost Tracking**: Monitor token usage per user/conversation

## References

- Research Document: `specs/001-ai-chatbot/research.md`
- Specification: `specs/001-ai-chatbot/spec.md`
- Gemini API Docs: https://ai.google.dev/docs
- AsyncOpenAI: https://github.com/openai/openai-python
- LiteLLM: https://docs.litellm.ai/
