#!/usr/bin/env python3
"""
Mock API Provider System for Forge API Tool
Simulates multiple API providers without requiring actual servers.
"""

import json
import time
import base64
import random
import threading
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
from .centralized_logger import logger
from .api_config import api_config


class MockAPIProvider:
    """Base class for mock API providers."""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.is_connected = False
        self.response_time = random.uniform(0.1, 0.5)  # Simulate response time
        
    def test_connection(self) -> bool:
        """Test connection to mock API."""
        self.is_connected = True
        logger.info(f"Mock {self.name} API connection test successful")
        return True
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get available models."""
        return [
            {"title": "stable-diffusion-v1-5", "model_name": "sd-v1-5", "hash": "abc123"},
            {"title": "stable-diffusion-xl", "model_name": "sd-xl", "hash": "def456"},
            {"title": "dreamshaper-8", "model_name": "dreamshaper", "hash": "ghi789"}
        ]
    
    def get_samplers(self) -> List[Dict[str, Any]]:
        """Get available samplers."""
        return [
            {"name": "Euler a", "aliases": ["euler_a"]},
            {"name": "DPM++ 2M Karras", "aliases": ["dpmpp_2m"]},
            {"name": "DPM++ SDE Karras", "aliases": ["dpmpp_sde"]},
            {"name": "LMS", "aliases": ["lms"]},
            {"name": "Heun", "aliases": ["heun"]}
        ]
    
    def get_options(self) -> Dict[str, Any]:
        """Get current options."""
        return {
            "sd_model_checkpoint": "sd-v1-5",
            "CLIP_stop_at_last_layers": 1,
            "sd_vae": "Automatic"
        }
    
    def set_options(self, options: Dict[str, Any]) -> bool:
        """Set options."""
        logger.info(f"Mock {self.name} API options updated")
        return True
    
    def get_progress(self) -> Dict[str, Any]:
        """Get generation progress."""
        return {
            "progress": 0.0,
            "eta_relative": 0.0,
            "state": {"job_count": 0, "job_no": 0, "sampling_step": 0, "sampling_steps": 0},
            "current_image": None,
            "textinfo": None
        }
    
    def interrupt_generation(self) -> bool:
        """Interrupt current generation."""
        logger.info(f"Mock {self.name} API generation interrupted")
        return True
    
    def skip_generation(self) -> bool:
        """Skip current generation."""
        logger.info(f"Mock {self.name} API generation skipped")
        return True


class LocalMockProvider(MockAPIProvider):
    """Mock provider for local Forge installation."""
    
    def __init__(self):
        super().__init__("Local Forge", "http://localhost:3000")
    
    def generate_image(self, config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a mock image."""
        return self._simulate_generation(config, "Local Forge")
    
    def _simulate_generation(self, config: Dict[str, Any], provider: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Simulate image generation process."""
        try:
            # Extract parameters
            prompt = config.get('prompt', 'A beautiful landscape')
            steps = config.get('steps', 20)
            width = config.get('width', 512)
            height = config.get('height', 512)
            seed = config.get('seed', -1)
            
            # Create a mock image
            image_data = self._create_mock_image(prompt, width, height, provider)
            
            # Simulate processing time
            processing_time = steps * 0.1 + random.uniform(0.5, 2.0)
            time.sleep(min(processing_time, 3.0))  # Cap at 3 seconds for demo
            
            metadata = {
                "prompt": prompt,
                "negative_prompt": config.get('negative_prompt', ''),
                "steps": steps,
                "sampler_name": config.get('sampler_name', 'Euler a'),
                "cfg_scale": config.get('cfg_scale', 7.0),
                "seed": seed if seed != -1 else random.randint(1, 999999),
                "width": width,
                "height": height,
                "model": config.get('override_settings', {}).get('sd_model_checkpoint', 'sd-v1-5'),
                "provider": provider,
                "generated_at": datetime.now().isoformat()
            }
            
            return True, image_data, metadata
            
        except Exception as e:
            logger.error(f"Mock generation failed: {e}")
            return False, "", {}


class RunDiffusionMockProvider(MockAPIProvider):
    """Mock provider for RunDiffusion API."""
    
    def __init__(self):
        super().__init__("RunDiffusion", "https://api.rundiffusion.com")
        self.username = "demo_user"
        self.api_key = "demo_api_key_12345"
    
    def generate_image(self, config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a mock image via RunDiffusion."""
        return self._simulate_generation(config, "RunDiffusion")


class ComfyUIMockProvider(MockAPIProvider):
    """Mock provider for ComfyUI API."""
    
    def __init__(self):
        super().__init__("ComfyUI", "http://localhost:8188")
    
    def generate_image(self, config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a mock image via ComfyUI."""
        return self._simulate_generation(config, "ComfyUI")


class Automatic1111MockProvider(MockAPIProvider):
    """Mock provider for Automatic1111 WebUI."""
    
    def __init__(self):
        super().__init__("Automatic1111", "http://localhost:7860")
    
    def generate_image(self, config: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate a mock image via Automatic1111."""
        return self._simulate_generation(config, "Automatic1111")


class MockAPIProviderFactory:
    """Factory for creating mock API providers."""
    
    _providers = {
        "local": LocalMockProvider,
        "rundiffusion": RunDiffusionMockProvider,
        "comfyui": ComfyUIMockProvider,
        "automatic1111": Automatic1111MockProvider
    }
    
    @classmethod
    def create_provider(cls, api_type: str) -> MockAPIProvider:
        """Create a mock provider based on API type."""
        provider_class = cls._providers.get(api_type.lower())
        if not provider_class:
            raise ValueError(f"Unknown API type: {api_type}")
        
        provider = provider_class()
        logger.info(f"Created mock {provider.name} provider")
        return provider
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available mock providers."""
        return list(cls._providers.keys())


# Global mock provider instance
_mock_provider: Optional[MockAPIProvider] = None


def initialize_mock_provider(api_type: str = None) -> MockAPIProvider:
    """Initialize the global mock provider."""
    global _mock_provider
    
    if api_type is None:
        api_type = api_config.api_type
    
    _mock_provider = MockAPIProviderFactory.create_provider(api_type)
    logger.info(f"Mock API provider initialized: {_mock_provider.name}")
    
    return _mock_provider


def get_mock_provider() -> MockAPIProvider:
    """Get the current mock provider."""
    global _mock_provider
    
    if _mock_provider is None:
        _mock_provider = initialize_mock_provider()
    
    return _mock_provider


def switch_mock_provider(api_type: str) -> MockAPIProvider:
    """Switch to a different mock provider."""
    global _mock_provider
    
    _mock_provider = MockAPIProviderFactory.create_provider(api_type)
    logger.info(f"Switched to mock provider: {_mock_provider.name}")
    
    return _mock_provider


# Add the missing _simulate_generation method to MockAPIProvider
def _simulate_generation(self, config: Dict[str, Any], provider: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Simulate image generation process."""
    try:
        # Extract parameters
        prompt = config.get('prompt', 'A beautiful landscape')
        steps = config.get('steps', 20)
        width = config.get('width', 512)
        height = config.get('height', 512)
        seed = config.get('seed', -1)
        
        # Create a mock image
        image_data = self._create_mock_image(prompt, width, height, provider)
        
        # Simulate processing time
        processing_time = steps * 0.1 + random.uniform(0.5, 2.0)
        time.sleep(min(processing_time, 3.0))  # Cap at 3 seconds for demo
        
        metadata = {
            "prompt": prompt,
            "negative_prompt": config.get('negative_prompt', ''),
            "steps": steps,
            "sampler_name": config.get('sampler_name', 'Euler a'),
            "cfg_scale": config.get('cfg_scale', 7.0),
            "seed": seed if seed != -1 else random.randint(1, 999999),
            "width": width,
            "height": height,
            "model": config.get('override_settings', {}).get('sd_model_checkpoint', 'sd-v1-5'),
            "provider": provider,
            "generated_at": datetime.now().isoformat()
        }
        
        return True, image_data, metadata
        
    except Exception as e:
        logger.error(f"Mock generation failed: {e}")
        return False, "", {}


def _create_mock_image(self, prompt: str, width: int, height: int, provider: str) -> str:
    """Create a mock image with the provider's branding."""
    try:
        # Create a colored background based on provider
        colors = {
            "Local Forge": (50, 50, 150),
            "RunDiffusion": (150, 50, 50),
            "ComfyUI": (50, 150, 50),
            "Automatic1111": (150, 150, 50)
        }
        
        bg_color = colors.get(provider, (100, 100, 100))
        
        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add provider text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"{provider}\nMock Image\n{prompt[:30]}..."
        
        # Calculate text position (center)
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(text) * 6
            text_height = 20
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # Add some decorative elements
        for i in range(5):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        
        return base64.b64encode(img_bytes).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Error creating mock image: {e}")
        # Return a simple colored rectangle as fallback
        img = Image.new('RGB', (width, height), (128, 128, 128))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


# Add the methods to the base class
MockAPIProvider._simulate_generation = _simulate_generation
MockAPIProvider._create_mock_image = _create_mock_image
