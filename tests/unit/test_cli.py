#!/usr/bin/env python3
"""
Unit tests for the Forge API Tool CLI interface.
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the CLI class directly from the cli.py file
import cli
from cli import ForgeAPICLI


class TestForgeAPICLI(unittest.TestCase):
    """Test cases for the Forge API Tool CLI."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test directories
        os.makedirs('configs', exist_ok=True)
        os.makedirs('wildcards', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
        
        # Create test configuration
        self.test_config = {
            'name': 'test_config',
            'description': 'Test configuration',
            'model_type': 'sd',
            'generation_settings': {
                'steps': 20,
                'sampler': 'Euler a',
                'width': 512,
                'height': 512
            },
            'prompt_settings': {
                'base_prompt': 'a beautiful __STYLE__ portrait of __SUBJECT__',
                'negative_prompt': 'low quality, blurry'
            },
            'output_settings': {
                'output_dir': 'outputs/test',
                'save_metadata': True
            }
        }
        
        with open('configs/test_config.json', 'w') as f:
            json.dump(self.test_config, f)
        
        # Create test wildcard files
        with open('wildcards/style.txt', 'w') as f:
            f.write('realistic\nartistic\nphotographic\n')
        
        with open('wildcards/subject.txt', 'w') as f:
            f.write('man\nwoman\nchild\n')
        
        # Initialize CLI with mocked components
        with patch('cli.ForgeAPIClient'), \
             patch('cli.BatchRunner'), \
             patch('cli.OutputManager'), \
             patch('cli.WildcardManagerFactory'), \
             patch('cli.PromptBuilder'), \
             patch('cli.ImageAnalyzer'), \
             patch('cli.JobQueue'), \
             patch('cli.api_config'):
            
            self.cli = ForgeAPICLI()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test CLI initialization."""
        self.assertIsNotNone(self.cli)
        self.assertIsNotNone(self.cli.output_manager)
        self.assertIsNotNone(self.cli.wildcard_factory)
        self.assertIsNotNone(self.cli.prompt_builder)
        self.assertIsNotNone(self.cli.image_analyzer)
        self.assertIsNotNone(self.cli.job_queue)
    
    @patch('cli.ForgeAPIClient')
    def test_initialize_api_client_success(self, mock_client_class):
        """Test successful API client initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        cli = ForgeAPICLI()
        self.assertIsNotNone(cli.forge_client)
    
    @patch('cli.ForgeAPIClient')
    def test_initialize_api_client_failure(self, mock_client_class):
        """Test API client initialization failure."""
        mock_client_class.side_effect = Exception("Connection failed")
        
        cli = ForgeAPICLI()
        self.assertIsNone(cli.forge_client)
    
    @patch('cli.config_handler')
    def test_list_configs_success(self, mock_config_handler):
        """Test successful configuration listing."""
        mock_config_handler.list_configs.return_value = ['config1', 'config2']
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            self.cli.list_configs()
            
            # Verify configs were listed
            mock_config_handler.list_configs.assert_called_once()
            self.assertTrue(mock_print.called)
    
    @patch('cli.config_handler')
    def test_list_configs_empty(self, mock_config_handler):
        """Test configuration listing with no configs."""
        mock_config_handler.list_configs.return_value = []
        
        with patch('builtins.print') as mock_print:
            self.cli.list_configs()
            
            # Verify empty message was printed
            mock_print.assert_called_with("📋 No configurations found")
    
    @patch('cli.config_handler')
    def test_list_configs_error(self, mock_config_handler):
        """Test configuration listing with error."""
        mock_config_handler.list_configs.side_effect = Exception("Config error")
        
        with patch('builtins.print') as mock_print:
            self.cli.list_configs()
            
            # Verify error was handled
            mock_print.assert_called_with("❌ Error listing configurations: Config error")
    
    @patch('cli.config_handler')
    def test_show_config_success(self, mock_config_handler):
        """Test successful configuration display."""
        mock_config_handler.load_config.return_value = self.test_config
        
        with patch('builtins.print') as mock_print:
            self.cli.show_config('test_config')
            
            # Verify config was loaded and displayed
            mock_config_handler.load_config.assert_called_once_with('test_config')
            self.assertTrue(mock_print.called)
    
    @patch('cli.config_handler')
    def test_show_config_not_found(self, mock_config_handler):
        """Test configuration display with non-existent config."""
        mock_config_handler.load_config.side_effect = FileNotFoundError("Config not found")
        
        with patch('builtins.print') as mock_print:
            self.cli.show_config('nonexistent')
            
            # Verify error was handled
            mock_print.assert_called_with("❌ Error showing configuration: Config not found")
    
    @patch('cli.ForgeAPIClient')
    def test_test_connection_success(self, mock_client_class):
        """Test successful connection test."""
        mock_client = Mock()
        mock_client.test_connection.return_value = True
        mock_client_class.return_value = mock_client
        
        self.cli.forge_client = mock_client
        
        with patch('builtins.print') as mock_print:
            result = self.cli.test_connection()
            
            self.assertTrue(result)
            mock_print.assert_called_with("✅ API connection successful")
    
    @patch('cli.ForgeAPIClient')
    def test_test_connection_failure(self, mock_client_class):
        """Test failed connection test."""
        mock_client = Mock()
        mock_client.test_connection.return_value = False
        mock_client_class.return_value = mock_client
        
        self.cli.forge_client = mock_client
        
        with patch('builtins.print') as mock_print:
            result = self.cli.test_connection()
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ API connection failed")
    
    def test_test_connection_no_client(self):
        """Test connection test with no API client."""
        self.cli.forge_client = None
        
        with patch('builtins.print') as mock_print:
            result = self.cli.test_connection()
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ No API client configured")
    
    @patch('cli.config_handler')
    @patch('cli.ForgeAPIClient')
    def test_generate_single_success(self, mock_client_class, mock_config_handler):
        """Test successful single image generation."""
        mock_client = Mock()
        mock_client.generate_image.return_value = (True, "image_data", {"info": "test"})
        mock_client.save_image.return_value = True
        mock_client_class.return_value = mock_client
        
        mock_config_handler.load_config.return_value = self.test_config
        
        self.cli.forge_client = mock_client
        
        with patch('builtins.print') as mock_print:
            result = self.cli.generate_single('test_config', 'test prompt', 123)
            
            self.assertTrue(result)
            mock_client.generate_image.assert_called_once()
            mock_client.save_image.assert_called_once()
    
    @patch('cli.config_handler')
    @patch('cli.ForgeAPIClient')
    def test_generate_single_failure(self, mock_client_class, mock_config_handler):
        """Test failed single image generation."""
        mock_client = Mock()
        mock_client.generate_image.return_value = (False, None, {})
        mock_client_class.return_value = mock_client
        
        mock_config_handler.load_config.return_value = self.test_config
        
        self.cli.forge_client = mock_client
        
        with patch('builtins.print') as mock_print:
            result = self.cli.generate_single('test_config', 'test prompt')
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ Image generation failed")
    
    def test_generate_single_no_client(self):
        """Test single generation with no API client."""
        self.cli.forge_client = None
        
        with patch('builtins.print') as mock_print:
            result = self.cli.generate_single('test_config', 'test prompt')
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ No API client configured")
    
    @patch('cli.BatchRunner')
    def test_generate_batch_success(self, mock_batch_runner_class):
        """Test successful batch generation."""
        mock_batch_runner = Mock()
        mock_batch_runner_class.return_value = mock_batch_runner
        
        mock_job = Mock()
        mock_job.id = "test_job_123"
        mock_batch_runner.add_job.return_value = mock_job
        
        self.cli.batch_runner = mock_batch_runner
        
        with patch('builtins.print') as mock_print:
            result = self.cli.generate_batch('test_config', 4, 2)
            
            self.assertTrue(result)
            mock_batch_runner.add_job.assert_called_once_with('test_config', 4, 2)
            mock_batch_runner.start_processing.assert_called_once()
    
    def test_generate_batch_no_client(self):
        """Test batch generation with no API client."""
        self.cli.forge_client = None
        
        with patch('builtins.print') as mock_print:
            result = self.cli.generate_batch('test_config', 4, 2)
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ No API client configured")
    
    def test_list_outputs_empty(self):
        """Test listing outputs with empty directory."""
        with patch('builtins.print') as mock_print:
            self.cli.list_outputs()
            
            mock_print.assert_called_with("📁 No outputs found for date: today")
    
    def test_list_outputs_with_files(self):
        """Test listing outputs with files."""
        # Create test output files
        output_dir = os.path.join('outputs', '2024-01-01')
        os.makedirs(output_dir, exist_ok=True)
        
        # Create test image files
        test_files = ['image1.png', 'image2.jpg', 'document.txt']
        for filename in test_files:
            with open(os.path.join(output_dir, filename), 'w') as f:
                f.write('test content')
        
        with patch('builtins.print') as mock_print:
            self.cli.list_outputs('2024-01-01')
            
            # Verify files were listed
            self.assertTrue(mock_print.called)
    
    @patch('cli.ImageAnalyzer')
    def test_analyze_image_success(self, mock_analyzer_class):
        """Test successful image analysis."""
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.return_value = {
            'basic_info': {'width': 512, 'height': 512, 'format': 'PNG'},
            'generation_params': {'steps': 20, 'sampler': 'Euler a'},
            'prompt_info': {'prompt': 'test prompt', 'negative_prompt': 'test negative'}
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        self.cli.image_analyzer = mock_analyzer
        
        # Create test image file
        test_image = 'test_image.png'
        with open(test_image, 'w') as f:
            f.write('fake image data')
        
        with patch('builtins.print') as mock_print:
            self.cli.analyze_image(test_image)
            
            mock_analyzer.analyze_image.assert_called_once_with(test_image)
            self.assertTrue(mock_print.called)
    
    def test_analyze_image_not_found(self):
        """Test image analysis with non-existent file."""
        with patch('builtins.print') as mock_print:
            self.cli.analyze_image('nonexistent.png')
            
            mock_print.assert_called_with("❌ Image file not found: nonexistent.png")
    
    def test_list_wildcards_success(self):
        """Test successful wildcard listing."""
        with patch('builtins.print') as mock_print:
            self.cli.list_wildcards()
            
            # Verify wildcards were listed
            self.assertTrue(mock_print.called)
    
    def test_list_wildcards_empty(self):
        """Test wildcard listing with empty directory."""
        # Remove wildcards directory
        if os.path.exists('wildcards'):
            shutil.rmtree('wildcards')
        
        with patch('builtins.print') as mock_print:
            self.cli.list_wildcards()
            
            mock_print.assert_called_with("📁 No wildcards directory found")
    
    @patch('cli.config_handler')
    @patch('cli.PromptBuilder')
    def test_preview_wildcards_success(self, mock_builder_class, mock_config_handler):
        """Test successful wildcard preview."""
        mock_builder = Mock()
        mock_builder.build_prompt.return_value = "resolved prompt"
        mock_builder_class.return_value = mock_builder
        
        mock_config_handler.load_config.return_value = self.test_config
        
        self.cli.prompt_builder = mock_builder
        
        with patch('builtins.print') as mock_print:
            self.cli.preview_wildcards('test_config', 3)
            
            # Verify previews were generated
            self.assertEqual(mock_builder.build_prompt.call_count, 3)
            self.assertTrue(mock_print.called)
    
    @patch('cli.config_handler')
    def test_preview_wildcards_config_error(self, mock_config_handler):
        """Test wildcard preview with config error."""
        mock_config_handler.load_config.side_effect = Exception("Config error")
        
        with patch('builtins.print') as mock_print:
            self.cli.preview_wildcards('test_config')
            
            mock_print.assert_called_with("❌ Error previewing wildcards: Config error")
    
    @patch('cli.config_handler')
    def test_show_status_success(self, mock_config_handler):
        """Test successful status display."""
        mock_config_handler.list_configs.return_value = ['config1', 'config2']
        
        with patch('builtins.print') as mock_print:
            self.cli.show_status()
            
            # Verify status was displayed
            self.assertTrue(mock_print.called)
    
    @patch('cli.config_handler')
    def test_export_config_success(self, mock_config_handler):
        """Test successful configuration export."""
        mock_config_handler.load_config.return_value = self.test_config
        
        export_file = 'exported_config.json'
        
        with patch('builtins.print') as mock_print:
            result = self.cli.export_config('test_config', export_file)
            
            self.assertTrue(result)
            mock_print.assert_called_with(f"✅ Configuration exported to: {export_file}")
            
            # Verify file was created
            self.assertTrue(os.path.exists(export_file))
    
    @patch('cli.config_handler')
    def test_export_config_error(self, mock_config_handler):
        """Test configuration export with error."""
        mock_config_handler.load_config.side_effect = Exception("Export error")
        
        with patch('builtins.print') as mock_print:
            result = self.cli.export_config('test_config', 'export.json')
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ Error exporting configuration: Export error")
    
    def test_import_config_success(self):
        """Test successful configuration import."""
        import_file = 'import_config.json'
        with open(import_file, 'w') as f:
            json.dump(self.test_config, f)
        
        with patch('builtins.print') as mock_print:
            result = self.cli.import_config(import_file, 'imported_config')
            
            self.assertTrue(result)
            mock_print.assert_called_with("✅ Configuration imported as: imported_config")
    
    def test_import_config_file_not_found(self):
        """Test configuration import with non-existent file."""
        with patch('builtins.print') as mock_print:
            result = self.cli.import_config('nonexistent.json')
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ Error importing configuration: [Errno 2] No such file or directory: 'nonexistent.json'")
    
    def test_import_config_invalid_json(self):
        """Test configuration import with invalid JSON."""
        import_file = 'invalid_config.json'
        with open(import_file, 'w') as f:
            f.write('invalid json content')
        
        with patch('builtins.print') as mock_print:
            result = self.cli.import_config(import_file)
            
            self.assertFalse(result)
            mock_print.assert_called_with("❌ Error importing configuration: Expecting value: line 1 column 1 (char 0)")


if __name__ == '__main__':
    unittest.main() 