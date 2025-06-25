#!/usr/bin/env python3
"""
Forge API Tool Web Dashboard

A Flask-based web interface for managing Forge API configurations,
generating images, and monitoring the system.
"""

import os
import json
import time
import threading
import webbrowser
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import sys

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_handler import config_handler
from core.forge_api import forge_api_client
from core.output_manager import output_manager
from core.centralized_logger import centralized_logger
from core.job_queue import job_queue
from core.batch_runner import batch_runner
from core.prompt_builder import PromptBuilder
from core.wildcard_manager import WildcardManagerFactory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
logger = centralized_logger

# Global state for tracking current generation
current_generation = {
    'active': False,
    'current_image': 0,
    'total_images': 0,
    'config_name': '',
    'start_time': None,
    'progress': 0.0
}

@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Debug: Log the current working directory and config handler path
        logger.info(f"Dashboard accessed - Current working directory: {os.getcwd()}")
        logger.info(f"Config handler config_dir: {config_handler.config_dir}")
        logger.info(f"Config directory exists: {os.path.exists(config_handler.config_dir)}")
        
        # Get configurations - ensure we're using the correct path
        configs = config_handler.get_all_configs()
        logger.info(f"Loaded {len(configs)} configurations")
        
        # Debug: Log each config that was loaded
        for config_name, config in configs.items():
            logger.info(f"Config loaded: {config_name} - {config.get('name', 'N/A')} ({config.get('model_type', 'N/A')})")
        
        # Fallback: If no configs loaded, try direct loading
        if not configs:
            logger.warning("No configs loaded via config handler, trying direct loading...")
            configs = load_templates_directly()
            logger.info(f"Direct loading found {len(configs)} configurations")
        
        # Get output statistics
        output_stats = output_manager.get_output_statistics()
        
        # Get queue status - use get_queue_stats instead of get_status
        try:
            queue_status = job_queue.get_queue_stats()
        except Exception as e:
            logger.warning(f"Failed to get queue stats: {e}")
            queue_status = {
                'total_jobs': 0,
                'pending_jobs': 0,
                'running_jobs': 0,
                'completed_jobs': 0,
                'failed_jobs': 0,
                'total_images': 0,
                'completed_images': 0,
                'failed_images': 0,
                'current_job': None
            }
        
        # Get API connection status
        api_status = get_api_status()
        
        logger.log_app_event("dashboard_accessed", {
            "config_count": len(configs),
            "output_count": output_stats.get('total_outputs', 0),
            "queue_size": queue_status.get('total_jobs', 0),
            "api_connected": api_status.get('connected', False)
        })
        
        if not configs:
            logger.warning("No configuration templates found for dashboard display.")
            # Log the config directory path for debugging
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs')
            logger.warning(f"Config directory path: {config_dir}")
            logger.warning(f"Config directory exists: {os.path.exists(config_dir)}")
            if os.path.exists(config_dir):
                files = os.listdir(config_dir)
                logger.warning(f"Files in config directory: {files}")
        
        return render_template('dashboard.html', 
                             configs=configs, 
                             output_stats=output_stats,
                             queue_status=queue_status,
                             api_status=api_status)
    except Exception as e:
        logger.log_error(f"Failed to load dashboard: {e}")
        import traceback
        logger.log_error(f"Dashboard error traceback: {traceback.format_exc()}")
        return render_template('dashboard.html', 
                             configs={}, 
                             output_stats={},
                             queue_status={'total_jobs': 0, 'pending_jobs': 0, 'running_jobs': 0, 'completed_jobs': 0, 'failed_jobs': 0, 'total_images': 0, 'completed_images': 0, 'failed_images': 0, 'current_job': None},
                             api_status={'connected': False, 'error': str(e)},
                             error=str(e))

def load_templates_directly():
    """Fallback method to load templates directly without config handler."""
    configs = {}
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs')
        if not os.path.exists(config_dir):
            logger.warning(f"Config directory does not exist: {config_dir}")
            return configs
        
        for filename in os.listdir(config_dir):
            if filename.endswith('.json'):
                config_name = filename[:-5]  # Remove .json extension
                config_path = os.path.join(config_dir, filename)
                
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Basic validation
                    if 'name' in config and 'model_type' in config:
                        configs[config_name] = config
                        logger.info(f"Directly loaded config: {config_name}")
                    else:
                        logger.warning(f"Config {config_name} missing required fields")
                        
                except Exception as e:
                    logger.warning(f"Failed to load config {config_name}: {e}")
                    
    except Exception as e:
        logger.error(f"Error in direct template loading: {e}")
    
    return configs

