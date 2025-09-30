#!/usr/bin/env python3
"""
Generation Routes

Routes for image generation functionality.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import emit
from core.centralized_logger import logger

generation_bp = Blueprint('generation', __name__)


@generation_bp.route('/api/wildcards/process', methods=['POST'])
def process_wildcards():
    """Process wildcards in a prompt."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get request data
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt']
        iterations = data.get('iterations', 1)
        
        # Get prompt builder
        prompt_builder = app_context.get_prompt_builder()
        if not prompt_builder:
            return jsonify({'error': 'Prompt builder not available'}), 500
        
        # Process wildcards
        processed_prompts = []
        for i in range(iterations):
            processed_prompt = prompt_builder.build_prompt(prompt)
            processed_prompts.append({
                'iteration': i + 1,
                'prompt': processed_prompt,
                'wildcards_used': prompt_builder.get_last_wildcards_used()
            })
        
        return jsonify({
            'success': True,
            'original_prompt': prompt,
            'iterations': iterations,
            'processed_prompts': processed_prompts
        })
        
    except Exception as e:
        logger.error(f"Error processing wildcards: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/wildcards/preview', methods=['POST'])
def preview_wildcards():
    """Preview wildcard expansion for a prompt."""
    try:
        from flask import g
        import re
        app_context = g.app_context
        
        # Get request data
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt']
        max_previews = data.get('max_previews', 3)
        
        # Get prompt builder
        prompt_builder = app_context.get_prompt_builder()
        if not prompt_builder:
            return jsonify({'error': 'Prompt builder not available'}), 500
        
        # Find wildcards in the prompt
        wildcard_pattern = r'\{([^}]+)\}'
        wildcards_found = re.findall(wildcard_pattern, prompt)
        
        # Get wildcard info
        wildcard_info = {}
        for wildcard_name in wildcards_found:
            try:
                items = prompt_builder.wildcard_manager.get_wildcard_items(wildcard_name)
                wildcard_info[wildcard_name] = {
                    'available': True,
                    'item_count': len(items),
                    'sample_items': items[:5]  # Show first 5 items as examples
                }
            except Exception:
                wildcard_info[wildcard_name] = {
                    'available': False,
                    'item_count': 0,
                    'sample_items': []
                }
        
        # Generate preview expansions
        previews = []
        for i in range(min(max_previews, 5)):
            try:
                preview_prompt = prompt_builder.build_prompt(prompt)
                previews.append({
                    'preview_id': i + 1,
                    'prompt': preview_prompt,
                    'wildcards_used': prompt_builder.get_last_wildcards_used()
                })
            except Exception as e:
                logger.warning(f"Error generating preview {i + 1}: {e}")
                break
        
        return jsonify({
            'success': True,
            'original_prompt': prompt,
            'wildcards_found': wildcards_found,
            'wildcard_info': wildcard_info,
            'previews': previews
        })
        
    except Exception as e:
        logger.error(f"Error previewing wildcards: {e}")
        return jsonify({'error': str(e)}), 500


@generation_bp.route('/api/wildcards/suggest', methods=['GET'])
def suggest_wildcards():
    """Get wildcard suggestions for autocomplete."""
    try:
        from flask import g, request
        app_context = g.app_context
        
        query = request.args.get('q', '').lower()
        limit = int(request.args.get('limit', 10))
        
        # Get prompt builder
        prompt_builder = app_context.get_prompt_builder()
        if not prompt_builder:
            return jsonify({'error': 'Prompt builder not available'}), 500
        
        # Get all available wildcards
        all_wildcards = prompt_builder.wildcard_manager.get_available_wildcards()
        
        # Filter and rank suggestions
        suggestions = []
        for wildcard_name in all_wildcards:
            if query in wildcard_name.lower():
                try:
                    items = prompt_builder.wildcard_manager.get_wildcard_items(wildcard_name)
                    suggestions.append({
                        'name': wildcard_name,
                        'item_count': len(items),
                        'sample_items': items[:3]  # Show first 3 items
                    })
                except Exception:
                    suggestions.append({
                        'name': wildcard_name,
                        'item_count': 0,
                        'sample_items': []
                    })
        
        # Sort by relevance (exact matches first, then by length)
        suggestions.sort(key=lambda x: (
            not x['name'].lower().startswith(query),  # Exact matches first
            len(x['name'])  # Shorter names first
        ))
        
        return jsonify({
            'suggestions': suggestions[:limit],
            'query': query,
            'total_found': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error getting wildcard suggestions: {e}")
        return jsonify({'error': str(e)}), 500


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


