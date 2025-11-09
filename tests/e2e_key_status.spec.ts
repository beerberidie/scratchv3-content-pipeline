/**
 * E2E tests for API key status management
 */
import { test, expect } from '@playwright/test';

test.describe('API Key Status Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page.locator('header .logo')).toBeVisible();
    
    // Open settings modal
    await page.click('.settings-btn');
    await expect(page.locator('#settingsModal')).toBeVisible();
    
    // Switch to AI tab
    await page.click('.tab-btn[onclick="switchTab(\'ai\')"]');
    await expect(page.locator('#aiTab')).toHaveClass(/active/);
  });

  test('should show initial API key status', async ({ page }) => {
    // Check that API key cards are visible
    const openaiCard = page.locator('#openaiCard');
    const openrouterCard = page.locator('#openrouterCard');
    const pexelsCard = page.locator('#pexelsCard');
    
    await expect(openaiCard).toBeVisible();
    await expect(openrouterCard).toBeVisible();
    await expect(pexelsCard).toBeVisible();

    // Check initial status indicators
    const openaiStatus = page.locator('#openaiStatusBadge');
    const openrouterStatus = page.locator('#openrouterStatusBadge');
    const pexelsStatus = page.locator('#pexelsStatusBadge');
    
    await expect(openaiStatus).toBeVisible();
    await expect(openrouterStatus).toBeVisible();
    await expect(pexelsStatus).toBeVisible();

    // Status should show either connected, missing, or unknown icons
    const openaiIndicator = openaiStatus.locator('.status-indicator .icon');
    const indicatorClass = await openaiIndicator.getAttribute('class');
    expect(['icon-check', 'icon-cross', 'icon-question'].some(cls => indicatorClass?.includes(cls))).toBe(true);
  });

  test('should open API key edit modal', async ({ page }) => {
    // Click edit button for OpenAI
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    
    // Check that modal opens
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    // Check modal content
    await expect(page.locator('#apiKeyModal h2')).toHaveText('Edit API Key');
    await expect(page.locator('#apiKeyProvider')).toHaveValue('Openai');
    await expect(page.locator('#apiKeyInput')).toBeVisible();
    
    // Check help text is provider-specific
    const helpText = page.locator('#apiKeyHelp');
    await expect(helpText).toContainText('OpenAI API key');
    await expect(helpText).toContainText('platform.openai.com');
  });

  test('should save API key and update status', async ({ page }) => {
    // Click edit button for OpenAI
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    // Fill in API key
    const testKey = 'sk-test-key-1234567890123456789012345678901234567890';
    await page.fill('#apiKeyInput', testKey);
    
    // Save the key
    await page.click('button[type="submit"]:has-text("Save Key")');
    
    // Wait for modal to close
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
    
    // Check that status badge updates to connected
    const openaiStatus = page.locator('#openaiStatusBadge');
    const indicator = openaiStatus.locator('.status-indicator .icon');
    const statusText = openaiStatus.locator('.status-text');

    await expect(indicator).toHaveClass(/icon-check/);
    await expect(statusText).toHaveText('Connected');
    await expect(statusText).toHaveClass(/connected/);
  });

  test('should show validation errors for invalid keys', async ({ page }) => {
    // Click edit button for OpenAI
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    // Try to save empty key
    await page.click('button[type="submit"]:has-text("Save Key")');
    
    // Check for error message
    const errorElement = page.locator('#apiKeyError');
    await expect(errorElement).toBeVisible();
    await expect(errorElement).toContainText('API key is required');
    
    // Try to save short key
    await page.fill('#apiKeyInput', 'short');
    await page.click('button[type="submit"]:has-text("Save Key")');
    
    await expect(errorElement).toContainText('at least 10 characters');
  });

  test('should toggle password visibility', async ({ page }) => {
    // Click edit button for OpenAI
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    const keyInput = page.locator('#apiKeyInput');
    const toggleButton = page.locator('button[title="Toggle visibility"]');
    
    // Initially should be password type
    await expect(keyInput).toHaveAttribute('type', 'password');
    
    // Fill in some text
    await keyInput.fill('test-key-123');
    
    // Click toggle button
    await toggleButton.click();
    
    // Should now be text type
    await expect(keyInput).toHaveAttribute('type', 'text');
    
    // Click toggle again
    await toggleButton.click();
    
    // Should be password type again
    await expect(keyInput).toHaveAttribute('type', 'password');
  });

  test('should delete API key and update status', async ({ page }) => {
    // First, add a key
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    const testKey = 'sk-test-key-1234567890123456789012345678901234567890';
    await page.fill('#apiKeyInput', testKey);
    await page.click('button[type="submit"]:has-text("Save Key")');
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
    
    // Verify key is saved (status should be connected)
    const openaiStatus = page.locator('#openaiStatusBadge');
    await expect(openaiStatus.locator('.status-indicator')).toHaveText('✅');
    
    // Open edit modal again
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    // Delete button should be visible for existing key
    const deleteButton = page.locator('#deleteKeyBtn');
    await expect(deleteButton).toBeVisible();
    
    // Click delete and confirm
    page.on('dialog', dialog => dialog.accept());
    await deleteButton.click();
    
    // Modal should close
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
    
    // Status should update to missing
    await expect(openaiStatus.locator('.status-indicator .icon')).toHaveClass(/icon-cross/);
    await expect(openaiStatus.locator('.status-text')).toHaveText('Missing');
  });

  test('should handle different providers correctly', async ({ page }) => {
    // Test OpenRouter
    await page.click('#openrouterCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    await expect(page.locator('#apiKeyProvider')).toHaveValue('Openrouter');
    const helpText = page.locator('#apiKeyHelp');
    await expect(helpText).toContainText('OpenRouter API key');
    await expect(helpText).toContainText('openrouter.ai');
    
    // Close modal
    await page.click('button:has-text("Cancel")');
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
    
    // Test Pexels
    await page.click('#pexelsCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    await expect(page.locator('#apiKeyProvider')).toHaveValue('Pexels');
    await expect(helpText).toContainText('Pexels API key');
    await expect(helpText).toContainText('pexels.com');
  });

  test('should show loading state during save', async ({ page }) => {
    // Click edit button for OpenAI
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    // Fill in API key
    const testKey = 'sk-test-key-1234567890123456789012345678901234567890';
    await page.fill('#apiKeyInput', testKey);
    
    // Click save and immediately check for loading state
    const saveButton = page.locator('button[type="submit"]:has-text("Save Key")');
    await saveButton.click();
    
    // Button should show loading state briefly
    await expect(saveButton).toHaveText('Saving...');
    await expect(saveButton).toBeDisabled();
    
    // Wait for completion
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
  });

  test('should maintain status across page reloads', async ({ page }) => {
    // Save a key
    await page.click('#openaiCard .btn:has-text("Edit Key")');
    await expect(page.locator('#apiKeyModal')).toBeVisible();
    
    const testKey = 'sk-test-key-1234567890123456789012345678901234567890';
    await page.fill('#apiKeyInput', testKey);
    await page.click('button[type="submit"]:has-text("Save Key")');
    await expect(page.locator('#apiKeyModal')).not.toBeVisible();
    
    // Verify status is connected
    const openaiStatus = page.locator('#openaiStatusBadge');
    await expect(openaiStatus.locator('.status-indicator')).toHaveText('✅');
    
    // Close settings modal
    await page.click('button:has-text("Close")');
    await expect(page.locator('#settingsModal')).not.toBeVisible();
    
    // Reload page
    await page.reload();
    await expect(page.locator('header .logo')).toBeVisible();
    
    // Open settings again
    await page.click('.settings-btn');
    await page.click('.tab-btn[onclick="switchTab(\'ai\')"]');
    
    // Status should still be connected
    await expect(openaiStatus.locator('.status-indicator .icon')).toHaveClass(/icon-check/);
    await expect(openaiStatus.locator('.status-text')).toHaveText('Connected');
  });

  test('should have proper styling for status indicators', async ({ page }) => {
    const openaiStatus = page.locator('#openaiStatusBadge');
    const indicator = openaiStatus.locator('.status-indicator');
    const text = openaiStatus.locator('.status-text');
    
    // Check that status elements are properly styled
    await expect(indicator).toHaveCSS('font-size', '18px'); // --font-size-lg
    await expect(text).toHaveCSS('font-size', '14px'); // --font-size-sm
    await expect(text).toHaveCSS('font-weight', '500'); // --font-weight-medium
    
    // Check card styling
    const openaiCard = page.locator('#openaiCard');
    await expect(openaiCard).toHaveCSS('border-radius', '8px'); // --card-radius
    await expect(openaiCard).toHaveCSS('padding', '16px'); // --space-4
  });
});
