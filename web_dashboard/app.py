from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import os
import sys
import json
import time
from datetime import datetime
import base64

# Add the core directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
core_path = os.path.join(project_root, 'core')
sys.path.insert(0, core_path)

from config_handler import ConfigHandler
from wildcard_manager import WildcardManagerFactory
from prompt_builder import PromptBuilder
from forge_api import ForgeAPIClient
from batch_runner import BatchRunner
from image_analyzer import ImageAnalyzer
from output_manager import OutputManager
from logger import logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize core components
config_handler = ConfigHandler()
wildcard_factory = WildcardManagerFactory()
prompt_builder = PromptBuilder(wildcard_factory)
forge_client = ForgeAPIClient()
batch_runner = BatchRunner()
batch_runner.set_forge_client(forge_client)
image_analyzer = ImageAnalyzer()
output_manager = OutputManager()

# Global variables for tracking
current_job = None
processing_active = False


@app.route('/')
def dashboard():
    """Main dashboard page."""
    configs = config_handler.list_configs()
    config_summaries = []
    
    for config_name in configs:
        try:
            config = config_handler.load_config(config_name)
            summary = config_handler.get_config_summary(config)
            config_summaries.append(summary)
        except Exception as e:
            config_summaries.append({
                'name': config_name,
                'error': str(e)
            })
    
    return render_template('dashboard.html', configs=config_summaries)


@app.route('/api/configs')
def list_configs():
    """Get list of all configurations."""
    configs = config_handler.list_configs()
    summaries = []
    for name in configs:
        try:
            config = config_handler.load_config(name)
            summary = config_handler.get_config_summary(config)
            summary['missing_wildcards'] = config.get('missing_wildcards', [])
            summary['missing_wildcard_files'] = config.get('missing_wildcard_files', [])
            summary['error'] = False
        except Exception as e:
            summary = {'name': name, 'error': True, 'error_message': str(e)}
        summaries.append(summary)
    return jsonify(summaries)


@app.route('/api/config/<config_name>')
def get_config(config_name):
    """Get a specific configuration."""
    try:
        config = config_handler.load_config(config_name)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/summary')
def get_config_summary(config_name):
    """Get summary of a configuration."""
    try:
        config = config_handler.load_config(config_name)
        summary = config_handler.get_config_summary(config)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/preview')
def preview_config(config_name):
    """Preview prompts for a configuration."""
    count = request.args.get('count', 5, type=int)
    try:
        preview = batch_runner.preview_job(config_name, count)
        return jsonify(preview)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/wildcard-usage')
def get_wildcard_usage(config_name):
    """Get wildcard usage statistics for a configuration."""
    try:
        usage = batch_runner.get_wildcard_usage(config_name)
        return jsonify(usage)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/reset-wildcards', methods=['POST'])
