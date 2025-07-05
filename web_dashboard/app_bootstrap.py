#!/usr/bin/env python3
"""
Forge API Tool Web Dashboard - Bootstrap Version

A modern Flask-based web interface using Bootstrap 5 for responsive design.
This is a client-only application that connects to external APIs like Automatic1111.
"""

import os
import sys
import json
import time
import base64
import mimetypes
import threading
import asyncio
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, session, flash, redirect, url_for
from flask_socketio import SocketIO, emit
import re
from pathlib import Path

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_handler import config_handler
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.wildcard_manager import WildcardManagerFactory
from core.prompt_builder import PromptBuilder
from core.job_queue import job_queue
from core.batch_runner import batch_runner

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-bootstrap-secret'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize core components
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))
wildcard_manager_factory = WildcardManagerFactory()
prompt_builder = PromptBuilder(wildcard_manager_factory)

# External API connection settings
external_api_config = {
    'automatic1111': {
        'url': 'http://localhost:7860',
        'timeout': 30,
        'retry_attempts': 3
    },
    'comfyui': {
        'url': 'http://localhost:8188',
        'timeout': 30,
        'retry_attempts': 3
    },
    'rundiffusion': {
        'url': '',
        'username': '',
        'password': '',
        'timeout': 60,
        'api_key': ''
    }
}

# Current API connection
current_api = {
    'type': 'automatic1111',
    'connected': False,
    'last_test': None
}

# Job queue for managing generation requests
job_queue = {
    'jobs': [],
    'next_id': 1,
    'processing': False,
    'max_concurrent': 2
}

# System status
system_status = {
    'api_connected': False,
    'queue_size': 0,
    'active_jobs': 0,
    'system_health': 'healthy',
    'last_update': datetime.now()
}

# Application settings
app_settings = {
    'generation_settings': {
        'default_steps': 20,
        'default_cfg_scale': 7.0,
        'default_width': 512,
        'default_height': 512,
        'max_batch_size': 4
    },
    'output_settings': {
        'auto_organize': True,
        'keep_metadata': True,
        'compression_quality': 95
    },
    'template_settings': {
        'default_model': 'sd_xl_base_1.0.safetensors',
        'default_sampler': 'euler',
        'default_scheduler': 'karras',
        'default_seed': -1,
        'auto_load_templates': True,
        'template_validation': True,
        'template_backup': True,
        'template_cache_size': 50,
        'template_auto_save': 5,
        'default_category': 'general',
        'template_tags': ''
    }
}

def test_api_connection(api_type='automatic1111'):
    """Test connection to external API."""
    try:
        config = external_api_config.get(api_type, external_api_config['automatic1111'])
        url = config['url']
        
        if api_type == 'automatic1111':
            # Test Automatic1111 API
            response = requests.get(f"{url}/sdapi/v1/sd-models", timeout=config['timeout'])
            if response.status_code == 200:
                current_api['connected'] = True
                current_api['type'] = api_type
                current_api['last_test'] = datetime.now()
                system_status['api_connected'] = True
                return True
        elif api_type == 'comfyui':
            # Test ComfyUI API
            response = requests.get(f"{url}/system_stats", timeout=config['timeout'])
            if response.status_code == 200:
                current_api['connected'] = True
                current_api['type'] = api_type
                current_api['last_test'] = datetime.now()
                system_status['api_connected'] = True
                return True
        elif api_type == 'rundiffusion':
            # Test RunDiffusion API
            if config.get('api_key'):
                headers = {'Authorization': f'Bearer {config["api_key"]}'}
                response = requests.get(f"{url}/api/v1/models", headers=headers, timeout=config['timeout'])
                if response.status_code == 200:
                    current_api['connected'] = True
                    current_api['type'] = api_type
                    current_api['last_test'] = datetime.now()
                    system_status['api_connected'] = True
                    return True
        
        current_api['connected'] = False
        system_status['api_connected'] = False
        return False
        
    except Exception as e:
        logger.error(f"API connection test failed: {e}")
        current_api['connected'] = False
        system_status['api_connected'] = False
        return False

def send_to_external_api(payload, api_type=None):
    """Send generation request to external API."""
    if api_type is None:
        api_type = current_api['type']
    
    config = external_api_config.get(api_type, external_api_config['automatic1111'])
    
    try:
        if api_type == 'automatic1111':
            # Send to Automatic1111
            response = requests.post(
                f"{config['url']}/sdapi/v1/txt2img",
                json=payload,
                timeout=config['timeout']
            )
            return response.json() if response.status_code == 200 else None
            
        elif api_type == 'comfyui':
            # Send to ComfyUI
            response = requests.post(
                f"{config['url']}/prompt",
                json=payload,
                timeout=config['timeout']
            )
            return response.json() if response.status_code == 200 else None
            
        elif api_type == 'rundiffusion':
            # Send to RunDiffusion
            headers = {'Authorization': f'Bearer {config["api_key"]}'}
            response = requests.post(
                f"{config['url']}/api/v1/generate",
                json=payload,
                headers=headers,
                timeout=config['timeout']
            )
            return response.json() if response.status_code == 200 else None
            
    except Exception as e:
        logger.error(f"Error sending to external API: {e}")
        return None

