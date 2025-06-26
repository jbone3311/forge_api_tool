#!/usr/bin/env python3
"""
Comprehensive test runner for Forge API Tool
"""

import sys
import os
import json
import traceback
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all core module imports."""
    print("=" * 60)
    print("TESTING IMPORTS")
    print("=" * 60)
    
    results = {}
    
    try:
        from core.config_handler import config_handler
        results['config_handler'] = "✓ PASS"
        print("✓ config_handler imported successfully")
    except Exception as e:
        results['config_handler'] = f"✗ FAIL: {e}"
        print(f"✗ config_handler import failed: {e}")
    
    try:
        from core.forge_api import forge_api_client
        results['forge_api'] = "✓ PASS"
        print("✓ forge_api_client imported successfully")
    except Exception as e:
        results['forge_api'] = f"✗ FAIL: {e}"
        print(f"✗ forge_api_client import failed: {e}")
    
    try:
        from core.centralized_logger import centralized_logger
        results['centralized_logger'] = "✓ PASS"
        print("✓ centralized_logger imported successfully")
    except Exception as e:
        results['centralized_logger'] = f"✗ FAIL: {e}"
        print(f"✗ centralized_logger import failed: {e}")
    
    try:
        from core.output_manager import output_manager
        results['output_manager'] = "✓ PASS"
        print("✓ output_manager imported successfully")
    except Exception as e:
        results['output_manager'] = f"✗ FAIL: {e}"
        print(f"✗ output_manager import failed: {e}")
    
    try:
        from core.job_queue import job_queue
        results['job_queue'] = "✓ PASS"
        print("✓ job_queue imported successfully")
    except Exception as e:
        results['job_queue'] = f"✗ FAIL: {e}"
        print(f"✗ job_queue import failed: {e}")
    
    try:
        from core.batch_runner import batch_runner
        results['batch_runner'] = "✓ PASS"
        print("✓ batch_runner imported successfully")
    except Exception as e:
        results['batch_runner'] = f"✗ FAIL: {e}"
        print(f"✗ batch_runner import failed: {e}")
    
    return results

def test_config_handler():
    """Test config handler functionality."""
    print("\n" + "=" * 60)
    print("TESTING CONFIG HANDLER")
    print("=" * 60)
    
    results = {}
    
    try:
        from core.config_handler import config_handler
        
        # Test listing configs
        configs = config_handler.list_configs()
        results['list_configs'] = f"✓ PASS: Found {len(configs)} configs"
        print(f"✓ list_configs: Found {len(configs)} configs")
        
        # Test loading a config if available
        if configs:
            config_name = configs[0]
            config = config_handler.load_config(config_name)
            results['load_config'] = f"✓ PASS: Loaded {config_name}"
            print(f"✓ load_config: Loaded {config_name}")
        else:
            results['load_config'] = "⚠ SKIP: No configs available"
            print("⚠ load_config: No configs available")
        
    except Exception as e:
        results['config_handler'] = f"✗ FAIL: {e}"
        print(f"✗ config_handler test failed: {e}")
        traceback.print_exc()
    
    return results

def test_forge_api():
    """Test Forge API functionality."""
    print("\n" + "=" * 60)
    print("TESTING FORGE API")
    print("=" * 60)
    
    results = {}
    
    try:
        from core.forge_api import forge_api_client
        
        # Test connection
        connected = forge_api_client.test_connection()
        if connected:
            results['connection'] = "✓ PASS: Connected to Forge API"
            print("✓ connection: Connected to Forge API")
        else:
            results['connection'] = "⚠ WARN: Cannot connect to Forge API (server may not be running)"
            print("⚠ connection: Cannot connect to Forge API (server may not be running)")
        
        # Test getting models (even if connection fails, should handle gracefully)
        models = forge_api_client.get_models()
        if models:
            results['get_models'] = f"✓ PASS: Found {len(models)} models"
            print(f"✓ get_models: Found {len(models)} models")
        else:
            results['get_models'] = "⚠ WARN: No models found (server may not be running)"
            print("⚠ get_models: No models found (server may not be running)")
        
    except Exception as e:
        results['forge_api'] = f"✗ FAIL: {e}"
        print(f"✗ forge_api test failed: {e}")
        traceback.print_exc()
    
    return results

def test_output_manager():
    """Test output manager functionality."""
    print("\n" + "=" * 60)
    print("TESTING OUTPUT MANAGER")
    print("=" * 60)
    
    results = {}
    
    try:
        from core.output_manager import output_manager
        
        # Test getting output statistics
        stats = output_manager.get_output_statistics()
        results['get_statistics'] = f"✓ PASS: Got statistics"
        print(f"✓ get_statistics: Total outputs: {stats.get('total_outputs', 0)}")
        
        # Test getting all outputs
        all_outputs = output_manager.get_all_outputs()
        results['get_all_outputs'] = f"✓ PASS: Got {len(all_outputs)} config outputs"
        print(f"✓ get_all_outputs: Got {len(all_outputs)} config outputs")
        
    except Exception as e:
        results['output_manager'] = f"✗ FAIL: {e}"
        print(f"✗ output_manager test failed: {e}")
        traceback.print_exc()
    
    return results

def test_job_queue():
    """Test job queue functionality."""
    print("\n" + "=" * 60)
    print("TESTING JOB QUEUE")
    print("=" * 60)
    
    results = {}
    
    try:
        from core.job_queue import job_queue
        
        # Test getting queue status
        status = job_queue.get_queue_stats()
        results['get_status'] = f"✓ PASS: Queue size: {status.get('queue_size', 0)}"
        print(f"✓ get_status: Queue size: {status.get('queue_size', 0)}")
        
        # Test adding a job
        job = job_queue.add_job("test_config", 1, 1)
        results['add_job'] = f"✓ PASS: Added job {job.id}"
        print(f"✓ add_job: Added job {job.id}")
        
        # Test removing the job
        removed = job_queue.remove_job(job.id)
        results['remove_job'] = f"✓ PASS: Removed job: {removed}"
        print(f"✓ remove_job: Removed job: {removed}")
        
    except Exception as e:
        results['job_queue'] = f"✗ FAIL: {e}"
        print(f"✗ job_queue test failed: {e}")
        traceback.print_exc()
    
    return results

def test_web_dashboard():
    """Test web dashboard imports."""
    print("\n" + "=" * 60)
    print("TESTING WEB DASHBOARD")
    print("=" * 60)
    
    results = {}
    
    try:
        # Test importing the Flask app
        import web_dashboard.app
        results['app_import'] = "✓ PASS: Web dashboard app imported"
        print("✓ app_import: Web dashboard app imported")
        
    except Exception as e:
        results['app_import'] = f"✗ FAIL: {e}"
        print(f"✗ app_import failed: {e}")
        traceback.print_exc()
    
    return results

def run_all_tests():
    """Run all tests and generate a summary."""
    print("FORGE API TOOL - COMPREHENSIVE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_results = {}
    
    # Run all test suites
    all_results['imports'] = test_imports()
    all_results['config_handler'] = test_config_handler()
    all_results['forge_api'] = test_forge_api()
    all_results['output_manager'] = test_output_manager()
    all_results['job_queue'] = test_job_queue()
    all_results['web_dashboard'] = test_web_dashboard()
    
    # Generate summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warning_tests = 0
    
    for suite_name, suite_results in all_results.items():
        print(f"\n{suite_name.upper()}:")
        for test_name, result in suite_results.items():
            print(f"  {test_name}: {result}")
            total_tests += 1
            if "✓ PASS" in result:
                passed_tests += 1
            elif "✗ FAIL" in result:
                failed_tests += 1
            elif "⚠" in result:
                warning_tests += 1
    
    print(f"\nSUMMARY:")
    print(f"  Total tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Warnings: {warning_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return True
    else:
        print(f"\n❌ {failed_tests} TESTS FAILED ❌")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 