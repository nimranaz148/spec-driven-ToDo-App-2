import { test, expect } from '@playwright/test';

/**
 * E2E Test: T093 - Create Task
 *
 * This test verifies the task creation flow:
 * 1. User can access task creation form
 * 2. User can create a task with title
 * 3. User can create a task with title and description
 * 4. Task appears in the task list after creation
 * 5. Task counter updates
 */
test.describe('Create Task', () => {
  // Setup: Login before each test
  test.beforeEach(async ({ page, request }) => {
    // Create a test user
    const timestamp = Date.now();
    const email = `taskuser${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Task User',
        password: 'TestPassword123',
      },
    });

    test.info().annotations.push({ type: 'email', description: email });

    // Login via UI
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Wait for navigation to dashboard
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();
  });

  test('should create a new task with title only', async ({ page }) => {
    // Verify empty state
    await expect(page.getByText('No tasks yet')).toBeVisible();

    // Create a task
    const taskTitle = `Test Task ${Date.now()}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Wait for task to appear
    await expect(page.getByText(taskTitle)).toBeVisible();

    // Verify empty state is gone
    await expect(page.getByText('No tasks yet')).not.toBeVisible();

    // Verify task counter updated
    const taskCounter = page.getByText(/All \(\d+\)/);
    await expect(taskCounter).toBeVisible();
    await expect(taskCounter).toContainText('All (1)');
  });

  test('should create a new task with title and description', async ({ page }) => {
    const taskTitle = `Detailed Task ${Date.now()}`;
    const taskDescription = 'This is a detailed description for the task';

    // Create task with description
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByLabel('Description (optional)').fill(taskDescription);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Verify task appears with title and description
    await expect(page.getByText(taskTitle)).toBeVisible();
    await expect(page.getByText(taskDescription)).toBeVisible();
  });

  test('should validate required title field', async ({ page }) => {
    // Try to create task without title
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Verify validation error
    await expect(page.getByText('Title is required')).toBeVisible();

    // Verify no task was created
    await expect(page.getByText('No tasks yet')).toBeVisible();
  });

  test('should clear form after successful task creation', async ({ page }) => {
    // Create a task
    const taskTitle = `Test Task ${Date.now()}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Wait for task to be created
    await expect(page.getByText(taskTitle)).toBeVisible();

    // Verify form is cleared
    await expect(page.getByLabel('Title')).toHaveValue('');
    await expect(page.getByLabel('Description (optional)')).toHaveValue('');
  });

  test('should show loading state while creating task', async ({ page }) => {
    // Start creating a task
    const taskTitle = `Loading Test ${Date.now()}`;
    await page.getByLabel('Title').fill(taskTitle);

    // Click button and check for loading state
    const addButton = page.getByRole('button', { name: 'Add Task' });
    await addButton.click();

    // Verify button shows loading state
    await expect(addButton).toHaveText(/Adding.../);
    await expect(addButton).toBeDisabled();

    // Wait for completion
    await expect(page.getByText(taskTitle)).toBeVisible();

    // Verify button returns to normal state
    await expect(addButton).toHaveText('Add Task');
    await expect(addButton).toBeEnabled();
  });

  test('should create multiple tasks sequentially', async ({ page }) => {
    // Create first task
    const task1Title = `First Task ${Date.now()}`;
    await page.getByLabel('Title').fill(task1Title);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(task1Title)).toBeVisible();

    // Create second task
    const task2Title = `Second Task ${Date.now()}`;
    await page.getByLabel('Title').fill(task2Title);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(task2Title)).toBeVisible();

    // Verify both tasks are visible
    await expect(page.getByText(task1Title)).toBeVisible();
    await expect(page.getByText(task2Title)).toBeVisible();

    // Verify task counter shows 2 tasks
    await expect(page.getByText('All (2)')).toBeVisible();
  });

  test('should handle long task titles', async ({ page }) => {
    // Create a task with a long title (200 chars max)
    const longTitle = 'A'.repeat(200);
    await page.getByLabel('Title').fill(longTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Verify task was created
    await expect(page.getByText(longTitle)).toBeVisible();
  });

  test('should validate maximum title length', async ({ page }) => {
    // Try to create a task with title exceeding 200 characters
    const tooLongTitle = 'A'.repeat(201);
    await page.getByLabel('Title').fill(tooLongTitle);

    // Trigger validation by blurring the field
    await page.getByLabel('Description (optional)').click();

    // Verify validation error
    await expect(page.getByText('Title must be 200 characters or less')).toBeVisible();

    // Verify task was not created
    await expect(page.getByText('No tasks yet')).toBeVisible();
  });

  test('should validate maximum description length', async ({ page }) => {
    // Try to create a task with description exceeding 1000 characters
    await page.getByLabel('Title').fill('Test Task');
    const tooLongDescription = 'B'.repeat(1001);
    await page.getByLabel('Description (optional)').fill(tooLongDescription);

    // Trigger validation by blurring the field
    await page.getByLabel('Title').click();

    // Verify validation error
    await expect(page.getByText('Description must be 1000 characters or less')).toBeVisible();

    // Verify task was not created
    await expect(page.getByRole('button', { name: 'Add Task' })).not.toBeDisabled();
  });
});
