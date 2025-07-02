#!/usr/bin/env python3
"""
Comprehensive Test Script for Forge API Tool Web Dashboard
Tests all major functionality including API endpoints, JavaScript loading, and core features.
"""

import requests
import json
import time
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:4000"

def test_endpoint(endpoint, expected_status=200, description=""):
    """Test a single endpoint and return success status."""
    try:
        url = urljoin(BASE_URL, endpoint)
        response = requests.get(url, timeout=10)
        success = response.status_code == expected_status
        print(f"{'✓' if success else '✗'} {description or endpoint}: {response.status_code}")
        return success
    except Exception as e:
        print(f"✗ {description or endpoint}: Error - {e}")
        return False

def test_api_endpoint(endpoint, expected_fields=None, description=""):
    """Test an API endpoint and verify JSON response."""
    try:
        url = urljoin(BASE_URL, endpoint)
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if expected_fields:
                missing_fields = [field for field in expected_fields if field not in data]
                if missing_fields:
                    print(f"✗ {description or endpoint}: Missing fields {missing_fields}")
                    return False
            print(f"✓ {description or endpoint}: OK")
            return True
        else:
            print(f"✗ {description or endpoint}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {description or endpoint}: Error - {e}")
        return False

def test_js_file(file_path):
    """Test if a JavaScript file is accessible."""
    try:
        url = urljoin(BASE_URL, f"static/js/{file_path}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ JS {file_path}: OK")
            return True
        else:
            print(f"✗ JS {file_path}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ JS {file_path}: Error - {e}")
        return False

def main():
    print("🧪 Comprehensive Test Suite for Forge API Tool Web Dashboard")
    print("=" * 60)
    
    # Test basic connectivity
    print("\n📡 Basic Connectivity Tests:")
    print("-" * 30)
    test_endpoint("/", description="Main Dashboard Page")
    test_endpoint("/static/css/dashboard.css", description="CSS File")
    
    # Test API endpoints
    print("\n🔌 API Endpoint Tests:")
    print("-" * 30)
    test_api_endpoint("/api/configs/", description="Configs API")
    test_api_endpoint("/api/status/", expected_fields=["api", "generation", "queue"], description="Status API")
    test_api_endpoint("/api/queue/status", description="Queue Status API")
    test_api_endpoint("/api/outputs/list", description="Outputs List API")
    
    # Test JavaScript files
    print("\n📜 JavaScript File Tests:")
    print("-" * 30)
    test_js_file("dashboard-modular.js")
    test_js_file("modules/notifications.js")
    test_js_file("modules/modals.js")
    test_js_file("modules/templates.js")
    test_js_file("modules/generation.js")
    test_js_file("modules/queue.js")
    test_js_file("modules/output.js")
    test_js_file("modules/settings.js")
    test_js_file("modules/analysis.js")
    test_js_file("modules/utils.js")
    
    # Test template loading
    print("\n📋 Template Loading Tests:")
    print("-" * 30)
    try:
        response = requests.get(f"{BASE_URL}/api/configs/", timeout=10)
        if response.status_code == 200:
            configs = response.json()
            config_count = len([k for k in configs.keys() if k not in ['success', 'timestamp', 'message']])
            print(f"✓ Configs loaded: {config_count} configurations")
            
            # Test a specific config
            if 'Quick Start' in configs:
                quick_start = configs['Quick Start']
                required_fields = ['name', 'model_type', 'generation_settings']
                missing = [f for f in required_fields if f not in quick_start]
                if not missing:
                    print("✓ Quick Start config has all required fields")
                else:
                    print(f"✗ Quick Start config missing fields: {missing}")
            else:
                print("✗ Quick Start config not found")
        else:
            print(f"✗ Failed to load configs: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ Template loading test failed: {e}")
    
    # Test status service
    print("\n🔍 Status Service Tests:")
    print("-" * 30)
    try:
        response = requests.get(f"{BASE_URL}/api/status/", timeout=10)
        if response.status_code == 200:
            status = response.json()
            api_status = status.get('api', {})
            print(f"✓ API Status: Connected={api_status.get('connected', False)}")
            print(f"✓ Server URL: {api_status.get('server_url', 'N/A')}")
            
            generation_status = status.get('generation', {})
            print(f"✓ Generation Status: Generating={generation_status.get('is_generating', False)}")
        else:
            print(f"✗ Status API failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"✗ Status service test failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("\nTo test the full interface:")
    print("1. Open http://localhost:4000 in Safari")
    print("2. Open Developer Tools (Cmd+Option+I)")
    print("3. Check the Console tab for any JavaScript errors")
    print("4. Test the template loading and generation features")

if __name__ == "__main__":
    main() 