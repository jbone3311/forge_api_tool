"""
Settings Service - Handles all settings management operations
"""

import os
import sys
import json
import requests
from typing import Dict, Any, Optional

# Add the parent directory to the path to import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.exceptions import ConfigurationError
from utils.response_helpers import create_success_response, create_error_response
from utils.validators import validate_settings_data


class SettingsService:
    """Service class for managing application settings."""
    
    def __init__(self, logger_instance, forge_api_client_instance):
        """Initialize the settings service.
        
        Args:
            logger_instance: The logger instance
            forge_api_client_instance: The forge API client instance
        """
        self.logger = logger_instance
        self.forge_api_client = forge_api_client_instance
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def get_api_settings(self) -> Dict[str, Any]:
        """Get current API settings.
        
        Returns:
            Dictionary containing API settings
        """
        try:
            # Load from api_preference.json
            api_pref_path = os.path.join(self.base_dir, 'api_preference.json')
            
            if os.path.exists(api_pref_path):
                with open(api_pref_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # Default settings
                settings = {
                    'api_type': 'local',
                    'local_config': {
                        'url': 'http://localhost:3000',
                        'timeout': 30
                    },
                    'rundiffusion_config': {
                        'url': '',
                        'username': '',
                        'password': '',
                        'timeout': 60
                    }
                }
            
            self.logger.log_app_event("api_settings_retrieved", settings)
            return create_success_response(settings)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get API settings: {e}")
            return create_error_response(str(e), 500)
    
    def save_api_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save API settings.
        
        Args:
            data: API settings data
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Validate required fields
            if 'api_type' not in data:
                return create_error_response('API type is required', 400)
            
            # Validate settings data
            if not validate_settings_data(data, 'api'):
                return create_error_response('Invalid API settings data', 400)
            
            # Save to api_preference.json
            api_pref_path = os.path.join(self.base_dir, 'api_preference.json')
            
            with open(api_pref_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # If switching to RunDiffusion, also update rundiffusion_config.json
            if data['api_type'] == 'rundiffusion' and 'rundiffusion_config' in data:
                rundiffusion_path = os.path.join(self.base_dir, 'rundiffusion_config.json')
                with open(rundiffusion_path, 'w', encoding='utf-8') as f:
                    json.dump(data['rundiffusion_config'], f, indent=2)
            
            self.logger.log_app_event("api_settings_saved", data)
            return create_success_response({'message': 'API settings saved successfully'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to save API settings: {e}")
            return create_error_response(str(e), 500)
    
    def test_api_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test API connection.
        
        Args:
            data: Connection test data
            
        Returns:
            Dictionary containing test result
        """
        try:
            api_type = data.get('api_type', 'local')
            
            if api_type == 'rundiffusion':
                # Test RunDiffusion connection
                success = self.forge_api_client.test_connection()
                if success:
                    return create_success_response({'message': 'RunDiffusion connection successful'})
                else:
                    return create_error_response('Failed to connect to RunDiffusion', 400)
            else:
                # Test local API connection
                try:
                    response = requests.get('http://localhost:3000/api/status', timeout=5)
                    if response.status_code == 200:
                        return create_success_response({'message': 'Local API connection successful'})
                    else:
                        return create_error_response(f'Local API returned status {response.status_code}', 400)
                except requests.exceptions.RequestException as e:
                    return create_error_response(f'Failed to connect to local API: {str(e)}', 400)
            
        except Exception as e:
            self.logger.log_error(f"Failed to test API connection: {e}")
            return create_error_response(str(e), 500)
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings.
        
        Returns:
            Dictionary containing output settings
        """
        try:
            # Load from settings file or return defaults
            settings_path = os.path.join(self.base_dir, 'output_settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # Default settings
                settings = {
                    'base_directory': os.path.join(self.base_dir, 'outputs'),
                    'naming_pattern': 'timestamp',
                    'custom_pattern': '{config}_{timestamp}_{seed}',
                    'auto_open_outputs': True,
                    'max_outputs_display': 50
                }
            
            return create_success_response(settings)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get output settings: {e}")
            return create_error_response(str(e), 500)
    
    def save_output_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save output settings.
        
        Args:
            data: Output settings data
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Validate settings data
            if not validate_settings_data(data, 'output'):
                return create_error_response('Invalid output settings data', 400)
            
            # Save to settings file
            settings_path = os.path.join(self.base_dir, 'output_settings.json')
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.log_app_event("output_settings_saved", data)
            return create_success_response({'message': 'Output settings saved successfully'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to save output settings: {e}")
            return create_error_response(str(e), 500)
    
    def get_log_settings(self) -> Dict[str, Any]:
        """Get log settings.
        
        Returns:
            Dictionary containing log settings
        """
        try:
            # Load from settings file or return defaults
            settings_path = os.path.join(self.base_dir, 'log_settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # Default settings
                settings = {
                    'retention_days': 30,
                    'auto_cleanup': True
                }
            
            return create_success_response(settings)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get log settings: {e}")
            return create_error_response(str(e), 500)
    
    def save_log_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save log settings.
        
        Args:
            data: Log settings data
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Validate settings data
            if not validate_settings_data(data, 'logs'):
                return create_error_response('Invalid log settings data', 400)
            
            # Save to settings file
            settings_path = os.path.join(self.base_dir, 'log_settings.json')
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.log_app_event("log_settings_saved", data)
            return create_success_response({'message': 'Log settings saved successfully'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to save log settings: {e}")
            return create_error_response(str(e), 500)
    
    def get_advanced_settings(self) -> Dict[str, Any]:
        """Get advanced settings.
        
        Returns:
            Dictionary containing advanced settings
        """
        try:
            # Load from settings file or return defaults
            settings_path = os.path.join(self.base_dir, 'advanced_settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # Default settings
                settings = {
                    'max_concurrent_jobs': 2,
                    'job_timeout': 30,
                    'auto_refresh_interval': 5,
                    'enable_cors': True,
                    'max_upload_size': 10,
                    'theme': 'light',
                    'sidebar_width': 300
                }
            
            return create_success_response(settings)
            
        except Exception as e:
            self.logger.log_error(f"Failed to get advanced settings: {e}")
            return create_error_response(str(e), 500)
    
    def save_advanced_settings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save advanced settings.
        
        Args:
            data: Advanced settings data
            
        Returns:
            Dictionary containing operation result
        """
        try:
            # Validate settings data
            if not validate_settings_data(data, 'advanced'):
                return create_error_response('Invalid advanced settings data', 400)
            
            # Save to settings file
            settings_path = os.path.join(self.base_dir, 'advanced_settings.json')
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self.logger.log_app_event("advanced_settings_saved", data)
            return create_success_response({'message': 'Advanced settings saved successfully'})
            
        except Exception as e:
            self.logger.log_error(f"Failed to save advanced settings: {e}")
            return create_error_response(str(e), 500) 