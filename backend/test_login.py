"""
Test script to verify login functionality
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_auth_flow():
    """Test complete authentication flow"""
    print("=" * 60)
    print("Testing Todo App Authentication")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Test 1: Register a new user
        print("\n1. Registering new user...")
        register_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "SecurePassword123!"
        }

        try:
            response = await client.post("/api/auth/register", json=register_data)
            print(f"   Status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Registration successful!")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Email: {data.get('user', {}).get('email')}")
                print(f"   Token: {data.get('token', '')[:50]}...")
                registration_token = data.get('token')
            else:
                print(f"   ❌ Registration failed: {response.text}")
                # User might already exist, try login anyway
                registration_token = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            registration_token = None

        # Test 2: Login with correct password
        print("\n2. Login with CORRECT password...")
        login_data = {
            "email": "test@example.com",
            "password": "SecurePassword123!"
        }

        try:
            response = await client.post("/api/auth/login", json=login_data)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login successful!")
                print(f"   User ID: {data.get('user', {}).get('id')}")
                print(f"   Email: {data.get('user', {}).get('email')}")
                print(f"   Token: {data.get('token', '')[:50]}...")
                user_id = data.get('user', {}).get('id')
                auth_token = data.get('token')
            else:
                print(f"   ❌ Login failed: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return

        # Test 3: Login with WRONG password (should fail)
        print("\n3. Login with WRONG password (should fail)...")
        wrong_login_data = {
            "email": "test@example.com",
            "password": "WrongPassword456!"
        }

        try:
            response = await client.post("/api/auth/login", json=wrong_login_data)
            print(f"   Status: {response.status_code}")

            if response.status_code == 401:
                print(f"   ✅ Correctly rejected wrong password!")
                print(f"   Error: {response.json()}")
            else:
                print(f"   ❌ SECURITY ISSUE: Wrong password was accepted!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 4: Create a task with authentication
        print("\n4. Creating a task (authenticated)...")
        headers = {"Authorization": f"Bearer {auth_token}"}
        task_data = {
            "title": "Test Task",
            "description": "This is a test task"
        }

        try:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers=headers
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Task created successfully!")
                print(f"   Task ID: {data.get('id')}")
                print(f"   Title: {data.get('title')}")
                task_id = data.get('id')
            else:
                print(f"   ❌ Task creation failed: {response.text}")
                task_id = None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            task_id = None

        # Test 5: List tasks
        print("\n5. Listing tasks...")
        try:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers=headers
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                tasks = response.json()
                print(f"   ✅ Retrieved {len(tasks)} task(s)")
                for task in tasks[:3]:  # Show first 3
                    print(f"      - {task.get('title')} (Completed: {task.get('completed')})")
            else:
                print(f"   ❌ Failed to list tasks: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 6: Toggle task completion
        if task_id:
            print("\n6. Toggling task completion...")
            try:
                response = await client.patch(
                    f"/api/{user_id}/tasks/{task_id}/complete",
                    headers=headers
                )
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Task toggled!")
                    print(f"   Completed: {data.get('completed')}")
                else:
                    print(f"   ❌ Toggle failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Test 7: Logout
        print("\n7. Logging out...")
        try:
            response = await client.post(
                "/api/auth/logout",
                headers=headers
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ Logout successful!")
                print(f"   Message: {response.json().get('message')}")
            else:
                print(f"   ❌ Logout failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 8: Try to use invalidated token
        print("\n8. Trying to use invalidated token (should fail)...")
        try:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers=headers
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 401:
                print(f"   ✅ Token correctly invalidated!")
                print(f"   Error: {response.json()}")
            else:
                print(f"   ❌ SECURITY ISSUE: Invalidated token still works!")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("Authentication tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    print("Make sure the backend server is running on http://localhost:8000")
    print("Starting tests in 2 seconds...\n")
    asyncio.run(test_auth_flow())
