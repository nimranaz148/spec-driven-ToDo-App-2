"""Comprehensive tests for user data isolation.

Security Requirements:
- Users can only access their own tasks
- Return 404 (not 403) when task belongs to another user to avoid revealing task existence
- Return 403 when user_id in URL path doesn't match authenticated user
- All task queries must filter by authenticated user's ID from JWT token
"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def user_a_auth(client: AsyncClient) -> dict:
    """Create and authenticate User A."""
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "user_a@example.com",
            "name": "User A",
            "password": "password123",
        },
    )

    if register_response.status_code == 409:
        # User already exists, login instead
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "user_a@example.com",
                "password": "password123",
            },
        )
    else:
        login_response = register_response

    assert login_response.status_code == 200
    data = login_response.json()
    return {
        "token": data["access_token"],
        "user_id": data["user_id"],
    }


@pytest.fixture
async def user_b_auth(client: AsyncClient) -> dict:
    """Create and authenticate User B."""
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "user_b@example.com",
            "name": "User B",
            "password": "password456",
        },
    )

    if register_response.status_code == 409:
        # User already exists, login instead
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "user_b@example.com",
                "password": "password456",
            },
        )
    else:
        login_response = register_response

    assert login_response.status_code == 200
    data = login_response.json()
    return {
        "token": data["access_token"],
        "user_id": data["user_id"],
    }


@pytest.fixture
async def user_a_task(client: AsyncClient, user_a_auth: dict) -> dict:
    """Create a task for User A."""
    response = await client.post(
        f"/api/{user_a_auth['user_id']}/tasks",
        json={
            "title": "User A's Private Task",
            "description": "This belongs to User A only",
        },
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def user_b_task(client: AsyncClient, user_b_auth: dict) -> dict:
    """Create a task for User B."""
    response = await client.post(
        f"/api/{user_b_auth['user_id']}/tasks",
        json={
            "title": "User B's Private Task",
            "description": "This belongs to User B only",
        },
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )
    assert response.status_code == 201
    return response.json()


# ============================================================================
# Test 1: User A cannot see User B's tasks in list view
# ============================================================================


@pytest.mark.asyncio
async def test_user_a_cannot_list_user_b_tasks(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
    user_b_task: dict,
):
    """User A cannot see User B's tasks when listing their own tasks."""
    # User A lists their tasks
    response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify User A can see their own task
    task_ids = [task["id"] for task in data["tasks"]]
    assert user_a_task["id"] in task_ids

    # Verify User A CANNOT see User B's task
    assert user_b_task["id"] not in task_ids

    # Verify all returned tasks belong to User A
    for task in data["tasks"]:
        assert task["user_id"] == user_a_auth["user_id"]


@pytest.mark.asyncio
async def test_user_b_cannot_list_user_a_tasks(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
    user_b_task: dict,
):
    """User B cannot see User A's tasks when listing their own tasks."""
    # User B lists their tasks
    response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify User B can see their own task
    task_ids = [task["id"] for task in data["tasks"]]
    assert user_b_task["id"] in task_ids

    # Verify User B CANNOT see User A's task
    assert user_a_task["id"] not in task_ids

    # Verify all returned tasks belong to User B
    for task in data["tasks"]:
        assert task["user_id"] == user_b_auth["user_id"]


# ============================================================================
# Test 2: User A cannot access User B's specific task (returns 404)
# ============================================================================


