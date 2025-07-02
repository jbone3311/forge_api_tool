#!/usr/bin/env node

/**
 * Test API Server for Forge API Tool Dashboard
 * 
 * Provides REST API endpoints for test management, results, and reporting.
 */

import express from 'express';
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.TEST_API_PORT || 4001;

// Middleware
app.use(express.json());
app.use(express.static('test-reports'));

// Test data storage
let testResults = {
    unit: [],
    e2e: [],
    integration: [],
    performance: []
};

let recentRuns = [];
let testStats = {
    total: 0,
    passed: 0,
    failed: 0,
    skipped: 0
};

// Load existing test data
function loadTestData() {
    try {
        const summaryPath = join(__dirname, 'test-reports', 'test-summary.json');
        if (existsSync(summaryPath)) {
            const data = JSON.parse(readFileSync(summaryPath, 'utf8'));
            testStats = data.testStats || testStats;
            recentRuns = data.recentRuns || recentRuns;
        }
    } catch (error) {
        console.log('No existing test data found, using defaults');
    }
}

// Save test data
function saveTestData() {
    const data = {
        timestamp: new Date().toISOString(),
        testStats,
        recentRuns,
        testResults
    };
    
    const summaryPath = join(__dirname, 'test-reports', 'test-summary.json');
    writeFileSync(summaryPath, JSON.stringify(data, null, 2));
}

// API Routes

// Get test dashboard data
app.get('/api/test-dashboard/data', (req, res) => {
    const dashboardData = {
        stats: testStats,
        recentRuns: recentRuns.slice(0, 10), // Last 10 runs
        testResults,
        coverage: getCoverageData(),
        performance: getPerformanceData()
    };
    
    res.json(dashboardData);
});

// Get test results by type
app.get('/api/test-results/:type', (req, res) => {
    const { type } = req.params;
    
    if (testResults[type]) {
        res.json(testResults[type]);
    } else {
        res.status(404).json({ error: 'Test type not found' });
    }
});

// Get test statistics
app.get('/api/test-stats', (req, res) => {
    res.json(testStats);
});

// Get recent test runs
app.get('/api/recent-runs', (req, res) => {
    res.json(recentRuns);
});

// Get coverage data
app.get('/api/coverage', (req, res) => {
    res.json(getCoverageData());
});

// Get performance data
app.get('/api/performance', (req, res) => {
    res.json(getPerformanceData());
});

// Run tests
app.post('/api/tests/run-all', async (req, res) => {
    try {
        console.log('Running all tests...');
        
        // Simulate test execution
        const runId = Date.now().toString();
        const startTime = Date.now();
        
        // Update test status
        updateTestStatus('running');
        
        // Simulate test execution time
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        const duration = Date.now() - startTime;
        
        // Generate mock results
        const results = generateMockResults();
        
        // Update test data
        updateTestResults(results);
        
        // Add to recent runs
        const run = {
            id: runId,
            timestamp: new Date().toISOString(),
            type: 'all',
            duration: `${(duration / 1000).toFixed(1)}s`,
            status: 'completed',
            results: results
        };
        
        recentRuns.unshift(run);
        if (recentRuns.length > 50) {
            recentRuns = recentRuns.slice(0, 50);
        }
        
        saveTestData();
        
        res.json({
            success: true,
            runId,
            duration: `${(duration / 1000).toFixed(1)}s`,
            results
        });
        
    } catch (error) {
        console.error('Error running tests:', error);
        res.status(500).json({ error: 'Failed to run tests' });
    }
});

// Run specific test type
app.post('/api/tests/run-unit', async (req, res) => {
    try {
        console.log('Running unit tests...');
        
        const runId = Date.now().toString();
        const startTime = Date.now();
        
        // Simulate unit test execution
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const duration = Date.now() - startTime;
        const results = generateMockUnitResults();
        
        updateTestResults({ unit: results });
        
        const run = {
            id: runId,
            timestamp: new Date().toISOString(),
            type: 'unit',
            duration: `${(duration / 1000).toFixed(1)}s`,
            status: 'completed',
            results: { unit: results }
        };
        
        recentRuns.unshift(run);
        saveTestData();
        
        res.json({
            success: true,
            runId,
            duration: `${(duration / 1000).toFixed(1)}s`,
            results: { unit: results }
        });
        
    } catch (error) {
        console.error('Error running unit tests:', error);
        res.status(500).json({ error: 'Failed to run unit tests' });
    }
});

