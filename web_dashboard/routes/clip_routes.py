#!/usr/bin/env python3
"""
CLIP Routes

Flask routes for CLIP Interrogator image processing.
"""

from flask import Blueprint, render_template, request, jsonify, send_file
from flask import g
from core.centralized_logger import logger
from pathlib import Path

clip_bp = Blueprint('clip', __name__, url_prefix='/clip')


@clip_bp.route('/')
def clip_dashboard():
    """Main CLIP processing dashboard."""
    try:
        app_context = g.app_context
        
        # Get CLIP service
        clip_service = app_context.get_component('clip_service')
        if not clip_service:
            from web_dashboard.services.clip_service import CLIPService
            clip_service = CLIPService(app_context)
            app_context.set_component('clip_service', clip_service)
        
        # Get stats
        stats = clip_service.get_stats()
        
        # Get list of generated wildcards
        wildcards = clip_service.get_generated_wildcards()
        
        # Get available modes
        modes = clip_service.get_available_modes()
        
        return render_template('clip_dashboard.html',
                             stats=stats,
                             wildcards=wildcards,
                             modes=modes)
    
    except Exception as e:
        logger.error(f"Error in CLIP dashboard: {e}")
        return render_template('clip_dashboard.html',
                             stats={},
                             wildcards=[],
                             modes=[])


@clip_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """Test connection to CLIP API."""
    try:
        app_context = g.app_context
        clip_service = app_context.get_component('clip_service')
        
        if not clip_service:
            from web_dashboard.services.clip_service import CLIPService
            clip_service = CLIPService(app_context)
            app_context.set_component('clip_service', clip_service)
        
        result = clip_service.test_connection()
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error testing CLIP connection: {e}")
        return jsonify({
            'connected': False,
            'error': str(e)
        }), 500


@clip_bp.route('/process', methods=['POST'])
def process_images():
    """Process images through CLIP Interrogator."""
    try:
        app_context = g.app_context
        clip_service = app_context.get_component('clip_service')
        
        if not clip_service:
            from web_dashboard.services.clip_service import CLIPService
            clip_service = CLIPService(app_context)
            app_context.set_component('clip_service', clip_service)
        
        # Get parameters
        data = request.get_json()
        input_dir = data.get('input_dir')
        modes = data.get('modes', [])
        theme_name = data.get('theme_name')
        recursive = data.get('recursive', True)
        
        if not input_dir:
            return jsonify({
                'success': False,
                'error': 'No input directory specified'
            }), 400
        
        # Validate directory exists
        if not Path(input_dir).exists():
            return jsonify({
                'success': False,
                'error': f'Directory not found: {input_dir}'
            }), 400
        
        # Process directory
        results = clip_service.process_directory(
            input_dir=input_dir,
            modes=modes if modes else None,
            theme_name=theme_name,
            recursive=recursive
        )
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Error processing images: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@clip_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get CLIP processing statistics."""
    try:
        app_context = g.app_context
        clip_service = app_context.get_component('clip_service')
        
        if not clip_service:
            from web_dashboard.services.clip_service import CLIPService
            clip_service = CLIPService(app_context)
            app_context.set_component('clip_service', clip_service)
        
        stats = clip_service.get_stats()
        return jsonify(stats)
    
    except Exception as e:
        logger.error(f"Error getting CLIP stats: {e}")
        return jsonify({'error': str(e)}), 500


@clip_bp.route('/wildcards', methods=['GET'])
def list_wildcards():
    """List generated wildcard files."""
    try:
        app_context = g.app_context
        clip_service = app_context.get_component('clip_service')
        
        if not clip_service:
            from web_dashboard.services.clip_service import CLIPService
            clip_service = CLIPService(app_context)
            app_context.set_component('clip_service', clip_service)
        
        wildcards = clip_service.get_generated_wildcards()
        return jsonify({'wildcards': wildcards})
    
    except Exception as e:
        logger.error(f"Error listing wildcards: {e}")
        return jsonify({'error': str(e)}), 500


@clip_bp.route('/wildcards/<path:filename>', methods=['GET'])
def download_wildcard(filename):
    """Download a wildcard file."""
    try:
        app_context = g.app_context
        clip_service = app_context.get_component('clip_service')
        
        if not clip_service:
            return jsonify({'error': 'CLIP service not available'}), 500
        
        # Find the wildcard file
        output_dir = Path(clip_service.processor.output_dir)
        file_path = output_dir / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(str(file_path), as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error downloading wildcard: {e}")
        return jsonify({'error': str(e)}), 500


@clip_bp.route('/job/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status of a CLIP processing job."""
    try:
        app_context = g.app_context
        job = app_context.get_job(job_id)
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(job)
    
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return jsonify({'error': str(e)}), 500
