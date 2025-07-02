"""
Configuration API routes for the Flask web dashboard.

This module contains all configuration-related API endpoints,
using the service layer for business logic and utilities for
error handling and response formatting.
"""

from flask import Blueprint, request
from utils.decorators import handle_errors, validate_input, require_json
from utils.response_helpers import (
    success_response, error_response, config_response, 
    not_found_response, validation_error_response
)
from services.config_service import ConfigService
from core.config_handler import config_handler
from core.centralized_logger import logger

# Create blueprint
configs_bp = Blueprint('configs', __name__)

# Initialize service
config_service = ConfigService(config_handler)


@configs_bp.route('/api/configs', methods=['GET'])
@handle_errors
def get_configs():
    """
    Get all configurations.
    
    Returns:
        JSON response with all configurations
    """
    configs = config_service.get_all_configs()
    return success_response({'configs': configs})


@configs_bp.route('/api/configs/<config_name>', methods=['GET'])
@handle_errors
def get_config(config_name):
    """
    Get a specific configuration.
    
    Args:
        config_name: Name of the configuration
        
    Returns:
        JSON response with configuration data
    """
    config = config_service.get_config(config_name)
    return config_response(config, config_name)


@configs_bp.route('/api/configs', methods=['POST'])
@handle_errors
@require_json
@validate_input(required_fields=['name', 'config'])
def create_config():
    """
    Create a new configuration.
    
    Expected JSON:
        {
            "name": "config_name",
            "config": { ... }
        }
        
    Returns:
        JSON response indicating success or failure
    """
    data = request.get_json()
    config_name = data['name']
    config_data = data['config']
    
    success = config_service.create_config(config_name, config_data)
    
    if success:
        return success_response(
            message=f'Configuration {config_name} created successfully'
        )
    else:
        return error_response("Failed to create configuration")


@configs_bp.route('/api/configs/<config_name>', methods=['PUT'])
@handle_errors
@require_json
@validate_input(required_fields=['config'])
def update_config(config_name):
    """
    Update an existing configuration.
    
    Args:
        config_name: Name of the configuration
        
    Expected JSON:
        {
            "config": { ... }
        }
        
    Returns:
        JSON response indicating success or failure
    """
    data = request.get_json()
    config_data = data['config']
    
    success = config_service.update_config(config_name, config_data)
    
    if success:
        return success_response(
            message=f'Configuration {config_name} updated successfully'
        )
    else:
        return error_response("Failed to update configuration")


@configs_bp.route('/api/configs/<config_name>', methods=['DELETE'])
@handle_errors
def delete_config(config_name):
    """
    Delete a configuration.
    
    Args:
        config_name: Name of the configuration
        
    Returns:
        JSON response indicating success or failure
    """
    success = config_service.delete_config(config_name)
    
    if success:
        return success_response(
            message=f'Configuration {config_name} deleted successfully'
        )
    else:
        return error_response("Failed to delete configuration")


@configs_bp.route('/api/configs/<config_name>/settings', methods=['GET'])
@handle_errors
def get_config_settings(config_name):
    """
    Get detailed settings for a specific config.
    
    Args:
        config_name: Name of the configuration
        
    Returns:
        JSON response with configuration settings
    """
    settings = config_service.get_config_settings(config_name)
    return success_response(settings)


@configs_bp.route('/api/configs/<config_name>/settings', methods=['PUT'])
@handle_errors
@require_json
@validate_input(required_fields=['settings'])
def update_config_settings(config_name):
    """
    Update settings for a specific config.
    
    Args:
        config_name: Name of the configuration
        
    Expected JSON:
        {
            "settings": { ... }
        }
        
    Returns:
        JSON response indicating success or failure
    """
    data = request.get_json()
    settings = data['settings']
    
    success = config_service.update_config_settings(config_name, settings)
    
    if success:
        return success_response(
            message=f'Config {config_name} updated successfully',
            data={'config_name': config_name}
        )
    else:
        return error_response("Failed to update configuration settings")


