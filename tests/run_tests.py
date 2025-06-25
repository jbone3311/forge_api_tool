#!/usr/bin/env python3
"""
Test runner for Forge API Tool
Runs all tests and provides a comprehensive report.
"""

import unittest
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all tests and return results."""
    # Discover all test files
    test_dir = project_root / "tests"
    loader = unittest.TestLoader()
    
    # Load all test modules
    test_modules = [
        'tests.test_wildcard_manager',
        'tests.test_config_handler', 
        'tests.test_image_analyzer',
        'tests.test_output_manager',
        'tests.test_integration'
    ]
    
    # Create test suite
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            module = __import__(module_name, fromlist=['*'])
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print(f"✓ Loaded {module_name}")
        except ImportError as e:
            print(f"✗ Failed to load {module_name}: {e}")
        except Exception as e:
            print(f"✗ Error loading {module_name}: {e}")
    
    # Run tests
    print(f"\n{'='*60}")
    print("RUNNING TESTS")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Create test runner with verbosity
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run tests
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Duration: {duration:.2f} seconds")
    
    if result.failures:
        print(f"\n{'='*60}")
        print("FAILURES")
        print(f"{'='*60}")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print(f"\n{'='*60}")
        print("ERRORS")
        print(f"{'='*60}")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    # Return success/failure
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n{'='*60}")
        print("🎉 ALL TESTS PASSED! 🎉")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("❌ SOME TESTS FAILED ❌")
        print(f"{'='*60}")
    
    return success

def run_specific_test(test_name):
    """Run a specific test module or class."""
    loader = unittest.TestLoader()
    
    if test_name.startswith('tests.'):
        # Full module path
        try:
            module = __import__(test_name, fromlist=['*'])
            suite = loader.loadTestsFromModule(module)
        except ImportError as e:
            print(f"Error importing {test_name}: {e}")
            return False
    else:
        # Try to find the test
        test_dir = project_root / "tests"
        suite = loader.discover(str(test_dir), pattern=f"*{test_name}*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running specific test: {test_name}")
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 