app.post('/api/tests/run-e2e', async (req, res) => {
    try {
        console.log('Running E2E tests...');
        
        const runId = Date.now().toString();
        const startTime = Date.now();
        
        // Simulate E2E test execution
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        const duration = Date.now() - startTime;
        const results = generateMockE2EResults();
        
        updateTestResults({ e2e: results });
        
        const run = {
            id: runId,
            timestamp: new Date().toISOString(),
            type: 'e2e',
            duration: `${(duration / 1000).toFixed(1)}s`,
            status: 'completed',
            results: { e2e: results }
        };
        
        recentRuns.unshift(run);
        saveTestData();
        
        res.json({
            success: true,
            runId,
            duration: `${(duration / 1000).toFixed(1)}s`,
            results: { e2e: results }
        });
        
    } catch (error) {
        console.error('Error running E2E tests:', error);
        res.status(500).json({ error: 'Failed to run E2E tests' });
    }
});

app.post('/api/tests/run-integration', async (req, res) => {
    try {
        console.log('Running integration tests...');
        
        const runId = Date.now().toString();
        const startTime = Date.now();
        
        // Simulate integration test execution
        await new Promise(resolve => setTimeout(resolve, 4000));
        
        const duration = Date.now() - startTime;
        const results = generateMockIntegrationResults();
        
        updateTestResults({ integration: results });
        
        const run = {
            id: runId,
            timestamp: new Date().toISOString(),
            type: 'integration',
            duration: `${(duration / 1000).toFixed(1)}s`,
            status: 'completed',
            results: { integration: results }
        };
        
        recentRuns.unshift(run);
        saveTestData();
        
        res.json({
            success: true,
            runId,
            duration: `${(duration / 1000).toFixed(1)}s`,
            results: { integration: results }
        });
        
    } catch (error) {
        console.error('Error running integration tests:', error);
        res.status(500).json({ error: 'Failed to run integration tests' });
    }
});

app.post('/api/tests/run-performance', async (req, res) => {
    try {
        console.log('Running performance tests...');
        
        const runId = Date.now().toString();
        const startTime = Date.now();
        
        // Simulate performance test execution
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const duration = Date.now() - startTime;
        const results = generateMockPerformanceResults();
        
        updateTestResults({ performance: results });
        
        const run = {
            id: runId,
            timestamp: new Date().toISOString(),
            type: 'performance',
            duration: `${(duration / 1000).toFixed(1)}s`,
            status: 'completed',
            results: { performance: results }
        };
        
        recentRuns.unshift(run);
        saveTestData();
        
        res.json({
            success: true,
            runId,
            duration: `${(duration / 1000).toFixed(1)}s`,
            results: { performance: results }
        });
        
    } catch (error) {
        console.error('Error running performance tests:', error);
        res.status(500).json({ error: 'Failed to run performance tests' });
    }
});

// Get test reports
app.get('/api/test-reports', (req, res) => {
    const reportsDir = join(__dirname, 'test-reports');
    const reports = [];
    
    if (existsSync(reportsDir)) {
        const files = readdirSync(reportsDir);
        files.forEach(file => {
            if (file.endsWith('.json') || file.endsWith('.html')) {
                reports.push({
                    name: file,
                    type: file.split('.').pop(),
                    path: `/test-reports/${file}`,
                    size: getFileSize(join(reportsDir, file))
                });
            }
        });
    }
    
    res.json(reports);
});

// Export test data
app.get('/api/export/:format', (req, res) => {
    const { format } = req.params;
    const data = {
        timestamp: new Date().toISOString(),
        testStats,
        recentRuns,
        testResults,
        coverage: getCoverageData(),
        performance: getPerformanceData()
    };
    
    switch (format) {
        case 'json':
            res.setHeader('Content-Type', 'application/json');
            res.setHeader('Content-Disposition', 'attachment; filename=test-report.json');
            res.json(data);
            break;
        case 'csv':
            res.setHeader('Content-Type', 'text/csv');
            res.setHeader('Content-Disposition', 'attachment; filename=test-report.csv');
            res.send(convertToCSV(data));
            break;
        default:
            res.status(400).json({ error: 'Unsupported format' });
    }
});

// Helper functions

function updateTestStatus(status) {
    // Update test status in real-time
    console.log(`Test status: ${status}`);
}

