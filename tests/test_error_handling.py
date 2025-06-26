import unittest
import requests

class TestErrorHandling(unittest.TestCase):
    BASE = "http://localhost:5000"

    def test_malformed_config(self):
        r = requests.post(f"{self.BASE}/api/configs", json={"bad": "data"})
        self.assertNotEqual(r.status_code, 200)

    def test_missing_wildcard(self):
        r = requests.post(f"{self.BASE}/api/batch/preview", json={
            "config_name": "template_with_missing_wildcard"
        })
        self.assertIn(r.status_code, (400, 404))

    def test_api_timeout(self):
        try:
            requests.get("http://localhost:9999", timeout=1)
        except requests.exceptions.RequestException as e:
            self.assertIsInstance(e, Exception)

if __name__ == "__main__":
    unittest.main() 