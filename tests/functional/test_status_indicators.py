#!/usr/bin/env python3
"""
Test script to check status indicators and API endpoints
"""

import requests
import json
import time

def test_status_endpoints():
    """Test the status endpoints to see if they're working."""
    base_url = "http://localhost:3000"
    
    print("Testing Status Endpoints")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✓ Dashboard accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False
    
    # Test 2: System status endpoint
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ System status endpoint working")
            print(f"  API Status: {data.get('api', {}).get('connected', 'Unknown')}")
            print(f"  Queue Status: {data.get('queue', {}).get('total_jobs', 0)} jobs")
            print(f"  Generation Status: {data.get('generation', {}).get('active', False)}")
        else:
            print(f"❌ System status endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"❌ System status endpoint error: {e}")
    
    # Test 3: API status endpoint
    try:
        response = requests.get(f"{base_url}/api/status/api", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ API status endpoint working")
            print(f"  Connected: {data.get('connected', False)}")
            print(f"  Server URL: {data.get('server_url', 'Unknown')}")
        else:
            print(f"❌ API status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API status endpoint error: {e}")
    
    # Test 4: Connect endpoint
    try:
        response = requests.post(f"{base_url}/api/connect", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Connect endpoint working")
            print(f"  Success: {data.get('success', False)}")
        else:
            print(f"⚠ Connect endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Connect endpoint error: {e}")
    
    # Test 5: Queue status endpoint
    try:
        response = requests.get(f"{base_url}/api/queue/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Queue status endpoint working")
            print(f"  Total jobs: {data.get('total_jobs', 0)}")
        else:
            print(f"❌ Queue status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Queue status endpoint error: {e}")
    
    return True

def test_forge_connection():
    """Test if Forge API is accessible."""
    print("\nTesting Forge API Connection")
    print("=" * 50)
    
    try:
        # Test direct connection to Forge
        response = requests.get("http://127.0.0.1:7860/sdapi/v1/progress", timeout=5)
        if response.status_code == 200:
            print("✓ Forge API is accessible at http://127.0.0.1:7860")
            return True
        else:
            print(f"⚠ Forge API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Forge API not accessible: {e}")
        print("  Make sure Forge is running at http://127.0.0.1:7860")
        return False

def main():
    """Run all tests."""
    print("🔧 Status Indicators Test")
    print("=" * 50)
    
    # Test if dashboard is running
    if not test_status_endpoints():
        print("\n❌ Dashboard is not running or not accessible")
        print("Start the dashboard with: cd web_dashboard && python app.py")
        return
    
    # Test Forge connection
    forge_connected = test_forge_connection()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if forge_connected:
        print("✅ Forge API is running - status indicators should work")
        print("💡 Try clicking the 'Connect' button in the dashboard")
    else:
        print("⚠️  Forge API is not running")
        print("💡 Start Forge first, then try the 'Connect' button")
    
    print("\n🔍 Debugging Tips:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify all status elements exist in the DOM")
    print("3. Check if Socket.IO is working")
    print("4. Ensure all API endpoints return valid JSON")

if __name__ == "__main__":
    main() 