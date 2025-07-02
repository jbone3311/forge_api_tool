"""
Status routes for the Flask application.
"""

from flask import Blueprint, jsonify, request
from flask_socketio import emit

from web_dashboard.services.status_service import StatusService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response


# Create blueprint
status_bp = Blueprint('status', __name__, url_prefix='/api/status')


@status_bp.route('/')
@handle_errors
def get_system_status():
    """Get comprehensive system status."""
    from web_dashboard.app import status_service
    
    try:
        status = status_service.get_system_status()
        return jsonify(status)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}", status_code=400)


@status_bp.route('/api')
@handle_errors
def get_api_status():
    """Get Forge API connection status."""
    from web_dashboard.app import status_service
    
    try:
        status = status_service.get_api_status()
        return jsonify(status)
    except Exception as e:
        return create_error_response(f"Failed to check API status: {str(e)}", status_code=400)


@status_bp.route('/current-api')
@handle_errors
def get_current_api_status():
    """Get current API connection status."""
    from web_dashboard.app import status_service
    
    try:
        status = status_service.get_current_api_status()
        return jsonify(status)
    except Exception as e:
        return create_error_response(f"Error getting current API status: {str(e)}", status_code=500)


# SocketIO event handlers
def handle_status_request(socketio, status_service):
    """Handle status request for SocketIO."""
    try:
        status = status_service.get_socketio_status()
        socketio.emit('status_update', status)
    except Exception as e:
        socketio.emit('error', {'message': str(e)})


def handle_connect(socketio):
    """Handle client connection."""
    socketio.emit('connected', {'message': 'Connected to server'})


def handle_disconnect(socketio):
    """Handle client disconnection."""
    # No specific action needed for disconnect
    pass 