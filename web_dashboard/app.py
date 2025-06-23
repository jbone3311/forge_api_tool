from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import os
import sys
import json
import time
from datetime import datetime

# Add the core directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from core.config_handler import ConfigHandler
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.forge_api import ForgeAPIClient
from core.batch_runner import BatchRunner

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
def get_configs():
    """Get list of all configurations."""
    configs = config_handler.list_configs()
    return jsonify(configs)


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
    """Get Forge API status."""
    try:
        connected = forge_client.test_connection()
        models = forge_client.get_models()
        samplers = forge_client.get_samplers()
        
        return jsonify({
            'connected': connected,
            'models': models,
            'samplers': samplers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


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


if __name__ == '__main__':
    print("Starting Forge API Tool Dashboard...")
    print("Access the dashboard at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 