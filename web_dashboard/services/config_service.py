"""
Configuration Service for managing configuration files and operations.
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from core.config_handler import config_handler
from core.centralized_logger import logger
from core.exceptions import ConfigurationError, ValidationError, FileOperationError
# from utils.validators import validate_config_name, validate_generation_settings
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response


class ConfigService:
    """Service for managing configuration files and operations."""
    
    def __init__(self, config_handler_instance=None):
        """Initialize the config service.
        
        Args:
            config_handler_instance: The config handler instance (defaults to global)
        """
        self.config_handler = config_handler_instance or config_handler
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations.
        
        Returns:
            Dict containing all configurations
        """
        try:
            configs = self.config_handler.get_all_configs()
            logger.log_app_event("configs_retrieved", {"count": len(configs)})
            return create_success_response(configs)
        except Exception as e:
            logger.log_error(f"Failed to get configs: {e}")
            return create_error_response(str(e))
    
    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get a specific configuration.
        
        Args:
            config_name: Name of the configuration to retrieve
            
        Returns:
            Dict containing the configuration
        """
        try:
            config = self.config_handler.get_config(config_name)
            logger.log_config_operation("retrieved", config_name, True)
            return create_success_response(config)
        except FileNotFoundError:
            logger.log_config_operation("retrieved", config_name, False, {"error": "Config not found"})
            return create_error_response("Configuration not found", status_code=404)
        except Exception as e:
            logger.log_config_operation("retrieved", config_name, False, {"error": str(e)})
            return create_error_response(str(e))
    
    def create_config(self, config_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new configuration.
        
        Args:
            config_name: Name for the new configuration
            config_data: Configuration data
            
        Returns:
            Dict containing success/error response
        """
        try:
            success = self.config_handler.create_config(config_name, config_data)
            
            if success:
                logger.log_config_operation("created", config_name, True)
                return create_success_response({
                    'message': f'Configuration {config_name} created successfully'
                })
            else:
                logger.log_config_operation("created", config_name, False, {"error": "Failed to create"})
                return create_error_response("Failed to create configuration")
        except Exception as e:
            logger.log_config_operation("created", config_name, False, {"error": str(e)})
            return create_error_response(str(e))
    
    def update_config(self, config_name: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a configuration.
        
        Args:
            config_name: Name of the configuration to update
            config_data: New configuration data
            
        Returns:
            Dict containing success/error response
        """
        try:
            success = self.config_handler.update_config(config_name, config_data)
            
            if success:
                logger.log_config_operation("updated", config_name, True)
                return create_success_response({
                    'message': f'Configuration {config_name} updated successfully'
                })
            else:
                logger.log_config_operation("updated", config_name, False, {"error": "Failed to update"})
                return create_error_response("Failed to update configuration")
        except Exception as e:
            logger.log_config_operation("updated", config_name, False, {"error": str(e)})
            return create_error_response(str(e))
    
    def delete_config(self, config_name: str) -> Dict[str, Any]:
        """Delete a configuration.
        
        Args:
            config_name: Name of the configuration to delete
            
        Returns:
            Dict containing success/error response
        """
        try:
            success = self.config_handler.delete_config(config_name)
            
            if success:
                logger.log_config_operation("deleted", config_name, True)
                return create_success_response({
                    'message': f'Configuration {config_name} deleted successfully'
                })
            else:
                logger.log_config_operation("deleted", config_name, False, {"error": "Failed to delete"})
                return create_error_response("Failed to delete configuration")
        except Exception as e:
            logger.log_config_operation("deleted", config_name, False, {"error": str(e)})
            return create_error_response(str(e))
    
    def get_config_settings(self, config_name: str) -> Dict[str, Any]:
        """Get detailed settings for a specific config.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Dict containing the configuration settings
        """
        try:
            config = self.config_handler.get_config(config_name)
            
            return create_success_response({
                'config_name': config_name,
                'settings': config,
                'timestamp': datetime.now().isoformat()
            })
        except FileNotFoundError:
            logger.log_error(f"Config file not found: {config_name}")
            return create_error_response(f'Config {config_name} not found', status_code=404)
        except ConfigurationError as e:
            logger.log_error(f"Configuration error getting settings for {config_name}: {e}")
            return create_error_response(str(e))
        except Exception as e:
            logger.log_error(f"Unexpected error getting settings for {config_name}: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    def update_config_settings(self, config_name: str, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update settings for a specific config.
        
        Args:
            config_name: Name of the configuration
            new_settings: New settings to apply
            
        Returns:
            Dict containing success/error response
        """
        try:
            # Validate the config structure
            required_fields = ['name', 'model_type']
            for field in required_fields:
                if field not in new_settings:
                    return create_error_response(f'Missing required field: {field}')
            
            # Update the config
            success = self.config_handler.update_config(config_name, new_settings)
            
            if success:
                logger.log_app_event("config_updated", {
                    "config_name": config_name,
                    "model_type": new_settings.get('model_type', 'unknown'),
                    "has_prompt_settings": 'prompt_settings' in new_settings,
                    "has_generation_settings": 'generation_settings' in new_settings
                })
                
                return create_success_response({
                    'message': f'Config {config_name} updated successfully',
                    'config_name': config_name,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return create_error_response("Failed to update configuration")
        except ConfigurationError as e:
            logger.log_error(f"Configuration error updating {config_name}: {e}")
            return create_error_response(str(e))
        except ValidationError as e:
            logger.log_error(f"Validation error updating {config_name}: {e}")
            return create_error_response(str(e))
        except Exception as e:
            logger.log_error(f"Unexpected error updating {config_name}: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    def create_config_from_image(self, config_name: str, analysis_result: Dict[str, Any], 
                                custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new config based on image analysis.
        
        Args:
            config_name: Name for the new configuration
            analysis_result: Result from image analysis
            custom_settings: Optional custom settings to override defaults
            
        Returns:
            Dict containing success/error response
        """
        try:
            # Check if config already exists
            if self.config_handler.config_exists(config_name):
                return create_error_response(f'Config {config_name} already exists', status_code=409)
            
            # Create config from analysis
            from core.image_analyzer import ImageAnalyzer
            analyzer = ImageAnalyzer()
            
            # Merge analysis result with custom settings
            if 'suggested_config' in analysis_result:
                suggested_config = analysis_result['suggested_config']
                # Handle case where suggested_config might be a string
                if isinstance(suggested_config, str):
                    # Try to parse as JSON, otherwise use as description
                    try:
                        base_config = json.loads(suggested_config)
                    except (json.JSONDecodeError, TypeError):
                        # If it's not valid JSON, create a basic config with the string as description
                        base_config = self._create_basic_config_from_analysis(config_name, analysis_result, suggested_config)
                else:
                    # It's already a dictionary
                    base_config = suggested_config
            else:
                # Create basic config if no suggested config
                base_config = self._create_basic_config_from_analysis(config_name, analysis_result)
            
            # Override with custom settings
            if custom_settings:
                for section, settings in custom_settings.items():
                    if section in base_config:
                        if isinstance(settings, dict) and isinstance(base_config[section], dict):
                            base_config[section].update(settings)
                        else:
                            # If either is not a dict, replace the entire section
                            base_config[section] = settings
                    else:
                        base_config[section] = settings
            
            # Update name and description
            base_config['name'] = config_name
            if 'description' not in base_config:
                base_config['description'] = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            
            # Save the config
            success = self.config_handler.create_config(config_name, base_config)
            
            if not success:
                return create_error_response("Failed to create configuration")
            
            logger.log_app_event("config_created_from_image", {
                "config_name": config_name,
                "image_width": analysis_result.get('width', 0),
                "image_height": analysis_result.get('height', 0),
                "has_metadata": 'metadata' in analysis_result,
                "has_parameters": 'parameters' in analysis_result
            })
            
            return create_success_response({
                'message': f'Config {config_name} created successfully',
                'config_name': config_name,
                'config': base_config,
                'timestamp': datetime.now().isoformat()
            })
        except ConfigurationError as e:
            logger.log_error(f"Configuration error creating config from image: {e}")
            return create_error_response(str(e))
        except ValidationError as e:
            logger.log_error(f"Validation error creating config from image: {e}")
            return create_error_response(str(e))
        except Exception as e:
            logger.log_error(f"Unexpected error creating config from image: {e}")
            return create_error_response(f'Unexpected error: {str(e)}', status_code=500)
    
    def get_config_thumbnail(self, config_name: str) -> Dict[str, Any]:
        """Get thumbnail for a config if it exists.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Dict containing thumbnail data or error
        """
        try:
            config = self.config_handler.get_config(config_name)
            thumbnail = config.get('thumbnail')
            
            if thumbnail:
                return create_success_response({'thumbnail': thumbnail})
            else:
                return create_error_response('No thumbnail found', status_code=404)
        except Exception as e:
            logger.log_error(f"Failed to get thumbnail for {config_name}: {e}")
            return create_error_response(str(e), status_code=500)
    
    def save_config_thumbnail(self, config_name: str, thumbnail: str) -> Dict[str, Any]:
        """Save thumbnail for a config.
        
        Args:
            config_name: Name of the configuration
            thumbnail: Thumbnail data to save
            
        Returns:
            Dict containing success/error response
        """
        try:
            # Update config with thumbnail
            config = self.config_handler.get_config(config_name)
            config['thumbnail'] = thumbnail
            self.config_handler.save_config(config_name, config)
            
            return create_success_response({'message': 'Thumbnail saved successfully'})
        except Exception as e:
            logger.log_error(f"Failed to save thumbnail for {config_name}: {e}")
            return create_error_response(str(e), status_code=500)
    
    def _create_basic_config_from_analysis(self, config_name: str, analysis_result: Dict[str, Any], 
                                         description: Optional[str] = None) -> Dict[str, Any]:
        """Create a basic configuration from image analysis results.
        
        Args:
            config_name: Name for the configuration
            analysis_result: Analysis results from image
            description: Optional description
            
        Returns:
            Dict containing the basic configuration
        """
        if description is None:
            description = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        return {
            'name': config_name,
            'description': description,
            'model_type': 'sd',
            'prompt_settings': {
                'base_prompt': analysis_result.get('prompt', ''),
                'negative_prompt': analysis_result.get('negative_prompt', '')
            },
            'generation_settings': {
                'steps': 20,
                'width': analysis_result.get('width', 512),
                'height': analysis_result.get('height', 512),
                'batch_size': 1,
                'sampler': 'Euler a',
                'cfg_scale': 7.0
            },
            'model_settings': {
                'checkpoint': '',
                'vae': '',
                'text_encoder': '',
                'gpu_weight': 1.0,
                'swap_method': 'weight',
                'swap_location': 'cpu'
            },
            'output_settings': {
                'dir': f'outputs/{config_name}/{{timestamp}}/',
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            }
        } 