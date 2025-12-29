"""Tests for task endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    """Test task creation endpoint."""
    # First register and login
    register_response = await client.post(
        "/api/auth/register",
        json={
            "email": "taskuser@example.com",
            "name": "Task User",
            "password": "password123",
        },
    )

    if register_response.status_code == 409:
        # User already exists, login instead
        login_response = await client.post(
            "/api/auth/login",
            json={
                "email": "taskuser@example.com",
                "password": "password123",
            },
        )
    else:
        login_response = register_response

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Create a task
    response = await client.post(
        "/api/taskuser/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] == False


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient):
    """Test listing tasks endpoint."""
    # Get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # List tasks
    response = await client.get(
        "/api/taskuser/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert isinstance(data["tasks"], list)


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    """Test updating a task endpoint."""
    # Get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # First create a task
    create_response = await client.post(
        "/api/taskuser/tasks",
        json={"title": "Task to Update"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_response.json()["id"]

    # Update the task
    response = await client.put(
        f"/api/taskuser/tasks/{task_id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] == True


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    """Test deleting a task endpoint."""
    # Get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # First create a task
    create_response = await client.post(
        "/api/taskuser/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = await client.delete(
        f"/api/taskuser/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(
        f"/api/taskuser/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_task_completion(client: AsyncClient):
    """Test toggling task completion status endpoint."""
    # Get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # First create a task (initially not completed)
    create_response = await client.post(
        "/api/taskuser/tasks",
        json={"title": "Task to Toggle", "description": "Test completion toggle"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 200
    task_data = create_response.json()
    task_id = task_data["id"]
    assert task_data["completed"] == False

    # Toggle completion to True
    toggle_response = await client.patch(
        f"/api/taskuser/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert toggle_response.status_code == 200
    data = toggle_response.json()
    assert data["id"] == task_id
    assert data["user_id"] == "taskuser"
    assert data["title"] == "Task to Toggle"
    assert data["description"] == "Test completion toggle"
    assert data["completed"] == True
    assert "created_at" in data
    assert "updated_at" in data

    # Toggle completion back to False
    toggle_again_response = await client.patch(
        f"/api/taskuser/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert toggle_again_response.status_code == 200
    data_again = toggle_again_response.json()
    assert data_again["id"] == task_id
    assert data_again["completed"] == False


@pytest.mark.asyncio
async def test_toggle_task_completion_not_found(client: AsyncClient):
    """Test toggling completion for non-existent task returns 404."""
    # Get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    # Try to toggle a non-existent task
    response = await client.patch(
        "/api/taskuser/tasks/999999/complete",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_toggle_task_completion_unauthorized(client: AsyncClient):
    """Test toggling completion without authentication returns 401."""
    # Try to toggle without token
    response = await client.patch(
        "/api/taskuser/tasks/1/complete",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_toggle_task_completion_wrong_user(client: AsyncClient):
    """Test that users cannot toggle other users' tasks."""
    # Create first user and task
    register1 = await client.post(
        "/api/auth/register",
        json={
            "email": "user1_toggle@example.com",
            "name": "User One",
            "password": "password123",
        },
    )

    if register1.status_code == 409:
        login1 = await client.post(
            "/api/auth/login",
            json={
                "email": "user1_toggle@example.com",
                "password": "password123",
            },
        )
    else:
        login1 = register1

    token1 = login1.json()["access_token"]

    # Create task as user1
    create_response = await client.post(
        "/api/user1_toggle/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    task_id = create_response.json()["id"]

    # Create second user
    register2 = await client.post(
        "/api/auth/register",
        json={
            "email": "user2_toggle@example.com",
            "name": "User Two",
            "password": "password123",
        },
    )

    if register2.status_code == 409:
        login2 = await client.post(
            "/api/auth/login",
            json={
                "email": "user2_toggle@example.com",
                "password": "password123",
            },
        )
    else:
        login2 = register2

    token2 = login2.json()["access_token"]

    # Try to toggle user1's task as user2
    response = await client.patch(
        f"/api/user1_toggle/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token2}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot modify other users' tasks"
