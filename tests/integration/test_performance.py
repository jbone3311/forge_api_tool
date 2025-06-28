import unittest
import requests
import time

class TestPerformance(unittest.TestCase):
    BASE = "http://localhost:3000"

    def test_large_batch_generation(self):
        start = time.time()
        r = requests.post(f"{self.BASE}/api/batch/preview", json={
            "config_name": "SD_Default",
            "batch_size": 10,
            "num_batches": 10
        })
        duration = time.time() - start
        self.assertLess(duration, 10, f"Batch preview took too long: {duration}s")
        self.assertEqual(r.status_code, 200)

    def test_dashboard_with_many_outputs(self):
        # Simulate or check dashboard responsiveness with many outputs
        pass  # Implement as needed

if __name__ == "__main__":
    unittest.main() 