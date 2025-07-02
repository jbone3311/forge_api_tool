/**
 * Comprehensive test runner for the modular dashboard system
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class TestRunner {
    constructor() {
        this.testResults = {
            passed: 0,
            failed: 0,
            total: 0,
            errors: [],
            warnings: [],
            coverage: {}
        };
        this.startTime = Date.now();
    }

    async runAllTests() {
        console.log('🚀 Starting comprehensive test suite for Forge API Tool Dashboard...\n');
        
        try {
            // Run Jest tests
            await this.runJestTests();
            
            // Run code quality checks
            await this.runCodeQualityChecks();
            
            // Run performance tests
            await this.runPerformanceTests();
            
            // Generate comprehensive report
            this.generateReport();
            
        } catch (error) {
            console.error('❌ Test suite failed:', error.message);
            this.testResults.errors.push(error.message);
            this.generateReport();
            process.exit(1);
        }
    }

    async runJestTests() {
        console.log('📋 Running Jest unit and integration tests...');
        
        try {
            const jestOutput = execSync('npm test -- --json --coverage', {
                cwd: process.cwd(),
                encoding: 'utf8',
                stdio: 'pipe'
            });
            
            const jestResults = JSON.parse(jestOutput);
            
            this.testResults.passed += jestResults.numPassedTests;
            this.testResults.failed += jestResults.numFailedTests;
            this.testResults.total += jestResults.numTotalTests;
            
            // Process coverage data
            if (jestResults.coverageMap) {
                this.testResults.coverage = jestResults.coverageMap;
            }
            
            console.log(`✅ Jest tests completed: ${jestResults.numPassedTests} passed, ${jestResults.numFailedTests} failed`);
            
        } catch (error) {
            console.error('❌ Jest tests failed:', error.message);
            this.testResults.errors.push(`Jest tests failed: ${error.message}`);
        }
    }

    async runCodeQualityChecks() {
        console.log('🔍 Running code quality checks...');
        
        // Check for duplicate functions
        await this.checkDuplicateFunctions();
        
        // Check for unused functions
        await this.checkUnusedFunctions();
        
        // Check for proper error handling
        await this.checkErrorHandling();
        
        // Check for proper logging
        await this.checkLogging();
    }

    async checkDuplicateFunctions() {
        console.log('  - Checking for duplicate function definitions...');
        
        const jsFiles = this.getJSFiles();
        const allFunctions = new Map();
        const duplicates = [];
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            const functionMatches = content.match(/function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g);
            
            if (functionMatches) {
                functionMatches.forEach(match => {
                    const funcName = match.replace(/function\s+/, '').replace(/\s*\(.*/, '');
                    
                    if (allFunctions.has(funcName)) {
                        duplicates.push({
                            name: funcName,
                            files: [allFunctions.get(funcName), file]
                        });
                    } else {
                        allFunctions.set(funcName, file);
                    }
                });
            }
        }
        
        if (duplicates.length > 0) {
            this.testResults.warnings.push(`Found ${duplicates.length} duplicate function definitions`);
            duplicates.forEach(dup => {
                console.log(`    ⚠️  Function "${dup.name}" defined in: ${dup.files.join(', ')}`);
            });
        } else {
            console.log('    ✅ No duplicate functions found');
        }
    }

    async checkUnusedFunctions() {
        console.log('  - Checking for unused functions...');
        
        const jsFiles = this.getJSFiles();
        const definedFunctions = new Set();
        const calledFunctions = new Set();
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            // Find function definitions
            const functionMatches = content.match(/function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g);
            if (functionMatches) {
                functionMatches.forEach(match => {
                    const funcName = match.replace(/function\s+/, '').replace(/\s*\(.*/, '');
                    definedFunctions.add(funcName);
                });
            }
            
            // Find function calls
            const callMatches = content.match(/([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g);
            if (callMatches) {
                callMatches.forEach(match => {
                    const funcName = match.replace(/\s*\(.*/, '');
                    if (funcName !== 'if' && funcName !== 'for' && funcName !== 'while') {
                        calledFunctions.add(funcName);
                    }
                });
            }
        }
        
        const unused = Array.from(definedFunctions).filter(func => !calledFunctions.has(func));
        
        if (unused.length > 0) {
            this.testResults.warnings.push(`Found ${unused.length} potentially unused functions`);
            unused.forEach(func => {
                console.log(`    ⚠️  Potentially unused function: ${func}`);
            });
        } else {
            console.log('    ✅ No unused functions detected');
        }
    }

    async checkErrorHandling() {
        console.log('  - Checking error handling patterns...');
        
        const jsFiles = this.getJSFiles();
        let hasGlobalErrorHandler = false;
        let hasTryCatchBlocks = 0;
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            // Check for global error handlers
            if (content.includes('window.onerror') || content.includes('addEventListener(\'error\'')) {
                hasGlobalErrorHandler = true;
            }
            
            // Count try-catch blocks
            const tryCatchMatches = content.match(/try\s*{/g);
            if (tryCatchMatches) {
                hasTryCatchBlocks += tryCatchMatches.length;
            }
        }
        
        if (!hasGlobalErrorHandler) {
            this.testResults.warnings.push('No global error handler found');
            console.log('    ⚠️  No global error handler found');
        } else {
            console.log('    ✅ Global error handler found');
        }
        
        console.log(`    ✅ Found ${hasTryCatchBlocks} try-catch blocks`);
    }

    async checkLogging() {
        console.log('  - Checking logging implementation...');
        
        const jsFiles = this.getJSFiles();
        let hasLogging = false;
        let hasErrorLogging = false;
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            if (content.includes('console.log') || content.includes('fetch(\'/api/log')) {
                hasLogging = true;
            }
            
            if (content.includes('console.error') || content.includes('log-js-error')) {
                hasErrorLogging = true;
            }
        }
        
        if (!hasLogging) {
            this.testResults.warnings.push('No logging implementation found');
            console.log('    ⚠️  No logging implementation found');
        } else {
            console.log('    ✅ Logging implementation found');
        }
        
        if (!hasErrorLogging) {
            this.testResults.warnings.push('No error logging implementation found');
            console.log('    ⚠️  No error logging implementation found');
        } else {
            console.log('    ✅ Error logging implementation found');
        }
    }

    async runPerformanceTests() {
        console.log('⚡ Running performance tests...');
        
        // Check file sizes
        await this.checkFileSizes();
        
        // Check for memory leaks
        await this.checkMemoryLeaks();
        
        // Check for performance anti-patterns
        await this.checkPerformanceAntiPatterns();
    }

    async checkFileSizes() {
        console.log('  - Checking file sizes...');
        
        const jsFiles = this.getJSFiles();
        const largeFiles = [];
        
        for (const file of jsFiles) {
            const stats = fs.statSync(file);
            const sizeKB = stats.size / 1024;
            
            if (sizeKB > 100) { // Files larger than 100KB
                largeFiles.push({ file, size: sizeKB });
            }
        }
        
        if (largeFiles.length > 0) {
            this.testResults.warnings.push(`Found ${largeFiles.length} large files`);
            largeFiles.forEach(({ file, size }) => {
                console.log(`    ⚠️  Large file: ${file} (${size.toFixed(1)}KB)`);
            });
        } else {
            console.log('    ✅ All files are reasonably sized');
        }
    }

    async checkMemoryLeaks() {
        console.log('  - Checking for potential memory leaks...');
        
        const jsFiles = this.getJSFiles();
        let hasIntervalCleanup = false;
        let hasEventCleanup = false;
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            if (content.includes('clearInterval') || content.includes('clearTimeout')) {
                hasIntervalCleanup = true;
            }
            
            if (content.includes('removeEventListener')) {
                hasEventCleanup = true;
            }
        }
        
        if (!hasIntervalCleanup) {
            this.testResults.warnings.push('No interval cleanup found');
            console.log('    ⚠️  No interval cleanup found');
        } else {
            console.log('    ✅ Interval cleanup found');
        }
        
        if (!hasEventCleanup) {
            this.testResults.warnings.push('No event listener cleanup found');
            console.log('    ⚠️  No event listener cleanup found');
        } else {
            console.log('    ✅ Event listener cleanup found');
        }
    }

    async checkPerformanceAntiPatterns() {
        console.log('  - Checking for performance anti-patterns...');
        
        const jsFiles = this.getJSFiles();
        let hasDebouncing = false;
        let hasThrottling = false;
        
        for (const file of jsFiles) {
            const content = fs.readFileSync(file, 'utf8');
            
            if (content.includes('debounce') || content.includes('setTimeout')) {
                hasDebouncing = true;
            }
            
            if (content.includes('throttle') || content.includes('requestAnimationFrame')) {
                hasThrottling = true;
            }
        }
        
        if (!hasDebouncing) {
            this.testResults.warnings.push('No debouncing implementation found');
            console.log('    ⚠️  No debouncing implementation found');
        } else {
            console.log('    ✅ Debouncing implementation found');
        }
        
        if (!hasThrottling) {
            this.testResults.warnings.push('No throttling implementation found');
            console.log('    ⚠️  No throttling implementation found');
        } else {
            console.log('    ✅ Throttling implementation found');
        }
    }

    getJSFiles() {
        const jsDir = path.join(process.cwd(), 'static', 'js');
        const files = [];
        
        const walkDir = (dir) => {
            const items = fs.readdirSync(dir);
            items.forEach(item => {
                const fullPath = path.join(dir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    walkDir(fullPath);
                } else if (item.endsWith('.js')) {
                    files.push(fullPath);
                }
            });
        };
        
        if (fs.existsSync(jsDir)) {
            walkDir(jsDir);
        }
        
        return files;
    }

    generateReport() {
        const endTime = Date.now();
        const duration = (endTime - this.startTime) / 1000;
        
        console.log('\n' + '='.repeat(60));
        console.log('📊 COMPREHENSIVE TEST REPORT');
        console.log('='.repeat(60));
        
        console.log(`⏱️  Total test duration: ${duration.toFixed(2)}s`);
        console.log(`📈 Test results: ${this.testResults.passed} passed, ${this.testResults.failed} failed, ${this.testResults.total} total`);
        
        const passRate = this.testResults.total > 0 ? (this.testResults.passed / this.testResults.total * 100).toFixed(1) : 0;
        console.log(`📊 Pass rate: ${passRate}%`);
        
        if (this.testResults.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.testResults.errors.forEach(error => {
                console.log(`  - ${error}`);
            });
        }
        
        if (this.testResults.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.testResults.warnings.forEach(warning => {
                console.log(`  - ${warning}`);
            });
        }
        
        // Generate recommendations
        this.generateRecommendations();
        
        console.log('\n' + '='.repeat(60));
        
        // Write report to file
        this.writeReportToFile();
    }

    generateRecommendations() {
        console.log('\n💡 RECOMMENDATIONS:');
        
        if (this.testResults.failed > 0) {
            console.log('  - Fix failing tests before deployment');
        }
        
        if (this.testResults.warnings.length > 0) {
            console.log('  - Address warnings to improve code quality');
        }
        
        if (this.testResults.passed / this.testResults.total < 0.8) {
            console.log('  - Increase test coverage to at least 80%');
        }
        
        console.log('  - Run tests before each deployment');
        console.log('  - Monitor performance in production');
        console.log('  - Set up continuous integration for automated testing');
    }

    writeReportToFile() {
        const reportPath = path.join(process.cwd(), 'test-report.json');
        const report = {
            timestamp: new Date().toISOString(),
            duration: (Date.now() - this.startTime) / 1000,
            results: this.testResults,
            summary: {
                status: this.testResults.failed > 0 ? 'FAILED' : 'PASSED',
                passRate: this.testResults.total > 0 ? (this.testResults.passed / this.testResults.total * 100).toFixed(1) : 0
            }
        };
        
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`📄 Detailed report written to: ${reportPath}`);
    }
}

// Run the test suite
const runner = new TestRunner();
runner.runAllTests().catch(error => {
    console.error('Test runner failed:', error);
    process.exit(1);
}); 