#!/usr/bin/env python3
"""
Simple API test script for Forge API Tool
Tests the new connection management and shutdown endpoints
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single API endpoint."""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    print(f"   Method: {method}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"   ⚠️  Success but no JSON response: {response.text}")
                return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Could not connect to {BASE_URL}")
        print(f"   💡 Make sure the dashboard is running at {BASE_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout: Request took too long")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    """Run all API tests."""
    print("🚀 Forge API Tool - API Test Suite")
    print("=" * 50)
    
    # Test basic connectivity
    print("\n📡 Testing basic connectivity...")
    if not test_endpoint("/forge/status", description="Get Forge connection status"):
        print("\n❌ Cannot connect to dashboard. Please start the dashboard first:")
        print("   cd web_dashboard && python app.py")
        sys.exit(1)
    
    # Test connection management
    print("\n🔌 Testing connection management...")
    
    # Test connect with default URL
    test_endpoint("/forge/connect", method="POST", 
                  data={"server_url": "http://127.0.0.1:7860/"}, 
                  description="Connect to Forge API (default)")
    
    # Test status after connection
    test_endpoint("/forge/status", description="Get status after connection")
    
    # Test connect with custom URL
    test_endpoint("/forge/connect", method="POST", 
                  data={"server_url": "http://localhost:7860/"}, 
                  description="Connect to Forge API (custom URL)")
    
    # Test disconnect
    test_endpoint("/forge/disconnect", method="POST", 
                  description="Disconnect from Forge API")
    
    # Test status after disconnect
    test_endpoint("/forge/status", description="Get status after disconnect")
    
    # Test other endpoints
    print("\n📋 Testing other endpoints...")
    test_endpoint("/configs", description="Get list of configurations")
    test_endpoint("/queue/status", description="Get queue status")
    
    # Test shutdown (commented out for safety)
    print("\n⚠️  Shutdown test skipped for safety")
    print("   Uncomment the following lines to test shutdown:")
    print("   test_endpoint('/shutdown', method='POST', description='Shutdown application')")
    
    print("\n✅ API test suite completed!")
    print("\n💡 To test shutdown functionality, uncomment the shutdown test in this script.")

if __name__ == "__main__":
    main() 