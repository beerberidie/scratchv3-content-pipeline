/**
 * E2E tests for immediate task execution functionality
 */
import { test, expect } from '@playwright/test';

test.describe('Immediate Task Execution', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/');
    await page.fill('#username', 'admin');
    await page.fill('#password', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard to load
    await expect(page.locator('header .logo')).toBeVisible();
  });

  test('should show helper text for optional fields', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Check that scheduled time helper text indicates it's optional
    const timeHelperText = page.locator('#timeInput').locator('..').locator('.helper-text');
    await expect(timeHelperText).toContainText('Optional');
    await expect(timeHelperText).toContainText('generate article immediately');
    await expect(timeHelperText).toContainText('save to history');
    
    // Check that WordPress site helper text indicates it's optional
    const wpHelperText = page.locator('#topicWordPressDropdown').locator('..').locator('.helper-text');
    await expect(wpHelperText).toContainText('Optional');
    await expect(wpHelperText).toContainText('save to history only');
  });

  test('should allow creating task without scheduled time', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in only required fields
    await page.fill('#topicInput', 'Test Immediate Execution');
    await page.fill('#rulesInput', 'Generate a test article');
    
    // Leave scheduled time and WordPress site empty
    await expect(page.locator('#timeInput')).toHaveValue('');
    await expect(page.locator('#topicWordPressDropdown')).toHaveValue('');
    
    // Submit the form
    await page.click('button:has-text("Add")');
    
    // Should show success message for immediate execution
    await expect(page.locator('.notification, [role="alert"]')).toContainText('Article generated and saved to history');
    
    // Modal should close
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
  });

  test('should show scheduled message when time is provided', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in required fields and scheduled time
    await page.fill('#topicInput', 'Test Scheduled Execution');
    await page.fill('#rulesInput', 'Generate a scheduled article');
    
    // Set a future date/time
    const futureDate = new Date();
    futureDate.setHours(futureDate.getHours() + 1);
    const dateTimeString = futureDate.toISOString().slice(0, 16);
    await page.fill('#timeInput', dateTimeString);
    
    // Submit the form
    await page.click('button:has-text("Add")');
    
    // Should show success message for scheduled execution
    await expect(page.locator('.notification, [role="alert"]')).toContainText('Task created and scheduled successfully');
    
    // Modal should close
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
  });

  test('should show scheduled message when WordPress site is selected', async ({ page }) => {
    // First add a WordPress site in settings
    await page.click('.settings-btn');
    await expect(page.locator('#settingsModal')).toBeVisible();
    
    await page.click('.tab-btn[onclick="switchTab(\'wordpress\')"]');
    await expect(page.locator('#wordpressTab')).toHaveClass(/active/);
    
    // Add a test WordPress site
    await page.fill('#newWordPressPreset', 'https://test-site.com');
    await page.click('button:has-text("Add Site")');
    
    // Close settings
    await page.click('button:has-text("Close")');
    await expect(page.locator('#settingsModal')).not.toBeVisible();
    
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in required fields and select WordPress site
    await page.fill('#topicInput', 'Test WordPress Publication');
    await page.fill('#rulesInput', 'Generate an article for WordPress');
    
    // Select the WordPress site
    await page.selectOption('#topicWordPressDropdown', 'https://test-site.com');
    
    // Leave scheduled time empty
    await expect(page.locator('#timeInput')).toHaveValue('');
    
    // Submit the form
    await page.click('button:has-text("Add")');
    
    // Should show success message for scheduled execution (because WordPress site is selected)
    await expect(page.locator('.notification, [role="alert"]')).toContainText('Task created and scheduled successfully');
    
    // Modal should close
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
  });

  test('should display immediate execution tasks correctly in table', async ({ page }) => {
    // Create an immediate execution task
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    await page.fill('#topicInput', 'Immediate Task Display Test');
    await page.fill('#rulesInput', 'Test display in table');
    
    // Submit without scheduled time
    await page.click('button:has-text("Add")');
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
    
    // Wait for table to update
    await page.waitForTimeout(1000);
    
    // Check that the task appears in the table
    const taskRow = page.locator('tr').filter({ hasText: 'Immediate Task Display Test' });
    await expect(taskRow).toBeVisible();
    
    // Check that the scheduled time column shows "Immediate execution"
    await expect(taskRow).toContainText('Immediate execution');
  });

  test('should validate that topic is still required', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Try to submit without topic
    await page.click('button:has-text("Add")');
    
    // Should show validation error
    await expect(page.locator('.notification, [role="alert"], .error')).toContainText('Topic');
    
    // Modal should remain open
    await expect(page.locator('#addTopicModal')).toBeVisible();
  });

  test('should handle form validation correctly', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in topic but leave rules empty
    await page.fill('#topicInput', 'Test Validation');
    
    // Submit the form
    await page.click('button:has-text("Add")');
    
    // Should succeed even with empty rules (rules are optional)
    await expect(page.locator('.notification, [role="alert"]')).toContainText('Article generated and saved to history');
    
    // Modal should close
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
  });

  test('should handle future scheduled time validation', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in required fields
    await page.fill('#topicInput', 'Test Past Time Validation');
    await page.fill('#rulesInput', 'Test validation');
    
    // Set a past date/time
    const pastDate = new Date();
    pastDate.setHours(pastDate.getHours() - 1);
    const dateTimeString = pastDate.toISOString().slice(0, 16);
    await page.fill('#timeInput', dateTimeString);
    
    // Submit the form
    await page.click('button:has-text("Add")');
    
    // Should show validation error for past time
    await expect(page.locator('.field-error, .error')).toContainText('must be in the future');
    
    // Modal should remain open
    await expect(page.locator('#addTopicModal')).toBeVisible();
  });

  test('should clear form correctly after submission', async ({ page }) => {
    // Open add topic modal
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Fill in fields
    await page.fill('#topicInput', 'Test Form Clear');
    await page.fill('#rulesInput', 'Test clearing');
    await page.fill('#articleInput', 'Some article content');
    await page.check('#imageInput');
    
    // Submit the form
    await page.click('button:has-text("Add")');
    await expect(page.locator('#addTopicModal')).not.toBeVisible();
    
    // Open modal again
    await page.click('button:has-text("Add Topic")');
    await expect(page.locator('#addTopicModal')).toBeVisible();
    
    // Check that all fields are cleared
    await expect(page.locator('#topicInput')).toHaveValue('');
    await expect(page.locator('#rulesInput')).toHaveValue('');
    await expect(page.locator('#articleInput')).toHaveValue('');
    await expect(page.locator('#timeInput')).toHaveValue('');
    await expect(page.locator('#topicWordPressDropdown')).toHaveValue('');
    await expect(page.locator('#imageInput')).not.toBeChecked();
  });
});
