import requests
import json
import time
import base64
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import io
from PIL import PngImagePlugin
from .centralized_logger import logger
from .api_config import api_config
from .exceptions import ConnectionError, APIError, GenerationError, FileOperationError, ValidationError


class ForgeAPIClient:
    """Client for communicating with Forge's API or RunDiffusion API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        # Use central API config if not provided
        if base_url is None:
            base_url = api_config.base_url
        if timeout is None:
            timeout = api_config.timeout
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set up authentication for RunDiffusion if needed
        self._setup_authentication()
        
        logger.log_app_event("forge_api_client_initialized", {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_type": api_config.api_type
        })
    
    def _setup_authentication(self):
        """Set up authentication based on API type."""
        if api_config.api_type == "rundiffusion" and api_config.rundiffusion_config:
            from requests.auth import HTTPBasicAuth
            username = api_config.rundiffusion_config.get('username', 'rduser')
            password = api_config.rundiffusion_config.get('password', 'rdpass')
            self.session.auth = HTTPBasicAuth(username, password)
            logger.log_app_event("rundiffusion_auth_configured", {
                "username": username,
                "url": self.base_url
            })
        else:
            # Clear any existing authentication for local API
            self.session.auth = None
    
    def refresh_configuration(self):
        """Refresh the client configuration when API settings change."""
        # Update base URL
        self.base_url = api_config.base_url.rstrip('/')
        
        # Re-setup authentication
        self._setup_authentication()
        
        logger.log_app_event("api_client_configuration_refreshed", {
            "base_url": self.base_url,
            "api_type": api_config.api_type
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
        logger.log_app_event("forge_api_url_changed", {
            "old_url": old_url,
            "new_url": self.base_url
        })
    
    def test_connection(self) -> bool:
        """Test if API is accessible."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                logger.log_api_request("/sdapi/v1/progress", "GET", response.status_code, response_time)
                logger.log_app_event("api_connection_test_success", {
                    "response_time": response_time,
                    "api_type": api_config.api_type
                })
                return True
            else:
                logger.log_api_error("/sdapi/v1/progress", "GET", f"Status {response.status_code}", response_time)
                return False
        except requests.exceptions.ConnectionError as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            logger.log_error(f"Connection test failed: {e}")
            raise ConnectionError(f"Unable to connect to {self.base_url}", url=self.base_url, timeout=10) from e
        except requests.exceptions.Timeout as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            logger.log_error(f"Connection test timeout: {e}")
            raise ConnectionError(f"Connection timeout to {self.base_url}", url=self.base_url, timeout=10) from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            logger.log_error(f"Connection test failed: {e}")
            raise ConnectionError(f"Unexpected error connecting to {self.base_url}: {e}", url=self.base_url) from e
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/sd-models", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json()
                logger.log_api_request("/sdapi/v1/sd-models", "GET", response.status_code, response_time)
                logger.log_app_event("models_retrieved", {
                    "count": len(models),
                    "response_time": response_time
                })
                return models
            else:
                logger.log_api_error("/sdapi/v1/sd-models", "GET", f"Status {response.status_code}", response_time)
                logger.log_error(f"Failed to get models: {response.status_code}")
                raise APIError(f"Failed to get models: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/sd-models")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/sd-models", "GET", str(e), response_time)
            logger.log_error(f"Error getting models: {e}")
            raise APIError(f"Request failed getting models: {e}", endpoint="/sdapi/v1/sd-models") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/sd-models", "GET", str(e), response_time)
            logger.log_error(f"Error getting models: {e}")
            raise APIError(f"Unexpected error getting models: {e}", endpoint="/sdapi/v1/sd-models") from e
    
    def get_samplers(self) -> List[Dict[str, Any]]:
        """Get available samplers."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/samplers", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                samplers = response.json()
                logger.log_api_request("/sdapi/v1/samplers", "GET", response.status_code, response_time)
                logger.log_app_event("samplers_retrieved", {
                    "count": len(samplers),
                    "response_time": response_time
                })
                return samplers
            else:
                logger.log_api_error("/sdapi/v1/samplers", "GET", f"Status {response.status_code}", response_time)
                logger.log_error(f"Failed to get samplers: {response.status_code}")
                raise APIError(f"Failed to get samplers: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/samplers")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/samplers", "GET", str(e), response_time)
            logger.log_error(f"Error getting samplers: {e}")
            raise APIError(f"Request failed getting samplers: {e}", endpoint="/sdapi/v1/samplers") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/samplers", "GET", str(e), response_time)
            logger.log_error(f"Error getting samplers: {e}")
            raise APIError(f"Unexpected error getting samplers: {e}", endpoint="/sdapi/v1/samplers") from e
    
    def generate_image(self, config: Dict[str, Any], prompt: str, seed: Optional[int] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a single image using the provided configuration."""
        start_time = time.time()
        try:
            # Prepare the API payload
            payload = self._prepare_payload(config, prompt, seed)
            
            logger.log_app_event("image_generation_started", {
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
                
                logger.log_api_request("/sdapi/v1/txt2img", "POST", response.status_code, response_time)
                logger.log_performance("image_generation", response_time, {
                    "config_name": config.get('name', 'unknown'),
                    "prompt_length": len(prompt),
                    "seed": seed,
                    "success": True
                })
                
                if image_data:
                    logger.log_image_generation(
                        config.get('name', 'unknown'),
                        prompt,
                        seed or -1,
                        True
                    )
                
                return True, image_data, info
            else:
                logger.log_api_error("/sdapi/v1/txt2img", "POST", f"Status {response.status_code}: {response.text}", response_time)
                logger.log_performance("image_generation", response_time, {
                    "config_name": config.get('name', 'unknown'),
                    "prompt_length": len(prompt),
                    "seed": seed,
                    "success": False,
                    "error": f"Status {response.status_code}"
                })
                
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.log_error(error_msg)
                raise GenerationError(error_msg, config_name=config.get('name'), prompt=prompt)
                
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/txt2img", "POST", str(e), response_time)
            logger.log_performance("image_generation", response_time, {
                "config_name": config.get('name', 'unknown'),
                "prompt_length": len(prompt),
                "seed": seed,
                "success": False,
                "error": str(e)
            })
            
            error_msg = f"Request failed generating image: {e}"
            logger.log_error(error_msg)
            raise GenerationError(error_msg, config_name=config.get('name'), prompt=prompt) from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/txt2img", "POST", str(e), response_time)
            logger.log_performance("image_generation", response_time, {
                "config_name": config.get('name', 'unknown'),
                "prompt_length": len(prompt),
                "seed": seed,
                "success": False,
                "error": str(e)
            })
            
            error_msg = f"Unexpected error generating image: {e}"
            logger.log_error(error_msg)
            raise GenerationError(error_msg, config_name=config.get('name'), prompt=prompt) from e
    
    def generate_batch(self, config: Dict[str, Any], prompts: List[str], seeds: Optional[List[int]] = None) -> List[Tuple[bool, str, Dict[str, Any]]]:
        """Generate multiple images in a batch."""
        start_time = time.time()
        logger.log_app_event("batch_generation_started", {
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
        
        logger.log_performance("batch_generation", batch_time, {
            "config_name": config.get('name', 'unknown'),
            "total_images": len(prompts),
            "successful_images": successful_count,
            "success_rate": successful_count / len(prompts) if prompts else 0
        })
        
        logger.log_app_event("batch_generation_completed", {
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
        
        logger.log_app_event("payload_prepared", {
            "config_name": config.get('name', 'unknown'),
            "payload_keys": list(payload.keys()),
            "model_type": config['model_type']
        })
        
        return payload
    
    def save_image(self, image_data: str, output_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save image data to file with embedded metadata like Automatic1111."""
        start_time = time.time()
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Embed metadata in PNG if provided
            if metadata:
                # Convert metadata to PNG info format
                pnginfo = PngImagePlugin.PngInfo()
                
                # Add all metadata as text chunks
                for key, value in metadata.items():
                    if isinstance(value, (dict, list)):
                        # Convert complex objects to JSON strings
                        pnginfo.add_text(key, json.dumps(value, ensure_ascii=False))
                    else:
                        # Convert simple values to strings
                        pnginfo.add_text(key, str(value))
                
                # Save image with embedded metadata
                image.save(output_path, 'PNG', pnginfo=pnginfo)
            else:
                # Save image without metadata
                image.save(output_path, 'PNG')
            
            save_time = time.time() - start_time
            logger.log_performance("image_save", save_time, {
                "output_path": output_path,
                "image_size_bytes": len(image_bytes),
                "metadata_embedded": metadata is not None
            })
            
            logger.log_app_event("image_saved", {
                "output_path": output_path,
                "save_time": save_time,
                "metadata_embedded": metadata is not None
            })
            
            return True
        except (IOError, OSError) as e:
            save_time = time.time() - start_time
            logger.log_error(f"File system error saving image: {e}", {
                "output_path": output_path,
                "save_time": save_time
            })
            raise FileOperationError(f"Failed to save image: {e}", file_path=output_path, operation="write") from e
        except Exception as e:
            save_time = time.time() - start_time
            logger.log_error(f"Unexpected error saving image: {e}", {
                "output_path": output_path,
                "save_time": save_time
            })
            raise FileOperationError(f"Unexpected error saving image: {e}", file_path=output_path, operation="write") from e
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current generation progress."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                progress_data = response.json()
                logger.log_api_request("/sdapi/v1/progress", "GET", response.status_code, response_time)
                return progress_data
            else:
                logger.log_api_error("/sdapi/v1/progress", "GET", f"Status {response.status_code}", response_time)
                raise APIError(f"Failed to get progress: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/progress")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            logger.log_error(f"Request error getting progress: {e}")
            raise APIError(f"Request failed getting progress: {e}", endpoint="/sdapi/v1/progress") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
            logger.log_error(f"Unexpected error getting progress: {e}")
            raise APIError(f"Unexpected error getting progress: {e}", endpoint="/sdapi/v1/progress") from e
    
    def interrupt_generation(self) -> bool:
        """Interrupt current generation."""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/interrupt", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                logger.log_api_request("/sdapi/v1/interrupt", "POST", response.status_code, response_time)
                logger.log_app_event("generation_interrupted", {"response_time": response_time})
                return True
            else:
                logger.log_api_error("/sdapi/v1/interrupt", "POST", f"Status {response.status_code}", response_time)
                raise APIError(f"Failed to interrupt generation: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/interrupt")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/interrupt", "POST", str(e), response_time)
            logger.log_error(f"Request error interrupting generation: {e}")
            raise APIError(f"Request failed interrupting generation: {e}", endpoint="/sdapi/v1/interrupt") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/interrupt", "POST", str(e), response_time)
            logger.log_error(f"Unexpected error interrupting generation: {e}")
            raise APIError(f"Unexpected error interrupting generation: {e}", endpoint="/sdapi/v1/interrupt") from e
    
    def skip_generation(self) -> bool:
        """Skip current generation."""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/skip", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                logger.log_api_request("/sdapi/v1/skip", "POST", response.status_code, response_time)
                logger.log_app_event("generation_skipped", {"response_time": response_time})
                return True
            else:
                logger.log_api_error("/sdapi/v1/skip", "POST", f"Status {response.status_code}", response_time)
                raise APIError(f"Failed to skip generation: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/skip")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/skip", "POST", str(e), response_time)
            logger.log_error(f"Request error skipping generation: {e}")
            raise APIError(f"Request failed skipping generation: {e}", endpoint="/sdapi/v1/skip") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/skip", "POST", str(e), response_time)
            logger.log_error(f"Unexpected error skipping generation: {e}")
            raise APIError(f"Unexpected error skipping generation: {e}", endpoint="/sdapi/v1/skip") from e
    
    def get_options(self) -> Dict[str, Any]:
        """Get current options."""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/options", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                options = response.json()
                logger.log_api_request("/sdapi/v1/options", "GET", response.status_code, response_time)
                logger.log_app_event("options_retrieved", {
                    "option_count": len(options),
                    "response_time": response_time
                })
                return options
            else:
                logger.log_api_error("/sdapi/v1/options", "GET", f"Status {response.status_code}", response_time)
                raise APIError(f"Failed to get options: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/options")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/options", "GET", str(e), response_time)
            logger.log_error(f"Request error getting options: {e}")
            raise APIError(f"Request failed getting options: {e}", endpoint="/sdapi/v1/options") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/options", "GET", str(e), response_time)
            logger.log_error(f"Unexpected error getting options: {e}")
            raise APIError(f"Unexpected error getting options: {e}", endpoint="/sdapi/v1/options") from e
    
    def set_options(self, options: Dict[str, Any]) -> bool:
        """Set options."""
        start_time = time.time()
        try:
            response = self.session.post(f"{self.base_url}/sdapi/v1/options", json=options, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                logger.log_api_request("/sdapi/v1/options", "POST", response.status_code, response_time)
                logger.log_app_event("options_updated", {
                    "options_count": len(options),
                    "response_time": response_time
                })
                return True
            else:
                logger.log_api_error("/sdapi/v1/options", "POST", f"Status {response.status_code}", response_time)
                raise APIError(f"Failed to set options: HTTP {response.status_code}", status_code=response.status_code, endpoint="/sdapi/v1/options")
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/options", "POST", str(e), response_time)
            logger.log_error(f"Request error setting options: {e}")
            raise APIError(f"Request failed setting options: {e}", endpoint="/sdapi/v1/options") from e
        except Exception as e:
            response_time = time.time() - start_time
            logger.log_api_error("/sdapi/v1/options", "POST", str(e), response_time)
            logger.log_error(f"Unexpected error setting options: {e}")
            raise APIError(f"Unexpected error setting options: {e}", endpoint="/sdapi/v1/options") from e
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate configuration."""
        errors = []
        
        try:
            # Check required fields
            required_fields = ['name', 'model_type', 'generation_settings', 'prompt_settings']
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
            
            if errors:
                return False, errors
            
            # Validate generation settings
            gen_settings = config['generation_settings']
            required_gen_fields = ['steps', 'sampler', 'width', 'height', 'batch_size']
            for field in required_gen_fields:
                if field not in gen_settings:
                    errors.append(f"Missing generation setting: {field}")
            
            # Validate prompt settings
            prompt_settings = config['prompt_settings']
            if 'base_prompt' not in prompt_settings:
                errors.append("Missing base_prompt in prompt_settings")
            
            if errors:
                return False, errors
            
            return True, []
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors


# Create a global instance for easy importing
forge_api_client = ForgeAPIClient() 