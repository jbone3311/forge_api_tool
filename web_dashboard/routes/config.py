"""
Configuration routes for the Flask application.
"""

from flask import Blueprint, request, jsonify
from web_dashboard.services.config_service import ConfigService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response

# Create blueprint
config_bp = Blueprint('config', __name__, url_prefix='/api/configs')

# Initialize the service
config_service = ConfigService()


@config_bp.route('/', methods=['GET'])
@handle_errors
def get_configs():
    """Get all configurations."""
    result = config_service.get_all_configs()
    return jsonify(result)


@config_bp.route('/<config_name>', methods=['GET'])
@handle_errors
def get_config(config_name):
    """Get a specific configuration."""
    result = config_service.get_config(config_name)
    return jsonify(result)


@config_bp.route('/', methods=['POST'])
@handle_errors
def create_config():
    """Create a new configuration."""
    data = request.get_json()
    config_name = data.get('name')
    config_data = data.get('config')
    
    if not config_name or not config_data:
        return jsonify(create_error_response('Name and config data are required', status_code=400)), 400
    
    result = config_service.create_config(config_name, config_data)
    return jsonify(result)


@config_bp.route('/<config_name>', methods=['PUT'])
@handle_errors
def update_config(config_name):
    """Update a configuration."""
    data = request.get_json()
    config_data = data.get('config')
    
    if not config_data:
        return jsonify(create_error_response('Config data is required', status_code=400)), 400
    
    result = config_service.update_config(config_name, config_data)
    return jsonify(result)


@config_bp.route('/<config_name>', methods=['DELETE'])
@handle_errors
def delete_config(config_name):
    """Delete a configuration."""
    result = config_service.delete_config(config_name)
    return jsonify(result)


@config_bp.route('/<config_name>/settings', methods=['GET'])
@handle_errors
def get_config_settings(config_name):
    """Get detailed settings for a specific config."""
    result = config_service.get_config_settings(config_name)
    
    # Check if the service returned an error response
    if not result.get('success', True):
        status_code = 404 if 'not found' in result.get('error', '').lower() else 400
        return jsonify(result), status_code
    
    return jsonify(result)


@config_bp.route('/<config_name>/settings', methods=['PUT'])
@handle_errors
def update_config_settings(config_name):
    """Update settings for a specific config."""
    data = request.get_json()
    if not data or 'settings' not in data:
        return jsonify(create_error_response('No settings data provided', status_code=400)), 400
    
    new_settings = data['settings']
    result = config_service.update_config_settings(config_name, new_settings)
    
    # Check if the service returned an error response
    if not result.get('success', True):
        status_code = 400
        return jsonify(result), status_code
    
    return jsonify(result)


@config_bp.route('/create-from-image', methods=['POST'])
@handle_errors
def create_config_from_image():
    """Create a new config based on image analysis."""
    data = request.get_json()
    if not data:
        return jsonify(create_error_response('No data provided', status_code=400)), 400
    
    config_name = data.get('config_name')
    analysis_result = data.get('analysis_result')
    custom_settings = data.get('custom_settings', {})
    
    if not config_name:
        return jsonify(create_error_response('Config name is required', status_code=400)), 400
    
    if not analysis_result:
        return jsonify(create_error_response('Analysis result is required', status_code=400)), 400
    
    result = config_service.create_config_from_image(config_name, analysis_result, custom_settings)
    
    # Check if the service returned an error response
    if not result.get('success', True):
        status_code = 409 if 'already exists' in result.get('error', '').lower() else 400
        return jsonify(result), status_code
    
    return jsonify(result)


@config_bp.route('/<config_name>/thumbnail', methods=['GET'])
@handle_errors
def get_config_thumbnail(config_name):
    """Get thumbnail for a config if it exists."""
    result = config_service.get_config_thumbnail(config_name)
    return jsonify(result)


@config_bp.route('/<config_name>/thumbnail', methods=['POST'])
@handle_errors
def save_config_thumbnail(config_name):
    """Save thumbnail for a config."""
    data = request.get_json()
    thumbnail = data.get('thumbnail')
    
    if not thumbnail:
        return jsonify(create_error_response('No thumbnail data provided', status_code=400)), 400
    
    result = config_service.save_config_thumbnail(config_name, thumbnail)
    return jsonify(result) 