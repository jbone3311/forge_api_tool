import unittest
import requests

class TestEndpointCoverage(unittest.TestCase):
    BASE = "http://localhost:3000"

    def test_all_endpoints(self):
        endpoints = [
            ("/api/status", "GET"), ("/api/status/api", "GET"), ("/api/configs", "GET"), ("/api/queue/status", "GET"),
            ("/api/batch/preview", "POST"), ("/api/batch", "POST"), ("/api/connect", "POST"), ("/api/disconnect", "POST"),
            ("/api/outputs", "GET"), ("/api/outputs/export/SD_Default", "POST")
            # Add all other endpoints from app.py as needed
        ]
        for ep, method in endpoints:
            url = self.BASE + ep
            if method == "GET":
                r = requests.get(url)
            else:
                r = requests.post(url)
            self.assertIn(r.status_code, (200, 400, 404), f"Endpoint {ep} failed: {r.status_code}")

if __name__ == "__main__":
    unittest.main() 