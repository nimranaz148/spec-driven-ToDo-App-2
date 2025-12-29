"""Request ID middleware for distributed tracing.

This middleware generates a unique ID for each request and includes it
in all logs and response headers for easy tracing across the system.
"""
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logger import bind_context, clear_context, get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request.

    This middleware:
    1. Generates a unique request ID for each incoming request
    2. Binds the request ID to the logging context
    3. Includes the request ID in the response headers
    4. Clears the context after the request completes

    Headers:
    - X-Request-ID: Generated if not provided in request
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Process the request and add request ID.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response with X-Request-ID header
        """
        # Get request ID from header or generate a new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:16]}"

        # Bind request ID to logging context
        bind_context(request_id=request_id)

        # Log the incoming request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        try:
            # Process the request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log successful response
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )

            return response

        except Exception as e:
            # Log error
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

        finally:
            # Clear logging context to prevent leakage
            clear_context()
