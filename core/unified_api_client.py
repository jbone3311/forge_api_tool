#!/usr/bin/env python3
"""
Unified API Client

Implements a unified interface for both real and mock API clients using the strategy pattern.
"""

import requests
import json
import time
import base64
from typing import Dict, Any, List, Optional, Tuple, Protocol
from PIL import Image
import io
from PIL import PngImagePlugin
from abc import ABC, abstractmethod
from core.centralized_logger import logger
from core.api_config import api_config
from core.exceptions import ConnectionError, APIError, GenerationError, FileOperationError, ValidationError


class APIProvider(Protocol):
    """Protocol defining the interface for API providers."""
    
    def test_connection(self, silent: bool = False) -> bool:
        """Test connection to the API provider."""
        ...
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1) -> Dict[str, Any]:
        """Generate a single image."""
        ...
    
    def generate_batch(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1, 
                      batch_size: int = 1) -> List[Dict[str, Any]]:
        """Generate a batch of images."""
        ...


class RealAPIProvider:
    """Real API provider implementation."""
    
    def __init__(self, base_url: str, timeout: int = 300, auth: Optional[Tuple[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        if auth:
            from requests.auth import HTTPBasicAuth
            self.session.auth = HTTPBasicAuth(auth[0], auth[1])
        
        logger.log_app_event("real_api_provider_initialized", {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "has_auth": auth is not None
        })
    
    def test_connection(self, silent: bool = False) -> bool:
        """Test connection to the real API."""
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/progress", timeout=10)
            if not silent:
                logger.info("Real API connection test successful")
            return response.status_code == 200
        except Exception as e:
            if not silent:
                logger.error(f"Real API connection test failed: {e}")
            return False
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1) -> Dict[str, Any]:
        """Generate a single image using real API."""
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "width": width,
                "height": height,
                "sampler_name": sampler,
                "seed": seed if seed != -1 else -1,
                "batch_size": 1,
                "n_iter": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed with status {response.status_code}")
            
            result = response.json()
            
            if "images" not in result or not result["images"]:
                raise GenerationError("No images returned from API")
            
            return {
                "images": result["images"],
                "info": result.get("info", {}),
                "success": True,
                "provider": "real"
            }
            
        except Exception as e:
            logger.error(f"Real API generation error: {e}")
            raise GenerationError(f"Failed to generate image: {e}")
    
    def generate_batch(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1, 
                      batch_size: int = 1) -> List[Dict[str, Any]]:
        """Generate a batch of images using real API."""
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "width": width,
                "height": height,
                "sampler_name": sampler,
                "seed": seed if seed != -1 else -1,
                "batch_size": batch_size,
                "n_iter": 1
            }
            
            response = self.session.post(
                f"{self.base_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed with status {response.status_code}")
            
            result = response.json()
            
            if "images" not in result or not result["images"]:
                raise GenerationError("No images returned from API")
            
            # Return list of individual image results
            images = []
            for i, image_data in enumerate(result["images"]):
                images.append({
                    "images": [image_data],
                    "info": result.get("info", {}),
                    "success": True,
                    "provider": "real",
                    "batch_index": i
                })
            
            return images
            
        except Exception as e:
            logger.error(f"Real API batch generation error: {e}")
            raise GenerationError(f"Failed to generate batch: {e}")


class MockAPIProvider:
    """Mock API provider implementation."""
    
    def __init__(self, provider_name: str = "Mock Provider"):
        self.provider_name = provider_name
        logger.log_app_event("mock_api_provider_initialized", {
            "provider_name": self.provider_name
        })
    
    def test_connection(self, silent: bool = False) -> bool:
        """Test connection to the mock API (always succeeds)."""
        if not silent:
            logger.info(f"Mock API connection test successful ({self.provider_name})")
        return True
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1) -> Dict[str, Any]:
        """Generate a mock image."""
        try:
            # Create a simple mock image
            mock_image = self._create_mock_image(width, height, prompt)
            
            # Convert to base64
            buffered = io.BytesIO()
            mock_image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "images": [img_base64],
                "info": {
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "steps": steps,
                    "cfg_scale": cfg_scale,
                    "width": width,
                    "height": height,
                    "sampler_name": sampler,
                    "seed": seed
                },
                "success": True,
                "provider": self.provider_name
            }
            
        except Exception as e:
            logger.error(f"Mock API generation error: {e}")
            raise GenerationError(f"Failed to generate mock image: {e}")
    
    def generate_batch(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1, 
                      batch_size: int = 1) -> List[Dict[str, Any]]:
        """Generate a batch of mock images."""
        images = []
        
        for i in range(batch_size):
            try:
                # Create slightly different mock images for variety
                mock_image = self._create_mock_image(width, height, f"{prompt} (variant {i+1})")
                
                # Convert to base64
                buffered = io.BytesIO()
                mock_image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                images.append({
                    "images": [img_base64],
                    "info": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "steps": steps,
                        "cfg_scale": cfg_scale,
                        "width": width,
                        "height": height,
                        "sampler_name": sampler,
                        "seed": seed + i if seed != -1 else -1
                    },
                    "success": True,
                    "provider": self.provider_name,
                    "batch_index": i
                })
                
            except Exception as e:
                logger.error(f"Mock API batch generation error for image {i}: {e}")
                raise GenerationError(f"Failed to generate mock image {i}: {e}")
        
        return images
    
    def _create_mock_image(self, width: int, height: int, prompt: str) -> Image.Image:
        """Create a simple mock image based on the prompt."""
        # Create a simple gradient image
        image = Image.new('RGB', (width, height))
        
        # Simple gradient based on prompt hash
        import hashlib
        prompt_hash = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        
        # Generate colors based on prompt hash
        r = (prompt_hash & 0xFF0000) >> 16
        g = (prompt_hash & 0x00FF00) >> 8
        b = (prompt_hash & 0x0000FF)
        
        # Create gradient
        for y in range(height):
            for x in range(width):
                # Simple gradient effect
                factor = (x + y) / (width + height)
                pixel_r = int(r * (1 - factor) + 255 * factor)
                pixel_g = int(g * (1 - factor) + 255 * factor)
                pixel_b = int(b * (1 - factor) + 255 * factor)
                image.putpixel((x, y), (pixel_r, pixel_g, pixel_b))
        
        return image


