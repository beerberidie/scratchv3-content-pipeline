/**
 * E2E tests for WordPress URL management
 */
import { test, expect } from '@playwright/test';

test.describe('WordPress URL Management', () => {
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
    
    // Switch to WordPress tab
    await page.click('.tab-btn[onclick="switchTab(\'wordpress\')"]');
    await expect(page.locator('#wordpressTab')).toHaveClass(/active/);
  });

  test('should show WordPress sites section', async ({ page }) => {
    // Check that WordPress sites section is visible
    const sitesSection = page.locator('h3:has-text("WordPress Sites")');
    await expect(sitesSection).toBeVisible();
    
    // Check that sites list container exists
    const sitesList = page.locator('#wordpressPresetsList');
    await expect(sitesList).toBeVisible();
    
    // Check that add site form exists
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    await expect(addSiteInput).toBeVisible();
    await expect(addSiteButton).toBeVisible();
    await expect(addSiteInput).toHaveAttribute('placeholder', /Enter WordPress URL/);
  });

  test('should add a new WordPress site', async ({ page }) => {
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    // Add a test site
    const testUrl = 'https://test-site.com';
    await addSiteInput.fill(testUrl);
    await addSiteButton.click();
    
    // Check that site appears in the list
    const sitesList = page.locator('#wordpressPresetsList');
    await expect(sitesList.locator('.wordpress-site-item')).toBeVisible();
    
    // Check that the URL is displayed correctly
    const siteItem = sitesList.locator('.wordpress-site-item').first();
    await expect(siteItem.locator('.site-url')).toHaveText(testUrl);
    
    // Check that delete button is present
    await expect(siteItem.locator('.delete-site-btn')).toBeVisible();
    await expect(siteItem.locator('.delete-site-btn .icon')).toHaveClass(/icon-delete/);
    
    // Input should be cleared after adding
    await expect(addSiteInput).toHaveValue('');
  });

  test('should validate WordPress URL format', async ({ page }) => {
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    // Try to add invalid URL
    await addSiteInput.fill('not-a-valid-url');
    await addSiteButton.click();
    
    // Should show validation error (browser validation or custom)
    // The input has type="url" so browser should validate
    const isValid = await addSiteInput.evaluate((input: HTMLInputElement) => input.validity.valid);
    expect(isValid).toBe(false);
  });

  test('should prevent duplicate WordPress sites', async ({ page }) => {
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    const testUrl = 'https://duplicate-test.com';
    
    // Add site first time
    await addSiteInput.fill(testUrl);
    await addSiteButton.click();
    
    // Wait for site to be added
    const sitesList = page.locator('#wordpressPresetsList');
    await expect(sitesList.locator('.wordpress-site-item')).toBeVisible();
    
    // Try to add same URL again
    await addSiteInput.fill(testUrl);
    await addSiteButton.click();
    
    // Should show error notification or prevent duplicate
    // Check that only one instance exists
    const siteItems = sitesList.locator('.wordpress-site-item');
    const count = await siteItems.count();
    
    // Should still be only 1 (or show error message)
    expect(count).toBeLessThanOrEqual(1);
  });

  test('should delete WordPress site', async ({ page }) => {
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    // Add a test site first
    const testUrl = 'https://delete-test.com';
    await addSiteInput.fill(testUrl);
    await addSiteButton.click();
    
    // Wait for site to appear
    const sitesList = page.locator('#wordpressPresetsList');
    const siteItem = sitesList.locator('.wordpress-site-item').first();
    await expect(siteItem).toBeVisible();
    
    // Click delete button
    const deleteButton = siteItem.locator('.delete-site-btn');
    await deleteButton.click();
    
    // Site should be removed from list
    await expect(siteItem).not.toBeVisible();
    
    // Should show "no sites" message if list is empty
    const noSitesMessage = sitesList.locator('.no-sites-message');
    await expect(noSitesMessage).toBeVisible();
    await expect(noSitesMessage).toContainText('No WordPress sites added yet');
  });

  test('should show WordPress authentication section', async ({ page }) => {
    // Check that authentication section is visible
    const authSection = page.locator('h3:has-text("WordPress Authentication")');
    await expect(authSection).toBeVisible();
    
    // Check authentication card
    const authCard = page.locator('.wordpress-auth-card');
    await expect(authCard).toBeVisible();
    
    // Check status indicator
    const authStatus = page.locator('#wordpressAuthStatus');
    await expect(authStatus).toBeVisible();
    
    // Check username and password fields
    const usernameInput = page.locator('#wordpressUsername');
    const passwordInput = page.locator('#wordpressPassword');
    
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    
    // Fields should be readonly initially
    await expect(usernameInput).toHaveAttribute('readonly');
    await expect(passwordInput).toHaveAttribute('readonly');
    
    // Check edit button
    const editButton = page.locator('#editAuthBtn');
    await expect(editButton).toBeVisible();
    await expect(editButton).toContainText('Edit');
  });

  test('should edit WordPress authentication', async ({ page }) => {
    const usernameInput = page.locator('#wordpressUsername');
    const passwordInput = page.locator('#wordpressPassword');
    const editButton = page.locator('#editAuthBtn');
    
    // Click edit button
    await editButton.click();
    
    // Fields should become editable
    await expect(usernameInput).not.toHaveAttribute('readonly');
    await expect(passwordInput).not.toHaveAttribute('readonly');
    
    // Edit button should be hidden
    await expect(editButton).not.toBeVisible();
    
    // Action buttons should appear
    const authActions = page.locator('#authActions');
    await expect(authActions).toBeVisible();
    
    const saveButton = authActions.locator('button:has-text("Save Credentials")');
    const cancelButton = authActions.locator('button:has-text("Cancel")');
    const deleteButton = authActions.locator('button:has-text("Delete Credentials")');
    
    await expect(saveButton).toBeVisible();
    await expect(cancelButton).toBeVisible();
    await expect(deleteButton).toBeVisible();
  });

  test('should save WordPress credentials', async ({ page }) => {
    const usernameInput = page.locator('#wordpressUsername');
    const passwordInput = page.locator('#wordpressPassword');
    const editButton = page.locator('#editAuthBtn');
    
    // Enter edit mode
    await editButton.click();
    
    // Fill in credentials
    await usernameInput.fill('testuser');
    await passwordInput.fill('testpassword123');
    
    // Save credentials
    const saveButton = page.locator('button:has-text("Save Credentials")');
    await saveButton.click();
    
    // Should exit edit mode
    await expect(usernameInput).toHaveAttribute('readonly');
    await expect(passwordInput).toHaveAttribute('readonly');
    
    // Edit button should be visible again
    await expect(editButton).toBeVisible();
    
    // Status should update to configured
    const authStatus = page.locator('#wordpressAuthStatus');
    const statusIndicator = authStatus.locator('.status-indicator');
    const statusText = authStatus.locator('.status-text');
    
    await expect(statusIndicator).toHaveText('✅');
    await expect(statusText).toHaveText('Credentials configured');
    
    // Password should be masked
    await expect(passwordInput).toHaveValue(/••••••••••••/);
  });

  test('should cancel WordPress credentials editing', async ({ page }) => {
    const usernameInput = page.locator('#wordpressUsername');
    const passwordInput = page.locator('#wordpressPassword');
    const editButton = page.locator('#editAuthBtn');
    
    // Store original values
    const originalUsername = await usernameInput.inputValue();
    const originalPassword = await passwordInput.inputValue();
    
    // Enter edit mode
    await editButton.click();
    
    // Make changes
    await usernameInput.fill('changeduser');
    await passwordInput.fill('changedpassword');
    
    // Cancel changes
    const cancelButton = page.locator('button:has-text("Cancel")');
    await cancelButton.click();
    
    // Should exit edit mode
    await expect(usernameInput).toHaveAttribute('readonly');
    await expect(passwordInput).toHaveAttribute('readonly');
    
    // Values should be restored
    await expect(usernameInput).toHaveValue(originalUsername);
    await expect(passwordInput).toHaveValue(originalPassword);
    
    // Edit button should be visible again
    await expect(editButton).toBeVisible();
  });

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.locator('#wordpressPassword');
    const toggleButton = page.locator('button[title="Toggle visibility"]');
    
    // Initially should be password type
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle button
    await toggleButton.click();
    
    // Should become text type
    await expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle again
    await toggleButton.click();
    
    // Should be password type again
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should have proper styling for WordPress elements', async ({ page }) => {
    // Check site item styling
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    // Add a site to test styling
    await addSiteInput.fill('https://styling-test.com');
    await addSiteButton.click();
    
    const siteItem = page.locator('.wordpress-site-item').first();
    await expect(siteItem).toBeVisible();
    
    // Check site item styling
    await expect(siteItem).toHaveCSS('border-radius', '6px'); // --radius-md
    await expect(siteItem).toHaveCSS('padding', '12px'); // --space-3
    await expect(siteItem).toHaveCSS('border', /1px solid/);
    
    // Check site URL styling
    const siteUrl = siteItem.locator('.site-url');
    await expect(siteUrl).toHaveCSS('font-family', /monospace/); // --font-mono
    await expect(siteUrl).toHaveCSS('font-size', '14px'); // --font-size-sm
    
    // Check delete button styling
    const deleteButton = siteItem.locator('.delete-site-btn');
    await expect(deleteButton).toHaveCSS('color', /rgb\(220, 38, 38\)/); // --error-600
    
    // Check auth card styling
    const authCard = page.locator('.wordpress-auth-card');
    await expect(authCard).toHaveCSS('border-radius', '8px'); // --card-radius
    await expect(authCard).toHaveCSS('padding', '20px'); // --space-5
  });

  test('should maintain WordPress sites across page reloads', async ({ page }) => {
    const addSiteInput = page.locator('#newWordPressPreset');
    const addSiteButton = page.locator('button:has-text("Add Site")');
    
    // Add a test site
    const testUrl = 'https://persistent-test.com';
    await addSiteInput.fill(testUrl);
    await addSiteButton.click();
    
    // Verify site is added
    const sitesList = page.locator('#wordpressPresetsList');
    await expect(sitesList.locator('.wordpress-site-item')).toBeVisible();
    
    // Close settings modal
    await page.click('button:has-text("Close")');
    await expect(page.locator('#settingsModal')).not.toBeVisible();
    
    // Reload page
    await page.reload();
    await expect(page.locator('header .logo')).toBeVisible();
    
    // Open settings again
    await page.click('.settings-btn');
    await page.click('.tab-btn[onclick="switchTab(\'wordpress\')"]');
    
    // Site should still be there
    await expect(sitesList.locator('.wordpress-site-item')).toBeVisible();
    const siteItem = sitesList.locator('.wordpress-site-item').first();
    await expect(siteItem.locator('.site-url')).toHaveText(testUrl);
  });
});
