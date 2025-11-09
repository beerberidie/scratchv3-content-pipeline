/**
 * E2E tests for login page theme consistency
 */
import { test, expect } from '@playwright/test';

test.describe('Login Page Theme', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should have consistent theme colors', async ({ page }) => {
    // Check that theme CSS is loaded
    const themeLink = page.locator('link[href="/static/css/theme.css"]');
    await expect(themeLink).toBeAttached();

    // Check header styling
    const header = page.locator('header');
    await expect(header).toHaveCSS('background', /rgb\(255, 255, 255\)/); // --nav-bg (white)
    await expect(header).toHaveCSS('border-bottom', /1px solid/);

    // Check logo styling
    const logo = page.locator('.logo');
    await expect(logo).toHaveCSS('color', /rgb\(37, 99, 235\)/); // --primary-600
    await expect(logo).toHaveCSS('font-weight', '700'); // --font-weight-bold

    // Check login box styling
    const loginBox = page.locator('.login-box');
    await expect(loginBox).toHaveCSS('background', /rgb\(255, 255, 255\)/); // --card-bg
    await expect(loginBox).toHaveCSS('border-radius', '12px'); // --card-radius
    await expect(loginBox).toHaveCSS('box-shadow', /rgba\(0, 0, 0, 0\.25\)/); // --shadow-xl

    // Check input styling
    const usernameInput = page.locator('#username');
    await expect(usernameInput).toHaveCSS('border-radius', '12px'); // --radius-xl
    await expect(usernameInput).toHaveCSS('border', /1px solid/);

    // Check button styling
    const loginButton = page.locator('button[type="submit"]');
    await expect(loginButton).toHaveCSS('background-color', /rgb\(37, 99, 235\)/); // --btn-primary-bg
    await expect(loginButton).toHaveCSS('border-radius', '12px'); // --radius-xl
    await expect(loginButton).toHaveCSS('color', /rgb\(255, 255, 255\)/); // --btn-primary-text
  });

  test('should have proper typography', async ({ page }) => {
    // Check main heading
    const heading = page.locator('h2');
    await expect(heading).toHaveCSS('font-size', '30px'); // --font-size-3xl
    await expect(heading).toHaveCSS('font-weight', '700'); // --font-weight-bold

    // Check subtitle
    const subtitle = page.locator('.login-subtitle');
    await expect(subtitle).toHaveCSS('font-size', '16px'); // --font-size-base
    await expect(subtitle).toHaveCSS('color', /rgb\(75, 85, 99\)/); // --text-secondary

    // Check form labels
    const label = page.locator('label').first();
    await expect(label).toHaveCSS('font-weight', '500'); // --font-weight-medium
    await expect(label).toHaveCSS('font-size', '14px'); // --font-size-sm
  });

  test('should show test accounts in development mode', async ({ page }) => {
    // Test accounts should be hidden by default
    const testAccounts = page.locator('#testAccounts');
    await expect(testAccounts).toHaveCSS('display', 'none');

    // Navigate to localhost to trigger debug mode
    if (page.url().includes('localhost') || page.url().includes('127.0.0.1')) {
      await page.reload();
      await expect(testAccounts).toBeVisible();
      
      // Check test account selector
      const testAccountSelect = page.locator('#testAccountSelect');
      await expect(testAccountSelect).toBeVisible();
      
      // Check that options are available
      const options = testAccountSelect.locator('option');
      await expect(options).toHaveCount(4); // Empty + 3 test accounts
    }
  });

  test('should have responsive design', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    const loginContainer = page.locator('.login-container');
    await expect(loginContainer).toHaveCSS('max-width', '480px');

    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(loginContainer).toBeVisible();
    
    // Login box should still be properly sized
    const loginBox = page.locator('.login-box');
    await expect(loginBox).toBeVisible();
  });

  test('should have proper focus states', async ({ page }) => {
    // Focus username input
    const usernameInput = page.locator('#username');
    await usernameInput.focus();
    
    // Check focus styling
    await expect(usernameInput).toHaveCSS('border-color', /rgb\(59, 130, 246\)/); // --input-border-focus
    await expect(usernameInput).toHaveCSS('box-shadow', /rgba\(37, 99, 235, 0\.1\)/);

    // Focus password input
    const passwordInput = page.locator('#password');
    await passwordInput.focus();
    await expect(passwordInput).toHaveCSS('border-color', /rgb\(59, 130, 246\)/);
  });

  test('should have proper hover states', async ({ page }) => {
    const loginButton = page.locator('button[type="submit"]');
    
    // Hover over login button
    await loginButton.hover();
    
    // Check hover styling (transform and shadow)
    await expect(loginButton).toHaveCSS('transform', /translateY\(-1px\)/);
    await expect(loginButton).toHaveCSS('box-shadow', /rgba\(0, 0, 0, 0\.1\)/);
  });

  test('should handle test account selection', async ({ page }) => {
    // Only test if in development mode
    if (page.url().includes('localhost') || page.url().includes('127.0.0.1')) {
      await page.reload();
      
      const testAccountSelect = page.locator('#testAccountSelect');
      const usernameInput = page.locator('#username');
      const passwordInput = page.locator('#password');
      
      // Select admin test account
      await testAccountSelect.selectOption('admin:admin123');
      
      // Check that inputs are filled
      await expect(usernameInput).toHaveValue('admin');
      await expect(passwordInput).toHaveValue('admin123');
      
      // Select demo test account
      await testAccountSelect.selectOption('demo:demo123');
      
      // Check that inputs are updated
      await expect(usernameInput).toHaveValue('demo');
      await expect(passwordInput).toHaveValue('demo123');
    }
  });

  test('should maintain theme consistency across elements', async ({ page }) => {
    // Check that all interactive elements use consistent spacing
    const formGroups = page.locator('.form-group');
    const count = await formGroups.count();
    
    for (let i = 0; i < count; i++) {
      const formGroup = formGroups.nth(i);
      await expect(formGroup).toHaveCSS('margin-bottom', /20px/); // --space-5
    }

    // Check consistent border radius on inputs
    const inputs = page.locator('input[type="text"], input[type="password"]');
    const inputCount = await inputs.count();
    
    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      await expect(input).toHaveCSS('border-radius', '12px'); // --radius-xl
    }

    // Check consistent padding on inputs
    for (let i = 0; i < inputCount; i++) {
      const input = inputs.nth(i);
      await expect(input).toHaveCSS('padding', /12px 16px/); // --input-padding-y --input-padding-x
    }
  });

  test('should have accessible color contrast', async ({ page }) => {
    // Check that text has sufficient contrast
    const heading = page.locator('h2');
    await expect(heading).toHaveCSS('color', /rgb\(17, 24, 39\)/); // --text-primary (dark)

    const subtitle = page.locator('.login-subtitle');
    await expect(subtitle).toHaveCSS('color', /rgb\(75, 85, 99\)/); // --text-secondary

    // Check button text contrast
    const loginButton = page.locator('button[type="submit"]');
    await expect(loginButton).toHaveCSS('color', /rgb\(255, 255, 255\)/); // White text on blue background
  });
});
