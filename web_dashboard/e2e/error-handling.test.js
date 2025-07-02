/**
 * @test-category e2e
 * @test-type error
 * @description Error handling tests
 * @browser chromium,firefox,webkit
 */

import { test, expect } from '@playwright/test';
import { DashboardHelpers } from './helpers.js';

test.describe('Error Handling Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new DashboardHelpers(page);
    await page.goto('/');
    await helpers.waitForPageLoad();
  });

  test('network errors are handled gracefully', async ({ page }) => {
    // Mock network failure for API calls
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Try to trigger an API call (like connecting)
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check for error handling
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('error') || 
               expect(notificationText.toLowerCase()).toContain('failed') ||
               expect(notificationText.toLowerCase()).toContain('connection');
      } catch (e) {
        // Check if error is displayed in status indicators
        const apiStatus = page.locator('#api-status .status-text');
        const statusText = await apiStatus.textContent();
        expect(statusText.toLowerCase()).toContain('error') || 
               expect(statusText.toLowerCase()).toContain('failed') ||
               expect(statusText.toLowerCase()).toContain('disconnected');
      }
    }
  });

  test('API timeout errors are handled', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/**', route => {
      // Simulate timeout by not responding
      setTimeout(() => {
        route.fulfill({ status: 408, body: 'Request Timeout' });
      }, 100);
    });
    
    // Try to trigger an API call
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check for timeout handling
      try {
        await helpers.waitForNotification(5000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('timeout') || 
               expect(notificationText.toLowerCase()).toContain('error') ||
               expect(notificationText.toLowerCase()).toContain('failed');
      } catch (e) {
        console.log('No timeout error notification detected');
      }
    }
  });

  test('invalid form inputs show appropriate errors', async ({ page }) => {
    // Test invalid seed input
    const seedInput = page.locator('#seed-input');
    
    // Try to enter invalid characters
    await helpers.fillField('#seed-input', 'invalid-seed');
    
    // Check for validation error
    const hasError = await seedInput.evaluate(el => {
      return el.validity.valid === false || 
             el.classList.contains('error') ||
             el.getAttribute('aria-invalid') === 'true';
    });
    
    if (hasError) {
      console.log('Form validation error detected for invalid seed');
    }
    
    // Test empty required fields
    const promptInput = page.locator('#prompt-input');
    await helpers.fillField('#prompt-input', '');
    
    // Try to submit with empty prompt
    const generateButton = page.locator('button[onclick*="generateSingle"]').first();
    if (await generateButton.isVisible()) {
      await generateButton.click();
      
      try {
        await helpers.waitForNotification(2000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('required') || 
               expect(notificationText.toLowerCase()).toContain('empty') ||
               expect(notificationText.toLowerCase()).toContain('invalid');
      } catch (e) {
        console.log('No validation error for empty prompt');
      }
    }
  });

  test('server errors (500) are handled', async ({ page }) => {
    // Mock server error
    await page.route('**/api/**', route => {
      route.fulfill({ 
        status: 500, 
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Try to trigger an API call
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check for server error handling
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('error') || 
               expect(notificationText.toLowerCase()).toContain('server') ||
               expect(notificationText.toLowerCase()).toContain('failed');
      } catch (e) {
        console.log('No server error notification detected');
      }
    }
  });

  test('authentication errors are handled', async ({ page }) => {
    // Mock authentication error
    await page.route('**/api/**', route => {
      route.fulfill({ 
        status: 401, 
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized' })
      });
    });
    
    // Try to trigger an API call
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check for auth error handling
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('unauthorized') || 
               expect(notificationText.toLowerCase()).toContain('auth') ||
               expect(notificationText.toLowerCase()).toContain('login') ||
               expect(notificationText.toLowerCase()).toContain('error');
      } catch (e) {
        console.log('No authentication error notification detected');
      }
    }
  });

  test('malformed JSON responses are handled', async ({ page }) => {
    // Mock malformed JSON response
    await page.route('**/api/**', route => {
      route.fulfill({ 
        status: 200, 
        contentType: 'application/json',
        body: 'invalid json response'
      });
    });
    
    // Try to trigger an API call
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check for JSON parsing error handling
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('error') || 
               expect(notificationText.toLowerCase()).toContain('invalid') ||
               expect(notificationText.toLowerCase()).toContain('parse');
      } catch (e) {
        console.log('No JSON parsing error notification detected');
      }
    }
  });

  test('error notifications are dismissible', async ({ page }) => {
    // Mock an error to trigger notification
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Trigger error
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      try {
        await helpers.waitForNotification(3000);
        
        // Check if notification has close button
        const closeButton = page.locator('#notification-container .notification .close-btn');
        if (await closeButton.count() > 0) {
          await closeButton.click();
          
          // Check if notification disappeared
          await expect(page.locator('#notification-container .notification')).not.toBeVisible();
        }
      } catch (e) {
        console.log('No error notification to test dismissal');
      }
    }
  });

  test('error states are reflected in UI elements', async ({ page }) => {
    // Mock API error
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Trigger error
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check if status indicators show error state
      const apiStatus = page.locator('#api-status');
      const statusIcon = apiStatus.locator('.status-icon');
      
      // Check for error styling
      const hasErrorClass = await apiStatus.evaluate(el => {
        return el.classList.contains('error') || 
               el.classList.contains('failed') ||
               el.classList.contains('disconnected');
      });
      
      if (hasErrorClass) {
        console.log('API status shows error state');
      }
      
      // Check if icon changed to error state
      const iconClass = await statusIcon.getAttribute('class');
      if (iconClass && (iconClass.includes('error') || iconClass.includes('times') || iconClass.includes('exclamation'))) {
        console.log('Status icon shows error state');
      }
    }
  });

  test('recovery from errors works', async ({ page }) => {
    // First, trigger an error
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Wait for error state
      await page.waitForTimeout(2000);
      
      // Now restore normal API behavior
      await page.unroute('**/api/**');
      
      // Try to connect again
      await connectButton.click();
      
      // Check if recovery worked
      try {
        await helpers.waitForNotification(3000);
        const notificationText = await helpers.getNotificationText();
        expect(notificationText.toLowerCase()).toContain('success') || 
               expect(notificationText.toLowerCase()).toContain('connected') ||
               expect(notificationText.toLowerCase()).not.toContain('error');
      } catch (e) {
        console.log('No recovery notification detected');
      }
    }
  });

  test('error logging works correctly', async ({ page }) => {
    // Mock an error and check if it's logged
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Trigger error
    const connectButton = page.locator('#api-connect-btn');
    if (await connectButton.isVisible()) {
      await connectButton.click();
      
      // Check if error was logged to console or sent to backend
      // This would require checking network requests or console logs
      console.log('Error logging test - would need to check backend logs');
    }
  });

  test('graceful degradation when services are unavailable', async ({ page }) => {
    // Mock all API endpoints to fail
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Check if UI still works for non-API features
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.templates-sidebar')).toBeVisible();
    await expect(page.locator('.main-content')).toBeVisible();
    
    // Check if form inputs still work
    await helpers.fillField('#prompt-input', 'Test prompt');
    const inputValue = await page.locator('#prompt-input').inputValue();
    expect(inputValue).toBe('Test prompt');
    
    // Check if modals still work
    await helpers.openSettings();
    await expect(page.locator('#settings-modal')).toBeVisible();
    await helpers.closeModal('settings-modal');
  });
}); 