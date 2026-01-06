"""E2E tests for chat history persistence across reloads."""

import { test, expect } from '@playwright/test'

test.describe('Chat History Persistence', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('chat history persists across page reload', async ({ page }) => {
    // Navigate to chat
    await page.goto('/dashboard/chat')
    
    // Send a message
    const messageInput = page.locator('[data-testid="chat-input"]')
    await messageInput.fill('Add a task to buy groceries')
    await page.click('[data-testid="send-button"]')
    
    // Wait for response
    await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible()
    
    // Send another message
    await messageInput.fill('What tasks do I have?')
    await page.click('[data-testid="send-button"]')
    await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible()
    
    // Verify we have messages before reload
    const messagesBefore = await page.locator('[data-testid="chat-message"]').count()
    expect(messagesBefore).toBeGreaterThan(2)
    
    // Reload the page
    await page.reload()
    
    // Wait for chat to load
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible()
    
    // Verify messages are still there
    const messagesAfter = await page.locator('[data-testid="chat-message"]').count()
    expect(messagesAfter).toBe(messagesBefore)
    
    // Verify specific message content is preserved
    await expect(page.locator('text=Add a task to buy groceries')).toBeVisible()
    await expect(page.locator('text=What tasks do I have?')).toBeVisible()
  })

  test('chat history shows correct chronological order', async ({ page }) => {
    await page.goto('/dashboard/chat')
    
    // Send multiple messages in sequence
    const messages = [
      'First message',
      'Second message', 
      'Third message'
    ]
    
    for (const message of messages) {
      await page.fill('[data-testid="chat-input"]', message)
      await page.click('[data-testid="send-button"]')
      await page.waitForTimeout(1000) // Ensure order
    }
    
    // Reload page
    await page.reload()
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible()
    
    // Verify messages appear in correct order
    const messageElements = page.locator('[data-testid="user-message"]')
    await expect(messageElements.nth(0)).toContainText('First message')
    await expect(messageElements.nth(1)).toContainText('Second message')
    await expect(messageElements.nth(2)).toContainText('Third message')
  })

  test('chat references previous context correctly', async ({ page }) => {
    await page.goto('/dashboard/chat')
    
    // Create a task first
    await page.fill('[data-testid="chat-input"]', 'Add a task called "Important Meeting"')
    await page.click('[data-testid="send-button"]')
    await expect(page.locator('[data-testid="assistant-message"]').last()).toBeVisible()
    
    // Reload page
    await page.reload()
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible()
    
    // Reference the previous task
    await page.fill('[data-testid="chat-input"]', 'Mark that task as complete')
    await page.click('[data-testid="send-button"]')
    
    // Should understand "that task" refers to "Important Meeting"
    await expect(page.locator('[data-testid="assistant-message"]').last()).toContainText(/completed|marked|done/i)
  })
})
