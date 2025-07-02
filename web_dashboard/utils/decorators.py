"""
Custom decorators for the Flask web dashboard.

This module provides decorators for error handling, input validation,
and other common patterns used across route handlers.
"""

import functools
import sys
import os
import importlib
# Ensure the project root is in sys.path for core imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import request, jsonify

# Robust import for logger
try:
    from core.centralized_logger import logger
except ModuleNotFoundError:
    try:
        from ..core.centralized_logger import logger
    except (ModuleNotFoundError, ImportError):
        logger_module = importlib.import_module('core.centralized_logger')
        logger = getattr(logger_module, 'logger')

from core.exceptions import (
    ForgeAPIError, ConfigurationError, JobQueueError, ValidationError, FileOperationError, GenerationError, LoggingError, APIError
)
from functools import wraps


def handle_errors(f):
    """
    Decorator to handle common exceptions and return appropriate HTTP responses.
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function with error handling
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConfigurationError as e:
            logger.log_error(f"Configuration error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except FileOperationError as e:
            logger.log_error(f"File operation error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        except ValidationError as e:
            logger.log_error(f"Validation error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except JobQueueError as e:
            logger.log_error(f"Job queue error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        except APIError as e:
            logger.log_error(f"API error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        except GenerationError as e:
            logger.log_error(f"Generation error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        except LoggingError as e:
            logger.log_error(f"Logging error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': 'Internal logging error'}), 500
        except Exception as e:
            logger.log_error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return decorated_function


def validate_input(required_fields=None, optional_fields=None):
    """
    Decorator to validate request input data.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json() or {}
                
                # Validate required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'success': False,
                            'error': f'Missing required fields: {", ".join(missing_fields)}'
                        }), 400
                
                # Validate field types and values
                if optional_fields:
                    for field in optional_fields:
                        if field in data:
                            # Add field-specific validation here if needed
                            pass
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.log_error(f"Input validation error in {f.__name__}: {e}")
                return jsonify({'success': False, 'error': 'Invalid input data'}), 400
        return decorated_function
    return decorator


def log_operation(operation_type):
    """
    Decorator to log application operations.
    
    Args:
        operation_type: Type of operation being performed
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                logger.log_app_event(f"{operation_type}_completed", {
                    "function": f.__name__,
                    "success": True
                })
                return result
            except Exception as e:
                logger.log_app_event(f"{operation_type}_failed", {
                    "function": f.__name__,
                    "error": str(e)
                })
                raise
        return decorated_function
    return decorator


def require_json(f):
    """
    Decorator to ensure request contains valid JSON data.
    
    Args:
        f: The function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        return f(*args, **kwargs)
    return decorated_function


def cache_response(timeout=300):
    """
    Decorator to cache response data (placeholder for future implementation).
    
    Args:
        timeout: Cache timeout in seconds
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # TODO: Implement caching logic
            return f(*args, **kwargs)
        return decorated_function
    return decorator 