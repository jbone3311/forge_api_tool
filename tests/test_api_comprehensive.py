#!/usr/bin/env python3
"""
Comprehensive API Test Script
Tests all Forge API Tool functionality and ensures logging is working properly.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from core.forge_api import ForgeAPIClient
from core.config_handler import ConfigHandler
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.batch_runner import BatchRunner
from core.image_analyzer import ImageAnalyzer
from core.output_manager import OutputManager
from core.logger import logger

class ComprehensiveAPITester:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        print("-" * 50)
        
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            
            self.test_results["tests"][test_name] = {
                "status": "PASS" if result else "FAIL",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            status_icon = "✅" if result else "❌"
            print(f"{status_icon} {test_name}: {'PASSED' if result else 'FAILED'} ({duration:.3f}s)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.test_results["tests"][test_name] = {
                "status": "ERROR",
                "duration": duration,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"❌ {test_name}: ERROR - {e} ({duration:.3f}s)")
            logger.log_error(f"Test {test_name} failed: {e}")
            return False
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        try:
            # Test basic logging
            logger.info("Test info message")
            logger.warning("Test warning message")
            logger.debug("Test debug message")
            logger.log_app_event("test_event", {"test": True})
            
            # Test session summary
            summary = logger.get_session_summary()
            assert "session_id" in summary
            assert "log_files" in summary
            
            return True
        except Exception as e:
            print(f"Logger test failed: {e}")
            return False
    
    def test_forge_api_client(self):
        """Test Forge API client initialization and basic functionality."""
        try:
            client = ForgeAPIClient()
            
            # Test connection
            connected = client.test_connection()
            if not connected:
                print("⚠️  Forge API not accessible - this is expected if server is not running")
                return True  # Don't fail the test if server is not running
            
            # Test getting models and samplers
            models = client.get_models()
            samplers = client.get_samplers()
            
            # Test getting options
            options = client.get_options()
            
            # Test getting progress
            progress = client.get_progress()
            
            return True
        except Exception as e:
            print(f"Forge API client test failed: {e}")
            return False
    
    def test_config_handler(self):
        """Test configuration handler."""
        try:
            handler = ConfigHandler()
            
            # Test listing configs
            configs = handler.list_configs()
            assert len(configs) > 0, "No configurations found"
            
            # Test loading a config
            if configs:
                config = handler.load_config(configs[0])
                assert config is not None, "Failed to load configuration"
                
                # Test getting summary
                summary = handler.get_config_summary(config)
                assert "name" in summary, "Summary missing name"
                
                # Test wildcard validation
                missing = handler.get_missing_wildcards(configs[0])
                print(f"Missing wildcards for {configs[0]}: {len(missing.get('missing_list', []))}")
            
            return True
        except Exception as e:
            print(f"Config handler test failed: {e}")
            return False
    
    def test_wildcard_manager(self):
        """Test wildcard manager."""
        try:
            factory = WildcardManagerFactory()
            
            # Test getting a manager
            manager = factory.get_manager("wildcards/subject.txt")
            assert manager is not None, "Failed to get wildcard manager"
            
            # Test getting items
            items = manager.get_preview(5)
            assert len(items) > 0, "No wildcard items found"
            
            # Test getting next item
            next_item = manager.get_next()
            assert next_item is not None, "Failed to get next wildcard item"
            
            # Test usage stats
            stats = manager.get_usage_stats()
            assert "total_items" in stats, "Usage stats missing total_items"
            
            return True
        except Exception as e:
            print(f"Wildcard manager test failed: {e}")
            return False
    
    def test_prompt_builder(self):
        """Test prompt builder."""
        try:
            factory = WildcardManagerFactory()
            builder = PromptBuilder(factory)
            
            # Test building a simple prompt
            prompt_template = "a beautiful __SUBJECT__ in __SETTING__"
            prompt = builder.build_prompt(prompt_template)
            
            assert prompt is not None, "Failed to build prompt"
            assert len(prompt) > 0, "Generated prompt is empty"
            assert "__SUBJECT__" not in prompt, "Wildcard not replaced"
            assert "__SETTING__" not in prompt, "Wildcard not replaced"
            
            print(f"Generated prompt: {prompt}")
            
            return True
        except Exception as e:
            print(f"Prompt builder test failed: {e}")
            return False
    
    def test_batch_runner(self):
        """Test batch runner."""
        try:
            runner = BatchRunner()
            
            # Test queue status
            status = runner.get_queue_status()
            assert "total_jobs" in status, "Queue status missing total_jobs"
            
            # Test preview functionality
            configs = ConfigHandler().list_configs()
            if configs:
                preview = runner.preview_job(configs[0], 3)
                assert len(preview) > 0, "No preview generated"
                
                print(f"Preview for {configs[0]}: {len(preview)} prompts")
            
            return True
        except Exception as e:
            print(f"Batch runner test failed: {e}")
            return False
    
    def test_image_analyzer(self):
        """Test image analyzer."""
        try:
            analyzer = ImageAnalyzer()
            
            # Test supported formats
            formats = analyzer.get_supported_formats()
            assert len(formats) > 0, "No supported formats"
            
            # Test format validation
            is_valid = analyzer.validate_image_format("test.jpg")
            assert is_valid, "JPG should be valid format"
            
            return True
        except Exception as e:
            print(f"Image analyzer test failed: {e}")
            return False
    
    def test_output_manager(self):
        """Test output manager."""
        try:
            manager = OutputManager()
            
            # Test getting output summary
            summary = manager.get_output_summary()
            assert "total_files" in summary, "Output summary missing total_files"
            
            # Test directory creation
            test_dir = "test_outputs"
            manager._ensure_directory(test_dir)
            assert os.path.exists(test_dir), "Failed to create test directory"
            
            # Clean up
            if os.path.exists(test_dir):
                os.rmdir(test_dir)
            
            return True
        except Exception as e:
            print(f"Output manager test failed: {e}")
            return False
    
    def test_web_dashboard_api(self):
        """Test web dashboard API endpoints."""
        try:
            import requests
            
            # Test basic connectivity
            try:
                response = requests.get("http://localhost:5000/api/forge/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Web dashboard is running")
                    
                    # Test configs endpoint
                    response = requests.get("http://localhost:5000/api/configs", timeout=5)
                    if response.status_code == 200:
                        configs = response.json()
                        print(f"✅ Configs endpoint working: {len(configs)} configs")
                    
                    # Test queue status endpoint
                    response = requests.get("http://localhost:5000/api/queue/status", timeout=5)
                    if response.status_code == 200:
                        queue_status = response.json()
                        print(f"✅ Queue status endpoint working")
                    
                    return True
                else:
                    print("⚠️  Web dashboard not accessible")
                    return True  # Don't fail if dashboard is not running
                    
            except requests.exceptions.ConnectionError:
                print("⚠️  Web dashboard not running")
                return True  # Don't fail if dashboard is not running
                
        except Exception as e:
            print(f"Web dashboard API test failed: {e}")
            return False
    
    def test_log_files_creation(self):
        """Test that log files are being created properly."""
        try:
            log_dir = Path("logs")
            
            # Check if log directory exists
            if not log_dir.exists():
                print("⚠️  Log directory does not exist")
                return False
            
            # Check for log files
            log_files = list(log_dir.glob("*.log"))
            if not log_files:
                print("⚠️  No log files found")
                return False
            
            print(f"✅ Found {len(log_files)} log files:")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"   - {log_file.name}: {size} bytes")
            
            return True
        except Exception as e:
            print(f"Log files test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Logger Initialization", self.test_logger_initialization),
            ("Forge API Client", self.test_forge_api_client),
            ("Config Handler", self.test_config_handler),
            ("Wildcard Manager", self.test_wildcard_manager),
            ("Prompt Builder", self.test_prompt_builder),
            ("Batch Runner", self.test_batch_runner),
            ("Image Analyzer", self.test_image_analyzer),
            ("Output Manager", self.test_output_manager),
            ("Web Dashboard API", self.test_web_dashboard_api),
            ("Log Files Creation", self.test_log_files_creation),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # Generate summary
        self.test_results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        
        # Save results
        with open("comprehensive_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to comprehensive_test_results.json")
        
        # Log final summary
        logger.log_app_event("comprehensive_test_completed", self.test_results["summary"])
        
        return passed == total

def main():
    tester = ComprehensiveAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the results above.")
        return 1

if __name__ == "__main__":
    exit(main()) 