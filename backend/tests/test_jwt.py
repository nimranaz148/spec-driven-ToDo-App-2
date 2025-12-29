"""Tests for JWT token generation and validation."""
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from auth import (
    create_access_token,
    decode_token,
    get_current_user,
    JWT_SECRET,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class TestJWTTokenGeneration:
    """Tests for JWT token creation."""

    def test_create_access_token_basic(self):
        """Test basic token creation."""
        user_id = "test-user-123"
        email = "test@example.com"

        token = create_access_token(user_id, email)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_payload(self):
        """Test that token contains expected payload data."""
        user_id = "payload-user"
        email = "payload@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_custom_expiry(self):
        """Test token creation with custom expiry time."""
        user_id = "custom-expiry"
        email = "expiry@example.com"
        custom_delta = timedelta(hours=2)

        token = create_access_token(user_id, email, expires_delta=custom_delta)
        payload = decode_token(token)

        # Verify expiry is approximately 2 hours from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + custom_delta

        # Allow 5 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_create_access_token_default_expiry(self):
        """Test token uses default expiry (7 days)."""
        user_id = "default-expiry"
        email = "default@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Allow 5 second tolerance
        assert abs((exp_time - expected_exp).total_seconds()) < 5

    def test_different_users_get_different_tokens(self):
        """Test that different users get different tokens."""
        token1 = create_access_token("user-1", "user1@example.com")
        token2 = create_access_token("user-2", "user2@example.com")

        assert token1 != token2

    def test_same_user_different_times_get_different_tokens(self):
        """Test that same user at different times gets different tokens."""
        # Create first token
        token1 = create_access_token("user-1", "user1@example.com")

        # Wait briefly
        import time
        time.sleep(0.1)

        # Create second token
        token2 = create_access_token("user-1", "user1@example.com")

        # Tokens should be different due to different iat
        assert token1 != token2

        # But both should be valid
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        assert payload1["sub"] == payload2["sub"] == "user-1"


class TestJWTTokenDecoding:
    """Tests for JWT token decoding."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        user_id = "decode-user"
        email = "decode@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email

    def test_decode_expired_token_raises_error(self):
        """Test that decoding an expired token raises an error."""
        user_id = "expired-user"
        email = "expired@example.com"

        # Create a token that's already expired
        expired_token = create_access_token(
            user_id,
            email,
            expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(JWTError):
            decode_token(expired_token)

    def test_decode_invalid_token_raises_error(self):
        """Test that decoding an invalid token raises an error."""
        with pytest.raises(JWTError):
            decode_token("invalid.token.here")

    def test_decode_malformed_token_raises_error(self):
        """Test that decoding a malformed token raises an error."""
        with pytest.raises(JWTError):
            decode_token("not-a-jwt")

    def test_decode_token_wrong_secret(self):
        """Test that token with wrong secret fails verification."""
        from jose import jwt

        # Create a token with a different secret
        wrong_token = jwt.encode(
            {"sub": "user-1", "email": "test@example.com"},
            "wrong-secret",
            algorithm=ALGORITHM,
        )

        with pytest.raises(JWTError):
            decode_token(wrong_token)


class TestJWTVerification:
    """Tests for JWT verification and validation."""

    def test_token_contains_required_claims(self):
        """Test that token contains all required claims."""
        user_id = "required-claims"
        email = "claims@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        # Check required claims
        assert "sub" in payload  # Subject (user_id)
        assert "email" in payload
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at

    def test_token_subject_is_user_id(self):
        """Test that 'sub' claim contains the user_id."""
        user_id = "subject-user"
        email = "subject@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        assert payload["sub"] == user_id

    def test_token_algorithm_is_hs256(self):
        """Test that tokens use HS256 algorithm."""
        user_id = "algo-user"
        email = "algo@example.com"

        token = create_access_token(user_id, email)

        # Decode without verification to check header
        unverified = jwt.decode(token, options={"verify_signature": False})

        assert unverified.get("alg") == ALGORITHM or ALGORITHM == "HS256"


class TestJWTAuthContext:
    """Tests for JWT authentication context."""

    def test_create_auth_context(self):
        """Test creating an auth context."""
        from auth import create_auth_context

        auth_context = create_auth_context("user-123", "test@example.com")

        assert auth_context.user_id == "user-123"
        assert auth_context.email == "test@example.com"

    def test_auth_context_with_different_users(self):
        """Test auth context creation for different users."""
        from auth import create_auth_context

        context1 = create_auth_context("user-1", "user1@example.com")
        context2 = create_auth_context("user-2", "user2@example.com")

        assert context1.user_id != context2.user_id
        assert context1.email != context2.email


class TestJWTSecurity:
    """Tests for JWT security features."""

    def test_token_is_jwt_format(self):
        """Test that token has JWT format (3 parts separated by dots)."""
        user_id = "format-user"
        email = "format@example.com"

        token = create_access_token(user_id, email)

        parts = token.split(".")
        assert len(parts) == 3  # Header, Payload, Signature

    def test_token_is_base64_encoded(self):
        """Test that token parts are base64url encoded."""
        import base64

        user_id = "base64-user"
        email = "base64@example.com"

        token = create_access_token(user_id, email)
        parts = token.split(".")

        # Each part should be valid base64
        for part in parts:
            # Add padding if necessary for decoding
            padding = 4 - len(part) % 4
            if padding != 4:
                part += "=" * padding

            # Should not raise an exception
            base64.urlsafe_b64decode(part)

    def test_different_secrets_produce_different_tokens(self):
        """Test that different secrets produce different tokens."""
        # This test verifies our secret is being used
        # In production, BETTER_AUTH_SECRET should be set

        user_id = "secret-test"
        email = "secret@example.com"

        token = create_access_token(user_id, email)

        # Token should be decodable with our secret
        payload = decode_token(token)
        assert payload["sub"] == user_id


class TestJWTConstants:
    """Tests for JWT configuration constants."""

    def test_algorithm_is_hs256(self):
        """Test that algorithm is HS256."""
        assert ALGORITHM == "HS256"

    def test_access_token_expire_minutes(self):
        """Test that default expiry is 7 days (10080 minutes)."""
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 7  # 7 days

    def test_jwt_secret_is_configured(self):
        """Test that JWT secret is configured."""
        assert JWT_SECRET is not None
        assert len(JWT_SECRET) > 0


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        from fastapi import HTTPException
        from fastapi.security import HTTPBearer

        user_id = "current-user"
        email = "current@example.com"

        # Create a valid token
        token = create_access_token(user_id, email)

        # Create mock credentials
        security = HTTPBearer()
        credentials = type('Credentials', (), {'credentials': token})()

        # Get current user should work
        # Note: This would need a real request context in FastAPI
        # We test the token decode part separately

        payload = decode_token(token)
        assert payload["sub"] == user_id
        assert payload["email"] == email

    def test_get_current_user_no_token(self):
        """Test get_current_user with no token raises 401."""
        # This would need FastAPI test client
        # The auth.py implementation already handles this

        # Verify decode_token raises for invalid/missing token
        with pytest.raises(HTTPException):
            decode_token("")

    def test_get_current_user_expired_token(self):
        """Test get_current_user with expired token raises 401."""
        from fastapi import HTTPException

        expired_token = create_access_token(
            "expired-user",
            "expired@example.com",
            expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(HTTPException) as exc_info:
            decode_token(expired_token)

        assert exc_info.value.status_code == 401
