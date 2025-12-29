"""Integration tests for logout flow - T049-US3."""
import pytest
import uuid
from httpx import AsyncClient


class TestLogoutIntegration:
    """Integration tests for complete logout flow."""

    @pytest.mark.asyncio
    async def test_complete_logout_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> logout -> verify token invalid."""
        unique_email = f"flow_{uuid.uuid4().hex[:8]}@example.com"
        password = "securepassword123"

        # Step 1: Register user
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Flow Test User",
                "password": password,
            },
        )
        assert register_response.status_code == 201
        register_token = register_response.json()["access_token"]

        # Step 2: Logout with registration token
        logout_response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {register_token}"},
        )
        assert logout_response.status_code == 200

        # Wait a moment to ensure different timestamp in JWT
        import asyncio
        await asyncio.sleep(1.1)

        # Step 3: Login again
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]

        # Step 4: New token should work
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login_token}"},
        )
        assert me_response.status_code == 200

        # Step 5: Old token should still be invalid
        old_token_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {register_token}"},
        )
        assert old_token_response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_invalidates_only_specific_token(self, client: AsyncClient):
        """Test that logout invalidates only the specific token, not all user sessions."""
        unique_email = f"multi_{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # Register user
        await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Multi Session User",
                "password": password,
            },
        )

        # Login twice to get two different tokens
        login1 = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": password},
        )
        token1 = login1.json()["access_token"]

        # Wait a bit to ensure different iat (tokens issued in same second are identical)
        import asyncio
        await asyncio.sleep(1.1)

        login2 = await client.post(
            "/api/auth/login",
            json={"email": unique_email, "password": password},
        )
        token2 = login2.json()["access_token"]

        # Both tokens should work
        assert (await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"})).status_code == 200
        assert (await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})).status_code == 200

        # Logout with token1
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token1}"},
        )

        # Token1 should be invalid
        assert (await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"})).status_code == 401

        # Token2 should still work
        assert (await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})).status_code == 200

    @pytest.mark.asyncio
    async def test_logout_prevents_access_to_protected_resources(self, client: AsyncClient):
        """Test that logout prevents access to all protected endpoints."""
        unique_email = f"protected_{uuid.uuid4().hex[:8]}@example.com"
        password = "password123"

        # Register
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Protected Test",
                "password": password,
            },
        )
        token = register_response.json()["access_token"]
        user_id = register_response.json()["user"]["id"]

        # Verify token works with protected endpoints
        me_before = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_before.status_code == 200

        tasks_before = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tasks_before.status_code == 200

        # Logout
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        # All protected endpoints should reject the token
        me_after = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_after.status_code == 401

        tasks_after = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tasks_after.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_error_handling(self, client: AsyncClient):
        """Test error handling in logout flow."""
        # Test with no Authorization header
        no_auth = await client.post("/api/auth/logout")
        assert no_auth.status_code in [401, 403]

        # Test with malformed Authorization header
        malformed = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "NotBearer token"},
        )
        assert malformed.status_code in [401, 403]

        # Test with invalid token format
        invalid = await client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert invalid.status_code == 401

    @pytest.mark.asyncio
    async def test_token_blacklist_persistence_in_memory(self, client: AsyncClient):
        """Test that blacklisted tokens remain invalid across multiple requests."""
        unique_email = f"persist_{uuid.uuid4().hex[:8]}@example.com"

        # Register and get token
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Persist Test",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]

        # Logout
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try to use token multiple times - should fail every time
        for _ in range(3):
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 401
            assert "revoked" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_logout_with_expired_token(self, client: AsyncClient):
        """Test logout behavior with expired token (edge case)."""
        # Create a token that expires immediately
        from datetime import timedelta
        from src.auth import create_access_token

        expired_token = create_access_token(
            user_id="test-user",
            email="test@example.com",
            expires_delta=timedelta(seconds=-1)  # Already expired
        )

        # Attempt to logout with expired token should fail
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_concurrent_logout_attempts(self, client: AsyncClient):
        """Test that concurrent logout attempts with same token are handled correctly."""
        import asyncio

        unique_email = f"concurrent_{uuid.uuid4().hex[:8]}@example.com"

        # Register and get token
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Concurrent Test",
                "password": "password123",
            },
        )
        token = register_response.json()["access_token"]

        # Attempt logout concurrently
        logout_tasks = [
            client.post(
                "/api/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
            )
            for _ in range(3)
        ]

        results = await asyncio.gather(*logout_tasks, return_exceptions=True)

        # At least one should succeed
        success_count = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 200)
        assert success_count >= 1

        # After all attempts, token should be invalid
        verify_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert verify_response.status_code == 401
