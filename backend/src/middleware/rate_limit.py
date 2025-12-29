"""Rate limiting middleware for FastAPI."""
import time
import os
from typing import Dict, Tuple, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import JWTError, jwt

# Import JWT settings directly to avoid relative import issues
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# In-memory storage for rate limiting (user_id -> (count, reset_time))
rate_limit_storage: Dict[str, Tuple[int, float]] = {}

# Rate limit configuration
RATE_LIMIT_REQUESTS = 60  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds (1 minute)


def extract_user_id_from_token(authorization: Optional[str]) -> Optional[str]:
    """
    Extract user_id from JWT token in Authorization header.

    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")

    Returns:
        User ID if token is valid, None otherwise
    """
    if not authorization:
        return None

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    token = parts[1]

    try:
        # Decode token to extract user_id
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return user_id
    except JWTError:
        return None


def check_rate_limit(user_id: str) -> Tuple[bool, int, float]:
    """
    Check if user has exceeded rate limit.

    Args:
        user_id: User identifier

    Returns:
        Tuple of (is_allowed, remaining_requests, reset_time)
    """
    current_time = time.time()

    # Get or initialize user's rate limit data
    if user_id in rate_limit_storage:
        count, reset_time = rate_limit_storage[user_id]

        # Check if window has expired
        if current_time > reset_time:
            # Reset the counter for new window
            rate_limit_storage[user_id] = (1, current_time + RATE_LIMIT_WINDOW)
            return True, RATE_LIMIT_REQUESTS - 1, current_time + RATE_LIMIT_WINDOW

        # Check if limit exceeded
        if count >= RATE_LIMIT_REQUESTS:
            return False, 0, reset_time

        # Increment counter
        rate_limit_storage[user_id] = (count + 1, reset_time)
        return True, RATE_LIMIT_REQUESTS - (count + 1), reset_time
    else:
        # First request from this user
        reset_time = current_time + RATE_LIMIT_WINDOW
        rate_limit_storage[user_id] = (1, reset_time)
        return True, RATE_LIMIT_REQUESTS - 1, reset_time


def add_rate_limit_headers(response: Response, remaining: int, reset_time: float) -> None:
    """
    Add rate limit headers to response.

    Args:
        response: FastAPI Response object
        remaining: Number of requests remaining
        reset_time: Unix timestamp when limit resets
    """
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(reset_time))


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limiting on API requests.

    Rate limits requests to 60 per minute per authenticated user.
    Adds rate limit headers to all responses.
    Returns 429 Too Many Requests when limit is exceeded.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and apply rate limiting.

        Args:
            request: FastAPI Request object
            call_next: Next middleware/handler in chain

        Returns:
            Response with rate limit headers
        """
        # Extract user_id from JWT token
        authorization = request.headers.get("Authorization")
        user_id = extract_user_id_from_token(authorization)

        # If no user_id, allow request to proceed (auth middleware will handle)
        if not user_id:
            response = await call_next(request)
            return response

        # Check rate limit
        is_allowed, remaining, reset_time = check_rate_limit(user_id)

        if not is_allowed:
            # Rate limit exceeded
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED"
                }
            )
            add_rate_limit_headers(response, 0, reset_time)
            return response

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        add_rate_limit_headers(response, remaining, reset_time)

        return response


def reset_rate_limits() -> None:
    """
    Reset all rate limit counters.

    Useful for testing and maintenance.
    """
    rate_limit_storage.clear()


def get_rate_limit_info(user_id: str) -> Optional[Tuple[int, float]]:
    """
    Get current rate limit info for a user.

    Args:
        user_id: User identifier

    Returns:
        Tuple of (request_count, reset_time) or None if no data
    """
    return rate_limit_storage.get(user_id)
