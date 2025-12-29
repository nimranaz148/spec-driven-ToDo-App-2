import { test, expect } from '@playwright/test';

/**
 * E2E Test: T091 - User Registration Flow
 *
 * This test verifies the complete user registration flow:
 * 1. Navigate to signup page
 * 2. Fill out the registration form with valid credentials
 * 3. Submit the form
 * 4. Verify successful registration and redirect to dashboard
 * 5. Verify the user is authenticated
 */
test.describe('User Registration Flow', () => {
  test('should successfully register a new user', async ({ page }) => {
    // Generate unique email to avoid conflicts
    const timestamp = Date.now();
    const email = `testuser${timestamp}@example.com`;

    // Navigate to signup page
    await page.goto('/signup');
    await expect(page).toHaveTitle(/Create an account/);

    // Fill out the registration form
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill('TestPassword123');

    // Submit the form
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify redirect to dashboard (home page)
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Verify the user is logged in by checking for logout button
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();

    // Verify user name is displayed in header
    await expect(page.getByText('Test User')).toBeVisible();
  });

  test('should validate required fields on registration', async ({ page }) => {
    await page.goto('/signup');

    // Submit form without filling any fields
    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify validation errors
    await expect(page.getByText('Name is required')).toBeVisible();
    await expect(page.getByText('Invalid email address')).toBeVisible();
    await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();
  });

  test('should validate password minimum length', async ({ page }) => {
    await page.goto('/signup');

    // Fill form with short password
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('short');

    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify password validation
    await expect(page.getByText('Password must be at least 8 characters')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/signup');

    // Fill form with invalid email
    await page.getByLabel('Name').fill('Test User');
    await page.getByLabel('Email').fill('invalid-email');
    await page.getByLabel('Password').fill('TestPassword123');

    await page.getByRole('button', { name: 'Create Account' }).click();

    // Verify email validation
    await expect(page.getByText('Invalid email address')).toBeVisible();
  });

  test('should show link to login page', async ({ page }) => {
    await page.goto('/signup');

    // Verify login link is present
    const loginLink = page.getByRole('link', { name: /Sign in/i });
    await expect(loginLink).toBeVisible();

    // Click link and verify navigation
    await loginLink.click();
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /Welcome back/i })).toBeVisible();
  });
});
