#!/usr/bin/env python3
"""
Unit tests for ImageAnalyzer class.
Tests image analysis functionality including metadata extraction,
parameter parsing, and config generation.
"""

import unittest
import json
import base64
import io
from unittest.mock import Mock, patch, MagicMock
from PIL import Image, PngImagePlugin
import sys
import os

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.image_analyzer import ImageAnalyzer


class TestImageAnalyzer(unittest.TestCase):
    """Test cases for ImageAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ImageAnalyzer()
        
        # Create a test image with metadata
        self.test_image = Image.new('RGB', (512, 512), color='red')
        
        # Create test metadata
        self.test_metadata = {
            'parameters': 'a beautiful landscape, masterpiece, best quality, Steps: 20, CFG scale: 7.0, Sampler: Euler a, Seed: 12345, Size: 512x512, Model: test_model.safetensors, VAE: test_vae.safetensors',
            'prompt': 'a beautiful landscape, masterpiece, best quality',
            'negative_prompt': 'blurry, low quality, bad anatomy',
            'steps': '20',
            'cfg_scale': '7.0',
            'sampler': 'Euler a',
            'seed': '12345',
            'width': '512',
            'height': '512',
            'model': 'test_model.safetensors',
            'vae': 'test_vae.safetensors'
        }
    
    def test_analyzer_initialization(self):
        """Test ImageAnalyzer initialization."""
        self.assertIsInstance(self.analyzer, ImageAnalyzer)
        self.assertIsInstance(self.analyzer.supported_formats, list)
        self.assertIn('.png', self.analyzer.supported_formats)
        self.assertIn('.jpg', self.analyzer.supported_formats)
        self.assertIn('.jpeg', self.analyzer.supported_formats)
        self.assertIn('.webp', self.analyzer.supported_formats)
    
    def test_validate_image_format(self):
        """Test image format validation."""
        self.assertTrue(self.analyzer.validate_image_format('test.png'))
        self.assertTrue(self.analyzer.validate_image_format('test.jpg'))
        self.assertTrue(self.analyzer.validate_image_format('test.jpeg'))
        self.assertTrue(self.analyzer.validate_image_format('test.webp'))
        self.assertFalse(self.analyzer.validate_image_format('test.txt'))
        self.assertFalse(self.analyzer.validate_image_format('test.pdf'))
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.analyzer.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn('.png', formats)
        self.assertIn('.jpg', formats)
        self.assertIn('.jpeg', formats)
        self.assertIn('.webp', formats)
    
    def test_analyze_image_basic(self):
        """Test basic image analysis without metadata."""
        # Create a simple image without metadata
        img = Image.new('RGB', (256, 256), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        result = self.analyzer.analyze_image(img_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 256)
        self.assertEqual(result['height'], 256)
        self.assertEqual(result['format'], 'PNG')
        self.assertEqual(result['mode'], 'RGB')
    
    def test_analyze_image_with_metadata(self):
        """Test image analysis with embedded metadata."""
        # Create image with metadata
        img = Image.new('RGB', (512, 512), color='red')
        
        # Add metadata to image
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', self.test_metadata['parameters'])
        metadata.add_text('prompt', self.test_metadata['prompt'])
        metadata.add_text('negative_prompt', self.test_metadata['negative_prompt'])
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', pnginfo=metadata)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        result = self.analyzer.analyze_image(img_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 512)
        self.assertEqual(result['height'], 512)
        self.assertIn('metadata', result)
        self.assertIn('parameters', result)
        self.assertIn('prompt_info', result)
        
        # Check extracted parameters
        params = result['parameters']
        self.assertEqual(params['prompt'], 'a beautiful landscape, masterpiece, best quality')
        self.assertEqual(params['negative_prompt'], 'blurry, low quality, bad anatomy')
        self.assertEqual(params['steps'], '20')
        self.assertEqual(params['cfg_scale'], '7.0')
        self.assertEqual(params['sampler'], 'Euler a')
        self.assertEqual(params['seed'], '12345')
        self.assertEqual(params['width'], '512')
        self.assertEqual(params['height'], '512')
        self.assertEqual(params['model'], 'test_model.safetensors')
        self.assertEqual(params['vae'], 'test_vae.safetensors')
    
    def test_analyze_image_data_url(self):
        """Test image analysis with data URL format."""
        img = Image.new('RGB', (128, 128), color='green')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Test with data URL prefix
        data_url = f"data:image/png;base64,{img_data}"
        result = self.analyzer.analyze_image(data_url)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 128)
        self.assertEqual(result['height'], 128)
    
    def test_analyze_image_invalid_data(self):
        """Test image analysis with invalid data."""
        result = self.analyzer.analyze_image("invalid_base64_data")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_extract_metadata_from_image(self):
        """Test metadata extraction from image."""
        # Create image with metadata
        img = Image.new('RGB', (64, 64), color='yellow')
        
        # Add metadata
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'test parameters')
        metadata.add_text('prompt', 'test prompt')
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', pnginfo=metadata)
        img = Image.open(img_buffer)
        
        extracted_metadata = self.analyzer._extract_metadata_from_image(img)
        
        self.assertIsNotNone(extracted_metadata)
        self.assertIn('parameters', extracted_metadata)
        self.assertIn('prompt', extracted_metadata)
        self.assertEqual(extracted_metadata['parameters'], 'test parameters')
        self.assertEqual(extracted_metadata['prompt'], 'test prompt')
    
    def test_extract_parameters(self):
        """Test parameter extraction from metadata."""
        metadata = {
            'parameters': self.test_metadata['parameters'],
            'prompt': self.test_metadata['prompt'],
            'negative_prompt': self.test_metadata['negative_prompt'],
            'steps': self.test_metadata['steps'],
            'cfg_scale': self.test_metadata['cfg_scale']
        }
        
        params = self.analyzer._extract_parameters(metadata)
        
        self.assertIn('prompt', params)
        self.assertIn('negative_prompt', params)
        self.assertIn('steps', params)
        self.assertIn('cfg_scale', params)
        self.assertIn('sampler', params)
        self.assertIn('seed', params)
        self.assertIn('width', params)
        self.assertIn('height', params)
        self.assertIn('model', params)
        self.assertIn('vae', params)
    
    def test_parse_parameters_string(self):
        """Test parsing of parameters string."""
        param_string = self.test_metadata['parameters']
        params = self.analyzer._parse_parameters_string(param_string)
        
        self.assertEqual(params['prompt'], 'a beautiful landscape, masterpiece, best quality')
        self.assertEqual(params['steps'], '20')
        self.assertEqual(params['cfg_scale'], '7.0')
        self.assertEqual(params['sampler'], 'Euler a')
        self.assertEqual(params['seed'], '12345')
        self.assertEqual(params['width'], '512')
        self.assertEqual(params['height'], '512')
        self.assertEqual(params['model'], 'test_model.safetensors')
        self.assertEqual(params['vae'], 'test_vae.safetensors')
    
    def test_extract_prompt_info(self):
        """Test prompt information extraction."""
        metadata = {
            'prompt': 'test prompt',
            'negative_prompt': 'test negative prompt',
            'parameters': 'test prompt, Negative prompt: test negative prompt'
        }
        
        prompt_info = self.analyzer._extract_prompt_info(metadata)
        
        self.assertEqual(prompt_info['prompt'], 'test prompt')
        self.assertEqual(prompt_info['negative_prompt'], 'test negative prompt')
        self.assertIsInstance(prompt_info['wildcards'], list)
    
    def test_detect_wildcards(self):
        """Test wildcard detection in prompts."""
        prompt_with_wildcards = "a beautiful __ART_STYLE__ landscape with __WEATHER__ and __TIME_OF_DAY__"
        wildcards = self.analyzer._detect_wildcards(prompt_with_wildcards)
        
        self.assertIn('ART_STYLE', wildcards)
        self.assertIn('WEATHER', wildcards)
        self.assertIn('TIME_OF_DAY', wildcards)
        self.assertEqual(len(wildcards), 3)
    
    def test_detect_wildcards_no_wildcards(self):
        """Test wildcard detection with no wildcards."""
        prompt_no_wildcards = "a beautiful landscape with mountains and trees"
        wildcards = self.analyzer._detect_wildcards(prompt_no_wildcards)
        
        self.assertEqual(len(wildcards), 0)
    
    def test_create_suggested_config(self):
        """Test creation of suggested config from parameters."""
        params = {
            'steps': '25',
            'width': '768',
            'height': '768',
            'sampler': 'DPM++ 2M',
            'cfg_scale': '8.5',
            'model': 'realistic_vision_v5.1.safetensors',
            'vae': 'vae-ft-mse-840000-ema-pruned.safetensors'
        }
        
        prompt_info = {
            'prompt': 'a beautiful landscape',
            'negative_prompt': 'blurry, low quality',
            'wildcards': []
        }
        
        config = self.analyzer._create_suggested_config(params, prompt_info)
        
        self.assertEqual(config['name'], 'Extracted Configuration')
        self.assertEqual(config['model_type'], 'sd')
        self.assertEqual(config['prompt_settings']['base_prompt'], 'a beautiful landscape')
        self.assertEqual(config['prompt_settings']['negative_prompt'], 'blurry, low quality')
        self.assertEqual(config['generation_settings']['steps'], 25)
        self.assertEqual(config['generation_settings']['width'], 768)
        self.assertEqual(config['generation_settings']['height'], 768)
        self.assertEqual(config['generation_settings']['sampler'], 'DPM++ 2M')
        self.assertEqual(config['generation_settings']['cfg_scale'], 8.5)
        self.assertEqual(config['model_settings']['checkpoint'], 'realistic_vision_v5.1.safetensors')
        self.assertEqual(config['model_settings']['vae'], 'vae-ft-mse-840000-ema-pruned.safetensors')
    
    def test_analyze_multiple_images(self):
        """Test analyzing multiple images."""
        # Create test images
        images = []
        for i in range(3):
            img = Image.new('RGB', (256 + i*64, 256 + i*64), color=(i*50, i*50, i*50))
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            images.append(img_data)
        
        results = self.analyzer.analyze_multiple_images(images)
        
        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertTrue(result['success'])
            self.assertEqual(result['width'], 256 + i*64)
            self.assertEqual(result['height'], 256 + i*64)
    
    def test_error_handling(self):
        """Test error handling in image analysis."""
        # Test with invalid base64
        result = self.analyzer.analyze_image("invalid_data")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Test with empty data
        result = self.analyzer.analyze_image("")
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_extract_parameters_from_string(self):
        """Test extracting parameters from string."""
        param_string = "test prompt, Negative prompt: test negative, Steps: 30, CFG scale: 9.0, Sampler: Euler a, Seed: 42, Size: 1024x1024, Model: test.safetensors"
        params = self.analyzer.extract_parameters_from_string(param_string)
        
        self.assertEqual(params['prompt'], 'test prompt')
        self.assertEqual(params['negative_prompt'], 'test negative')
        self.assertEqual(params['steps'], '30')
        self.assertEqual(params['cfg_scale'], '9.0')
        self.assertEqual(params['sampler'], 'Euler a')
        self.assertEqual(params['seed'], '42')
        self.assertEqual(params['width'], '1024')
        self.assertEqual(params['height'], '1024')
        self.assertEqual(params['model'], 'test.safetensors')


if __name__ == '__main__':
    unittest.main() 