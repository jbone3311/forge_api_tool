#!/usr/bin/env python3
"""
Configuration Routes

Routes for configuration management functionality.
"""

from flask import Blueprint, request, jsonify, send_from_directory
from core.centralized_logger import logger
from core.config_templates import get_config_templates
from core.config_validator import get_config_validator

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


@config_bp.route('/api/settings/<config_name>/thumbnail')
def get_config_thumbnail_image(config_name):
    """Get thumbnail for a configuration."""
    try:
        from flask import g, send_file, Response
        import io
        from PIL import Image, ImageDraw, ImageFont
        import hashlib
        
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Try to get the configuration
        config = config_service.get_config(config_name)
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Generate a simple thumbnail based on config name
        # Create a 200x200 image with a gradient background
        img = Image.new('RGB', (200, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Create gradient background based on config name hash
        config_hash = hashlib.md5(config_name.encode()).hexdigest()
        colors = [
            f'#{config_hash[0:6]}',
            f'#{config_hash[6:12]}',
            f'#{config_hash[12:18]}',
            f'#{config_hash[18:24]}'
        ]
        
        # Draw gradient rectangles
        for i, color in enumerate(colors):
            y_start = i * 50
            y_end = (i + 1) * 50
            draw.rectangle([0, y_start, 200, y_end], fill=color)
        
        # Add text overlay
        try:
            # Try to use a system font
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw config name
        text = config_name.replace('_', ' ').title()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2
        
        # Draw text with outline for visibility
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill='black')
        
        draw.text((x, y), text, font=font, fill='white')
        
        # Convert to bytes
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        return send_file(img_byte_array, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error generating thumbnail for {config_name}: {e}")
        # Return a simple placeholder
        img = Image.new('RGB', (200, 200), color='#cccccc')
        draw = ImageDraw.Draw(img)
        draw.text((50, 90), config_name[:20], fill='black')
        
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        return send_file(img_byte_array, mimetype='image/png')


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


# Template endpoints
@config_bp.route('/api/templates')
def get_templates():
    """Get all configuration templates."""
    try:
        templates = get_config_templates()
        
        return jsonify({
            'templates': templates.get_all_templates(),
            'categories': templates.get_categories(),
            'count': len(templates.get_all_templates())
        })
        
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/templates/<template_name>')
def get_template(template_name):
    """Get a specific template."""
    try:
        templates = get_config_templates()
        template = templates.get_template(template_name)
        
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template)
        
    except Exception as e:
        logger.error(f"Error getting template {template_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/templates/category/<category>')
def get_templates_by_category(category):
    """Get templates by category."""
    try:
        templates = get_config_templates()
        
        return jsonify({
            'templates': templates.get_templates_by_category(category),
            'category': category,
            'count': len(templates.get_templates_by_category(category))
        })
        
    except Exception as e:
        logger.error(f"Error getting templates by category {category}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/templates/search')
def search_templates():
    """Search templates."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        templates = get_config_templates()
        results = templates.search_templates(query)
        
        return jsonify({
            'templates': results,
            'query': query,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching templates: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/templates/<template_name>/create-config', methods=['POST'])
def create_config_from_template(template_name):
    """Create a configuration from a template."""
    try:
        from flask import g
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Get custom parameters
        custom_params = request.get_json() or {}
        
        # Create config from template
        templates = get_config_templates()
        config = templates.create_config_from_template(template_name, custom_params)
        
        # Get config name
        config_name = custom_params.get('config_name', f"{template_name}_config")
        
        # Save the configuration
        success = config_service.save_config(config_name, config)
        
        if success:
            return jsonify({
                'message': f'Configuration "{config_name}" created from template "{template_name}"',
                'config_name': config_name,
                'config': config
            })
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
        
    except Exception as e:
        logger.error(f"Error creating config from template {template_name}: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/templates/suggest', methods=['POST'])
def suggest_templates():
    """Suggest templates based on current configuration."""
    try:
        # Get current configuration from request
        current_config = request.get_json()
        if not current_config:
            return jsonify({'error': 'Current configuration required'}), 400
        
        templates = get_config_templates()
        suggestions = templates.get_template_suggestions(current_config)
        
        return jsonify({
            'suggestions': suggestions,
            'count': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error getting template suggestions: {e}")
        return jsonify({'error': str(e)}), 500


# Validation endpoints
@config_bp.route('/api/configs/validate', methods=['POST'])
def validate_configuration():
    """Validate a configuration."""
    try:
        from flask import g
        app_context = g.app_context
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Configuration data is required'}), 400
        
        config = data.get('config', {})
        api_provider = data.get('api_provider', 'local')
        
        validator = get_config_validator()
        validation_summary = validator.get_validation_summary(config, api_provider)
        
        return jsonify(validation_summary)
        
    except Exception as e:
        logger.error(f"Error validating configuration: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/validate-parameter', methods=['POST'])
def validate_parameter():
    """Validate a single parameter."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Parameter data is required'}), 400
        
        param_name = data.get('param_name')
        value = data.get('value')
        api_provider = data.get('api_provider', 'local')
        
        if not param_name:
            return jsonify({'error': 'param_name is required'}), 400
        
        validator = get_config_validator()
        result = validator.validate_parameter(param_name, value, api_provider)
        
        return jsonify(result.to_dict())
        
    except Exception as e:
        logger.error(f"Error validating parameter: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/parameter-suggestions', methods=['POST'])
def get_parameter_suggestions():
    """Get suggestions for a parameter."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Parameter data is required'}), 400
        
        param_name = data.get('param_name')
        current_value = data.get('current_value')
        api_provider = data.get('api_provider', 'local')
        
        if not param_name:
            return jsonify({'error': 'param_name is required'}), 400
        
        validator = get_config_validator()
        suggestions = validator.get_parameter_suggestions(param_name, current_value, api_provider)
        
        return jsonify(suggestions)
        
    except Exception as e:
        logger.error(f"Error getting parameter suggestions: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/validate-prompt', methods=['POST'])
def validate_prompt():
    """Validate a prompt."""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'prompt is required'}), 400
        
        prompt = data['prompt']
        validator = get_config_validator()
        result = validator.validate_prompt(prompt)
        
        return jsonify(result.to_dict())
        
    except Exception as e:
        logger.error(f"Error validating prompt: {e}")
        return jsonify({'error': str(e)}), 500


# Enhanced Export/Import endpoints
@config_bp.route('/api/configs/export-all', methods=['POST'])
def export_all_configs():
    """Export all configurations as a zip file."""
    try:
        from flask import g
        import zipfile
        import tempfile
        import os
        import json
        import time
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Get all configs
        configs = config_service.get_all_configs()
        if not configs:
            return jsonify({'error': 'No configurations to export'}), 400
        
        # Create zip file
        temp_zip = tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False)
        temp_zip_path = temp_zip.name
        temp_zip.close()
        
        with zipfile.ZipFile(temp_zip_path, 'w') as zip_file:
            for config_name, config_data in configs.items():
                # Create individual config file
                config_json = json.dumps(config_data, indent=2)
                zip_file.writestr(f"{config_name}.json", config_json)
        
        # Create metadata file
        metadata = {
            'export_date': time.time(),
            'total_configs': len(configs),
            'config_names': list(configs.keys()),
            'version': '1.0'
        }
        
        with zipfile.ZipFile(temp_zip_path, 'a') as zip_file:
            zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        return send_from_directory(
            os.path.dirname(temp_zip_path),
            os.path.basename(temp_zip_path),
            as_attachment=True,
            download_name=f"forge_configs_export_{int(time.time())}.zip"
        )
        
    except Exception as e:
        logger.error(f"Error exporting all configs: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/configs/import-zip', methods=['POST'])
def import_configs_zip():
    """Import configurations from a zip file."""
    try:
        from flask import g
        import zipfile
        import tempfile
        import os
        import json
        app_context = g.app_context
        
        # Get config service
        config_service = app_context.get_component('config_service')
        if not config_service:
            return jsonify({'error': 'Config service not available'}), 500
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No zip file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.zip'):
            return jsonify({'error': 'File must be a zip archive'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False) as f:
            file.save(f.name)
            temp_zip_path = f.name
        
        imported_configs = []
        errors = []
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_file:
                # Read metadata if available
                metadata = None
                if 'metadata.json' in zip_file.namelist():
                    try:
                        metadata_content = zip_file.read('metadata.json').decode('utf-8')
                        metadata = json.loads(metadata_content)
                    except Exception as e:
                        errors.append(f"Could not read metadata: {e}")
                
                # Import each config file
                for filename in zip_file.namelist():
                    if filename.endswith('.json') and filename != 'metadata.json':
                        try:
                            config_content = zip_file.read(filename).decode('utf-8')
                            config_data = json.loads(config_content)
                            
                            # Extract config name from filename
                            config_name = filename[:-5]  # Remove .json extension
                            
                            # Save configuration
                            success = config_service.save_config(config_name, config_data)
                            if success:
                                imported_configs.append(config_name)
                            else:
                                errors.append(f"Failed to save config: {config_name}")
                        
                        except Exception as e:
                            errors.append(f"Error importing {filename}: {e}")
        
        finally:
            # Clean up temporary file
            os.unlink(temp_zip_path)
        
        return jsonify({
            'message': f'Import completed. {len(imported_configs)} configs imported successfully.',
            'imported_configs': imported_configs,
            'errors': errors,
            'total_imported': len(imported_configs),
            'total_errors': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Error importing configs from zip: {e}")
        return jsonify({'error': str(e)}), 500


