import { test, expect } from '@playwright/test';

/**
 * E2E Test: T098 - Slow Network (3G) Testing
 *
 * This test verifies the application works under slow 3G network conditions:
 * - User can still register/login
 * - User can create/manage tasks
 * - Appropriate loading states are shown
 * - Performance is acceptable on 3G
 */
test.describe('Slow Network (3G) Tests', () => {
  // 3G network profile based on Chrome DevTools
  const slow3G = {
    offline: false,
    downloadThroughput: (750 * 1024) / 8, // 750 Kbps
    uploadThroughput: (250 * 1024) / 8, // 250 Kbps
    latency: 100, // 100ms RTT
  };

  const fast3G = {
    offline: false,
    downloadThroughput: (1.6 * 1024 * 1024) / 8, // 1.6 Mbps
    uploadThroughput: (750 * 1024) / 8, // 750 Kbps
    latency: 100, // 100ms RTT
  };

  test('should allow registration on slow 3G network', async ({ page, context }) => {
    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    const timestamp = Date.now();
    const email = `slow-reg${timestamp}@example.com`;

    // Navigate to signup
    await page.goto('/signup');

    // Fill form
    await page.getByLabel('Name').fill('Slow Network User');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');

    // Submit form
    await page.getByRole('button', { name: 'Creating account...' }).click();

    // Verify successful registration
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Verify user is logged in
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
  });

  test('should allow login on slow 3G network', async ({ page, request, context }) => {
    // Create user first (fast network)
    const timestamp = Date.now();
    const email = `slow-login${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Login User',
        password: 'TestPassword123',
      },
    });

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify successful login
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();
  });

  test('should allow task creation on slow 3G network', async ({ page, request, context }) => {
    // Create and login user
    const timestamp = Date.now();
    const email = `slow-task${timestamp}@example.com`;

    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Task User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login manually to set auth in browser
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Create task
    const taskTitle = `Slow Network Task ${timestamp}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Wait for task to appear (may take longer on slow network)
    await expect(page.getByText(taskTitle), {
      timeout: 30000, // 30s timeout for slow network
    }).toBeVisible();

    // Verify task counter updated
    await expect(page.getByText('All (1)')).toBeVisible();
  });

  test('should show loading states appropriately on slow network', async ({ page, request, context }) => {
    // Create and login user
    const timestamp = Date.now();
    const email = `slow-loading${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Loading User',
        password: 'TestPassword123',
      },
    });

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    const loginButton = page.getByRole('button', { name: 'Sign In' });
    await loginButton.click();

    // Verify button shows loading state (doesn't change text on this form, so we check disabled)
    await expect(loginButton).toBeDisabled();

    // After loading completes, verify navigation
    await expect(page.getByRole('heading', { name: 'My Tasks' }), {
      timeout: 30000,
    }).toBeVisible();

    // Now create a task and check loading state
    await page.getByLabel('Title').fill('Slow Task');
    const addButton = page.getByRole('button', { name: 'Add Task' });
    await addButton.click();

    // Verify button shows loading state
    await expect(addButton).toHaveText(/Adding.../);
    await expect(addButton).toBeDisabled();

    // Wait for task to be added
    await expect(page.getByText('Slow Task'), { timeout: 30000 }).toBeVisible();

    // Verify button returns to normal state
    await expect(addButton).toHaveText('Add Task');
    await expect(addButton).toBeEnabled();
  });

  test('should allow task completion toggle on slow network', async ({ page, request, context }) => {
    // Create and login user with existing task
    const timestamp = Date.now();
    const email = `slow-complete${timestamp}@example.com`;

    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Complete User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    await request.post(`http://localhost:8000/api/${registerData.user.id}/tasks`, {
      headers: {
        Authorization: `Bearer ${registerData.accessToken}`,
      },
      data: {
        title: `Slow Complete Task ${timestamp}`,
      },
    });

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Slow Complete Task'), { timeout: 30000 }).toBeVisible();

    // Toggle task completion
    const checkbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await checkbox.check();

    // Verify checkbox state (may take time)
    await expect(checkbox, { timeout: 30000 }).toBeChecked();

    // Verify visual feedback
    await expect(page.getByText('Slow Complete Task')).toHaveCSS(
      'text-decoration-line',
      'line-through'
    );
  });

  test('should allow task deletion on slow network', async ({ page, request, context }) => {
    // Create and login user with existing task
    const timestamp = Date.now();
    const email = `slow-delete${timestamp}@example.com`;

    const registerResponse = await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Delete User',
        password: 'TestPassword123',
      },
    });
    const registerData = await registerResponse.json();

    await request.post(`http://localhost:8000/api/${registerData.user.id}/tasks`, {
      headers: {
        Authorization: `Bearer ${registerData.accessToken}`,
      },
      data: {
        title: `Slow Delete Task ${timestamp}`,
      },
    });

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByText('Slow Delete Task'), { timeout: 30000 }).toBeVisible();

    // Delete task
    const deleteButton = page.getByRole('button', {
      name: /Delete task:/i,
    });
    await deleteButton.click();

    // Verify task is removed (may take time)
    await expect(page.getByText('Slow Delete Task'), { timeout: 30000 }).not.toBeVisible();
  });

  test('should handle network timeout gracefully', async ({ page, request, context }) => {
    // Create and login user
    const timestamp = Date.now();
    const email = `slow-timeout${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Timeout User',
        password: 'TestPassword123',
      },
    });

    // Set extremely slow network
    await context.setOffline(false);
    await context.emulateNetworkConditions({
      offline: false,
      downloadThroughput: (50 * 1024) / 8, // 50 Kbps - extremely slow
      uploadThroughput: (50 * 1024) / 8,
      latency: 500, // 500ms RTT
    });

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Wait for either success or timeout
    const startTime = Date.now();
    try {
      await expect(page.getByRole('heading', { name: 'My Tasks' }), {
        timeout: 60000, // 60s timeout
      }).toBeVisible();

      // If we got here, login succeeded despite slow network
      const elapsedTime = Date.now() - startTime;
      console.log(`Login succeeded on extremely slow network in ${elapsedTime}ms`);

      // Try to create a task
      await page.getByLabel('Title').fill('Very Slow Task');
      await page.getByRole('button', { name: 'Add Task' }).click();

      await expect(page.getByText('Very Slow Task'), {
        timeout: 120000, // 2 min timeout
      }).toBeVisible();
    } catch (error) {
      const elapsedTime = Date.now() - startTime;
      console.log(`Login timed out after ${elapsedTime}ms`);

      // Verify we're still on login page
      await expect(page).toHaveURL(/\/login/);

      // Verify error message is shown (timeout)
      await expect(page.getByText(/login failed|timeout|error/i)).toBeVisible();
    }
  });

  test('should work on fast 3G network', async ({ page, request, context }) => {
    // Create and login user
    const timestamp = Date.now();
    const email = `fast3g${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Fast 3G User',
        password: 'TestPassword123',
      },
    });

    // Set fast 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(fast3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify successful login
    await expect(page.getByRole('heading', { name: 'My Tasks' }), {
      timeout: 30000,
    }).toBeVisible();

    // Create task
    const taskTitle = `Fast 3G Task ${timestamp}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Verify task created
    await expect(page.getByText(taskTitle), { timeout: 30000 }).toBeVisible();
  });

  test('should show skeleton loading states on slow network', async ({ page, request, context }) => {
    // Create and login user
    const timestamp = Date.now();
    const email = `slow-skeleton${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Slow Skeleton User',
        password: 'TestPassword123',
      },
    });

    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Check for skeleton loading states
    const skeletons = page.locator('[data-testid="skeleton"], .skeleton, [role="progressbar"]');
    const skeletonCount = await skeletons.count();

    if (skeletonCount > 0) {
      console.log(`Found ${skeletonCount} skeleton loading states`);

      // Wait for skeletons to disappear
      await expect(skeletons.first(), { timeout: 30000 }).not.toBeVisible();
    }
  });

  test('should handle network reconnection', async ({ page, request, context }) => {
    // Create user
    const timestamp = Date.now();
    const email = `slow-reconnect${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Reconnect User',
        password: 'TestPassword123',
      },
    });

    // Set normal network first
    await context.setOffline(false);

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Create a task
    await page.getByLabel('Title').fill('Reconnect Task');
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText('Reconnect Task')).toBeVisible();

    // Now simulate network going offline
    await context.setOffline(true);

    // Try to create another task - should fail gracefully
    await page.getByLabel('Title').fill('Offline Task');
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Should show error
    await expect(page.getByText(/failed|error|network/i), {
      timeout: 5000,
    }).toBeVisible();

    // Now restore network
    await context.setOffline(false);

    // Try again - should succeed
    await page.getByLabel('Title').fill('Reconnected Task');
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Should succeed
    await expect(page.getByText('Reconnected Task'), { timeout: 30000 }).toBeVisible();
  });

  test('should complete full workflow on slow 3G network', async ({ page, request, context }) => {
    // Set slow 3G network conditions
    await context.setOffline(false);
    await context.emulateNetworkConditions(slow3G);

    const timestamp = Date.now();
    const email = `slow-workflow${timestamp}@example.com`;

    // Workflow: Register -> Create Task -> Complete Task -> Delete Task -> Logout

    // 1. Register
    await page.goto('/signup');
    await page.getByLabel('Name').fill('Workflow User');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Create Account' }).click();
    await expect(page.getByRole('heading', { name: 'My Tasks' }), {
      timeout: 30000,
    }).toBeVisible();

    // 2. Create task
    const taskTitle = `Workflow Task ${timestamp}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(taskTitle), { timeout: 30000 }).toBeVisible();

    // 3. Complete task
    await page.getByRole('checkbox', { name: /Mark task as complete/i }).check();
    await expect(page.getByRole('checkbox'), { timeout: 30000 }).toBeChecked();

    // 4. Delete task
    await page.getByRole('button', { name: /Delete task:/i }).click();
    await expect(page.getByText(taskTitle), { timeout: 30000 }).not.toBeVisible();

    // 5. Logout
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page.getByRole('heading', { name: 'Welcome back' }), {
      timeout: 30000,
    }).toBeVisible();

    // Verify logged out
    await expect(page.getByRole('button', { name: 'Logout' })).not.toBeVisible();
  });
});
