#!/usr/bin/env python3
"""
Batch Operations Routes

Routes for batch operations functionality.
"""

from flask import Blueprint, request, jsonify
from core.centralized_logger import logger
from core.batch_manager import get_batch_operations

batch_bp = Blueprint('batch', __name__)


@batch_bp.route('/api/batch/operations')
def get_batch_operations_list():
    """Get all batch operations."""
    try:
        batch_ops = get_batch_operations()
        operations = batch_ops.batch_manager.get_all_operations()
        
        return jsonify({
            'operations': operations,
            'count': len(operations)
        })
        
    except Exception as e:
        logger.error(f"Error getting batch operations: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/operations/<operation_id>')
def get_batch_operation(operation_id):
    """Get a specific batch operation."""
    try:
        batch_ops = get_batch_operations()
        operation = batch_ops.batch_manager.get_operation(operation_id)
        
        if not operation:
            return jsonify({'error': 'Operation not found'}), 404
        
        return jsonify(operation.get_summary())
        
    except Exception as e:
        logger.error(f"Error getting batch operation {operation_id}: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/operations/<operation_id>/results')
def get_batch_operation_results(operation_id):
    """Get results for a batch operation."""
    try:
        batch_ops = get_batch_operations()
        operation = batch_ops.batch_manager.get_operation(operation_id)
        
        if not operation:
            return jsonify({'error': 'Operation not found'}), 404
        
        return jsonify({
            'operation_id': operation_id,
            'results': operation.results,
            'errors': operation.errors,
            'summary': operation.get_summary()
        })
        
    except Exception as e:
        logger.error(f"Error getting batch operation results {operation_id}: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/operations/<operation_id>/cancel', methods=['POST'])
def cancel_batch_operation(operation_id):
    """Cancel a batch operation."""
    try:
        batch_ops = get_batch_operations()
        success = batch_ops.batch_manager.cancel_operation(operation_id)
        
        if success:
            return jsonify({'message': f'Operation {operation_id} cancelled successfully'})
        else:
            return jsonify({'error': 'Operation not found or cannot be cancelled'}), 400
        
    except Exception as e:
        logger.error(f"Error cancelling batch operation {operation_id}: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/operations/<operation_id>', methods=['DELETE'])
def delete_batch_operation(operation_id):
    """Delete a batch operation."""
    try:
        batch_ops = get_batch_operations()
        success = batch_ops.batch_manager.delete_operation(operation_id)
        
        if success:
            return jsonify({'message': f'Operation {operation_id} deleted successfully'})
        else:
            return jsonify({'error': 'Operation not found'}), 404
        
    except Exception as e:
        logger.error(f"Error deleting batch operation {operation_id}: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/export-configs', methods=['POST'])
def batch_export_configs():
    """Export multiple configurations."""
    try:
        from flask import g
        app_context = g.app_context
        
        data = request.get_json()
        if not data or 'config_names' not in data:
            return jsonify({'error': 'config_names is required'}), 400
        
        config_names = data['config_names']
        if not isinstance(config_names, list) or not config_names:
            return jsonify({'error': 'config_names must be a non-empty list'}), 400
        
        # Start batch export operation
        batch_ops = get_batch_operations()
        operation_id = batch_ops.batch_export_configs(config_names, "/tmp/exports")
        
        return jsonify({
            'message': 'Batch export started',
            'operation_id': operation_id,
            'total_configs': len(config_names)
        })
        
    except Exception as e:
        logger.error(f"Error starting batch export: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/import-configs', methods=['POST'])
def batch_import_configs():
    """Import multiple configuration files."""
    try:
        from flask import g
        app_context = g.app_context
        
        data = request.get_json()
        if not data or 'file_paths' not in data:
            return jsonify({'error': 'file_paths is required'}), 400
        
        file_paths = data['file_paths']
        if not isinstance(file_paths, list) or not file_paths:
            return jsonify({'error': 'file_paths must be a non-empty list'}), 400
        
        # Start batch import operation
        batch_ops = get_batch_operations()
        operation_id = batch_ops.batch_import_configs(file_paths)
        
        return jsonify({
            'message': 'Batch import started',
            'operation_id': operation_id,
            'total_files': len(file_paths)
        })
        
    except Exception as e:
        logger.error(f"Error starting batch import: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/process-wildcards', methods=['POST'])
def batch_process_wildcards():
    """Process multiple wildcard files."""
    try:
        from flask import g
        app_context = g.app_context
        
        data = request.get_json()
        if not data or 'wildcard_files' not in data:
            return jsonify({'error': 'wildcard_files is required'}), 400
        
        wildcard_files = data['wildcard_files']
        if not isinstance(wildcard_files, list) or not wildcard_files:
            return jsonify({'error': 'wildcard_files must be a non-empty list'}), 400
        
        # Start batch wildcard processing operation
        batch_ops = get_batch_operations()
        operation_id = batch_ops.batch_process_wildcards(wildcard_files)
        
        return jsonify({
            'message': 'Batch wildcard processing started',
            'operation_id': operation_id,
            'total_files': len(wildcard_files)
        })
        
    except Exception as e:
        logger.error(f"Error starting batch wildcard processing: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/generate-images', methods=['POST'])
def batch_generate_images():
    """Generate multiple images from prompts."""
    try:
        from flask import g
        app_context = g.app_context
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        prompts = data.get('prompts', [])
        config_name = data.get('config_name', 'default')
        
        if not isinstance(prompts, list) or not prompts:
            return jsonify({'error': 'prompts must be a non-empty list'}), 400
        
        # Start batch image generation operation
        batch_ops = get_batch_operations()
        operation_id = batch_ops.batch_generate_images(prompts, config_name)
        
        return jsonify({
            'message': 'Batch image generation started',
            'operation_id': operation_id,
            'total_prompts': len(prompts),
            'config_name': config_name
        })
        
    except Exception as e:
        logger.error(f"Error starting batch image generation: {e}")
        return jsonify({'error': str(e)}), 500


@batch_bp.route('/api/batch/cleanup', methods=['POST'])
def cleanup_batch_operations():
    """Clean up old batch operations."""
    try:
        data = request.get_json() or {}
        older_than_hours = data.get('older_than_hours', 24)
        
        batch_ops = get_batch_operations()
        deleted_count = batch_ops.batch_manager.cleanup_completed_operations(older_than_hours)
        
        return jsonify({
            'message': f'Cleaned up {deleted_count} old operations',
            'deleted_count': deleted_count,
            'older_than_hours': older_than_hours
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up batch operations: {e}")
        return jsonify({'error': str(e)}), 500

