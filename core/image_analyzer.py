import json
import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image, PngImagePlugin
import re


class ImageAnalyzer:
    """Analyzes images to extract generation settings and metadata."""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.webp']
    
    def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze an image to extract generation settings."""
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Extract metadata
            metadata = self._extract_metadata(image)
            
            # Extract generation parameters
            params = self._extract_parameters(metadata)
            
            # Extract prompt information
            prompt_info = self._extract_prompt_info(metadata)
            
            return {
                'success': True,
                'metadata': metadata,
                'parameters': params,
                'prompt_info': prompt_info,
                'suggested_config': self._create_suggested_config(params, prompt_info)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_metadata(self, image: Image.Image) -> Dict[str, Any]:
        """Extract metadata from image."""
        metadata = {}
        
        # Extract PNG metadata
        if hasattr(image, 'info') and image.info:
            metadata.update(image.info)
        
        # Extract EXIF data
        if hasattr(image, '_getexif') and image._getexif():
            metadata['exif'] = dict(image._getexif())
        
        # Extract PNG text chunks
        if hasattr(image, 'text') and image.text:
            metadata['text'] = dict(image.text)
        
        return metadata
    
    def _extract_parameters(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generation parameters from metadata."""
        params = {}
        
        # Look for common parameter keys
        parameter_keys = [
            'parameters', 'prompt', 'negative_prompt', 'steps', 'sampler',
            'cfg_scale', 'seed', 'width', 'height', 'model', 'vae'
        ]
        
        for key in parameter_keys:
            if key in metadata:
                params[key] = metadata[key]
        
        # Parse parameters string if it exists
        if 'parameters' in metadata:
            params.update(self._parse_parameters_string(metadata['parameters']))
        
        return params
    
    def _parse_parameters_string(self, params_str: str) -> Dict[str, Any]:
        """Parse parameters string into individual parameters."""
        params = {}
        
        # Common patterns in parameter strings
        patterns = {
            'steps': r'Steps: (\d+)',
            'sampler': r'Sampler: ([^,]+)',
            'cfg_scale': r'CFG scale: ([\d.]+)',
            'seed': r'Seed: (\d+)',
            'size': r'Size: (\d+)x(\d+)',
            'model': r'Model: ([^,]+)',
            'vae': r'VAE: ([^,]+)',
            'negative_prompt': r'Negative prompt: ([^,]+)',
        }
        
        for param_name, pattern in patterns.items():
            match = re.search(pattern, params_str)
            if match:
                if param_name == 'size':
                    params['width'] = int(match.group(1))
                    params['height'] = int(match.group(2))
                else:
                    params[param_name] = match.group(1)
        
        return params
    
    def _extract_prompt_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract prompt information from metadata."""
        prompt_info = {
            'prompt': '',
            'negative_prompt': '',
            'wildcards': []
        }
        
        # Extract prompt
        if 'prompt' in metadata:
            prompt_info['prompt'] = metadata['prompt']
        elif 'parameters' in metadata:
            # Try to extract prompt from parameters
            prompt_match = re.search(r'^([^,]+?)(?:,|$)', metadata['parameters'])
            if prompt_match:
                prompt_info['prompt'] = prompt_match.group(1).strip()
        
        # Extract negative prompt
        if 'negative_prompt' in metadata:
            prompt_info['negative_prompt'] = metadata['negative_prompt']
        
        # Detect potential wildcards in prompt
        if prompt_info['prompt']:
            wildcards = self._detect_wildcards(prompt_info['prompt'])
            prompt_info['wildcards'] = wildcards
        
        return prompt_info
    
    def _detect_wildcards(self, prompt: str) -> List[str]:
        """Detect potential wildcard patterns in prompt using Automatic1111 format."""
        wildcards = []
        
        # Look for Automatic1111 wildcard patterns only
        pattern = r'__([A-Z_]+)__'  # __wildcard_name__ (Automatic1111 format)
        matches = re.findall(pattern, prompt)
        wildcards.extend(matches)
        
        return list(set(wildcards))  # Remove duplicates
    
    def _create_suggested_config(self, params: Dict[str, Any], prompt_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a suggested configuration based on extracted parameters."""
        config = {
            'name': 'Extracted Configuration',
            'description': 'Configuration extracted from image analysis',
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': prompt_info.get('prompt', ''),
                'negative_prompt': prompt_info.get('negative_prompt', ''),
                'wildcards': {}
            },
            'generation_settings': {
                'steps': int(params.get('steps', 20)),
                'width': int(params.get('width', 512)),
                'height': int(params.get('height', 512)),
                'batch_size': 1,
                'sampler': params.get('sampler', 'Euler a'),
                'cfg_scale': float(params.get('cfg_scale', 7.0))
            },
            'model_settings': {
                'checkpoint': params.get('model', ''),
                'vae': params.get('vae', ''),
                'text_encoder': '',
                'gpu_weight': 1.0,
                'swap_method': 'weight',
                'swap_location': 'cpu'
            },
            'output_settings': {
                'output_dir': 'outputs/extracted_config',
                'filename_pattern': '{prompt_hash}_{seed}_{timestamp}',
                'save_metadata': True,
                'save_prompt_list': True
            },
            'wildcard_settings': {
                'randomization_mode': 'smart_cycle',
                'cycle_length': 10,
                'shuffle_on_reset': True
            },
            'alwayson_scripts': {}
        }
        
        # Add wildcards if detected
        if prompt_info.get('wildcards'):
            for wildcard in prompt_info['wildcards']:
                config['prompt_settings']['wildcards'][wildcard] = f'wildcards/{wildcard}.txt'
        
        return config
    
    def validate_image_format(self, filename: str) -> bool:
        """Validate if the image format is supported."""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported image formats."""
        return self.supported_formats.copy()
    
    def extract_prompt_from_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract prompt information from metadata."""
        return self._extract_prompt_info(metadata)
    
    def parse_prompt_for_wildcards(self, prompt: str) -> List[str]:
        """Parse prompt to identify wildcards using Automatic1111 format."""
        return self._detect_wildcards(prompt)
    
    def create_config_from_image(self, analysis_result: Dict[str, Any], config_name: str, wildcard_dir: str) -> Dict[str, Any]:
        """Create a configuration from analyzed image."""
        config = {
            'name': config_name,
            'description': 'Configuration created from image analysis',
            'model_type': 'sd',
            'model_settings': {
                'width': analysis_result.get('width', 512),
                'height': analysis_result.get('height', 512),
                'steps': 20,
                'cfg_scale': 7.0,
                'sampler': 'DPM++ 2M Karras'
            },
            'prompt_settings': {
                'base_prompt': analysis_result.get('prompt', ''),
                'negative_prompt': ''
            },
            'wildcards': {},
            'output_settings': {
                'output_dir': f'outputs/{config_name.lower().replace(" ", "_")}',
                'filename_pattern': '{prompt_hash}_{seed}_{timestamp}',
                'save_metadata': True
            },
            'batch_settings': {
                'batch_size': 1,
                'total_images': 1
            }
        }
        
        # Add wildcards if detected
        if 'prompt' in analysis_result:
            wildcards = self._detect_wildcards(analysis_result['prompt'])
            for wildcard in wildcards:
                config['wildcards'][wildcard] = f'{wildcard_dir}/{wildcard.lower()}.txt'
        
        return config
    
    def validate_wildcard_files(self, wildcards: Dict[str, str]) -> Dict[str, Any]:
        """Validate that wildcard files exist."""
        import os
        
        missing = []
        available = []
        
        for wildcard_name, wildcard_path in wildcards.items():
            if os.path.exists(wildcard_path):
                available.append(wildcard_name)
            else:
                missing.append(wildcard_name)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'available': available
        }
    
    def suggest_wildcard_values(self, prompt: str) -> Dict[str, List[str]]:
        """Suggest wildcard values based on prompt context."""
        suggestions = {}
        
        # Extract wildcards from prompt
        wildcards = self._detect_wildcards(prompt)
        
        # Suggest values based on wildcard name
        for wildcard in wildcards:
            wildcard_lower = wildcard.lower()
            if 'style' in wildcard_lower:
                suggestions[wildcard] = ['realistic', 'anime', 'cyberpunk', 'photorealistic', 'oil painting', 'watercolor']
            elif 'location' in wildcard_lower:
                suggestions[wildcard] = ['forest', 'city', 'mountain', 'beach', 'desert', 'ocean']
            elif 'lighting' in wildcard_lower:
                suggestions[wildcard] = ['sunset', 'dawn', 'night', 'midday', 'golden hour', 'blue hour']
            else:
                suggestions[wildcard] = ['option1', 'option2', 'option3']
        
        return suggestions
    
    def enhance_prompt_with_wildcards(self, simple_prompt: str) -> str:
        """Enhance a simple prompt with wildcards."""
        enhanced = simple_prompt
        
        # Add style wildcard if not present
        if '__STYLE__' not in enhanced:
            enhanced = enhanced.replace('beautiful', 'beautiful __STYLE__')
        
        # Add location wildcard if not present
        if '__LOCATION__' not in enhanced:
            if 'landscape' in enhanced:
                enhanced = enhanced.replace('landscape', '__LOCATION__ landscape')
            elif 'portrait' in enhanced:
                enhanced = enhanced.replace('portrait', '__LOCATION__ portrait')
        
        return enhanced
    
    def analyze_multiple_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple images for batch processing."""
        results = []
        
        for path in image_paths:
            try:
                # For now, return basic info since we can't easily decode file paths
                results.append({
                    'path': path,
                    'analysis': {
                        'success': True,
                        'metadata': {},
                        'parameters': {},
                        'prompt_info': {'prompt': '', 'negative_prompt': '', 'wildcards': []}
                    }
                })
            except Exception as e:
                results.append({
                    'path': path,
                    'analysis': {
                        'success': False,
                        'error': str(e)
                    }
                })
        
        return results
    
    def extract_parameters_from_string(self, param_string: str) -> Dict[str, Any]:
        """Extract generation parameters from string."""
        return self._parse_parameters_string(param_string)
    
    def create_wildcard_file(self, wildcard_name: str, suggestions: List[str], wildcard_dir: str) -> str:
        """Create wildcard file from suggestions."""
        import os
        
        # Create wildcard directory if it doesn't exist
        os.makedirs(wildcard_dir, exist_ok=True)
        
        # Create file path
        file_path = os.path.join(wildcard_dir, f"{wildcard_name.lower()}.txt")
        
        # Write suggestions to file
        with open(file_path, 'w') as f:
            f.write('\n'.join(suggestions))
        
        return file_path 