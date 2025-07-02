// E2E Test Helpers
export class DashboardHelpers {
  constructor(page) {
    this.page = page;
  }

  // Wait for page to be ready
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForSelector('h1', { timeout: 10000 });
  }

  // Wait for element to be visible
  async waitForElement(selector, timeout = 5000) {
    await this.page.waitForSelector(selector, { state: 'visible', timeout });
  }

  // Fill a form field
  async fillField(selector, value) {
    await this.page.fill(selector, value);
  }

  // Click a button
  async clickButton(selector) {
    await this.page.click(selector);
  }

  // Open settings modal
  async openSettings() {
    await this.clickButton('button[onclick="openSettingsModal()"]');
    await this.waitForElement('#settings-modal');
  }

  // Close modal
  async closeModal(modalId) {
    await this.clickButton(`#${modalId} .close-btn`);
    await this.page.waitForSelector(`#${modalId}`, { state: 'hidden' });
  }

  // Switch to a settings tab
  async switchSettingsTab(tabName) {
    await this.clickButton(`[onclick="switchSettingsTab('${tabName}')"]`);
    await this.waitForElement(`#${tabName}-settings-tab.active`);
  }

  // Get notification text
  async getNotificationText() {
    const notification = await this.page.locator('#notification-container .notification');
    return await notification.textContent();
  }

  // Wait for notification to appear
  async waitForNotification(timeout = 5000) {
    await this.page.waitForSelector('#notification-container .notification', { timeout });
  }

  // Check if element has class
  async hasClass(selector, className) {
    const element = await this.page.locator(selector);
    return await element.hasClass(className);
  }

  // Get element text
  async getText(selector) {
    const element = await this.page.locator(selector);
    return await element.textContent();
  }

  // Check if element is visible
  async isVisible(selector) {
    const element = await this.page.locator(selector);
    return await element.isVisible();
  }

  // Wait for API status to update
  async waitForApiStatus(expectedStatus = 'connected') {
    await this.page.waitForFunction(
      (status) => {
        const statusElement = document.querySelector('#api-status .status-text');
        return statusElement && statusElement.textContent.toLowerCase().includes(status);
      },
      expectedStatus,
      { timeout: 10000 }
    );
  }

  // Mock API responses for testing
  async mockApiResponse(url, response) {
    await this.page.route(url, route => {
      route.fulfill({ 
        status: 200, 
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }
} 