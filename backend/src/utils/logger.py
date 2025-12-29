"""Structured JSON logging utility using structlog.

This module provides a centralized logging configuration for the application.
All logs are output as structured JSON to stdout for easy containerization
and log aggregation.

Security Notes:
- NEVER log passwords, tokens, JWTs, or other sensitive data
- Sensitive fields are masked automatically
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


# Fields that should never be logged (security)
SENSITIVE_FIELDS = {
    "password",
    "token",
    "jwt",
    "authorization",
    "secret",
    "api_key",
    "access_token",
    "refresh_token",
    "bearer",
    "credentials",
}


def mask_sensitive_data(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Mask sensitive fields in log records.

    This processor ensures that passwords, tokens, and other sensitive
    data are never logged, even accidentally.
    """
    for key in list(event_dict.keys()):
        # Check if key is sensitive
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            event_dict[key] = "***MASKED***"

        # Check nested dictionaries
        if isinstance(event_dict[key], dict):
            for nested_key in list(event_dict[key].keys()):
                if any(sensitive in nested_key.lower() for sensitive in SENSITIVE_FIELDS):
                    event_dict[key][nested_key] = "***MASKED***"

    return event_dict


def add_log_level(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add log level to the event dictionary."""
    event_dict["level"] = method_name
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    This configures structlog to output JSON logs to stdout with:
    - Timestamp in ISO format
    - Log level
    - Message
    - Context fields (user_id, request_id, etc.)
    - Masked sensitive data
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        mask_sensitive_data,  # Security: mask sensitive fields
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Configured structlog logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("user_logged_in", user_id="user_123", email="user@example.com")
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """Bind context variables that will be included in all subsequent logs.

    This is useful for adding request_id, user_id, etc. that should appear
    in all logs within a request context.

    Args:
        **kwargs: Key-value pairs to bind to the logging context

    Example:
        bind_context(request_id="req_123", user_id="user_456")
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """Remove context variables from the logging context.

    Args:
        *keys: Keys to remove from the context

    Example:
        unbind_context("request_id", "user_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """Clear all context variables from the logging context.

    This should be called at the end of each request to prevent
    context leakage between requests.
    """
    structlog.contextvars.clear_contextvars()


# Initialize logging when module is imported
configure_logging()
