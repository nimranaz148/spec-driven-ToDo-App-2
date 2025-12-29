"""Password hashing utilities."""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Note: bcrypt has a 72-byte limit. Passwords are automatically truncated at 72 bytes.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Note: bcrypt has a 72-byte limit. Passwords are automatically truncated at 72 bytes.
    """
    # Convert both to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    # Verify password
    return bcrypt.checkpw(password_bytes, hashed_bytes)
