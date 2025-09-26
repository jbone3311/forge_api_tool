#!/usr/bin/env python3
"""
Configuration Routes

Routes for configuration management functionality.
"""

from flask import Blueprint, request, jsonify, send_from_directory
from core.centralized_logger import logger

config_bp = Blueprint('config', __name__)


@config_bp.route('/api/configs')
def get_all_configs():
    """Get all configurations."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        configs = config_service.get_all_configs()
        
        return jsonify({
            'configs': configs,
            'count': len(configs)
        })
        
    except Exception as e:
        logger.error(f"Error getting all configs: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/list')
def get_config_list():
    """Get configuration list."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        configs = config_service.get_config_list()
        
        return jsonify({
            'configs': configs,
            'count': len(configs)
        })
        
    except Exception as e:
        logger.error(f"Error getting config list: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>')
def get_config(config_name):
    """Get a specific configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        config = config_service.get_config(config_name)
        
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"Error getting config {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>', methods=['PUT'])
def update_config(config_name):
    """Update a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update configuration
        success = config_service.save_config(config_name, data)
        
        if success:
            return jsonify({'message': 'Configuration updated successfully'})
        else:
            return jsonify({'error': 'Failed to update configuration'}), 500
        
    except Exception as e:
        logger.error(f"Error updating config {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    """Delete a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config handler directly for file operations
        config_handler = app_context.get_config_handler()
        
        # Delete configuration file
        import os
        config_path = os.path.join(config_handler.config_dir, f"{config_name}.json")
        
        if os.path.exists(config_path):
            os.remove(config_path)
            return jsonify({'message': 'Configuration deleted successfully'})
        else:
            return jsonify({'error': 'Configuration not found'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting config {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>/thumbnail')
def get_config_thumbnail(config_name):
    """Get configuration thumbnail."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        thumbnail_path = config_service.get_config_thumbnail(config_name)
        
        if not thumbnail_path:
            return jsonify({'error': 'Thumbnail not found'}), 404
        
        # Send file
        import os
        thumbnail_dir = os.path.dirname(thumbnail_path)
        thumbnail_filename = os.path.basename(thumbnail_path)
        
        return send_from_directory(thumbnail_dir, thumbnail_filename)
        
    except Exception as e:
        logger.error(f"Error getting thumbnail for {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>/validate')
def validate_config(config_name):
    """Validate a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        validation_result = config_service.validate_config(config_name)
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error validating config {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/<config_name>/export')
def export_config(config_name):
    """Export a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Create temporary export file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        success = config_service.export_config(config_name, temp_path)
        
        if success:
            return send_from_directory(
                os.path.dirname(temp_path),
                os.path.basename(temp_path),
                as_attachment=True,
                download_name=f"{config_name}.json"
            )
        else:
            return jsonify({'error': 'Failed to export configuration'}), 500
        
    except Exception as e:
        logger.error(f"Error exporting config {config_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/import', methods=['POST'])
def import_config():
    """Import a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get config name from form data or use filename
        config_name = request.form.get('config_name')
        if not config_name:
            config_name = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.json', delete=False) as f:
            file.save(f.name)
            temp_path = f.name
        
        # Import configuration
        success = config_service.import_config(temp_path, config_name)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        if success:
            return jsonify({'message': f'Configuration "{config_name}" imported successfully'})
        else:
            return jsonify({'error': 'Failed to import configuration'}), 500
        
    except Exception as e:
        logger.error(f"Error importing config: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/search')
def search_configs():
    """Search configurations."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        matching_configs = config_service.search_configs(query)
        
        return jsonify({
            'configs': matching_configs,
            'query': query,
            'count': len(matching_configs)
        })
        
    except Exception as e:
        logger.error(f"Error searching configs: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/stats')
def get_config_stats():
    """Get configuration statistics."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        stats = config_service.get_config_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting config stats: {e}")
        return jsonify({'error': str(e)}), 500


