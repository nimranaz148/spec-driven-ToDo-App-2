#!/usr/bin/env python3
"""
Environment Variables Validation Script

Validates that all required environment variables are set and properly formatted
for the Todo Web Application backend.

Usage:
    python validate_env.py

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import os
import sys
import re
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class Color:
    """Terminal color codes for output formatting."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text:^70}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.END}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Color.GREEN}✓{Color.END} {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Color.YELLOW}⚠{Color.END} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Color.RED}✗{Color.END} {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Color.BLUE}ℹ{Color.END} {text}")


def validate_database_url(url: str) -> Tuple[bool, str]:
    """
    Validate PostgreSQL database URL format.

    Args:
        url: Database connection URL

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "DATABASE_URL is not set"

    try:
        parsed = urlparse(url)

        # Check scheme
        if parsed.scheme not in ['postgresql', 'postgresql+asyncpg']:
            return False, f"Invalid scheme '{parsed.scheme}'. Expected 'postgresql' or 'postgresql+asyncpg'"

        # Check hostname
        if not parsed.hostname:
            return False, "Missing hostname in DATABASE_URL"

        # Check database name
        if not parsed.path or parsed.path == '/':
            return False, "Missing database name in DATABASE_URL"

        # Check for SSL mode in production-like URLs
        if 'localhost' not in parsed.hostname and '127.0.0.1' not in parsed.hostname:
            if 'sslmode' not in url:
                return False, "Production database URL should include '?sslmode=require'"

        return True, "Valid PostgreSQL URL"

    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_jwt_secret(secret: str) -> Tuple[bool, str]:
    """
    Validate JWT secret key strength.

    Args:
        secret: JWT secret key

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not secret:
        return False, "BETTER_AUTH_SECRET is not set"

    if secret in ['your-secret-key-change-in-production', 'changeme', 'secret']:
        return False, "BETTER_AUTH_SECRET is using a default/insecure value"

    if len(secret) < 32:
        return False, f"BETTER_AUTH_SECRET is too short ({len(secret)} chars). Minimum: 32 characters"

    # Check for sufficient entropy
    unique_chars = len(set(secret))
    if unique_chars < 16:
        return False, f"BETTER_AUTH_SECRET has low entropy (only {unique_chars} unique characters)"

    # Check if it's not just a simple word or phrase
    if secret.isalpha() or secret.isdigit():
        return False, "BETTER_AUTH_SECRET should contain a mix of characters (letters, numbers, symbols)"

    return True, f"Strong secret key ({len(secret)} characters)"


def validate_cors_origin(origin: str) -> Tuple[bool, str]:
    """
    Validate CORS origin format.

    Args:
        origin: CORS origin URL

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not origin:
        return True, "Using default CORS origin (http://localhost:3000)"

    try:
        parsed = urlparse(origin)

        if not parsed.scheme:
            return False, "CORS_ORIGIN must include scheme (http:// or https://)"

        if parsed.scheme not in ['http', 'https']:
            return False, f"Invalid scheme '{parsed.scheme}'. Expected 'http' or 'https'"

        if not parsed.netloc:
            return False, "CORS_ORIGIN must include hostname"

        # Production warning
        if parsed.scheme == 'http' and 'localhost' not in parsed.netloc and '127.0.0.1' not in parsed.netloc:
            return False, "Production CORS_ORIGIN should use https://, not http://"

        return True, f"Valid CORS origin: {origin}"

    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def validate_log_level(level: str) -> Tuple[bool, str]:
    """
    Validate logging level.

    Args:
        level: Log level string

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not level:
        return True, "Using default log level (INFO)"

    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    if level.upper() not in valid_levels:
        return False, f"Invalid log level '{level}'. Must be one of: {', '.join(valid_levels)}"

    if level.upper() == 'DEBUG':
        print_warning("  DEBUG log level should not be used in production")

    return True, f"Valid log level: {level.upper()}"


def check_required_env_vars() -> Dict[str, bool]:
    """
    Check all required environment variables.

    Returns:
        Dictionary mapping variable names to validation status
    """
    results = {}

    print_header("Environment Variables Validation")

    # Required variables
    required_vars = [
        ('DATABASE_URL', validate_database_url),
        ('BETTER_AUTH_SECRET', validate_jwt_secret),
    ]

    # Optional variables with validation
    optional_vars = [
        ('CORS_ORIGIN', validate_cors_origin),
        ('LOG_LEVEL', validate_log_level),
    ]

    print(f"{Color.BOLD}Required Variables:{Color.END}\n")

    for var_name, validator in required_vars:
        value = os.getenv(var_name, '')
        is_valid, message = validator(value)

        if is_valid:
            print_success(f"{var_name}: {message}")
            results[var_name] = True
        else:
            print_error(f"{var_name}: {message}")
            results[var_name] = False

    print(f"\n{Color.BOLD}Optional Variables:{Color.END}\n")

    for var_name, validator in optional_vars:
        value = os.getenv(var_name, '')
        is_valid, message = validator(value)

        if is_valid:
            print_success(f"{var_name}: {message}")
            results[var_name] = True
        else:
            print_warning(f"{var_name}: {message}")
            results[var_name] = False

    return results


def print_summary(results: Dict[str, bool]) -> None:
    """
    Print validation summary.

    Args:
        results: Dictionary of validation results
    """
    print_header("Validation Summary")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    if failed == 0:
        print_success(f"All {total} validations passed!")
        print_info("\nYour environment is properly configured.")
    else:
        print_error(f"{failed} of {total} validations failed")
        print_info("\nPlease fix the errors above before running the application.")


def print_recommendations() -> None:
    """Print security recommendations."""
    print_header("Security Recommendations")

    recommendations = [
        "1. Never commit .env files to version control",
        "2. Use different secrets for development and production",
        "3. Generate JWT secrets with cryptographically secure random generators:",
        "   python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
        "4. Rotate JWT secrets periodically (every 90 days)",
        "5. Use HTTPS in production (never HTTP)",
        "6. Enable database SSL/TLS (sslmode=require)",
        "7. Set LOG_LEVEL to INFO or WARNING in production (not DEBUG)",
        "8. Store secrets in secure secret management systems (AWS Secrets Manager, etc.)",
    ]

    for rec in recommendations:
        print_info(rec)


def print_example_env() -> None:
    """Print example .env file."""
    print_header("Example .env File")

    example = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db?sslmode=require

# Authentication
BETTER_AUTH_SECRET=your-strong-secret-key-at-least-32-characters-long

# CORS Configuration (optional)
CORS_ORIGIN=http://localhost:3000

# Logging Configuration (optional)
LOG_LEVEL=INFO
"""

    print(example)


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Load .env file if it exists
        env_file = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_file):
            print_info(f"Loading environment variables from: {env_file}\n")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
        else:
            print_warning(f".env file not found at: {env_file}")
            print_info("Checking system environment variables...\n")

        # Run validations
        results = check_required_env_vars()

        # Print summary
        print_summary(results)

        # Check if any required validation failed
        required_vars = ['DATABASE_URL', 'BETTER_AUTH_SECRET']
        required_failed = any(not results.get(var, False) for var in required_vars)

        if required_failed:
            print_recommendations()
            print_example_env()
            return 1

        # Print recommendations even on success
        print_recommendations()

        return 0

    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
