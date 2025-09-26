#!/usr/bin/env python3
"""
Generation Routes

Routes for image generation functionality.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
from core.centralized_logger import logger

generation_bp = Blueprint('generation', __name__)


@generation_bp.route('/api/generate', methods=['POST'])
def generate_image():
    """Generate an image."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['config_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create generation job
        job_id = generation_service.create_generation_job(data)
        
        return jsonify({
            'job_id': job_id,
            'message': 'Generation job created successfully',
            'status': 'pending'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_image: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/generate/preview', methods=['POST'])
def preview_generation():
    """Preview generation without actually generating."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data or 'config_name' not in data:
            return jsonify({'error': 'Config name required'}), 400
        
        config_name = data['config_name']
        count = data.get('count', 5)
        
        # Get preview prompts
        preview_prompts = generation_service.preview_prompt(config_name, count)
        
        return jsonify({
            'config_name': config_name,
            'preview_prompts': preview_prompts,
            'count': len(preview_prompts)
        })
        
    except Exception as e:
        logger.error(f"Error in preview_generation: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/generate/validate', methods=['POST'])
def validate_generation():
    """Validate generation parameters."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data or 'config_name' not in data:
            return jsonify({'error': 'Config name required'}), 400
        
        config_name = data['config_name']
        
        # Validate configuration
        validation_result = generation_service.validate_config(config_name)
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error in validate_generation: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/jobs/active')
def get_active_jobs():
    """Get all active jobs."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        active_jobs = generation_service.get_active_jobs()
        
        return jsonify({
            'active_jobs': active_jobs,
            'count': len(active_jobs)
        })
        
    except Exception as e:
        logger.error(f"Error getting active jobs: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/jobs/<int:job_id>/status')
def get_job_status(job_id):
    """Get job status."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        job_status = generation_service.get_job_status(job_id)
        
        if not job_status:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job_status)
        
    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return jsonify({'error': str(e)}), 500


# Socket.IO events for real-time updates
def register_socketio_events(socketio, app_context):
    """Register Socket.IO events for generation."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        try:
            connection_id = request.sid
            app_context.add_connection(connection_id)
            
            logger.info(f"Client connected to clean app: {connection_id}")
            emit('connected', {
                'message': 'Connected to Forge API Tool',
                'connection_id': connection_id,
                'app_info': app_context.get_app_info()
            })
            
        except Exception as e:
            logger.error(f"Error in connect handler: {e}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        try:
            connection_id = request.sid
            app_context.remove_connection(connection_id)
            
            logger.info(f"Client disconnected from clean app: {connection_id}")
            
        except Exception as e:
            logger.error(f"Error in disconnect handler: {e}")
    
    @socketio.on('request_job_status')
    def handle_job_status_request(data):
        """Handle job status request."""
        try:
            job_id = data.get('job_id')
            if not job_id:
                emit('error', {'message': 'Job ID required'})
                return
            
            # Get generation service
            generation_service = app_context.get_component('generation_service')
            if generation_service:
                job_status = generation_service.get_job_status(job_id)
                if job_status:
                    emit('job_status_update', job_status)
                else:
                    emit('error', {'message': 'Job not found'})
            else:
                emit('error', {'message': 'Generation service not available'})
                
        except Exception as e:
            logger.error(f"Error in job status request: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('request_active_jobs')
    def handle_active_jobs_request():
        """Handle active jobs request."""
        try:
            # Get generation service
            generation_service = app_context.get_component('generation_service')
            if generation_service:
                active_jobs = generation_service.get_active_jobs()
                emit('active_jobs_update', {
                    'jobs': active_jobs,
                    'count': len(active_jobs)
                })
            else:
                emit('error', {'message': 'Generation service not available'})
                
        except Exception as e:
            logger.error(f"Error in active jobs request: {e}")
            emit('error', {'message': str(e)})
    
    @socketio.on('request_app_status')
    def handle_app_status_request():
        """Handle app status request."""
        try:
            emit('app_status_update', app_context.get_app_info())
            
        except Exception as e:
            logger.error(f"Error in app status request: {e}")
            emit('error', {'message': str(e)})


