import unittest
import os

class TestPermissions(unittest.TestCase):
    def test_config_dir_permissions(self):
        self.assertTrue(os.access("configs", os.R_OK | os.W_OK), "Config dir not readable/writable")

    def test_output_dir_permissions(self):
        self.assertTrue(os.access("outputs", os.R_OK | os.W_OK), "Outputs dir not readable/writable")

    def test_logs_dir_permissions(self):
        self.assertTrue(os.access("logs", os.R_OK | os.W_OK), "Logs dir not readable/writable")

    def test_protected_endpoint(self):
        # If you have any protected endpoints, try accessing them without auth
        pass  # Implement as needed

if __name__ == "__main__":
    unittest.main() 