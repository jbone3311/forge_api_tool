#!/usr/bin/env python3
"""
Functional integration tests for the Forge API Tool CLI interface.
Tests real command execution and integration between components.
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
import subprocess
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from cli import ForgeAPICLI


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test directory structure
        os.makedirs('configs', exist_ok=True)
        os.makedirs('wildcards', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Create test configuration
        self.test_config = {
            'name': 'test_config',
            'description': 'Test configuration for integration tests',
            'model_type': 'sd',
            'generation_settings': {
                'steps': 20,
                'sampler': 'Euler a',
                'width': 512,
                'height': 512,
                'batch_size': 1,
                'cfg_scale': 7.0,
                'seed': -1
            },
            'prompt_settings': {
                'base_prompt': 'a beautiful __STYLE__ portrait of __SUBJECT__ in __LIGHTING__ lighting',
                'negative_prompt': 'low quality, blurry, distorted, ugly, deformed, bad anatomy'
            },
            'output_settings': {
                'output_dir': 'outputs/test_integration',
                'save_metadata': True,
                'save_prompts': True,
                'filename_pattern': '{config}_{timestamp}_{seed}'
            },
            'model_settings': {
                'checkpoint': 'test_model.safetensors',
                'vae': 'test_vae.safetensors'
            }
        }
        
        with open('configs/test_config.json', 'w') as f:
            json.dump(self.test_config, f)
        
        # Create test wildcard files
        wildcard_data = {
            'style.txt': 'realistic\nartistic\nphotographic\ncinematic\npainterly',
            'subject.txt': 'man\nwoman\nchild\nelderly person\nprofessional',
            'lighting.txt': 'studio lighting\nnatural lighting\ndramatic lighting\nsoft lighting\nbacklit'
        }
        
        for filename, content in wildcard_data.items():
            with open(f'wildcards/{filename}', 'w') as f:
                f.write(content)
        
        # Create test image for analysis
        self.create_test_image('test_image.png')
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def create_test_image(self, filename):
        """Create a simple test image file."""
        # Create a minimal PNG file for testing
        png_header = b'\x89PNG\r\n\x1a\n'
        png_data = png_header + b'test image data'
        
        with open(filename, 'wb') as f:
            f.write(png_data)
    
    def test_cli_help_command(self):
        """Test CLI help command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', '--help'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn('Forge API Tool - Command Line Interface', result.stdout)
            self.assertIn('Available commands', result.stdout)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_status_command(self):
        """Test CLI status command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'status'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Status command should work even without API connection
            self.assertIn('System Status', result.stdout)
            self.assertIn('Configurations', result.stdout)
            self.assertIn('Outputs', result.stdout)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_configs_list_command(self):
        """Test CLI configs list command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'list'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show available configurations
            self.assertIn('configurations', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_configs_show_command(self):
        """Test CLI configs show command."""
        try:
            # First, create a test config
            test_config_path = os.path.join(project_root, 'configs', 'test_show_config.json')
            with open(test_config_path, 'w') as f:
                json.dump(self.test_config, f)
            
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'show', 'test_show_config'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show configuration details
            self.assertIn('test_show_config', result.stdout)
            self.assertIn('Test configuration', result.stdout)
            
            # Clean up
            os.remove(test_config_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_configs_export_import_cycle(self):
        """Test CLI configs export and import cycle."""
        try:
            # Create test config
            test_config_path = os.path.join(project_root, 'configs', 'test_export_config.json')
            with open(test_config_path, 'w') as f:
                json.dump(self.test_config, f)
            
            export_path = os.path.join(self.temp_dir, 'exported_config.json')
            
            # Export config
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'export', 'test_export_config', export_path],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn('exported to', result.stdout)
            self.assertTrue(os.path.exists(export_path))
            
            # Import config with new name
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'import', export_path, '--name', 'imported_config'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertIn('imported as', result.stdout)
            
            # Verify imported config exists
            imported_config_path = os.path.join(project_root, 'configs', 'imported_config.json')
            self.assertTrue(os.path.exists(imported_config_path))
            
            # Clean up
            os.remove(test_config_path)
            os.remove(imported_config_path)
            os.remove(export_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_wildcards_list_command(self):
        """Test CLI wildcards list command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'wildcards', 'list'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show wildcard files
            self.assertIn('wildcard', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_wildcards_preview_command(self):
        """Test CLI wildcards preview command."""
        try:
            # Create test config for preview
            test_config_path = os.path.join(project_root, 'configs', 'test_preview_config.json')
            with open(test_config_path, 'w') as f:
                json.dump(self.test_config, f)
            
            result = subprocess.run(
                [sys.executable, 'cli.py', 'wildcards', 'preview', 'test_preview_config', '--count', '3'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show preview information
            self.assertIn('preview', result.stdout.lower())
            
            # Clean up
            os.remove(test_config_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_outputs_list_command(self):
        """Test CLI outputs list command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'outputs', 'list'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show output information
            self.assertIn('outputs', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_analyze_command(self):
        """Test CLI analyze command."""
        try:
            # Create test image in project root
            test_image_path = os.path.join(project_root, 'test_analyze_image.png')
            self.create_test_image(test_image_path)
            
            result = subprocess.run(
                [sys.executable, 'cli.py', 'analyze', test_image_path],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show analysis information
            self.assertIn('analyzing', result.stdout.lower())
            
            # Clean up
            os.remove(test_image_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_test_connection_command(self):
        """Test CLI test connection command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'test'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show connection test information
            self.assertIn('connection', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_invalid_command(self):
        """Test CLI with invalid command."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'invalid_command'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show help or error message
            self.assertIn('help', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_missing_arguments(self):
        """Test CLI with missing required arguments."""
        try:
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'show'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show error about missing argument
            self.assertNotEqual(result.returncode, 0)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_generate_commands_without_api(self):
        """Test CLI generate commands without API connection."""
        try:
            # Test single generation command
            result = subprocess.run(
                [sys.executable, 'cli.py', 'generate', 'single', 'test_config', 'test prompt'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show error about no API client
            self.assertIn('client', result.stdout.lower())
            
            # Test batch generation command
            result = subprocess.run(
                [sys.executable, 'cli.py', 'generate', 'batch', 'test_config', '--batch-size', '2'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show error about no API client
            self.assertIn('client', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_config_file_operations(self):
        """Test CLI configuration file operations."""
        try:
            # Test with non-existent config
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'show', 'nonexistent_config'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show error about config not found
            self.assertIn('error', result.stdout.lower())
            
            # Test export with non-existent config
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'export', 'nonexistent_config', 'export.json'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should show error
            self.assertIn('error', result.stdout.lower())
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_file_permissions(self):
        """Test CLI with file permission issues."""
        try:
            # Create a read-only directory
            read_only_dir = os.path.join(self.temp_dir, 'readonly')
            os.makedirs(read_only_dir, exist_ok=True)
            os.chmod(read_only_dir, 0o444)  # Read-only
            
            # Try to create config in read-only directory
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'import', 'nonexistent.json'],
                capture_output=True,
                text=True,
                cwd=read_only_dir
            )
            
            # Should handle permission errors gracefully
            self.assertIn('error', result.stdout.lower())
            
            # Restore permissions
            os.chmod(read_only_dir, 0o755)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_unicode_support(self):
        """Test CLI with Unicode characters."""
        try:
            # Create config with Unicode characters
            unicode_config = self.test_config.copy()
            unicode_config['description'] = 'Test configuration with Unicode: 测试配置 🎨'
            unicode_config['prompt_settings']['base_prompt'] = 'a beautiful portrait with 艺术风格'
            
            unicode_config_path = os.path.join(project_root, 'configs', 'unicode_test_config.json')
            with open(unicode_config_path, 'w', encoding='utf-8') as f:
                json.dump(unicode_config, f, ensure_ascii=False, indent=2)
            
            # Test showing Unicode config
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'show', 'unicode_test_config'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should handle Unicode correctly
            self.assertEqual(result.returncode, 0)
            
            # Clean up
            os.remove(unicode_config_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_large_config_handling(self):
        """Test CLI with large configuration files."""
        try:
            # Create large config with many settings
            large_config = self.test_config.copy()
            large_config['generation_settings'].update({
                'steps': 150,
                'width': 2048,
                'height': 2048,
                'batch_size': 10,
                'cfg_scale': 15.0
            })
            
            # Add many prompt variations
            large_config['prompt_settings']['base_prompt'] = 'a ' + 'very ' * 100 + 'detailed prompt'
            
            large_config_path = os.path.join(project_root, 'configs', 'large_test_config.json')
            with open(large_config_path, 'w') as f:
                json.dump(large_config, f, indent=2)
            
            # Test showing large config
            result = subprocess.run(
                [sys.executable, 'cli.py', 'configs', 'show', 'large_test_config'],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Should handle large configs
            self.assertEqual(result.returncode, 0)
            
            # Clean up
            os.remove(large_config_path)
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_concurrent_operations(self):
        """Test CLI with concurrent operations."""
        try:
            import threading
            import queue
            
            results = queue.Queue()
            
            def run_cli_command(cmd_args):
                try:
                    result = subprocess.run(
                        [sys.executable, 'cli.py'] + cmd_args,
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                        timeout=10
                    )
                    results.put((cmd_args, result.returncode, result.stdout))
                except Exception as e:
                    results.put((cmd_args, -1, str(e)))
            
            # Run multiple CLI commands concurrently
            threads = []
            commands = [
                ['status'],
                ['configs', 'list'],
                ['wildcards', 'list'],
                ['outputs', 'list']
            ]
            
            for cmd in commands:
                thread = threading.Thread(target=run_cli_command, args=(cmd,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            while not results.empty():
                cmd, returncode, output = results.get()
                # All commands should complete successfully
                self.assertNotEqual(returncode, -1, f"Command {cmd} failed")
                
        except FileNotFoundError:
            self.skipTest("CLI script not found")


if __name__ == '__main__':
    unittest.main() 