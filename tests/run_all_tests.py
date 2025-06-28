#!/usr/bin/env python3
"""
Comprehensive test runner for the Forge API Tool.
Runs all unit, integration, and functional tests.
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def run_all_tests():
    """Run all tests and return results."""
    print("🧪 Forge API Tool - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test categories
    test_categories = {
        'Unit Tests': [
            'tests.unit.test_config_handler',
            'tests.unit.test_image_analyzer',
            'tests.unit.test_output_manager',
            'tests.unit.test_wildcard_manager',
            'tests.unit.test_imports'
        ],
        'Integration Tests': [
            'tests.integration.test_api_comprehensive',
            'tests.integration.test_api_simple',
            'tests.integration.test_endpoint_coverage',
            'tests.integration.test_error_handling',
            'tests.integration.test_forge_api',
            'tests.integration.test_forge_direct',
            'tests.integration.test_forge_endpoints',
            'tests.integration.test_integration',
            'tests.integration.test_performance',
            'tests.integration.test_permissions',
            'tests.integration.test_image_analysis_endpoints'
        ],
        'Functional Tests': [
            'tests.functional.test_completed_prompts',
            'tests.functional.test_generation',
            'tests.functional.test_preview_wildcards',
            'tests.functional.test_status_indicators',
            'tests.functional.test_template_loading',
            'tests.functional.test_template_prompt_loading',
            'tests.functional.test_templates',
            'tests.functional.test_image_analysis_frontend'
        ]
    }
    
    # Add tests to suite
    total_tests = 0
    for category, test_modules in test_categories.items():
        print(f"📋 Loading {category}...")
        category_tests = 0
        
        for module_name in test_modules:
            try:
                # Load the test module
                module = __import__(module_name, fromlist=[''])
                
                # Add all tests from the module
                module_suite = loader.loadTestsFromModule(module)
                suite.addTest(module_suite)
                
                # Count tests in this module
                module_test_count = module_suite.countTestCases()
                category_tests += module_test_count
                total_tests += module_test_count
                
                print(f"  ✅ {module_name}: {module_test_count} tests")
                
            except ImportError as e:
                print(f"  ❌ {module_name}: Import failed - {e}")
            except Exception as e:
                print(f"  ❌ {module_name}: Loading failed - {e}")
        
        print(f"  📊 {category}: {category_tests} tests loaded")
        print()
    
    print(f"🎯 Total tests loaded: {total_tests}")
    print("=" * 60)
    print()
    
    # Run tests
    start_time = time.time()
    
    # Create test runner with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run the test suite
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print()
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Duration: {duration:.2f} seconds")
    print()
    
    # Print detailed results
    if result.failures:
        print("❌ FAILURES:")
        print("-" * 30)
        for test, traceback in result.failures:
            print(f"Test: {test}")
            print(f"Traceback:\n{traceback}")
            print()
    
    if result.errors:
        print("🚨 ERRORS:")
        print("-" * 30)
        for test, traceback in result.errors:
            print(f"Test: {test}")
            print(f"Traceback:\n{traceback}")
            print()
    
    # Print success rate
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"✅ Success Rate: {success_rate:.1f}%")
    
    # Return appropriate exit code
    if result.failures or result.errors:
        print("❌ Some tests failed!")
        return 1
    else:
        print("🎉 All tests passed!")
        return 0


def run_specific_category(category):
    """Run tests from a specific category."""
    categories = {
        'unit': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unit'),
        'integration': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'integration'), 
        'functional': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'functional')
    }
    
    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return 1
    
    print(f"🧪 Running {category} tests...")
    
    # Create test suite for specific category
    loader = unittest.TestLoader()
    
    # Add the category directory to Python path
    category_path = categories[category]
    if category_path not in sys.path:
        sys.path.insert(0, category_path)
    
    # Discover tests in the category directory
    suite = loader.discover(category_path, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if not (result.failures or result.errors) else 1


def run_specific_test(test_name):
    """Run a specific test."""
    print(f"🧪 Running specific test: {test_name}")
    
    # Create test suite for specific test
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    # Run test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if not (result.failures or result.errors) else 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Forge API Tool tests')
    parser.add_argument('--category', '-c', choices=['unit', 'integration', 'functional'],
                       help='Run tests from a specific category')
    parser.add_argument('--test', '-t', help='Run a specific test')
    parser.add_argument('--list', '-l', action='store_true', help='List all available tests')
    
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available test categories:")
        print("  unit - Unit tests for individual components")
        print("  integration - Integration tests for API endpoints")
        print("  functional - Functional tests for user workflows")
        print()
        print("📋 Available test modules:")
        
        # List all test modules
        test_modules = [
            'tests.unit.test_config_handler',
            'tests.unit.test_image_analyzer', 
            'tests.unit.test_output_manager',
            'tests.unit.test_wildcard_manager',
            'tests.unit.test_imports',
            'tests.integration.test_api_comprehensive',
            'tests.integration.test_api_simple',
            'tests.integration.test_endpoint_coverage',
            'tests.integration.test_error_handling',
            'tests.integration.test_forge_api',
            'tests.integration.test_forge_direct',
            'tests.integration.test_forge_endpoints',
            'tests.integration.test_integration',
            'tests.integration.test_performance',
            'tests.integration.test_permissions',
            'tests.integration.test_image_analysis_endpoints',
            'tests.functional.test_completed_prompts',
            'tests.functional.test_generation',
            'tests.functional.test_preview_wildcards',
            'tests.functional.test_status_indicators',
            'tests.functional.test_template_loading',
            'tests.functional.test_template_prompt_loading',
            'tests.functional.test_templates',
            'tests.functional.test_image_analysis_frontend'
        ]
        
        for module in test_modules:
            print(f"  {module}")
        
        sys.exit(0)
    
    if args.category:
        sys.exit(run_specific_category(args.category))
    elif args.test:
        sys.exit(run_specific_test(args.test))
    else:
        sys.exit(run_all_tests()) 