def reset_wildcards(config_name):
    """Reset wildcard usage for a configuration."""
    try:
        batch_runner.reset_wildcards(config_name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/export-prompts')
def export_prompts(config_name):
    """Export prompt list for a configuration."""
    count = request.args.get('count', 10, type=int)
    try:
        prompts = batch_runner.export_prompt_list(config_name, count)
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/status')
def get_queue_status():
    """Get current queue status."""
    status = batch_runner.get_queue_status()
    return jsonify(status)


@app.route('/api/queue/job/<job_id>')
def get_job_details(job_id):
    """Get details of a specific job."""
    job = batch_runner.get_job_details(job_id)
    if job:
        return jsonify(job)
    else:
        return jsonify({'error': 'Job not found'}), 404


@app.route('/api/queue/add', methods=['POST'])
def add_job():
    """Add a job to the queue."""
    data = request.get_json()
    config_name = data.get('config_name')
    batch_size = data.get('batch_size')
    num_batches = data.get('num_batches')
    
    if not config_name:
        return jsonify({'error': 'config_name is required'}), 400
    
    try:
        job = batch_runner.add_job(config_name, batch_size, num_batches)
        return jsonify(job.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/remove/<job_id>', methods=['DELETE'])
def remove_job(job_id):
    """Remove a job from the queue."""
    try:
        success = batch_runner.job_queue.remove_job(job_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/start', methods=['POST'])
def start_processing():
    """Start processing the queue."""
    global processing_active
    
    if processing_active:
        return jsonify({'error': 'Processing already active'}), 400
    
    try:
        batch_runner.start_processing()
        processing_active = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/stop', methods=['POST'])
def stop_processing():
    """Stop processing the queue."""
    global processing_active
    
    try:
        batch_runner.stop_processing()
        processing_active = False
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/cancel', methods=['POST'])
def cancel_current_job():
    """Cancel the currently running job."""
    try:
        batch_runner.cancel_current_job()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/clear-completed', methods=['POST'])
def clear_completed_jobs():
    """Clear completed jobs from the queue."""
    try:
        batch_runner.clear_completed_jobs()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/queue/clear-all', methods=['POST'])
def clear_all_jobs():
    """Clear all jobs from the queue."""
    try:
        batch_runner.clear_all_jobs()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/forge/status')
def get_forge_status():
    """Get Forge API connection status."""
    try:
        # Test connection to Forge API
        models = forge_client.get_models()
        samplers = forge_client.get_samplers()
        
        return jsonify({
            'connected': True,
            'models': models if models else [],
            'samplers': samplers if samplers else [],
            'server_url': forge_client.server_url,
            'last_check': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'connected': False,
            'error': str(e),
            'server_url': forge_client.server_url,
            'last_check': datetime.now().isoformat()
        })


@app.route('/api/forge/connect', methods=['POST'])
def connect_forge():
    """Connect to Forge API."""
    try:
        data = request.get_json()
        server_url = data.get('server_url', 'http://127.0.0.1:7860/')
        
        # Update the Forge client with new server URL
        forge_client.server_url = server_url.rstrip('/')
        
        # Test the connection
        models = forge_client.get_models()
        samplers = forge_client.get_samplers()
        
        logger.info(f"Successfully connected to Forge API at {server_url}")
        
        return jsonify({
            'success': True,
            'message': f'Connected to Forge API at {server_url}',
            'models': models if models else [],
            'samplers': samplers if samplers else [],
            'server_url': forge_client.server_url
        })
    except Exception as e:
        logger.error(f"Failed to connect to Forge API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'server_url': forge_client.server_url
        }), 400


@app.route('/api/forge/disconnect', methods=['POST'])
def disconnect_forge():
    """Disconnect from Forge API."""
    try:
        # Reset the Forge client
        forge_client.server_url = 'http://127.0.0.1:7860/'
        
        logger.info("Disconnected from Forge API")
        
        return jsonify({
            'success': True,
            'message': 'Disconnected from Forge API'
        })
    except Exception as e:
        logger.error(f"Error disconnecting from Forge API: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/shutdown', methods=['POST'])
def shutdown_application():
    """Shutdown the application gracefully."""
    try:
        # Stop any active processing
        global processing_active
        if processing_active:
            batch_runner.stop_processing()
            processing_active = False
        
        # Save any pending data
        logger.info("Shutting down Forge API Tool...")
        
        # Schedule shutdown after response is sent
        def delayed_shutdown():
            time.sleep(1)  # Give time for response to be sent
            os._exit(0)
        
        import threading
        shutdown_thread = threading.Thread(target=delayed_shutdown)
        shutdown_thread.daemon = True
        shutdown_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Application shutting down...'
        })
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/forge/validate-config/<config_name>')
def validate_forge_config(config_name):
    """Validate a configuration against Forge API."""
    try:
        config = config_handler.load_config(config_name)
        is_valid, errors = forge_client.validate_config(config)
        
        return jsonify({
            'valid': is_valid,
            'errors': errors
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/wildcards')
def get_wildcards():
    """Get list of available wildcard files."""
    wildcard_dir = "wildcards"
    wildcards = []
    
    if os.path.exists(wildcard_dir):
        for file in os.listdir(wildcard_dir):
            if file.endswith('.txt'):
                file_path = os.path.join(wildcard_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        wildcards.append({
                            'name': file.replace('.txt', ''),
                            'path': file_path,
                            'count': len([line.strip() for line in lines if line.strip()])
                        })
                except Exception as e:
                    wildcards.append({
                        'name': file.replace('.txt', ''),
                        'path': file_path,
                        'error': str(e)
                    })
    
    return jsonify(wildcards)


@app.route('/api/wildcards/<wildcard_name>/items')
def get_wildcard_items(wildcard_name):
    """Get items from a wildcard file."""
    wildcard_path = os.path.join("wildcards", f"{wildcard_name}.txt")
    
    if not os.path.exists(wildcard_path):
        return jsonify({'error': 'Wildcard file not found'}), 404
    
    try:
        with open(wildcard_path, 'r', encoding='utf-8') as f:
            items = [line.strip() for line in f.readlines() if line.strip()]
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/wildcards/usage')
def get_wildcard_usage_stats():
    """Get overall wildcard usage statistics."""
    try:
        stats = wildcard_factory.get_all_usage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Progress callback for batch runner
def progress_callback(progress_data):
    """Callback for progress updates from batch runner."""
    socketio.emit('progress_update', progress_data)


# Set up progress callback
batch_runner.set_progress_callback(progress_callback)


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to Forge API Tool'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('get_queue_status')
def handle_get_queue_status():
    """Handle queue status request."""
    status = batch_runner.get_queue_status()
    emit('queue_status', status)


# Image Analysis Endpoints
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image to extract settings."""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not image_analyzer.validate_image_format(file.filename):
            return jsonify({'error': 'Unsupported image format'}), 400
        
        # Read image data
        image_data = file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Analyze image
        result = image_analyzer.analyze_image(image_base64)
        
        logger.log_app_event('image_analysis', {
            'filename': file.filename,
            'success': result.get('success', False)
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.log_error(f"Image analysis failed: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/supported-formats')
def get_supported_formats():
    """Get supported image formats for analysis."""
    return jsonify(image_analyzer.get_supported_formats())


# Configuration Management Endpoints
@app.route('/api/config/upload', methods=['POST'])
def upload_config():
    """Upload a new configuration file."""
    try:
        if 'config' not in request.files:
            return jsonify({'error': 'No config file provided'}), 400
        
        file = request.files['config']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'Only JSON files are supported'}), 400
        
        # Read and validate config
        config_data = json.load(file)
        config_name = config_data.get('name', file.filename.replace('.json', ''))
        
        # Save config
        config_handler.save_config(config_name, config_data)
        
        logger.log_config_operation('upload', config_name, True)
        
        return jsonify({
            'success': True,
            'config_name': config_name,
            'message': 'Configuration uploaded successfully'
        })
        
    except Exception as e:
        logger.log_config_operation('upload', 'unknown', False, {'error': str(e)})
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/create', methods=['POST'])
def create_config():
    """Create a new configuration from scratch."""
    try:
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        config_name = config_data.get('name')
        if not config_name:
            return jsonify({'error': 'Configuration name is required'}), 400
        
        # Check if config already exists
        if config_handler.config_exists(config_name):
            return jsonify({'error': f'Configuration "{config_name}" already exists'}), 400
        
        # Save config
        config_handler.save_config(config_name, config_data)
        
        logger.log_config_operation('create', config_name, True)
        
        return jsonify({
            'success': True,
            'config_name': config_name,
            'message': 'Configuration created successfully'
        })
        
    except Exception as e:
        logger.log_config_operation('create', 'unknown', False, {'error': str(e)})
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/templates')
def get_config_templates():
    """Get available configuration templates."""
    templates = [
        {
            'name': 'Quick Start',
            'description': 'Simple configuration for basic image generation',
            'template': {
                'name': 'Quick Start',
                'description': 'A simple configuration to get started quickly',
                'model_type': 'sd',
                'prompt_settings': {
                    'base_prompt': 'a beautiful __STYLE__ __SUBJECT__',
                    'negative_prompt': 'blurry, low quality, distorted, ugly, bad anatomy'
                },
                'wildcards': {
                    'STYLE': 'wildcards/style.txt',
                    'SUBJECT': 'wildcards/subject.txt'
                },
                'generation_settings': {
                    'steps': 20,
                    'width': 512,
                    'height': 512,
                    'batch_size': 1,
                    'sampler': 'Euler a',
                    'cfg_scale': 7.0,
                    'seed': 'random'
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
                    'output_dir': 'outputs/quick_start',
                    'filename_pattern': '{prompt_hash}_{seed}_{timestamp}',
                    'save_metadata': True,
                    'save_prompt_list': True
                },
                'wildcard_settings': {
                    'randomization_mode': 'smart_cycle',
                    'cycle_length': 10,
                    'shuffle_on_reset': True
                },
                'alwayson_scripts': {}
            }
        },
        {
            'name': 'Anime Style',
            'description': 'Configuration for anime and manga style artwork',
            'template': {
                'name': 'Anime Style',
                'description': 'Generate anime and manga style artwork',
                'model_type': 'sd',
                'prompt_settings': {
                    'base_prompt': 'anime style __CHARACTER__ __ACTION__ __SETTING__, __ART_STYLE__',
                    'negative_prompt': 'blurry, low quality, distorted, ugly, bad anatomy, realistic'
                },
                'wildcards': {
                    'CHARACTER': 'wildcards/people_types.txt',
                    'ACTION': 'wildcards/portrait_poses.txt',
                    'SETTING': 'wildcards/locations.txt',
                    'ART_STYLE': 'wildcards/style.txt'
                },
                'generation_settings': {
                    'steps': 25,
                    'width': 512,
                    'height': 768,
                    'batch_size': 1,
                    'sampler': 'DPM++ 2M Karras',
                    'cfg_scale': 8.0,
                    'seed': 'random'
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
                    'output_dir': 'outputs/anime_style',
                    'filename_pattern': '{prompt_hash}_{seed}_{timestamp}',
                    'save_metadata': True,
                    'save_prompt_list': True
                },
                'wildcard_settings': {
                    'randomization_mode': 'smart_cycle',
                    'cycle_length': 15,
                    'shuffle_on_reset': True
                },
                'alwayson_scripts': {}
            }
        },
        {
            'name': 'Landscape Photography',
            'description': 'Configuration for landscape photography',
            'template': {
                'name': 'Landscape Photography',
                'description': 'High-quality landscape photography',
                'model_type': 'sd',
                'prompt_settings': {
                    'base_prompt': 'a stunning __STYLE__ photograph of __LOCATION__, __LIGHTING__, __WEATHER__',
                    'negative_prompt': 'blurry, low quality, distorted, ugly, bad anatomy, watermark'
                },
                'wildcards': {
                    'STYLE': 'wildcards/landscape_styles.txt',
                    'LOCATION': 'wildcards/landscape_locations.txt',
                    'LIGHTING': 'wildcards/lighting_conditions.txt',
                    'WEATHER': 'wildcards/weather_conditions.txt'
                },
                'generation_settings': {
                    'steps': 30,
                    'width': 1024,
                    'height': 768,
                    'batch_size': 1,
                    'sampler': 'DPM++ 2M Karras',
                    'cfg_scale': 7.0,
                    'seed': 'random'
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
                    'output_dir': 'outputs/landscape_photography',
                    'filename_pattern': '{prompt_hash}_{seed}_{timestamp}',
                    'save_metadata': True,
                    'save_prompt_list': True
                },
                'wildcard_settings': {
                    'randomization_mode': 'smart_cycle',
                    'cycle_length': 20,
                    'shuffle_on_reset': True
                },
                'alwayson_scripts': {}
            }
        }
    ]
    
    return jsonify(templates)


@app.route('/api/config/<config_name>', methods=['PUT'])
def update_config(config_name):
    """Update an existing configuration."""
    try:
        config_data = request.get_json()
        if not config_data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        # Validate and save config
        config_handler.save_config(config_name, config_data)
        
        logger.log_config_operation('update', config_name, True)
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully'
        })
        
    except Exception as e:
        logger.log_config_operation('update', config_name, False, {'error': str(e)})
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    """Delete a configuration."""
    try:
        config_handler.delete_config(config_name)
        
        logger.log_config_operation('delete', config_name, True)
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted successfully'
        })
        
    except Exception as e:
        logger.log_config_operation('delete', config_name, False, {'error': str(e)})
        return jsonify({'error': str(e)}), 400


# Output Management Endpoints
@app.route('/api/outputs/summary')
def get_output_summary():
    """Get output summary."""
    try:
        config_name = request.args.get('config_name')
        summary = output_manager.get_output_summary(config_name)
        return jsonify(summary)
    except Exception as e:
        logger.log_error(f"Failed to get output summary: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/outputs/search')
def search_outputs():
    """Search for images by prompt content."""
    try:
        query = request.args.get('query', '')
        config_name = request.args.get('config_name')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = output_manager.search_images(query, config_name)
        return jsonify(results)
    except Exception as e:
        logger.log_error(f"Failed to search outputs: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/outputs/cleanup', methods=['POST'])
def cleanup_outputs():
    """Clean up old output files."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 30)
        config_name = data.get('config_name')
        
        cleaned_files = output_manager.cleanup_old_files(days_to_keep, config_name)
        
        logger.log_app_event('output_cleanup', {
            'days_to_keep': days_to_keep,
            'config_name': config_name,
            'files_cleaned': len(cleaned_files)
        })
        
        return jsonify({
            'success': True,
            'files_cleaned': len(cleaned_files),
            'cleaned_files': cleaned_files
        })
    except Exception as e:
        logger.log_error(f"Failed to cleanup outputs: {e}")
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
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/logs/cleanup', methods=['POST'])
def cleanup_logs():
    """Clean up old log files."""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 30)
        
        logger.cleanup_old_logs(days_to_keep)
        
        return jsonify({
            'success': True,
            'message': f'Logs older than {days_to_keep} days cleaned up'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/missing_wildcards', methods=['GET'])
def get_missing_wildcards(config_name):
    """Get missing wildcards and files for a config."""
    try:
        missing = config_handler.get_missing_wildcards(config_name)
        return jsonify(missing)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/<config_name>/create_missing_wildcards', methods=['POST'])
def create_missing_wildcards(config_name):
    """Create missing wildcard files for a config."""
    try:
        created = config_handler.create_missing_wildcard_files(config_name)
        return jsonify({'created': created, 'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Error handling
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.log_error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.log_error(f"Unhandled exception: {e}")
    return jsonify({'error': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    print("Starting Forge API Tool Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 