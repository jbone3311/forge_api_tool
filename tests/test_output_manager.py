import unittest
import tempfile
import os
import json
import base64
from pathlib import Path
import sys
from PIL import Image
import io

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from output_manager import OutputManager


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
        """Test saving image and metadata."""
        config_name = "test_config"
        prompt = "a beautiful landscape"
        seed = 12345
        metadata = {"test": "data"}
        
        image_path, metadata_path = self.manager.save_image(
            self.image_data, config_name, prompt, seed, metadata
        )
        
        # Check that files were created
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(os.path.exists(metadata_path))
        
        # Check image file
        saved_image = Image.open(image_path)
        self.assertEqual(saved_image.size, (512, 512))
        
        # Check metadata file
        with open(metadata_path, 'r') as f:
            saved_metadata = json.load(f)
        
        self.assertEqual(saved_metadata['config_name'], config_name)
        self.assertEqual(saved_metadata['prompt'], prompt)
        self.assertEqual(saved_metadata['seed'], seed)
        self.assertEqual(saved_metadata['metadata']['test'], 'data')
    
    def test_hash_prompt(self):
        """Test prompt hashing functionality."""
        prompt1 = "a beautiful landscape"
        prompt2 = "a beautiful landscape"
        prompt3 = "a different landscape"
        
        hash1 = self.manager._hash_prompt(prompt1)
        hash2 = self.manager._hash_prompt(prompt2)
        hash3 = self.manager._hash_prompt(prompt3)
        
        self.assertEqual(hash1, hash2)  # Same prompt should have same hash
        self.assertNotEqual(hash1, hash3)  # Different prompts should have different hashes
        self.assertEqual(len(hash1), 8)  # Hash should be 8 characters
    
    def test_save_prompt_list(self):
        """Test saving prompt list."""
        config_name = "test_config"
        prompts = [
            {"prompt": "prompt1", "seed": 1},
            {"prompt": "prompt2", "seed": 2},
            {"prompt": "prompt3", "seed": 3}
        ]
        
        prompt_path = self.manager.save_prompt_list(config_name, prompts)
        
        # Check that file was created
        self.assertTrue(os.path.exists(prompt_path))
        
        # Check prompt list content
        with open(prompt_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['config_name'], config_name)
        self.assertEqual(saved_data['total_prompts'], 3)
        self.assertEqual(len(saved_data['prompts']), 3)
    
    def test_get_output_summary(self):
        """Test getting output summary."""
        # Save some test images
        config_name = "test_config"
        for i in range(3):
            self.manager.save_image(
                self.image_data, config_name, f"prompt{i}", i
            )
        
        summary = self.manager.get_output_summary()
        
        self.assertEqual(summary['total_images'], 3)
        self.assertEqual(summary['total_configs'], 1)
        self.assertIn(config_name, summary['configs'])
        self.assertEqual(summary['configs'][config_name]['images'], 3)
    
    def test_get_output_summary_specific_config(self):
        """Test getting output summary for specific config."""
        # Save images for multiple configs
        self.manager.save_image(self.image_data, "config1", "prompt1", 1)
        self.manager.save_image(self.image_data, "config2", "prompt2", 2)
        self.manager.save_image(self.image_data, "config2", "prompt3", 3)
        
        summary = self.manager.get_output_summary("config1")
        
        self.assertEqual(summary['total_images'], 1)
        self.assertEqual(summary['total_configs'], 1)
        self.assertIn("config1", summary['configs'])
        self.assertNotIn("config2", summary['configs'])
    
    def test_get_recent_files(self):
        """Test getting recent files."""
        # Save some test images
        config_name = "test_config"
        for i in range(5):
            self.manager.save_image(
                self.image_data, config_name, f"prompt{i}", i
            )
        
        summary = self.manager.get_output_summary()
        recent_files = summary['recent_files']
        
        self.assertLessEqual(len(recent_files), 10)  # Should be limited to 10
        self.assertGreater(len(recent_files), 0)
        
        # Check that files have required fields
        for file_info in recent_files:
            self.assertIn('path', file_info)
            self.assertIn('config', file_info)
            self.assertIn('modified', file_info)
    
    def test_cleanup_old_files(self):
        """Test cleaning up old files."""
        # Save some test images
        config_name = "test_config"
        for i in range(3):
            self.manager.save_image(
                self.image_data, config_name, f"prompt{i}", i
            )
        
        # Get initial count
        initial_summary = self.manager.get_output_summary()
        initial_count = initial_summary['total_images']
        
        # Clean up files (should not remove recent files)
        cleaned_files = self.manager.cleanup_old_files(days_to_keep=30)
        
        # Check that no files were cleaned (they're recent)
        self.assertEqual(len(cleaned_files), 0)
        
        # Check that all files still exist
        final_summary = self.manager.get_output_summary()
        self.assertEqual(final_summary['total_images'], initial_count)
    
    def test_export_config_outputs(self):
        """Test exporting config outputs."""
        # Save some test images
        config_name = "test_config"
        for i in range(2):
            self.manager.save_image(
                self.image_data, config_name, f"prompt{i}", i
            )
        
        # Export outputs
        export_path = os.path.join(self.temp_dir, "export")
        export_dir = self.manager.export_config_outputs(config_name, export_path)
        
        # Check that export directory was created
        self.assertTrue(os.path.exists(export_dir))
        
        # Check that images were exported
        images_dir = os.path.join(export_dir, "images")
        self.assertTrue(os.path.exists(images_dir))
        
        # Check that metadata was exported
        metadata_dir = os.path.join(export_dir, "metadata")
        self.assertTrue(os.path.exists(metadata_dir))
        
        # Check export summary
        summary_path = os.path.join(export_dir, "export_summary.json")
        self.assertTrue(os.path.exists(summary_path))
        
        with open(summary_path, 'r') as f:
            summary = json.load(f)
        
        self.assertEqual(summary['config_name'], config_name)
        self.assertEqual(summary['images_count'], 2)
    
    def test_get_image_metadata(self):
        """Test getting image metadata."""
        # Save a test image
        config_name = "test_config"
        prompt = "test prompt"
        seed = 12345
        
        image_path, _ = self.manager.save_image(
            self.image_data, config_name, prompt, seed
        )
        
        # Get metadata
        metadata = self.manager.get_image_metadata(image_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['config_name'], config_name)
        self.assertEqual(metadata['prompt'], prompt)
        self.assertEqual(metadata['seed'], seed)
    
    def test_get_image_metadata_nonexistent(self):
        """Test getting metadata for nonexistent image."""
        metadata = self.manager.get_image_metadata("nonexistent/path.png")
        self.assertIsNone(metadata)
    
    def test_search_images(self):
        """Test searching images by prompt content."""
        # Save test images with different prompts
        config_name = "test_config"
        self.manager.save_image(self.image_data, config_name, "beautiful landscape", 1)
        self.manager.save_image(self.image_data, config_name, "ugly building", 2)
        self.manager.save_image(self.image_data, config_name, "beautiful sunset", 3)
        
        # Search for "beautiful"
        results = self.manager.search_images("beautiful")
        
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("beautiful", result['prompt'].lower())
    
    def test_search_images_specific_config(self):
        """Test searching images in specific config."""
        # Save images in different configs
        self.manager.save_image(self.image_data, "config1", "beautiful landscape", 1)
        self.manager.save_image(self.image_data, "config2", "beautiful building", 2)
        
        # Search in config1 only
        results = self.manager.search_images("beautiful", "config1")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['config'], "config1")
    
    def test_search_images_no_results(self):
        """Test searching with no results."""
        # Save an image
        self.manager.save_image(self.image_data, "test_config", "landscape", 1)
        
        # Search for something that doesn't exist
        results = self.manager.search_images("nonexistent")
        
        self.assertEqual(len(results), 0)
    
    def test_directory_creation(self):
        """Test that directories are created properly."""
        # Check that all required directories exist
        self.assertTrue(os.path.exists(self.manager.images_dir))
        self.assertTrue(os.path.exists(self.manager.metadata_dir))
        self.assertTrue(os.path.exists(self.manager.prompts_dir))
        self.assertTrue(os.path.exists(self.manager.logs_dir))
    
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