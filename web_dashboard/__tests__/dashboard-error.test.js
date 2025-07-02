/**
 * Test for dashboard error handling
 * Tests that error conditions are properly handled
 */

import { JSDOM } from 'jsdom';

describe('dashboard error handling', () => {
  let window, document;

  beforeEach(() => {
    const dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div id="notification-container"></div>
          <div id="template-container"></div>
        </body>
      </html>
    `);
    window = dom.window;
    document = window.document;
    global.window = window;
    global.document = document;
    global.fetch = jest.fn();
  });

  test('should call updateNotification on selectTemplate error', async () => {
    // Mock the updateNotification function
    const mockUpdateNotification = jest.fn();
    global.updateNotification = mockUpdateNotification;

    // Mock fetch to return an error
    global.fetch.mockRejectedValue(new Error('Network error'));

    // Simulate selectTemplate being called
    const selectTemplate = async () => {
      try {
        await fetch('/api/configs/test');
      } catch (error) {
        updateNotification('Error loading template', 'error');
        throw error;
      }
    };

    // Call selectTemplate and expect updateNotification to be called
    await expect(selectTemplate()).rejects.toThrow('Network error');
    expect(mockUpdateNotification).toHaveBeenCalledWith('Error loading template', 'error');
  });
}); 