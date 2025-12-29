# Logging & Observability Setup

## Installation

The logging dependencies are already included in `pyproject.toml`. To install:

```bash
cd backend
pip install -e .
```

Dependencies added:
- `structlog>=24.1.0` - Structured logging framework
- `python-json-logger>=2.0.7` - JSON formatter

## Environment Configuration

Add the following to your `.env` file:

```bash
# Logging configuration
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Default log level is `INFO` if not specified.

## Quick Start

### 1. Basic Logging

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Log structured events
logger.info("user_action", user_id="user_123", action="create_task")
logger.error("operation_failed", error=str(e), error_type=type(e).__name__)
```

### 2. Run with Pretty-Printed Logs

During development, pipe logs through `jq` for readable output:

```bash
uvicorn src.main:app --reload | jq .
```

### 3. View Logs in Real-Time

```bash
# Tail application logs with pretty printing
tail -f logs/app.log | jq .

# Or with color highlighting
tail -f logs/app.log | jq -C . | less -R
```

## Features Implemented

### T105-OBS: Structured JSON Logging
- **File:** `backend/src/utils/logger.py`
- **Features:**
  - Structured JSON output to stdout
  - ISO timestamp on every log
  - Log level included
  - Context variables (request_id, user_id)
  - Automatic sensitive data masking

### T106-OBS: Request ID Middleware
- **File:** `backend/src/middleware/request_id.py`
- **Features:**
  - Unique request ID for each request
  - Request ID in all logs
  - Request ID in response headers
  - Context cleanup after request

### T107-OBS: Authentication Logging
- **Files:** `backend/src/routes/auth.py`, `backend/src/auth.py`
- **Events logged:**
  - User registration attempts
  - Login attempts (success/failure)
  - Logout events
  - Token verification failures
- **Security:** Passwords and tokens are NEVER logged

### T108-OBS: Database Error Logging
- **File:** `backend/src/db.py`
- **Events logged:**
  - Database errors with context
  - Transaction commits
  - Table creation
  - Connection lifecycle

### T109-OBS: Response Time Metrics
- **File:** `backend/src/middleware/timing.py`
- **Metrics tracked:**
  - Response time for every request
  - Slow request warnings (> 1s)
  - Response time in headers

### T110-OBS: Security Verification
- **File:** `backend/tests/test_logging_security.py`
- **Tests verify:**
  - Passwords are masked
  - Tokens are masked
  - JWTs are masked
  - Authorization headers are masked
  - API keys are masked

## Testing

Run the logging security tests:

```bash
cd backend
pytest tests/test_logging_security.py -v
```

Expected output:
```
tests/test_logging_security.py::TestLoggingSecurity::test_mask_password_field PASSED
tests/test_logging_security.py::TestLoggingSecurity::test_mask_token_field PASSED
tests/test_logging_security.py::TestLoggingSecurity::test_mask_jwt_field PASSED
...
```

## Example Log Output

### Successful Login
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

### Failed Login
```json
{
  "event": "login_failed",
  "timestamp": "2024-01-15T10:31:12.456789Z",
  "level": "warning",
  "logger": "src.routes.auth",
  "request_id": "req_b2c3d4e5f6g7h8i9",
  "email": "user@example.com",
  "reason": "Invalid credentials"
}
```

### Response Time Metric
```json
{
  "event": "response_time_metric",
  "timestamp": "2024-01-15T10:32:00.789012Z",
  "level": "info",
  "logger": "src.middleware.timing",
  "request_id": "req_c3d4e5f6g7h8i9j0",
  "method": "GET",
  "path": "/api/user_123/tasks",
  "status_code": 200,
  "response_time_ms": 45.23,
  "endpoint": "GET /api/user_123/tasks"
}
```

### Database Error
```json
{
  "event": "database_error",
  "timestamp": "2024-01-15T10:33:30.012345Z",
  "level": "error",
  "logger": "src.db",
  "request_id": "req_d4e5f6g7h8i9j0k1",
  "error": "connection refused",
  "error_type": "OperationalError",
  "exc_info": "..."
}
```

## Response Headers

Every API response includes observability headers:

```
X-Request-ID: req_a1b2c3d4e5f6g7h8
X-Response-Time: 45.23ms
```

Use the request ID to trace logs for specific requests:

```bash
curl -i http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"

# Response includes:
# X-Request-ID: req_abc123

# Find all logs for this request:
grep "req_abc123" logs/app.log
```

## Integration with Log Aggregation

### ELK Stack

Add to logstash configuration:

```ruby
input {
  file {
    path => "/var/log/todo-api/*.log"
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

### Datadog

Configure Datadog agent:

```yaml
logs:
  - type: file
    path: /var/log/todo-api/*.log
    service: todo-api
    source: python
    sourcecategory: sourcecode
```

### CloudWatch

Use AWS CloudWatch agent configuration:

```json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/todo-api/*.log",
            "log_group_name": "/aws/todo-api",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
```

## Monitoring Queries

### Find failed login attempts

```bash
# Using jq
cat logs/app.log | jq 'select(.event == "login_failed")'

# Count by email
cat logs/app.log | jq -r 'select(.event == "login_failed") | .email' | sort | uniq -c
```

### Find slow requests

```bash
# Requests over 1 second
cat logs/app.log | jq 'select(.event == "response_time_metric" and .response_time_ms > 1000)'

# Average response time
cat logs/app.log | jq -r 'select(.event == "response_time_metric") | .response_time_ms' | awk '{sum+=$1; count++} END {print sum/count}'
```

### Find database errors

```bash
cat logs/app.log | jq 'select(.event == "database_error")'
```

### Trace a specific request

```bash
# Replace with actual request ID
REQUEST_ID="req_abc123"
cat logs/app.log | jq "select(.request_id == \"$REQUEST_ID\")"
```

## Production Recommendations

1. **Set LOG_LEVEL to INFO**
   - DEBUG creates too many logs in production
   - INFO provides good balance

2. **Use log rotation**
   ```bash
   # logrotate configuration
   /var/log/todo-api/*.log {
       daily
       rotate 7
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
   }
   ```

3. **Monitor key metrics**
   - Failed login rate
   - Average response time
   - Database error count
   - Token verification failures

4. **Set up alerts**
   - Alert if > 10 login failures per minute
   - Alert if p95 response time > 1000ms
   - Alert on any database errors
   - Alert if > 100 token verification failures per minute

## Troubleshooting

### Logs not appearing

Check that logging is configured:
```python
from src.utils.logger import configure_logging
configure_logging(log_level="INFO")
```

### Sensitive data in logs

Run security tests:
```bash
pytest tests/test_logging_security.py -v
```

If tests fail, the masking is working. If tests pass but sensitive data appears, check:
1. Field names match sensitive keywords
2. Masking processor is in the pipeline
3. No direct string formatting in log calls

### Performance impact

Structured logging has minimal overhead:
- ~0.1ms per log call
- Middleware adds ~0.5ms per request
- Negligible impact on overall performance

To minimize impact:
- Use INFO level in production
- Avoid DEBUG level in hot paths
- Use async logging if needed

## Documentation

- Full documentation: `backend/src/utils/LOGGING.md`
- Security tests: `backend/tests/test_logging_security.py`
- Logger source: `backend/src/utils/logger.py`
- Middleware: `backend/src/middleware/request_id.py`, `backend/src/middleware/timing.py`

## Support

For questions or issues with logging:
1. Check `backend/src/utils/LOGGING.md` for detailed documentation
2. Run security tests to verify no sensitive data leaks
3. Check log output with `jq` for proper JSON formatting
