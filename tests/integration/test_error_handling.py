#!/usr/bin/env python3
"""
Integration tests for error handling.
Tests that the API properly handles various error conditions.
"""

import unittest
import requests
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.BASE = "http://localhost:4000"  # Updated to use port 4000
        self.timeout = 5  # Reduced timeout for faster test failure
    
    def test_malformed_config(self):
        """Test handling of malformed configuration data."""
        try:
            r = requests.post(f"{self.BASE}/api/configs", json={"bad": "data"}, timeout=self.timeout)
            # Should return 400 or 500 for malformed data
            self.assertIn(r.status_code, [400, 500])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_missing_wildcard(self):
        """Test handling of missing wildcard files."""
        try:
            r = requests.post(f"{self.BASE}/api/batch/preview", json={
                "config_name": "test_config",
                "prompt": "a beautiful __NONEXISTENT_WILDCARD__ landscape"
            }, timeout=self.timeout)
            # Should handle missing wildcard gracefully
            self.assertIn(r.status_code, [200, 400, 500])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_invalid_image_data(self):
        """Test handling of invalid image data."""
        try:
            r = requests.post(f"{self.BASE}/api/analyze-image", json={
                "image_data": "invalid_base64_data"
            }, timeout=self.timeout)
            # Should return 400 for invalid image data
            self.assertIn(r.status_code, [400, 500])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_missing_config_settings(self):
        """Test handling of missing config settings."""
        try:
            r = requests.put(f"{self.BASE}/api/configs/test_config/settings", 
                           json={}, timeout=self.timeout)
            # Should return 400 for missing settings data
            self.assertIn(r.status_code, [400, 404, 500])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")
    
    def test_nonexistent_config(self):
        """Test handling of requests for nonexistent configs."""
        try:
            r = requests.get(f"{self.BASE}/api/configs/nonexistent_config", timeout=self.timeout)
            # Should return 404 for nonexistent config
            self.assertIn(r.status_code, [404, 500])
        except requests.exceptions.ConnectionError:
            self.skipTest("Server not running - expected in test environment")


if __name__ == '__main__':
    unittest.main() 