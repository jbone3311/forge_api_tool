import { test, expect } from '@playwright/test';

test.describe('Load Performance Tests', () => {
    test('Page loads within acceptable time', async ({ page }) => {
        const startTime = Date.now();
        await page.goto('http://localhost:4000');
        const loadTime = Date.now() - startTime;
        
        expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds
    });

    test('API responses are fast', async ({ request }) => {
        const startTime = Date.now();
        const response = await request.get('/api/status');
        const responseTime = Date.now() - startTime;
        
        expect(response.status()).toBe(200);
        expect(responseTime).toBeLessThan(500); // Should respond within 500ms
    });
});