#!/usr/bin/env python3
"""
Comprehensive test suite for Forge API Tool.
Organized by test type: unit, integration, functional, debug
"""

import sys
import os
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test_category(category: str, test_dir: str) -> dict:
    """Run all tests in a specific category."""
    print(f"\n{'='*60}")
    print(f"TESTING {category.upper()}")
    print(f"{'='*60}")
    
    results = {}
    test_path = Path(test_dir)
    
    if not test_path.exists():
        print(f"⚠️  Test directory {test_dir} not found")
        return results
    
    # Find all test files in the category
    test_files = list(test_path.glob("test_*.py"))
    
    if not test_files:
        print(f"⚠️  No test files found in {test_dir}")
        return results
    
    for test_file in sorted(test_files):
        test_name = test_file.stem
        print(f"\nRunning {test_name}...")
        
        try:
            # Set up the Python path for this test
            test_dir_path = test_file.parent
            project_root = test_dir_path.parent.parent
            
            # Create a temporary environment for the test
            import subprocess
            import sys
            
            # Run the test as a subprocess with proper path setup
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{project_root}:{env.get('PYTHONPATH', '')}"
            
            result = subprocess.run([
                sys.executable, str(test_file)
            ], 
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=30)
            
            if result.returncode == 0:
                results[test_name] = "✓ PASS"
                print(f"✓ {test_name}: PASS")
                if result.stdout.strip():
                    print(f"  Output: {result.stdout.strip()}")
            else:
                results[test_name] = f"✗ FAIL: {result.stderr.strip() if result.stderr else 'Unknown error'}"
                print(f"✗ {test_name}: FAIL")
                if result.stderr.strip():
                    print(f"  Error: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            results[test_name] = "✗ FAIL: Timeout"
            print(f"✗ {test_name}: FAIL - Timeout")
        except Exception as e:
            results[test_name] = f"✗ FAIL: {e}"
            print(f"✗ {test_name}: FAIL - {e}")
    
    return results

def run_comprehensive_tests():
    """Run all tests in organized categories."""
    print("FORGE API TOOL - COMPREHENSIVE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_results = {}
    
    # Test categories
    test_categories = [
        ("UNIT TESTS", "tests/unit"),
        ("INTEGRATION TESTS", "tests/integration"), 
        ("FUNCTIONAL TESTS", "tests/functional"),
        ("DEBUG TESTS", "tests/debug")
    ]
    
    for category_name, test_dir in test_categories:
        category_results = run_test_category(category_name, test_dir)
        all_results[category_name] = category_results
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category_name, category_results in all_results.items():
        print(f"\n{category_name}:")
        for test_name, result in category_results.items():
            print(f"  {test_name}: {result}")
            total_tests += 1
            if "✓ PASS" in result:
                passed_tests += 1
            elif "✗ FAIL" in result:
                failed_tests += 1
    
    print(f"\nSUMMARY:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Warnings: {total_tests - passed_tests - failed_tests}")
    
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} TESTS FAILED ❌")
    else:
        print(f"\n✅ ALL TESTS PASSED ✅")
    
    return failed_tests == 0

def run_quick_tests():
    """Run only essential tests for quick validation."""
    print("Running quick validation tests...")
    
    # Test core imports
    try:
        from tests.unit.test_imports import test_imports
        success = test_imports()
        if success:
            print("✅ Core imports working")
        else:
            print("❌ Core imports failed")
            return False
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    # Test basic functionality
    try:
        from core.config_handler import config_handler
        configs = config_handler.list_configs()
        print(f"✅ Config handler working ({len(configs)} configs found)")
    except Exception as e:
        print(f"❌ Config handler failed: {e}")
        return False
    
    return True

def main():
    """Main test runner with command line options."""
    parser = argparse.ArgumentParser(description="Forge API Tool Test Suite")
    parser.add_argument("--quick", action="store_true", help="Run only quick validation tests")
    parser.add_argument("--category", choices=["unit", "integration", "functional", "debug"], 
                       help="Run tests from specific category only")
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
    elif args.category:
        category_map = {
            "unit": "tests/unit",
            "integration": "tests/integration", 
            "functional": "tests/functional",
            "debug": "tests/debug"
        }
        test_dir = category_map[args.category]
        results = run_test_category(args.category.upper(), test_dir)
        success = all("✓ PASS" in result for result in results.values())
    else:
        success = run_comprehensive_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 