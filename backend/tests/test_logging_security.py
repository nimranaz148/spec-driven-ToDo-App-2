"""Test suite for logging security - ensures no sensitive data is logged.

This test suite verifies that passwords, tokens, JWTs, and other sensitive
data are NEVER logged to stdout or any log destination.

Task: T110-OBS - Verify no sensitive data in logs
"""
import json
from io import StringIO
import sys

import pytest
from structlog.testing import capture_logs

from src.utils.logger import get_logger, mask_sensitive_data, configure_logging


class TestLoggingSecurity:
    """Test that sensitive data is never logged."""

    def test_mask_password_field(self):
        """Test that password fields are masked."""
        logger = get_logger(__name__)
        event_dict = {
            "event": "user_created",
            "email": "user@example.com",
            "password": "supersecret123",
        }

        # Mask sensitive data
        masked = mask_sensitive_data(None, "info", event_dict)

        # Password should be masked
        assert masked["password"] == "***MASKED***"
        # Other fields should not be masked
        assert masked["email"] == "user@example.com"

    def test_mask_token_field(self):
        """Test that token fields are masked."""
        event_dict = {
            "event": "token_generated",
            "user_id": "user_123",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        # Token should be masked
        assert masked["access_token"] == "***MASKED***"
        # User ID should not be masked
        assert masked["user_id"] == "user_123"

    def test_mask_jwt_field(self):
        """Test that JWT fields are masked."""
        event_dict = {
            "event": "auth_check",
            "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["jwt"] == "***MASKED***"

    def test_mask_authorization_header(self):
        """Test that authorization headers are masked."""
        event_dict = {
            "event": "request_received",
            "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["authorization"] == "***MASKED***"

    def test_mask_api_key_field(self):
        """Test that API key fields are masked."""
        event_dict = {
            "event": "api_call",
            "api_key": "sk_live_123456789",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["api_key"] == "***MASKED***"

    def test_mask_nested_sensitive_fields(self):
        """Test that nested sensitive fields are masked."""
        event_dict = {
            "event": "user_data",
            "user": {
                "email": "user@example.com",
                "password": "secret123",
                "name": "John Doe",
            },
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        # Nested password should be masked
        assert masked["user"]["password"] == "***MASKED***"
        # Other nested fields should not be masked
        assert masked["user"]["email"] == "user@example.com"
        assert masked["user"]["name"] == "John Doe"

    def test_mask_refresh_token(self):
        """Test that refresh tokens are masked."""
        event_dict = {
            "event": "token_refresh",
            "refresh_token": "refresh_abc123xyz",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["refresh_token"] == "***MASKED***"

    def test_mask_bearer_token(self):
        """Test that bearer tokens are masked."""
        event_dict = {
            "event": "auth_header",
            "bearer": "token_here",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["bearer"] == "***MASKED***"

    def test_mask_credentials(self):
        """Test that credentials are masked."""
        event_dict = {
            "event": "login_attempt",
            "credentials": {"username": "user", "password": "pass"},
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["credentials"] == "***MASKED***"

    def test_case_insensitive_masking(self):
        """Test that masking is case-insensitive."""
        event_dict = {
            "event": "test",
            "Password": "secret",
            "TOKEN": "abc123",
            "Api_Key": "key123",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        assert masked["Password"] == "***MASKED***"
        assert masked["TOKEN"] == "***MASKED***"
        assert masked["Api_Key"] == "***MASKED***"

    def test_non_sensitive_fields_not_masked(self):
        """Test that non-sensitive fields are not masked."""
        event_dict = {
            "event": "user_action",
            "user_id": "user_123",
            "email": "user@example.com",
            "action": "login",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        masked = mask_sensitive_data(None, "info", event_dict)

        # None of these should be masked
        assert masked["user_id"] == "user_123"
        assert masked["email"] == "user@example.com"
        assert masked["action"] == "login"
        assert masked["timestamp"] == "2024-01-01T00:00:00Z"


class TestLoggingOutput:
    """Test that actual log output doesn't contain sensitive data."""

    def test_no_password_in_log_output(self, capfd):
        """Test that passwords never appear in log output."""
        configure_logging(log_level="INFO")
        logger = get_logger(__name__)

        # Attempt to log sensitive data
        logger.info(
            "user_registration",
            email="user@example.com",
            password="supersecret123",
        )

        # Capture output
        captured = capfd.readouterr()

        # Password should be masked in output
        assert "supersecret123" not in captured.out
        assert "***MASKED***" in captured.out
        # Email should still be present
        assert "user@example.com" in captured.out

    def test_no_token_in_log_output(self, capfd):
        """Test that tokens never appear in log output."""
        configure_logging(log_level="INFO")
        logger = get_logger(__name__)

        # Attempt to log a token
        logger.info(
            "token_generated",
            user_id="user_123",
            token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
        )

        # Capture output
        captured = capfd.readouterr()

        # Token should be masked
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in captured.out
        assert "***MASKED***" in captured.out
        # User ID should still be present
        assert "user_123" in captured.out


class TestSecurityBestPractices:
    """Test that security best practices are followed in logging."""

    def test_structured_json_output(self, capfd):
        """Test that logs are output as structured JSON."""
        configure_logging(log_level="INFO")
        logger = get_logger(__name__)

        logger.info("test_event", field1="value1", field2="value2")

        captured = capfd.readouterr()

        # Output should be valid JSON
        try:
            log_line = captured.out.strip()
            log_data = json.loads(log_line)
            assert log_data["event"] == "test_event"
            assert "timestamp" in log_data
        except json.JSONDecodeError:
            pytest.fail("Log output is not valid JSON")

    def test_log_includes_timestamp(self, capfd):
        """Test that all logs include a timestamp."""
        configure_logging(log_level="INFO")
        logger = get_logger(__name__)

        logger.info("test_event")

        captured = capfd.readouterr()
        log_data = json.loads(captured.out.strip())

        assert "timestamp" in log_data

    def test_log_includes_level(self, capfd):
        """Test that all logs include a log level."""
        configure_logging(log_level="INFO")
        logger = get_logger(__name__)

        logger.info("test_event")

        captured = capfd.readouterr()
        log_data = json.loads(captured.out.strip())

        assert "level" in log_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
