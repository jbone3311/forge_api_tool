import { test, expect } from '@playwright/test';

test.describe('API Integration Tests', () => {
    test('API endpoints respond correctly', async ({ request }) => {
        const response = await request.get('/api/status');
        expect(response.status()).toBe(200);
        
        const data = await response.json();
        expect(data).toHaveProperty('status');
    });

    test('Database operations work correctly', async ({ request }) => {
        // Test database integration
        const response = await request.post('/api/configs', {
            data: {
                name: 'Test Config',
                description: 'Test configuration'
            }
        });
        expect(response.status()).toBe(201);
    });

    test('File system operations work correctly', async ({ request }) => {
        // Test file system integration
        const response = await request.get('/api/outputs');
        expect(response.status()).toBe(200);
    });
});