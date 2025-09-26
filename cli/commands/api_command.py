#!/usr/bin/env python3
"""
API Command

Commands for managing API connections and providers.
"""

import json
import os
from typing import Dict, Any
from .base import BaseCommand


class APITestCommand(BaseCommand):
    """Command to test API connection."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the API test command."""
        try:
            if not self.context._ensure_api_client():
                print("❌ No API client configured")
                return False
            
            print("🔗 Testing API connection...")
            if self.context.forge_client.test_connection():
                print("✅ API connection successful")
                return True
            else:
                print("❌ API connection failed")
                return False
            
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the API test command."""
        return "Test connection to the configured API."


class APISwitchCommand(BaseCommand):
    """Command to switch API provider."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the API switch command."""
        try:
            provider = args.get('provider')
            if not provider:
                print("❌ Provider name required")
                return False
            
            if provider not in ['local', 'rundiffusion', 'pinokio', 'mock']:
                print("❌ Invalid provider. Available: local, rundiffusion, pinokio, mock")
                return False
            
            # Load configuration based on provider
            if provider == 'pinokio':
                success = self._configure_pinokio()
            elif provider == 'rundiffusion':
                success = self._configure_rundiffusion()
            elif provider == 'local':
                success = self._configure_local()
            elif provider == 'mock':
                success = self._configure_mock()
            
            if success:
                print(f"✅ Switched to {provider} API provider")
                # Test connection
                if provider != 'mock':
                    print("🔗 Testing connection...")
                    if self.context.forge_client.test_connection():
                        print("✅ Connection successful")
                    else:
                        print("⚠️  Connection failed, but provider configured")
                return True
            else:
                print(f"❌ Failed to switch to {provider} provider")
                return False
            
        except Exception as e:
            print(f"❌ Error switching API provider: {e}")
            return False
    
    def _configure_pinokio(self) -> bool:
        """Configure PINOKIO provider."""
        try:
            # Load PINOKIO config
            config_path = os.path.join(self.context.project_root, 'config', 'pinokio_config.json')
            if not os.path.exists(config_path):
                print("❌ PINOKIO configuration not found. Please create config/pinokio_config.json")
                return False
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update API preference
            preference_path = os.path.join(self.context.project_root, 'api_preference.json')
            preference = {
                'api_type': 'pinokio',
                'pinokio_config': config['pinokio_config']
            }
            
            with open(preference_path, 'w') as f:
                json.dump(preference, f, indent=2)
            
            # Reinitialize API client
            self.context._initialize_api_client()
            
            return True
            
        except Exception as e:
            print(f"❌ Error configuring PINOKIO: {e}")
            return False
    
    def _configure_rundiffusion(self) -> bool:
        """Configure RunDiffusion provider."""
        print("📝 RunDiffusion configuration not implemented yet")
        return False
    
    def _configure_local(self) -> bool:
        """Configure local provider."""
        try:
            preference_path = os.path.join(self.context.project_root, 'api_preference.json')
            preference = {
                'api_type': 'local',
                'base_url': 'http://127.0.0.1:7860'
            }
            
            with open(preference_path, 'w') as f:
                json.dump(preference, f, indent=2)
            
            # Reinitialize API client
            self.context._initialize_api_client()
            
            return True
            
        except Exception as e:
            print(f"❌ Error configuring local API: {e}")
            return False
    
    def _configure_mock(self) -> bool:
        """Configure mock provider."""
        try:
            # Switch to mock without saving to file (for testing)
            self.context.forge_client.switch_to_mock("Test Mock Provider")
            return True
            
        except Exception as e:
            print(f"❌ Error configuring mock API: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the API switch command."""
        return "Switch to a different API provider (local, rundiffusion, pinokio, mock)."


class APIStatusCommand(BaseCommand):
    """Command to show API status."""
    
    def execute(self, args: Dict[str, Any]) -> bool:
        """Execute the API status command."""
        try:
            print("🔗 API Status")
            print("=" * 30)
            
            if self.context.forge_client:
                print("✅ API Client: Configured")
                print(f"   Type: {self.context.forge_client.use_mock and 'Mock' or 'Real'}")
                print(f"   Base URL: {self.context.forge_client.base_url}")
                
                # Test connection
                if self.context.forge_client.test_connection(silent=True):
                    print("   Connection: ✅ Connected")
                else:
                    print("   Connection: ❌ Disconnected")
            else:
                print("❌ API Client: Not configured")
            
            return True
            
        except Exception as e:
            print(f"❌ Error getting API status: {e}")
            return False
    
    def get_help(self) -> str:
        """Get help text for the API status command."""
        return "Show current API configuration and connection status."
