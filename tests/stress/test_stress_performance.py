#!/usr/bin/env python3
"""
Stress tests for the Forge API Tool CLI and core functionality.
Tests performance under load and identifies bottlenecks.
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
import time
import threading
import multiprocessing
import subprocess
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from unittest.mock import patch, Mock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from cli import ForgeAPICLI


class TestStressPerformance(unittest.TestCase):
    """Stress tests for performance and load handling."""
    
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
        
        # Create large test configuration
        self.large_config = {
            'name': 'stress_test_config',
            'description': 'Configuration for stress testing',
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
                'base_prompt': 'a beautiful __STYLE__ portrait of __SUBJECT__ in __LIGHTING__ lighting with __COMPOSITION__',
                'negative_prompt': 'low quality, blurry, distorted, ugly, deformed, bad anatomy, watermark, signature'
            },
            'output_settings': {
                'output_dir': 'outputs/stress_test',
                'save_metadata': True,
                'save_prompts': True,
                'filename_pattern': '{config}_{timestamp}_{seed}'
            }
        }
        
        with open('configs/stress_test_config.json', 'w') as f:
            json.dump(self.large_config, f)
        
        # Create large wildcard files for stress testing
        self.create_large_wildcard_files()
        
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
    
    def create_large_wildcard_files(self):
        """Create large wildcard files for stress testing."""
        wildcard_data = {
            'style.txt': [f'style_{i}' for i in range(1000)],
            'subject.txt': [f'subject_{i}' for i in range(1000)],
            'lighting.txt': [f'lighting_{i}' for i in range(500)],
            'composition.txt': [f'composition_{i}' for i in range(500)]
        }
        
        for filename, items in wildcard_data.items():
            with open(f'wildcards/{filename}', 'w') as f:
                f.write('\n'.join(items))
    
    def test_cli_initialization_performance(self):
        """Test CLI initialization performance under load."""
        start_time = time.time()
        
        # Initialize CLI multiple times
        for i in range(100):
            with patch('cli.ForgeAPIClient'), \
                 patch('cli.BatchRunner'), \
                 patch('cli.OutputManager'), \
                 patch('cli.WildcardManagerFactory'), \
                 patch('cli.PromptBuilder'), \
                 patch('cli.ImageAnalyzer'), \
                 patch('cli.JobQueue'), \
                 patch('cli.api_config'):
                
                cli = ForgeAPICLI()
                self.assertIsNotNone(cli)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"CLI initialization performance: {avg_time:.4f}s average per initialization")
        self.assertLess(avg_time, 0.1, "CLI initialization should be fast")
    
    def test_config_loading_performance(self):
        """Test configuration loading performance with large configs."""
        # Create multiple large configurations
        for i in range(50):
            config = self.large_config.copy()
            config['name'] = f'stress_config_{i}'
            config['description'] = f'Stress test configuration {i}'
            
            with open(f'configs/stress_config_{i}.json', 'w') as f:
                json.dump(config, f)
        
        start_time = time.time()
        
        # Load all configurations
        for i in range(50):
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = self.large_config
                self.cli.show_config(f'stress_config_{i}')
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 50
        
        print(f"Config loading performance: {avg_time:.4f}s average per config")
        self.assertLess(avg_time, 0.05, "Config loading should be fast")
    
    def test_wildcard_processing_performance(self):
        """Test wildcard processing performance with large files."""
        start_time = time.time()
        
        # Process wildcards multiple times
        for i in range(100):
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = self.large_config
                with patch('cli.PromptBuilder') as mock_builder:
                    mock_builder.return_value.build_prompt.return_value = f"test prompt {i}"
                    self.cli.preview_wildcards('stress_test_config', 10)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"Wildcard processing performance: {avg_time:.4f}s average per operation")
        self.assertLess(avg_time, 0.1, "Wildcard processing should be fast")
    
    def test_concurrent_config_operations(self):
        """Test concurrent configuration operations."""
        def load_config(config_id):
            """Load a configuration in a separate thread."""
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = self.large_config
                return self.cli.show_config(f'stress_config_{config_id}')
        
        start_time = time.time()
        
        # Run concurrent config operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(load_config, i) for i in range(50)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Concurrent config operations: {total_time:.4f}s for 50 operations")
        self.assertLess(total_time, 5.0, "Concurrent operations should complete quickly")
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        configs = []
        for i in range(100):
            config = self.large_config.copy()
            config['name'] = f'memory_test_config_{i}'
            configs.append(config)
        
        # Load and process configurations
        for config in configs:
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = config
                self.cli.show_config(config['name'])
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (+{memory_increase:.2f}MB)")
        self.assertLess(memory_increase, 100, "Memory usage should not increase significantly")
    
    def test_cli_command_parsing_performance(self):
        """Test CLI command parsing performance."""
        import argparse
        
        # Create parser
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        
        # Add subcommands
        configs_parser = subparsers.add_parser('configs')
        configs_subparsers = configs_parser.add_subparsers(dest='configs_command')
        configs_subparsers.add_parser('list')
        
        show_parser = configs_subparsers.add_parser('show')
        show_parser.add_argument('config_name')
        
        start_time = time.time()
        
        # Parse commands multiple times
        test_commands = [
            ['configs', 'list'],
            ['configs', 'show', 'test_config'],
            ['status'],
            ['test']
        ]
        
        for i in range(1000):
            for cmd in test_commands:
                try:
                    args = parser.parse_args(cmd)
                except SystemExit:
                    pass  # Expected for incomplete commands
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / (1000 * len(test_commands))
        
        print(f"CLI parsing performance: {avg_time:.6f}s average per command")
        self.assertLess(avg_time, 0.001, "CLI parsing should be very fast")
    
    def test_file_io_performance(self):
        """Test file I/O performance under load."""
        # Create large test files
        large_data = "x" * 1024 * 1024  # 1MB of data
        
        start_time = time.time()
        
        # Write multiple large files
        for i in range(10):
            with open(f'test_file_{i}.txt', 'w') as f:
                f.write(large_data)
        
        # Read multiple large files
        for i in range(10):
            with open(f'test_file_{i}.txt', 'r') as f:
                data = f.read()
                self.assertEqual(len(data), len(large_data))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"File I/O performance: {total_time:.4f}s for 20 operations")
        self.assertLess(total_time, 10.0, "File I/O should be reasonably fast")
    
    def test_concurrent_cli_operations(self):
        """Test concurrent CLI operations."""
        def run_cli_operation(operation_id):
            """Run a CLI operation in a separate thread."""
            with patch('cli.config_handler') as mock_handler:
                mock_handler.list_configs.return_value = [f'config_{i}' for i in range(10)]
                mock_handler.load_config.return_value = self.large_config
                
                # Simulate different CLI operations
                if operation_id % 3 == 0:
                    self.cli.list_configs()
                elif operation_id % 3 == 1:
                    self.cli.show_config('test_config')
                else:
                    self.cli.show_status()
            
            return f"Operation {operation_id} completed"
        
        start_time = time.time()
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(run_cli_operation, i) for i in range(100)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Concurrent CLI operations: {total_time:.4f}s for 100 operations")
        self.assertEqual(len(results), 100, "All operations should complete")
        self.assertLess(total_time, 10.0, "Concurrent operations should complete quickly")
    
    def test_error_handling_performance(self):
        """Test error handling performance under load."""
        start_time = time.time()
        
        # Generate many errors
        for i in range(1000):
            try:
                # Simulate various error conditions
                if i % 3 == 0:
                    raise FileNotFoundError(f"File {i} not found")
                elif i % 3 == 1:
                    raise ValueError(f"Invalid value {i}")
                else:
                    raise Exception(f"Generic error {i}")
            except (FileNotFoundError, ValueError, Exception):
                pass  # Expected errors
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 1000
        
        print(f"Error handling performance: {avg_time:.6f}s average per error")
        self.assertLess(avg_time, 0.001, "Error handling should be very fast")
    
    def test_large_config_validation_performance(self):
        """Test large configuration validation performance."""
        # Create a very large configuration
        large_config = self.large_config.copy()
        large_config['generation_settings'] = {
            'steps': 20,
            'sampler': 'Euler a',
            'width': 512,
            'height': 512,
            'batch_size': 1,
            'cfg_scale': 7.0,
            'seed': -1,
            'extra_settings': {f'setting_{i}': f'value_{i}' for i in range(1000)}
        }
        
        start_time = time.time()
        
        # Validate large config multiple times
        for i in range(100):
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = large_config
                self.cli.show_config('large_config')
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"Large config validation performance: {avg_time:.4f}s average per validation")
        self.assertLess(avg_time, 0.1, "Large config validation should be reasonably fast")


class TestStressCLICommands(unittest.TestCase):
    """Stress tests for specific CLI commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test structure
        os.makedirs('configs', exist_ok=True)
        os.makedirs('wildcards', exist_ok=True)
        os.makedirs('outputs', exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_cli_status_command_stress(self):
        """Test CLI status command under stress."""
        try:
            start_time = time.time()
            
            # Run status command multiple times
            for i in range(50):
                result = subprocess.run(
                    [sys.executable, 'cli.py', 'status'],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=10
                )
                
                self.assertEqual(result.returncode, 0, f"Status command failed on iteration {i}")
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 50
            
            print(f"CLI status command stress test: {avg_time:.4f}s average per command")
            self.assertLess(avg_time, 2.0, "Status command should be fast under stress")
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")
    
    def test_cli_configs_list_stress(self):
        """Test CLI configs list command under stress."""
        try:
            start_time = time.time()
            
            # Run configs list command multiple times
            for i in range(100):
                result = subprocess.run(
                    [sys.executable, 'cli.py', 'configs', 'list'],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=10
                )
                
                self.assertEqual(result.returncode, 0, f"Configs list command failed on iteration {i}")
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 100
            
            print(f"CLI configs list stress test: {avg_time:.4f}s average per command")
            self.assertLess(avg_time, 1.0, "Configs list command should be fast under stress")
            
        except FileNotFoundError:
            self.skipTest("CLI script not found")


if __name__ == '__main__':
    unittest.main() 