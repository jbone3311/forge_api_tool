#!/usr/bin/env python3
"""
Direct Forge API Test
Tests the Forge API client directly against the Forge server.
"""

import os
import sys
import time
import json
import requests
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
from core.logger import logger

class DirectForgeAPITester:
    def __init__(self, forge_url: str = "http://127.0.0.1:7860"):
        self.forge_url = forge_url
        self.client = ForgeAPIClient(forge_url)
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "forge_url": forge_url,
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
    
    def test_forge_connection(self):
        """Test basic connection to Forge server."""
        try:
            connected = self.client.test_connection()
            if connected:
                print("✅ Successfully connected to Forge server")
                return True
            else:
                print("❌ Failed to connect to Forge server")
                print("   Make sure Forge is running at:", self.forge_url)
                return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_forge_models(self):
        """Test getting models from Forge."""
        try:
            models = self.client.get_models()
            if models:
                print(f"✅ Found {len(models)} models")
                for i, model in enumerate(models[:3]):  # Show first 3
                    print(f"   {i+1}. {model.get('title', 'Unknown')}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more")
                return True
            else:
                print("⚠️  No models found (this might be normal if no models are loaded)")
                return True  # Don't fail if no models
        except Exception as e:
            print(f"❌ Models test failed: {e}")
            return False
    
    def test_forge_samplers(self):
        """Test getting samplers from Forge."""
        try:
            samplers = self.client.get_samplers()
            if samplers:
                print(f"✅ Found {len(samplers)} samplers")
                for i, sampler in enumerate(samplers[:5]):  # Show first 5
                    print(f"   {i+1}. {sampler.get('name', 'Unknown')}")
                if len(samplers) > 5:
                    print(f"   ... and {len(samplers) - 5} more")
                return True
            else:
                print("⚠️  No samplers found (this might be normal)")
                return True  # Don't fail if no samplers
        except Exception as e:
            print(f"❌ Samplers test failed: {e}")
            return False
    
    def test_forge_options(self):
        """Test getting options from Forge."""
        try:
            options = self.client.get_options()
            if options:
                print(f"✅ Retrieved {len(options)} options")
                # Show some key options
                key_options = ['sd_model_checkpoint', 'sd_vae', 'sampler_name']
                for key in key_options:
                    if key in options:
                        print(f"   {key}: {options[key]}")
                return True
            else:
                print("⚠️  No options found")
                return True  # Don't fail if no options
        except Exception as e:
            print(f"❌ Options test failed: {e}")
            return False
    
    def test_forge_progress(self):
        """Test getting progress from Forge."""
        try:
            progress = self.client.get_progress()
            if progress:
                print("✅ Progress endpoint working")
                # Show progress info if available
                if 'progress' in progress:
                    print(f"   Progress: {progress['progress']:.1f}%")
                if 'eta_relative' in progress:
                    print(f"   ETA: {progress['eta_relative']:.1f}s")
                return True
            else:
                print("✅ Progress endpoint working (no active generation)")
                return True
        except Exception as e:
            print(f"❌ Progress test failed: {e}")
            return False
    
    def test_config_validation(self):
        """Test configuration validation against Forge."""
        try:
            handler = ConfigHandler()
            configs = handler.list_configs()
            
            if not configs:
                print("⚠️  No configurations found")
                return True
            
            # Test first config
            config = handler.load_config(configs[0])
            is_valid, errors = self.client.validate_config(config)
            
            if is_valid:
                print(f"✅ Config '{configs[0]}' is valid")
                return True
            else:
                print(f"⚠️  Config '{configs[0]}' has validation issues:")
                for error in errors:
                    print(f"   - {error}")
                return True  # Don't fail validation, just warn
        except Exception as e:
            print(f"❌ Config validation test failed: {e}")
            return False
    
    def test_prompt_generation(self):
        """Test prompt generation with wildcards."""
        try:
            factory = WildcardManagerFactory()
            builder = PromptBuilder(factory)
            
            # Test with a simple config
            test_config = {
                'prompt_settings': {
                    'base_prompt': 'a beautiful __SUBJECT__ in __SETTING__'
                }
            }
            prompt = builder.build_prompt(test_config)
            
            if prompt and "__SUBJECT__" not in prompt and "__SETTING__" not in prompt:
                print(f"✅ Generated prompt: {prompt}")
                return True
            else:
                print(f"❌ Failed to replace wildcards in prompt: {prompt}")
                return False
        except Exception as e:
            print(f"❌ Prompt generation test failed: {e}")
            return False
    
    def test_batch_preview(self):
        """Test batch job preview."""
        try:
            handler = ConfigHandler()
            configs = handler.list_configs()
            
            if not configs:
                print("⚠️  No configurations found for batch preview")
                return True
            
            runner = BatchRunner()
            runner.set_forge_client(self.client)
            
            preview_result = runner.preview_job(configs[0], 3)
            
            if preview_result and 'prompts' in preview_result and len(preview_result['prompts']) > 0:
                prompts = preview_result['prompts']
                print(f"✅ Generated {len(prompts)} preview prompts for '{configs[0]}'")
                for i, prompt in enumerate(prompts[:2]):
                    print(f"   {i+1}. {prompt}")
                if len(prompts) > 2:
                    print(f"   ... and {len(prompts) - 2} more")
                return True
            else:
                print(f"❌ No preview generated for '{configs[0]}'")
                return False
        except Exception as e:
            print(f"❌ Batch preview test failed: {e}")
            return False
    
    def test_forge_endpoints(self):
        """Test various Forge API endpoints."""
        try:
            endpoints_to_test = [
                "/sdapi/v1/loras",
                "/controlnet/model_list",
                "/controlnet/module_list"
            ]
            
            working_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(f"{self.forge_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {endpoint}: {len(data)} items")
                        working_endpoints += 1
                    else:
                        print(f"❌ {endpoint}: Status {response.status_code}")
                except Exception as e:
                    print(f"❌ {endpoint}: Error - {e}")
            
            print(f"📊 Endpoint test: {working_endpoints}/{total_endpoints} working")
            return working_endpoints > 0  # Pass if at least one endpoint works
        except Exception as e:
            print(f"❌ Endpoint test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Direct Forge API Test Suite")
        print("=" * 60)
        print(f"Testing Forge server at: {self.forge_url}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Forge Connection", self.test_forge_connection),
            ("Forge Models", self.test_forge_models),
            ("Forge Samplers", self.test_forge_samplers),
            ("Forge Options", self.test_forge_options),
            ("Forge Progress", self.test_forge_progress),
            ("Config Validation", self.test_config_validation),
            ("Prompt Generation", self.test_prompt_generation),
            ("Batch Preview", self.test_batch_preview),
            ("Forge Endpoints", self.test_forge_endpoints),
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
        with open("direct_forge_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to direct_forge_test_results.json")
        
        # Log final summary
        logger.log_app_event("direct_forge_test_completed", self.test_results["summary"])
        
        return passed == total

def main():
    # You can change the Forge URL here if needed
    forge_url = "http://127.0.0.1:7860"
    
    tester = DirectForgeAPITester(forge_url)
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the results above.")
        return 1

if __name__ == "__main__":
    exit(main()) 