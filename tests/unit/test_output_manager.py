#!/usr/bin/env python3
"""
Unit tests for OutputManager class.
Tests the new Automatic1111-style output management system.
"""

import unittest
import tempfile
import os
import json
import base64
import io
from datetime import datetime
from PIL import Image, PngImagePlugin
import sys

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.output_manager import OutputManager


class TestOutputManager(unittest.TestCase):
    """Test cases for OutputManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = OutputManager(self.temp_dir)
        
        # Create test image data
        self.test_image = Image.new('RGB', (512, 512), color='red')
        img_buffer = io.BytesIO()
        self.test_image.save(img_buffer, format='PNG')
        self.image_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Test generation settings
        self.generation_settings = {
            'steps': 20,
            'cfg_scale': 7.0,
            'sampler': 'Euler a',
            'width': 512,
            'height': 512,
            'negative_prompt': 'blurry, low quality'
        }
        
        # Test model settings
        self.model_settings = {
            'checkpoint': 'test_model.safetensors',
            'vae': 'test_vae.safetensors',
            'model_hash': 'abc123',
            'vae_hash': 'def456'
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test OutputManager initialization."""
        self.assertIsInstance(self.manager, OutputManager)
        self.assertEqual(self.manager.base_output_dir, self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_get_output_directory(self):
        """Test getting output directory for specific date."""
        # Test with specific date
        test_date = "2024-01-15"
        output_dir = self.manager.get_output_directory(test_date)
        expected_dir = os.path.join(self.temp_dir, test_date)
        self.assertEqual(output_dir, expected_dir)
        self.assertTrue(os.path.exists(output_dir))
        
        # Test with today's date
        today_dir = self.manager.get_output_directory()
        today_date = datetime.now().strftime("%Y-%m-%d")
        expected_today_dir = os.path.join(self.temp_dir, today_date)
        self.assertEqual(today_dir, expected_today_dir)
        self.assertTrue(os.path.exists(today_dir))
    
    def test_save_image(self):
        """Test saving image with embedded metadata."""
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        
        filepath = self.manager.save_image(
            self.image_data, 
            config_name, 
            prompt, 
            seed,
            self.generation_settings,
            self.model_settings
        )
        
        # Check file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.png'))
        
        # Check filename format
        filename = os.path.basename(filepath)
        self.assertRegex(filename, r'\d{8}_\d{6}_\d{8}\.png')
        
        # Check metadata was embedded
        metadata = self.manager.extract_metadata_from_image(filepath)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['prompt'], prompt)
        self.assertEqual(metadata['seed'], seed)
        self.assertEqual(metadata['config_name'], config_name)
        self.assertEqual(metadata['steps'], 20)
        self.assertEqual(metadata['cfg_scale'], 7.0)
        self.assertEqual(metadata['sampler_name'], 'Euler a')
        self.assertEqual(metadata['model_name'], 'test_model.safetensors')
        self.assertEqual(metadata['vae_name'], 'test_vae.safetensors')
    
    def test_save_image_with_data_url(self):
        """Test saving image with data URL format."""
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        
        # Create data URL
        data_url = f"data:image/png;base64,{self.image_data}"
        
        filepath = self.manager.save_image(
            data_url, 
            config_name, 
            prompt, 
            seed,
            self.generation_settings,
            self.model_settings
        )
        
        self.assertTrue(os.path.exists(filepath))
        
        # Check metadata
        metadata = self.manager.extract_metadata_from_image(filepath)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['prompt'], prompt)
    
    def test_get_outputs_for_date(self):
        """Test getting outputs for a specific date."""
        # Save some test images
        config_name = "test_config"
        prompt = "a beautiful landscape"
        
        for i in range(3):
            seed = 1000 + i
            self.manager.save_image(
                self.image_data, 
                config_name, 
                f"{prompt} {i}", 
                seed,
                self.generation_settings,
                self.model_settings
            )
        
        # Get outputs for today
        today = datetime.now().strftime("%Y-%m-%d")
        outputs = self.manager.get_outputs_for_date(today)
        
        self.assertEqual(len(outputs), 3)
        
        # Check output structure
        for output in outputs:
            self.assertIn('filename', output)
            self.assertIn('filepath', output)
            self.assertIn('date', output)
            self.assertIn('prompt', output)
            self.assertIn('seed', output)
            self.assertIn('config_name', output)
            self.assertEqual(output['date'], today)
            self.assertEqual(output['config_name'], config_name)
    
    def test_get_outputs_for_config(self):
        """Test getting outputs for a specific configuration."""
        # Save images with different configs
        configs = ["config1", "config2", "config1"]
        prompt = "a beautiful landscape"
        
        for i, config_name in enumerate(configs):
            seed = 1000 + i
            self.manager.save_image(
                self.image_data, 
                config_name, 
                f"{prompt} {i}", 
                seed,
                self.generation_settings,
                self.model_settings
            )
        
        # Get outputs for config1
        config1_outputs = self.manager.get_outputs_for_config("config1")
        self.assertEqual(len(config1_outputs), 2)
        
        # Check all outputs belong to config1
        for output in config1_outputs:
            self.assertEqual(output['config_name'], "config1")
        
        # Get outputs for config2
        config2_outputs = self.manager.get_outputs_for_config("config2")
        self.assertEqual(len(config2_outputs), 1)
        self.assertEqual(config2_outputs[0]['config_name'], "config2")
    
    def test_extract_metadata_from_image(self):
        """Test extracting metadata from image file."""
        # Save test image
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        
        filepath = self.manager.save_image(
            self.image_data, 
            config_name, 
            prompt, 
            seed,
            self.generation_settings,
            self.model_settings
        )
        
        # Extract metadata
        metadata = self.manager.extract_metadata_from_image(filepath)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['prompt'], prompt)
        self.assertEqual(metadata['seed'], seed)
        self.assertEqual(metadata['config_name'], config_name)
        self.assertEqual(metadata['steps'], 20)
        self.assertEqual(metadata['cfg_scale'], 7.0)
        self.assertEqual(metadata['model_name'], 'test_model.safetensors')
    
    def test_get_output_statistics(self):
        """Test getting output statistics."""
        # Save some test images
        configs = ["config1", "config2", "config1"]
        prompt = "a beautiful landscape"
        
        for i, config_name in enumerate(configs):
            seed = 1000 + i
            self.manager.save_image(
                self.image_data, 
                config_name, 
                f"{prompt} {i}", 
                seed,
                self.generation_settings,
                self.model_settings
            )
        
        # Get statistics
        stats = self.manager.get_output_statistics()
        
        self.assertIn('total_outputs', stats)
        self.assertIn('total_size_mb', stats)
        self.assertIn('configs_with_outputs', stats)
        self.assertIn('date_breakdown', stats)
        
        self.assertEqual(stats['total_outputs'], 3)
        self.assertIn('config1', stats['configs_with_outputs'])
        self.assertIn('config2', stats['configs_with_outputs'])
    
    def test_cleanup_old_outputs(self):
        """Test cleaning up old outputs."""
        # This test would require time manipulation to be comprehensive
        # For now, just test the method doesn't crash
        cleaned_count = self.manager.cleanup_old_outputs(days_to_keep=30)
        self.assertIsInstance(cleaned_count, int)
        self.assertGreaterEqual(cleaned_count, 0)
    
    def test_delete_output(self):
        """Test deleting a specific output."""
        # Save test image
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        
        filepath = self.manager.save_image(
            self.image_data, 
            config_name, 
            prompt, 
            seed,
            self.generation_settings,
            self.model_settings
        )
        
        # Verify file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Delete the file
        success = self.manager.delete_output(filepath)
        self.assertTrue(success)
        
        # Verify file was deleted
        self.assertFalse(os.path.exists(filepath))
    
    def test_export_outputs(self):
        """Test exporting outputs to a different location."""
        # Save test image
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        
        self.manager.save_image(
            self.image_data, 
            config_name, 
            prompt, 
            seed,
            self.generation_settings,
            self.model_settings
        )
        
        # Create export directory
        export_dir = os.path.join(self.temp_dir, "export")
        
        # Export all outputs
        export_path = self.manager.export_outputs(export_dir)
        
        self.assertTrue(os.path.exists(export_path))
        
        # Check that exported files exist
        exported_files = [f for f in os.listdir(export_path) if f.endswith('.png')]
        self.assertGreater(len(exported_files), 0)
    
    def test_error_handling(self):
        """Test error handling with invalid inputs."""
        # Test with invalid image data
        with self.assertRaises(Exception):
            self.manager.save_image(
                "invalid_base64_data", 
                "test_config", 
                "test prompt", 
                12345
            )
        
        # Test with non-existent file for metadata extraction
        metadata = self.manager.extract_metadata_from_image("nonexistent_file.png")
        self.assertIsNone(metadata)
    
    def test_search_images(self):
        """Test searching images by various criteria."""
        # Save test images with different prompts
        prompts = [
            "a beautiful landscape with mountains",
            "a beautiful portrait of a person",
            "a beautiful cityscape at night"
        ]
        
        for i, prompt in enumerate(prompts):
            seed = 1000 + i
            self.manager.save_image(
                self.image_data, 
                "test_config", 
                prompt, 
                seed,
                self.generation_settings,
                self.model_settings
            )
        
        # Get all outputs
        today = datetime.now().strftime("%Y-%m-%d")
        outputs = self.manager.get_outputs_for_date(today)
        
        # Search for landscape images
        landscape_images = [o for o in outputs if 'landscape' in o['prompt'].lower()]
        self.assertEqual(len(landscape_images), 1)
        
        # Search for portrait images
        portrait_images = [o for o in outputs if 'portrait' in o['prompt'].lower()]
        self.assertEqual(len(portrait_images), 1)
        
        # Search for cityscape images
        cityscape_images = [o for o in outputs if 'cityscape' in o['prompt'].lower()]
        self.assertEqual(len(cityscape_images), 1)


if __name__ == '__main__':
    unittest.main() 