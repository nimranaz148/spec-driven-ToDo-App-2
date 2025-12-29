import { test, expect } from '@playwright/test';

/**
 * E2E Test: T092 - Login/Logout Flow
 *
 * This test verifies the complete authentication flow:
 * 1. User can login with valid credentials
 * 2. User is redirected to dashboard after login
 * 3. User can logout
 * 4. User is redirected to login page after logout
 * 5. JWT token is cleared
 */
test.describe('Login/Logout Flow', () => {
  // Setup: Create a test user before tests run
  test.beforeEach(async ({ page, request }) => {
    // This assumes the backend is running at localhost:8000
    // Create a test user via API
    const timestamp = Date.now();
    const email = `loginuser${timestamp}@example.com`;

    await request.post('http://localhost:8000/api/auth/register', {
      data: {
        email,
        name: 'Login User',
        password: 'TestPassword123',
      },
    });

    // Store email in test context for use in tests
    test.info().annotations.push({ type: 'email', description: email });
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    const email = test.info().annotations.find(a => a.type === 'email')?.description;

    await page.goto('/login');
    await expect(page).toHaveTitle(/Welcome back/);

    // Fill in login form
    await page.getByLabel('Email').fill(email!);
    await page.getByLabel('Password').fill('TestPassword123');

    // Submit form
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify redirect to dashboard
    await expect(page).toHaveURL(/\/$/);
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Verify user is logged in
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
    await expect(page.getByText('Login User')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    // Fill in with wrong password
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('WrongPassword');

    // Submit form
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify error message is shown
    await expect(page.locator('text=/login failed|invalid credentials/i')).toBeVisible();

    // Verify still on login page
    await expect(page).toHaveURL(/\/login/);
  });

  test('should validate required fields on login', async ({ page }) => {
    await page.goto('/login');

    // Submit form without filling fields
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify validation errors
    await expect(page.getByText('Invalid email address')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });

  test('should successfully logout', async ({ page }) => {
    const email = test.info().annotations.find(a => a.type === 'email')?.description;

    // First login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email!);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify logged in
    await expect(page.getByRole('heading', { name: 'My Tasks' })).toBeVisible();

    // Click logout button
    await page.getByRole('button', { name: 'Logout' }).click();

    // Verify redirect to login page
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();

    // Verify logout button is not visible
    await expect(page.getByRole('button', { name: 'Logout' })).not.toBeVisible();

    // Try to access protected route - should redirect to login
    await page.goto('/');
    await expect(page).toHaveURL(/\/login/);
  });

  test('should show link to signup page', async ({ page }) => {
    await page.goto('/login');

    // Verify signup link is present
    const signupLink = page.getByRole('link', { name: /Sign up/i });
    await expect(signupLink).toBeVisible();

    // Click link and verify navigation
    await signupLink.click();
    await expect(page).toHaveURL(/\/signup/);
    await expect(page.getByRole('heading', { name: /Create an account/i })).toBeVisible();
  });

  test('should maintain session across navigation', async ({ page }) => {
    const email = test.info().annotations.find(a => a.type === 'email')?.description;

    // Login
    await page.goto('/login');
    await page.getByLabel('Email').fill(email!);
    await page.getByLabel('Password').fill('TestPassword123');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify logged in
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();

    // Navigate to different routes and verify user stays logged in
    await page.goto('/');
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();

    await page.reload();
    await expect(page.getByRole('button', { name: 'Logout' })).toBeVisible();
  });
});
