import { test, expect } from '@playwright/test';

/**
 * E2E Test: T097 - API Response Time
 *
 * This test verifies API endpoints meet performance targets:
 * - Target: p95 response time < 200ms
 * - Measures response times for auth and task endpoints
 */
test.describe('API Response Time Tests', () => {
  test('should have fast POST /api/auth/register response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `register-perf${timestamp}@example.com`;

    const startTime = Date.now();
    const response = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();

    // Target: Registration < 200ms
    console.log(`POST /api/auth/register: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast POST /api/auth/login response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `login-perf${timestamp}@example.com`;

    // First register a user
    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });

    // Now test login
    const startTime = Date.now();
    const response = await request.post('http://localhost:8000/api/auth/login', {
      data: {
        email,
        password: 'TestPassword123',
      },
    });
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();

    // Target: Login < 200ms
    console.log(`POST /api/auth/login: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast POST /api/auth/logout response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `logout-perf${timestamp}@example.com`;

    // Register and login
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Test logout
    const startTime = Date.now();
    const response = await request.post('http://localhost:8000/api/auth/logout', {
      headers: {
        Authorization: `Bearer ${registerData.accessToken}`,
      },
    });
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();

    // Target: Logout < 200ms
    console.log(`POST /api/auth/logout: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast GET /api/{user_id}/tasks response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `gettasks-perf${timestamp}@example.com`;

    // Register and login
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Create some tasks first
    for (let i = 0; i < 5; i++) {
      await request.post(`http://localhost:8000/api/${registerData.user.id}/tasks`, {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
        data: {
          title: `Task ${i}`,
          description: `Description ${i}`,
        },
      });
    }

    // Test GET tasks
    const startTime = Date.now();
    const response = await request.get(
      `http://localhost:8000/api/${registerData.user.id}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
      }
    );
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.tasks.length).toBe(5);

    // Target: GET tasks < 200ms (with 5 tasks)
    console.log(`GET /api/{user_id}/tasks (5 tasks): ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast POST /api/{user_id}/tasks response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `createtask-perf${timestamp}@example.com`;

    // Register and login
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Test create task
    const startTime = Date.now();
    const response = await request.post(
      `http://localhost:8000/api/${registerData.user.id}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
        data: {
          title: 'Performance Test Task',
          description: 'Testing API response time',
        },
      }
    );
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.title).toBe('Performance Test Task');

    // Target: Create task < 200ms
    console.log(`POST /api/{user_id}/tasks: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast PATCH /api/{user_id}/tasks/{id}/complete response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `complete-perf${timestamp}@example.com`;

    // Register and login
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Create a task
    const createResponse = await request.post(
      `http://localhost:8000/api/${registerData.user.id}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
        data: {
          title: 'Task to Complete',
        },
      }
    );
    const taskData = await createResponse.json();

    // Test toggle completion
    const startTime = Date.now();
    const response = await request.patch(
      `http://localhost:8000/api/${registerData.user.id}/tasks/${taskData.id}/complete`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
      }
    );
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.completed).toBe(true);

    // Target: Toggle completion < 200ms
    console.log(`PATCH /api/{user_id}/tasks/{id}/complete: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should have fast DELETE /api/{user_id}/tasks/{id} response time', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `delete-perf${timestamp}@example.com`;

    // Register and login
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Perf User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Create a task
    const createResponse = await request.post(
      `http://localhost:8000/api/${registerData.user.id}/tasks`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
        data: {
          title: 'Task to Delete',
        },
      }
    );
    const taskData = await createResponse.json();

    // Test delete task
    const startTime = Date.now();
    const response = await request.delete(
      `http://localhost:8000/api/${registerData.user.id}/tasks/${taskData.id}`,
      {
        headers: {
          Authorization: `Bearer ${registerData.accessToken}`,
        },
      }
    );
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    // Verify success
    expect(response.ok()).toBeTruthy();

    // Target: Delete task < 200ms
    console.log(`DELETE /api/{user_id}/tasks/{id}: ${responseTime}ms`);
    expect(responseTime).toBeLessThan(200);
  });

  test('should measure p95 response time for all endpoints', async ({ page, request }) => {
    const responseTimes: number[] = [];
    const numTests = 10;

    const timestamp = Date.now();
    const email = `p95-perf${timestamp}@example.com`;

    // Register
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'P95 User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Measure GET tasks response times
    for (let i = 0; i < numTests; i++) {
      const startTime = Date.now();
      const response = await request.get(
        `http://localhost:8000/api/${registerData.user.id}/tasks`,
        {
          headers: {
            Authorization: `Bearer ${registerData.accessToken}`,
          },
        }
      );
      const endTime = Date.now();
      responseTimes.push(endTime - startTime);
      expect(response.ok()).toBeTruthy();
    }

    // Calculate p95 (95th percentile)
    const sorted = responseTimes.sort((a, b) => a - b);
    const p95Index = Math.ceil(sorted.length * 0.95) - 1;
    const p95 = sorted[p95Index];

    console.log(`GET tasks response times (ms):`, responseTimes);
    console.log(`Average: ${responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length}ms`);
    console.log(`Min: ${sorted[0]}ms`);
    console.log(`Max: ${sorted[sorted.length - 1]}ms`);
    console.log(`P95: ${p95}ms`);

    // Target: P95 < 200ms
    expect(p95).toBeLessThan(200);
  });

  test('should handle concurrent requests efficiently', async ({ page, request }) => {
    const timestamp = Date.now();
    const email = `concurrent-perf${timestamp}@example.com`;

    // Register
    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Concurrent User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Make 10 concurrent requests
    const startTime = Date.now();
    const promises = Array(10).fill(null).map(async (_, i) => {
      return request.get(
        `http://localhost:8000/api/${registerData.user.id}/tasks`,
        {
          headers: {
            Authorization: `Bearer ${registerData.accessToken}`,
          },
        }
      );
    });

    const responses = await Promise.all(promises);
    const endTime = Date.now();
    const totalTime = endTime - startTime;

    // Verify all requests succeeded
    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
    }

    // With 10 concurrent requests, the total time should be less than sequential (10 * single_request_time)
    // Target: < 500ms for 10 concurrent requests
    console.log(`10 concurrent GET requests completed in: ${totalTime}ms`);
    console.log(`Average per request: ${totalTime / 10}ms`);
    expect(totalTime).toBeLessThan(500);
  });
});
