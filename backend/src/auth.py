"""JWT authentication middleware and utilities."""
import os
import httpx
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .utils.logger import get_logger

logger = get_logger(__name__)

# Security scheme
security = HTTPBearer()

# Get JWT secret from environment (fallback for HS256)
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"  # For backend-generated tokens (fallback)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Frontend URL for JWKS endpoint
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
JWKS_URL = f"{FRONTEND_URL}/api/auth/jwks"

# Cache for JWKS client
_jwks_client: Optional[PyJWKClient] = None

def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(JWKS_URL, cache_keys=True, lifespan=3600)
    return _jwks_client


def create_access_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token (for backend-generated tokens)."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token from Better Auth (EdDSA via JWKS)."""
    from .utils.jwt_utils import is_token_blacklisted

    # Check if token is blacklisted first
    if is_token_blacklisted(token):
        logger.warning("token_verification_failed", reason="Token has been revoked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Try JWKS validation first (for Better Auth EdDSA tokens)
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA", "ES256", "RS256"],
            audience=FRONTEND_URL,
            issuer=FRONTEND_URL,
            options={"verify_aud": False, "verify_iss": False}  # Be flexible with aud/iss
        )
        logger.debug("token_verified_via_jwks")
        return payload
    except jwt.exceptions.PyJWKClientError as e:
        logger.warning("jwks_fetch_failed", error=str(e))
        # Fall through to try HS256
    except jwt.ExpiredSignatureError:
        logger.warning("token_expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning("jwks_token_invalid", error=str(e))
        # Fall through to try HS256

    # Fallback: Try HS256 with secret (for backward compatibility)
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        logger.debug("token_verified_via_hs256")
        return payload
    except jwt.InvalidTokenError as e:
        logger.warning(
            "token_verification_failed",
            reason="Invalid token",
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency to get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)

    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None or email is None:
        logger.warning("invalid_token_payload", reason="Missing user_id or email")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful authentication (adds user context to logs)
    logger.debug("user_authenticated", user_id=user_id, email=email)

    return {
        "user_id": user_id,
        "email": email,
    }


class AuthContext:
    """Context holder for authenticated user information."""

    def __init__(self, user_id: str, email: str):
        self.user_id = user_id
        self.email = email


def create_auth_context(user_id: str, email: str) -> AuthContext:
    """Create an auth context object."""
    return AuthContext(user_id=user_id, email=email)
