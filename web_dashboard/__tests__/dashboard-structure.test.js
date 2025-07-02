/**
 * Test for dashboard.js structure
 * Tests that the dashboard.js file has proper structure
 */

import fs from 'fs';
import path from 'path';

describe('dashboard.js structure', () => {
  test('should not have duplicate function names', () => {
    const dashboardPath = path.join(process.cwd(), 'static', 'js', 'dashboard.js');
    
    // Check if file exists
    if (!fs.existsSync(dashboardPath)) {
      console.warn('dashboard.js not found, skipping test');
      return;
    }
    
    const content = fs.readFileSync(dashboardPath, 'utf8');
    
    // Extract function names using regex
    const functionRegex = /function\s+(\w+)\s*\(/g;
    const arrowFunctionRegex = /const\s+(\w+)\s*=\s*\(/g;
    const methodRegex = /(\w+)\s*:\s*function\s*\(/g;
    
    const functions = [];
    let match;
    
    // Find regular functions
    while ((match = functionRegex.exec(content)) !== null) {
      functions.push(match[1]);
    }
    
    // Find arrow functions
    while ((match = arrowFunctionRegex.exec(content)) !== null) {
      functions.push(match[1]);
    }
    
    // Find object methods
    while ((match = methodRegex.exec(content)) !== null) {
      functions.push(match[1]);
    }
    
    // Check for duplicates
    const duplicates = functions.filter((item, index) => functions.indexOf(item) !== index);
    
    expect(duplicates).toHaveLength(0);
  });
}); 