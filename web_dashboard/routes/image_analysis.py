"""
Image Analysis routes for the Flask application.
"""

from flask import Blueprint, request, jsonify
from web_dashboard.services.image_analysis_service import ImageAnalysisService
from web_dashboard.utils.decorators import handle_errors
from web_dashboard.utils.response_helpers import create_error_response, create_success_response

# Create blueprint
image_analysis_bp = Blueprint('image_analysis', __name__, url_prefix='/api')

# Initialize the service
image_analysis_service = ImageAnalysisService()


@image_analysis_bp.route('/analyze-image', methods=['POST'])
@handle_errors
def analyze_image():
    """Analyze an uploaded image to extract generation settings."""
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify(create_error_response('No image data provided', status_code=400)), 400
    
    image_data = data['image_data']
    result = image_analysis_service.analyze_image(image_data)
    
    # Check if the service returned an error response
    if not result.get('success', True):
        status_code = 400  # Default error status code
        return jsonify(result), status_code
    
    return jsonify(result)


@image_analysis_bp.route('/extract-metadata', methods=['POST'])
@handle_errors
def extract_metadata():
    """Extract metadata from an image without full analysis."""
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify(create_error_response('No image data provided', status_code=400)), 400
    
    image_data = data['image_data']
    result = image_analysis_service.extract_image_metadata(image_data)
    return jsonify(result)


@image_analysis_bp.route('/validate-image', methods=['POST'])
@handle_errors
def validate_image():
    """Validate image format and basic properties."""
    data = request.get_json()
    if not data or 'image_data' not in data:
        return jsonify(create_error_response('No image data provided', status_code=400)), 400
    
    image_data = data['image_data']
    result = image_analysis_service.validate_image_format(image_data)
    return jsonify(result) 