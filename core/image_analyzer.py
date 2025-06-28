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
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Extract basic image info
            result = {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'success': True
            }
            
            # Try to extract metadata
            metadata = self._extract_metadata_from_image(image)
            if metadata:
                result['metadata'] = metadata
                
                # Extract parameters from metadata
                params = self._extract_parameters(metadata)
                if params:
                    result['parameters'] = params
                
                # Extract prompt information
                prompt_info = self._extract_prompt_info(metadata)
                if prompt_info:
                    result['prompt_info'] = prompt_info
                    result['prompt'] = prompt_info.get('prompt', '')
                    result['negative_prompt'] = prompt_info.get('negative_prompt', '')
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_metadata_from_image(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """Extract metadata from image."""
        try:
            metadata = {}
            
            # Try to get EXIF data
            try:
                exif = image.getexif()
                if exif:
                    metadata.update(dict(exif))
            except Exception:
                pass
            
            # Try to get PNG-specific metadata
            if hasattr(image, 'info') and image.info:
                metadata.update(image.info)
            
            # Try to get PNG text chunks (common in AI-generated images)
            if hasattr(image, 'text') and image.text:
                metadata.update(image.text)
            
            # Try to get PNG metadata chunks
            if hasattr(image, '_getexif') and image._getexif:
                png_metadata = image._getexif()
                if png_metadata:
                    metadata.update(png_metadata)
            
            # Look for specific PNG chunks that might contain generation data
            if hasattr(image, 'info') and image.info:
                # Check for common PNG text chunks used by AI generators
                text_chunks = ['parameters', 'prompt', 'negative_prompt', 'generation_data', 
                              'comfyui_workflow', 'automatic1111_metadata', 'generation_settings']
                
                for chunk in text_chunks:
                    if chunk in image.info:
                        metadata[chunk] = image.info[chunk]
            
            return metadata if metadata else None
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None
    
    def _extract_parameters(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generation parameters from metadata."""
        params = {}
        
        # Look for common parameter keys
        parameter_keys = ['parameters', 'prompt', 'negative_prompt', 'steps', 'cfg_scale', 
                         'sampler', 'seed', 'width', 'height', 'model', 'vae', 'denoising_strength',
                         'clip_skip', 'restore_faces', 'tiling', 'hires_fix', 'hires_steps',
                         'hires_upscaler', 'hires_denoising', 'subseed', 'subseed_strength',
                         'text_encoder', 'model_hash', 'vae_hash', 'lora', 'embedding']
        
        for key in parameter_keys:
            if key in metadata:
                params[key] = metadata[key]
        
        # Try to parse parameters string if present
        if 'parameters' in metadata:
            parsed_params = self._parse_parameters_string(metadata['parameters'])
            params.update(parsed_params)
        
        # Try to parse generation_data if present
        if 'generation_data' in metadata:
            try:
                gen_data = json.loads(metadata['generation_data'])
                if isinstance(gen_data, dict):
                    params.update(gen_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Try to parse automatic1111_metadata if present
        if 'automatic1111_metadata' in metadata:
            try:
                a1111_data = json.loads(metadata['automatic1111_metadata'])
                if isinstance(a1111_data, dict):
                    params.update(a1111_data)
            except (json.JSONDecodeError, TypeError):
                pass
        
        # If we have individual prompt fields, use them (but don't override parsed ones)
        if 'prompt' in metadata and not params.get('prompt'):
            params['prompt'] = metadata['prompt']
        if 'negative_prompt' in metadata and not params.get('negative_prompt'):
            params['negative_prompt'] = metadata['negative_prompt']
        
        return params
    
    def _parse_parameters_string(self, param_string: str) -> Dict[str, Any]:
        """Parse parameters string to extract individual values."""
        params = {}
        
        # Extract prompt (up to ', Steps:' or ', Negative prompt:' or end)
        prompt_match = re.search(r'^(.*?)(?:,\s*Steps:|,\s*Negative prompt:|$)', param_string)
        if prompt_match:
            params['prompt'] = prompt_match.group(1).strip()
        
        # Extract negative prompt
        neg_prompt_match = re.search(r'Negative prompt: ([^,]+?)(?:,|$)', param_string)
        if neg_prompt_match:
            params['negative_prompt'] = neg_prompt_match.group(1).strip()
        
        # Extract other parameters with enhanced patterns
        param_patterns = {
            'steps': r'Steps: (\d+)',
            'cfg_scale': r'CFG scale: ([\d.]+)',
            'sampler': r'Sampler: ([^,]+)',
            'seed': r'Seed: (\d+)',
            'width': r'Size: (\d+)x(\d+)',
            'model': r'Model: ([^,]+)',
            'vae': r'VAE: ([^,]+)',
            'denoising_strength': r'Denoising strength: ([\d.]+)',
            'clip_skip': r'Clip skip: (\d+)',
            'restore_faces': r'Restore faces: ([^,]+)',
            'tiling': r'Tiling: ([^,]+)',
            'hires_fix': r'Hires fix: ([^,]+)',
            'hires_steps': r'Hires steps: (\d+)',
            'hires_upscaler': r'Hires upscaler: ([^,]+)',
            'hires_denoising': r'Hires denoising: ([\d.]+)',
            'subseed': r'Subseed: (\d+)',
            'subseed_strength': r'Subseed strength: ([\d.]+)',
            'text_encoder': r'Text encoder: ([^,]+)',
            'model_hash': r'Model hash: ([a-f0-9]+)',
            'vae_hash': r'VAE hash: ([a-f0-9]+)',
            'lora': r'LoRA: ([^,]+)',
            'embedding': r'Embedding: ([^,]+)'
        }
        
        for param_name, pattern in param_patterns.items():
            match = re.search(pattern, param_string)
            if match:
                if param_name == 'width':
                    params['width'] = int(match.group(1))
                    params['height'] = int(match.group(2))
                elif param_name in ['steps', 'clip_skip', 'hires_steps', 'subseed']:
                    params[param_name] = int(match.group(1))
                elif param_name in ['cfg_scale', 'denoising_strength', 'hires_denoising', 'subseed_strength']:
                    params[param_name] = float(match.group(1))
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
        
        # Extract prompt - prioritize individual prompt field over parameters string
        if 'prompt' in metadata:
            prompt_info['prompt'] = metadata['prompt']
        elif 'parameters' in metadata:
            # Try to extract prompt from parameters
            prompt_match = re.search(r'^([^,]+?)(?:,|$)', metadata['parameters'])
            if prompt_match:
                prompt_info['prompt'] = prompt_match.group(1).strip()
        
        # Extract negative prompt - prioritize individual negative_prompt field
        if 'negative_prompt' in metadata:
            prompt_info['negative_prompt'] = metadata['negative_prompt']
        elif 'parameters' in metadata:
            # Try to extract negative prompt from parameters
            neg_prompt_match = re.search(r'Negative prompt: ([^,]+?)(?:,|$)', metadata['parameters'])
            if neg_prompt_match:
                prompt_info['negative_prompt'] = neg_prompt_match.group(1).strip()
        
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
                'negative_prompt': prompt_info.get('negative_prompt', '')
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
                'dir': 'outputs/extracted_config/{timestamp}/',
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            },
            'controlnet': [],
            'alwayson_scripts': {
                'Lora': []
            },
            'forge_api': {
                'base_url': 'http://127.0.0.1:7860',
                'timeout': 300,
                'retry_attempts': 3
            }
        }
        
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
                'checkpoint': '',
                'vae': '',
                'text_encoder': '',
                'gpu_weight': 1.0,
                'swap_method': 'weight',
                'swap_location': 'cpu'
            },
            'generation_settings': {
                'sampler': 'DPM++ 2M Karras',
                'scheduler': 'Simple',
                'steps': int(analysis_result.get('steps', 20)),
                'cfg_scale': float(analysis_result.get('cfg_scale', 7.0)),
                'distilled_cfg_scale': None,
                'width': int(analysis_result.get('width', 512)),
                'height': int(analysis_result.get('height', 512)),
                'batch_size': 1,
                'num_batches': 10,
                'seed': 'random'
            },
            'prompt_settings': {
                'base_prompt': analysis_result.get('prompt', ''),
                'negative_prompt': analysis_result.get('negative_prompt', '')
            },
            'output_settings': {
                'dir': f'outputs/{config_name.lower().replace(" ", "_")}/{{timestamp}}/',
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            },
            'controlnet': [],
            'alwayson_scripts': {
                'Lora': []
            },
            'forge_api': {
                'base_url': 'http://127.0.0.1:7860',
                'timeout': 300,
                'retry_attempts': 3
            }
        }
        
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
    
    def analyze_multiple_images(self, image_data_list: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple images for batch processing."""
        results = []
        
        for image_data in image_data_list:
            try:
                # Analyze each image using the existing method
                result = self.analyze_image(image_data)
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e)
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
    
    def error_handling(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Handle errors during image analysis."""
        return {
            'success': False,
            'error_type': error_type,
            'error_message': error_message
        } 