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
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO, emit
import sys
import re

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_handler import config_handler
from core.forge_api import forge_api_client
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.job_queue import job_queue
from core.batch_runner import batch_runner
from core.prompt_builder import PromptBuilder
from core.wildcard_manager import WildcardManagerFactory
from core.exceptions import (
    ForgeAPIError, ConnectionError, ConfigurationError, JobQueueError, 
    WildcardError, APIError, ValidationError, FileOperationError, 
    GenerationError, LoggingError
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
logger = logger

# Initialize output manager with centralized structure
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))

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
        except JobQueueError as e:
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
    except ConfigurationError as e:
        logger.log_error(f"Configuration error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             configs={}, 
                             output_stats={},
                             queue_status={'total_jobs': 0, 'pending_jobs': 0, 'running_jobs': 0, 'completed_jobs': 0, 'failed_jobs': 0, 'total_images': 0, 'completed_images': 0, 'failed_images': 0, 'current_job': None},
                             api_status={'connected': False, 'error': str(e)},
                             error=f"Configuration error: {e}")
    except FileOperationError as e:
        logger.log_error(f"File operation error loading dashboard: {e}")
        return render_template('dashboard.html', 
                             configs={}, 
                             output_stats={},
                             queue_status={'total_jobs': 0, 'pending_jobs': 0, 'running_jobs': 0, 'completed_jobs': 0, 'failed_jobs': 0, 'total_images': 0, 'completed_images': 0, 'failed_images': 0, 'current_job': None},
                             api_status={'connected': False, 'error': str(e)},
                             error=f"File operation error: {e}")
    except Exception as e:
        logger.log_error(f"Unexpected error loading dashboard: {e}")
        import traceback
        logger.log_error(f"Dashboard error traceback: {traceback.format_exc()}")
        return render_template('dashboard.html', 
                             configs={}, 
                             output_stats={},
                             queue_status={'total_jobs': 0, 'pending_jobs': 0, 'running_jobs': 0, 'completed_jobs': 0, 'failed_jobs': 0, 'total_images': 0, 'completed_images': 0, 'failed_images': 0, 'current_job': None},
                             api_status={'connected': False, 'error': str(e)},
                             error=f"Unexpected error: {e}")

def load_templates_directly():
    """Fallback method to load templates directly without config handler."""
    configs = {}
    try:
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs')
        if not os.path.exists(config_dir):
            logger.warning(f"Config directory does not exist: {config_dir}")
            raise FileOperationError(f"Config directory does not exist: {config_dir}", file_path=config_dir, operation="read")
        
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
                        raise ValidationError(f"Config {config_name} missing required fields", field="name/model_type", value=config_name)
                        
                except (IOError, OSError) as e:
                    logger.warning(f"File error loading config {config_name}: {e}")
                    raise FileOperationError(f"Failed to load config {config_name}: {e}", file_path=config_path, operation="read") from e
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON error loading config {config_name}: {e}")
                    raise ValidationError(f"Invalid JSON in config {config_name}: {e}", field="json", value=config_name) from e
                except Exception as e:
                    logger.warning(f"Unexpected error loading config {config_name}: {e}")
                    raise ConfigurationError(f"Unexpected error loading config {config_name}: {e}", config_name=config_name) from e
                    
    except FileOperationError:
        # Re-raise file operation errors
        raise
    except Exception as e:
        logger.error(f"Unexpected error in direct template loading: {e}")
        raise ConfigurationError(f"Unexpected error in direct template loading: {e}") from e
    
    return configs

