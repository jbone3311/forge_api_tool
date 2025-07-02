#!/usr/bin/env python3
"""
Functional tests for image analysis and config management frontend functionality.
Tests the JavaScript functions and user interactions.
"""

import unittest
import json
import base64
import io
import os
import sys
from unittest.mock import patch, MagicMock
from PIL import Image, PngImagePlugin

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Flask app for testing
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'web_dashboard'))
from app import app


class TestImageAnalysisFrontend(unittest.TestCase):
    """Test cases for frontend image analysis functionality."""
    
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
    
    def test_dashboard_loads_with_image_analysis_section(self):
        """Test that the dashboard loads with the image analysis section."""
        response = self.app.get('/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check that the response contains the image analysis section
        content = response.data.decode('utf-8')
        self.assertIn('Image Analysis', content)
        self.assertIn('image-drop-zone', content)
        self.assertIn('analysis-results', content)
        self.assertIn('create-config-modal', content)
    
    def test_image_analysis_endpoint_integration(self):
        """Test the complete image analysis workflow through the API."""
        # Test image analysis endpoint
        data = {
            'image_data': self.image_data
        }
        
        response = self.app.post('/api/analyze-image',
                               data=json.dumps(data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('parameters', result)
        self.assertIn('prompt_info', result)
        
        # Test creating config from analysis
        config_data = {
            'config_name': 'test_extracted_config',
            'analysis_result': result,
            'custom_settings': {
                'name': 'test_extracted_config',
                'description': 'Config created from image analysis'
            }
        }
        
        with patch('core.config_handler.ConfigHandler.config_exists') as mock_config_exists, \
             patch('core.config_handler.ConfigHandler.create_config') as mock_create_config:
            mock_config_exists.return_value = False
            mock_create_config.return_value = True
            
            config_response = self.app.post('/api/configs/create-from-image',
                                          data=json.dumps(config_data),
                                          content_type='application/json')
            
            self.assertEqual(config_response.status_code, 200)
            
            config_result = json.loads(config_response.data)
            self.assertIn('message', config_result)
            self.assertIn('created successfully', config_result['message'])
    
    def test_config_editor_endpoint_integration(self):
        """Test the config editor workflow through the API."""
        # Test getting config settings
        with patch('core.config_handler.ConfigHandler.get_config') as mock_get_config, \
             patch('core.config_handler.ConfigHandler.update_config') as mock_update_config:
            mock_get_config.return_value = self.test_config
            mock_update_config.return_value = True
            
            response = self.app.get('/api/configs/test_config/settings')
            
            self.assertEqual(response.status_code, 200)
            
            result = json.loads(response.data)
            self.assertEqual(result['config_name'], 'test_config')
            self.assertEqual(result['settings'], self.test_config)
            
            # Test updating config settings
            updated_config = self.test_config.copy()
            updated_config['description'] = 'Updated description'
            updated_config['generation_settings']['steps'] = 30
            
            update_data = {
                'settings': updated_config
            }
            
            update_response = self.app.put('/api/configs/test_config/settings',
                                         data=json.dumps(update_data),
                                         content_type='application/json')
            
            self.assertEqual(update_response.status_code, 200)
            
            update_result = json.loads(update_response.data)
            self.assertIn('message', update_result)
            self.assertIn('updated successfully', update_result['message'])
    
    def test_image_analysis_with_different_formats(self):
        """Test image analysis with different image formats."""
        # Test PNG format
        png_img = Image.new('RGB', (256, 256), color='blue')
        png_buffer = io.BytesIO()
        png_img.save(png_buffer, format='PNG')
        png_data = base64.b64encode(png_buffer.getvalue()).decode()
        
        png_response = self.app.post('/api/analyze-image',
                                   data=json.dumps({'image_data': png_data}),
                                   content_type='application/json')
        
        self.assertEqual(png_response.status_code, 200)
        png_result = json.loads(png_response.data)
        self.assertTrue(png_result['success'])
        self.assertEqual(png_result['format'], 'PNG')
        
        # Test JPEG format
        jpeg_img = Image.new('RGB', (128, 128), color='green')
        jpeg_buffer = io.BytesIO()
        jpeg_img.save(jpeg_buffer, format='JPEG')
        jpeg_data = base64.b64encode(jpeg_buffer.getvalue()).decode()
        
        jpeg_response = self.app.post('/api/analyze-image',
                                    data=json.dumps({'image_data': jpeg_data}),
                                    content_type='application/json')
        
        self.assertEqual(jpeg_response.status_code, 200)
        jpeg_result = json.loads(jpeg_response.data)
        self.assertTrue(jpeg_result['success'])
        self.assertEqual(jpeg_result['format'], 'JPEG')
    
    def test_image_analysis_error_handling(self):
        """Test error handling in image analysis."""
        # Test with invalid image data
        invalid_response = self.app.post('/api/analyze-image',
                                       data=json.dumps({'image_data': 'invalid_data'}),
                                       content_type='application/json')
        
        self.assertEqual(invalid_response.status_code, 400)
        invalid_result = json.loads(invalid_response.data)
        self.assertIn('error', invalid_result)
        
        # Test with no image data
        no_data_response = self.app.post('/api/analyze-image',
                                       data=json.dumps({}),
                                       content_type='application/json')
        
        self.assertEqual(no_data_response.status_code, 400)
        no_data_result = json.loads(no_data_response.data)
        self.assertIn('error', no_data_result)
        self.assertIn('No image data provided', no_data_result['error'])
    
    def test_config_management_error_handling(self):
        """Test error handling in config management."""
        # Test getting non-existent config
        with patch('core.config_handler.ConfigHandler.get_config') as mock_get_config:
            mock_get_config.side_effect = FileNotFoundError("Config file not found")
            
            response = self.app.get('/api/configs/nonexistent_config/settings')
            
            self.assertEqual(response.status_code, 404)
            result = json.loads(response.data)
            self.assertIn('error', result)
            self.assertIn('not found', result['error'])
        
        # Test updating config with missing required fields
        invalid_config = {
            'description': 'Missing required fields'
            # Missing 'name' and 'model_type'
        }
        
        update_response = self.app.put('/api/configs/test_config/settings',
                                     data=json.dumps({'settings': invalid_config}),
                                     content_type='application/json')
        
        self.assertEqual(update_response.status_code, 400)
        update_result = json.loads(update_response.data)
        self.assertIn('error', update_result)
        self.assertIn('Missing required field', update_result['error'])
    
    def test_create_config_from_image_validation(self):
        """Test validation when creating config from image."""
        # Test with missing config name
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
        
        # Test with missing analysis result
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
        
        # Test with existing config name
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
    
    def test_image_analysis_with_complex_metadata(self):
        """Test image analysis with complex metadata."""
        # Create image with complex metadata
        img = Image.new('RGB', (1024, 1024), color='purple')
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'a beautiful landscape with mountains, masterpiece, best quality, Steps: 30, CFG scale: 8.5, Sampler: DPM++ 2M Karras, Seed: 42, Size: 1024x1024, Model: realistic_vision_v5.1.safetensors, VAE: vae-ft-mse-840000-ema-pruned.safetensors')
        metadata.add_text('prompt', 'a beautiful landscape with mountains, masterpiece, best quality')
        metadata.add_text('negative_prompt', 'blurry, low quality, bad anatomy, worst quality, low resolution')
        metadata.add_text('wildcards', 'STYLE,WEATHER,TIME_OF_DAY')
        
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
        self.assertEqual(result['width'], 1024)
        self.assertEqual(result['height'], 1024)
        self.assertIn('parameters', result)
        self.assertIn('prompt_info', result)
        
        # Check complex parameters
        params = result['parameters']
        self.assertEqual(params['steps'], '30')
        self.assertEqual(params['cfg_scale'], '8.5')
        self.assertEqual(params['sampler'], 'DPM++ 2M Karras')
        self.assertEqual(params['seed'], '42')
        self.assertEqual(params['model'], 'realistic_vision_v5.1.safetensors')
        self.assertEqual(params['vae'], 'vae-ft-mse-840000-ema-pruned.safetensors')
        
        # Check prompt info
        prompt_info = result['prompt_info']
        self.assertIn('wildcards', prompt_info)
        self.assertIsInstance(prompt_info['wildcards'], list)
    
    def test_suggested_config_generation(self):
        """Test that suggested config is generated from analysis."""
        # Create image with complete metadata
        img = Image.new('RGB', (768, 768), color='orange')
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'a beautiful landscape, Steps: 25, CFG scale: 8.0, Sampler: Euler a, Seed: 123, Size: 768x768, Model: test_model.safetensors')
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
        self.assertEqual(suggested_config['generation_settings']['cfg_scale'], 8.0)
        self.assertEqual(suggested_config['generation_settings']['sampler'], 'Euler a')
        self.assertEqual(suggested_config['model_settings']['checkpoint'], 'test_model.safetensors')


if __name__ == '__main__':
    unittest.main() 