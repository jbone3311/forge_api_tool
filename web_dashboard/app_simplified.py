#!/usr/bin/env python3
"""
Forge API Tool Web Dashboard - Enhanced Simplified Version

A comprehensive Flask-based web interface with all features but no external dependencies.
"""

import os
import sys
import json
import time
import base64
import mimetypes
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO, emit
import re

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_handler import config_handler
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.wildcard_manager import WildcardManagerFactory

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-enhanced-simplified'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize output manager
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))

# Initialize wildcard manager
wildcard_manager_factory = WildcardManagerFactory()
# For now, we'll use a default wildcard path - this can be enhanced later
wildcard_manager = None  # We'll initialize this when needed

# Simple job queue (in-memory)
simple_job_queue = {
    'jobs': [],
    'next_id': 1
}

# Simple settings storage
app_settings = {
    'api_type': 'local',
    'local_config': {
        'url': 'http://localhost:3000',
        'timeout': 30
    },
    'rundiffusion_config': {
        'url': '',
        'username': '',
        'password': '',
        'timeout': 60
    }
}

# Test results storage
test_results = {
    'unit_tests': [],
    'integration_tests': [],
    'e2e_tests': [],
    'coverage': {},
    'last_run': None
}

@app.route('/')
def dashboard():
    """Main dashboard page - enhanced simplified version."""
    try:
        logger.info("Dashboard accessed - Enhanced simplified version")
        
        # Get configurations
        configs = config_handler.get_all_configs()
        logger.info(f"Loaded {len(configs)} configurations")
        
        # Get output statistics
        output_stats = output_manager.get_output_statistics()
        
        # Get queue status
        queue_status = {
            'total_jobs': len(simple_job_queue['jobs']),
            'pending_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'pending']),
            'running_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'running']),
            'completed_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'completed']),
            'failed_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'failed'])
        }
        
        logger.log_app_event("dashboard_accessed", {
            "config_count": len(configs),
            "output_count": output_stats.get('total_outputs', 0),
            "queue_size": queue_status['total_jobs'],
            "api_connected": False  # Simplified - no external API
        })
        
        return render_template('enhanced_dashboard.html', 
                             configs=configs, 
                             output_stats=output_stats)
                             
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return render_template('simple_dashboard.html', 
                             configs={}, 
                             output_stats={'total_outputs': 0},
                             error=str(e))

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

