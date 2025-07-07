#!/usr/bin/env python3
"""
Comprehensive test runner for the Forge API Tool.
Runs all unit, functional, and stress tests with detailed reporting.
"""

import os
import sys
import time
import subprocess
import unittest
from pathlib import Path
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_tests_with_pytest(test_path, test_type="unit"):
    """Run tests using pytest with detailed output."""
    print(f"\n{'='*60}")
    print(f"Running {test_type.upper()} tests: {test_path}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("\nSTDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        return result.returncode == 0, duration
        
    except subprocess.TimeoutExpired:
        print(f"❌ {test_type} tests timed out after 5 minutes")
        return False, 300
    except Exception as e:
        print(f"❌ Error running {test_type} tests: {e}")
        return False, 0


def run_tests_with_unittest(test_path, test_type="unit"):
    """Run tests using unittest with detailed output."""
    print(f"\n{'='*60}")
    print(f"Running {test_type.upper()} tests: {test_path}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Discover and run tests
        loader = unittest.TestLoader()
        suite = loader.discover(test_path, pattern="test_*.py")
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"\n{test}:")
                print(traceback)
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"\n{test}:")
                print(traceback)
        
        return len(result.failures) == 0 and len(result.errors) == 0, duration
        
    except Exception as e:
        print(f"❌ Error running {test_type} tests: {e}")
        return False, 0


def run_cli_tests():
    """Run CLI-specific tests."""
    print(f"\n{'='*60}")
    print("Running CLI TESTS")
    print(f"{'='*60}")
    
    cli_tests = [
        ("tests/unit/test_cli.py", "CLI Unit"),
        ("tests/functional/test_cli_integration.py", "CLI Integration"),
        ("tests/stress/test_stress_performance.py", "CLI Stress")
    ]
    
    results = []
    
    for test_path, test_name in cli_tests:
        if os.path.exists(test_path):
            success, duration = run_tests_with_unittest(test_path, test_name)
            results.append((test_name, success, duration))
        else:
            print(f"⚠️  Test file not found: {test_path}")
            results.append((test_name, False, 0))
    
    return results


def run_core_tests():
    """Run core module tests."""
    print(f"\n{'='*60}")
    print("Running CORE MODULE TESTS")
    print(f"{'='*60}")
    
    core_tests = [
        ("tests/unit/test_config_handler.py", "Config Handler"),
        ("tests/unit/test_image_analyzer.py", "Image Analyzer"),
        ("tests/unit/test_imports.py", "Imports")
    ]
    
    results = []
    
    for test_path, test_name in core_tests:
        if os.path.exists(test_path):
            success, duration = run_tests_with_unittest(test_path, test_name)
            results.append((test_name, success, duration))
        else:
            print(f"⚠️  Test file not found: {test_path}")
            results.append((test_name, False, 0))
    
    return results


def run_web_dashboard_tests():
    """Run web dashboard tests."""
    print(f"\n{'='*60}")
    print("Running WEB DASHBOARD TESTS")
    print(f"{'='*60}")
    
    web_tests = [
        ("web_dashboard/__tests__", "Web Dashboard Unit"),
        ("web_dashboard/e2e", "Web Dashboard E2E")
    ]
    
    results = []
    
    for test_path, test_name in web_tests:
        if os.path.exists(test_path):
            success, duration = run_tests_with_pytest(test_path, test_name)
            results.append((test_name, success, duration))
        else:
            print(f"⚠️  Test directory not found: {test_path}")
            results.append((test_name, False, 0))
    
    return results


def run_stress_tests():
    """Run stress and performance tests."""
    print(f"\n{'='*60}")
    print("Running STRESS AND PERFORMANCE TESTS")
    print(f"{'='*60}")
    
    stress_tests = [
        ("tests/stress", "Stress Tests")
    ]
    
    results = []
    
    for test_path, test_name in stress_tests:
        if os.path.exists(test_path):
            success, duration = run_tests_with_unittest(test_path, test_name)
            results.append((test_name, success, duration))
        else:
            print(f"⚠️  Test directory not found: {test_path}")
            results.append((test_name, False, 0))
    
    return results


def generate_test_report(all_results):
    """Generate a comprehensive test report."""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST REPORT")
    print(f"{'='*80}")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success, _ in all_results if success)
    failed_tests = total_tests - passed_tests
    total_duration = sum(duration for _, _, duration in all_results)
    
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print()
    
    print("DETAILED RESULTS:")
    print("-" * 80)
    
    for test_name, success, duration in all_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<10} {test_name:<30} {duration:>8.2f}s")
    
    print()
    
    if failed_tests > 0:
        print("FAILED TESTS:")
        print("-" * 40)
        for test_name, success, duration in all_results:
            if not success:
                print(f"❌ {test_name}")
    
    print(f"\n{'='*80}")
    
    return passed_tests == total_tests


def main():
    """Main test runner function."""
    print("🚀 Starting Comprehensive Test Suite for Forge API Tool")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    all_results = []
    
    # Run CLI tests
    cli_results = run_cli_tests()
    all_results.extend(cli_results)
    
    # Run core module tests
    core_results = run_core_tests()
    all_results.extend(core_results)
    
    # Run web dashboard tests
    web_results = run_web_dashboard_tests()
    all_results.extend(web_results)
    
    # Run stress tests
    stress_results = run_stress_tests()
    all_results.extend(stress_results)
    
    # Generate report
    overall_success = generate_test_report(all_results)
    
    # Exit with appropriate code
    if overall_success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 