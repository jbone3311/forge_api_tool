/**
 * @test-category e2e
 * @test-type general
 * @description Dashboard.e2e tests
 * @browser chromium,firefox,webkit
 */

// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Forge API Tool Dashboard', () => {
  test('dashboard loads and shows title', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toHaveText(/Forge API Tool/);
  });
}); 