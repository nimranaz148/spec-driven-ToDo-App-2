"""Tests for authentication endpoints."""
import pytest
import uuid
from httpx import AsyncClient


class TestUserRegistration:
    """Tests for user registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration."""
        unique_email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "New User",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == unique_email
        assert data["user"]["name"] == "New User"
        assert "id" in data["user"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email fails."""
        email = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"

        # First registration should succeed
        await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "name": "First User",
                "password": "password123",
            },
        )

        # Second registration with same email should fail
        response = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "name": "Second User",
                "password": "password456",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "name": "Test User",
                "password": "password123",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with password too short."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "name": "Test User",
                "password": "short",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_missing_name(self, client: AsyncClient):
        """Test registration without name."""
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_returns_valid_jwt(self, client: AsyncClient):
        """Test that registration returns a valid JWT token."""
        import base64
        import json

        unique_email = f"jwt_test_{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "JWT Test",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        token = response.json()["access_token"]

        # Token should have 3 parts
        parts = token.split(".")
        assert len(parts) == 3

        # Payload should be valid JSON
        padding = 4 - len(parts[1]) % 4
        if padding != 4:
            payload = base64.urlsafe_b64decode(parts[1] + "=" * padding)
            data = json.loads(payload)
            assert "sub" in data  # user_id
            assert "email" in data


class TestUserLogin:
    """Tests for user login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful login."""
        unique_email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        password = "testpassword123"

        # First register the user
        await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Login Test User",
                "password": password,
            },
        )

        # Then login
        response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password fails."""
        unique_email = f"wrongpass_{uuid.uuid4().hex[:8]}@example.com"

        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Wrong Pass User",
                "password": "correctpassword",
            },
        )

        # Try login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Test login with invalid email format."""
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_missing_credentials(self, client: AsyncClient):
        """Test login without credentials fails."""
        response = await client.post(
            "/api/auth/login",
            json={},
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_returns_different_token_than_registration(self, client: AsyncClient):
        """Test that login and registration return different tokens."""
        import time

        unique_email = f"token_diff_{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # Register
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Token Test",
                "password": password,
            },
        )
        reg_token = reg_response.json()["access_token"]

        # Wait briefly
        time.sleep(0.1)

        # Login
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )
        login_token = login_response.json()["access_token"]

        # Tokens should be different due to different iat
        assert reg_token != login_token


class TestAuthMiddleware:
    """Tests for authentication middleware."""

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test that protected endpoints require authentication."""
        response = await client.get("/api/test-user/tasks")

        assert response.status_code == 403  # No auth header

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test that protected endpoints reject invalid tokens."""
        response = await client.get(
            "/api/test-user/tasks",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401


class TestAuthResponseFormat:
    """Tests for authentication response format."""

    @pytest.mark.asyncio
    async def test_register_response_format(self, client: AsyncClient):
        """Test registration response has correct structure."""
        unique_email = f"format_{uuid.uuid4().hex[:8]}@example.com"
        response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Format Test",
                "password": "password123",
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert "name" in data["user"]
        assert "created_at" in data["user"]

    @pytest.mark.asyncio
    async def test_login_response_format(self, client: AsyncClient):
        """Test login response has correct structure."""
        unique_email = f"login_format_{uuid.uuid4().hex[:8]}@example.com"
        password = "formatpassword123"

        # Register first
        await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Login Format Test",
                "password": password,
            },
        )

        # Then login
        response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert "id" in data["user"]
        assert "email" in data["user"]
        assert "name" in data["user"]


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration endpoint."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123",
        },
    )

    # Should return 201 or 409 if user exists
    assert response.status_code in [201, 409]

    if response.status_code == 201:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login endpoint."""
    # First register a user
    await client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "name": "Login User",
            "password": "securepassword123",
        },
    )

    # Then try to login
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


class TestLogout:
    """Tests for logout endpoint - Contract Tests (T048-US3)."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient):
        """Test successful logout with valid token."""
        # Register a user first
        unique_email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Logout Test",
                "password": "password123",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def test_logout_without_token(self, client: AsyncClient):
        """Test logout fails without authentication token."""
        response = await client.post("/api/auth/logout")

        # Can be 401 or 403 depending on how auth is configured
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, client: AsyncClient):
        """Test logout fails with invalid token."""
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid-token-string"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_with_malformed_token(self, client: AsyncClient):
        """Test logout fails with malformed token."""
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_token_invalidation_after_logout(self, client: AsyncClient):
        """Test that token cannot be used after logout."""
        # Register and get token
        unique_email = f"invalidate_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Invalidate Test",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]

        # Verify token works before logout
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200

        # Logout
        logout_response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status_code == 200

        # Try to use token after logout - should fail
        after_logout_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert after_logout_response.status_code == 401
        assert "revoked" in after_logout_response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_logout_response_format(self, client: AsyncClient):
        """Test logout response has correct structure."""
        # Register and get token
        unique_email = f"format_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Format Test",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)

    @pytest.mark.asyncio
    async def test_logout_twice_fails(self, client: AsyncClient):
        """Test that logging out twice with same token fails on second attempt."""
        # Register and get token
        unique_email = f"twice_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Twice Test",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]

        # First logout succeeds
        first_logout = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert first_logout.status_code == 200

        # Second logout with same token should fail
        second_logout = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert second_logout.status_code == 401
