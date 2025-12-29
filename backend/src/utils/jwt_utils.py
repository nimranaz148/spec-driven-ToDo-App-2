"""JWT utilities for token management."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError

from ..auth import JWT_SECRET, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# In-memory token blacklist (in production, use Redis with TTL)
# Stores token JTI (JWT ID) or full token string for revocation
token_blacklist: set[str] = set()


def create_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT token for a user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def invalidate_token(token: str) -> None:
    """
    Add a token to the blacklist to invalidate it.

    Args:
        token: The JWT token string to invalidate
    """
    token_blacklist.add(token)


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token has been blacklisted.

    Args:
        token: The JWT token string to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    return token in token_blacklist


def clear_blacklist() -> None:
    """Clear all tokens from the blacklist. Used for testing."""
    token_blacklist.clear()


def get_blacklist_size() -> int:
    """Get the number of blacklisted tokens. Used for testing."""
    return len(token_blacklist)


# Legacy aliases for backwards compatibility
revoke_token = invalidate_token
is_token_revoked = is_token_blacklisted
revoked_tokens = token_blacklist
