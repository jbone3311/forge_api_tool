"""
Output Routes - Flask Blueprint for output management endpoints
"""

from flask import Blueprint, request, current_app
from services.output_service import OutputService

# Create blueprint
output_bp = Blueprint('output', __name__, url_prefix='/api/outputs')

# Create separate blueprint for direct file serving
output_files_bp = Blueprint('output_files', __name__)

# Global variable to store the output service instance
_output_service = None

def init_output_service(output_service_instance):
    """Initialize the output service for use in routes.
    
    Args:
        output_service_instance: The OutputService instance
    """
    global _output_service
    _output_service = output_service_instance


@output_bp.route('')
def get_outputs():
    """Get all outputs with optional filtering."""
    try:
        # Get query parameters
        date = request.args.get('date')
        config_name = request.args.get('config')
        
        # Get outputs
        result = _output_service.get_outputs(date=date, config_name=config_name)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_outputs: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/list')
def list_outputs():
    """Get all outputs (alias for root endpoint)."""
    return get_outputs()


@output_bp.route('/statistics')
def get_output_statistics():
    """Get output statistics."""
    try:
        # Get statistics
        result = _output_service.get_output_statistics()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_output_statistics: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/dates')
def get_output_dates():
    """Get all available output dates."""
    try:
        # Get dates
        result = _output_service.get_output_dates()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_output_dates: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/metadata/<date>/<filename>')
def get_output_metadata(date, filename):
    """Get metadata for a specific output image."""
    try:
        # Get metadata
        result = _output_service.get_output_metadata(date, filename)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_output_metadata: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/directory/<config_name>')
def get_output_directory(config_name):
    """Get the output directory path for a specific config."""
    try:
        # Get directory
        result = _output_service.get_output_directory(config_name)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_output_directory: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/directory/<config_name>/latest')
def get_latest_output_directory(config_name):
    """Get the most recent output directory for a specific config."""
    try:
        # Get latest directory
        result = _output_service.get_latest_output_directory(config_name)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in get_latest_output_directory: {e}")
        return {'success': False, 'error': str(e)}, 500


@output_bp.route('/open-folder/<config_name>')
def open_output_folder(config_name):
    """Open the output folder for a specific configuration."""
    try:
        # Open folder
        result = _output_service.open_output_folder(config_name)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in open_output_folder: {e}")
        return {'success': False, 'error': str(e)}, 500


# Direct file serving route (separate blueprint)
@output_files_bp.route('/outputs/<date>/<filename>')
def serve_output_image(date, filename):
    """Serve output images from date-based folders."""
    try:
        # Serve image
        return _output_service.serve_output_image(date, filename)
        
    except Exception as e:
        _output_service.logger.log_error(f"Unexpected error in serve_output_image: {e}")
        return {'success': False, 'error': str(e)}, 500 