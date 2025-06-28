#!/usr/bin/env python3
"""
Central API configuration for Forge API Tool
"""

import os
import json
from typing import Dict, Any, Optional

class APIConfig:
    """Central configuration for API settings."""
    
    def __init__(self):
        # Default API settings
        self.base_url = "http://127.0.0.1:7860"
        self.timeout = 300
        self.retry_attempts = 3
        
        # API type and configuration
        self.api_type = "local"  # "local" or "rundiffusion"
        self.rundiffusion_config = None
        
        # Load configuration
        self._load_from_env()
        self._load_api_preference()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        if os.getenv('FORGE_API_URL'):
            self.base_url = os.getenv('FORGE_API_URL')
        if os.getenv('FORGE_API_TIMEOUT'):
            self.timeout = int(os.getenv('FORGE_API_TIMEOUT'))
        if os.getenv('FORGE_API_RETRY_ATTEMPTS'):
            self.retry_attempts = int(os.getenv('FORGE_API_RETRY_ATTEMPTS'))
    
    def _load_api_preference(self):
        """Load API preference from file."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api_preference.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.api_type = data.get('api_type', 'local')
                    self.rundiffusion_config = data.get('rundiffusion_config')
                    
                    # Update base_url based on API type
                    if self.api_type == 'rundiffusion' and self.rundiffusion_config:
                        self.base_url = self.rundiffusion_config.get('url', self.base_url)
        except Exception as e:
            print(f"Warning: Could not load API preference: {e}")
    
    def _save_api_preference(self):
        """Save API preference to file."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api_preference.json')
            data = {
                'api_type': self.api_type,
                'rundiffusion_config': self.rundiffusion_config
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save API preference: {e}")
    
    def switch_to_rundiffusion(self, config: Dict[str, Any]):
        """Switch to RunDiffusion API."""
        self.api_type = "rundiffusion"
        self.rundiffusion_config = config
        self.base_url = config.get('url', self.base_url)
        self._save_api_preference()
        
        # Also save to rundiffusion_config.json for compatibility
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rundiffusion_config.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save RunDiffusion config: {e}")
    
    def switch_to_local(self):
        """Switch to local Forge API."""
        self.api_type = "local"
        self.rundiffusion_config = None
        self.base_url = "http://127.0.0.1:7860"
        self._save_api_preference()
        
        # Remove rundiffusion_config.json for compatibility
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rundiffusion_config.json')
            if os.path.exists(config_path):
                os.remove(config_path)
        except Exception as e:
            print(f"Warning: Could not remove RunDiffusion config: {e}")
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings as a dictionary."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "api_type": self.api_type,
            "rundiffusion_config": self.rundiffusion_config
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update API settings."""
        if 'base_url' in settings:
            self.base_url = settings['base_url']
        if 'timeout' in settings:
            self.timeout = settings['timeout']
        if 'retry_attempts' in settings:
            self.retry_attempts = settings['retry_attempts']
    
    def get_current_api_info(self) -> Dict[str, Any]:
        """Get information about the current API configuration."""
        if self.api_type == "rundiffusion" and self.rundiffusion_config:
            return {
                "type": "rundiffusion",
                "url": self.rundiffusion_config.get('url'),
                "username": self.rundiffusion_config.get('username'),
                "base_url": self.base_url
            }
        else:
            return {
                "type": "local",
                "url": self.base_url,
                "base_url": self.base_url
            }

# Global API configuration instance
api_config = APIConfig() 