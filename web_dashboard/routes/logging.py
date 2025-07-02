"""
Logging Routes - Flask Blueprint for logging management endpoints
"""

from flask import Blueprint, request
from services.logging_service import LoggingService
from core.exceptions import LoggingError

# Create blueprint
logging_bp = Blueprint('logging', __name__, url_prefix='/api/logs')

# Global variable to store the logging service instance
_logging_service = None

def init_logging_service(logging_service_instance):
    """Initialize the logging service for use in routes.
    
    Args:
        logging_service_instance: The LoggingService instance
    """
    global _logging_service
    _logging_service = logging_service_instance


@logging_bp.route('/summary')
def get_logs_summary():
    """Get logging summary."""
    try:
        result = _logging_service.get_logs_summary()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in get_logs_summary: {e}")
        return {'success': False, 'error': str(e)}, 500


@logging_bp.route('/cleanup', methods=['POST'])
def cleanup_logs():
    """Clean up old log files."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 30)
        
        result = _logging_service.cleanup_logs(days_to_keep)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in cleanup_logs: {e}")
        return {'success': False, 'error': str(e)}, 500


@logging_bp.route('/structure')
def get_logs_structure():
    """Get log directory structure information."""
    try:
        result = _logging_service.get_logs_structure()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in get_logs_structure: {e}")
        return {'success': False, 'error': str(e)}, 500


@logging_bp.route('/stats')
def get_logs_stats():
    """Get log file statistics."""
    try:
        result = _logging_service.get_logs_stats()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in get_logs_stats: {e}")
        return {'success': False, 'error': str(e)}, 500


@logging_bp.route('/<log_type>')
def get_logs(log_type):
    """Get logs by type."""
    try:
        content = _logging_service.get_logs_by_type(log_type)
        return content
        
    except LoggingError as e:
        return str(e), 404
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in get_logs: {e}")
        return f"Failed to load logs: {str(e)}", 500


@logging_bp.route('/download')
def download_logs():
    """Download all logs as a zip file."""
    try:
        return _logging_service.download_logs()
        
    except LoggingError as e:
        return {'error': str(e)}, 404
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in download_logs: {e}")
        return {'error': str(e)}, 500


@logging_bp.route('/log-js-error', methods=['POST'])
def log_js_error():
    """Log JavaScript errors."""
    try:
        data = request.get_json()
        result = _logging_service.log_js_error(data)
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in log_js_error: {e}")
        return {'success': False, 'error': str(e)}, 500


# Cache routes (closely related to logging)
@logging_bp.route('/cache/stats')
def get_cache_stats():
    """Get cache statistics."""
    try:
        result = _logging_service.get_cache_stats()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in get_cache_stats: {e}")
        return {'success': False, 'error': str(e)}, 500


@logging_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the cache."""
    try:
        result = _logging_service.clear_cache()
        
        # Return appropriate response
        if result.get('success'):
            return result
        else:
            return result, result.get('status_code', 500)
            
    except Exception as e:
        _logging_service.logger.log_error(f"Unexpected error in clear_cache: {e}")
        return {'success': False, 'error': str(e)}, 500 