#!/usr/bin/env node

/**
 * E2E Test Runner for Forge API Tool Dashboard
 * 
 * This script runs all Playwright E2E tests with proper setup and reporting.
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';

console.log('🚀 Starting E2E Test Suite for Forge API Tool Dashboard...\n');

// Check if server is running
function checkServer() {
  try {
    const response = execSync('curl -s -o /dev/null -w "%{http_code}" http://localhost:5000', { encoding: 'utf8' });
    return response.trim() === '200';
  } catch (error) {
    return false;
  }
}

// Start server if not running
function startServer() {
  console.log('📡 Starting Flask server...');
  try {
    execSync('python app.py > server.log 2>&1 &', { stdio: 'inherit' });
    console.log('⏳ Waiting for server to start...');
    
    // Wait for server to be ready
    let attempts = 0;
    while (!checkServer() && attempts < 30) {
      execSync('sleep 1', { stdio: 'ignore' });
      attempts++;
    }
    
    if (checkServer()) {
      console.log('✅ Server is running on http://localhost:5000');
      return true;
    } else {
      console.log('❌ Server failed to start');
      return false;
    }
  } catch (error) {
    console.log('❌ Failed to start server:', error.message);
    return false;
  }
}

// Run tests
function runTests() {
  console.log('\n🧪 Running E2E tests...\n');
  
  try {
    execSync('npx playwright test e2e/ --reporter=list --timeout=30000', { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    console.log('\n✅ All E2E tests completed successfully!');
    return true;
  } catch (error) {
    console.log('\n❌ Some E2E tests failed');
    return false;
  }
}

// Generate test report
function generateReport() {
  console.log('\n📊 Generating test report...');
  
  try {
    execSync('npx playwright show-report', { stdio: 'inherit' });
  } catch (error) {
    console.log('Could not open test report:', error.message);
  }
}

// Main execution
async function main() {
  const serverRunning = checkServer();
  
  if (!serverRunning) {
    console.log('🔍 Server not detected on http://localhost:5000');
    const started = startServer();
    if (!started) {
      console.log('\n❌ Cannot run tests without server. Please start the server manually:');
      console.log('   python app.py');
      process.exit(1);
    }
  } else {
    console.log('✅ Server already running on http://localhost:5000');
  }
  
  const testsPassed = runTests();
  
  if (testsPassed) {
    console.log('\n🎉 E2E test suite completed successfully!');
    generateReport();
  } else {
    console.log('\n💥 E2E test suite failed!');
    process.exit(1);
  }
}

// Handle cleanup
process.on('SIGINT', () => {
  console.log('\n🛑 Test run interrupted');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Test run terminated');
  process.exit(0);
});

// Run the main function
main().catch(error => {
  console.error('💥 Unexpected error:', error);
  process.exit(1);
}); 