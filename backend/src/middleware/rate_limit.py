"""Rate limiting middleware for chat endpoints."""

import time
from typing import Dict, Optional, Callable
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque


class ChatRateLimiter:
    """Rate limiter for chat endpoints with per-user limits."""
    
    def __init__(self, max_requests: int = 30, window_minutes: int = 1):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_minutes: Time window in minutes
        """
        self.max_requests = max_requests
        self.window_seconds = window_minutes * 60
        self.user_requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, user_id: str) -> tuple[bool, Optional[int]]:
        """Check if user is within rate limit.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        user_queue = self.user_requests[user_id]
        
        # Remove old requests outside the window
        while user_queue and user_queue[0] <= now - self.window_seconds:
            user_queue.popleft()
        
        # Check if under limit
        if len(user_queue) < self.max_requests:
            user_queue.append(now)
            return True, None
        
        # Calculate retry after time
        oldest_request = user_queue[0]
        retry_after = int(oldest_request + self.window_seconds - now) + 1
        
        return False, retry_after
    
    def get_remaining(self, user_id: str) -> int:
        """Get remaining requests for user."""
        now = time.time()
        user_queue = self.user_requests[user_id]
        
        # Remove old requests
        while user_queue and user_queue[0] <= now - self.window_seconds:
            user_queue.popleft()
        
        return max(0, self.max_requests - len(user_queue))
    
    def get_reset_time(self, user_id: str) -> int:
        """Get timestamp when rate limit resets."""
        user_queue = self.user_requests[user_id]
        if not user_queue:
            return int(time.time())
        
        return int(user_queue[0] + self.window_seconds)


# Global rate limiter instance
chat_rate_limiter = ChatRateLimiter(max_requests=30, window_minutes=1)


async def check_chat_rate_limit(request: Request, user_id: str) -> None:
    """Check rate limit for chat endpoints.
    
    Args:
        request: FastAPI request object
        user_id: User ID for rate limiting
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    is_allowed, retry_after = chat_rate_limiter.is_allowed(user_id)
    
    if not is_allowed:
        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(chat_rate_limiter.max_requests),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(chat_rate_limiter.get_reset_time(user_id)),
            "Retry-After": str(retry_after)
        }
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many chat requests. Try again in {retry_after} seconds.",
                "retry_after": retry_after
            },
            headers=headers
        )


def add_rate_limit_headers(response: JSONResponse, user_id: str) -> JSONResponse:
    """Add rate limit headers to successful responses.
    
    Args:
        response: Response object
        user_id: User ID
        
    Returns:
        Response with rate limit headers
    """
    response.headers["X-RateLimit-Limit"] = str(chat_rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(chat_rate_limiter.get_remaining(user_id))
    response.headers["X-RateLimit-Reset"] = str(chat_rate_limiter.get_reset_time(user_id))
    
    return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Basic rate limiting middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # For now, just pass through - specific rate limiting is handled in endpoints
        response = await call_next(request)
        return response


def reset_rate_limits():
    """Reset all rate limits (for testing)."""
    global chat_rate_limiter
    chat_rate_limiter = ChatRateLimiter(max_requests=30, window_minutes=1)
