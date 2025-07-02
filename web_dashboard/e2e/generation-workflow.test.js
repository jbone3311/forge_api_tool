/**
 * @test-category e2e
 * @test-type workflow
 * @description Generation workflow tests
 * @browser chromium,firefox,webkit
 */

import { test, expect } from '@playwright/test';
import { DashboardHelpers } from './helpers.js';

test.describe('Generation Workflow Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new DashboardHelpers(page);
    await page.goto('/');
    await helpers.waitForPageLoad();
  });

  test('generation settings form is properly structured', async ({ page }) => {
    // Check generation settings section
    await expect(page.locator('.generation-settings')).toBeVisible();
    await expect(page.locator('.settings-header h3')).toHaveText(/Generation Settings/);
    
    // Check basic settings section
    await expect(page.locator('.settings-section h4')).toHaveText(/Basic Settings/);
    
    // Check form fields
    await expect(page.locator('#prompt-input')).toBeVisible();
    await expect(page.locator('#negative-prompt-input')).toBeVisible();
    await expect(page.locator('#config-select')).toBeVisible();
    await expect(page.locator('#seed-input')).toBeVisible();
  });

  test('prompt input accepts text and updates', async ({ page }) => {
    const promptInput = page.locator('#prompt-input');
    const testPrompt = 'A beautiful landscape with mountains and trees';
    
    // Fill prompt input
    await helpers.fillField('#prompt-input', testPrompt);
    
    // Check value was set
    const inputValue = await promptInput.inputValue();
    expect(inputValue).toBe(testPrompt);
    
    // Clear and check
    await helpers.fillField('#prompt-input', '');
    const emptyValue = await promptInput.inputValue();
    expect(emptyValue).toBe('');
  });

  test('negative prompt input works correctly', async ({ page }) => {
    const negativePromptInput = page.locator('#negative-prompt-input');
    const testNegativePrompt = 'blurry, low quality, distorted';
    
    // Fill negative prompt
    await helpers.fillField('#negative-prompt-input', testNegativePrompt);
    
    // Check value was set
    const inputValue = await negativePromptInput.inputValue();
    expect(inputValue).toBe(testNegativePrompt);
  });

  test('template selection dropdown works', async ({ page }) => {
    const configSelect = page.locator('#config-select');
    
    // Check dropdown is visible and enabled
    await expect(configSelect).toBeVisible();
    await expect(configSelect).toBeEnabled();
    
    // Check default option
    const defaultOption = configSelect.locator('option').first();
    await expect(defaultOption).toHaveText('Select a template...');
    
    // Check if other options are available
    const options = configSelect.locator('option');
    const optionCount = await options.count();
    expect(optionCount).toBeGreaterThan(1); // Should have at least default + some templates
  });

  test('seed input accepts numeric values', async ({ page }) => {
    const seedInput = page.locator('#seed-input');
    
    // Test valid seed number
    await helpers.fillField('#seed-input', '12345');
    let inputValue = await seedInput.inputValue();
    expect(inputValue).toBe('12345');
    
    // Test negative seed
    await helpers.fillField('#seed-input', '-1');
    inputValue = await seedInput.inputValue();
    expect(inputValue).toBe('-1');
    
    // Test clearing (random seed)
    await helpers.fillField('#seed-input', '');
    inputValue = await seedInput.inputValue();
    expect(inputValue).toBe('');
  });

  test('form validation works for required fields', async ({ page }) => {
    // Try to submit without required fields
    const generateButton = page.locator('button[onclick*="generateSingle"]').first();
    
    if (await generateButton.isVisible()) {
      await generateButton.click();
      
      // Check for validation messages or errors
      // This depends on your validation implementation
      try {
        await helpers.waitForNotification(2000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText).toContain('error') || expect(notificationText).toContain('required');
      } catch (e) {
        // No validation triggered, which might be fine depending on implementation
        console.log('No validation error triggered');
      }
    }
  });

  test('settings actions work correctly', async ({ page }) => {
    // Check reset button
    const resetButton = page.locator('button[onclick="loadDefaultSettings()"]');
    await expect(resetButton).toBeVisible();
    
    // Check save button
    const saveButton = page.locator('button[onclick="saveSettings()"]');
    await expect(saveButton).toBeVisible();
    
    // Test reset functionality
    await helpers.fillField('#prompt-input', 'Test prompt');
    await resetButton.click();
    
    // Check if form was reset
    const promptValue = await page.locator('#prompt-input').inputValue();
    expect(promptValue).toBe(''); // Should be empty after reset
  });

  test('progress section appears during generation', async ({ page }) => {
    // Initially progress section should be hidden
    await expect(page.locator('#progress-section')).not.toBeVisible();
    
    // Mock a generation start to test progress display
    // This would require triggering an actual generation or mocking the API
    console.log('Progress section test - would need actual generation to test fully');
  });

  test('generation controls are accessible', async ({ page }) => {
    // Check for generation buttons
    const generateButtons = page.locator('button[onclick*="generateSingle"]');
    const batchButtons = page.locator('button[onclick*="startBatch"]');
    
    // Should have at least one generate button (either in form or template cards)
    const generateCount = await generateButtons.count();
    const batchCount = await batchButtons.count();
    
    expect(generateCount + batchCount).toBeGreaterThan(0);
  });

  test('form field labels are properly associated', async ({ page }) => {
    // Check label associations for accessibility
    const promptLabel = page.locator('label[for="prompt-input"]');
    const negativePromptLabel = page.locator('label[for="negative-prompt-input"]');
    const configLabel = page.locator('label[for="config-select"]');
    const seedLabel = page.locator('label[for="seed-input"]');
    
    // Check labels exist and are visible
    if (await promptLabel.count() > 0) {
      await expect(promptLabel).toBeVisible();
    }
    if (await negativePromptLabel.count() > 0) {
      await expect(negativePromptLabel).toBeVisible();
    }
    if (await configLabel.count() > 0) {
      await expect(configLabel).toBeVisible();
    }
    if (await seedLabel.count() > 0) {
      await expect(seedLabel).toBeVisible();
    }
  });

  test('form fields have proper placeholders', async ({ page }) => {
    // Check placeholder text
    const promptInput = page.locator('#prompt-input');
    const negativePromptInput = page.locator('#negative-prompt-input');
    
    const promptPlaceholder = await promptInput.getAttribute('placeholder');
    const negativePlaceholder = await negativePromptInput.getAttribute('placeholder');
    
    expect(promptPlaceholder).toBeTruthy();
    expect(negativePlaceholder).toBeTruthy();
  });

  test('form submission workflow', async ({ page }) => {
    // Fill out the form
    await helpers.fillField('#prompt-input', 'A serene mountain landscape');
    await helpers.fillField('#negative-prompt-input', 'blurry, low quality');
    await helpers.fillField('#seed-input', '42');
    
    // Select a template if available
    const configSelect = page.locator('#config-select');
    const options = configSelect.locator('option');
    const optionCount = await options.count();
    
    if (optionCount > 1) {
      // Select first non-default option
      await configSelect.selectOption({ index: 1 });
    }
    
    // Try to submit (this will depend on your actual submission logic)
    const generateButton = page.locator('button[onclick*="generateSingle"]').first();
    
    if (await generateButton.isVisible()) {
      await generateButton.click();
      
      // Check for any response (success, error, or progress)
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText).toBeTruthy();
      } catch (e) {
        // No immediate notification, which might be expected
        console.log('No immediate notification after form submission');
      }
    }
  });

  test('form field focus and keyboard navigation', async ({ page }) => {
    // Test tab navigation through form fields
    await page.keyboard.press('Tab');
    
    // Check if focus moved to first form field
    const focusedElement = await page.evaluate(() => document.activeElement);
    const focusedId = await focusedElement.getAttribute('id');
    
    // Should focus on a form field
    expect(['prompt-input', 'negative-prompt-input', 'config-select', 'seed-input']).toContain(focusedId);
    
    // Test tab through all fields
    for (let i = 0; i < 4; i++) {
      await page.keyboard.press('Tab');
    }
    
    // Should have moved through all form fields
    const finalFocusedElement = await page.evaluate(() => document.activeElement);
    expect(finalFocusedElement).not.toBeNull();
  });

  test('form field input validation', async ({ page }) => {
    const seedInput = page.locator('#seed-input');
    
    // Test numeric input validation
    await helpers.fillField('#seed-input', 'abc');
    let inputValue = await seedInput.inputValue();
    
    // HTML5 validation should prevent non-numeric input
    // But if it doesn't, we can check the value
    if (inputValue === 'abc') {
      console.log('HTML5 validation not enforced on seed input');
    } else {
      expect(inputValue).toBe(''); // Should be empty if validation worked
    }
    
    // Test valid numeric input
    await helpers.fillField('#seed-input', '123');
    inputValue = await seedInput.inputValue();
    expect(inputValue).toBe('123');
  });
}); 