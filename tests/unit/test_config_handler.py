import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from core.config_handler import ConfigHandler


class TestConfigHandler(unittest.TestCase):
    """Test cases for ConfigHandler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, "configs")
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.handler = ConfigHandler(self.config_dir)
        
        # Create test config
        self.test_config = {
            "name": "Test Config",
            "description": "Test configuration",
            "model_type": "sd",
            "prompt_settings": {
                "base_prompt": "a beautiful __STYLE__ landscape",
                "negative_prompt": "blurry, low quality"
            },
            "wildcards": {
                "STYLE": "wildcards/style.txt"
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
                "output_dir": "outputs/test_config",
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
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_and_load_config(self):
        """Test saving and loading a configuration."""
        config_name = "test_config"
        
        # Save config
        self.handler.save_config(config_name, self.test_config)
        
        # Load config
        loaded_config = self.handler.load_config(config_name)
        
        # Check that config was loaded correctly
        self.assertEqual(loaded_config["name"], self.test_config["name"])
        self.assertEqual(loaded_config["model_type"], self.test_config["model_type"])
        self.assertEqual(loaded_config["generation_settings"]["steps"], 20)
    
    def test_list_configs(self):
        """Test listing available configurations."""
        # Save multiple configs
        self.handler.save_config("config1", self.test_config)
        self.handler.save_config("config2", self.test_config)
        
        configs = self.handler.list_configs()
        
        self.assertIn("config1", configs)
        self.assertIn("config2", configs)
        self.assertEqual(len(configs), 2)
    
    def test_create_config_from_template(self):
        """Test creating config from template."""
        # Create template
        template_path = os.path.join(self.config_dir, "template.json")
        with open(template_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Create config from template
        new_config = self.handler.create_config_from_template("new_config", "New description")
        
        self.assertEqual(new_config["name"], "new_config")
        self.assertEqual(new_config["description"], "New description")
        self.assertEqual(new_config["model_type"], "sd")
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Valid config should not raise exception
        try:
            self.handler._validate_config(self.test_config)
        except Exception as e:
            self.fail(f"Valid config raised exception: {e}")
        
        # Invalid config should raise exception
        invalid_config = self.test_config.copy()
        del invalid_config["name"]
        
        with self.assertRaises(ValueError):
            self.handler._validate_config(invalid_config)
    
    def test_extract_wildcards(self):
        """Test wildcard extraction from template."""
        template = "a __STYLE__ __LOCATION__ with __LIGHTING__"
        wildcards = self.handler.extract_wildcards_from_template(template)
        
        expected = ["STYLE", "LOCATION", "LIGHTING"]
        self.assertEqual(wildcards, expected)
    
    def test_validate_wildcards(self):
        """Test wildcard validation."""
        config = {
            'name': 'test_config',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a beautiful __STYLE__ __ANIMAL__ in __LOCATION__'
            },
            'model_settings': {},
            'generation_settings': {},
            'output_settings': {}
        }
        
        validation = self.handler.validate_wildcards(config)
        
        # Should have 3 wildcards in the template
        self.assertEqual(len(validation['missing']) + len(validation['available']), 3)
        
        # Check that the wildcards are correctly identified
        all_wildcards = validation['missing'] + validation['available']
        self.assertIn('STYLE', all_wildcards)
        self.assertIn('ANIMAL', all_wildcards)
        self.assertIn('LOCATION', all_wildcards)
    
    def test_get_config_summary(self):
        """Test getting configuration summary."""
        config_name = "test_config"
        self.handler.save_config(config_name, self.test_config)
        
        summary = self.handler.get_config_summary(self.test_config)
        
        self.assertEqual(summary["name"], "Test Config")
        self.assertEqual(summary["model_type"], "sd")
        self.assertEqual(summary["steps"], 20)
        self.assertEqual(summary["width"], 512)
        self.assertEqual(summary["height"], 512)
    
    def test_delete_config(self):
        """Test deleting a configuration."""
        config_name = "test_config"
        self.handler.save_config(config_name, self.test_config)
        
        # Verify config exists
        self.assertIn(config_name, self.handler.list_configs())
        
        # Delete config
        self.handler.delete_config(config_name)
        
        # Verify config is deleted
        self.assertNotIn(config_name, self.handler.list_configs())
    
    def test_load_nonexistent_config(self):
        """Test loading a nonexistent configuration."""
        with self.assertRaises(FileNotFoundError):
            self.handler.load_config("nonexistent")
    
    def test_save_config_with_defaults(self):
        """Test saving config with default values applied."""
        minimal_config = {
            "name": "Minimal Config",
            "model_type": "sd",
            "prompt_settings": {
                "base_prompt": "test prompt",
                "negative_prompt": ""
            },
            "wildcards": {},
            "generation_settings": {
                "steps": 20
            },
            "model_settings": {},
            "output_settings": {},
            "wildcard_settings": {},
            "alwayson_scripts": {}
        }
        
        config_name = "minimal_config"
        self.handler.save_config(config_name, minimal_config)
        
        loaded_config = self.handler.load_config(config_name)
        
        # Check that the config was loaded correctly
        self.assertEqual(loaded_config["name"], "Minimal Config")
        self.assertEqual(loaded_config["model_type"], "sd")
        self.assertEqual(loaded_config["generation_settings"]["steps"], 20)
        
        # Check that the config structure is valid
        self.assertIn("generation_settings", loaded_config)
        self.assertIn("model_settings", loaded_config)
        self.assertIn("prompt_settings", loaded_config)
    
    def test_merge_dicts(self):
        """Test dictionary merging functionality."""
        defaults = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": 4
        }
        
        config = {
            "a": 10,
            "b": {"c": 20},
            "f": 5
        }
        
        merged = self.handler._merge_dicts(defaults, config)
        
        self.assertEqual(merged["a"], 10)  # Overridden
        self.assertEqual(merged["b"]["c"], 20)  # Overridden
        self.assertEqual(merged["b"]["d"], 3)  # Preserved
        self.assertEqual(merged["e"], 4)  # Preserved
        self.assertEqual(merged["f"], 5)  # Added


if __name__ == '__main__':
    unittest.main() 