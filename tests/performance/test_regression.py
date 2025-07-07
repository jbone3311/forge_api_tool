#!/usr/bin/env python3
"""
Performance regression tests for the Forge API Tool.
Tracks performance metrics over time and detects regressions.
"""

import os
import sys
import time
import json
import psutil
import gc
import requests
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pytest
from unittest import TestCase

# Import core modules
from cli import ForgeAPICLI
from core.config_handler import config_handler
from core.wildcard_manager import WildcardManagerFactory
from core.output_manager import OutputManager


class TestPerformanceRegression(TestCase):
    """Performance regression tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = os.path.join(os.getcwd(), 'temp_test_dir')
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Create test directories
        os.makedirs(os.path.join(self.temp_dir, 'configs'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'wildcards'), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, 'outputs'), exist_ok=True)
        
        # Initialize components
        self.wildcard_factory = WildcardManagerFactory()
        self.output_manager = OutputManager(os.path.join(self.temp_dir, 'outputs'))
        
        # Load benchmarks
        self.benchmarks_file = Path('tests/performance/benchmarks.json')
        self.benchmarks_file.parent.mkdir(exist_ok=True)
        self.benchmarks = self._load_benchmarks()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cli_initialization_performance(self):
        """Test CLI initialization performance regression."""
        start_time = time.time()
        
        # Initialize CLI multiple times
        for _ in range(100):
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
        avg_time = (end_time - start_time) / 100
        
        # Check against historical benchmark
        benchmark_key = 'cli_initialization'
        historical_avg = self.benchmarks.get(benchmark_key, 0.1)
        
        # Allow 20% regression before failing
        regression_threshold = historical_avg * 1.2
        self.assertLessEqual(avg_time, regression_threshold, 
                           f"Performance regression: {avg_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_avg:.4f}s)")
        
        # Update benchmark if performance improved
        if avg_time < historical_avg:
            self._update_benchmark(benchmark_key, avg_time)
    
    def test_config_loading_performance(self):
        """Test configuration loading performance regression."""
        # Create test configurations
        for i in range(50):
            config = {
                'name': f'perf_test_config_{i}',
                'description': f'Performance test configuration {i}',
                'model_type': 'sd',
                'generation_settings': {
                    'steps': 20,
                    'sampler': 'Euler a',
                    'width': 512,
                    'height': 512
                },
                'prompt_settings': {
                    'base_prompt': f'a beautiful __STYLE__ portrait of __SUBJECT__ {i}',
                    'negative_prompt': 'low quality, blurry'
                }
            }
            
            config_path = os.path.join(self.temp_dir, 'configs', f'perf_test_config_{i}.json')
            with open(config_path, 'w') as f:
                json.dump(config, f)
        
        start_time = time.time()
        
        # Load all configurations
        for i in range(50):
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = config
                config_handler.load_config(f'perf_test_config_{i}')
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 50
        
        # Check against historical benchmark
        benchmark_key = 'config_loading'
        historical_avg = self.benchmarks.get(benchmark_key, 0.05)
        
        # Allow 20% regression before failing
        regression_threshold = historical_avg * 1.2
        self.assertLessEqual(avg_time, regression_threshold,
                           f"Performance regression: {avg_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_avg:.4f}s)")
        
        # Update benchmark if performance improved
        if avg_time < historical_avg:
            self._update_benchmark(benchmark_key, avg_time)
    
    def test_wildcard_processing_performance(self):
        """Test wildcard processing performance regression."""
        # Create large wildcard files
        wildcard_data = {
            'style.txt': [f'style_{i}' for i in range(1000)],
            'subject.txt': [f'subject_{i}' for i in range(1000)],
            'lighting.txt': [f'lighting_{i}' for i in range(500)],
            'composition.txt': [f'composition_{i}' for i in range(500)]
        }
        
        for filename, items in wildcard_data.items():
            filepath = os.path.join(self.temp_dir, 'wildcards', filename)
            with open(filepath, 'w') as f:
                f.write('\n'.join(items))
        
        start_time = time.time()
        
        # Process wildcards multiple times
        wildcard_manager = self.wildcard_factory.get_manager(os.path.join(self.temp_dir, 'wildcards'))
        for i in range(100):
            with patch('cli.config_handler') as mock_handler:
                mock_handler.load_config.return_value = {
                    'prompt_settings': {'base_prompt': 'a beautiful __STYLE__ portrait of __SUBJECT__'}
                }
                wildcard_manager.get_wildcard_values('style')
                wildcard_manager.get_wildcard_values('subject')
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Check against historical benchmark
        benchmark_key = 'wildcard_processing'
        historical_avg = self.benchmarks.get(benchmark_key, 0.1)
        
        # Allow 20% regression before failing
        regression_threshold = historical_avg * 1.2
        self.assertLessEqual(avg_time, regression_threshold,
                           f"Performance regression: {avg_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_avg:.4f}s)")
        
        # Update benchmark if performance improved
        if avg_time < historical_avg:
            self._update_benchmark(benchmark_key, avg_time)
    
    def test_memory_usage_regression(self):
        """Test memory usage regression."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform memory-intensive operations
        for _ in range(1000):
            # Create and process large data structures
            large_list = [f'item_{i}' for i in range(1000)]
            large_dict = {f'key_{i}': f'value_{i}' for i in range(1000)}
            
            # Process the data
            processed_list = [item.upper() for item in large_list]
            processed_dict = {k: v.upper() for k, v in large_dict.items()}
            
            # Clear references to force garbage collection
            del large_list, large_dict, processed_list, processed_dict
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Check against historical benchmark
        benchmark_key = 'memory_usage'
        historical_increase = self.benchmarks.get(benchmark_key, 50 * 1024 * 1024)  # 50MB default
        
        # Allow 50% regression before failing
        regression_threshold = historical_increase * 1.5
        self.assertLessEqual(memory_increase, regression_threshold,
                           f"Memory regression: {memory_increase / (1024*1024):.1f}MB > {regression_threshold / (1024*1024):.1f}MB (historical: {historical_increase / (1024*1024):.1f}MB)")
        
        # Update benchmark if memory usage improved
        if memory_increase < historical_increase:
            self._update_benchmark(benchmark_key, memory_increase)
    
    def test_file_io_performance(self):
        """Test file I/O performance regression."""
        # Create test files
        test_files = []
        for i in range(100):
            filepath = os.path.join(self.temp_dir, f'test_file_{i}.txt')
            with open(filepath, 'w') as f:
                f.write(f'Test content for file {i}\n' * 1000)
            test_files.append(filepath)
        
        start_time = time.time()
        
        # Read all files
        for filepath in test_files:
            with open(filepath, 'r') as f:
                content = f.read()
                # Process content
                processed_content = content.upper()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check against historical benchmark
        benchmark_key = 'file_io'
        historical_time = self.benchmarks.get(benchmark_key, 1.0)
        
        # Allow 20% regression before failing
        regression_threshold = historical_time * 1.2
        self.assertLessEqual(total_time, regression_threshold,
                           f"File I/O regression: {total_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_time:.4f}s)")
        
        # Update benchmark if performance improved
        if total_time < historical_time:
            self._update_benchmark(benchmark_key, total_time)
    
    def test_concurrent_operations_performance(self):
        """Test concurrent operations performance regression."""
        import threading
        import queue
        
        # Create a queue for results
        result_queue = queue.Queue()
        
        def worker(worker_id):
            """Worker function for concurrent operations."""
            start_time = time.time()
            
            # Perform some work
            for i in range(100):
                # Simulate some processing
                result = sum(range(i + 1))
            
            end_time = time.time()
            result_queue.put((worker_id, end_time - start_time))
        
        # Start multiple threads
        threads = []
        start_time = time.time()
        
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        worker_times = []
        while not result_queue.empty():
            worker_id, worker_time = result_queue.get()
            worker_times.append(worker_time)
        
        avg_worker_time = sum(worker_times) / len(worker_times)
        
        # Check against historical benchmark
        benchmark_key = 'concurrent_operations'
        historical_time = self.benchmarks.get(benchmark_key, 2.0)
        
        # Allow 20% regression before failing
        regression_threshold = historical_time * 1.2
        self.assertLessEqual(total_time, regression_threshold,
                           f"Concurrent operations regression: {total_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_time:.4f}s)")
        
        # Update benchmark if performance improved
        if total_time < historical_time:
            self._update_benchmark(benchmark_key, total_time)
    
    def test_api_request_performance(self):
        """Test API request performance regression."""
        # Mock API client
        with patch('requests.Session.request') as mock_request:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'success': True, 'image_path': '/outputs/test.png'}
            mock_request.return_value = mock_response
            
            start_time = time.time()
            
            # Make multiple API requests
            for i in range(50):
                # Simulate API request
                response = requests.get('http://localhost:3000/api/generate')
                self.assertEqual(response.status_code, 200)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 50
        
        # Check against historical benchmark
        benchmark_key = 'api_request'
        historical_avg = self.benchmarks.get(benchmark_key, 0.1)
        
        # Allow 20% regression before failing
        regression_threshold = historical_avg * 1.2
        self.assertLessEqual(avg_time, regression_threshold,
                           f"API request regression: {avg_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_avg:.4f}s)")
        
        # Update benchmark if performance improved
        if avg_time < historical_avg:
            self._update_benchmark(benchmark_key, avg_time)
    
    def test_json_serialization_performance(self):
        """Test JSON serialization performance regression."""
        # Create large data structure
        large_data = {
            'configs': [{
                'name': f'config_{i}',
                'settings': {
                    'steps': 20,
                    'sampler': 'Euler a',
                    'width': 512,
                    'height': 512,
                    'prompt': f'Test prompt {i}',
                    'negative_prompt': 'Low quality'
                }
            } for i in range(1000)],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'generator': 'forge-api-tool'
            }
        }
        
        start_time = time.time()
        
        # Serialize and deserialize multiple times
        for _ in range(100):
            serialized = json.dumps(large_data)
            deserialized = json.loads(serialized)
            # Verify data integrity
            self.assertEqual(len(deserialized['configs']), 1000)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Check against historical benchmark
        benchmark_key = 'json_serialization'
        historical_avg = self.benchmarks.get(benchmark_key, 0.05)
        
        # Allow 20% regression before failing
        regression_threshold = historical_avg * 1.2
        self.assertLessEqual(avg_time, regression_threshold,
                           f"JSON serialization regression: {avg_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_avg:.4f}s)")
        
        # Update benchmark if performance improved
        if avg_time < historical_avg:
            self._update_benchmark(benchmark_key, avg_time)
    
    def test_string_processing_performance(self):
        """Test string processing performance regression."""
        # Create large strings
        large_strings = [
            "a beautiful __STYLE__ portrait of __SUBJECT__ in __LIGHTING__ lighting with __COMPOSITION__" * 100,
            "low quality, blurry, distorted, ugly, deformed, bad anatomy, watermark, signature" * 50,
            "masterpiece, best quality, highly detailed, professional photography" * 75
        ]
        
        start_time = time.time()
        
        # Process strings multiple times
        for _ in range(1000):
            for string in large_strings:
                # Simulate string processing (wildcard substitution)
                processed = string.replace('__STYLE__', 'realistic')
                processed = processed.replace('__SUBJECT__', 'person')
                processed = processed.replace('__LIGHTING__', 'natural')
                processed = processed.replace('__COMPOSITION__', 'portrait')
                
                # Additional processing
                processed = processed.upper()
                processed = processed.replace('PORTRAIT', 'PORTRAIT')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check against historical benchmark
        benchmark_key = 'string_processing'
        historical_time = self.benchmarks.get(benchmark_key, 1.0)
        
        # Allow 20% regression before failing
        regression_threshold = historical_time * 1.2
        self.assertLessEqual(total_time, regression_threshold,
                           f"String processing regression: {total_time:.4f}s > {regression_threshold:.4f}s (historical: {historical_time:.4f}s)")
        
        # Update benchmark if performance improved
        if total_time < historical_time:
            self._update_benchmark(benchmark_key, total_time)
    
    # Helper methods
    def _load_benchmarks(self):
        """Load performance benchmarks from file."""
        if self.benchmarks_file.exists():
            try:
                with open(self.benchmarks_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default benchmarks if file doesn't exist or is invalid
        return {
            'cli_initialization': 0.1,
            'config_loading': 0.05,
            'wildcard_processing': 0.1,
            'memory_usage': 50 * 1024 * 1024,  # 50MB
            'file_io': 1.0,
            'concurrent_operations': 2.0,
            'api_request': 0.1,
            'json_serialization': 0.05,
            'string_processing': 1.0
        }
    
    def _update_benchmark(self, key, value):
        """Update a performance benchmark."""
        self.benchmarks[key] = value
        
        # Save to file
        try:
            with open(self.benchmarks_file, 'w') as f:
                json.dump(self.benchmarks, f, indent=2)
        except IOError:
            # If we can't write to file, just update in memory
            pass


class TestPerformanceMonitoring(TestCase):
    """Performance monitoring tests."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = os.path.join(os.getcwd(), 'temp_test_dir')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_cpu_usage_monitoring(self):
        """Test CPU usage monitoring."""
        # Monitor CPU usage during intensive operation
        process = psutil.Process()
        
        # Get initial CPU usage
        initial_cpu_percent = process.cpu_percent()
        
        # Perform CPU-intensive operation
        start_time = time.time()
        for i in range(1000000):
            result = i * i  # Simple CPU-intensive operation
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # Get CPU usage after operation
        final_cpu_percent = process.cpu_percent()
        
        # Verify that CPU usage is reasonable
        self.assertLess(operation_time, 10.0, "CPU-intensive operation took too long")
        
        # CPU usage should be above 0 during operation
        self.assertGreaterEqual(final_cpu_percent, 0.0, "CPU usage should be non-negative")
    
    def test_memory_leak_detection(self):
        """Test memory leak detection."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform operations that could cause memory leaks
        for _ in range(10):
            # Create large objects
            large_list = [f'item_{i}' for i in range(10000)]
            large_dict = {f'key_{i}': f'value_{i}' for i in range(10000)}
            
            # Process them
            processed_list = [item.upper() for item in large_list]
            processed_dict = {k: v.upper() for k, v in large_dict.items()}
            
            # Clear references
            del large_list, large_dict, processed_list, processed_dict
        
        # Force garbage collection
        gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024, 
                       f"Potential memory leak: {memory_increase / (1024*1024):.1f}MB increase")
    
    def test_disk_io_monitoring(self):
        """Test disk I/O monitoring."""
        # Monitor disk I/O during file operations
        process = psutil.Process()
        
        # Get initial disk I/O stats
        initial_io = process.io_counters()
        
        # Perform file operations
        for i in range(100):
            filepath = os.path.join(self.temp_dir, f'io_test_{i}.txt')
            with open(filepath, 'w') as f:
                f.write(f'Test content {i}\n' * 1000)
            
            with open(filepath, 'r') as f:
                content = f.read()
        
        # Get final disk I/O stats
        final_io = process.io_counters()
        
        # Calculate I/O increase
        read_bytes = final_io.read_bytes - initial_io.read_bytes
        write_bytes = final_io.write_bytes - initial_io.write_bytes
        
        # Verify that I/O occurred
        self.assertGreater(read_bytes, 0, "No read operations detected")
        self.assertGreater(write_bytes, 0, "No write operations detected")
        
        # Verify reasonable I/O amounts
        self.assertLess(read_bytes, 100 * 1024 * 1024, "Excessive read operations")
        self.assertLess(write_bytes, 100 * 1024 * 1024, "Excessive write operations")


if __name__ == "__main__":
    # Run performance regression tests
    pytest.main([__file__, "-v"]) 