#!/usr/bin/env python3
"""
Central API configuration for Forge API Tool
"""

import os
from typing import Dict, Any

class APIConfig:
    """Central configuration for API settings."""
    
    def __init__(self):
        # Default API settings
        self.base_url = "http://127.0.0.1:7860"
        self.timeout = 300
        self.retry_attempts = 3
        
        # Load from environment variables if available
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        if os.getenv('FORGE_API_URL'):
            self.base_url = os.getenv('FORGE_API_URL')
        if os.getenv('FORGE_API_TIMEOUT'):
            self.timeout = int(os.getenv('FORGE_API_TIMEOUT'))
        if os.getenv('FORGE_API_RETRY_ATTEMPTS'):
            self.retry_attempts = int(os.getenv('FORGE_API_RETRY_ATTEMPTS'))
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get API settings as a dictionary."""
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update API settings."""
        if 'base_url' in settings:
            self.base_url = settings['base_url']
        if 'timeout' in settings:
            self.timeout = settings['timeout']
        if 'retry_attempts' in settings:
            self.retry_attempts = settings['retry_attempts']

# Global API configuration instance
api_config = APIConfig() 