# API Status Endpoints
@app.route('/api/status')
def get_system_status():
    """Get comprehensive system status."""
    try:
        # Get API connection status
        api_status = get_api_status()
        
        # Get queue status
        queue_status = job_queue.get_status()
        
        # Get current generation status
        generation_status = get_generation_status()
        
        # Get output statistics
        output_stats = output_manager.get_output_statistics()
        
        status = {
            'api': api_status,
            'queue': queue_status,
            'generation': generation_status,
            'outputs': output_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(status)
    except Exception as e:
        logger.log_error(f"Failed to get system status: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/status/api')
def get_api_status():
    """Get Forge API connection status."""
    try:
        # Test connection to Forge API
        connected = forge_api_client.test_connection()
        
        if connected:
            # Get additional API info
            try:
                progress = forge_api_client.get_progress()
                options = forge_api_client.get_options()
                
                status = {
                    'connected': True,
                    'server_url': forge_api_client.base_url,
                    'progress': progress,
                    'options_count': len(options) if options else 0,
                    'last_check': datetime.now().isoformat()
                }
            except Exception as e:
                status = {
                    'connected': True,
                    'server_url': forge_api_client.base_url,
                    'error': f'Failed to get API details: {str(e)}',
                    'last_check': datetime.now().isoformat()
                }
        else:
            status = {
                'connected': False,
                'server_url': forge_api_client.base_url,
                'error': 'Cannot connect to Forge API',
                'last_check': datetime.now().isoformat()
            }
        
        return status
    except Exception as e:
        logger.log_error(f"Failed to check API status: {e}")
        return {
            'connected': False,
            'server_url': forge_api_client.base_url,
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }

@app.route('/api/status/generation')
def get_generation_status():
    """Get current generation status."""
    global current_generation
    
    try:
        # Get Forge progress if available
        forge_progress = {}
        try:
            forge_progress = forge_api_client.get_progress()
        except:
            pass
        
        status = {
            'active': current_generation['active'],
            'current_image': current_generation['current_image'],
            'total_images': current_generation['total_images'],
            'config_name': current_generation['config_name'],
            'progress': current_generation['progress'],
            'forge_progress': forge_progress,
            'start_time': current_generation['start_time'],
            'elapsed_time': None
        }
        
        # Calculate elapsed time
        if current_generation['start_time']:
            elapsed = datetime.now() - current_generation['start_time']
            status['elapsed_time'] = elapsed.total_seconds()
        
        return status
    except Exception as e:
        logger.log_error(f"Failed to get generation status: {e}")
        return {
            'active': False,
            'error': str(e)
        }

def update_generation_progress(current: int, total: int, config_name: str = ''):
    """Update the current generation progress."""
    global current_generation
    
    current_generation['current_image'] = current
    current_generation['total_images'] = total
    current_generation['config_name'] = config_name
    current_generation['progress'] = (current / total * 100) if total > 0 else 0
    
    if current == 1 and total > 0:
        current_generation['active'] = True
        current_generation['start_time'] = datetime.now()
    
    if current >= total:
        current_generation['active'] = False
    
    # Emit progress update via WebSocket
    socketio.emit('generation_progress', {
        'current': current,
        'total': total,
        'progress': current_generation['progress'],
        'config_name': config_name,
        'active': current_generation['active']
    })

@app.route('/api/configs')
def get_configs():
    """Get all configurations."""
    try:
        configs = config_handler.get_all_configs()
        logger.log_app_event("configs_retrieved", {"count": len(configs)})
        return jsonify(configs)
    except Exception as e:
        logger.log_error(f"Failed to get configs: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/configs/<config_name>')
def get_config(config_name):
    """Get a specific configuration."""
    try:
        config = config_handler.get_config(config_name)
        if config:
            logger.log_config_operation("retrieved", config_name, True)
            return jsonify(config)
        else:
            logger.log_config_operation("retrieved", config_name, False, {"error": "Config not found"})
            return jsonify({'error': 'Configuration not found'}), 404
    except Exception as e:
        logger.log_config_operation("retrieved", config_name, False, {"error": str(e)})
        return jsonify({'error': str(e)}), 400

@app.route('/api/configs', methods=['POST'])
def create_config():
    """Create a new configuration."""
    try:
        data = request.get_json()
        config_name = data.get('name')
        config_data = data.get('config')
        
        if not config_name or not config_data:
            return jsonify({'error': 'Name and config data are required'}), 400
        
        success = config_handler.save_config(config_name, config_data)
        
        if success:
            logger.log_config_operation("created", config_name, True)
            return jsonify({'success': True, 'message': f'Configuration {config_name} created successfully'})
        else:
            logger.log_config_operation("created", config_name, False, {"error": "Failed to save"})
            return jsonify({'error': 'Failed to create configuration'}), 400
    except Exception as e:
        logger.log_config_operation("created", config_name, False, {"error": str(e)})
        return jsonify({'error': str(e)}), 400

@app.route('/api/configs/<config_name>', methods=['PUT'])
def update_config(config_name):
    """Update a configuration."""
    try:
        data = request.get_json()
        config_data = data.get('config')
        
        if not config_data:
            return jsonify({'error': 'Config data is required'}), 400
        
        success = config_handler.save_config(config_name, config_data)
        
        if success:
            logger.log_config_operation("updated", config_name, True)
            return jsonify({'success': True, 'message': f'Configuration {config_name} updated successfully'})
        else:
            logger.log_config_operation("updated", config_name, False, {"error": "Failed to save"})
            return jsonify({'error': 'Failed to update configuration'}), 400
    except Exception as e:
        logger.log_config_operation("updated", config_name, False, {"error": str(e)})
        return jsonify({'error': str(e)}), 400

@app.route('/api/configs/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    """Delete a configuration."""
    try:
        success = config_handler.delete_config(config_name)
        
        if success:
            logger.log_config_operation("deleted", config_name, True)
            return jsonify({'success': True, 'message': f'Configuration {config_name} deleted successfully'})
        else:
            logger.log_config_operation("deleted", config_name, False, {"error": "Failed to delete"})
            return jsonify({'error': 'Failed to delete configuration'}), 400
    except Exception as e:
        logger.log_config_operation("deleted", config_name, False, {"error": str(e)})
        return jsonify({'error': str(e)}), 400

@app.route('/api/generate', methods=['POST'])
def generate_image():
    """Generate a single image."""
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        prompt = data.get('prompt', '')
        seed_input = data.get('seed')
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Handle seed properly - convert string to int or None
        seed = None
        if seed_input is not None and seed_input != '':
            try:
                seed = int(seed_input)
            except (ValueError, TypeError):
                # Invalid seed value, use random seed
                seed = None
        
        config = config_handler.get_config(config_name)
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # If the prompt contains wildcards, resolve them
        if '__' in prompt:
            wildcard_factory = WildcardManagerFactory()
            prompt_builder = PromptBuilder(wildcard_factory)
            # Use the prompt as a template, but allow fallback to config template if empty
            resolved_prompt = prompt_builder.build_prompt({**config, 'prompt_settings': {**config['prompt_settings'], 'base_prompt': prompt}})
        else:
            resolved_prompt = prompt
        
        logger.log_app_event("image_generation_requested", {
            "config_name": config_name,
            "prompt_length": len(resolved_prompt),
            "seed": seed,
            "seed_input": seed_input,
            "user_provided_prompt": True,
            "wildcards_resolved": ('__' in prompt)
        })
        
        # Update generation progress
        update_generation_progress(1, 1, config_name)
        
        # Generate image with the resolved prompt
        success, image_data, metadata = forge_api_client.generate_image(config, resolved_prompt, seed)
        
        if success:
            # Save image
            output_path = output_manager.save_image(image_data, config_name, resolved_prompt, seed or 0)
            
            logger.log_image_generation(config_name, resolved_prompt, seed or 0, True, output_path)
            
            # Update progress to complete
            update_generation_progress(1, 1, config_name)
            
            return jsonify({
                'success': True,
                'image_data': image_data,
                'output_path': output_path,
                'metadata': metadata,
                'prompt_used': resolved_prompt,
                'seed_used': seed
            })
        else:
            logger.log_image_generation(config_name, resolved_prompt, seed or 0, False)
            return jsonify({'error': 'Failed to generate image'}), 400
    except Exception as e:
        logger.log_error(f"Failed to generate image: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/batch', methods=['POST'])
def start_batch():
    """Start a batch generation job."""
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        batch_size = data.get('batch_size', 1)
        num_batches = data.get('num_batches', 1)
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        config = config_handler.get_config(config_name)
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Calculate total images
        total_images = batch_size * num_batches
        
        # Update generation progress
        update_generation_progress(0, total_images, config_name)
        
        # Add job to queue
        job_id = job_queue.add_job(config, batch_size, num_batches)
        
        logger.log_queue_operation("job_added", job_id, {
            "config_name": config_name,
            "batch_size": batch_size,
            "num_batches": num_batches,
            "total_images": total_images
        })
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Batch job {job_id} added to queue',
            'total_images': total_images
        })
    except Exception as e:
        logger.log_error(f"Failed to start batch: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/batch/preview', methods=['POST'])
def preview_batch():
    """Preview batch prompts without generating images."""
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        batch_size = data.get('batch_size', 1)
        num_batches = data.get('num_batches', 1)
        prompt = data.get('prompt', '')  # User must provide a completed prompt
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        if not prompt:
            return jsonify({'error': 'Prompt is required - please provide a completed prompt with all wildcards substituted'}), 400
        
        config = config_handler.get_config(config_name)
        if not config:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Generate the same prompt for all images in the batch
        total_prompts = batch_size * num_batches
        prompts = [prompt] * total_prompts
        
        logger.log_app_event("batch_preview_generated", {
            "config_name": config_name,
            "batch_size": batch_size,
            "num_batches": num_batches,
            "prompt_count": len(prompts),
            "user_provided_prompt": True
        })
        
        return jsonify({
            'success': True,
            'prompts': prompts
        })
    except Exception as e:
        logger.log_error(f"Failed to preview batch: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/queue/status')
def get_queue_status():
    """Get queue status."""
    try:
        status = job_queue.get_status()
        return jsonify(status)
    except Exception as e:
        logger.log_error(f"Failed to get queue status: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/queue/clear', methods=['POST'])
def clear_queue():
    """Clear the job queue."""
    try:
        cleared_count = job_queue.clear_queue()
        
        logger.log_queue_operation("cleared", None, {"cleared_count": cleared_count})
        
        return jsonify({
            'success': True,
            'message': f'Queue cleared. {cleared_count} jobs removed.'
        })
    except Exception as e:
        logger.log_error(f"Failed to clear queue: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs')
def get_outputs():
    """Get all outputs."""
    try:
        outputs = output_manager.get_all_outputs()
        return jsonify(outputs)
    except Exception as e:
        logger.log_error(f"Failed to get outputs: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs/<config_name>')
def get_config_outputs(config_name):
    """Get outputs for a specific configuration."""
    try:
        outputs = output_manager.get_outputs_for_config(config_name)
        return jsonify(outputs)
    except Exception as e:
        logger.log_error(f"Failed to get outputs for config {config_name}: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs/delete/<config_name>', methods=['DELETE'])
def delete_config_outputs(config_name):
    """Delete all outputs for a configuration."""
    try:
        deleted_count = output_manager.delete_config_outputs(config_name)
        
        logger.log_app_event("config_outputs_deleted", {
            "config_name": config_name,
            "deleted_count": deleted_count
        })
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} outputs for {config_name}'
        })
    except Exception as e:
        logger.log_error(f"Failed to delete outputs for config {config_name}: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs/export/<config_name>', methods=['POST'])
def export_outputs(config_name):
    """Export outputs for a configuration."""
    try:
        data = request.get_json() or {}
        export_path = data.get('export_path', f'exports/{config_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        export_dir = output_manager.export_config_outputs(config_name, export_path)
        
        logger.log_app_event('output_export', {
            'config_name': config_name,
            'export_path': export_dir
        })
        
        return jsonify({
            'success': True,
            'export_path': export_dir
        })
    except Exception as e:
        logger.log_error(f"Failed to export outputs: {e}")
        return jsonify({'error': str(e)}), 400

# Logging Endpoints
@app.route('/api/logs/summary')
def get_logs_summary():
    """Get logging summary."""
    try:
        summary = logger.get_session_summary()
        # For live status, just return recent_events
        return jsonify({'recent_events': summary.get('recent_events', [])})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/logs/cleanup', methods=['POST'])
def cleanup_logs():
    """Clean up old log files."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 30)
        
        cleaned_files = logger.cleanup_old_logs(days_to_keep)
        
        logger.log_app_event("logs_cleaned", {
            "days_to_keep": days_to_keep,
            "cleaned_files": len(cleaned_files)
        })
        
        return jsonify({
            'success': True,
            'message': f'Logs older than {days_to_keep} days cleaned up',
            'cleaned_files': cleaned_files
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/logs/structure')
def get_logs_structure():
    """Get log directory structure information."""
    try:
        structure = logger.get_log_directory_structure()
        return jsonify(structure)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Static file serving
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.log_app_event("websocket_connected", {"client_id": request.sid})
    emit('status', {'message': 'Connected to Forge API Tool'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.log_app_event("websocket_disconnected", {"client_id": request.sid})

@socketio.on('request_status')
def handle_status_request():
    """Handle status request."""
    try:
        # Get comprehensive status
        api_status = get_api_status()
        queue_status = job_queue.get_status()
        generation_status = get_generation_status()
        output_stats = output_manager.get_output_statistics()
        
        emit('status_update', {
            'api': api_status,
            'queue': queue_status,
            'generation': generation_status,
            'outputs': output_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.log_error(f"Failed to send status update: {e}")
        emit('error', {'message': str(e)})

def start_background_processor():
    """Start the background job processor."""
    def processor():
        while True:
            try:
                # Process jobs in queue
                job_queue.process_next_job()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.log_error(f"Background processor error: {e}")
                time.sleep(5)  # Wait longer on error
    
    thread = threading.Thread(target=processor, daemon=True)
    thread.start()
    logger.log_app_event("background_processor_started")

# API Connection Management
@app.route('/api/connect', methods=['POST'])
def connect_api():
    """Connect to the Forge API."""
    try:
        # Test connection
        connected = forge_api_client.test_connection()
        
        if connected:
            logger.log_app_event("api_connected", {
                "server_url": forge_api_client.base_url,
                "status": "success"
            })
            return jsonify({
                'success': True,
                'message': 'Successfully connected to Forge API'
            })
        else:
            logger.log_app_event("api_connection_failed", {
                "server_url": forge_api_client.base_url,
                "status": "failed"
            })
            return jsonify({
                'success': False,
                'message': 'Failed to connect to Forge API'
            }), 400
    except Exception as e:
        logger.log_error(f"API connection error: {e}")
        return jsonify({
            'success': False,
            'message': f'Connection error: {str(e)}'
        }), 400

@app.route('/api/disconnect', methods=['POST'])
def disconnect_api():
    """Disconnect from the Forge API."""
    try:
        # Log disconnection
        logger.log_app_event("api_disconnected", {
            "server_url": forge_api_client.base_url
        })
        
        return jsonify({
            'success': True,
            'message': 'API disconnected'
        })
    except Exception as e:
        logger.log_error(f"API disconnection error: {e}")
        return jsonify({
            'success': False,
            'message': f'Disconnection error: {str(e)}'
        }), 400

# Generation Control
@app.route('/api/generation/stop', methods=['POST'])
def stop_generation():
    """Stop the current generation."""
    global current_generation
    
    try:
        # Stop current generation
        if current_generation['active']:
            current_generation['active'] = False
            current_generation['current_image'] = 0
            current_generation['total_images'] = 0
            current_generation['progress'] = 0.0
            current_generation['config_name'] = ''
            current_generation['start_time'] = None
            
            # Clear the job queue
            cleared_count = job_queue.clear_queue()
            
            logger.log_app_event("generation_stopped", {
                "cleared_jobs": cleared_count
            })
            
            return jsonify({
                'success': True,
                'message': f'Generation stopped. {cleared_count} jobs cleared from queue.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No active generation to stop'
            }), 400
    except Exception as e:
        logger.log_error(f"Failed to stop generation: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to stop generation: {str(e)}'
        }), 400

if __name__ == '__main__':
    # Start background processor
    start_background_processor()
    
    # Log startup
    logger.log_app_event("web_dashboard_started", {
        "port": 5000,
        "debug": True
    })
    
    # Launch browser after a short delay
    def launch_browser():
        time.sleep(1.5)  # Wait for server to start
        try:
            webbrowser.open('http://localhost:5000')
            logger.log_app_event("browser_launched", {"url": "http://localhost:5000"})
        except Exception as e:
            logger.log_error(f"Failed to launch browser: {e}")
    
    # Start browser launch in a separate thread
    browser_thread = threading.Thread(target=launch_browser, daemon=True)
    browser_thread.start()
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 