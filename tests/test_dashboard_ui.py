import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

class TestDashboardUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.get("http://localhost:5000")
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_status_indicators(self):
        api_status = self.driver.find_element(By.ID, "api-status")
        self.assertIn("API", api_status.text)

    def test_connect_button(self):
        connect_btn = self.driver.find_element(By.ID, "api-connect-btn")
        connect_btn.click()
        time.sleep(1)
        # Check for status update or notification
        api_status = self.driver.find_element(By.ID, "api-status")
        self.assertTrue("Connected" in api_status.text or "Disconnected" in api_status.text)

    def test_template_prompt_autopopulate(self):
        config_select = self.driver.find_element(By.ID, "config-select")
        config_select.click()
        time.sleep(1)
        # Select a template and check prompt field is populated
        options = config_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()
            time.sleep(1)
            prompt_input = self.driver.find_element(By.ID, "prompt-input")
            self.assertTrue(len(prompt_input.get_attribute("value")) > 0 or len(prompt_input.text) > 0)

    def test_batch_preview_and_generation(self):
        preview_btn = self.driver.find_element(By.CSS_SELECTOR, ".batch-actions .btn-secondary")
        preview_btn.click()
        time.sleep(1)
        modal = self.driver.find_element(By.ID, "batch-preview-modal")
        self.assertTrue(modal.is_displayed())

    def test_no_js_errors(self):
        logs = self.driver.get_log("browser")
        errors = [log for log in logs if log["level"] == "SEVERE"]
        self.assertEqual(len(errors), 0, f"JS errors found: {errors}")

if __name__ == "__main__":
    unittest.main() 