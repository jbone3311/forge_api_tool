"""
Generation routes for the Flask web dashboard.

This module contains route handlers for image generation operations,
using the Generation Service for business logic.
"""

from flask import Blueprint, request, jsonify
from services.generation_service import GenerationService
from core.exceptions import (
    ConfigurationError, GenerationError, ValidationError, 
    JobQueueError
)
from utils.response_helpers import error_response, success_response
from utils.decorators import handle_errors

# Create blueprint
generation_bp = Blueprint('generation', __name__)

# Service instance (will be initialized in app.py)
generation_service = None


def init_generation_service(service_instance):
    """Initialize the generation service instance."""
    global generation_service
    generation_service = service_instance


@generation_bp.route('/api/generate', methods=['POST'])
@handle_errors
def generate_image():
    """Generate a single image."""
    data = request.get_json()
    config_name = data.get('config_name')
    prompt = data.get('prompt', '')
    seed = data.get('seed')
    
    if not config_name:
        return error_response('Config name is required', 400)
    
    try:
        result = generation_service.generate_single_image(config_name, prompt, seed)
        return success_response(result)
    except ConfigurationError as e:
        return error_response(str(e), 404)
    except ValidationError as e:
        return error_response(str(e), 400)
    except GenerationError as e:
        return error_response(str(e), 400)


@generation_bp.route('/api/batch', methods=['POST'])
@handle_errors
def start_batch():
    """Start a batch generation job."""
    data = request.get_json()
    config_name = data.get('config_name')
    batch_size = data.get('batch_size', 1)
    num_batches = data.get('num_batches', 1)
    prompts = data.get('prompts', [])
    user_prompt = data.get('prompt', '')
    
    if not config_name:
        return error_response('Config name is required', 400)
    
    try:
        result = generation_service.start_batch_generation(
            config_name=config_name,
            batch_size=batch_size,
            num_batches=num_batches,
            prompts=prompts if prompts else None,
            user_prompt=user_prompt
        )
        return success_response(result)
    except ConfigurationError as e:
        return error_response(str(e), 404)
    except ValidationError as e:
        return error_response(str(e), 400)
    except JobQueueError as e:
        return error_response(str(e), 400)


@generation_bp.route('/api/batch/preview', methods=['POST'])
@handle_errors
def preview_batch():
    """Preview batch prompts without generating images."""
    data = request.get_json()
    config_name = data.get('config_name')
    batch_size = data.get('batch_size', 1)
    num_batches = data.get('num_batches', 1)
    user_prompt = data.get('prompt', '')
    
    if not config_name:
        return error_response('Config name is required', 400)
    
    try:
        result = generation_service.preview_batch_prompts(
            config_name=config_name,
            batch_size=batch_size,
            num_batches=num_batches,
            user_prompt=user_prompt
        )
        return success_response(result)
    except ConfigurationError as e:
        return error_response(str(e), 404)
    except ValidationError as e:
        return error_response(str(e), 400)


@generation_bp.route('/api/generation/stop', methods=['POST'])
@handle_errors
def stop_generation():
    """Stop the current generation."""
    try:
        result = generation_service.stop_generation()
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['message'], 400)
    except JobQueueError as e:
        return error_response(str(e), 400)


@generation_bp.route('/api/status/generation')
@handle_errors
def get_generation_status():
    """Get current generation status."""
    try:
        status = generation_service.get_generation_status()
        return success_response(status)
    except Exception as e:
        return error_response(str(e), 500) 