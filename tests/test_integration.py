import unittest
import tempfile
import os
import json
import sys
from pathlib import Path
from PIL import Image
import io
import base64

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from config_handler import ConfigHandler
from wildcard_manager import WildcardManagerFactory
from prompt_builder import PromptBuilder
from output_manager import OutputManager
from image_analyzer import ImageAnalyzer


class TestIntegration(unittest.TestCase):
    """Integration tests for the Forge API Tool."""
    
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
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        loaded_config = self.config_handler.load_config(config_name)
        
        # Validate wildcards
        validation = self.config_handler.validate_wildcards(loaded_config)
        
        # Check that all wildcards are available
        self.assertEqual(len(validation['available']), 3)
        self.assertEqual(len(validation['missing']), 0)
        self.assertIn('STYLE', validation['available'])
        self.assertIn('LOCATION', validation['available'])
        self.assertIn('LIGHTING', validation['available'])
    
    def test_prompt_builder_integration(self):
        """Test integration between prompt builder and wildcard manager."""
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Generate prompts
        prompts = self.prompt_builder.generate_prompts(config, 5)
        
        # Check that prompts were generated
        self.assertEqual(len(prompts), 5)
        
        # Check that each prompt contains wildcard replacements
        for prompt in prompts:
            self.assertNotIn('__STYLE__', prompt['prompt'])
            self.assertNotIn('__LOCATION__', prompt['prompt'])
            self.assertNotIn('__LIGHTING__', prompt['prompt'])
            
            # Check that wildcard values are from our test files
            style_values = ["realistic", "anime", "cyberpunk", "photorealistic"]
            location_values = ["forest", "city", "mountain", "beach"]
            lighting_values = ["sunset", "dawn", "night", "midday"]
            
            # At least one wildcard value should be present
            style_present = any(style in prompt['prompt'] for style in style_values)
            location_present = any(location in prompt['prompt'] for location in location_values)
            lighting_present = any(lighting in prompt['prompt'] for lighting in lighting_values)
            
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
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Generate prompts
        prompts = self.prompt_builder.generate_prompts(config, 3)
        
        # Create proper test image data
        test_image = Image.new('RGB', (512, 512), color='red')
        image_buffer = io.BytesIO()
        test_image.save(image_buffer, format='PNG')
        image_data = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        
        for i, prompt_info in enumerate(prompts):
            self.output_manager.save_image(
                image_data,
                config_name,
                prompt_info['prompt'],
                prompt_info.get('seed', i)
            )
        
        # Check output summary
        summary = self.output_manager.get_output_summary(config_name)
        
        self.assertEqual(summary['total_images'], 3)
        self.assertEqual(summary['total_configs'], 1)
        self.assertIn(config_name, summary['configs'])
        self.assertEqual(summary['configs'][config_name]['images'], 3)
    
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
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Generate some prompts
        initial_prompts = self.prompt_builder.generate_prompts(config, 3)
        
        # Reset wildcards
        self.prompt_builder.reset_wildcards(config)
        
        # Generate more prompts
        reset_prompts = self.prompt_builder.generate_prompts(config, 3)
        
        # Check that prompts are different after reset
        # (Note: this is probabilistic, but very likely to be different)
        self.assertNotEqual(initial_prompts, reset_prompts)
    
    def test_config_validation_integration(self):
        """Test configuration validation with wildcards."""
        # Test valid config
        valid_config = self.test_config.copy()
        validation = self.config_handler.validate_wildcards(valid_config)
        self.assertEqual(len(validation['missing']), 0)
        
        # Test invalid config (wildcard in template but not in wildcards dict)
        invalid_config = self.test_config.copy()
        invalid_config['prompt_settings']['base_prompt'] = "a beautiful __STYLE__ landscape with __MISSING_WILDCARD__"
        
        # Debug: print the config to see what's happening
        print(f"Invalid config wildcards: {invalid_config.get('wildcards', {})}")
        print(f"Invalid config prompt: {invalid_config['prompt_settings']['base_prompt']}")
        
        validation = self.config_handler.validate_wildcards(invalid_config)
        print(f"Validation result: {validation}")
        
        self.assertIn('MISSING_WILDCARD', validation['missing'])
    
    def test_prompt_stats_integration(self):
        """Test prompt statistics integration."""
        # Save config
        config_name = "integration_test"
        self.config_handler.save_config(config_name, self.test_config)
        
        # Load config
        config = self.config_handler.load_config(config_name)
        
        # Get prompt stats
        stats = self.prompt_builder.get_prompt_stats(config)
        
        # Check stats
        self.assertEqual(stats['wildcard_count'], 3)
        self.assertGreater(stats['total_wildcard_items'], 0)
        self.assertTrue(stats['validation']['valid'])
        self.assertGreater(stats['estimated_combinations'], 0)
    
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