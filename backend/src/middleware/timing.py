"""API response time metrics middleware.

This middleware tracks the response time for each API request and logs
performance metrics for monitoring and optimization.
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track and log API response times.

    This middleware:
    1. Records the start time of each request
    2. Calculates the response time after completion
    3. Logs metrics including endpoint, method, status code, and duration
    4. Adds response time to response headers

    Headers:
    - X-Response-Time: Response time in milliseconds
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """Process the request and track timing.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler

        Returns:
            Response with X-Response-Time header
        """
        # Record start time
        start_time = time.perf_counter()

        try:
            # Process the request
            response = await call_next(request)

            # Calculate response time in milliseconds
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000

            # Add response time to headers
            response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"

            # Log response time metrics
            logger.info(
                "response_time_metric",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time_ms=round(response_time_ms, 2),
                endpoint=f"{request.method} {request.url.path}",
            )

            # Log slow requests (> 1 second)
            if response_time_ms > 1000:
                logger.warning(
                    "slow_request_detected",
                    method=request.method,
                    path=request.url.path,
                    response_time_ms=round(response_time_ms, 2),
                    threshold_ms=1000,
                )

            return response

        except Exception as e:
            # Calculate response time even for errors
            end_time = time.perf_counter()
            response_time_ms = (end_time - start_time) * 1000

            # Log error with timing
            logger.error(
                "request_error_with_timing",
                method=request.method,
                path=request.url.path,
                response_time_ms=round(response_time_ms, 2),
                error=str(e),
                error_type=type(e).__name__,
            )

            raise
