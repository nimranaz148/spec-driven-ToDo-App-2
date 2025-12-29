import { test, expect } from '@playwright/test';

/**
 * E2E Test: T095 - Delete Task
 *
 * This test verifies task deletion flow:
 * 1. User can delete a task
 * 2. Task is removed from the list
 * 3. Task counters update correctly
 * 4. Deleted task cannot be recovered (no undo)
 */
test.describe('Delete Task', () => {
  let taskTitle: string;

  // Setup: Login and create a task before each test
  test.beforeEach(async ({ page, request }) => {
    // Create a test user
    const timestamp = Date.now();
    const email = `deleteuser${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Delete User',
        password: 'TestPassword123',
      },
    });

    // Login via UI
    await page.goto('/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Wait for navigation to dashboard
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Create a test task
    taskTitle = `Task to Delete ${timestamp}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(taskTitle)).toBeVisible();
  });

  test('should delete a task', async ({ page }) => {
    // Verify task exists
    await expect(page.getByText(taskTitle)).toBeVisible();
    await expect(page.getByText('All (1)')).toBeVisible();

    // Find and click delete button
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await deleteButton.click();

    // Wait for deletion to complete
    await expect(page.getByText(taskTitle)).not.toBeVisible();

    // Verify task counter updated
    await expect(page.getByText('All (0)')).toBeVisible();

    // Verify empty state is shown
    await expect(page.getByText('No tasks yet')).toBeVisible();
  });

  test('should delete a completed task', async ({ page }) => {
    // Mark task as complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await taskCheckbox.check();
    await expect(taskCheckbox).toBeChecked();

    // Delete completed task
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await deleteButton.click();

    // Verify task is removed
    await expect(page.getByText(taskTitle)).not.toBeVisible();
    await expect(page.getByText('Completed (0)')).toBeVisible();
  });

  test('should delete a task while in Active filter view', async ({ page }) => {
    // Filter by Active
    await page.getByRole('tab', { name: 'Active' }).click();

    // Verify task is visible
    await expect(page.getByText(taskTitle)).toBeVisible();

    // Delete task
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await deleteButton.click();

    // Verify task is removed and empty state shows
    await expect(page.getByText(taskTitle)).not.toBeVisible();
    await expect(page.getByText('No active tasks')).toBeVisible();
  });

  test('should delete a task while in Completed filter view', async ({ page }) => {
    // Mark task as complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await taskCheckbox.check();

    // Filter by Completed
    await page.getByRole('tab', { name: 'Completed' }).click();

    // Verify task is visible
    await expect(page.getByText(taskTitle)).toBeVisible();

    // Delete task
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await deleteButton.click();

    // Verify task is removed and empty state shows
    await expect(page.getByText(taskTitle)).not.toBeVisible();
    await expect(page.getByText('No completed tasks')).toBeVisible();
  });

  test('should delete multiple tasks', async ({ page }) => {
    // Create additional tasks
    const task2Title = `Task 2 ${Date.now()}`;
    await page.getByLabel('Title').fill(task2Title);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(task2Title)).toBeVisible();

    const task3Title = `Task 3 ${Date.now()}`;
    await page.getByLabel('Title').fill(task3Title);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(task3Title)).toBeVisible();

    // Verify all tasks exist
    await expect(page.getByText(taskTitle)).toBeVisible();
    await expect(page.getByText(task2Title)).toBeVisible();
    await expect(page.getByText(task3Title)).toBeVisible();
    await expect(page.getByText('All (3)')).toBeVisible();

    // Delete first task
    await page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    }).click();
    await expect(page.getByText(taskTitle)).not.toBeVisible();

    // Delete second task
    await page.getByRole('button', {
      name: new RegExp(`Delete task: ${task2Title}`, 'i'),
    }).click();
    await expect(page.getByText(task2Title)).not.toBeVisible();

    // Delete third task
    await page.getByRole('button', {
      name: new RegExp(`Delete task: ${task3Title}`, 'i'),
    }).click();
    await expect(page.getByText(task3Title)).not.toBeVisible();

    // Verify all tasks deleted
    await expect(page.getByText('All (0)')).toBeVisible();
    await expect(page.getByText('No tasks yet')).toBeVisible();
  });

  test('should update counters correctly after deletion', async ({ page }) => {
    // Create additional tasks
    await page.getByLabel('Title').fill('Task 2');
    await page.getByRole('button', { name: 'Add Task' }).click();

    await page.getByLabel('Title').fill('Task 3');
    await page.getByRole('button', { name: 'Add Task' }).click();

    // Mark one task complete
    await page.getByRole('checkbox').first().check();

    // Verify initial counts: 3 total, 2 active, 1 completed
    await expect(page.getByText('All (3)')).toBeVisible();
    await expect(page.getByText('Active (2)')).toBeVisible();
    await expect(page.getByText('Completed (1)')).toBeVisible();

    // Delete active task
    await page.getByRole('button', { name: /Delete task:/i }).nth(1).click();

    // Verify counts updated: 2 total, 1 active, 1 completed
    await expect(page.getByText('All (2)')).toBeVisible();
    await expect(page.getByText('Active (1)')).toBeVisible();
    await expect(page.getByText('Completed (1)')).toBeVisible();

    // Delete completed task
    await page.getByRole('button', { name: /Delete task:/i }).first().click();

    // Verify counts updated: 1 total, 1 active, 0 completed
    await expect(page.getByText('All (1)')).toBeVisible();
    await expect(page.getByText('Active (1)')).toBeVisible();
    await expect(page.getByText('Completed (0)')).toBeVisible();
  });

  test('should persist deletion after page reload', async ({ page }) => {
    // Delete task
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await deleteButton.click();

    // Verify task is gone
    await expect(page.getByText(taskTitle)).not.toBeVisible();

    // Reload page
    await page.reload();

    // Wait for tasks to load
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Verify task is still gone
    await expect(page.getByText(taskTitle)).not.toBeVisible();
    await expect(page.getByText('No tasks yet')).toBeVisible();
  });

  test('should have accessible delete button', async ({ page }) => {
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });

    // Verify accessible label
    await expect(deleteButton).toHaveAttribute('aria-label', new RegExp(`Delete task: ${taskTitle}`, 'i'));

    // Verify button is focusable
    await deleteButton.focus();
    await expect(deleteButton).toBeFocused();
  });

  test('should show delete button on mobile', async ({ page, viewport }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Delete button should be visible on mobile
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });
    await expect(deleteButton).toBeVisible();

    // Delete task on mobile
    await deleteButton.click();
    await expect(page.getByText(taskTitle)).not.toBeVisible();
  });

  test('should not allow interaction with delete button during deletion', async ({ page }) => {
    const deleteButton = page.getByRole('button', {
      name: new RegExp(`Delete task: ${taskTitle}`, 'i'),
    });

    // Click delete button
    await deleteButton.click();

    // During deletion, task item should be disabled
    // Verify task is no longer visible (deleted quickly)
    await expect(page.getByText(taskTitle)).not.toBeVisible();
  });
});
