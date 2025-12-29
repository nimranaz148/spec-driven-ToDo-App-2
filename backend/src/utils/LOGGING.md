# Backend Logging & Observability

This document describes the structured logging and observability implementation for the Todo API backend.

## Overview

The backend uses **structlog** for structured JSON logging with comprehensive observability features:

- **Structured JSON logs** - All logs output as JSON to stdout
- **Request ID tracing** - Unique ID for each request across all logs
- **Response time metrics** - Track performance of every endpoint
- **Authentication logging** - Log all auth attempts (success/failure)
- **Database error logging** - Comprehensive error tracking
- **Security-first** - Never logs passwords, tokens, or JWTs

## Quick Start

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Log with structured data
logger.info("user_action", user_id="user_123", action="create_task")

# Log errors with context
logger.error("database_error", error=str(e), table="tasks")
```

## Logging Components

### 1. Structured Logger (`src/utils/logger.py`)

Provides centralized logging configuration with automatic JSON formatting and sensitive data masking.

**Features:**
- JSON output to stdout
- Automatic timestamp (ISO format)
- Log level included in every message
- Context variables (request_id, user_id)
- Sensitive data masking

**Usage:**
```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("event_name", field1="value1", field2="value2")
```

### 2. Request ID Middleware (`src/middleware/request_id.py`)

Generates a unique request ID for each incoming request and includes it in all logs.

**Features:**
- Generates unique request ID (format: `req_<16-char-hex>`)
- Accepts `X-Request-ID` header if provided
- Adds request ID to all logs in the request context
- Returns request ID in response headers
- Clears context after request completes

**Headers:**
- Request: `X-Request-ID` (optional)
- Response: `X-Request-ID` (always included)

### 3. Timing Middleware (`src/middleware/timing.py`)

Tracks response time for every API request and logs performance metrics.

**Features:**
- Records start/end time for each request
- Calculates response time in milliseconds
- Logs metrics for every request
- Warns on slow requests (> 1 second)
- Adds response time to headers

**Headers:**
- Response: `X-Response-Time: <time>ms`

**Log Fields:**
- `method` - HTTP method
- `path` - Request path
- `status_code` - Response status
- `response_time_ms` - Response time in milliseconds
- `endpoint` - Formatted as "METHOD /path"

### 4. Database Logging (`src/db.py`)

Logs all database operations and errors.

**Logged Events:**
- Transaction commits
- Database errors (with context)
- Table creation
- Connection lifecycle

**Security:**
- Never logs SQL query parameters
- Never logs sensitive data

### 5. Authentication Logging (`src/routes/auth.py`, `src/auth.py`)

Comprehensive logging of all authentication operations.

**Logged Events:**
- User registration attempts
- Login attempts (success/failure)
- Logout events
- Token verification failures
- Invalid token payloads

**Security:**
- **NEVER** logs passwords
- **NEVER** logs tokens or JWTs
- Logs email (not sensitive) for failed attempts
- Logs user_id for successful operations

## Log Format

All logs are output as JSON with the following structure:

```json
{
  "event": "user_logged_in_successfully",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "level": "info",
  "logger": "src.routes.auth",
  "request_id": "req_a1b2c3d4e5f6g7h8",
  "user_id": "user_123",
  "email": "user@example.com"
}
```

## Common Log Events

### Authentication Events

| Event | Level | Fields | Description |
|-------|-------|--------|-------------|
| `user_registration_attempt` | INFO | email | User started registration |
| `user_registered_successfully` | INFO | user_id, email | Registration completed |
| `registration_failed_user_exists` | WARNING | email, reason | User already exists |
| `user_login_attempt` | INFO | email | User started login |
| `user_logged_in_successfully` | INFO | user_id, email | Login successful |
| `login_failed` | WARNING | email, reason | Login failed |
| `user_logout_attempt` | INFO | user_id, email | User started logout |
| `user_logged_out_successfully` | INFO | user_id, email | Logout completed |
| `token_verification_failed` | WARNING | reason | JWT verification failed |

### Request Events

| Event | Level | Fields | Description |
|-------|-------|--------|-------------|
| `request_started` | INFO | method, path, client_host | Request received |
| `request_completed` | INFO | method, path, status_code | Request completed |
| `request_failed` | ERROR | method, path, error, error_type | Request error |
| `response_time_metric` | INFO | method, path, status_code, response_time_ms | Performance metric |
| `slow_request_detected` | WARNING | method, path, response_time_ms | Request > 1s |

### Database Events

| Event | Level | Fields | Description |
|-------|-------|--------|-------------|
| `database_transaction_committed` | DEBUG | - | Transaction completed |
| `database_error` | ERROR | error, error_type | SQL error |
| `creating_database_tables` | INFO | - | Starting table creation |
| `database_tables_created_successfully` | INFO | - | Tables created |
| `closing_database_connection` | INFO | - | Shutting down |

### Application Events

| Event | Level | Fields | Description |
|-------|-------|--------|-------------|
| `application_starting` | INFO | - | App startup |
| `application_ready` | INFO | - | App ready |
| `application_shutting_down` | INFO | - | App shutdown started |
| `application_stopped` | INFO | - | App stopped |

## Security

### Sensitive Data Masking

The following fields are **automatically masked** and replaced with `***MASKED***`:

- `password`
- `token`
- `jwt`
- `authorization`
- `secret`
- `api_key`
- `access_token`
- `refresh_token`
- `bearer`
- `credentials`

Masking is **case-insensitive** and works on:
- Top-level fields
- Nested dictionary fields
- Any field containing sensitive keywords

### Best Practices

1. **Never log sensitive data explicitly**
   ```python
   # BAD
   logger.info("user_login", email=email, password=password)

   # GOOD
   logger.info("user_login", email=email)
   ```

2. **Use structured logging**
   ```python
   # BAD
   logger.info(f"User {user_id} created task {task_id}")

   # GOOD
   logger.info("task_created", user_id=user_id, task_id=task_id)
   ```

3. **Include context in error logs**
   ```python
   # GOOD
   logger.error(
       "database_error",
       error=str(e),
       error_type=type(e).__name__,
       exc_info=True
   )
   ```

4. **Log at appropriate levels**
   - `DEBUG` - Detailed information for debugging
   - `INFO` - Normal operations, user actions
   - `WARNING` - Failed attempts, slow requests
   - `ERROR` - Errors that need attention
   - `CRITICAL` - System failures

## Configuration

Set log level via environment variable:

```bash
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Default: `INFO`

