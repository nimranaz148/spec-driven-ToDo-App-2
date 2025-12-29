import { test, expect } from '@playwright/test';

/**
 * E2E Test: T094 - Complete Task
 *
 * This test verifies task completion toggle flow:
 * 1. User can mark a task as complete
 * 2. Visual feedback is shown (strikethrough, muted)
 * 3. Task counters update correctly
 * 4. User can unmark a task (toggle back)
 * 5. Filter tabs work correctly
 */
test.describe('Complete Task', () => {
  let taskTitle: string;

  // Setup: Login and create a task before each test
  test.beforeEach(async ({ page, request }) => {
    // Create a test user
    const timestamp = Date.now();
    const email = `completeuser${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Complete User',
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
    taskTitle = `Task to Complete ${timestamp}`;
    await page.getByLabel('Title').fill(taskTitle);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(taskTitle)).toBeVisible();
  });

  test('should mark task as complete', async ({ page }) => {
    // Find the task's checkbox and click it
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await expect(taskCheckbox).toBeVisible();
    await expect(taskCheckbox).not.toBeChecked();

    // Check the checkbox to mark task complete
    await taskCheckbox.check();

    // Verify checkbox is checked
    await expect(taskCheckbox).toBeChecked();

    // Verify visual changes - task title should have strikethrough
    const taskTitleElement = page.getByText(taskTitle);
    await expect(taskTitleElement).toHaveCSS('text-decoration-line', 'line-through');

    // Verify task card has muted background
    const taskCard = taskTitleElement.locator('..').locator('..').locator('..');
    await expect(taskCard).toHaveClass(/bg-muted/);

    // Verify task counter for active tasks decreased
    await expect(page.getByText('Active (0)')).toBeVisible();
    await expect(page.getByText('Completed (1)')).toBeVisible();
  });

  test('should unmark task as complete', async ({ page }) => {
    // First mark task as complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await taskCheckbox.check();
    await expect(taskCheckbox).toBeChecked();

    // Uncheck the task
    await taskCheckbox.uncheck();

    // Verify checkbox is unchecked
    await expect(taskCheckbox).not.toBeChecked();

    // Verify visual changes reverted
    const taskTitleElement = page.getByText(taskTitle);
    await expect(taskTitleElement).not.toHaveCSS('text-decoration-line', 'line-through');

    // Verify task counter for active tasks increased
    await expect(page.getByText('Active (1)')).toBeVisible();
    await expect(page.getByText('Completed (0)')).toBeVisible();
  });

  test('should toggle task completion multiple times', async ({ page }) => {
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });

    // Toggle 1: Mark complete
    await taskCheckbox.check();
    await expect(taskCheckbox).toBeChecked();
    await expect(page.getByText('Completed (1)')).toBeVisible();

    // Toggle 2: Unmark
    await taskCheckbox.uncheck();
    await expect(taskCheckbox).not.toBeChecked();
    await expect(page.getByText('Active (1)')).toBeVisible();

    // Toggle 3: Mark complete again
    await taskCheckbox.check();
    await expect(taskCheckbox).toBeChecked();
    await expect(page.getByText('Completed (1)')).toBeVisible();
  });

  test('should show correct accessible labels on checkbox', async ({ page }) => {
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });

    // Verify initial label
    await expect(taskCheckbox).toHaveAttribute('aria-label', 'Mark task as complete');

    // Mark complete
    await taskCheckbox.check();

    // Verify label changed
    const completedCheckbox = page.getByRole('checkbox', { name: /Mark task as incomplete/i });
    await expect(completedCheckbox).toHaveAttribute('aria-label', 'Mark task as incomplete');
  });

  test('should filter tasks by completion status', async ({ page }) => {
    // Create another task
    const task2Title = `Second Task ${Date.now()}`;
    await page.getByLabel('Title').fill(task2Title);
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText(task2Title)).toBeVisible();

    // Mark first task as complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i }).first();
    await taskCheckbox.check();

    // Filter by All - should show both tasks
    await page.getByRole('tab', { name: 'All' }).click();
    await expect(page.getByText(taskTitle)).toBeVisible();
    await expect(page.getByText(task2Title)).toBeVisible();

    // Filter by Active - should show only incomplete task
    await page.getByRole('tab', { name: 'Active' }).click();
    await expect(page.getByText(taskTitle)).not.toBeVisible();
    await expect(page.getByText(task2Title)).toBeVisible();

    // Filter by Completed - should show only complete task
    await page.getByRole('tab', { name: 'Completed' }).click();
    await expect(page.getByText(taskTitle)).toBeVisible();
    await expect(page.getByText(task2Title)).not.toBeVisible();
  });

  test('should update task counts correctly when toggling', async ({ page }) => {
    // Create additional tasks
    await page.getByLabel('Title').fill('Task 2');
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText('Task 2')).toBeVisible();

    await page.getByLabel('Title').fill('Task 3');
    await page.getByRole('button', { name: 'Add Task' }).click();
    await expect(page.getByText('Task 3')).toBeVisible();

    // Verify initial counts: 3 total, 3 active, 0 completed
    await expect(page.getByText('All (3)')).toBeVisible();
    await expect(page.getByText('Active (3)')).toBeVisible();
    await expect(page.getByText('Completed (0)')).toBeVisible();

    // Mark one task complete
    await page.getByRole('checkbox').first().check();

    // Verify counts updated: 3 total, 2 active, 1 completed
    await expect(page.getByText('All (3)')).toBeVisible();
    await expect(page.getByText('Active (2)')).toBeVisible();
    await expect(page.getByText('Completed (1)')).toBeVisible();

    // Mark another task complete
    await page.getByRole('checkbox').nth(1).check();

    // Verify counts updated: 3 total, 1 active, 2 completed
    await expect(page.getByText('All (3)')).toBeVisible();
    await expect(page.getByText('Active (1)')).toBeVisible();
    await expect(page.getByText('Completed (2)')).toBeVisible();

    // Unmark first task
    await page.getByRole('checkbox').first().uncheck();

    // Verify counts updated: 3 total, 2 active, 1 completed
    await expect(page.getByText('All (3)')).toBeVisible();
    await expect(page.getByText('Active (2)')).toBeVisible();
    await expect(page.getByText('Completed (1)')).toBeVisible();
  });

  test('should persist completion status after page reload', async ({ page }) => {
    // Mark task as complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await taskCheckbox.check();
    await expect(taskCheckbox).toBeChecked();

    // Reload page
    await page.reload();

    // Wait for tasks to load
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Verify task is still marked as complete
    const reloadedCheckbox = page.getByRole('checkbox', { name: /Mark task as incomplete/i });
    await expect(reloadedCheckbox).toBeChecked();
    await expect(page.getByText(taskTitle)).toHaveCSS('text-decoration-line', 'line-through');
  });

  test('should show empty state in Completed tab when no tasks completed', async ({ page }) => {
    // Click on Completed tab
    await page.getByRole('tab', { name: 'Completed' }).click();

    // Verify empty state message
    await expect(page.getByText('No completed tasks')).toBeVisible();
    await expect(page.getByText('Complete a task to see it here')).toBeVisible();
  });

  test('should show empty state in Active tab when all tasks completed', async ({ page }) => {
    // Mark all tasks complete
    const taskCheckbox = page.getByRole('checkbox', { name: /Mark task as complete/i });
    await taskCheckbox.check();

    // Click on Active tab
    await page.getByRole('tab', { name: 'Active' }).click();

    // Verify empty state message
    await expect(page.getByText('No active tasks')).toBeVisible();
    await expect(page.getByText('All tasks are completed!')).toBeVisible();
  });
});
