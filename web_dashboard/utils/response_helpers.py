"""
Response helper functions for the Flask web dashboard.

This module provides standardized response formatting functions
to ensure consistent API responses across all endpoints.
"""

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, Optional, Union


def success_response(data: Optional[Dict[str, Any]] = None, 
                    message: Optional[str] = None,
                    status_code: int = 200) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        data: Response data dictionary
        message: Success message
        status_code: HTTP status code (default: 200)
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {'success': True}
    
    if data is not None:
        response.update(data)
    
    if message:
        response['message'] = message
    
    response['timestamp'] = datetime.now().isoformat()
    
    return jsonify(response), status_code


def error_response(error: Union[str, Exception], 
                  status_code: int = 400,
                  details: Optional[Dict[str, Any]] = None) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        error: Error message or exception
        status_code: HTTP status code (default: 400)
        details: Additional error details
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'success': False,
        'error': str(error),
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code


def api_response(data: Optional[Dict[str, Any]] = None,
                message: Optional[str] = None,
                success: bool = True,
                status_code: Optional[int] = None) -> tuple:
    """
    Create a standardized API response.
    
    Args:
        data: Response data dictionary
        message: Response message
        success: Whether the operation was successful
        status_code: HTTP status code (auto-determined if None)
        
    Returns:
        Tuple of (response, status_code)
    """
    if status_code is None:
        status_code = 200 if success else 400
    
    if success:
        return success_response(data, message, status_code)
    else:
        return error_response(message or "Operation failed", status_code, data)


def paginated_response(data: list,
                      page: int,
                      per_page: int,
                      total: int,
                      message: Optional[str] = None) -> tuple:
    """
    Create a paginated response.
    
    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Optional message
        
    Returns:
        Tuple of (response, status_code)
    """
    total_pages = (total + per_page - 1) // per_page
    
    pagination_data = {
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return success_response(pagination_data, message)


def validation_error_response(errors: Dict[str, str]) -> tuple:
    """
    Create a validation error response.
    
    Args:
        errors: Dictionary of field names to error messages
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        "Validation failed",
        status_code=400,
        details={'validation_errors': errors}
    )


def not_found_response(resource: str, identifier: str) -> tuple:
    """
    Create a not found response.
    
    Args:
        resource: Type of resource (e.g., 'config', 'job')
        identifier: Resource identifier
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        f"{resource.capitalize()} '{identifier}' not found",
        status_code=404
    )


def unauthorized_response(message: str = "Unauthorized") -> tuple:
    """
    Create an unauthorized response.
    
    Args:
        message: Unauthorized message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(message, status_code=401)


def forbidden_response(message: str = "Forbidden") -> tuple:
    """
    Create a forbidden response.
    
    Args:
        message: Forbidden message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(message, status_code=403)


def server_error_response(message: str = "Internal server error") -> tuple:
    """
    Create a server error response.
    
    Args:
        message: Server error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(message, status_code=500)


def create_success_response(data: Optional[Dict[str, Any]] = None, 
                          message: Optional[str] = None,
                          status_code: int = 200) -> Dict[str, Any]:
    """
    Create a success response dictionary (not a Flask Response object).
    
    Args:
        data: Response data dictionary
        message: Success message
        status_code: HTTP status code (default: 200)
        
    Returns:
        Dictionary containing success response
    """
    response = {'success': True}
    
    if data is not None:
        response.update(data)
    
    if message:
        response['message'] = message
    
    response['timestamp'] = datetime.now().isoformat()
    
    return response


def create_error_response(error: Union[str, Exception], 
                         status_code: int = 400,
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create an error response dictionary (not a Flask Response object).
    
    Args:
        error: Error message or exception
        status_code: HTTP status code (default: 400)
        details: Additional error details
        
    Returns:
        Dictionary containing error response
    """
    response = {
        'success': False,
        'error': str(error),
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return response


def queue_status_response(queue_stats: Dict[str, Any]) -> tuple:
    """
    Create a queue status response.
    
    Args:
        queue_stats: Queue statistics dictionary
        
    Returns:
        Tuple of (response, status_code)
    """
    return success_response({
        'queue': queue_stats,
        'timestamp': datetime.now().isoformat()
    })


def generation_status_response(generation_stats: Dict[str, Any]) -> tuple:
    """
    Create a generation status response.
    
    Args:
        generation_stats: Generation statistics dictionary
        
    Returns:
        Tuple of (response, status_code)
    """
    return success_response({
        'generation': generation_stats,
        'timestamp': datetime.now().isoformat()
    })


def config_response(config: Dict[str, Any], config_name: str) -> tuple:
    """
    Create a configuration response.
    
    Args:
        config: Configuration data
        config_name: Name of the configuration
        
    Returns:
        Tuple of (response, status_code)
    """
    return success_response({
        'config': config,
        'config_name': config_name
    })


def output_response(outputs: list, 
                   date: Optional[str] = None,
                   config_name: Optional[str] = None) -> tuple:
    """
    Create an output response.
    
    Args:
        outputs: List of output data
        date: Optional date filter
        config_name: Optional config name filter
        
    Returns:
        Tuple of (response, status_code)
    """
    data = {'outputs': outputs}
    
    if date:
        data['date'] = date
    if config_name:
        data['config_name'] = config_name
    
    return success_response(data)


# Note: create_success_response and create_error_response are defined above
# and return dictionaries, not Flask Response objects 