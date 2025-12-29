"""Integration tests for full task CRUD flow."""
import pytest
from httpx import AsyncClient

import sys
sys.path.insert(0, 'backend/src')


class TestTaskCRUDFlow:
    """End-to-end tests for complete task CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_task_crud_lifecycle(self, client: AsyncClient):
        """Test complete lifecycle: create -> read -> update -> delete."""
        import uuid

        # Setup: Register user and get token
        unique_email = f"crud_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "CRUD User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Step 1: CREATE - Create a new task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 200
        task = create_response.json()
        assert task["id"] is not None
        assert task["title"] == "Test Task"
        assert task["description"] == "Test Description"
        assert task["completed"] is False
        task_id = task["id"]

        # Step 2: READ - Get the task by ID
        get_response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_response.status_code == 200
        fetched_task = get_response.json()
        assert fetched_task["id"] == task_id
        assert fetched_task["title"] == "Test Task"

        # Step 3: UPDATE - Update the task
        update_response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={
                "title": "Updated Task",
                "description": "Updated Description",
                "completed": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["title"] == "Updated Task"
        assert updated_task["description"] == "Updated Description"
        assert updated_task["completed"] is True

        # Step 4: DELETE - Delete the task
        delete_response = await client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_response.status_code == 204

        # Verify deletion
        get_deleted_response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_deleted_response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_multiple_tasks(self, client: AsyncClient):
        """Test creating multiple tasks for a user."""
        import uuid

        unique_email = f"multi_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Multi Task User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create 5 tasks
        task_titles = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]
        created_ids = []

        for title in task_titles:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": title},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            created_ids.append(response.json()["id"])

        # List all tasks
        list_response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 5
        assert len(data["tasks"]) == 5

    @pytest.mark.asyncio
    async def test_task_pagination(self, client: AsyncClient):
        """Test task list pagination."""
        import uuid

        unique_email = f"page_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Pagination User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create 10 tasks
        for i in range(10):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i}"},
                headers={"Authorization": f"Bearer {token}"},
            )

        # Get first page (limit 3, skip 0)
        page1 = await client.get(
            f"/api/{user_id}/tasks?skip=0&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert page1.json()["total"] == 10
        assert len(page1.json()["tasks"]) == 3

        # Get second page
        page2 = await client.get(
            f"/api/{user_id}/tasks?skip=3&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert len(page2.json()["tasks"]) == 3

        # Get last page
        page3 = await client.get(
            f"/api/{user_id}/tasks?skip=9&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert len(page3.json()["tasks"]) == 1

    @pytest.mark.asyncio
    async def test_filter_tasks_by_completion(self, client: AsyncClient):
        """Test filtering tasks by completion status."""
        import uuid

        unique_email = f"filter_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Filter User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create tasks with different completion status
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Active Task 1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Completed Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Active Task 2"},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Mark one as completed
        tasks = (await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )).json()["tasks"]
        completed_task = next(t for t in tasks if t["title"] == "Completed Task")
        await client.patch(
            f"/api/{user_id}/tasks/{completed_task['id']}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Filter for active tasks
        active_response = await client.get(
            f"/api/{user_id}/tasks?completed=false",
            headers={"Authorization": f"Bearer {token}"},
        )
        active_tasks = active_response.json()["tasks"]
        assert all(not t["completed"] for t in active_tasks)
        assert len(active_tasks) == 2

        # Filter for completed tasks
        completed_response = await client.get(
            f"/api/{user_id}/tasks?completed=true",
            headers={"Authorization": f"Bearer {token}"},
        )
        completed_tasks = completed_response.json()["tasks"]
        assert all(t["completed"] for t in completed_tasks)
        assert len(completed_tasks) == 1


class TestTaskValidation:
    """Tests for task input validation."""

    @pytest.mark.asyncio
    async def test_create_task_without_title(self, client: AsyncClient):
        """Test that creating a task without title fails."""
        import uuid

        unique_email = f"notitle_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "No Title User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        response = await client.post(
            f"/api/{user_id}/tasks",
            json={"description": "No title task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_with_empty_title(self, client: AsyncClient):
        """Test that creating a task with empty title fails."""
        import uuid

        unique_email = f"empty_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Empty Title User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": ""},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_title_too_long(self, client: AsyncClient):
        """Test that creating a task with title > 200 chars fails."""
        import uuid

        unique_email = f"longtitle_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Long Title User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        long_title = "x" * 201
        response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": long_title},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_partial_update_task(self, client: AsyncClient):
        """Test partial update of task (only some fields)."""
        import uuid

        unique_email = f"partial_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Partial Update User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Original Title", "description": "Original Desc"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = create_response.json()["id"]

        # Update only title
        update_response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json={"title": "New Title Only"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == "New Title Only"
        assert updated["description"] == "Original Desc"  # Unchanged


class TestTaskIsolation:
    """Tests for task data isolation between users."""

    @pytest.mark.asyncio
    async def test_users_cannot_see_each_others_tasks(self, client: AsyncClient):
        """Test that users can only see their own tasks."""
        import uuid

        # Create two users
        email1 = f"user1_{uuid.uuid4().hex[:8]}@example.com"
        email2 = f"user2_{uuid.uuid4().hex[:8]}@example.com"

        reg1 = await client.post(
            "/api/auth/register",
            json={"email": email1, "name": "User 1", "password": "pass123"},
        )
        user1_id = reg1.json()["user"]["id"]
        user1_token = reg1.json()["access_token"]

        reg2 = await client.post(
            "/api/auth/register",
            json={"email": email2, "name": "User 2", "password": "pass123"},
        )
        user2_id = reg2.json()["user"]["id"]
        user2_token = reg2.json()["access_token"]

        # User 1 creates a task
        await client.post(
            f"/api/{user1_id}/tasks",
            json={"title": "User 1's Private Task"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )

        # User 1 sees their task
        user1_tasks = (await client.get(
            f"/api/{user1_id}/tasks",
            headers={"Authorization": f"Bearer {user1_token}"},
        )).json()
        assert user1_tasks["total"] == 1

        # User 2 does not see User 1's task
        user2_tasks = (await client.get(
            f"/api/{user2_id}/tasks",
            headers={"Authorization": f"Bearer {user2_token}"},
        )).json()
        assert user2_tasks["total"] == 0

    @pytest.mark.asyncio
    async def test_users_cannot_modify_each_others_tasks(self, client: AsyncClient):
        """Test that users cannot modify other users' tasks."""
        import uuid

        email1 = f"mod1_{uuid.uuid4().hex[:8]}@example.com"
        email2 = f"mod2_{uuid.uuid4().hex[:8]}@example.com"

        reg1 = await client.post(
            "/api/auth/register",
            json={"email": email1, "name": "User 1", "password": "pass123"},
        )
        user1_id = reg1.json()["user"]["id"]
        user1_token = reg1.json()["access_token"]

        reg2 = await client.post(
            "/api/auth/register",
            json={"email": email2, "name": "User 2", "password": "pass123"},
        )
        user2_id = reg2.json()["user"]["id"]
        user2_token = reg2.json()["access_token"]

        # User 1 creates a task
        task = (await client.post(
            f"/api/{user1_id}/tasks",
            json={"title": "User 1's Task"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )).json()

        # User 2 tries to modify it
        update_response = await client.put(
            f"/api/{user1_id}/tasks/{task['id']}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert update_response.status_code == 404  # Not found for user 2

        # Verify task wasn't modified
        get_response = await client.get(
            f"/api/{user1_id}/tasks/{task['id']}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert get_response.json()["title"] == "User 1's Task"

    @pytest.mark.asyncio
    async def test_users_cannot_delete_each_others_tasks(self, client: AsyncClient):
        """Test that users cannot delete other users' tasks."""
        import uuid

        email1 = f"del1_{uuid.uuid4().hex[:8]}@example.com"
        email2 = f"del2_{uuid.uuid4().hex[:8]}@example.com"

        reg1 = await client.post(
            "/api/auth/register",
            json={"email": email1, "name": "User 1", "password": "pass123"},
        )
        user1_id = reg1.json()["user"]["id"]
        user1_token = reg1.json()["access_token"]

        reg2 = await client.post(
            "/api/auth/register",
            json={"email": email2, "name": "User 2", "password": "pass123"},
        )
        user2_token = reg2.json()["access_token"]

        # User 1 creates a task
        task = (await client.post(
            f"/api/{user1_id}/tasks",
            json={"title": "User 1's Task"},
            headers={"Authorization": f"Bearer {user1_token}"},
        )).json()

        # User 2 tries to delete it
        delete_response = await client.delete(
            f"/api/{user1_id}/tasks/{task['id']}",
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert delete_response.status_code == 404  # Not found for user 2

        # Verify task still exists
        get_response = await client.get(
            f"/api/{user1_id}/tasks/{task['id']}",
            headers={"Authorization": f"Bearer {user1_token}"},
        )
        assert get_response.status_code == 200


class TestTaskCompletion:
    """Tests for task completion toggle."""

    @pytest.mark.asyncio
    async def test_toggle_completion(self, client: AsyncClient):
        """Test toggling task completion status."""
        import uuid

        unique_email = f"toggle_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "Toggle User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        # Create task
        task = (await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Toggle Me"},
            headers={"Authorization": f"Bearer {token}"},
        )).json()

        # Toggle to completed
        toggle1 = await client.patch(
            f"/api/{user_id}/tasks/{task['id']}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert toggle1.json()["completed"] is True

        # Toggle back to incomplete
        toggle2 = await client.patch(
            f"/api/{user_id}/tasks/{task['id']}/complete",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert toggle2.json()["completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_nonexistent_task(self, client: AsyncClient):
        """Test toggling a non-existent task returns 404."""
        import uuid

        unique_email = f"notoggle_{uuid.uuid4().hex[:8]}@example.com"
        reg_response = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "name": "No Toggle User",
                "password": "password123",
            },
        )
        user_id = reg_response.json()["user"]["id"]
        token = reg_response.json()["access_token"]

        response = await client.patch(
            f"/api/{user_id}/tasks/99999/complete",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
