#!/usr/bin/env python3
"""
Integration tests for image analysis and config management endpoints.
Tests the web dashboard API endpoints for image analysis functionality.
"""

import unittest
import json
import base64
import io
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image, PngImagePlugin

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'web_dashboard'))
from app import app


class TestImageAnalysisEndpoints(unittest.TestCase):
    """Test cases for image analysis and config management endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test image with metadata
        self.test_image = Image.new('RGB', (512, 512), color='red')
        
        # Add metadata to test image
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'a beautiful landscape, masterpiece, best quality, Steps: 20, CFG scale: 7.0, Sampler: Euler a, Seed: 12345, Size: 512x512, Model: test_model.safetensors, VAE: test_vae.safetensors')
        metadata.add_text('prompt', 'a beautiful landscape, masterpiece, best quality')
        metadata.add_text('negative_prompt', 'blurry, low quality, bad anatomy')
        
        # Save image to buffer
        img_buffer = io.BytesIO()
        self.test_image.save(img_buffer, format='PNG', pnginfo=metadata)
        self.image_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Create test config
        self.test_config = {
            'name': 'Test Config',
            'description': 'Test configuration for unit tests',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': 'a beautiful landscape',
                'negative_prompt': 'blurry, low quality'
            },
            'generation_settings': {
                'steps': 20,
                'width': 512,
                'height': 512,
                'batch_size': 1,
                'sampler': 'Euler a',
                'cfg_scale': 7.0
            },
            'model_settings': {
                'checkpoint': 'test_model.safetensors',
                'vae': 'test_vae.safetensors',
                'text_encoder': '',
                'gpu_weight': 1.0,
                'swap_method': 'weight',
                'swap_location': 'cpu'
            },
            'output_settings': {
                'dir': 'outputs/test_config/{timestamp}/',
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            }
        }
    
    def test_analyze_image_endpoint_success(self):
        """Test successful image analysis endpoint."""
        data = {
            'image_data': self.image_data
        }
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 512)
        self.assertEqual(result['height'], 512)
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
    
    def test_analyze_image_endpoint_no_data(self):
        """Test image analysis endpoint with no image data."""
        data = {}
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('No image data provided', result['error'])
    
    def test_analyze_image_endpoint_invalid_data(self):
        """Test image analysis endpoint with invalid image data."""
        data = {
            'image_data': 'invalid_base64_data'
        }
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
    
    def test_get_config_settings_endpoint(self):
        """Test getting config settings endpoint."""
        with patch('core.config_handler.ConfigHandler.get_config') as mock_get_config:
            mock_get_config.return_value = self.test_config
            
            response = self.app.get('/api/configs/test_config/settings')
            
            self.assertEqual(response.status_code, 200)
            
            result = json.loads(response.data)
            self.assertEqual(result['config_name'], 'test_config')
            self.assertEqual(result['settings'], self.test_config)
    
    def test_get_config_settings_endpoint_not_found(self):
        """Test getting config settings for non-existent config."""
        with patch('web_dashboard.app.config_handler') as mock_config_handler:
            mock_config_handler.get_config.return_value = None
            
            response = self.app.get('/api/configs/nonexistent_config/settings')
            
            self.assertEqual(response.status_code, 404)
            
            result = json.loads(response.data)
            self.assertIn('error', result)
            self.assertIn('not found', result['error'])
    
    def test_update_config_settings_endpoint(self):
        """Test updating config settings endpoint."""
        updated_config = self.test_config.copy()
        updated_config['description'] = 'Updated description'
        updated_config['generation_settings']['steps'] = 30
        
        with patch('core.config_handler.ConfigHandler.update_config') as mock_update_config:
            mock_update_config.return_value = True
            
            data = {
                'settings': updated_config
            }
            
            response = self.app.put('/api/configs/test_config/settings',
                                  data=json.dumps(data),
                                  content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            
            result = json.loads(response.data)
            self.assertIn('message', result)
            self.assertIn('updated successfully', result['message'])
    
    def test_update_config_settings_endpoint_no_data(self):
        """Test updating config settings with no data."""
        data = {}
        
        response = self.app.put('/api/configs/test_config/settings',
                              data=json.dumps(data),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('No settings data provided', result['error'])
    
    def test_update_config_settings_endpoint_missing_fields(self):
        """Test updating config settings with missing required fields."""
        invalid_config = {
            'description': 'Missing required fields'
            # Missing 'name' and 'model_type'
        }
        
        data = {
            'settings': invalid_config
        }
        
        response = self.app.put('/api/configs/test_config/settings',
                              data=json.dumps(data),
                              content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('Missing required field', result['error'])
    
    def test_create_config_from_image_endpoint(self):
        """Test creating config from image analysis endpoint."""
        analysis_result = {
            'width': 512,
            'height': 512,
            'parameters': {
                'prompt': 'a beautiful landscape',
                'negative_prompt': 'blurry, low quality',
                'steps': '20',
                'cfg_scale': '7.0',
                'sampler': 'Euler a',
                'seed': '12345',
                'model': 'test_model.safetensors',
                'vae': 'test_vae.safetensors'
            },
            'prompt_info': {
                'prompt': 'a beautiful landscape',
                'negative_prompt': 'blurry, low quality',
                'wildcards': []
            }
        }
        
        data = {
            'config_name': 'test_extracted_config',
            'analysis_result': analysis_result,
            'custom_settings': {
                'name': 'test_extracted_config',
                'description': 'Config created from image analysis'
            }
        }
        
        with patch('core.config_handler.ConfigHandler.config_exists') as mock_config_exists, \
             patch('core.config_handler.ConfigHandler.create_config') as mock_create_config:
            mock_config_exists.return_value = False
            mock_create_config.return_value = True
            
            response = self.app.post('/api/configs/create-from-image',
                                   data=json.dumps(data),
                                   content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            
            result = json.loads(response.data)
            self.assertIn('message', result)
            self.assertIn('created successfully', result['message'])
            self.assertEqual(result['config_name'], 'test_extracted_config')
            
            # Verify config handler was called
            mock_create_config.assert_called_once()
    
    def test_create_config_from_image_endpoint_missing_name(self):
        """Test creating config from image with missing config name."""
        data = {
            'analysis_result': {'width': 512, 'height': 512}
        }
        
        response = self.app.post('/api/configs/create-from-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('Config name is required', result['error'])
    
    def test_create_config_from_image_endpoint_missing_analysis(self):
        """Test creating config from image with missing analysis result."""
        data = {
            'config_name': 'test_config'
        }
        
        response = self.app.post('/api/configs/create-from-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        result = json.loads(response.data)
        self.assertIn('error', result)
        self.assertIn('Analysis result is required', result['error'])
    
    def test_create_config_from_image_endpoint_config_exists(self):
        """Test creating config from image when config already exists."""
        analysis_result = {
            'width': 512,
            'height': 512,
            'parameters': {},
            'prompt_info': {'prompt': '', 'negative_prompt': '', 'wildcards': []}
        }
        
        data = {
            'config_name': 'existing_config',
            'analysis_result': analysis_result,
            'custom_settings': {}
        }
        
        with patch('core.config_handler.ConfigHandler.config_exists') as mock_config_exists:
            mock_config_exists.return_value = True
            
            response = self.app.post('/api/configs/create-from-image',
                                   data=json.dumps(data),
                                   content_type='application/json')
            
            self.assertEqual(response.status_code, 409)
            
            result = json.loads(response.data)
            self.assertIn('error', result)
            self.assertIn('already exists', result['error'])
    
    def test_analyze_image_with_data_url(self):
        """Test image analysis with data URL format."""
        # Create simple image
        img = Image.new('RGB', (256, 256), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Test with data URL prefix
        data_url = f"data:image/png;base64,{img_data}"
        
        data = {
            'image_data': data_url
        }
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 256)
        self.assertEqual(result['height'], 256)
    
    def test_analyze_image_with_suggested_config(self):
        """Test image analysis that generates suggested config."""
        # Create image with complete metadata
        img = Image.new('RGB', (768, 768), color='green')
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'a beautiful landscape, Steps: 25, CFG scale: 8.5, Sampler: DPM++ 2M, Seed: 42, Size: 768x768, Model: realistic_vision_v5.1.safetensors')
        metadata.add_text('prompt', 'a beautiful landscape')
        metadata.add_text('negative_prompt', 'blurry, low quality')
        
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', pnginfo=metadata)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        data = {
            'image_data': img_data
        }
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('suggested_config', result)
        
        suggested_config = result['suggested_config']
        self.assertEqual(suggested_config['name'], 'Extracted Configuration')
        self.assertEqual(suggested_config['model_type'], 'sd')
        self.assertEqual(suggested_config['generation_settings']['steps'], 25)
        self.assertEqual(suggested_config['generation_settings']['cfg_scale'], 8.5)
        self.assertEqual(suggested_config['generation_settings']['sampler'], 'DPM++ 2M')
        self.assertEqual(suggested_config['model_settings']['checkpoint'], 'realistic_vision_v5.1.safetensors')


if __name__ == '__main__':
    unittest.main() 