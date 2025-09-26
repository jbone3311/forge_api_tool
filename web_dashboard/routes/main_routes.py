#!/usr/bin/env python3
"""
Main Routes

Main application routes for the web dashboard.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_socketio import emit
from core.centralized_logger import logger

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def dashboard():
    """Main dashboard route."""
    try:
        # Get app context from Flask's g object (set by app factory)
        from flask import g
        app_context = g.app_context
        
        # Get configuration handler for settings
        config_handler = app_context.get_config_handler()
        image_settings = config_handler.get_all_configs()
        
        # Get app info
        app_info = app_context.get_app_info()
        
        # Get output statistics
        output_manager = app_context.get_output_manager()
        output_stats = output_manager.get_output_statistics()
        
        # Get wildcard information
        prompt_builder = app_context.get_prompt_builder()
        wildcard_info = prompt_builder.get_wildcard_info()
        available_wildcards = list(wildcard_info.keys())
        
        logger.info("Clean app dashboard accessed")
        
        return render_template('clean_dashboard.html', 
                             configs=image_settings, 
                             app_info=app_info,
                             api_info=app_info,
                             output_stats=output_stats,
                             available_wildcards=available_wildcards,
                             wildcard_info=wildcard_info)
        
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}")
        return render_template('clean_dashboard.html', 
                             configs={}, 
                             app_info={},
                             api_info={},
                             output_stats={'total_outputs': 0},
                             available_wildcards=[],
                             wildcard_info={})


@main_bp.route('/api/status')
def api_status():
    """API status endpoint."""
    try:
        from flask import g
        app_context = g.app_context
        
        api_client = app_context.get_api_client()
        
        # Test connection
        connection_status = api_client.test_connection(silent=True)
        
        return jsonify({
            'status': 'connected' if connection_status else 'disconnected',
            'api_type': app_context.state['current_api_type'],
            'connection_test': connection_status
        })
        
    except Exception as e:
        logger.error(f"Error in status API: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@main_bp.route('/api/app/info')
def app_info():
    """Application information endpoint."""
    try:
        from flask import g
        app_context = g.app_context
        
        return jsonify(app_context.get_app_info())
        
    except Exception as e:
        logger.error(f"Error getting app info: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/jobs')
def get_jobs():
    """Get all jobs."""
    try:
        from flask import g
        app_context = g.app_context
        
        jobs = app_context.get_all_jobs()
        return jsonify(jobs)
        
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/jobs/<int:job_id>')
def get_job(job_id):
    """Get a specific job."""
    try:
        from flask import g
        app_context = g.app_context
        
        job = app_context.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job)
        
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/jobs/<int:job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a job."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get generation service
        generation_service = app_context.get_component('generation_service')
        if not generation_service:
            return jsonify({'error': 'Generation service not available'}), 500
        
        success = generation_service.cancel_job(job_id)
        
        if success:
            return jsonify({'message': 'Job cancelled successfully'})
        else:
            return jsonify({'error': 'Could not cancel job'}), 400
        
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Basic health checks
        config_handler = app_context.get_config_handler()
        api_client = app_context.get_api_client()
        
        # Test components
        configs_ok = len(config_handler.list_configs()) >= 0
        api_ok = api_client.test_connection(silent=True)
        
        health_status = {
            'status': 'healthy' if configs_ok and api_ok else 'degraded',
            'components': {
                'config_handler': configs_ok,
                'api_client': api_ok
            },
            'timestamp': app_context.state['startup_time']
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


