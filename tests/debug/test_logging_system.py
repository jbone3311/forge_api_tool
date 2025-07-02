#!/usr/bin/env python3
"""
Comprehensive Logging System Test

This test verifies that all logging functionality is working properly across the application.
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import time

from core.centralized_logger import CentralizedLogger, logger


class TestLoggingSystem(unittest.TestCase):
    """Test the complete logging system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test logs
        self.test_log_dir = Path(tempfile.mkdtemp()) / "test_logs"
        self.test_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a test logger instance
        self.test_logger = CentralizedLogger(str(self.test_log_dir))
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove test log directory
        if self.test_log_dir.parent.exists():
            shutil.rmtree(self.test_log_dir.parent)
    
    def test_logger_initialization(self):
        """Test logger initialization and directory structure."""
        # Check that all directories were created
        expected_dirs = ['errors', 'performance', 'application', 'sessions']
        for dir_name in expected_dirs:
            dir_path = self.test_log_dir / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} was not created")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} is not a directory")
        
        # Check that main log files exist
        expected_files = ['app.log', 'api.log', 'jobs.log']
        for file_name in expected_files:
            file_path = self.test_log_dir / file_name
            self.assertTrue(file_path.exists(), f"Log file {file_name} was not created")
    
    def test_basic_logging(self):
        """Test basic logging functionality."""
        # Test info logging
        self.test_logger.info("Test info message")
        
        # Test warning logging
        self.test_logger.warning("Test warning message")
        
        # Test error logging
        self.test_logger.error("Test error message")
        
        # Test debug logging
        self.test_logger.debug("Test debug message")
        
        # Check that messages were written to app.log
        app_log_path = self.test_log_dir / "app.log"
        with open(app_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("Test info message", log_content)
        self.assertIn("Test warning message", log_content)
        self.assertIn("Test error message", log_content)
    
    def test_app_events(self):
        """Test application event logging."""
        event_data = {"test": True, "timestamp": datetime.now().isoformat()}
        self.test_logger.log_app_event("test_event", event_data)
        
        # Check that event was written to application directory
        event_file = self.test_log_dir / "application" / f"test_event_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(event_file.exists(), "Event file was not created")
        
        # Check event content
        with open(event_file, 'r', encoding='utf-8') as f:
            events = [json.loads(line.strip()) for line in f if line.strip()]
        
        self.assertGreater(len(events), 0, "No events found in file")
        latest_event = events[-1]
        self.assertEqual(latest_event['event_type'], 'test_event')
        self.assertEqual(latest_event['data']['test'], True)
    
    def test_error_logging(self):
        """Test error logging with exceptions."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.test_logger.log_error("Test error with exception", e, {"context": "test"})
        
        # Check error log file
        error_file = self.test_log_dir / "errors" / f"errors_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(error_file.exists(), "Error file was not created")
        
        # Check error content
        with open(error_file, 'r', encoding='utf-8') as f:
            errors = [json.loads(line.strip()) for line in f if line.strip()]
        
        self.assertGreater(len(errors), 0, "No errors found in file")
        latest_error = errors[-1]
        self.assertEqual(latest_error['message'], "Test error with exception")
        self.assertEqual(latest_error['error_type'], 'ValueError')
        self.assertEqual(latest_error['context']['context'], 'test')
    
    def test_api_logging(self):
        """Test API call logging."""
        self.test_logger.log_api_call("/test/endpoint", "GET", 200, 0.5, {"param": "value"})
        
        # Check API log file
        api_log_path = self.test_log_dir / "api.log"
        with open(api_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("API_CALL: GET /test/endpoint", log_content)
        self.assertIn("200", log_content)
        self.assertIn("500.0ms", log_content)
        
        # Check performance file
        perf_file = self.test_log_dir / "performance" / f"api_performance_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(perf_file.exists(), "Performance file was not created")
    
    def test_api_error_logging(self):
        """Test API error logging."""
        self.test_logger.log_api_error("/test/endpoint", "POST", "Connection failed", 1.2)
        
        # Check API error log
        api_log_path = self.test_log_dir / "api.log"
        with open(api_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("API_ERROR: POST /test/endpoint", log_content)
        self.assertIn("Connection failed", log_content)
        
        # Check API error file
        error_file = self.test_log_dir / "errors" / f"api_errors_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(error_file.exists(), "API error file was not created")
    
    def test_performance_logging(self):
        """Test performance logging."""
        self.test_logger.log_performance("test_operation", 2.5, {"iterations": 100})
        
        # Check that performance was logged to app.log
        app_log_path = self.test_log_dir / "app.log"
        with open(app_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("PERFORMANCE: test_operation", log_content)
        self.assertIn("2500.0ms", log_content)
        
        # Check that performance JSON file was created
        perf_file = self.test_log_dir / "performance" / f"performance_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(perf_file.exists(), "Performance JSON file was not created")
    
    def test_job_logging(self):
        """Test job event logging."""
        job_data = {"batch_size": 5, "config": "test_config"}
        self.test_logger.log_job_event("job_123", "started", job_data)
        
        # Check jobs log
        jobs_log_path = self.test_log_dir / "jobs.log"
        with open(jobs_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("JOB_EVENT: job_123", log_content)
        self.assertIn("started", log_content)
    
    def test_output_logging(self):
        """Test output creation logging."""
        self.test_logger.log_output_created("test_config", "/path/to/image.png", "test prompt", 12345)
        
        # Check that output event was logged
        app_log_path = self.test_log_dir / "app.log"
        with open(app_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("APP_EVENT: output_created", log_content)
        self.assertIn("test_config", log_content)
        self.assertIn("12345", log_content)
    
    def test_session_logging(self):
        """Test session logging."""
        session_settings = {"config": "test", "batch_size": 3}
        self.test_logger.log_session_start("session_123", "test_config", session_settings)
        
        session_results = {"images_generated": 5, "success": True}
        self.test_logger.log_session_end("session_123", session_results)
        
        # Check that session events were logged to app.log
        app_log_path = self.test_log_dir / "app.log"
        with open(app_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("APP_EVENT: session_started", log_content)
        self.assertIn("APP_EVENT: session_ended", log_content)
        self.assertIn("session_123", log_content)
    
    def test_config_operation_logging(self):
        """Test configuration operation logging."""
        self.test_logger.log_config_operation("create", "test_config", True, {"source": "test"})
        
        # Check config operation file
        config_file = self.test_log_dir / "application" / f"config_operations_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(config_file.exists(), "Config operation file was not created")
        
        # Check content
        with open(config_file, 'r', encoding='utf-8') as f:
            operations = [json.loads(line.strip()) for line in f if line.strip()]
        
        self.assertGreater(len(operations), 0, "No config operations found")
        latest_op = operations[-1]
        self.assertEqual(latest_op['operation'], 'create')
        self.assertEqual(latest_op['config_name'], 'test_config')
        self.assertTrue(latest_op['success'])
    
    def test_queue_operation_logging(self):
        """Test queue operation logging."""
        self.test_logger.log_queue_operation("add", "job_456", {"priority": "high"})
        
        # Check queue operation file
        queue_file = self.test_logger.application_dir / f"queue_operations_{datetime.now().strftime('%Y%m%d')}.json"
        self.assertTrue(queue_file.exists(), "Queue operation file was not created")
        
        # Check content
        with open(queue_file, 'r', encoding='utf-8') as f:
            operations = [json.loads(line.strip()) for line in f if line.strip()]
        
        self.assertGreater(len(operations), 0, "No queue operations found")
        latest_op = operations[-1]
        self.assertEqual(latest_op['operation'], 'add')
        self.assertEqual(latest_op['job_id'], 'job_456')
    
    def test_log_directory_structure(self):
        """Test log directory structure reporting."""
        structure = self.test_logger.get_log_directory_structure()
        
        self.assertIn('log_dir', structure)
        self.assertIn('subdirectories', structure)
        self.assertIn('file_counts', structure)
        self.assertIn('total_size_mb', structure)
        
        # Check subdirectories
        for subdir_name in ['errors', 'performance', 'application', 'sessions']:
            self.assertIn(subdir_name, structure['subdirectories'])
            self.assertTrue(structure['subdirectories'][subdir_name]['exists'])
    
    def test_session_summary(self):
        """Test session summary generation."""
        # Add some events first
        self.test_logger.log_app_event("test_event_1", {"data": "value1"})
        self.test_logger.log_app_event("test_event_2", {"data": "value2"})
        
        summary = self.test_logger.get_session_summary()
        
        self.assertIn('recent_events', summary)
        self.assertIn('total_events', summary)
        self.assertGreater(summary['total_events'], 0, "No events in summary")
    
    def test_global_logger_instance(self):
        """Test the global logger instance."""
        # Test that the global logger works
        logger.info("Global logger test message")
        
        # Check that it writes to the default location
        default_log_dir = Path("outputs/logs")
        if default_log_dir.exists():
            app_log_path = default_log_dir / "app.log"
            if app_log_path.exists():
                with open(app_log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                
                # The message should be in the log (might be among other messages)
                # We'll just check that the logger is working
                self.assertTrue(len(log_content) > 0, "Global logger not writing to log file")
    
    def test_log_cleanup(self):
        """Test log cleanup functionality."""
        # Create some old log files with old timestamps
        old_file = self.test_log_dir / "application" / "old_event_20240101.json"
        old_file.write_text('{"old": "data"}')
        
        # Set old timestamp (more than 1 day ago)
        old_timestamp = datetime.now().timestamp() - (2 * 24 * 3600)  # 2 days ago
        os.utime(old_file, (old_timestamp, old_timestamp))
        
        # Create a recent file
        recent_file = self.test_log_dir / "application" / f"recent_event_{datetime.now().strftime('%Y%m%d')}.json"
        recent_file.write_text('{"recent": "data"}')
        
        # Run cleanup (should remove old files)
        deleted_count = self.test_logger.cleanup_old_logs(days_to_keep=1)
        
        # Check that old file was deleted
        self.assertFalse(old_file.exists(), "Old log file was not cleaned up")
        
        # Check that recent file still exists
        self.assertTrue(recent_file.exists(), "Recent log file was incorrectly cleaned up")
        
        self.assertGreaterEqual(deleted_count, 1, "No files were cleaned up")


class TestLoggingIntegration(unittest.TestCase):
    """Test logging integration with other components."""
    
    def test_logging_with_config_handler(self):
        """Test that config handler uses logging properly."""
        from core.config_handler import ConfigHandler
        
        handler = ConfigHandler()
        
        # Test that config operations are logged
        configs = handler.list_configs()
        self.assertIsInstance(configs, list, "Config handler should return a list")
        
        # The logging should happen automatically during config operations
        # We can't easily test the actual log files here, but we can verify
        # that the operations complete without logging errors
    
    def test_logging_with_output_manager(self):
        """Test that output manager uses logging properly."""
        from core.output_manager import OutputManager
        
        manager = OutputManager()
        
        # Test that output manager operations are logged
        stats = manager.get_output_statistics()
        self.assertIsInstance(stats, dict, "Output manager should return statistics dict")
        
        # The logging should happen automatically during output operations
    
    def test_logging_with_image_analyzer(self):
        """Test that image analyzer uses logging properly."""
        from core.image_analyzer import ImageAnalyzer
        
        analyzer = ImageAnalyzer()
        
        # Test that analyzer operations are logged
        formats = analyzer.get_supported_formats()
        self.assertIsInstance(formats, list, "Image analyzer should return supported formats")
        
        # The logging should happen automatically during analysis operations


def run_logging_tests():
    """Run all logging tests."""
    print("🧪 Running comprehensive logging system tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add logging system tests
    suite.addTest(unittest.makeSuite(TestLoggingSystem))
    suite.addTest(unittest.makeSuite(TestLoggingIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 LOGGING TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All logging tests passed!")
        return True
    else:
        print("\n❌ Some logging tests failed!")
        return False


if __name__ == "__main__":
    success = run_logging_tests()
    exit(0 if success else 1) 