@pytest.mark.asyncio
async def test_user_a_cannot_get_user_b_task_returns_404(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_task: dict,
):
    """User A gets 404 when trying to access User B's task (security: don't reveal existence)."""
    # User A tries to get User B's task using their own user_id in path
    response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_user_b_cannot_get_user_a_task_returns_404(
    client: AsyncClient,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User B gets 404 when trying to access User A's task (security: don't reveal existence)."""
    # User B tries to get User A's task using their own user_id in path
    response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# ============================================================================
# Test 3: User A cannot update User B's task (returns 404)
# ============================================================================


@pytest.mark.asyncio
async def test_user_a_cannot_update_user_b_task_returns_404(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_task: dict,
):
    """User A gets 404 when trying to update User B's task."""
    # User A tries to update User B's task
    response = await client.put(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}",
        json={
            "title": "Malicious Update Attempt",
            "description": "User A trying to modify User B's task",
        },
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_user_b_cannot_update_user_a_task_returns_404(
    client: AsyncClient,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User B gets 404 when trying to update User A's task."""
    # User B tries to update User A's task
    response = await client.put(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        json={
            "title": "Malicious Update Attempt",
            "description": "User B trying to modify User A's task",
        },
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_update_does_not_modify_other_users_task(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_b_task: dict,
):
    """Verify that attempted cross-user update doesn't modify the task."""
    original_title = user_b_task["title"]
    original_description = user_b_task["description"]

    # User A tries to update User B's task (should fail)
    update_response = await client.put(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}",
        json={
            "title": "HACKED",
            "description": "This should never be applied",
        },
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert update_response.status_code == 404

    # Verify User B's task is unchanged
    get_response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )
    assert get_response.status_code == 200
    task_data = get_response.json()
    assert task_data["title"] == original_title
    assert task_data["description"] == original_description


# ============================================================================
# Test 4: User A cannot delete User B's task (returns 404)
# ============================================================================


@pytest.mark.asyncio
async def test_user_a_cannot_delete_user_b_task_returns_404(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_task: dict,
):
    """User A gets 404 when trying to delete User B's task."""
    # User A tries to delete User B's task
    response = await client.delete(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_user_b_cannot_delete_user_a_task_returns_404(
    client: AsyncClient,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User B gets 404 when trying to delete User A's task."""
    # User B tries to delete User A's task
    response = await client.delete(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_delete_does_not_remove_other_users_task(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_b_task: dict,
):
    """Verify that attempted cross-user delete doesn't remove the task."""
    # User A tries to delete User B's task (should fail)
    delete_response = await client.delete(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert delete_response.status_code == 404

    # Verify User B's task still exists
    get_response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == user_b_task["id"]


# ============================================================================
# Test 5: User A cannot toggle User B's task completion (returns 404)
# ============================================================================


@pytest.mark.asyncio
async def test_user_a_cannot_toggle_user_b_task_completion_returns_404(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_task: dict,
):
    """User A gets 404 when trying to toggle User B's task completion."""
    # User A tries to toggle User B's task completion
    response = await client.patch(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}/complete",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_user_b_cannot_toggle_user_a_task_completion_returns_404(
    client: AsyncClient,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User B gets 404 when trying to toggle User A's task completion."""
    # User B tries to toggle User A's task completion
    response = await client.patch(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}/complete",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )

    # Should return 404, not 403, to avoid revealing that the task exists
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_toggle_does_not_modify_other_users_task(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_b_task: dict,
):
    """Verify that attempted cross-user toggle doesn't modify the task."""
    original_completed = user_b_task["completed"]

    # User A tries to toggle User B's task (should fail)
    toggle_response = await client.patch(
        f"/api/{user_a_auth['user_id']}/tasks/{user_b_task['id']}/complete",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert toggle_response.status_code == 404

    # Verify User B's task completion status is unchanged
    get_response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks/{user_b_task['id']}",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )
    assert get_response.status_code == 200
    task_data = get_response.json()
    assert task_data["completed"] == original_completed


# ============================================================================
# Test 6: URL path manipulation (user_id mismatch) returns 403
# ============================================================================


@pytest.mark.asyncio
async def test_list_tasks_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
):
    """User A cannot access User B's endpoint by putting their user_id in path."""
    # User A tries to access User B's tasks endpoint
    response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access other users' tasks"


@pytest.mark.asyncio
async def test_create_task_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
):
    """User A cannot create tasks for User B by putting their user_id in path."""
    # User A tries to create a task for User B
    response = await client.post(
        f"/api/{user_b_auth['user_id']}/tasks",
        json={
            "title": "Malicious Task",
            "description": "Trying to create task for another user",
        },
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot create tasks for other users"


@pytest.mark.asyncio
async def test_get_task_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User A cannot access their own task via User B's endpoint."""
    # User A tries to access their own task through User B's endpoint path
    response = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot access other users' tasks"


@pytest.mark.asyncio
async def test_update_task_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User A cannot update via User B's endpoint path."""
    # User A tries to update their task through User B's endpoint path
    response = await client.put(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        json={"title": "Updated via wrong endpoint"},
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot update other users' tasks"


@pytest.mark.asyncio
async def test_delete_task_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User A cannot delete via User B's endpoint path."""
    # User A tries to delete their task through User B's endpoint path
    response = await client.delete(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot delete other users' tasks"


@pytest.mark.asyncio
async def test_toggle_task_with_wrong_user_id_in_path_returns_403(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
    user_a_task: dict,
):
    """User A cannot toggle completion via User B's endpoint path."""
    # User A tries to toggle their task through User B's endpoint path
    response = await client.patch(
        f"/api/{user_b_auth['user_id']}/tasks/{user_a_task['id']}/complete",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 403 for URL manipulation attempt
    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot modify other users' tasks"


# ============================================================================
# Test 7: JWT token validation ensures correct user_id
# ============================================================================


@pytest.mark.asyncio
async def test_jwt_user_id_extraction_is_correct(
    client: AsyncClient,
    user_a_auth: dict,
    user_a_task: dict,
):
    """Verify that user_id from JWT matches the user who can access the task."""
    # User A accesses their task
    response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks/{user_a_task['id']}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    assert response.status_code == 200
    task_data = response.json()

    # Verify the task's user_id matches the authenticated user
    assert task_data["user_id"] == user_a_auth["user_id"]


@pytest.mark.asyncio
async def test_all_operations_filter_by_jwt_user_id(
    client: AsyncClient,
    user_a_auth: dict,
):
    """Comprehensive test that all operations respect JWT user_id filtering."""
    # Create a task
    create_response = await client.post(
        f"/api/{user_a_auth['user_id']}/tasks",
        json={"title": "Test Task for JWT Filtering"},
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # List tasks - should only return User A's tasks
    list_response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert list_response.status_code == 200
    for task in list_response.json()["tasks"]:
        assert task["user_id"] == user_a_auth["user_id"]

    # Get task - should return the task
    get_response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["user_id"] == user_a_auth["user_id"]

    # Update task - should work
    update_response = await client.put(
        f"/api/{user_a_auth['user_id']}/tasks/{task_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["user_id"] == user_a_auth["user_id"]

    # Toggle completion - should work
    toggle_response = await client.patch(
        f"/api/{user_a_auth['user_id']}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["user_id"] == user_a_auth["user_id"]

    # Delete task - should work
    delete_response = await client.delete(
        f"/api/{user_a_auth['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert delete_response.status_code == 204


# ============================================================================
# Test 8: Edge cases and security verification
# ============================================================================


@pytest.mark.asyncio
async def test_nonexistent_task_returns_404_not_different_error(
    client: AsyncClient,
    user_a_auth: dict,
):
    """Non-existent task returns 404, same as unauthorized access (security)."""
    # Try to access a task that definitely doesn't exist
    response = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks/999999999",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )

    # Should return 404 with same message as cross-user access
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_multiple_users_see_only_their_own_tasks(
    client: AsyncClient,
    user_a_auth: dict,
    user_b_auth: dict,
):
    """Create multiple tasks for multiple users and verify isolation."""
    # Create 3 tasks for User A
    user_a_tasks = []
    for i in range(3):
        response = await client.post(
            f"/api/{user_a_auth['user_id']}/tasks",
            json={"title": f"User A Task {i+1}"},
            headers={"Authorization": f"Bearer {user_a_auth['token']}"},
        )
        assert response.status_code == 201
        user_a_tasks.append(response.json()["id"])

    # Create 2 tasks for User B
    user_b_tasks = []
    for i in range(2):
        response = await client.post(
            f"/api/{user_b_auth['user_id']}/tasks",
            json={"title": f"User B Task {i+1}"},
            headers={"Authorization": f"Bearer {user_b_auth['token']}"},
        )
        assert response.status_code == 201
        user_b_tasks.append(response.json()["id"])

    # User A lists tasks - should see exactly 3 tasks
    response_a = await client.get(
        f"/api/{user_a_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_a_auth['token']}"},
    )
    assert response_a.status_code == 200
    tasks_a = response_a.json()["tasks"]
    assert len([t for t in tasks_a if t["id"] in user_a_tasks]) >= 3
    assert all(t["id"] not in user_b_tasks for t in tasks_a)

    # User B lists tasks - should see exactly 2 tasks
    response_b = await client.get(
        f"/api/{user_b_auth['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user_b_auth['token']}"},
    )
    assert response_b.status_code == 200
    tasks_b = response_b.json()["tasks"]
    assert len([t for t in tasks_b if t["id"] in user_b_tasks]) >= 2
    assert all(t["id"] not in user_a_tasks for t in tasks_b)
