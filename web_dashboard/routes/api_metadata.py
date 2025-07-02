"""
API Metadata routes for the Flask application.
"""

from flask import Blueprint, request, jsonify
from web_dashboard.services.api_metadata_service import APIMetadataService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response

# Create blueprint
api_metadata_bp = Blueprint('api_metadata', __name__, url_prefix='/api')

# Initialize the service
api_metadata_service = APIMetadataService()


@api_metadata_bp.route('/models', methods=['GET'])
@handle_errors
def get_models():
    """Get available models from the API."""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    result = api_metadata_service.get_models(force_refresh=force_refresh)
    return jsonify(result)


@api_metadata_bp.route('/samplers', methods=['GET'])
@handle_errors
def get_samplers():
    """Get available samplers from the API."""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    result = api_metadata_service.get_samplers(force_refresh=force_refresh)
    return jsonify(result)


@api_metadata_bp.route('/options', methods=['GET'])
@handle_errors
def get_options():
    """Get available options from the API."""
    force_refresh = request.args.get('refresh', 'false').lower() == 'true'
    result = api_metadata_service.get_options(force_refresh=force_refresh)
    return jsonify(result)


@api_metadata_bp.route('/refresh-metadata', methods=['POST'])
@handle_errors
def refresh_metadata():
    """Refresh all metadata from the API."""
    result = api_metadata_service.refresh_all_metadata()
    return jsonify(result)


@api_metadata_bp.route('/metadata-status', methods=['GET'])
@handle_errors
def get_metadata_status():
    """Get the current status of metadata cache."""
    result = api_metadata_service.get_metadata_status()
    return jsonify(result)


@api_metadata_bp.route('/clear-cache', methods=['DELETE'])
@handle_errors
def clear_cache():
    """Clear metadata cache."""
    data = request.get_json() or {}
    metadata_type = data.get('metadata_type')  # Optional: models, samplers, options, or None for all
    
    result = api_metadata_service.clear_cache(metadata_type=metadata_type)
    return jsonify(result) 