function updateTestResults(results) {
    Object.assign(testResults, results);
    
    // Update test stats
    testStats = {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0
    };
    
    Object.values(testResults).forEach(typeResults => {
        typeResults.forEach(test => {
            testStats.total++;
            testStats[test.status]++;
        });
    });
}

function generateMockResults() {
    return {
        unit: generateMockUnitResults(),
        e2e: generateMockE2EResults(),
        integration: generateMockIntegrationResults(),
        performance: generateMockPerformanceResults()
    };
}

function generateMockUnitResults() {
    return [
        {
            name: 'Dashboard Structure Tests',
            status: 'passed',
            duration: '2.3s',
            description: 'Validates dashboard layout and component structure'
        },
        {
            name: 'UI Component Tests',
            status: 'passed',
            duration: '1.8s',
            description: 'Tests individual UI components and interactions'
        },
        {
            name: 'Error Handling Tests',
            status: 'passed',
            duration: '2.1s',
            description: 'Validates error handling and recovery mechanisms'
        },
        {
            name: 'Modular System Tests',
            status: 'passed',
            duration: '3.2s',
            description: 'Tests modular JavaScript system integration'
        }
    ];
}

function generateMockE2EResults() {
    return [
        {
            name: 'Basic UI Tests',
            status: 'passed',
            duration: '8.5s',
            description: 'Dashboard loading, layout, and basic interactions'
        },
        {
            name: 'Template Management',
            status: 'passed',
            duration: '12.3s',
            description: 'Template loading, selection, and management operations'
        },
        {
            name: 'Generation Workflow',
            status: 'passed',
            duration: '15.7s',
            description: 'Form validation, submission, and generation process'
        },
        {
            name: 'Error Handling',
            status: 'passed',
            duration: '10.2s',
            description: 'Network errors, API failures, and error recovery'
        }
    ];
}

function generateMockIntegrationResults() {
    return [
        {
            name: 'API Integration',
            status: 'passed',
            duration: '5.2s',
            description: 'API endpoint integration and response validation'
        },
        {
            name: 'Database Operations',
            status: 'passed',
            duration: '3.8s',
            description: 'Database operation flows and data persistence'
        },
        {
            name: 'File System Operations',
            status: 'passed',
            duration: '4.1s',
            description: 'File system operations and storage management'
        }
    ];
}

function generateMockPerformanceResults() {
    return [
        {
            name: 'Load Time Tests',
            status: 'passed',
            duration: '2.1s',
            description: 'Page load time and performance validation'
        },
        {
            name: 'Memory Usage',
            status: 'passed',
            duration: '1.5s',
            description: 'Memory usage patterns and optimization'
        },
        {
            name: 'Response Time',
            status: 'passed',
            duration: '3.2s',
            description: 'API response time and performance metrics'
        }
    ];
}

function getCoverageData() {
    return {
        total: {
            lines: { pct: 94.2 },
            functions: { pct: 89.4 },
            branches: { pct: 92.8 }
        },
        javascript: { pct: 94.2 },
        css: { pct: 87.5 },
        api: { pct: 96.8 },
        workflows: { pct: 91.3 }
    };
}

function getPerformanceData() {
    return {
        pageLoadTime: '1.2s',
        apiResponseTime: '245ms',
        memoryUsage: '45MB',
        testExecutionTime: '45.2s',
        uptime: '98%',
        testsPerMinute: 156
    };
}

function getFileSize(filePath) {
    try {
        const stats = readFileSync(filePath, { encoding: 'utf8' });
        return stats.length;
    } catch (error) {
        return 0;
    }
}

function convertToCSV(data) {
    const rows = [
        ['Timestamp', 'Test Type', 'Status', 'Duration', 'Description']
    ];
    
    Object.entries(data.testResults).forEach(([type, tests]) => {
        tests.forEach(test => {
            rows.push([
                new Date().toISOString(),
                type,
                test.status,
                test.duration,
                test.description
            ]);
        });
    });
    
    return rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
}

// Initialize and start server
loadTestData();

app.listen(PORT, () => {
    console.log(`🧪 Test API Server running on http://localhost:${PORT}`);
    console.log(`📊 Test Dashboard: http://localhost:${PORT}/test-dashboard.html`);
    console.log(`📋 Test Reports: http://localhost:${PORT}/test-reports/`);
});

export default app; 