@app.route('/api/configs')
def get_configs():
    """Get all configurations."""
    try:
        configs = config_handler.get_all_configs()
        logger.log_app_event("configs_retrieved", {"count": len(configs)})
        return jsonify({'success': True, 'configs': configs})
    except Exception as e:
        logger.error(f"Error getting configs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/<config_name>')
def get_config(config_name):
    """Get specific configuration."""
    try:
        config = config_handler.get_config(config_name)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f"Error getting config {config_name}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs', methods=['POST'])
def create_config():
    """Create a new configuration."""
    try:
        data = request.get_json()
        config_name = data.get('name', f'config_{int(time.time())}')
        config_handler.save_config(config_name, data)
        logger.log_app_event("config_created", {"config_name": config_name})
        return jsonify({'success': True, 'config_name': config_name})
    except Exception as e:
        logger.error(f"Error creating config: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/<config_name>', methods=['PUT'])
def update_config(config_name):
    """Update a configuration."""
    try:
        data = request.get_json()
        config_handler.save_config(config_name, data)
        logger.log_app_event("config_updated", {"config_name": config_name})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating config {config_name}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    """Delete a configuration."""
    try:
        config_handler.delete_config(config_name)
        logger.log_app_event("config_deleted", {"config_name": config_name})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting config {config_name}: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# OUTPUT MANAGEMENT
# ============================================================================

@app.route('/api/outputs/list')
def list_outputs():
    """List outputs."""
    try:
        outputs = output_manager.get_output_statistics()
        logger.log_app_event("outputs_retrieved", {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "config_name": None,
            "output_count": outputs.get('total_outputs', 0)
        })
        return jsonify({'success': True, 'outputs': outputs})
    except Exception as e:
        logger.error(f"Error listing outputs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/outputs/<path:filepath>')
def download_output(filepath):
    """Download an output file."""
    try:
        # Ensure the filepath is safe
        safe_path = os.path.normpath(filepath)
        if safe_path.startswith('..') or safe_path.startswith('/'):
            return jsonify({'success': False, 'error': 'Invalid file path'})
        
        output_dir = output_manager.base_output_dir
        file_path = os.path.join(output_dir, safe_path)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        logger.log_app_event("output_downloaded", {"filepath": filepath})
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading output {filepath}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/outputs/delete/<path:filepath>', methods=['DELETE'])
def delete_output(filepath):
    """Delete an output file."""
    try:
        # Ensure the filepath is safe
        safe_path = os.path.normpath(filepath)
        if safe_path.startswith('..') or safe_path.startswith('/'):
            return jsonify({'success': False, 'error': 'Invalid file path'})
        
        output_dir = output_manager.base_output_dir
        file_path = os.path.join(output_dir, safe_path)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'})
        
        os.remove(file_path)
        logger.log_app_event("output_deleted", {"filepath": filepath})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting output {filepath}: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# QUEUE MANAGEMENT
# ============================================================================

@app.route('/api/queue/status')
def get_queue_status():
    """Get queue status."""
    try:
        status = {
            'total_jobs': len(simple_job_queue['jobs']),
            'pending_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'pending']),
            'running_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'running']),
            'completed_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'completed']),
            'failed_jobs': len([j for j in simple_job_queue['jobs'] if j['status'] == 'failed']),
            'jobs': simple_job_queue['jobs']
        }
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/add', methods=['POST'])
def add_job():
    """Add a job to the queue."""
    try:
        data = request.get_json()
        job = {
            'id': simple_job_queue['next_id'],
            'config_name': data.get('config_name', 'Unknown'),
            'prompt': data.get('prompt', ''),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'progress': 0
        }
        simple_job_queue['jobs'].append(job)
        simple_job_queue['next_id'] += 1
        
        logger.log_app_event("job_added", {
            "job_id": job['id'],
            "config_name": job['config_name']
        })
        
        return jsonify({'success': True, 'job_id': job['id']})
    except Exception as e:
        logger.error(f"Error adding job: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/job/<int:job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a job."""
    try:
        job = next((j for j in simple_job_queue['jobs'] if j['id'] == job_id), None)
        if job:
            job['status'] = 'cancelled'
            logger.log_app_event("job_cancelled", {"job_id": job_id})
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Job not found'})
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/clear', methods=['POST'])
def clear_queue():
    """Clear the queue."""
    try:
        simple_job_queue['jobs'] = []
        logger.log_app_event("queue_cleared", {})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing queue: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# IMAGE ANALYSIS
# ============================================================================

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze an uploaded image."""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        # Save the uploaded file temporarily
        upload_dir = os.path.join(output_manager.base_output_dir, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"upload_{int(time.time())}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Analyze the image (simplified analysis)
        file_size = os.path.getsize(filepath)
        file_type = mimetypes.guess_type(filepath)[0] or 'unknown'
        
        analysis = {
            'filename': filename,
            'file_size': file_size,
            'file_type': file_type,
            'dimensions': 'Unknown (simplified analysis)',
            'colors': 'Unknown (simplified analysis)',
            'objects': 'Unknown (simplified analysis)',
            'text': 'Unknown (simplified analysis)',
            'upload_time': datetime.now().isoformat()
        }
        
        logger.log_app_event("image_analyzed", {
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type
        })
        
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# SETTINGS MANAGEMENT
# ============================================================================

@app.route('/api/settings')
def get_settings():
    """Get API settings."""
    try:
        logger.log_app_event("api_settings_retrieved", app_settings)
        return jsonify({'success': True, 'settings': app_settings})
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update API settings."""
    try:
        data = request.get_json()
        app_settings.update(data)
        logger.log_app_event("api_settings_updated", app_settings)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# STATUS MONITORING
# ============================================================================

@app.route('/api/status')
def get_status():
    """Get system status."""
    try:
        status = {
            'api_connected': False,  # Simplified - no external API
            'queue_size': len(simple_job_queue['jobs']),
            'outputs_count': output_manager.get_output_statistics().get('total_outputs', 0),
            'configs_count': len(config_handler.get_all_configs()),
            'system_status': 'running',
            'uptime': 'Unknown (simplified)',
            'memory_usage': 'Unknown (simplified)',
            'cpu_usage': 'Unknown (simplified)'
        }
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# LOGGING SYSTEM
# ============================================================================

@app.route('/api/logs')
def get_logs():
    """Get application logs."""
    try:
        # Get recent log entries (simplified)
        logs = [
            {
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'message': 'Simplified logging system active',
                'module': 'app_simplified'
            }
        ]
        
        # Add some recent events
        for job in simple_job_queue['jobs'][-5:]:  # Last 5 jobs
            logs.append({
                'timestamp': job['created_at'],
                'level': 'INFO',
                'message': f"Job {job['id']} - {job['config_name']}",
                'module': 'queue'
            })
        
        logger.log_app_event("logs_retrieved", {"count": len(logs)})
        return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear application logs."""
    try:
        # In a real implementation, this would clear log files
        logger.log_app_event("logs_cleared", {})
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# TEST RESULTS
# ============================================================================

@app.route('/api/test-results')
def get_test_results():
    """Get test results."""
    try:
        return jsonify({'success': True, 'results': test_results})
    except Exception as e:
        logger.error(f"Error getting test results: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-results/unit')
def get_unit_test_results():
    """Get unit test results."""
    try:
        return jsonify({'success': True, 'results': test_results['unit_tests']})
    except Exception as e:
        logger.error(f"Error getting unit test results: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-results/integration')
def get_integration_test_results():
    """Get integration test results."""
    try:
        return jsonify({'success': True, 'results': test_results['integration_tests']})
    except Exception as e:
        logger.error(f"Error getting integration test results: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-results/e2e')
def get_e2e_test_results():
    """Get E2E test results."""
    try:
        return jsonify({'success': True, 'results': test_results['e2e_tests']})
    except Exception as e:
        logger.error(f"Error getting E2E test results: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-results/coverage')
def get_test_coverage():
    """Get test coverage."""
    try:
        return jsonify({'success': True, 'coverage': test_results['coverage']})
    except Exception as e:
        logger.error(f"Error getting test coverage: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# WILDCARD MANAGEMENT
# ============================================================================

@app.route('/api/wildcards')
def get_wildcards():
    """Get available wildcards."""
    try:
        # For now, return a simple list of available wildcard files
        wildcard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wildcards")
        wildcards = []
        
        if os.path.exists(wildcard_dir):
            for root, dirs, files in os.walk(wildcard_dir):
                for file in files:
                    if file.endswith('.txt'):
                        rel_path = os.path.relpath(os.path.join(root, file), wildcard_dir)
                        wildcards.append(rel_path.replace('.txt', ''))
        
        logger.log_app_event("wildcards_retrieved", {"count": len(wildcards)})
        return jsonify({'success': True, 'wildcards': wildcards})
    except Exception as e:
        logger.error(f"Error getting wildcards: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wildcards/<wildcard_name>')
def get_wildcard(wildcard_name):
    """Get specific wildcard content."""
    try:
        wildcard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wildcards")
        wildcard_path = os.path.join(wildcard_dir, f"{wildcard_name}.txt")
        
        if not os.path.exists(wildcard_path):
            return jsonify({'success': False, 'error': 'Wildcard not found'})
        
        with open(wildcard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        logger.error(f"Error getting wildcard {wildcard_name}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wildcards/process', methods=['POST'])
def process_wildcards():
    """Process wildcards in a prompt."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Simple wildcard processing - replace {wildcard} with placeholder
        processed_prompt = re.sub(r'\{([^}]+)\}', r'[WILDCARD:\1]', prompt)
        
        return jsonify({'success': True, 'processed_prompt': processed_prompt})
    except Exception as e:
        logger.error(f"Error processing wildcards: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# STATIC FILES AND SOCKET.IO
# ============================================================================

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info("Client connected via WebSocket")
    emit('status', {'message': 'Connected to enhanced simplified server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info("Client disconnected from WebSocket")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request via WebSocket."""
    try:
        status = {
            'api_connected': False,
            'queue_size': len(simple_job_queue['jobs']),
            'outputs_count': output_manager.get_output_statistics().get('total_outputs', 0),
            'configs_count': len(config_handler.get_all_configs()),
            'system_status': 'running'
        }
        emit('status_update', status)
    except Exception as e:
        logger.error(f"Error handling status request: {e}")
        emit('error', {'message': str(e)})

# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting Enhanced Simplified Forge API Tool...")
    print("📱 Dashboard will be available at: http://localhost:4000")
    print("✅ All features included: Configs, Outputs, Queue, Analysis, Settings, Logs, Tests, Wildcards")
    print("⚠️  Note: This is a simplified version without external API dependencies")
    
    socketio.run(app, host='0.0.0.0', port=4000, debug=True) 