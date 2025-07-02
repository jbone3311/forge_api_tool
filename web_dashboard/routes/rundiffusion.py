"""
RunDiffusion routes for the Flask application.
"""
from flask import Blueprint, request, jsonify
from web_dashboard.services.rundiffusion_service import RunDiffusionService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response

rundiffusion_bp = Blueprint('rundiffusion', __name__, url_prefix='/api/rundiffusion')

# Initialize the service (could be injected in app factory)
rundiffusion_service = RunDiffusionService()

@rundiffusion_bp.route('/config', methods=['GET'])
@handle_errors
def get_rundiffusion_config():
    return jsonify(rundiffusion_service.get_config())

@rundiffusion_bp.route('/config', methods=['POST'])
@handle_errors
def save_rundiffusion_config():
    config = request.get_json()
    return jsonify(rundiffusion_service.save_config(config))

@rundiffusion_bp.route('/test', methods=['POST'])
@handle_errors
def test_rundiffusion_connection():
    config = request.get_json()
    return jsonify(rundiffusion_service.test_connection(config))

@rundiffusion_bp.route('/disable', methods=['POST'])
@handle_errors
def disable_rundiffusion():
    return jsonify(rundiffusion_service.disable()) 