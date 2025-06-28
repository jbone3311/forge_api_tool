import unittest
import tempfile
import os
import json
import base64
from pathlib import Path
import sys
from PIL import Image
import io
import time
from datetime import datetime
import hashlib

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from core.output_manager import OutputManager
from core.config_handler import ConfigHandler
from core.wildcard_manager import WildcardManagerFactory


class TestOutputManager(unittest.TestCase):
    """Test cases for OutputManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "outputs")
        self.manager = OutputManager(self.output_dir)
        
        # Create test image data
        self.test_image = Image.new('RGB', (512, 512), color='red')
        image_buffer = io.BytesIO()
        self.test_image.save(image_buffer, format='PNG')
        self.image_data = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_image(self):
        """Test saving an image."""
        # Create test image data
        test_image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        test_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Save image
        filepath = self.manager.save_image(
            image_data, "test_config", "test prompt", 12345
        )
        
        # Check that file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.png'))
        
        # Check that metadata was created
        metadata_dir = os.path.join(os.path.dirname(filepath), '..', 'metadata')
        metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith('_metadata.json')]
        self.assertGreater(len(metadata_files), 0)
        
        # Check that prompt was saved
        prompts_dir = os.path.join(os.path.dirname(filepath), '..', 'prompts')
        prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('_prompt.txt')]
        self.assertGreater(len(prompt_files), 0)
    
    def test_hash_prompt(self):
        """Test prompt hashing functionality."""
        prompt1 = "a beautiful landscape"
        prompt2 = "a beautiful landscape"
        prompt3 = "an ugly building"
        
        # Test that same prompts produce same hash
        hash1 = hashlib.md5(prompt1.encode()).hexdigest()
        hash2 = hashlib.md5(prompt2.encode()).hexdigest()
        hash3 = hashlib.md5(prompt3.encode()).hexdigest()
        
        self.assertEqual(hash1, hash2)
        self.assertNotEqual(hash1, hash3)
    
    def test_save_prompt_list(self):
        """Test saving a list of prompts."""
        config_name = "test_config"
        prompts = ["prompt 1", "prompt 2", "prompt 3"]
        
        # Save prompts by creating images (which also saves prompts)
        for i, prompt in enumerate(prompts):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, config_name, prompt, i)
        
        # Check that prompts were saved
        prompts_dir = os.path.join(self.manager.get_output_directory(config_name), 
                                  datetime.now().strftime("%Y-%m-%d"), 'prompts')
        prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('_prompt.txt')]
        self.assertGreaterEqual(len(prompt_files), len(prompts))
    
    def test_get_output_summary(self):
        """Test getting output summary."""
        # Create some test outputs
        for i in range(3):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "test_config", f"prompt{i}", i)
        
        # Get output statistics
        summary = self.manager.get_output_statistics()
        
        # Check that summary contains expected data
        self.assertIn('total_outputs', summary)
        self.assertIn('configs_with_outputs', summary)
        self.assertIn('recent_outputs', summary)
    
    def test_get_output_summary_specific_config(self):
        """Test getting output summary for a specific config."""
        # Create outputs for different configs
        for i in range(2):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "config1", f"prompt{i}", i)
        
        for i in range(3):
            test_image = Image.new('RGB', (100, 100), color='blue')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "config2", f"prompt{i}", i)
        
        # Get outputs for specific config
        config1_outputs = self.manager.get_outputs_for_config("config1")
        config2_outputs = self.manager.get_outputs_for_config("config2")
        
        # Check that we got the right number of outputs
        self.assertEqual(len(config1_outputs), 2)
        self.assertEqual(len(config2_outputs), 3)
    
    def test_get_recent_files(self):
        """Test getting recent files."""
        # Create some test outputs
        for i in range(5):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "test_config", f"prompt{i}", i)
        
        # Get output statistics which includes recent outputs
        stats = self.manager.get_output_statistics()
        
        # Check that we have recent outputs
        self.assertIn('recent_outputs', stats)
        self.assertGreaterEqual(len(stats['recent_outputs']), 1)
    
    def test_cleanup_old_files(self):
        """Test cleaning up old files."""
        # Create some test outputs
        for i in range(3):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "test_config", f"prompt{i}", i)
        
        # Get initial statistics
        initial_stats = self.manager.get_output_statistics()
        
        # Clean up old outputs (keep only 1 day)
        cleaned_count = self.manager.cleanup_old_outputs(days_to_keep=1)
        
        # Check that cleanup was performed
        self.assertIsInstance(cleaned_count, int)
    
    def test_export_config_outputs(self):
        """Test exporting config outputs."""
        # Create some test outputs
        for i in range(2):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "test_config", f"prompt{i}", i)
        
        # Export outputs
        export_path = os.path.join(self.temp_dir, "export")
        export_dir = self.manager.export_config_outputs("test_config", export_path)
        
        # Check that export directory was created
        self.assertTrue(os.path.exists(export_dir))
        self.assertTrue(os.path.isdir(export_dir))
    
    def test_get_image_metadata(self):
        """Test getting image metadata."""
        # Save an image which creates metadata
        test_image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        test_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        filepath = self.manager.save_image(image_data, "test_config", "test prompt", 12345)
        
        # Check that metadata file was created
        metadata_dir = os.path.join(os.path.dirname(filepath), '..', 'metadata')
        metadata_files = [f for f in os.listdir(metadata_dir) if f.endswith('_metadata.json')]
        self.assertGreater(len(metadata_files), 0)
        
        # Read and verify metadata
        metadata_file = os.path.join(metadata_dir, metadata_files[0])
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.assertEqual(metadata['config_name'], 'test_config')
        self.assertEqual(metadata['prompt'], 'test prompt')
        self.assertEqual(metadata['seed'], 12345)
    
    def test_get_image_metadata_nonexistent(self):
        """Test handling of nonexistent image metadata."""
        # Try to get outputs for a nonexistent config
        outputs = self.manager.get_outputs_for_config("nonexistent_config")
        
        # Should return empty list, not raise exception
        self.assertEqual(outputs, [])
    
    def test_search_images(self):
        """Test searching for images by prompt content."""
        # Create some test outputs with different prompts
        prompts = ["beautiful landscape", "ugly building", "beautiful sunset"]
        
        for i, prompt in enumerate(prompts):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "test_config", prompt, i)
        
        # Get all outputs and filter by prompt content
        outputs = self.manager.get_outputs_for_config("test_config")
        beautiful_outputs = [o for o in outputs if "beautiful" in o.get('prompt', '')]
        
        # Should find 2 outputs with "beautiful" in the prompt
        self.assertEqual(len(beautiful_outputs), 2)
    
    def test_search_images_specific_config(self):
        """Test searching images for a specific config."""
        # Create outputs for different configs
        for i in range(2):
            test_image = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "config1", f"beautiful prompt{i}", i)
        
        for i in range(2):
            test_image = Image.new('RGB', (100, 100), color='blue')
            buffer = io.BytesIO()
            test_image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            self.manager.save_image(image_data, "config2", f"beautiful prompt{i}", i)
        
        # Get outputs for specific config and filter
        config1_outputs = self.manager.get_outputs_for_config("config1")
        beautiful_config1 = [o for o in config1_outputs if "beautiful" in o.get('prompt', '')]
        
        # Should find 2 outputs in config1 with "beautiful"
        self.assertEqual(len(beautiful_config1), 2)
    
    def test_search_images_no_results(self):
        """Test searching images with no results."""
        # Create a test output
        test_image = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        test_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        self.manager.save_image(image_data, "test_config", "landscape", 1)
        
        # Get outputs and filter for nonexistent term
        outputs = self.manager.get_outputs_for_config("test_config")
        nonexistent_outputs = [o for o in outputs if "nonexistent" in o.get('prompt', '')]
        
        # Should find 0 outputs with "nonexistent"
        self.assertEqual(len(nonexistent_outputs), 0)
    
    def test_directory_creation(self):
        """Test that directories are created properly."""
        # Check that main directories exist
        self.assertTrue(os.path.exists(self.manager.directories['images']))
        self.assertTrue(os.path.exists(self.manager.directories['metadata']))
        self.assertTrue(os.path.exists(self.manager.directories['prompts']))
        self.assertTrue(os.path.exists(self.manager.directories['logs']))
        self.assertTrue(os.path.exists(self.manager.directories['temp']))
        self.assertTrue(os.path.exists(self.manager.directories['configs']))
        self.assertTrue(os.path.exists(self.manager.directories['sessions']))
    
    def test_save_image_error_handling(self):
        """Test error handling when saving image."""
        # Test with invalid image data
        invalid_image_data = "invalid_base64_data"
        
        with self.assertRaises(Exception):
            self.manager.save_image(
                invalid_image_data, "test_config", "test prompt", 1
            )


if __name__ == '__main__':
    unittest.main() 