def process_job(job):
    """Process a generation job by sending to external API."""
    try:
        job['status'] = 'running'
        job['started_at'] = datetime.now().isoformat()
        
        # Prepare payload for external API
        payload = {
            'prompt': job.get('prompt', ''),
            'negative_prompt': job.get('negative_prompt', ''),
            'steps': job.get('steps', 20),
            'cfg_scale': job.get('cfg_scale', 7.0),
            'width': job.get('width', 512),
            'height': job.get('height', 512),
            'batch_size': job.get('batch_size', 1),
            'sampler_name': job.get('sampler', 'Euler a'),
            'seed': job.get('seed', -1)
        }
        
        # Send to external API
        result = send_to_external_api(payload)
        
        if result:
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            job['result'] = result
            
            # Save output
            if 'images' in result:
                save_output_images(result['images'], job)
            
            socketio.emit('job_completed', {
                'job_id': job['id'],
                'result': result
            })
        else:
            job['status'] = 'failed'
            job['error'] = 'External API request failed'
            job['failed_at'] = datetime.now().isoformat()
            
            socketio.emit('job_failed', {
                'job_id': job['id'],
                'error': 'External API request failed'
            })
        
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        job['failed_at'] = datetime.now().isoformat()
        logger.error(f"Job {job['id']} failed: {e}")
        
        socketio.emit('job_failed', {
            'job_id': job['id'],
            'error': str(e)
        })

def save_output_images(images, job):
    """Save output images from external API."""
    try:
        output_dir = os.path.join(output_manager.base_output_dir, datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(output_dir, exist_ok=True)
        
        for i, image_data in enumerate(images):
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            
            # Save image
            filename = f"job_{job['id']}_{i+1}.png"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            job['output_files'] = job.get('output_files', [])
            job['output_files'].append(filepath)
        
    except Exception as e:
        logger.error(f"Error saving output images: {e}")

# Background job processor
def background_job_processor():
    """Background thread for processing jobs."""
    while True:
        try:
            pending_jobs = [j for j in job_queue['jobs'] if j['status'] == 'pending']
            running_jobs = [j for j in job_queue['jobs'] if j['status'] == 'running']
            
            # Start new jobs if we have capacity
            if len(running_jobs) < job_queue['max_concurrent'] and pending_jobs:
                job = pending_jobs[0]
                threading.Thread(target=process_job, args=(job,)).start()
            
            # Update system status
            system_status['queue_size'] = len(job_queue['jobs'])
            system_status['active_jobs'] = len(running_jobs)
            system_status['last_update'] = datetime.now()
            
            time.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            logger.error(f"Background processor error: {e}")
            time.sleep(5)

# Start background processor
threading.Thread(target=background_job_processor, daemon=True).start()

# Test initial API connection
test_api_connection()

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Load configurations
        configs = config_handler.get_all_configs()
        
        # Load outputs
        outputs = output_manager.list_outputs()
        
        return render_template('dashboard_bootstrap.html',
                             configs=configs,
                             outputs=outputs,
                             settings=app_settings,
                             system_status=system_status,
                             current_api=current_api)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard_bootstrap.html',
                             configs={},
                             outputs=[],
                             settings=app_settings,
                             system_status=system_status,
                             current_api=current_api)

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    emit('status_update', system_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request."""
    emit('status_update', system_status)

@socketio.on('test_connection')
def handle_test_connection(data):
    """Handle API connection test request."""
    api_type = data.get('api_type', 'automatic1111')
    success = test_api_connection(api_type)
    emit('connection_test_result', {'success': success, 'api_type': api_type})

@socketio.on('generate_image')
def handle_generate_image(data):
    """Handle image generation request."""
    try:
        # Create job
        job = {
            'id': job_queue['next_id'],
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'prompt': data.get('prompt', ''),
            'negative_prompt': data.get('negative_prompt', ''),
            'steps': data.get('steps', 20),
            'cfg_scale': data.get('cfg_scale', 7.0),
            'width': data.get('width', 512),
            'height': data.get('height', 512),
            'batch_size': data.get('batch_size', 1),
            'sampler': data.get('sampler', 'Euler a'),
            'seed': data.get('seed', -1),
            'config_name': data.get('config_name', '')
        }
        
        job_queue['next_id'] += 1
        job_queue['jobs'].append(job)
        
        emit('job_created', {'job_id': job['id']})
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        emit('error', {'message': str(e)})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('dashboard_bootstrap.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('dashboard_bootstrap.html', error="Internal server error"), 500

@app.errorhandler(413)
def too_large(error):
    """Handle file too large errors."""
    return render_template('dashboard_bootstrap.html', error="File too large"), 413

if __name__ == '__main__':
    print("Starting Forge API Tool Web Dashboard (Bootstrap Version)")
    print("This is a client-only application that connects to external APIs.")
    print("Make sure your external API (Automatic1111, ComfyUI, etc.) is running.")
    print()
    
    # Test API connection on startup
    if test_api_connection():
        print(f"✓ Connected to {current_api['type']} API")
    else:
        print("✗ Failed to connect to external API")
        print("Please check your API configuration and ensure the external API is running.")
    
    print()
    print("Starting web server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 