@configs_bp.route('/api/configs/<config_name>/thumbnail', methods=['GET'])
@handle_errors
def get_config_thumbnail(config_name):
    """
    Get thumbnail for a config if it exists.
    
    Args:
        config_name: Name of the configuration
        
    Returns:
        JSON response with thumbnail data
    """
    config = config_service.get_config(config_name)
    thumbnail = config.get('thumbnail')
    
    if thumbnail:
        return success_response({'thumbnail': thumbnail})
    else:
        return not_found_response('thumbnail', config_name)


@configs_bp.route('/api/configs/<config_name>/thumbnail', methods=['POST'])
@handle_errors
@require_json
@validate_input(required_fields=['thumbnail'])
def save_config_thumbnail(config_name):
    """
    Save thumbnail for a config.
    
    Args:
        config_name: Name of the configuration
        
    Expected JSON:
        {
            "thumbnail": "base64_image_data"
        }
        
    Returns:
        JSON response indicating success or failure
    """
    data = request.get_json()
    thumbnail = data['thumbnail']
    
    # Get current config and update with thumbnail
    config = config_service.get_config(config_name)
    config['thumbnail'] = thumbnail
    
    success = config_service.update_config(config_name, config)
    
    if success:
        return success_response(message='Thumbnail saved successfully')
    else:
        return error_response("Failed to save thumbnail")


@configs_bp.route('/api/configs/create-from-image', methods=['POST'])
@handle_errors
@require_json
@validate_input(required_fields=['config_name', 'analysis_result'])
def create_config_from_image():
    """
    Create a new config based on image analysis.
    
    Expected JSON:
        {
            "config_name": "new_config_name",
            "analysis_result": { ... },
            "custom_settings": { ... }  // optional
        }
        
    Returns:
        JSON response with created configuration
    """
    data = request.get_json()
    config_name = data['config_name']
    analysis_result = data['analysis_result']
    custom_settings = data.get('custom_settings', {})
    
    # Check if config already exists
    if config_service.config_exists(config_name):
        return error_response(
            f'Config {config_name} already exists',
            status_code=409
        )
    
    # Create config from analysis
    from core.image_analyzer import ImageAnalyzer
    analyzer = ImageAnalyzer()
    
    # Merge analysis result with custom settings
    if 'suggested_config' in analysis_result:
        suggested_config = analysis_result['suggested_config']
        
        # Handle case where suggested_config might be a string
        if isinstance(suggested_config, str):
            try:
                import json
                base_config = json.loads(suggested_config)
            except (json.JSONDecodeError, TypeError):
                # Create basic config with the string as description
                base_config = {
                    'name': config_name,
                    'description': suggested_config,
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
        else:
            base_config = suggested_config
    else:
        # Create basic config if no suggested config
        base_config = {
            'name': config_name,
            'description': f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
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
    
    # Override with custom settings
    if custom_settings:
        for section, settings in custom_settings.items():
            if section in base_config:
                if isinstance(settings, dict) and isinstance(base_config[section], dict):
                    base_config[section].update(settings)
                else:
                    base_config[section] = settings
            else:
                base_config[section] = settings
    
    # Update name and description
    base_config['name'] = config_name
    if 'description' not in base_config:
        base_config['description'] = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    
    # Save the config
    success = config_service.create_config(config_name, base_config)
    
    if not success:
        return error_response("Failed to create configuration")
    
    logger.log_app_event("config_created_from_image", {
        "config_name": config_name,
        "image_width": analysis_result.get('width', 0),
        "image_height": analysis_result.get('height', 0),
        "has_metadata": 'metadata' in analysis_result,
        "has_parameters": 'parameters' in analysis_result
    })
    
    return success_response({
        'config_name': config_name,
        'config': base_config
    }, message=f'Config {config_name} created successfully') 