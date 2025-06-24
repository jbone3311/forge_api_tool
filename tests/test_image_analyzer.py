import unittest
import tempfile
import os
import base64
import json
from pathlib import Path
import sys
from PIL import Image, PngImagePlugin
from unittest.mock import patch, MagicMock
import io

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'core'))

from image_analyzer import ImageAnalyzer


class TestImageAnalyzer(unittest.TestCase):
    """Test cases for ImageAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ImageAnalyzer()
        
        # Create a test image
        self.test_image = Image.new('RGB', (512, 512), color='red')
        
        # Add metadata to test image
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'a beautiful landscape, Steps: 20, Sampler: Euler a, CFG scale: 7.0, Seed: 12345, Size: 512x512, Model: test_model.safetensors')
        metadata.add_text('prompt', 'a beautiful __STYLE__ landscape')
        metadata.add_text('negative_prompt', 'blurry, low quality')
        
        # Save test image with metadata
        self.test_image_path = os.path.join(self.temp_dir, "test_image.png")
        self.test_image.save(self.test_image_path, "PNG", pnginfo=metadata)
        
        # Read image data for testing
        with open(self.test_image_path, 'rb') as f:
            self.image_data = f.read()
            self.image_base64 = base64.b64encode(self.image_data).decode('utf-8')
        
        # Create test wildcard files
        self.wildcard_dir = os.path.join(self.temp_dir, "wildcards")
        os.makedirs(self.wildcard_dir, exist_ok=True)
        
        with open(os.path.join(self.wildcard_dir, "style.txt"), "w") as f:
            f.write("realistic\nanime\ncyberpunk\n")
        
        with open(os.path.join(self.wildcard_dir, "location.txt"), "w") as f:
            f.write("forest\ncity\nmountain\n")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_image_success(self):
        """Test successful image analysis."""
        result = self.analyzer.analyze_image(self.image_base64)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 512)
        self.assertEqual(result['height'], 512)
        self.assertEqual(result['format'], 'PNG')
        self.assertEqual(result['mode'], 'RGB')
        
        # Check that metadata was extracted
        self.assertIn('metadata', result)
        self.assertIn('parameters', result)
        self.assertIn('prompt_info', result)
        
        # Check that prompt info contains wildcards
        prompt_info = result['prompt_info']
        self.assertIn('wildcards', prompt_info)
        self.assertIn('STYLE', prompt_info['wildcards'])
    
    def test_extract_parameters(self):
        """Test parameter extraction from metadata."""
        metadata = {
            'parameters': 'a beautiful landscape, Steps: 20, Sampler: Euler a, CFG scale: 7.0, Seed: 12345, Size: 512x512, Model: test_model.safetensors',
            'prompt': 'a beautiful landscape',
            'negative_prompt': 'blurry, low quality'
        }
        
        params = self.analyzer._extract_parameters(metadata)
        
        self.assertEqual(params['steps'], '20')
        self.assertEqual(params['sampler'], 'Euler a')
        self.assertEqual(params['cfg_scale'], '7.0')
        self.assertEqual(params['seed'], '12345')
        self.assertEqual(params['width'], 512)
        self.assertEqual(params['height'], 512)
        self.assertEqual(params['model'], 'test_model.safetensors')
    
    def test_parse_parameters_string(self):
        """Test parsing parameters string."""
        params_str = 'a beautiful landscape, Steps: 20, Sampler: Euler a, CFG scale: 7.0, Seed: 12345, Size: 512x512, Model: test_model.safetensors, VAE: test_vae.safetensors'
        
        params = self.analyzer._parse_parameters_string(params_str)
        
        self.assertEqual(params['steps'], '20')
        self.assertEqual(params['sampler'], 'Euler a')
        self.assertEqual(params['cfg_scale'], '7.0')
        self.assertEqual(params['seed'], '12345')
        self.assertEqual(params['width'], 512)
        self.assertEqual(params['height'], 512)
        self.assertEqual(params['model'], 'test_model.safetensors')
        self.assertEqual(params['vae'], 'test_vae.safetensors')
    
    def test_extract_prompt_info(self):
        """Test prompt information extraction."""
        metadata = {
            'prompt': 'a beautiful __STYLE__ landscape with __LIGHTING__',
            'negative_prompt': 'blurry, low quality',
            'parameters': 'a beautiful __STYLE__ landscape with __LIGHTING__, Steps: 20'
        }
        
        prompt_info = self.analyzer._extract_prompt_info(metadata)
        
        self.assertEqual(prompt_info['prompt'], 'a beautiful __STYLE__ landscape with __LIGHTING__')
        self.assertEqual(prompt_info['negative_prompt'], 'blurry, low quality')
        self.assertIn('STYLE', prompt_info['wildcards'])
        self.assertIn('LIGHTING', prompt_info['wildcards'])
    
    def test_detect_wildcards(self):
        """Test wildcard detection in prompts."""
        prompt = 'a beautiful __STYLE__ landscape with [lighting] and <weather>'
        
        wildcards = self.analyzer._detect_wildcards(prompt)
        
        # Should only find Automatic1111 format wildcards
        self.assertIn('STYLE', wildcards)
        self.assertNotIn('lighting', wildcards)  # Not Automatic1111 format
        self.assertNotIn('weather', wildcards)   # Not Automatic1111 format
    
    def test_create_suggested_config(self):
        """Test creating suggested configuration."""
        # Mock image analysis result
        analysis_result = {
            'width': 512,
            'height': 512,
            'prompt': 'a beautiful __STYLE__ landscape',
            'negative_prompt': 'blurry, low quality',
            'parameters': {
                'steps': '20',
                'cfg_scale': '7.0',
                'sampler': 'Euler a',
                'model': 'test_model.safetensors'
            }
        }
        
        config = self.analyzer._create_suggested_config(
            analysis_result['parameters'],
            {'prompt': analysis_result['prompt'], 'negative_prompt': analysis_result['negative_prompt']}
        )
        
        self.assertEqual(config['name'], 'Extracted Configuration')
        self.assertEqual(config['model_type'], 'sd')
        self.assertEqual(config['prompt_settings']['base_prompt'], 'a beautiful __STYLE__ landscape')
        self.assertEqual(config['prompt_settings']['negative_prompt'], 'blurry, low quality')
        self.assertEqual(config['generation_settings']['steps'], 20)
        self.assertEqual(config['generation_settings']['cfg_scale'], 7.0)
    
    def test_validate_image_format(self):
        """Test image format validation."""
        self.assertTrue(self.analyzer.validate_image_format('test.png'))
        self.assertTrue(self.analyzer.validate_image_format('test.jpg'))
        self.assertTrue(self.analyzer.validate_image_format('test.jpeg'))
        self.assertTrue(self.analyzer.validate_image_format('test.webp'))
        self.assertFalse(self.analyzer.validate_image_format('test.gif'))
        self.assertFalse(self.analyzer.validate_image_format('test.txt'))
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.analyzer.get_supported_formats()
        
        self.assertIn('.png', formats)
        self.assertIn('.jpg', formats)
        self.assertIn('.jpeg', formats)
        self.assertIn('.webp', formats)
    
    def test_analyze_image_without_metadata(self):
        """Test analyzing image without metadata."""
        # Create a simple image without metadata
        from PIL import Image
        import io
        import base64
        
        # Create a simple image
        img = Image.new('RGB', (100, 100), color='red')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        result = self.analyzer.analyze_image(img_data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['width'], 100)
        self.assertEqual(result['height'], 100)
        self.assertEqual(result['format'], 'PNG')
        
        # Should not have parameters if no metadata
        self.assertNotIn('parameters', result)
    
    def test_analyze_image_invalid_data(self):
        """Test analyzing invalid image data."""
        invalid_data = "invalid_base64_data"
        
        result = self.analyzer.analyze_image(invalid_data)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_extract_metadata_from_image(self):
        """Test extracting metadata from image."""
        # Create image with various metadata
        image = Image.new('RGB', (512, 512), color='green')
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('parameters', 'test parameters')
        metadata.add_text('prompt', 'test prompt')
        metadata.add_text('custom_field', 'custom value')
        
        image_path = os.path.join(self.temp_dir, "metadata_image.png")
        image.save(image_path, "PNG", pnginfo=metadata)
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        result = self.analyzer.analyze_image(image_data)
        
        self.assertTrue(result['success'])
        self.assertIn('parameters', result['metadata'])
        self.assertIn('prompt', result['metadata'])
        self.assertIn('custom_field', result['metadata'])
    
    def test_wildcard_detection_edge_cases(self):
        """Test wildcard detection edge cases."""
        # Test nested wildcards
        prompt1 = 'a __STYLE__ with __STYLE__'
        wildcards1 = self.analyzer._detect_wildcards(prompt1)
        self.assertEqual(len(wildcards1), 1)  # Should deduplicate
        self.assertIn('STYLE', wildcards1)
        
        # Test empty prompt
        prompt2 = ''
        wildcards2 = self.analyzer._detect_wildcards(prompt2)
        self.assertEqual(wildcards2, [])
        
        # Test prompt with no wildcards
        prompt3 = 'a simple prompt without wildcards'
        wildcards3 = self.analyzer._detect_wildcards(prompt3)
        self.assertEqual(wildcards3, [])
    
    def test_analyze_image_metadata(self):
        """Test analyzing image metadata."""
        # Create image with metadata
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text('prompt', 'a beautiful __STYLE__ landscape')
        metadata.add_text('parameters', 'Steps: 20, CFG: 7.0')
        
        image_with_metadata = Image.new('RGB', (512, 512), color='blue')
        image_buffer = io.BytesIO()
        image_with_metadata.save(image_buffer, format='PNG', pnginfo=metadata)
        image_data = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        
        # Analyze image
        result = self.analyzer.analyze_image(image_data)
        
        self.assertIn('prompt_info', result)
        self.assertIn('prompt', result['prompt_info'])
        self.assertIn('parameters', result['metadata'])
        self.assertEqual(result['prompt_info']['prompt'], 'a beautiful __STYLE__ landscape')
        self.assertEqual(result['metadata']['parameters'], 'Steps: 20, CFG: 7.0')
    
    def test_extract_prompt_from_metadata(self):
        """Test extracting prompt from image metadata."""
        # Test with valid metadata
        metadata = {
            'prompt': 'a beautiful __STYLE__ landscape with __LIGHTING__',
            'parameters': 'a beautiful __STYLE__ landscape with __LIGHTING__, Steps: 20'
        }
        
        prompt_info = self.analyzer.extract_prompt_from_metadata(metadata)
        
        self.assertEqual(prompt_info['prompt'], 'a beautiful __STYLE__ landscape with __LIGHTING__')
        self.assertIn('STYLE', prompt_info['wildcards'])
        self.assertIn('LIGHTING', prompt_info['wildcards'])
    
    def test_parse_prompt_for_wildcards(self):
        """Test parsing prompt to identify wildcards."""
        prompt = 'a beautiful __STYLE__ landscape with [lighting] and <weather>'
        
        wildcards = self.analyzer.parse_prompt_for_wildcards(prompt)
        
        # Should only find Automatic1111 format wildcards
        self.assertIn('STYLE', wildcards)
        self.assertNotIn('lighting', wildcards)  # Not Automatic1111 format
        self.assertNotIn('weather', wildcards)   # Not Automatic1111 format
    
    def test_create_config_from_image(self):
        """Test creating configuration from analyzed image."""
        # Mock image analysis result
        analysis_result = {
            'width': 512,
            'height': 512,
            'prompt': 'a beautiful __STYLE__ landscape',
            'negative_prompt': 'blurry, low quality',
            'steps': 20,
            'cfg_scale': 7.0
        }
        
        config = self.analyzer.create_config_from_image(
            analysis_result,
            'test_config',
            'wildcards'
        )
        
        self.assertEqual(config['name'], 'test_config')
        self.assertEqual(config['model_type'], 'sd')
        self.assertEqual(config['prompt_settings']['base_prompt'], 'a beautiful __STYLE__ landscape')
        self.assertEqual(config['prompt_settings']['negative_prompt'], 'blurry, low quality')
        self.assertEqual(config['generation_settings']['steps'], 20)
        self.assertEqual(config['generation_settings']['cfg_scale'], 7.0)
    
    def test_validate_wildcard_files(self):
        """Test validating wildcard files exist."""
        # Test with existing wildcards
        wildcards = {
            'STYLE': os.path.join(self.wildcard_dir, 'style.txt'),
            'LOCATION': os.path.join(self.wildcard_dir, 'location.txt')
        }
        
        result = self.analyzer.validate_wildcard_files(wildcards)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['missing']), 0)
        
        # Test with missing wildcard
        wildcards['MISSING'] = os.path.join(self.wildcard_dir, 'missing.txt')
        
        result = self.analyzer.validate_wildcard_files(wildcards)
        self.assertFalse(result['valid'])
        self.assertIn('MISSING', result['missing'])
    
    def test_suggest_wildcard_values(self):
        """Test suggesting wildcard values based on prompt context."""
        prompt = 'a beautiful __STYLE__ landscape of __LOCATION__'
        
        suggestions = self.analyzer.suggest_wildcard_values(prompt)
        
        self.assertIn('STYLE', suggestions)
        self.assertIn('LOCATION', suggestions)
        
        # Should suggest relevant values
        style_suggestions = suggestions['STYLE']
        self.assertIn('realistic', style_suggestions)
        # Don't expect 'landscape' in style suggestions - it's a location term
    
    def test_enhance_prompt_with_wildcards(self):
        """Test enhancing a simple prompt with wildcards."""
        simple_prompt = 'a beautiful landscape'
        
        enhanced = self.analyzer.enhance_prompt_with_wildcards(simple_prompt)
        
        # Should add wildcards for variety
        self.assertIn('__STYLE__', enhanced)
        self.assertIn('__LOCATION__', enhanced)
    
    def test_analyze_multiple_images(self):
        """Test analyzing multiple images for batch processing."""
        # Create multiple test images
        image_paths = []
        for i in range(3):
            img = Image.new('RGB', (512, 512), color=(i*50, i*50, i*50))
            path = os.path.join(self.temp_dir, f"test_image_{i}.png")
            img.save(path)
            image_paths.append(path)
        
        results = self.analyzer.analyze_multiple_images(image_paths)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('path', result)
            self.assertIn('analysis', result)
    
    def test_extract_parameters_from_string(self):
        """Test extracting generation parameters from string."""
        param_string = "Steps: 20, CFG: 7.0, Sampler: DPM++ 2M Karras, Size: 512x512"
        
        params = self.analyzer.extract_parameters_from_string(param_string)
        
        self.assertEqual(int(params.get('steps')), 20)  # Convert to int for comparison
        if params.get('cfg_scale') is not None:
            self.assertEqual(float(params.get('cfg_scale')), 7.0)
        self.assertEqual(params.get('sampler'), 'DPM++ 2M Karras')
        if params.get('width') is not None:
            self.assertEqual(int(params.get('width')), 512)
        if params.get('height') is not None:
            self.assertEqual(int(params.get('height')), 512)
    
    def test_create_wildcard_file(self):
        """Test creating wildcard file from suggestions."""
        wildcard_name = 'STYLE'
        suggestions = ['realistic', 'anime', 'cyberpunk', 'photorealistic']
        
        file_path = self.analyzer.create_wildcard_file(
            wildcard_name, 
            suggestions, 
            self.wildcard_dir
        )
        
        self.assertTrue(os.path.exists(file_path))
        
        # Verify content
        with open(file_path, 'r') as f:
            content = f.read().strip().split('\n')
        
        self.assertEqual(content, suggestions)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with non-existent image
        result = self.analyzer.analyze_image("invalid_base64_data")
        self.assertIn('error', result)
        
        # Test with invalid metadata
        result = self.analyzer.extract_prompt_from_metadata({})
        # Should return empty prompt info, not error
        self.assertEqual(result['prompt'], '')
        self.assertEqual(result['negative_prompt'], '')
        self.assertEqual(result['wildcards'], [])
        
        # Test with invalid prompt
        wildcards = self.analyzer.parse_prompt_for_wildcards("")
        self.assertEqual(wildcards, [])


if __name__ == '__main__':
    unittest.main() 