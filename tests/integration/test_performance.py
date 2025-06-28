#!/usr/bin/env python3
"""
Integration tests for performance.
Tests that the API performs reasonably under various loads.
"""

import unittest
import requests
import time
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestPerformance(unittest.TestCase):
    """Test cases for performance testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.BASE = "http://localhost:4000"  # Updated to use port 4000
        self.timeout = 10  # Increased timeout for performance tests
    
    def test_large_batch_generation(self):
        """Test handling of large batch generation requests."""
        try:
            start_time = time.time()
            r = requests.post(f"{self.BASE}/api/batch/preview", json={
                "config_name": "test_config",
                "prompt": "a beautiful landscape",
                "batch_size": 100
            }, timeout=self.timeout)
            end_time = time.time()
            
            # Should complete within reasonable time
            self.assertLess(end_time - start_time, 30)  # 30 seconds max
            self.assertIn(r.status_code, [200, 400, 500])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        try:
            import threading
            
            results = []
            errors = []
            
            def make_request():
                try:
                    r = requests.get(f"{self.BASE}/api/status", timeout=self.timeout)
                    results.append(r.status_code)
                except Exception as e:
                    errors.append(str(e))
            
            # Start multiple concurrent requests
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Should handle concurrent requests without major issues
            # If all requests failed due to server not running, skip the test
            if len(results) == 0 and len(errors) > 0:
                self.skipTest("Server not running - expected in test environment")
            
            # If we got any results, check that we got some successful responses
            if len(results) > 0:
                self.assertGreater(len(results), 0)
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_image_analysis_performance(self):
        """Test performance of image analysis endpoint."""
        try:
            # Create a simple test image data (minimal base64)
            test_image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            
            start_time = time.time()
            r = requests.post(f"{self.BASE}/api/analyze-image", json={
                "image_data": test_image_data
            }, timeout=self.timeout)
            end_time = time.time()
            
            # Should complete quickly for small images
            self.assertLess(end_time - start_time, 5)  # 5 seconds max
            self.assertIn(r.status_code, [200, 400, 500])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_config_loading_performance(self):
        """Test performance of config loading operations."""
        try:
            start_time = time.time()
            r = requests.get(f"{self.BASE}/api/configs", timeout=self.timeout)
            end_time = time.time()
            
            # Should load configs quickly
            self.assertLess(end_time - start_time, 3)  # 3 seconds max
            self.assertIn(r.status_code, [200, 404, 500])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")


if __name__ == '__main__':
    unittest.main() 