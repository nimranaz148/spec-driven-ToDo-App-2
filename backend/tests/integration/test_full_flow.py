"""Integration tests for full user workflow from registration to deletion."""
import pytest
from httpx import AsyncClient
import uuid


class TestFullUserWorkflow:
    """End-to-end tests for complete user workflow."""

    @pytest.mark.asyncio
    async def test_complete_user_journey(self, client: AsyncClient):
        """
        Test complete user journey:
        1. User registers with email/password
        2. User logs in and receives JWT token
        3. User creates 3 tasks
        4. User lists all tasks (verify 3 tasks returned)
        5. User updates one task
        6. User toggles completion on another task
        7. User deletes one task (verify 2 tasks remain)
        8. User logs out
        9. Verify token is invalidated
        """
        # Step 1: Register a new user
        unique_email = f"fullflow_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123!"
        register_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Full Flow User",
                "password": password,
            },
        )
        assert register_response.status_code == 201, f"Registration failed: {register_response.json()}"
        reg_data = register_response.json()
        assert "access_token" in reg_data
        assert "user" in reg_data
        user_id = reg_data["user"]["id"]
        initial_token = reg_data["access_token"]

        # Step 2: Login with same credentials
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
        login_data = login_response.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # Verify different tokens
        assert token != initial_token, "Login token should be different from registration token"

        # Step 3: Create 3 tasks
        task_ids = []
        tasks_to_create = [
            {"title": "Buy groceries", "description": "Milk, eggs, bread"},
            {"title": "Write documentation", "description": "Update API docs"},
            {"title": "Review pull requests", "description": None},
        ]

        for task_data in tasks_to_create:
            create_response = await client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert create_response.status_code == 200, f"Task creation failed: {create_response.json()}"
            task = create_response.json()
            assert task["title"] == task_data["title"]
            assert task["completed"] is False
            task_ids.append(task["id"])

        assert len(task_ids) == 3, "Should have created 3 tasks"

        # Step 4: List all tasks and verify 3 tasks returned
        list_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200, f"List tasks failed: {list_response.json()}"
        tasks_data = list_response.json()
        assert "tasks" in tasks_data
        assert "total" in tasks_data
        assert tasks_data["total"] == 3, f"Expected 3 tasks, got {tasks_data['total']}"
        assert len(tasks_data["tasks"]) == 3

        # Verify all created task IDs are in the list
        returned_ids = {t["id"] for t in tasks_data["tasks"]}
        assert set(task_ids) == returned_ids, "All created tasks should be in the list"

        # Step 5: Update one task
        task_to_update = task_ids[0]
        update_response = await client.put(
            f"/api/{user_id}/tasks/{task_to_update}",
            json={
                "title": "Buy groceries - UPDATED",
                "description": "Milk, eggs, bread, butter, cheese",
                "completed": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200, f"Update failed: {update_response.json()}"
        updated_task = update_response.json()
        assert updated_task["title"] == "Buy groceries - UPDATED"
        assert updated_task["description"] == "Milk, eggs, bread, butter, cheese"
        assert updated_task["completed"] is False

        # Step 6: Toggle completion on another task
        task_to_toggle = task_ids[1]
        toggle_response = await client.patch(
            f"/api/{user_id}/tasks/{task_to_toggle}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert toggle_response.status_code == 200, f"Toggle failed: {toggle_response.json()}"
        toggled_task = toggle_response.json()
        assert toggled_task["completed"] is True, "Task should be marked as completed"

        # Step 7: Delete one task and verify 2 tasks remain
        task_to_delete = task_ids[2]
        delete_response = await client.delete(
            f"/api/{user_id}/tasks/{task_to_delete}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 204, f"Delete failed: status {delete_response.status_code}"

        # Verify 2 tasks remain
        list_after_delete = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_after_delete.status_code == 200
        remaining_tasks = list_after_delete.json()
        assert remaining_tasks["total"] == 2, f"Expected 2 tasks after delete, got {remaining_tasks['total']}"

        # Verify the deleted task is not in the list
        remaining_ids = {t["id"] for t in remaining_tasks["tasks"]}
        assert task_to_delete not in remaining_ids, "Deleted task should not be in the list"
        assert task_to_update in remaining_ids, "Updated task should still be in the list"
        assert task_to_toggle in remaining_ids, "Toggled task should still be in the list"

        # Step 8: User logs out
        logout_response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status_code == 200, f"Logout failed: {logout_response.json()}"

        # Step 9: Verify token is invalidated
        # Try to access tasks with invalidated token
        invalid_access_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invalid_access_response.status_code == 401, "Token should be invalidated after logout"
        assert "revoked" in invalid_access_response.json()["detail"].lower(), \
            "Error should indicate token was revoked"


    @pytest.mark.asyncio
    async def test_multiple_login_sessions_work_independently(self, client: AsyncClient):
        """
        Test that multiple login sessions for the same user work independently.
        Logging out one session should not affect another.
        """
        unique_email = f"multisession_{uuid.uuid4().hex[:8]}@example.com"
        password = "Password123!"

        # Register user
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Multi Session User",
                "password": password,
            },
        )
        assert reg_response.status_code == 201
        user_id = reg_response.json()["user"]["id"]
        token1 = reg_response.json()["access_token"]

        # Login again to create second session
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": password,
            },
        )
        assert login_response.status_code == 200
        token2 = login_response.json()["access_token"]

        # Both tokens should be different
        assert token1 != token2

        # Both tokens should work
        response1 = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response1.status_code == 200

        response2 = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response2.status_code == 200

        # Logout first session
        logout1 = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert logout1.status_code == 200

        # First token should be invalidated
        response1_after = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert response1_after.status_code == 401

        # Second token should still work
        response2_after = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response2_after.status_code == 200


    @pytest.mark.asyncio
    async def test_workflow_with_task_filtering(self, client: AsyncClient):
        """
        Test workflow with task filtering by completion status.
        """
        unique_email = f"filter_flow_{uuid.uuid4().hex[:8]}@example.com"
        password = "Password123!"

        # Register and login
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Filter Flow User",
                "password": password,
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create 5 tasks
        task_ids = []
        for i in range(5):
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}"},
                headers={"Authorization": f"Bearer {token}"},
            )
            task_ids.append(response.json()["id"])

        # Complete 3 of them
        for task_id in task_ids[:3]:
            await client.patch(
                f"/api/{user_id}/tasks/{task_id}/complete",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get all tasks
        all_tasks = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert all_tasks.json()["total"] == 5

        # Get completed tasks
        completed_tasks = await client.get(
            f"/api/{user_id}/tasks?completed=true",
            headers={"Authorization": f"Bearer {token}"},
        )
        completed_data = completed_tasks.json()
        assert completed_data["total"] == 3
        assert all(t["completed"] for t in completed_data["tasks"])

        # Get active tasks
        active_tasks = await client.get(
            f"/api/{user_id}/tasks?completed=false",
            headers={"Authorization": f"Bearer {token}"},
        )
        active_data = active_tasks.json()
        assert active_data["total"] == 2
        assert all(not t["completed"] for t in active_data["tasks"])


    @pytest.mark.asyncio
    async def test_pagination_in_workflow(self, client: AsyncClient):
        """
        Test pagination works correctly in workflow with many tasks.
        """
        unique_email = f"pagination_{uuid.uuid4().hex[:8]}@example.com"
        password = "Password123!"

        # Register
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Pagination User",
                "password": password,
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create 15 tasks
        for i in range(15):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1:02d}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get first page (5 tasks)
        page1 = await client.get(
            f"/api/{user_id}/tasks?skip=0&limit=5",
            headers={"Authorization": f"Bearer {token}"},
        )
        page1_data = page1.json()
        assert page1_data["total"] == 15
        assert len(page1_data["tasks"]) == 5

        # Get second page
        page2 = await client.get(
            f"/api/{user_id}/tasks?skip=5&limit=5",
            headers={"Authorization": f"Bearer {token}"},
        )
        page2_data = page2.json()
        assert page2_data["total"] == 15
        assert len(page2_data["tasks"]) == 5

        # Get third page
        page3 = await client.get(
            f"/api/{user_id}/tasks?skip=10&limit=5",
            headers={"Authorization": f"Bearer {token}"},
        )
        page3_data = page3.json()
        assert page3_data["total"] == 15
        assert len(page3_data["tasks"]) == 5

        # Ensure no overlap between pages
        page1_ids = {t["id"] for t in page1_data["tasks"]}
        page2_ids = {t["id"] for t in page2_data["tasks"]}
        page3_ids = {t["id"] for t in page3_data["tasks"]}

        assert len(page1_ids & page2_ids) == 0, "Page 1 and 2 should not overlap"
        assert len(page2_ids & page3_ids) == 0, "Page 2 and 3 should not overlap"
        assert len(page1_ids & page3_ids) == 0, "Page 1 and 3 should not overlap"


