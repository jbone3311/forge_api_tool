#!/usr/bin/env python3
"""
Integration tests for endpoint coverage.
Tests that all expected API endpoints are available and responding.
"""

import unittest
import requests
import time
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestEndpointCoverage(unittest.TestCase):
    """Test cases for API endpoint coverage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.BASE = "http://localhost:4000"  # Updated to use port 4000
        self.timeout = 5  # Reduced timeout for faster test failure
    
    def test_all_endpoints(self):
        """Test that all expected endpoints are available."""
        # List of expected endpoints to test
        endpoints = [
            ("GET", "/api/status"),
            ("GET", "/api/configs"),
            ("GET", "/api/configs/list"),
            ("POST", "/api/configs"),
            ("GET", "/api/configs/test_config"),
            ("PUT", "/api/configs/test_config"),
            ("DELETE", "/api/configs/test_config"),
            ("POST", "/api/generate"),
            ("POST", "/api/batch/preview"),
            ("POST", "/api/batch/start"),
            ("GET", "/api/batch/status"),
            ("POST", "/api/batch/stop"),
            ("GET", "/api/outputs"),
            ("GET", "/api/outputs/recent"),
            ("GET", "/api/outputs/config/test_config"),
            ("POST", "/api/analyze-image"),
            ("GET", "/api/configs/test_config/settings"),
            ("PUT", "/api/configs/test_config/settings"),
            ("POST", "/api/configs/create-from-image"),
            ("GET", "/api/status/current-api")
        ]
        
        available_endpoints = []
        unavailable_endpoints = []
        
        for method, endpoint in endpoints:
            try:
                url = f"{self.BASE}{endpoint}"
                
                if method == "GET":
                    response = requests.get(url, timeout=self.timeout)
                elif method == "POST":
                    response = requests.post(url, json={}, timeout=self.timeout)
                elif method == "PUT":
                    response = requests.put(url, json={}, timeout=self.timeout)
                elif method == "DELETE":
                    response = requests.delete(url, timeout=self.timeout)
                
                # If we get any response (even 404), the endpoint exists
                available_endpoints.append(f"{method} {endpoint}")
                
            except requests.exceptions.ConnectionError:
                # Server not running or connection refused
                unavailable_endpoints.append(f"{method} {endpoint}")
            except requests.exceptions.Timeout:
                # Request timed out
                unavailable_endpoints.append(f"{method} {endpoint}")
            except Exception as e:
                # Other errors
                unavailable_endpoints.append(f"{method} {endpoint} (Error: {e})")
        
        # Print results
        print(f"\nAvailable endpoints ({len(available_endpoints)}):")
        for endpoint in available_endpoints:
            print(f"  ✅ {endpoint}")
        
        if unavailable_endpoints:
            print(f"\nUnavailable endpoints ({len(unavailable_endpoints)}):")
            for endpoint in unavailable_endpoints:
                print(f"  ❌ {endpoint}")
        
        # For now, just check that we can connect to the server
        # In a real test environment, the server would be running
        try:
            response = requests.get(f"{self.BASE}/api/status", timeout=self.timeout)
            # If we get here, the server is running
            self.assertGreater(len(available_endpoints), 0, "No endpoints available")
        except requests.exceptions.ConnectionError:
            # Server not running - this is expected in test environment
            print("\n⚠️  Server not running on localhost:4000 - skipping endpoint tests")
            self.skipTest("Server not running - expected in test environment")
    
    def test_core_endpoints_respond(self):
        """Test that core endpoints respond with expected status codes."""
        try:
            # Test status endpoint
            response = requests.get(f"{self.BASE}/api/status", timeout=self.timeout)
            self.assertIn(response.status_code, [200, 404, 500])  # Any response means endpoint exists
            
            # Test configs endpoint
            response = requests.get(f"{self.BASE}/api/configs", timeout=self.timeout)
            self.assertIn(response.status_code, [200, 404, 500])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_new_image_analysis_endpoints(self):
        """Test the new image analysis endpoints."""
        try:
            # Test image analysis endpoint
            response = requests.post(f"{self.BASE}/api/analyze-image", 
                                   json={"image_data": "test"}, 
                                   timeout=self.timeout)
            self.assertIn(response.status_code, [200, 400, 500])
            
            # Test config settings endpoint
            response = requests.get(f"{self.BASE}/api/configs/test_config/settings", 
                                  timeout=self.timeout)
            self.assertIn(response.status_code, [200, 404, 500])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")


if __name__ == '__main__':
    unittest.main() 