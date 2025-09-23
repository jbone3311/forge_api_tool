#!/usr/bin/env python3
"""
Mock Forge API Client - Uses the same interface as ForgeAPIClient but with mock backends.
"""

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
from .mock_api_provider import get_mock_provider, initialize_mock_provider, switch_mock_provider


class MockForgeAPIClient:
    """Mock client that uses the same interface as ForgeAPIClient but with simulated backends."""
    
    def __init__(self, base_url: str = None, timeout: int = None, use_mock: bool = True):
        # Use central API config if not provided
        if base_url is None:
            base_url = api_config.base_url
        if timeout is None:
            timeout = api_config.timeout
            
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.use_mock = use_mock
        
        # Initialize mock provider
        if self.use_mock:
            self.mock_provider = initialize_mock_provider()
        else:
            self.mock_provider = None
        
        logger.log_app_event("mock_forge_api_client_initialized", {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_type": api_config.api_type,
            "use_mock": self.use_mock,
            "mock_provider": self.mock_provider.name if self.mock_provider else None
        })
    
    def switch_api_provider(self, api_type: str):
        """Switch to a different mock API provider."""
        if self.use_mock and self.mock_provider:
            self.mock_provider = switch_mock_provider(api_type)
            logger.info(f"Switched to mock provider: {self.mock_provider.name}")
        else:
            logger.warning("Cannot switch providers when not using mock mode")
    
    def test_connection(self) -> bool:
        """Test if API is accessible."""
        if not self.use_mock:
            # Fall back to real API testing
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    logger.log_api_request("/sdapi/v1/progress", "GET", response.status_code, response_time)
                    return True
                else:
                    logger.log_api_error("/sdapi/v1/progress", "GET", f"Status {response.status_code}", response_time)
                    return False
            except requests.exceptions.ConnectionError as e:
                response_time = time.time() - start_time
                logger.log_api_error("/sdapi/v1/progress", "GET", str(e), response_time)
                return False
        
        # Use mock provider
        return self.mock_provider.test_connection()
    
    def generate_image(self, config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate an image using mock or real API."""
        if not self.use_mock:
            # Fall back to real API (this would need the original ForgeAPIClient logic)
            raise NotImplementedError("Real API generation not implemented in mock client")
        
        try:
            # Validate config
            self.validate_config(config)
            
            # Use mock provider
            success, image_data, metadata = self.mock_provider.generate_image(config)
            
            if success:
                logger.log_app_event("mock_image_generated", {
                    "provider": self.mock_provider.name,
                    "prompt_length": len(config.get('prompt', '')),
                    "steps": config.get('steps', 20),
                    "size": f"{config.get('width', 512)}x{config.get('height', 512)}"
                })
                return True, image_data, metadata
            else:
                raise GenerationError("Mock generation failed")
                
        except Exception as e:
            logger.error(f"Mock generation error: {e}")
            raise GenerationError(f"Mock generation failed: {e}")
    
    def generate_batch(self, config: Dict[str, Any], count: int = 1) -> List[Tuple[bool, str, Dict[str, Any]]]:
        """Generate multiple images in batch."""
        results = []
        
        for i in range(count):
            try:
                # Create a copy of config for each image
                batch_config = config.copy()
                
                # Vary seed for each image if not specified
                if batch_config.get('seed', -1) == -1:
                    batch_config['seed'] = batch_config.get('seed', -1) + i
                
                success, image_data, metadata = self.generate_image(batch_config)
                results.append((success, image_data, metadata))
                
            except Exception as e:
                logger.error(f"Batch generation item {i+1} failed: {e}")
                results.append((False, "", {}))
        
        logger.log_app_event("mock_batch_generated", {
            "provider": self.mock_provider.name if self.mock_provider else "unknown",
            "count": count,
            "successful": sum(1 for success, _, _ in results if success)
        })
        
        return results
    
    def save_image(self, image_data: str, output_path: str) -> bool:
        """Save base64 image data to file."""
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            
            # Create output directory if it doesn't exist
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save image
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            
            logger.log_app_event("mock_image_saved", {
                "output_path": output_path,
                "file_size": len(image_bytes)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save mock image: {e}")
            raise FileOperationError(f"Failed to save image: {e}")
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.get(f"{self.base_url}/sdapi/v1/sd-models", timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise APIError(f"Failed to get models: {response.status_code}")
            except Exception as e:
                raise APIError(f"Error getting models: {e}")
        
        # Use mock provider
        return self.mock_provider.get_models()
    
    def get_samplers(self) -> List[Dict[str, Any]]:
        """Get available samplers."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.get(f"{self.base_url}/sdapi/v1/samplers", timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise APIError(f"Failed to get samplers: {response.status_code}")
            except Exception as e:
                raise APIError(f"Error getting samplers: {e}")
        
        # Use mock provider
        return self.mock_provider.get_samplers()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current generation progress."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise APIError(f"Failed to get progress: {response.status_code}")
            except Exception as e:
                raise APIError(f"Error getting progress: {e}")
        
        # Use mock provider
        return self.mock_provider.get_progress()
    
    def interrupt_generation(self) -> bool:
        """Interrupt current generation."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.post(f"{self.base_url}/sdapi/v1/interrupt", timeout=self.timeout)
                return response.status_code == 200
            except Exception as e:
                raise APIError(f"Error interrupting generation: {e}")
        
        # Use mock provider
        return self.mock_provider.interrupt_generation()
    
    def skip_generation(self) -> bool:
        """Skip current generation."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.post(f"{self.base_url}/sdapi/v1/skip", timeout=self.timeout)
                return response.status_code == 200
            except Exception as e:
                raise APIError(f"Error skipping generation: {e}")
        
        # Use mock provider
        return self.mock_provider.skip_generation()
    
    def get_options(self) -> Dict[str, Any]:
        """Get current options."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.get(f"{self.base_url}/sdapi/v1/options", timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise APIError(f"Failed to get options: {response.status_code}")
            except Exception as e:
                raise APIError(f"Error getting options: {e}")
        
        # Use mock provider
        return self.mock_provider.get_options()
    
    def set_options(self, options: Dict[str, Any]) -> bool:
        """Set options."""
        if not self.use_mock:
            # Fall back to real API
            try:
                response = self.session.post(f"{self.base_url}/sdapi/v1/options", 
                                           json=options, timeout=self.timeout)
                return response.status_code == 200
            except Exception as e:
                raise APIError(f"Error setting options: {e}")
        
        # Use mock provider
        return self.mock_provider.set_options(options)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration parameters."""
        required_fields = ['prompt']
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValidationError(f"Required field '{field}' is missing or empty")
        
        # Validate numeric ranges
        if 'steps' in config and (config['steps'] < 1 or config['steps'] > 150):
            raise ValidationError("Steps must be between 1 and 150")
        
        if 'cfg_scale' in config and (config['cfg_scale'] < 1.0 or config['cfg_scale'] > 30.0):
            raise ValidationError("CFG Scale must be between 1.0 and 30.0")
        
        if 'width' in config and (config['width'] < 64 or config['width'] > 2048):
            raise ValidationError("Width must be between 64 and 2048")
        
        if 'height' in config and (config['height'] < 64 or config['height'] > 2048):
            raise ValidationError("Height must be between 64 and 2048")
        
        return True
    
    def _prepare_payload(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the payload for API request."""
        # Extract model settings
        model_settings = config.get('model_settings', {})
        prompt_settings = config.get('prompt_settings', {})
        generation_settings = config.get('generation_settings', {})
        
        # Build the payload
        payload = {
            "prompt": prompt_settings.get('base_prompt', ''),
            "negative_prompt": prompt_settings.get('negative_prompt', ''),
            "steps": generation_settings.get('steps', 20),
            "cfg_scale": generation_settings.get('cfg_scale', 7.0),
            "width": generation_settings.get('width', 512),
            "height": generation_settings.get('height', 512),
            "seed": generation_settings.get('seed', -1),
            "sampler_name": generation_settings.get('sampler_name', 'Euler a'),
            "batch_size": generation_settings.get('batch_size', 1),
            "batch_count": generation_settings.get('batch_count', 1),
            "override_settings": {
                "sd_model_checkpoint": model_settings.get('checkpoint', 'sd-v1-5'),
                "sd_vae": model_settings.get('vae', 'Automatic')
            }
        }
        
        return payload
    
    @property
    def server_url(self) -> str:
        """Get the current server URL."""
        return self.base_url
    
    @server_url.setter
    def server_url(self, url: str):
        """Set the server URL and update the base_url."""
        old_url = self.base_url
        self.base_url = url.rstrip('/')
        logger.log_app_event("mock_api_url_changed", {
            "old_url": old_url,
            "new_url": self.base_url
        })
    
    def refresh_configuration(self):
        """Refresh the client configuration when API settings change."""
        # Update base URL
        self.base_url = api_config.base_url.rstrip('/')
        
        # Re-initialize mock provider if needed
        if self.use_mock:
            self.mock_provider = initialize_mock_provider()
        
        logger.log_app_event("mock_api_client_configuration_refreshed", {
            "base_url": self.base_url,
            "api_type": api_config.api_type
        })


# Factory function to create the appropriate client
def create_forge_client(use_mock: bool = True, api_type: str = None) -> MockForgeAPIClient:
    """Create a Forge API client (mock or real)."""
    if api_type:
        # Update the global API config
        api_config.api_type = api_type
    
    return MockForgeAPIClient(use_mock=use_mock)


# Convenience function to get available mock providers
def get_available_providers() -> List[str]:
    """Get list of available mock providers."""
    from .mock_api_provider import MockAPIProviderFactory
    return MockAPIProviderFactory.get_available_providers()