class TestErrorRecoveryWorkflow:
    """Tests for error handling and recovery in workflows."""

    @pytest.mark.asyncio
    async def test_workflow_continues_after_failed_operation(self, client: AsyncClient):
        """
        Test that workflow can continue after a failed operation.
        """
        unique_email = f"recovery_{uuid.uuid4().hex[:8]}@example.com"

        # Register
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Recovery User",
                "password": "Password123!",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Try to create invalid task (should fail)
        invalid_create = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": ""},  # Empty title
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invalid_create.status_code == 422

        # Create valid task (should succeed)
        valid_create = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Valid Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert valid_create.status_code == 200
        task_id = valid_create.json()["id"]

        # Try to update non-existent task (should fail)
        invalid_update = await client.put(
            f"/api/{user_id}/tasks/99999",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert invalid_update.status_code == 404

        # Update valid task (should succeed)
        valid_update = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "Updated Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert valid_update.status_code == 200

        # Verify the valid task is still accessible
        get_task = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_task.status_code == 200
        assert get_task.json()["title"] == "Updated Task"


    @pytest.mark.asyncio
    async def test_workflow_with_invalid_token_after_logout(self, client: AsyncClient):
        """
        Test that all operations fail with proper error after logout.
        """
        unique_email = f"invalid_token_{uuid.uuid4().hex[:8]}@example.com"

        # Register
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Invalid Token User",
                "password": "Password123!",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create a task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_response.json()["id"]

        # Logout
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try all operations with invalidated token
        operations = [
            ("GET", f"/api/{user_id}/tasks", None),
            ("POST", f"/api/{user_id}/tasks", {"title": "New Task"}),
            ("GET", f"/api/{user_id}/tasks/{task_id}", None),
            ("PUT", f"/api/{user_id}/tasks/{task_id}", {"title": "Updated"}),
            ("PATCH", f"/api/{user_id}/tasks/{task_id}/complete", None),
            ("DELETE", f"/api/{user_id}/tasks/{task_id}", None),
        ]

        for method, url, json_data in operations:
            if method == "GET":
                response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
            elif method == "POST":
                response = await client.post(url, json=json_data, headers={"Authorization": f"Bearer {token}"})
            elif method == "PUT":
                response = await client.put(url, json=json_data, headers={"Authorization": f"Bearer {token}"})
            elif method == "PATCH":
                response = await client.patch(url, headers={"Authorization": f"Bearer {token}"})
            elif method == "DELETE":
                response = await client.delete(url, headers={"Authorization": f"Bearer {token}"})

            assert response.status_code == 401, f"{method} {url} should fail with 401 after logout"