## Testing

Run security tests to verify no sensitive data leaks:

```bash
cd backend
pytest tests/test_logging_security.py -v
```

This test suite verifies:
- Passwords are masked
- Tokens are masked
- JWTs are masked
- Authorization headers are masked
- API keys are masked
- Nested sensitive fields are masked
- Non-sensitive data is not masked

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Response Time**
   - Alert if p95 > 1000ms
   - Query: `response_time_metric.response_time_ms`

2. **Failed Logins**
   - Alert if > 5 failures/minute for same email
   - Query: `login_failed.email`

3. **Database Errors**
   - Alert on any occurrence
   - Query: `database_error`

4. **Token Verification Failures**
   - Alert if spike detected
   - Query: `token_verification_failed`

### Log Aggregation

Logs are output to stdout in JSON format for easy integration with:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch**
- **Grafana Loki**

Example logstash configuration:

```ruby
input {
  stdin {
    codec => json
  }
}

filter {
  if [request_id] {
    mutate {
      add_field => { "trace_id" => "%{request_id}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "todo-api-%{+YYYY.MM.dd}"
  }
}
```

## Troubleshooting

### Finding logs for a specific request

Use the `X-Request-ID` from the response headers:

```bash
# Get request ID from response
curl -i http://localhost:8000/api/auth/me

# Search logs
grep "req_a1b2c3d4e5f6g7h8" application.log
```

### Finding logs for a specific user

```bash
grep "user_123" application.log | jq .
```

### Finding slow requests

```bash
grep "slow_request_detected" application.log | jq .
```

### Finding authentication failures

```bash
grep "login_failed" application.log | jq .
```

## Development Tips

1. **Test logging locally**
   ```bash
   uvicorn src.main:app --reload | jq .
   ```
   The `jq` command pretty-prints JSON logs.

2. **Use request ID in API clients**
   ```python
   headers = {"X-Request-ID": "custom_id_123"}
   response = requests.get(url, headers=headers)
   ```

3. **View logs in real-time**
   ```bash
   tail -f application.log | jq .
   ```

## References

- [structlog documentation](https://www.structlog.org/)
- [FastAPI middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [12-Factor App Logs](https://12factor.net/logs)