# API Status Endpoints
@app.route('/api/status')
def get_system_status():
    """Get comprehensive system status."""
    try:
        # Get API connection status
        api_status = get_api_status()
        
        # Get queue status
        queue_status = job_queue.get_queue_stats()
        
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
    except (ConnectionError, APIError) as e:
        logger.log_error(f"API error getting system status: {e}")
        return jsonify({'error': f"API error: {e}"}), 400
    except JobQueueError as e:
        logger.log_error(f"Job queue error getting system status: {e}")
        return jsonify({'error': f"Job queue error: {e}"}), 400
    except FileOperationError as e:
        logger.log_error(f"File operation error getting system status: {e}")
        return jsonify({'error': f"File operation error: {e}"}), 400
    except Exception as e:
        logger.log_error(f"Unexpected error getting system status: {e}")
        return jsonify({'error': f"Unexpected error: {e}"}), 400

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
        logger.log_config_operation("retrieved", config_name, True)
        return jsonify(config)
    except FileNotFoundError:
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
        
        # Create the config
        success = config_handler.create_config(config_name, config_data)
        
        if success:
            logger.log_config_operation("created", config_name, True)
            return jsonify({'success': True, 'message': f'Configuration {config_name} created successfully'})
        else:
            logger.log_config_operation("created", config_name, False, {"error": "Failed to create"})
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
        
        # Update the config
        success = config_handler.update_config(config_name, config_data)
        
        if success:
            logger.log_config_operation("updated", config_name, True)
            return jsonify({'success': True, 'message': f'Configuration {config_name} updated successfully'})
        else:
            logger.log_config_operation("updated", config_name, False, {"error": "Failed to update"})
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
        seed = data.get('seed')
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        try:
            config = config_handler.get_config(config_name)
        except FileNotFoundError:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Use user-provided prompt or template prompt
        if not prompt:
            prompt = config['prompt_settings']['base_prompt']
        
        # Resolve wildcards if present
        if '__' in prompt:
            wildcard_factory = WildcardManagerFactory()
            prompt_builder = PromptBuilder(wildcard_factory)
            temp_config = {**config, 'prompt_settings': {**config['prompt_settings'], 'base_prompt': prompt}}
            resolved_prompts = prompt_builder.preview_prompts(temp_config, 1)
            prompt = resolved_prompts[0] if resolved_prompts else prompt
        
        # Generate image
        success, image_data, info = forge_api_client.generate_image(config, prompt, seed)
        
        if success and image_data:
            # Extract seed from info, ensuring it's an integer
            api_seed = info.get('seed') if isinstance(info, dict) else None
            if api_seed is not None:
                try:
                    final_seed = int(api_seed)
                except (ValueError, TypeError):
                    final_seed = int(seed) if seed is not None else -1
            else:
                final_seed = int(seed) if seed is not None else -1
            
            # Save image with embedded metadata using the new output manager
            filepath = output_manager.save_image(
                image_data=image_data,
                config_name=config_name,
                prompt=prompt,
                seed=final_seed,
                generation_settings=config['generation_settings'],
                model_settings=config['model_settings']
            )
            
            logger.log_app_event("image_generation", {
                "config_name": config_name,
                "prompt": prompt,
                "seed": final_seed,
                "success": True,
                "output_path": filepath,
                "timestamp": datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'message': 'Image generated successfully',
                'filepath': filepath,
                'info': info
            })
        else:
            error_msg = info.get('error', 'Unknown error') if isinstance(info, dict) and info else 'Generation failed'
            logger.log_app_event("image_generation", {
                "config_name": config_name,
                "prompt": prompt,
                "seed": seed,
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            })
            
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
            
    except Exception as e:
        logger.log_error(f"Error generating image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch', methods=['POST'])
def start_batch():
    """Start a batch generation job."""
    try:
        data = request.get_json()
        config_name = data.get('config_name')
        batch_size = data.get('batch_size', 1)
        num_batches = data.get('num_batches', 1)
        prompts = data.get('prompts', [])  # Optional: pre-generated prompts from preview
        user_prompt = data.get('prompt', '')  # Optional: user-provided prompt
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        try:
            config = config_handler.get_config(config_name)
        except FileNotFoundError:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Calculate total images
        total_images = batch_size * num_batches
        
        # If prompts were provided from preview, use them
        if prompts:
            # Use pre-generated prompts from preview
            resolved_prompts = prompts
            user_provided = False
            wildcards_resolved = True
        elif user_prompt:
            # Use user-provided prompt (may contain wildcards)
            if '__' in user_prompt:
                # Resolve wildcards
                wildcard_factory = WildcardManagerFactory()
                prompt_builder = PromptBuilder(wildcard_factory)
                temp_config = {**config, 'prompt_settings': {**config['prompt_settings'], 'base_prompt': user_prompt}}
                resolved_prompts = prompt_builder.preview_prompts(temp_config, total_images)
                wildcards_resolved = True
            else:
                # No wildcards, repeat the same prompt
                resolved_prompts = [user_prompt] * total_images
                wildcards_resolved = False
            user_provided = True
        else:
            # Use template's base prompt
            template_prompt = config['prompt_settings']['base_prompt']
            if '__' in template_prompt:
                # Resolve wildcards
                wildcard_factory = WildcardManagerFactory()
                prompt_builder = PromptBuilder(wildcard_factory)
                resolved_prompts = prompt_builder.preview_prompts(config, total_images)
                wildcards_resolved = True
            else:
                # No wildcards, repeat the same prompt
                resolved_prompts = [template_prompt] * total_images
                wildcards_resolved = False
            user_provided = False
        
        # Update generation progress
        update_generation_progress(0, total_images, config_name)
        
        # Add job to queue with resolved prompts
        job_id = job_queue.add_job_with_prompts(config, resolved_prompts)
        
        logger.log_queue_operation("job_added", job_id, {
            "config_name": config_name,
            "batch_size": batch_size,
            "num_batches": num_batches,
            "total_images": total_images,
            "user_provided_prompt": user_provided,
            "wildcards_resolved": wildcards_resolved,
            "prompts_provided": len(prompts) > 0
        })
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Batch job {job_id} added to queue',
            'total_images': total_images,
            'wildcards_resolved': wildcards_resolved
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
        user_prompt = data.get('prompt', '')  # Optional user-provided prompt
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        try:
            config = config_handler.get_config(config_name)
        except FileNotFoundError:
            return jsonify({'error': 'Configuration not found'}), 404
        
        # Calculate total prompts needed
        total_prompts = batch_size * num_batches
        
        # If user provided a prompt, use it; otherwise use template's base prompt
        if user_prompt:
            # Use user-provided prompt (may contain wildcards)
            template_prompt = user_prompt
            user_provided = True
        else:
            # Use template's base prompt
            template_prompt = config['prompt_settings']['base_prompt']
            user_provided = False
        
        # Check if the prompt contains wildcards
        if '__' in template_prompt:
            # Resolve wildcards using PromptBuilder
            wildcard_factory = WildcardManagerFactory()
            prompt_builder = PromptBuilder(wildcard_factory)
            
            # Create a temporary config with the template prompt
            temp_config = {**config, 'prompt_settings': {**config['prompt_settings'], 'base_prompt': template_prompt}}
            
            # Generate varied prompts with wildcard resolution
            prompts = prompt_builder.preview_prompts(temp_config, total_prompts)
            wildcards_resolved = True
        else:
            # No wildcards, just repeat the same prompt
            prompts = [template_prompt] * total_prompts
            wildcards_resolved = False
        
        logger.log_app_event("batch_preview_generated", {
            "config_name": config_name,
            "batch_size": batch_size,
            "num_batches": num_batches,
            "prompt_count": len(prompts),
            "user_provided_prompt": user_provided,
            "wildcards_resolved": wildcards_resolved,
            "template_used": not user_provided
        })
        
        return jsonify({
            'success': True,
            'prompts': prompts,
            'wildcards_resolved': wildcards_resolved,
            'template_used': not user_provided
        })
    except Exception as e:
        logger.log_error(f"Failed to preview batch: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/queue/status')
def get_queue_status():
    """Get detailed queue status with enhanced statistics."""
    try:
        stats = job_queue.get_queue_stats()
        return jsonify(stats)
    except Exception as e:
        logger.log_error(f"Error getting queue status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/jobs')
def get_queue_jobs():
    """Get all jobs in the queue with detailed information."""
    try:
        jobs = job_queue.get_all_jobs()
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'total': len(jobs)
        })
    except Exception as e:
        logger.log_error(f"Error getting queue jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/jobs/<job_id>')
def get_job_details(job_id):
    """Get detailed information about a specific job."""
    try:
        job = job_queue.get_job(job_id)
        if job:
            return jsonify(job.to_dict())
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        logger.log_error(f"Error getting job details: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/jobs/<job_id>/retry', methods=['POST'])
def retry_job(job_id):
    """Retry a failed job."""
    try:
        success = job_queue.retry_job(job_id)
        if success:
            return jsonify({'message': 'Job queued for retry'})
        else:
            return jsonify({'error': 'Job cannot be retried'}), 400
    except Exception as e:
        logger.log_error(f"Error retrying job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a specific job."""
    try:
        success = job_queue.remove_job(job_id)
        if success:
            return jsonify({'message': 'Job cancelled'})
        else:
            return jsonify({'error': 'Job not found or cannot be cancelled'}), 404
    except Exception as e:
        logger.log_error(f"Error cancelling job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/clear', methods=['POST'])
def clear_queue():
    """Clear all jobs from the queue."""
    try:
        cleared_count = job_queue.clear_all_jobs()
        return jsonify({
            'message': f'Cleared {cleared_count} jobs from queue',
            'cleared_count': cleared_count
        })
    except Exception as e:
        logger.log_error(f"Error clearing queue: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/clear-completed', methods=['POST'])
def clear_completed_jobs():
    """Clear only completed and failed jobs from the queue."""
    try:
        cleared_count = job_queue.clear_completed_jobs()
        return jsonify({
            'message': f'Cleared {cleared_count} completed/failed jobs',
            'cleared_count': cleared_count
        })
    except Exception as e:
        logger.log_error(f"Error clearing completed jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue/priority-stats')
def get_priority_stats():
    """Get queue statistics broken down by priority."""
    try:
        stats = job_queue.get_queue_stats()
        priority_stats = stats.get('priority_stats', {})
        
        # Add detailed priority breakdown
        detailed_stats = {}
        for priority_name, count in priority_stats.items():
            jobs = job_queue.get_jobs_by_priority(getattr(job_queue.JobPriority, priority_name))
            detailed_stats[priority_name] = {
                'count': count,
                'pending': len([j for j in jobs if j.status == job_queue.JobStatus.PENDING]),
                'running': len([j for j in jobs if j.status == job_queue.JobStatus.RUNNING]),
                'completed': len([j for j in jobs if j.status == job_queue.JobStatus.COMPLETED]),
                'failed': len([j for j in jobs if j.status == job_queue.JobStatus.FAILED]),
                'retrying': len([j for j in jobs if j.status == job_queue.JobStatus.RETRYING])
            }
        
        return jsonify(detailed_stats)
    except Exception as e:
        logger.log_error(f"Error getting priority stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/outputs')
def get_outputs():
    """Get all outputs with the new date-based structure."""
    try:
        # Get outputs for today by default
        date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
        config_name = request.args.get('config')
        
        if config_name:
            # Get outputs for specific config
            outputs = output_manager.get_outputs_for_config(config_name)
        else:
            # Get outputs for specific date
            outputs = output_manager.get_outputs_for_date(date)
        
        # Format outputs for frontend
        formatted_outputs = []
        for output in outputs:
            formatted_output = {
                'filename': output.get('filename', ''),
                'filepath': output.get('filepath', ''),
                'config_name': output.get('config_name', ''),
                'prompt': output.get('prompt', ''),
                'seed': output.get('seed', 0),
                'created_at': output.get('generation_time', ''),
                'date': output.get('date', ''),
                'steps': output.get('steps', 20),
                'sampler_name': output.get('sampler_name', ''),
                'cfg_scale': output.get('cfg_scale', 7.0),
                'width': output.get('width', 512),
                'height': output.get('height', 512),
                'model_name': output.get('model_name', ''),
                'negative_prompt': output.get('negative_prompt', '')
            }
            formatted_outputs.append(formatted_output)
        
        logger.log_app_event("outputs_retrieved", {
            "date": date,
            "config_name": config_name,
            "output_count": len(formatted_outputs)
        })
        
        return jsonify({
            'success': True,
            'outputs': formatted_outputs,
            'date': date,
            'config_name': config_name
        })
        
    except Exception as e:
        logger.log_error(f"Error getting outputs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/outputs/statistics')
def get_output_statistics():
    """Get output statistics."""
    try:
        stats = output_manager.get_output_statistics()
        
        logger.log_app_event("output_statistics_retrieved", stats)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.log_error(f"Error getting output statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/outputs/dates')
def get_output_dates():
    """Get all available output dates."""
    try:
        dates = []
        if os.path.exists(output_manager.base_output_dir):
            date_dirs = [d for d in os.listdir(output_manager.base_output_dir) 
                        if os.path.isdir(os.path.join(output_manager.base_output_dir, d)) and 
                        re.match(r'\d{4}-\d{2}-\d{2}', d)]
            dates = sorted(date_dirs, reverse=True)
        
        return jsonify({
            'success': True,
            'dates': dates
        })
        
    except Exception as e:
        logger.log_error(f"Error getting output dates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<date>/<filename>')
def serve_output_image(date, filename):
    """Serve output images from date-based folders."""
    try:
        # Validate date format
        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Validate filename
        if not filename.endswith('.png'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Construct file path
        file_path = os.path.join(output_manager.base_output_dir, date, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Serve the image file
        return send_file(file_path, mimetype='image/png')
        
    except Exception as e:
        logger.log_error(f"Error serving output image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/outputs/metadata/<date>/<filename>')
def get_output_metadata(date, filename):
    """Get metadata for a specific output image."""
    try:
        # Validate date format
        if not re.match(r'\d{4}-\d{2}-\d{2}', date):
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Validate filename
        if not filename.endswith('.png'):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Construct file path
        file_path = os.path.join(output_manager.base_output_dir, date, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Extract metadata from image
        metadata = output_manager.extract_metadata_from_image(file_path)
        
        if not metadata:
            return jsonify({'error': 'No metadata found'}), 404
        
        return jsonify({
            'success': True,
            'metadata': metadata
        })
        
    except Exception as e:
        logger.log_error(f"Error getting output metadata: {e}")
        return jsonify({'error': str(e)}), 500

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
        
        # Validate input
        if not isinstance(days_to_keep, int) or days_to_keep < 1:
            return jsonify({
                'success': False,
                'error': 'days_to_keep must be a positive integer'
            }), 400
        
        cleaned_files = logger.cleanup_old_logs(days_to_keep)
        
        logger.log_app_event("logs_cleaned", {
            "days_to_keep": days_to_keep,
            "cleaned_files": cleaned_files
        })
        
        return jsonify({
            'success': True,
            'message': f'Logs older than {days_to_keep} days cleaned up successfully',
            'cleaned_files': cleaned_files
        })
        
    except Exception as e:
        error_msg = f"Error during log cleanup: {str(e)}"
        logger.log_error(error_msg, e)
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

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
        queue_status = job_queue.get_queue_stats()
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

@app.route('/api/outputs/directory/<config_name>')
def get_output_directory(config_name):
    """Get the output directory path for a specific config."""
    try:
        directory_path = output_manager.get_output_directory(config_name)
        return jsonify({
            'config_name': config_name,
            'directory_path': directory_path,
            'exists': os.path.exists(directory_path)
        })
    except Exception as e:
        logger.log_error(f"Failed to get output directory for {config_name}: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs/directory/<config_name>/latest')
def get_latest_output_directory(config_name):
    """Get the most recent output directory for a specific config."""
    try:
        directory_path = output_manager.get_latest_output_directory(config_name)
        return jsonify({
            'config_name': config_name,
            'directory_path': directory_path,
            'exists': os.path.exists(directory_path)
        })
    except Exception as e:
        logger.log_error(f"Failed to get latest output directory for {config_name}: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/outputs/open-folder/<config_name>')
def open_output_folder(config_name):
    """Open the output folder for a specific configuration."""
    try:
        logger.log_app_event("output_folder_opened", {"config_name": config_name})
        
        # Get the output directory for the configuration
        output_dir = output_manager.get_output_directory(config_name)
        
        if not output_dir or not os.path.exists(output_dir):
            # Create the directory if it doesn't exist
            output_dir = output_manager.create_output_directory(config_name)
            logger.info(f"Created output directory: {output_dir}")
        
        # Open the folder using the system's default file manager
        if os.name == 'nt':  # Windows
            os.startfile(output_dir)
        elif os.name == 'posix':  # macOS and Linux
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{output_dir}"')
        
        return jsonify({
            'success': True,
            'directory_path': output_dir,
            'message': f'Opened output folder for {config_name}'
        })
        
    except FileOperationError as e:
        logger.log_error(f"File operation error opening folder: {e}")
        return jsonify({
            'success': False,
            'error': f'File operation error: {e}'
        }), 500
    except Exception as e:
        logger.log_error(f"Unexpected error opening folder: {e}")
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {e}'
        }), 500

# RunDiffusion API Endpoints
@app.route('/api/rundiffusion/config', methods=['GET'])
def get_rundiffusion_config():
    """Get the current RunDiffusion configuration."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rundiffusion_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify({
                'success': True,
                'config': config
            })
        else:
            return jsonify({
                'success': True,
                'config': None
            })
            
    except Exception as e:
        logger.log_error(f"Error getting RunDiffusion config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rundiffusion/config', methods=['POST'])
def save_rundiffusion_config():
    """Save RunDiffusion configuration and switch to RunDiffusion API."""
    try:
        config = request.get_json()
        
        # Validate required fields
        required_fields = ['url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })
        
        # Validate URL format
        url = config['url'].strip()
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'URL must start with http:// or https://'
            }), 400
        
        # Switch to RunDiffusion API
        from core.api_config import api_config
        api_config.switch_to_rundiffusion(config)
        
        # Refresh the forge API client
        forge_api_client.refresh_configuration()
        
        logger.log_app_event("switched_to_rundiffusion", {
            "url": url,
            "username": config['username']
        })
        
        return jsonify({
            'success': True,
            'message': 'Switched to RunDiffusion API successfully'
        })
        
    except Exception as e:
        logger.log_error(f"Error switching to RunDiffusion: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rundiffusion/test', methods=['POST'])
def test_rundiffusion_connection():
    """Test RunDiffusion API connection."""
    try:
        config = request.get_json()
        
        # Validate required fields
        required_fields = ['url', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Test connection using requests
        import requests
        from requests.auth import HTTPBasicAuth
        
        url = config['url'].rstrip('/')
        test_url = f"{url}/sdapi/v1/progress"
        
        try:
            response = requests.get(
                test_url,
                auth=HTTPBasicAuth(config['username'], config['password']),
                timeout=10,
                verify=True
            )
            
            if response.status_code == 200:
                logger.log_app_event("rundiffusion_connection_successful", {"url": url})
                return jsonify({
                    'success': True,
                    'message': 'Connection successful'
                })
            else:
                error_msg = f'HTTP {response.status_code}: {response.text}'
                logger.log_error(f"RunDiffusion connection failed: {error_msg}")
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
                
        except requests.exceptions.ConnectionError:
            error_msg = 'Connection refused - server may not be running'
            logger.log_error(f"RunDiffusion connection error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        except requests.exceptions.Timeout:
            error_msg = 'Connection timeout'
            logger.log_error(f"RunDiffusion connection timeout: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        except requests.exceptions.RequestException as e:
            error_msg = f'Request error: {str(e)}'
            logger.log_error(f"RunDiffusion request error: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
            
    except Exception as e:
        logger.log_error(f"Error testing RunDiffusion connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rundiffusion/disable', methods=['POST'])
def disable_rundiffusion():
    """Disable RunDiffusion and switch back to local API."""
    try:
        # Switch to local API
        from core.api_config import api_config
        api_config.switch_to_local()
        
        # Refresh the forge API client
        forge_api_client.refresh_configuration()
        
        logger.log_app_event("switched_to_local_api", {})
        
        return jsonify({
            'success': True,
            'message': 'Switched to local API'
        })
        
    except Exception as e:
        logger.log_error(f"Error switching to local API: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status/current-api')
def get_current_api_status():
    """Get current API connection status."""
    try:
        # Get current API preference
        api_preference_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api_preference.json')
        current_api = 'local'
        
        if os.path.exists(api_preference_file):
            try:
                with open(api_preference_file, 'r') as f:
                    preference = json.load(f)
                    current_api = preference.get('current_api', 'local')
            except Exception as e:
                logger.warning(f"Failed to read API preference: {e}")
        
        # Test connection based on current API
        if current_api == 'rundiffusion':
            try:
                # Test RunDiffusion connection
                response = forge_api_client.get_progress()
                connected = True
                response_time = response.get('response_time', 0)
            except Exception as e:
                connected = False
                response_time = 0
        else:
            try:
                # Test local Forge connection
                response = forge_api_client.get_progress()
                connected = True
                response_time = response.get('response_time', 0)
            except Exception as e:
                connected = False
                response_time = 0
        
        return jsonify({
            'current_api': current_api,
            'connected': connected,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.log_error(f"Error getting current API status: {e}")
        return jsonify({
            'current_api': 'local',
            'connected': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Image Analysis and Config Management Endpoints
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image to extract generation settings."""
    try:
        from core.image_analyzer import ImageAnalyzer
        
        # Get image data from request
        data = request.get_json()
        if not data or 'image_data' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        image_data = data['image_data']
        
        # Initialize image analyzer
        analyzer = ImageAnalyzer()
        
        # Analyze the image
        result = analyzer.analyze_image(image_data)
        
        if not result.get('success', False):
            return jsonify({'error': result.get('error', 'Failed to analyze image')}), 400
        
        # Create suggested config from analysis
        if 'parameters' in result and 'prompt_info' in result:
            suggested_config = analyzer._create_suggested_config(
                result['parameters'], 
                result['prompt_info']
            )
            result['suggested_config'] = suggested_config
        
        logger.log_app_event("image_analyzed", {
            "image_width": result.get('width', 0),
            "image_height": result.get('height', 0),
            "has_metadata": 'metadata' in result,
            "has_parameters": 'parameters' in result,
            "has_prompt": 'prompt' in result
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.log_error(f"Error analyzing image: {e}")
        return jsonify({'error': f'Failed to analyze image: {str(e)}'}), 500

@app.route('/api/configs/<config_name>/settings', methods=['GET'])
def get_config_settings(config_name):
    """Get detailed settings for a specific config."""
    try:
        config = config_handler.get_config(config_name)
        
        # Return the full config with all settings
        return jsonify({
            'config_name': config_name,
            'settings': config,
            'timestamp': datetime.now().isoformat()
        })
        
    except FileNotFoundError:
        logger.log_error(f"Config file not found: {config_name}")
        return jsonify({'error': f'Config {config_name} not found'}), 404
    except ConfigurationError as e:
        logger.log_error(f"Configuration error getting settings for {config_name}: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.log_error(f"Unexpected error getting settings for {config_name}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/configs/<config_name>/settings', methods=['PUT'])
def update_config_settings(config_name):
    """Update settings for a specific config."""
    try:
        data = request.get_json()
        if not data or 'settings' not in data:
            return jsonify({'error': 'No settings data provided'}), 400
        
        new_settings = data['settings']
        
        # Validate the config structure
        required_fields = ['name', 'model_type']
        for field in required_fields:
            if field not in new_settings:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Update the config
        success = config_handler.update_config(config_name, new_settings)
        
        if success:
            logger.log_app_event("config_updated", {
                "config_name": config_name,
                "model_type": new_settings.get('model_type', 'unknown'),
                "has_prompt_settings": 'prompt_settings' in new_settings,
                "has_generation_settings": 'generation_settings' in new_settings
            })
            
            return jsonify({
                'message': f'Config {config_name} updated successfully',
                'config_name': config_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({'error': 'Failed to update configuration'}), 400
        
    except ConfigurationError as e:
        logger.log_error(f"Configuration error updating {config_name}: {e}")
        return jsonify({'error': str(e)}), 400
    except ValidationError as e:
        logger.log_error(f"Validation error updating {config_name}: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.log_error(f"Unexpected error updating {config_name}: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/configs/create-from-image', methods=['POST'])
def create_config_from_image():
    """Create a new config based on image analysis."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        config_name = data.get('config_name')
        analysis_result = data.get('analysis_result')
        custom_settings = data.get('custom_settings', {})
        
        if not config_name:
            return jsonify({'error': 'Config name is required'}), 400
        
        if not analysis_result:
            return jsonify({'error': 'Analysis result is required'}), 400
        
        # Check if config already exists
        if config_handler.config_exists(config_name):
            return jsonify({'error': f'Config {config_name} already exists'}), 409
        
        # Create config from analysis
        from core.image_analyzer import ImageAnalyzer
        analyzer = ImageAnalyzer()
        
        # Merge analysis result with custom settings
        if 'suggested_config' in analysis_result:
            suggested_config = analysis_result['suggested_config']
            # Handle case where suggested_config might be a string
            if isinstance(suggested_config, str):
                # Try to parse as JSON, otherwise use as description
                try:
                    import json
                    base_config = json.loads(suggested_config)
                except (json.JSONDecodeError, TypeError):
                    # If it's not valid JSON, create a basic config with the string as description
                    base_config = {
                        'name': config_name,
                        'description': suggested_config,
                        'model_type': 'sd',
                        'prompt_settings': {
                            'base_prompt': analysis_result.get('prompt', ''),
                            'negative_prompt': analysis_result.get('negative_prompt', '')
                        },
                        'generation_settings': {
                            'steps': 20,
                            'width': analysis_result.get('width', 512),
                            'height': analysis_result.get('height', 512),
                            'batch_size': 1,
                            'sampler': 'Euler a',
                            'cfg_scale': 7.0
                        },
                        'model_settings': {
                            'checkpoint': '',
                            'vae': '',
                            'text_encoder': '',
                            'gpu_weight': 1.0,
                            'swap_method': 'weight',
                            'swap_location': 'cpu'
                        },
                        'output_settings': {
                            'dir': f'outputs/{config_name}/{{timestamp}}/',
                            'format': 'png',
                            'save_metadata': True,
                            'save_prompts': True
                        }
                    }
            else:
                # It's already a dictionary
                base_config = suggested_config
        else:
            # Create basic config if no suggested config
            base_config = {
                'name': config_name,
                'description': f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                'model_type': 'sd',
                'prompt_settings': {
                    'base_prompt': analysis_result.get('prompt', ''),
                    'negative_prompt': analysis_result.get('negative_prompt', '')
                },
                'generation_settings': {
                    'steps': 20,
                    'width': analysis_result.get('width', 512),
                    'height': analysis_result.get('height', 512),
                    'batch_size': 1,
                    'sampler': 'Euler a',
                    'cfg_scale': 7.0
                },
                'model_settings': {
                    'checkpoint': '',
                    'vae': '',
                    'text_encoder': '',
                    'gpu_weight': 1.0,
                    'swap_method': 'weight',
                    'swap_location': 'cpu'
                },
                'output_settings': {
                    'dir': f'outputs/{config_name}/{{timestamp}}/',
                    'format': 'png',
                    'save_metadata': True,
                    'save_prompts': True
                }
            }
        
        # Override with custom settings
        if custom_settings:
            for section, settings in custom_settings.items():
                if section in base_config:
                    if isinstance(settings, dict) and isinstance(base_config[section], dict):
                        base_config[section].update(settings)
                    else:
                        # If either is not a dict, replace the entire section
                        base_config[section] = settings
                else:
                    base_config[section] = settings
        
        # Update name and description
        base_config['name'] = config_name
        if 'description' not in base_config:
            base_config['description'] = f'Config created from image analysis - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Save the config
        success = config_handler.create_config(config_name, base_config)
        
        if not success:
            return jsonify({'error': 'Failed to create configuration'}), 400
        
        logger.log_app_event("config_created_from_image", {
            "config_name": config_name,
            "image_width": analysis_result.get('width', 0),
            "image_height": analysis_result.get('height', 0),
            "has_metadata": 'metadata' in analysis_result,
            "has_parameters": 'parameters' in analysis_result
        })
        
        return jsonify({
            'message': f'Config {config_name} created successfully',
            'config_name': config_name,
            'config': base_config,
            'timestamp': datetime.now().isoformat()
        })
        
    except ConfigurationError as e:
        logger.log_error(f"Configuration error creating config from image: {e}")
        return jsonify({'error': str(e)}), 400
    except ValidationError as e:
        logger.log_error(f"Validation error creating config from image: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.log_error(f"Unexpected error creating config from image: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    # Start background processor
    start_background_processor()
    
    # Log startup
    logger.log_app_event("web_dashboard_started", {
        "port": 4000,
        "debug": True
    })
    
    # Launch browser after a short delay
    def launch_browser():
        time.sleep(1.5)  # Wait for server to start
        try:
            webbrowser.open('http://localhost:4000')
            logger.log_app_event("browser_launched", {"url": "http://localhost:4000"})
        except Exception as e:
            logger.log_error(f"Failed to launch browser: {e}")
    
    # Start browser launch in a separate thread
    browser_thread = threading.Thread(target=launch_browser, daemon=True)
    browser_thread.start()
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=4000, debug=True) 