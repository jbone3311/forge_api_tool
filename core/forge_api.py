import requests
import json
import time
import base64
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io
from .centralized_logger import centralized_logger
from .api_config import api_config


class ForgeAPIClient:
    """Client for communicating with Forge's API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        # Use central API config if not provided
        if base_url is None:
            base_url = api_config.base_url
        if timeout is None:
            timeout = api_config.timeout
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        centralized_logger.log_app_event("forge_api_client_initialized", {
            "base_url": self.base_url,
            "timeout": self.timeout
        })
    
    @property
    def server_url(self) -> str:
        """Get the current server URL."""
        return self.base_url
    
    @server_url.setter
    def server_url(self, url: str):
        """Set the server URL and update the base_url."""
        old_url = self.base_url
        self.base_url = url.rstrip('/')
        centralized_logger.log_app_event("forge_api_url_changed", {
            "old_url": old_url,
            "new_url": self.base_url
        })
    
    def test_connection(self) -> bool:
        """Test if Forge API is accessible."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                centralized_logger.log_api_request("/sdapi/v1/progress", "GET", response.status_code, response_time)
                centralized_logger.log_app_event("forge_api_connection_test_success", {
                    "response_time": response_time
                })
                return True
            else:
                centralized_logger.log_api_error("/sdapi/v1/progress", "GET", f"Status {response.status_code}", response_time)
                return False
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            centralized_logger.log_error(f"Connection test failed: {e}")
            return False
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/sd-models", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json()
                centralized_logger.log_api_request("/sdapi/v1/sd-models", "GET", response.status_code, response_time)
                centralized_logger.log_app_event("models_retrieved", {
                    "count": len(models),
                    "response_time": response_time
                })
                return models
            else:
                centralized_logger.log_api_error("/sdapi/v1/sd-models", "GET", f"Status {response.status_code}", response_time)
                centralized_logger.log_error(f"Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/sd-models", "GET", str(e), response_time)
            centralized_logger.log_error(f"Error getting models: {e}")
            return []
    
    def get_samplers(self) -> List[Dict[str, Any]]:
        """Get available samplers."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/samplers", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                samplers = response.json()
                centralized_logger.log_api_request("/sdapi/v1/samplers", "GET", response.status_code, response_time)
                centralized_logger.log_app_event("samplers_retrieved", {
                    "count": len(samplers),
                    "response_time": response_time
                })
                return samplers
            else:
                centralized_logger.log_api_error("/sdapi/v1/samplers", "GET", f"Status {response.status_code}", response_time)
                centralized_logger.log_error(f"Failed to get samplers: {response.status_code}")
                return []
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/samplers", "GET", str(e), response_time)
            centralized_logger.log_error(f"Error getting samplers: {e}")
            return []
    
    def generate_image(self, config: Dict[str, Any], prompt: str, seed: Optional[int] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a single image using the provided configuration."""
        start_time = time.time()
        try:
            # Prepare the API payload
            payload = self._prepare_payload(config, prompt, seed)
            
            centralized_logger.log_app_event("image_generation_started", {
                "config_name": config.get('name', 'unknown'),
                "prompt_length": len(prompt),
                "seed": seed
            })
            
            # Send request to Forge API
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                image_data = result.get('images', [None])[0]
                info = result.get('info', {})
                
                centralized_logger.log_api_request("/sdapi/v1/txt2img", "POST", response.status_code, response_time)
                centralized_logger.log_performance("image_generation", response_time, {
                    "config_name": config.get('name', 'unknown'),
                    "prompt_length": len(prompt),
                    "seed": seed,
                    "success": True
                })
                
                if image_data:
                    centralized_logger.log_image_generation(
                        config.get('name', 'unknown'),
                        prompt,
                        seed or -1,
                        True
                    )
                
                return True, image_data, info
            else:
                centralized_logger.log_api_error("/sdapi/v1/txt2img", "POST", f"Status {response.status_code}: {response.text}", response_time)
                centralized_logger.log_performance("image_generation", response_time, {
                    "config_name": config.get('name', 'unknown'),
                    "prompt_length": len(prompt),
                    "seed": seed,
                    "success": False,
                    "error": f"Status {response.status_code}"
                })
                
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                centralized_logger.log_error(error_msg)
                return False, "", {'error': error_msg}
                
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/txt2img", "POST", str(e), response_time)
            centralized_logger.log_performance("image_generation", response_time, {
                "config_name": config.get('name', 'unknown'),
                "prompt_length": len(prompt),
                "seed": seed,
                "success": False,
                "error": str(e)
            })
            
            error_msg = f"Error generating image: {e}"
            centralized_logger.log_error(error_msg)
            return False, "", {'error': error_msg}
    
    def generate_batch(self, config: Dict[str, Any], prompts: List[str], seeds: Optional[List[int]] = None) -> List[Tuple[bool, str, Dict[str, Any]]]:
        """Generate multiple images in a batch."""
        start_time = time.time()
        centralized_logger.log_app_event("batch_generation_started", {
            "config_name": config.get('name', 'unknown'),
            "batch_size": len(prompts),
            "seeds_provided": seeds is not None
        })
        
        results = []
        
        for i, prompt in enumerate(prompts):
            seed = seeds[i] if seeds and i < len(seeds) else None
            success, image_data, info = self.generate_image(config, prompt, seed)
            results.append((success, image_data, info))
            
            # Add small delay between requests to avoid overwhelming the API
            if i < len(prompts) - 1:
                time.sleep(0.5)
        
        batch_time = time.time() - start_time
        successful_count = sum(1 for success, _, _ in results if success)
        
        centralized_logger.log_performance("batch_generation", batch_time, {
            "config_name": config.get('name', 'unknown'),
            "total_images": len(prompts),
            "successful_images": successful_count,
            "success_rate": successful_count / len(prompts) if prompts else 0
        })
        
        centralized_logger.log_app_event("batch_generation_completed", {
            "config_name": config.get('name', 'unknown'),
            "total_images": len(prompts),
            "successful_images": successful_count,
            "batch_time": batch_time
        })
        
        return results
    
    def _prepare_payload(self, config: Dict[str, Any], prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
        """Prepare the API payload for image generation."""
        gen_settings = config['generation_settings']
        model_settings = config['model_settings']
        
        # Handle seed
        if seed is None:
            seed = -1  # Random seed
        
        # Prepare payload
        payload = {
            "prompt": prompt,
            "negative_prompt": config['prompt_settings']['negative_prompt'],
            "steps": gen_settings['steps'],
            "sampler_name": gen_settings['sampler'],
            "cfg_scale": gen_settings['cfg_scale'],
            "width": gen_settings['width'],
            "height": gen_settings['height'],
            "seed": seed,
            "batch_size": gen_settings['batch_size'],
            "save_images": True,
            "send_images": True
        }
        
        # Add model-specific settings
        if config['model_type'] == 'flux' and gen_settings.get('distilled_cfg_scale'):
            payload['distilled_cfg_scale'] = gen_settings['distilled_cfg_scale']
        
        # Add ControlNet if configured
        if config.get('controlnet'):
            payload['alwayson_scripts'] = {
                'controlnet': {
                    'args': config['controlnet']
                }
            }
        
        # Add LoRA if configured
        if config.get('alwayson_scripts', {}).get('Lora'):
            if 'alwayson_scripts' not in payload:
                payload['alwayson_scripts'] = {}
            payload['alwayson_scripts']['Lora'] = config['alwayson_scripts']['Lora']
        
        centralized_logger.log_app_event("payload_prepared", {
            "config_name": config.get('name', 'unknown'),
            "payload_keys": list(payload.keys()),
            "model_type": config['model_type']
        })
        
        return payload
    
    def save_image(self, image_data: str, output_path: str, metadata: Dict[str, Any] = None):
        """Save image data to file."""
        start_time = time.time()
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
            
            save_time = time.time() - start_time
            centralized_logger.log_performance("image_save", save_time, {
                "output_path": output_path,
                "image_size_bytes": len(image_bytes),
                "metadata_saved": metadata is not None
            })
            
            centralized_logger.log_app_event("image_saved", {
                "output_path": output_path,
                "save_time": save_time
            })
            
            return True
        except Exception as e:
            save_time = time.time() - start_time
            centralized_logger.log_error(f"Error saving image: {e}", {
                "output_path": output_path,
                "save_time": save_time
            })
            return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current generation progress."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                progress_data = response.json()
                centralized_logger.log_api_request("/sdapi/v1/progress", "GET", response.status_code, response_time)
                return progress_data
            else:
                centralized_logger.log_api_error("/sdapi/v1/progress", "GET", f"Status {response.status_code}", response_time)
                return {}
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            centralized_logger.log_error(f"Error getting progress: {e}")
            return {}
    
    def interrupt_generation(self) -> bool:
        """Interrupt current generation."""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/interrupt", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                centralized_logger.log_api_request("/sdapi/v1/interrupt", "POST", response.status_code, response_time)
                centralized_logger.log_app_event("generation_interrupted", {"response_time": response_time})
                return True
            else:
                centralized_logger.log_api_error("/sdapi/v1/interrupt", "POST", f"Status {response.status_code}", response_time)
                return False
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/interrupt", "POST", str(e), response_time)
            centralized_logger.log_error(f"Error interrupting generation: {e}")
            return False
    
    def skip_generation(self) -> bool:
        """Skip current generation."""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/skip", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                centralized_logger.log_api_request("/sdapi/v1/skip", "POST", response.status_code, response_time)
                centralized_logger.log_app_event("generation_skipped", {"response_time": response_time})
                return True
            else:
                centralized_logger.log_api_error("/sdapi/v1/skip", "POST", f"Status {response.status_code}", response_time)
                return False
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/skip", "POST", str(e), response_time)
            centralized_logger.log_error(f"Error skipping generation: {e}")
            return False
    
    def get_options(self) -> Dict[str, Any]:
        """Get current Forge options."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/options", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                options = response.json()
                centralized_logger.log_api_request("/sdapi/v1/options", "GET", response.status_code, response_time)
                centralized_logger.log_app_event("options_retrieved", {
                    "options_count": len(options),
                    "response_time": response_time
                })
                return options
            else:
                centralized_logger.log_api_error("/sdapi/v1/options", "GET", f"Status {response.status_code}", response_time)
                return {}
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/options", "GET", str(e), response_time)
            centralized_logger.log_error(f"Error getting options: {e}")
            return {}
    
    def set_options(self, options: Dict[str, Any]) -> bool:
        """Set Forge options."""
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/options",
                json=options,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                centralized_logger.log_api_request("/sdapi/v1/options", "POST", response.status_code, response_time)
                centralized_logger.log_app_event("options_updated", {
                    "options_count": len(options),
                    "response_time": response_time
                })
                return True
            else:
                centralized_logger.log_api_error("/sdapi/v1/options", "POST", f"Status {response.status_code}", response_time)
                return False
        except Exception as e:
            response_time = time.time() - start_time
            centralized_logger.log_api_error("/sdapi/v1/options", "POST", str(e), response_time)
            centralized_logger.log_error(f"Error setting options: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration against available API options."""
        start_time = time.time()
        errors = []
        
        centralized_logger.log_app_event("config_validation_started", {
            "config_name": config.get('name', 'unknown')
        })
        
        # Check if API is accessible
        if not self.test_connection():
            errors.append("Cannot connect to Forge API")
            centralized_logger.log_error("Config validation failed: Cannot connect to Forge API")
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
        
        validation_time = time.time() - start_time
        is_valid = len(errors) == 0
        
        centralized_logger.log_performance("config_validation", validation_time, {
            "config_name": config.get('name', 'unknown'),
            "is_valid": is_valid,
            "error_count": len(errors)
        })
        
        if is_valid:
            centralized_logger.log_app_event("config_validation_success", {
                "config_name": config.get('name', 'unknown'),
                "validation_time": validation_time
            })
        else:
            centralized_logger.log_app_event("config_validation_failed", {
                "config_name": config.get('name', 'unknown'),
                "errors": errors,
                "validation_time": validation_time
            })
        
        return is_valid, errors


# Create a global instance for easy importing
forge_api_client = ForgeAPIClient() 