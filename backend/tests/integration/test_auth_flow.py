"""Integration tests for full authentication flow."""
import pytest
from httpx import AsyncClient

import sys
sys.path.insert(0, 'backend/src')


class TestFullAuthFlow:
    """End-to-end tests for complete authentication flow."""

    @pytest.mark.asyncio
    async def test_complete_registration_to_login_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> access protected resource."""
        import uuid

        # Step 1: Register a new user
        unique_email = f"flow_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Flow Test User",
                "password": "securepassword123",
            },
        )

        assert register_response.status_code == 201
        register_data = register_response.json()
        assert "access_token" in register_data
        assert register_data["token_type"] == "bearer"

        # Extract user ID from response
        user_id = register_data["user"]["id"]
        token = register_data["access_token"]

        # Step 2: Login with same credentials
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": "securepassword123",
            },
        )

        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"

        # Step 3: Access protected resource with token
        tasks_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert tasks_response.status_code == 200
        tasks_data = tasks_response.json()
        assert "tasks" in tasks_data
        assert "total" in tasks_data

    @pytest.mark.asyncio
    async def test_user_can_create_and_list_tasks_after_auth(self, client: AsyncClient):
        """Test that authenticated user can create and list tasks."""
        import uuid

        # Register user
        unique_email = f"taskflow_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Task Flow User",
                "password": "password123",
            },
        )

        assert register_response.status_code == 201
        user_id = register_response.json()["user"]["id"]
        token = register_response.json()["access_token"]

        # Create first task
        create1_response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "First Task", "description": "Description 1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create1_response.status_code == 200
        task1 = create1_response.json()
        assert task1["title"] == "First Task"
        assert task1["completed"] is False

        # Create second task
        create2_response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Second Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create2_response.status_code == 200

        # List all tasks
        list_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] == 2
        assert len(list_data["tasks"]) == 2

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_users_tasks(self, client: AsyncClient):
        """Test that users cannot access other users' tasks."""
        import uuid

        # Create two users
        email1 = f"user1_{uuid.uuid4().hex[:8]}@example.com"
        email2 = f"user2_{uuid.uuid4().hex[:8]}@example.com"

        # Register user 1
        reg1 = await client.post(
            "/api/auth/register",
            json={"email": email1, "name": "User 1", "password": "pass123"},
        )
        user1_id = reg1.json()["user"]["id"]
        user1_token = reg1.json()["access_token"]

        # Register user 2
        reg2 = await client.post(
            "/api/auth/register",
            json={"email": email2, "name": "User 2", "password": "pass123"},
        )
        user2_id = reg2.json()["user"]["id"]
        user2_token = reg2.json()["access_token"]

        # User 1 creates a task
        await client.post(
            f"/api/{user1_id}/tasks",
            json={"title": "User 1's Task"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # User 2 tries to access User 1's tasks
        response = await client.get(
            f"/api/{user1_id}/tasks",
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # Should be forbidden (different user_id in path)
        assert response.status_code == 403

        # User 2 can access their own tasks
        my_tasks_response = await client.get(
            f"/api/{user2_id}/tasks",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert my_tasks_response.status_code == 200
        assert my_tasks_response.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_token_remains_valid_after_multiple_requests(self, client: AsyncClient):
        """Test that token works for multiple sequential requests."""
        import uuid

        # Register user
        unique_email = f"sequential_{uuid.uuid4().hex[:8]}@example.com"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Sequential User",
                "password": "password123",
            },
        )

        token = register_response.json()["access_token"]
        user_id = register_response.json()["user"]["id"]

        # Make multiple requests with the same token
        for i in range(5):
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_produces_different_token_than_registration(self, client: AsyncClient):
        """Test that login and registration produce different tokens."""
        import uuid
        import time

        unique_email = f"tokendiff_{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # Register user
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Token Diff User",
                "password": password,
            },
        )
        reg_token = reg_response.json()["access_token"]

        # Wait briefly to ensure different iat
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

        # Tokens should be different
        assert reg_token != login_token

        # Both should work for authenticated requests
        user_id = reg_response.json()["user"]["id"]

        reg_token_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {reg_token}"},
        )
        assert reg_token_response.status_code == 200

        login_token_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert login_token_response.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_token_rejected_on_protected_endpoint(self, client: AsyncClient):
        """Test that invalid tokens are rejected on protected endpoints."""
        import uuid

        # Register user
        unique_email = f"invalidtok_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Invalid Token User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]

        # Try various invalid token formats
        invalid_tokens = [
            "invalid-token",
            "not.a.valid.jwt",
            "",
            "Bearer",
            "Bearer ",
        ]

        for invalid_token in invalid_tokens:
            headers = {}
            if invalid_token:
                headers["Authorization"] = f"Bearer {invalid_token}"

            response = await client.get(f"/api/{user_id}/tasks", headers=headers)
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, client: AsyncClient):
        """Test that expired tokens are rejected."""
        # This would require creating a token with past expiry
        # For now, we test with a malformed token
        import uuid

        unique_email = f"expired_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Expired Token User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]

        # Create an expired token manually
        import sys
        sys.path.insert(0, 'backend/src')
        from auth import create_access_token
        from datetime import timedelta

        expired_token = create_access_token(
            user_id,
            unique_email,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401


class TestAuthEdgeCases:
    """Tests for authentication edge cases."""

    @pytest.mark.asyncio
    async def test_register_with_very_long_name(self, client: AsyncClient):
        """Test registration with name at max length."""
        import uuid

        long_name = "a" * 255  # Max length
        unique_email = f"longname_{uuid.uuid4().hex[:8]}@example.com"

        response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": long_name,
                "password": "password123",
            },
        )

        # Should succeed (255 chars is valid)
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_with_very_long_title(self, client: AsyncClient):
        """Test registration with name exceeding max length."""
        import uuid

        too_long_name = "a" * 256  # Exceeds max length
        unique_email = f"toolong_{uuid.uuid4().hex[:8]}@example.com"

        response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": too_long_name,
                "password": "password123",
            },
        )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_response_contains_same_user_as_registration(self, client: AsyncClient):
        """Test that login returns same user data as registration."""
        import uuid

        unique_email = f"consistency_{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"
        name = "Consistency Test User"

        # Register
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": name,
                "password": password,
            },
        )
        reg_data = reg_response.json()
        reg_user = reg_data["user"]

        # Login
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )
        login_data = login_response.json()
        login_user = login_data["user"]

        # User data should be consistent
        assert reg_user["id"] == login_user["id"]
        assert reg_user["email"] == login_user["email"]
        assert reg_user["name"] == login_user["name"]