class UnifiedAPIClient:
    """Unified API client that can work with different providers."""
    
    def __init__(self, provider: Optional[APIProvider] = None, 
                 base_url: str = None, timeout: int = None, 
                 use_mock: bool = False, mock_provider_name: str = "Mock Provider"):
        """
        Initialize the unified API client.
        
        Args:
            provider: Existing API provider instance (optional)
            base_url: Base URL for real API (when use_mock=False)
            timeout: Request timeout
            use_mock: Whether to use mock provider
            mock_provider_name: Name for mock provider
        """
        # Use central API config if not provided
        if base_url is None:
            base_url = api_config.base_url
        if timeout is None:
            timeout = api_config.timeout
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.use_mock = use_mock
        
        # Initialize provider
        if provider is not None:
            self.provider = provider
        elif use_mock:
            self.provider = MockAPIProvider(mock_provider_name)
        else:
            # Set up authentication for real API
            auth = None
            if api_config.api_type == "rundiffusion" and api_config.rundiffusion_config:
                username = api_config.rundiffusion_config.get('username', 'rduser')
                password = api_config.rundiffusion_config.get('password', 'rdpass')
                auth = (username, password)
            
            self.provider = RealAPIProvider(base_url, timeout, auth)
        
        logger.log_app_event("unified_api_client_initialized", {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "use_mock": self.use_mock,
            "provider_type": type(self.provider).__name__
        })
    
    def test_connection(self, silent: bool = False) -> bool:
        """Test connection to the API."""
        return self.provider.test_connection(silent)
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1) -> Dict[str, Any]:
        """Generate a single image."""
        return self.provider.generate_image(
            prompt, negative_prompt, steps, cfg_scale, 
            width, height, sampler, seed
        )
    
    def generate_batch(self, prompt: str, negative_prompt: str = "", 
                      steps: int = 20, cfg_scale: float = 7.0, 
                      width: int = 512, height: int = 512, 
                      sampler: str = "Euler a", seed: int = -1, 
                      batch_size: int = 1) -> List[Dict[str, Any]]:
        """Generate a batch of images."""
        return self.provider.generate_batch(
            prompt, negative_prompt, steps, cfg_scale, 
            width, height, sampler, seed, batch_size
        )
    
    def switch_provider(self, provider: APIProvider):
        """Switch to a different API provider."""
        self.provider = provider
        logger.log_app_event("api_provider_switched", {
            "new_provider_type": type(provider).__name__
        })
    
    def switch_to_mock(self, provider_name: str = "Mock Provider"):
        """Switch to mock provider."""
        self.provider = MockAPIProvider(provider_name)
        self.use_mock = True
        logger.log_app_event("switched_to_mock_provider", {
            "provider_name": provider_name
        })
    
    def switch_to_real(self, base_url: str = None, timeout: int = None):
        """Switch to real API provider."""
        if base_url is None:
            base_url = self.base_url
        if timeout is None:
            timeout = self.timeout
        
        # Set up authentication
        auth = None
        if api_config.api_type == "rundiffusion" and api_config.rundiffusion_config:
            username = api_config.rundiffusion_config.get('username', 'rduser')
            password = api_config.rundiffusion_config.get('password', 'rdpass')
            auth = (username, password)
        elif api_config.api_type == "pinokio" and api_config.pinokio_config:
            # PINOKIO uses basic auth with email and password
            email = api_config.pinokio_config.get('email', '')
            password = api_config.pinokio_config.get('password', '')
            auth = (email, password)
        
        self.provider = RealAPIProvider(base_url, timeout, auth)
        self.use_mock = False
        self.base_url = base_url
        self.timeout = timeout
        
        logger.log_app_event("switched_to_real_provider", {
            "base_url": base_url,
            "timeout": timeout
        })


# Factory functions for backward compatibility
def create_forge_client(use_mock: bool = True, api_type: str = "local") -> UnifiedAPIClient:
    """Create a forge client with specified configuration."""
    if use_mock:
        provider_name = f"Mock {api_type.title()} Provider"
        return UnifiedAPIClient(use_mock=True, mock_provider_name=provider_name)
    else:
        return UnifiedAPIClient(use_mock=False)


def get_available_providers() -> List[str]:
    """Get list of available API providers."""
    return ["local", "rundiffusion", "pinokio", "mock"]


