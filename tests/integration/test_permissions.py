#!/usr/bin/env python3
"""
Integration tests for permissions.
Tests that the application has proper permissions for required operations.
"""

import unittest
import os
import sys

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestPermissions(unittest.TestCase):
    """Test cases for permission testing."""
    
    def test_config_dir_permissions(self):
        """Test that config directory is readable/writable."""
        config_dir = "configs"
        
        # Check if directory exists, if not create it
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        self.assertTrue(os.access(config_dir, os.R_OK | os.W_OK), "Config dir not readable/writable")
    
    def test_output_dir_permissions(self):
        """Test that output directory is readable/writable."""
        output_dir = "outputs"
        
        # Check if directory exists, if not create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        self.assertTrue(os.access(output_dir, os.R_OK | os.W_OK), "Output dir not readable/writable")
    
    def test_wildcard_dir_permissions(self):
        """Test that wildcard directory is readable."""
        wildcard_dir = "wildcards"
        
        # Check if directory exists
        if os.path.exists(wildcard_dir):
            self.assertTrue(os.access(wildcard_dir, os.R_OK), "Wildcard dir not readable")
        else:
            # Directory doesn't exist, which is okay for tests
            self.skipTest("Wildcard directory doesn't exist - skipping permission test")
    
    def test_log_dir_permissions(self):
        """Test that log directory is writable."""
        log_dir = "logs"
        
        # Check if directory exists, if not create it
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        self.assertTrue(os.access(log_dir, os.W_OK), "Log dir not writable")
    
    def test_temp_file_creation(self):
        """Test that temporary files can be created."""
        import tempfile
        
        try:
            # Try to create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write("test content")
                temp_file_path = f.name
            
            # Check that file was created and is writable
            self.assertTrue(os.path.exists(temp_file_path))
            self.assertTrue(os.access(temp_file_path, os.R_OK | os.W_OK))
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.fail(f"Failed to create temporary file: {e}")


if __name__ == '__main__':
    unittest.main() 