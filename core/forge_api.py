import requests
import json
import time
import base64
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io


class ForgeAPIClient:
    """Client for communicating with Forge's API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:7860", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def test_connection(self) -> bool:
        """Test if Forge API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/sd-models", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def get_samplers(self) -> List[Dict[str, Any]]:
        """Get available samplers."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/samplers", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get samplers: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting samplers: {e}")
            return []
    
    def generate_image(self, config: Dict[str, Any], prompt: str, seed: Optional[int] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a single image using the provided configuration."""
        try:
            # Prepare the API payload
            payload = self._prepare_payload(config, prompt, seed)
            
            # Send request to Forge API
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result.get('images', [None])[0], result.get('info', {})
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                return False, "", {'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error generating image: {e}"
            return False, "", {'error': error_msg}
    
    def generate_batch(self, config: Dict[str, Any], prompts: List[str], seeds: Optional[List[int]] = None) -> List[Tuple[bool, str, Dict[str, Any]]]:
        """Generate multiple images in a batch."""
        results = []
        
        for i, prompt in enumerate(prompts):
            seed = seeds[i] if seeds and i < len(seeds) else None
            success, image_data, info = self.generate_image(config, prompt, seed)
            results.append((success, image_data, info))
            
            # Add small delay between requests to avoid overwhelming the API
            if i < len(prompts) - 1:
                time.sleep(0.1)
        
        return results
    
    def _prepare_payload(self, config: Dict[str, Any], prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
        """Prepare the API payload from configuration."""
        gen_settings = config['generation_settings']
        model_settings = config['model_settings']
        
        # Base payload
        payload = {
            'prompt': prompt,
            'negative_prompt': config['prompt_settings']['negative_prompt'],
            'steps': gen_settings['steps'],
            'width': gen_settings['width'],
            'height': gen_settings['height'],
            'batch_size': gen_settings['batch_size'],
            'sampler_name': gen_settings['sampler'],
            'cfg_scale': gen_settings['cfg_scale'],
            'restore_faces': False,
            'tiling': False,
            'enable_hr': False,
            'denoising_strength': 0.7,
            'firstphase_width': 0,
            'firstphase_height': 0,
            'hr_scale': 2.0,
            'hr_upscaler': 'Latent',
            'hr_second_pass_steps': 20,
            'hr_resize_x': 0,
            'hr_resize_y': 0,
            'subseed': -1,
            'subseed_strength': 0,
            'seed_resize_from_h': -1,
            'seed_resize_from_w': -1,
            'seed_enable_extras': True,
            'seed': seed if seed is not None else -1,
            'sampler_index': gen_settings['sampler'],
            'script_name': None,
            'script_args': [],
            'send_images': True,
            'save_images': False,
            'alwayson_scripts': config.get('alwayson_scripts', {})
        }
        
        # Model-specific settings
        if config['model_type'] == 'flux':
            # Flux-specific settings
            if gen_settings.get('distilled_cfg_scale'):
                payload['distilled_cfg_scale'] = gen_settings['distilled_cfg_scale']
            
            # Remove cfg_scale for Flux if not needed
            if gen_settings.get('cfg_scale') is None:
                payload.pop('cfg_scale', None)
        
        # Add ControlNet if specified
        if config.get('controlnet'):
            payload['alwayson_scripts']['ControlNet'] = {
                'args': config['controlnet']
            }
        
        # Add override settings for model loading
        override_settings = {}
        
        if model_settings.get('checkpoint'):
            override_settings['sd_model_checkpoint'] = model_settings['checkpoint']
        
        if model_settings.get('vae'):
            override_settings['sd_vae'] = model_settings['vae']
        
        if model_settings.get('text_encoder'):
            override_settings['sd_text_encoder'] = model_settings['text_encoder']
        
        if model_settings.get('gpu_weight'):
            override_settings['gpu_weight'] = model_settings['gpu_weight']
        
        if model_settings.get('swap_method'):
            override_settings['swap_method'] = model_settings['swap_method']
        
        if model_settings.get('swap_location'):
            override_settings['swap_location'] = model_settings['swap_location']
        
        if override_settings:
            payload['override_settings'] = override_settings
        
        return payload
    
    def save_image(self, image_data: str, output_path: str, metadata: Dict[str, Any] = None):
        """Save image data to file with optional metadata."""
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Save image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            # Save metadata if provided
            if metadata:
                metadata_path = output_path.replace('.png', '.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current generation progress."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"Error getting progress: {e}")
            return {}
    
    def interrupt_generation(self) -> bool:
        """Interrupt current generation."""
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/interrupt", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error interrupting generation: {e}")
            return False
    
    def skip_generation(self) -> bool:
        """Skip current generation."""
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/skip", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error skipping generation: {e}")
            return False
    
    def get_options(self) -> Dict[str, Any]:
        """Get current Forge options."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/options", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"Error getting options: {e}")
            return {}
    
    def set_options(self, options: Dict[str, Any]) -> bool:
        """Set Forge options."""
        try:
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/options",
                json=options,
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting options: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against available API options."""
        errors = []
        
        # Check if API is accessible
        if not self.test_connection():
            errors.append("Cannot connect to Forge API")
            return False, errors
        
        # Get available models and samplers
        models = self.get_models()
        samplers = self.get_samplers()
        
        # Validate model
        if models:
            model_names = [model['title'] for model in models]
            config_model = config['model_settings']['checkpoint']
            if config_model not in model_names:
                errors.append(f"Model '{config_model}' not found in available models")
        
        # Validate sampler
        if samplers:
            sampler_names = [sampler['name'] for sampler in samplers]
            config_sampler = config['generation_settings']['sampler']
            if config_sampler not in sampler_names:
                errors.append(f"Sampler '{config_sampler}' not found in available samplers")
        
        # Validate generation settings
        gen_settings = config['generation_settings']
        if gen_settings['steps'] < 1 or gen_settings['steps'] > 100:
            errors.append("Steps must be between 1 and 100")
        
        if gen_settings['width'] < 64 or gen_settings['height'] < 64:
            errors.append("Width and height must be at least 64")
        
        if gen_settings['width'] > 2048 or gen_settings['height'] > 2048:
            errors.append("Width and height must be at most 2048")
        
        return len(errors) == 0, errors 