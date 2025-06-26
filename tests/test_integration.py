import unittest
import tempfile
import os
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
import io
import base64
import shutil

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from core.forge_api import ForgeAPIClient
from core.config_handler import ConfigHandler
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.batch_runner import BatchRunner
from core.output_manager import OutputManager
from image_analyzer import ImageAnalyzer


class TestIntegration(unittest.TestCase):
    """Integration tests for the Forge API Tool."""
    
    @classmethod
    def setUpClass(cls):
        os.makedirs('wildcards', exist_ok=True)
        with open('wildcards/style.txt', 'w') as f:
            f.write('realistic\nanime\ncyberpunk\nphotorealistic\n')
        with open('wildcards/animal.txt', 'w') as f:
            f.write('cat\ndog\nbird\nfox\n')
        with open('wildcards/location.txt', 'w') as f:
            f.write('forest\ncity\nmountain\nbeach\n')
        with open('wildcards/lighting.txt', 'w') as f:
            f.write('sunset\ndawn\nnight\nmidday\n')
    
    @classmethod
    def tearDownClass(cls):
        # Clean up wildcard files after tests
        if os.path.exists('wildcards/style.txt'):
            os.remove('wildcards/style.txt')
        if os.path.exists('wildcards/animal.txt'):
            os.remove('wildcards/animal.txt')
        if os.path.exists('wildcards/location.txt'):
            os.remove('wildcards/location.txt')
        if os.path.exists('wildcards/lighting.txt'):
            os.remove('wildcards/lighting.txt')
        # Optionally remove the wildcards directory if empty
        if os.path.exists('wildcards') and not os.listdir('wildcards'):
            os.rmdir('wildcards')
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Set up directories
        self.config_dir = os.path.join(self.temp_dir, "configs")
        self.wildcard_dir = os.path.join(self.temp_dir, "wildcards")
        self.output_dir = os.path.join(self.temp_dir, "outputs")
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.wildcard_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.config_handler = ConfigHandler(self.config_dir)
        self.wildcard_factory = WildcardManagerFactory()
        self.prompt_builder = PromptBuilder(self.wildcard_factory)
        self.output_manager = OutputManager(self.output_dir)
        self.image_analyzer = ImageAnalyzer()
        
        # Create test wildcard files
        self._create_test_wildcards()
        
        # Create test config
        self.test_config = self._create_test_config()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_wildcards(self):
        """Create test wildcard files."""
        # Style wildcard
        with open(os.path.join(self.wildcard_dir, "style.txt"), 'w') as f:
            f.write("realistic\nanime\ncyberpunk\nphotorealistic\n")
        
        # Location wildcard
        with open(os.path.join(self.wildcard_dir, "location.txt"), 'w') as f:
            f.write("forest\ncity\nmountain\nbeach\n")
        
        # Lighting wildcard
        with open(os.path.join(self.wildcard_dir, "lighting.txt"), 'w') as f:
            f.write("sunset\ndawn\nnight\nmidday\n")
    
    def _create_test_config(self):
        """Create a test configuration."""
        return {
            "name": "Integration Test Config",
            "description": "Configuration for integration testing",
            "model_type": "sd",
            "prompt_settings": {
                "base_prompt": "a beautiful __STYLE__ landscape of __LOCATION__ with __LIGHTING__",
                "negative_prompt": "blurry, low quality, distorted"
            },
            "wildcards": {
                "STYLE": os.path.join(self.wildcard_dir, "style.txt"),
                "LOCATION": os.path.join(self.wildcard_dir, "location.txt"),
                "LIGHTING": os.path.join(self.wildcard_dir, "lighting.txt")
            },
            "generation_settings": {
                "steps": 20,
                "width": 512,
                "height": 512,
                "batch_size": 1,
                "sampler": "Euler a",
                "cfg_scale": 7.0
            },
            "model_settings": {
                "checkpoint": "test_model.safetensors",
                "vae": "",
                "text_encoder": "",
                "gpu_weight": 1.0,
                "swap_method": "weight",
                "swap_location": "cpu"
            },
            "output_settings": {
                "output_dir": "outputs/integration_test",
                "filename_pattern": "{prompt_hash}_{seed}_{timestamp}",
                "save_metadata": True,
                "save_prompt_list": True
            },
            "wildcard_settings": {
                "randomization_mode": "smart_cycle",
                "cycle_length": 10,
                "shuffle_on_reset": True
            },
            "alwayson_scripts": {}
        }
    
    def test_config_wildcard_integration(self):
        """Test integration between config handler and wildcard manager."""
        config = {
            'name': 'integration_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {},
            'output_settings': {}
        }
        validation = self.config_handler.validate_wildcards(config)
        # Should have 3 wildcards in the template
        self.assertEqual(len(validation['missing']) + len(validation['available']), 3)
        all_wildcards = validation['missing'] + validation['available']
        self.assertIn('STYLE', all_wildcards)
        self.assertIn('ANIMAL', all_wildcards)
        self.assertIn('LOCATION', all_wildcards)
    
    def test_prompt_builder_integration(self):
        """Test integration between prompt builder and wildcard manager."""
        config = {
            'name': 'prompt_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __LOCATION__ with __LIGHTING__'
            },
            'model_settings': {},
            'generation_settings': {},
            'output_settings': {}
        }
        prompt = self.prompt_builder.build_prompt(config)
        # Should contain at least one wildcard value from the files
        style_present = any(item in prompt for item in ['anime', 'realistic', 'cyberpunk'])
        location_present = any(item in prompt for item in ['forest', 'city', 'mountain'])
        lighting_present = any(item in prompt for item in ['sunset', 'dawn', 'night'])
        self.assertTrue(style_present or location_present or lighting_present)
    
    def test_wildcard_usage_tracking(self):
        """Test that wildcard usage is properly tracked across components."""
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Generate prompts multiple times
        for _ in range(3):
            self.prompt_builder.generate_prompts(config, 2)
        
        # Get usage statistics
        usage_info = self.prompt_builder.get_wildcard_usage_info(config)
        
        # Check that usage is tracked
        for wildcard_name in ['STYLE', 'LOCATION', 'LIGHTING']:
            self.assertIn(wildcard_name, usage_info)
            self.assertGreater(usage_info[wildcard_name]['total_uses'], 0)
    
    def test_output_manager_integration(self):
        """Test integration with output manager."""
        config = {
            'name': 'output_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {'steps': 20, 'width': 512, 'height': 512, 'batch_size': 1, 'num_batches': 3},
            'output_settings': {}
        }
        # Save 3 dummy images
        for i in range(3):
            img = Image.new('RGB', (512, 512), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            self.output_manager.save_image(
                image_data,
                config['name'],
                f"prompt {i}",
                seed=i
            )
        summary = self.output_manager.get_output_summary(config['name'])
        self.assertEqual(summary['total_images'], 3)
        # Clean up test output directory
        test_dir = 'outputs/images/output_test'
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    def test_prompt_preview_integration(self):
        """Test prompt preview functionality."""
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Get prompt preview
        preview = self.prompt_builder.preview_prompts(config, 5)
        
        # Check preview
        self.assertEqual(len(preview), 5)
        
        # Check that preview doesn't consume wildcards
        preview2 = self.prompt_builder.preview_prompts(config, 5)
        self.assertEqual(len(preview2), 5)
        
        # Both previews should be the same (not consuming wildcards)
        self.assertEqual(preview, preview2)
    
    def test_wildcard_reset_integration(self):
        """Test wildcard reset functionality."""
        config = {
            'name': 'reset_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {},
            'output_settings': {}
        }
        # Should not raise error even if wildcards are empty
        self.prompt_builder.reset_wildcards(config)
    
    def test_config_validation_integration(self):
        """Test configuration validation with wildcards."""
        config = {
            'name': 'integration_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {'steps': 20, 'width': 512, 'height': 512, 'batch_size': 1, 'num_batches': 1},
            'output_settings': {}
        }
        validation = self.config_handler.validate_wildcards(config)
        self.assertEqual(len(validation['missing']), 0)
        self.assertGreaterEqual(len(validation['available']), 3)
    
    def test_prompt_stats_integration(self):
        """Test prompt statistics integration."""
        config = {
            'name': 'stats_test',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {},
            'output_settings': {}
        }
        stats = self.prompt_builder.get_prompt_stats(config)
        self.assertGreater(stats['total_wildcard_items'], 0)
    
    def test_multiple_configs_integration(self):
        """Test working with multiple configurations."""
        # Create second config
        config2 = self.test_config.copy()
        config2['name'] = "Integration Test Config 2"
        config2['prompt_settings']['base_prompt'] = "a __STYLE__ portrait in __LIGHTING__"
        del config2['wildcards']['LOCATION']
        
        # Save both configs
        self.config_handler.save_config("config1", self.test_config)
        self.config_handler.save_config("config2", config2)
        
        # List configs
        configs = self.config_handler.list_configs()
        self.assertIn("config1", configs)
        self.assertIn("config2", configs)
        
        # Test that each config works independently
        for config_name in ["config1", "config2"]:
            config = self.config_handler.load_config(config_name)
            prompts = self.prompt_builder.generate_prompts(config, 2)
            self.assertEqual(len(prompts), 2)
    
    def test_error_handling_integration(self):
        """Test error handling across components."""
        # Test with invalid wildcard path
        invalid_config = self.test_config.copy()
        invalid_config['wildcards']['invalid'] = "nonexistent.txt"
        
        # Should handle gracefully
        try:
            prompts = self.prompt_builder.generate_prompts(invalid_config, 1)
            # Should still work, just with missing wildcard
            self.assertEqual(len(prompts), 1)
        except Exception as e:
            self.fail(f"Should handle missing wildcard gracefully: {e}")


if __name__ == '__main__':
    unittest.main() 