"""
API Connection routes for the Flask application.
"""

from flask import Blueprint, request, jsonify
from web_dashboard.services.api_connection_service import APIConnectionService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response

# Create blueprint
api_connection_bp = Blueprint('api_connection', __name__, url_prefix='/api')

# Initialize the service
api_connection_service = APIConnectionService()


@api_connection_bp.route('/connect', methods=['POST'])
@handle_errors
def connect_api():
    """Connect to the Forge API."""
    result = api_connection_service.connect_to_api()
    return jsonify(result)


@api_connection_bp.route('/disconnect', methods=['POST'])
@handle_errors
def disconnect_api():
    """Disconnect from the Forge API."""
    result = api_connection_service.disconnect_from_api()
    return jsonify(result)


@api_connection_bp.route('/connection-status', methods=['GET'])
@handle_errors
def get_connection_status():
    """Get the current API connection status."""
    result = api_connection_service.get_connection_status()
    return jsonify(result)


@api_connection_bp.route('/test-connection', methods=['POST'])
@handle_errors
def test_connection():
    """Test the current API connection."""
    result = api_connection_service.test_connection()
    return jsonify(result)


@api_connection_bp.route('/config', methods=['PUT'])
@handle_errors
def update_api_config():
    """Update API configuration settings."""
    data = request.get_json()
    if not data:
        return create_error_response('No configuration data provided', status_code=400)
    
    result = api_connection_service.update_api_config(data)
    return jsonify(result)


@api_connection_bp.route('/info', methods=['GET'])
@handle_errors
def get_api_info():
    """Get API information and capabilities."""
    result = api_connection_service.get_api_info()
    return jsonify(result) 