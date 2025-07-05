#!/usr/bin/env python3
"""
Simple import test script to verify all core modules can be imported.
"""

import sys
import os
import unittest

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class TestImports(unittest.TestCase):
    """Test that all core modules can be imported."""
    
    def test_config_handler_import(self):
        """Test importing config_handler."""
        try:
            from core.config_handler import config_handler
            self.assertIsNotNone(config_handler)
        except ImportError as e:
            self.fail(f"Failed to import config_handler: {e}")
    
    def test_centralized_logger_import(self):
        """Test importing centralized_logger."""
        try:
            from core.centralized_logger import logger
            self.assertIsNotNone(logger)
        except ImportError as e:
            self.fail(f"Failed to import centralized_logger: {e}")
    
    def test_output_manager_import(self):
        """Test importing output_manager."""
        try:
            from core.output_manager import OutputManager
            self.assertIsNotNone(OutputManager)
        except ImportError as e:
            self.fail(f"Failed to import output_manager: {e}")
    
    def test_job_queue_import(self):
        """Test importing job_queue."""
        try:
            from core.job_queue import job_queue
            self.assertIsNotNone(job_queue)
        except ImportError as e:
            self.fail(f"Failed to import job_queue: {e}")
    
    def test_batch_runner_import(self):
        """Test importing batch_runner."""
        try:
            from core.batch_runner import batch_runner
            self.assertIsNotNone(batch_runner)
        except ImportError as e:
            self.fail(f"Failed to import batch_runner: {e}")
    
    def test_wildcard_manager_import(self):
        """Test importing wildcard_manager."""
        try:
            from core.wildcard_manager import WildcardManagerFactory
            self.assertIsNotNone(WildcardManagerFactory)
        except ImportError as e:
            self.fail(f"Failed to import wildcard_manager: {e}")
    
    def test_prompt_builder_import(self):
        """Test importing prompt_builder."""
        try:
            from core.prompt_builder import PromptBuilder
            self.assertIsNotNone(PromptBuilder)
        except ImportError as e:
            self.fail(f"Failed to import prompt_builder: {e}")
    
    def test_image_analyzer_import(self):
        """Test importing image_analyzer."""
        try:
            from core.image_analyzer import ImageAnalyzer
            self.assertIsNotNone(ImageAnalyzer)
        except ImportError as e:
            self.fail(f"Failed to import image_analyzer: {e}")

if __name__ == "__main__":
    unittest.main() 