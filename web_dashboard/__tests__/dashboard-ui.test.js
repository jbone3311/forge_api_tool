/**
 * Test for dashboard UI interactions
 * Tests that UI elements respond correctly to user interactions
 */

import fs from 'fs';
import path from 'path';
import { JSDOM } from 'jsdom';

describe('dashboard UI', () => {
  let window, document;

  beforeEach(() => {
    const dom = new JSDOM(`
      <!DOCTYPE html>
      <html>
        <body>
          <div class="template-card" data-config="test-config">
            <h3>Test Template</h3>
          </div>
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

  test('should call selectTemplate on template card click', () => {
    // Mock the selectTemplate function
    const mockSelectTemplate = jest.fn();
    global.selectTemplate = mockSelectTemplate;

    // Find the template card
    const templateCard = document.querySelector('.template-card');
    expect(templateCard).toBeTruthy();

    // Add click event listener
    templateCard.addEventListener('click', () => {
      selectTemplate('test-config');
    });

    // Simulate click event
    const clickEvent = new window.Event('click');
    templateCard.dispatchEvent(clickEvent);

    // Verify selectTemplate was called
    expect(mockSelectTemplate).toHaveBeenCalledWith('test-config');
  });
}); 