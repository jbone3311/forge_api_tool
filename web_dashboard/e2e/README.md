# E2E Test Suite for Forge API Tool Dashboard

This directory contains comprehensive end-to-end tests for the Forge API Tool Dashboard using Playwright.

## 🧪 Test Coverage

### 1. **Basic UI Tests** (`basic-ui.test.js`)
- Dashboard loading and structure
- Sidebar resizing functionality
- Template card display
- Generation settings form accessibility
- Settings modal functionality
- Notification system
- Responsive design
- Keyboard navigation

### 2. **Template Management Tests** (`template-management.test.js`)
- Template sidebar loading
- Template card information display
- Template selection and form updates
- Template action buttons
- Create template modal
- Template refresh functionality
- Template card interactions
- Accessibility features

### 3. **Generation Workflow Tests** (`generation-workflow.test.js`)
- Generation settings form structure
- Prompt input validation
- Negative prompt handling
- Template selection dropdown
- Seed input validation
- Form validation
- Settings actions (reset/save)
- Progress tracking
- Form submission workflow
- Keyboard navigation

### 4. **Error Handling Tests** (`error-handling.test.js`)
- Network error handling
- API timeout handling
- Invalid form input validation
- Server error (500) handling
- Authentication error handling
- Malformed JSON response handling
- Error notification dismissal
- Error state UI reflection
- Error recovery
- Graceful degradation

## 🚀 Running Tests

### Prerequisites
1. **Install dependencies:**
   ```bash
   npm install
   npx playwright install
   ```

2. **Start the Flask server:**
   ```bash
   python app.py
   ```

### Test Commands

#### Run all E2E tests (recommended)
```bash
npm run test:e2e
```
This will:
- Check if server is running
- Start server if needed
- Run all E2E tests
- Generate a test report

#### Run specific test files
```bash
# Basic UI tests only
npx playwright test e2e/basic-ui.test.js

# Template management tests only
npx playwright test e2e/template-management.test.js

# Generation workflow tests only
npx playwright test e2e/generation-workflow.test.js

# Error handling tests only
npx playwright test e2e/error-handling.test.js
```

#### Run tests with UI (for debugging)
```bash
npm run test:e2e:ui
```

#### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

#### Run all tests (Jest + E2E)
```bash
npm run test:all
```

## 📊 Test Reports

After running tests, you can view detailed reports:

```bash
npx playwright show-report
```

This opens an HTML report with:
- Test results and screenshots
- Video recordings of failed tests
- Performance metrics
- Error details and stack traces

## 🛠️ Test Structure

### Helper Functions (`helpers.js`)
The `DashboardHelpers` class provides common utilities:
- `waitForPageLoad()` - Wait for page to be ready
- `waitForElement()` - Wait for specific elements
- `fillField()` - Fill form fields
- `clickButton()` - Click buttons
- `openSettings()` - Open settings modal
- `closeModal()` - Close modals
- `waitForNotification()` - Wait for notifications
- `mockApiResponse()` - Mock API responses

### Test Organization
Each test file follows this pattern:
```javascript
import { test, expect } from '@playwright/test';
import { DashboardHelpers } from './helpers.js';

test.describe('Test Category', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new DashboardHelpers(page);
    await page.goto('http://localhost:4000');
    await helpers.waitForPageLoad();
  });

  test('specific test case', async ({ page }) => {
    // Test implementation
  });
});
```

## 🔧 Configuration

### Playwright Configuration
Tests use Playwright's default configuration. You can customize by creating `playwright.config.js`:

```javascript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  use: {
    baseURL: 'http://localhost:4000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' }
    }
  ]
});
```

### Environment Variables
- `BASE_URL` - Override the default test URL (default: http://localhost:4000)
- `HEADLESS` - Run tests in headless mode (default: true)

## 🐛 Debugging Tests

### Debug Mode
Run tests in debug mode to step through:
```bash
npx playwright test --debug
```

### UI Mode
Use Playwright's UI for interactive debugging:
```bash
npm run test:e2e:ui
```

### Screenshots and Videos
Failed tests automatically capture:
- Screenshots at the time of failure
- Video recordings of the entire test
- Trace files for detailed debugging

### Console Logs
Tests include console logging for debugging:
```javascript
console.log('Debug information:', someValue);
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: python app.py &
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## 🎯 Best Practices

### Writing Tests
1. **Use descriptive test names** that explain what is being tested
2. **Keep tests independent** - each test should be able to run alone
3. **Use helper functions** for common operations
4. **Mock external dependencies** when appropriate
5. **Test both success and failure scenarios**
6. **Include accessibility testing**

### Test Data
- Tests should not depend on specific data
- Use mock data or create test data as needed
- Clean up any test data after tests

### Performance
- Tests should complete within reasonable time (under 30 seconds each)
- Use appropriate timeouts
- Avoid unnecessary waits

## 🚨 Troubleshooting

### Common Issues

#### Server Not Running
```
Error: page.goto: net::ERR_CONNECTION_REFUSED
```
**Solution:** Start the Flask server with `python app.py`

#### Tests Timing Out
```
Error: Timeout 30000ms exceeded
```
**Solution:** Increase timeout or check if server is responding slowly

#### Element Not Found
```
Error: locator.click: Target closed
```
**Solution:** Add proper waits or check if element selectors are correct

#### Browser Issues
```
Error: Browser not found
```
**Solution:** Run `npx playwright install` to install browsers

### Getting Help
1. Check the test report for detailed error information
2. Run tests in headed mode to see what's happening
3. Use debug mode to step through failing tests
4. Check browser console for JavaScript errors
5. Verify server logs for backend issues

## 📝 Contributing

When adding new tests:
1. Follow the existing test structure
2. Use helper functions for common operations
3. Add appropriate error handling
4. Include both positive and negative test cases
5. Update this README if adding new test categories
6. Ensure tests are fast and reliable

## 🎉 Success Metrics

A successful test run should show:
- ✅ All tests passing
- ✅ No flaky tests
- ✅ Reasonable execution time (< 5 minutes total)
- ✅ Good coverage of user workflows
- ✅ Proper error handling validation 