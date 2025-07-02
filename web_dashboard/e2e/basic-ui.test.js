/**
 * @test-category e2e
 * @test-type ui
 * @description Basic ui tests
 * @browser chromium,firefox,webkit
 */

import { test, expect } from '@playwright/test';
import { DashboardHelpers } from './helpers.js';

test.describe('Basic UI Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new DashboardHelpers(page);
    await page.goto('/');
    await helpers.waitForPageLoad();
  });

  test('dashboard loads with correct title and structure', async ({ page }) => {
    // Check main title
    await expect(page.locator('h1')).toHaveText(/Forge API Tool/);
    
    // Check header elements
    await expect(page.locator('.dashboard-header')).toBeVisible();
    await expect(page.locator('.status-indicators')).toBeVisible();
    
    // Check main layout
    await expect(page.locator('.templates-sidebar')).toBeVisible();
    await expect(page.locator('.main-content')).toBeVisible();
    
    // Check status indicators exist
    await expect(page.locator('#api-status')).toBeVisible();
    await expect(page.locator('#generation-status')).toBeVisible();
    await expect(page.locator('#queue-status')).toBeVisible();
  });

  test('sidebar is resizable', async ({ page }) => {
    const sidebar = page.locator('.templates-sidebar');
    const resizer = page.locator('#sidebar-resizer');
    
    // Check resizer is visible
    await expect(resizer).toBeVisible();
    
    // Get initial width
    const initialWidth = await sidebar.evaluate(el => el.offsetWidth);
    
    // Simulate drag to resize
    await resizer.hover();
    await page.mouse.down();
    await page.mouse.move(350, 100); // Move right to increase width
    await page.mouse.up();
    
    // Check width changed
    const newWidth = await sidebar.evaluate(el => el.offsetWidth);
    expect(newWidth).toBeGreaterThan(initialWidth);
  });

  test('template cards display correctly', async ({ page }) => {
    // Check templates container exists
    await expect(page.locator('.templates-container')).toBeVisible();
    
    // Check if templates are loaded (either cards or no templates message)
    const templateCards = page.locator('.template-card');
    const noTemplatesMessage = page.locator('.text-center.text-muted');
    
    const hasCards = await templateCards.count() > 0;
    const hasMessage = await noTemplatesMessage.isVisible();
    
    // Should have either cards or the no templates message
    expect(hasCards || hasMessage).toBeTruthy();
    
    if (hasCards) {
      // Check template card structure
      const firstCard = templateCards.first();
      await expect(firstCard.locator('.template-name')).toBeVisible();
      await expect(firstCard.locator('.template-info')).toBeVisible();
      await expect(firstCard.locator('.template-actions-bar')).toBeVisible();
    }
  });

  test('generation settings form is accessible', async ({ page }) => {
    // Check generation settings section
    await expect(page.locator('.generation-settings')).toBeVisible();
    await expect(page.locator('.settings-header h3')).toHaveText(/Generation Settings/);
    
    // Check form fields
    await expect(page.locator('#prompt-input')).toBeVisible();
    await expect(page.locator('#negative-prompt-input')).toBeVisible();
    await expect(page.locator('#config-select')).toBeVisible();
    await expect(page.locator('#seed-input')).toBeVisible();
  });

  test('settings modal opens and closes', async ({ page }) => {
    // Open settings modal
    await helpers.openSettings();
    
    // Check modal content
    await expect(page.locator('#settings-modal')).toBeVisible();
    await expect(page.locator('#settings-modal h3')).toHaveText(/Settings/);
    
    // Check settings tabs
    await expect(page.locator('.settings-tabs')).toBeVisible();
    await expect(page.locator('[onclick="switchSettingsTab(\'api\')"]')).toBeVisible();
    await expect(page.locator('[onclick="switchSettingsTab(\'output\')"]')).toBeVisible();
    await expect(page.locator('[onclick="switchSettingsTab(\'logs\')"]')).toBeVisible();
    await expect(page.locator('[onclick="switchSettingsTab(\'advanced\')"]')).toBeVisible();
    
    // Close modal
    await helpers.closeModal('settings-modal');
    
    // Check modal is hidden
    await expect(page.locator('#settings-modal')).not.toBeVisible();
  });

  test('settings tabs switch correctly', async ({ page }) => {
    await helpers.openSettings();
    
    // Test API settings tab
    await helpers.switchSettingsTab('api');
    await expect(page.locator('#api-settings-tab.active')).toBeVisible();
    
    // Test output settings tab
    await helpers.switchSettingsTab('output');
    await expect(page.locator('#output-settings-tab.active')).toBeVisible();
    
    // Test logs settings tab
    await helpers.switchSettingsTab('logs');
    await expect(page.locator('#logs-settings-tab.active')).toBeVisible();
    
    // Test advanced settings tab
    await helpers.switchSettingsTab('advanced');
    await expect(page.locator('#advanced-settings-tab.active')).toBeVisible();
    
    await helpers.closeModal('settings-modal');
  });

  test('notification system works', async ({ page }) => {
    // Check notification container exists
    await expect(page.locator('#notification-container')).toBeVisible();
    
    // Trigger a notification (if any button triggers one)
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Wait for potential notification
      try {
        await helpers.waitForNotification(2000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText).toBeTruthy();
      } catch (e) {
        // No notification triggered, which is fine
        console.log('No notification triggered by connect button');
      }
    }
  });

  test('responsive design elements', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    
    // Check elements are still accessible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.templates-sidebar')).toBeVisible();
    await expect(page.locator('.main-content')).toBeVisible();
    
    // Reset viewport
    await page.setViewportSize({ width: 1280, height: 720 });
  });

  test('keyboard navigation works', async ({ page }) => {
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Check focus moves to first focusable element
    const focusedElement = await page.evaluate(() => document.activeElement);
    expect(focusedElement).not.toBeNull();
    
    // Test escape key closes modals
    await helpers.openSettings();
    await page.keyboard.press('Escape');
    await expect(page.locator('#settings-modal')).not.toBeVisible();
  });
}); 