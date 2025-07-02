"""
Settings Routes - Flask Blueprint for settings management endpoints
"""

from flask import Blueprint, request
from services.settings_service import SettingsService

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# Global variable to store the settings service instance
_settings_service = None

def init_settings_service(settings_service_instance):
    """Initialize the settings service for use in routes.
    
    Args:
        settings_service_instance: The SettingsService instance
    """
    global _settings_service
    _settings_service = settings_service_instance


@settings_bp.route('', methods=['GET'])
def get_settings():
    """Get all settings."""
    try:
        # Get all settings
        api_settings = _settings_service.get_api_settings()
        output_settings = _settings_service.get_output_settings()
        log_settings = _settings_service.get_log_settings()
        advanced_settings = _settings_service.get_advanced_settings()
        
        # Combine all settings
        all_settings = {
            'success': True,
            'api': api_settings.get('data', {}),
            'output': output_settings.get('data', {}),
            'logs': log_settings.get('data', {}),
            'advanced': advanced_settings.get('data', {})
        }
        
        return all_settings
        
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in get_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/api', methods=['GET'])
def get_api_settings():
    """Get current API settings."""
    try:
        result = _settings_service.get_api_settings()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in get_api_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/api', methods=['POST'])
def save_api_settings():
    """Save API settings."""
    try:
        data = request.get_json()
        result = _settings_service.save_api_settings(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in save_api_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/test-connection', methods=['POST'])
def test_api_connection():
    """Test API connection."""
    try:
        data = request.get_json()
        result = _settings_service.test_api_connection(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in test_api_connection: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/output', methods=['GET'])
def get_output_settings():
    """Get output settings."""
    try:
        result = _settings_service.get_output_settings()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in get_output_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/output', methods=['POST'])
def save_output_settings():
    """Save output settings."""
    try:
        data = request.get_json()
        result = _settings_service.save_output_settings(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in save_output_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/logs', methods=['GET'])
def get_log_settings():
    """Get log settings."""
    try:
        result = _settings_service.get_log_settings()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in get_log_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/logs', methods=['POST'])
def save_log_settings():
    """Save log settings."""
    try:
        data = request.get_json()
        result = _settings_service.save_log_settings(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in save_log_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/advanced', methods=['GET'])
def get_advanced_settings():
    """Get advanced settings."""
    try:
        result = _settings_service.get_advanced_settings()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in get_advanced_settings: {e}")
        return {'success': False, 'error': str(e)}, 500


@settings_bp.route('/advanced', methods=['POST'])
def save_advanced_settings():
    """Save advanced settings."""
    try:
        data = request.get_json()
        result = _settings_service.save_advanced_settings(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _settings_service.logger.log_error(f"Unexpected error in save_advanced_settings: {e}")
        return {'success': False, 'error': str(e)}, 500 