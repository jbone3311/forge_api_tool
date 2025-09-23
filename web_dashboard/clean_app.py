#!/usr/bin/env python3
"""
Clean Forge API Tool - Organized interface with wildcard file management.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_config_handler import EnhancedConfigHandler
from core.output_manager import OutputManager
from core.centralized_logger import logger
from core.enhanced_prompt_builder import EnhancedPromptBuilder
from core.mock_forge_api import create_forge_client, get_available_providers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-clean-app-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize core components
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))
prompt_builder = EnhancedPromptBuilder(wildcards_base_dir="../wildcards")
config_handler = EnhancedConfigHandler(settings_dir="../image_settings", images_dir="../image_settings/images")

# Global API client
api_client = None
current_api_type = "local"

# Job queue for tracking generation jobs
job_queue = {
    'jobs': [],
    'next_id': 1
}

def initialize_api_client(api_type: str = None):
    """Initialize the API client with specified provider."""
    global api_client, current_api_type
    
    if api_type is None:
        api_type = current_api_type
    
    api_client = create_forge_client(use_mock=True, api_type=api_type)
    current_api_type = api_type
    
    logger.info(f"Clean app initialized with {api_type} API provider")
    return api_client

# Initialize with default provider
initialize_api_client()

def create_generation_job(job_data):
    """Create a generation job and process it."""
    job_id = job_queue['next_id']
    job_queue['next_id'] += 1
    
    job = {
        'id': job_id,
        'config_name': job_data.get('config_name', 'default'),
        'prompt': job_data.get('prompt', ''),
        'negative_prompt': job_data.get('negative_prompt', ''),
        'steps': job_data.get('steps', 20),
        'cfg_scale': job_data.get('cfg_scale', 7.0),
        'width': job_data.get('width', 512),
        'height': job_data.get('height', 512),
        'seed': job_data.get('seed', -1),
        'batch_size': job_data.get('batch_size', 1),
        'batch_count': job_data.get('batch_count', 1),
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'progress': 0,
        'api_provider': current_api_type
    }
    
    job_queue['jobs'].append(job)
    
    # Process job in background
    def process_job(job):
        """Process a generation job."""
        try:
            job['status'] = 'running'
            job['started_at'] = datetime.now().isoformat()
            
            # Emit status update
            socketio.emit('job_status_update', {
                'job_id': job['id'],
                'status': 'running'
            })
            
            # Load configuration
            settings_info = config_handler.get_setting(job['config_name'])
            if not settings_info:
                raise Exception(f"Settings '{job['config_name']}' not found")
            config = settings_info['config']
            
            # Override with job settings
            config['prompt_settings']['base_prompt'] = job['prompt']
            config['prompt_settings']['negative_prompt'] = job['negative_prompt']
            config['generation_settings'].update({
                'steps': job['steps'],
                'cfg_scale': job['cfg_scale'],
                'width': job['width'],
                'height': job['height'],
                'seed': job['seed']
            })
            
            # Process wildcards using enhanced prompt builder
            processed_prompt = prompt_builder.build_prompt(config)
            config['prompt_settings']['base_prompt'] = processed_prompt
            
            # Prepare payload
            payload = api_client._prepare_payload(config)
            
            # Simulate progress updates
            steps = job['steps']
            for i in range(steps):
                if job['status'] == 'cancelled':
                    break
                
                job['progress'] = (i + 1) / steps * 100
                job['current_step'] = i + 1
                
                # Emit progress update
                socketio.emit('job_progress', {
                    'job_id': job['id'],
                    'progress': job['progress'],
                    'current_step': job['current_step'],
                    'total_steps': steps
                })
                
                time.sleep(0.1)  # Simulate processing time
            
            if job['status'] != 'cancelled':
                # Generate image
                success, image_data, metadata = api_client.generate_image(payload)
                
                if success:
                    # Save image
                    output_path = output_manager.save_image(
                        image_data, job['config_name'], processed_prompt,
                        metadata.get('seed', -1),
                        config['generation_settings'],
                        config['model_settings']
                    )
                    
                    job['status'] = 'completed'
                    job['completed_at'] = datetime.now().isoformat()
                    job['progress'] = 100
                    job['output_path'] = output_path
                    job['metadata'] = metadata
                    job['processed_prompt'] = processed_prompt
                    
                    socketio.emit('job_completed', {
                        'job_id': job['id'],
                        'output_path': output_path,
                        'metadata': metadata,
                        'processed_prompt': processed_prompt
                    })
                else:
                    job['status'] = 'failed'
                    job['failed_at'] = datetime.now().isoformat()
                    job['error'] = 'Generation failed'
                    
                    socketio.emit('job_failed', {
                        'job_id': job['id'],
                        'error': 'Generation failed'
                    })
        
        except Exception as e:
            job['status'] = 'failed'
            job['failed_at'] = datetime.now().isoformat()
            job['error'] = str(e)
            
            logger.error(f"Job {job['id']} failed: {e}")
            
            socketio.emit('job_failed', {
                'job_id': job['id'],
                'error': str(e)
            })
    
    # Start processing in background
    threading.Thread(target=process_job, args=(job,), daemon=True).start()
    
    return job

@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Get image settings
        image_settings = config_handler.get_all_settings()
        
        # Get output statistics
        output_stats = output_manager.get_output_statistics()
        
        # Get queue status
        queue_status = {
            'total_jobs': len(job_queue['jobs']),
            'pending_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'pending']),
            'running_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'running']),
            'completed_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'completed']),
            'failed_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'failed'])
        }
        
        # Get API info
        api_info = {
            'current_provider': current_api_type,
            'available_providers': get_available_providers(),
            'is_connected': api_client.test_connection() if api_client else False
        }
        
        # Get wildcard information
        wildcard_info = prompt_builder.get_wildcard_info()
        available_wildcards = prompt_builder.get_available_wildcards()
        
        logger.info("Clean app dashboard accessed")
        
        return render_template('clean_dashboard.html', 
                             configs=image_settings, 
                             output_stats=output_stats,
                             api_info=api_info,
                             wildcard_info=wildcard_info,
                             available_wildcards=available_wildcards)
                             
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return render_template('clean_dashboard.html', 
                             configs={}, 
                             output_stats={'total_outputs': 0},
                             api_info={'current_provider': 'unknown', 'available_providers': [], 'is_connected': False},
                             wildcard_info={},
                             available_wildcards=[],
                             error=str(e))

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/settings')
def get_settings():
    """Get all image settings."""
    try:
        settings = config_handler.get_all_settings()
        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/<settings_name>')
def get_setting(settings_name):
    """Get specific image settings."""
    try:
        settings_info = config_handler.get_setting(settings_name)
        if not settings_info:
            return jsonify({'success': False, 'error': 'Settings not found'})
        return jsonify({'success': True, 'settings': settings_info})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/<settings_name>/thumbnail')
def get_setting_thumbnail(settings_name):
    """Get thumbnail for a settings file."""
    try:
        thumbnail_info = config_handler.get_thumbnail_info(settings_name)
        if not thumbnail_info:
            return jsonify({'success': False, 'error': 'Thumbnail not found'})
        
        from flask import send_file
        # Convert relative path to absolute path
        import os
        thumbnail_path = os.path.abspath(thumbnail_info['path'])
        return send_file(thumbnail_path)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/providers')
def get_providers():
    """Get available API providers."""
    try:
        providers = get_available_providers()
        return jsonify({
            'success': True, 
            'providers': providers,
            'current_provider': current_api_type
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/providers/<provider_type>', methods=['POST'])
def switch_provider(provider_type):
    """Switch to a different API provider."""
    try:
        if provider_type not in get_available_providers():
            return jsonify({'success': False, 'error': 'Invalid provider type'})
        
        global api_client, current_api_type
        api_client = initialize_api_client(provider_type)
        
        logger.info(f"Switched to {provider_type} provider")
        
        return jsonify({
            'success': True, 
            'provider': provider_type,
            'message': f'Switched to {provider_type} provider'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_image():
    """Generate image using the mock API."""
    try:
        data = request.get_json()
        
        if not data.get('prompt'):
            return jsonify({'success': False, 'error': 'Prompt is required'})
        
        # Create and process job
        job = create_generation_job(data)
        
        logger.info(f"Generation job {job['id']} created")
        
        return jsonify({
            'success': True, 
            'job_id': job['id'],
            'message': 'Generation job added to queue',
            'provider': current_api_type
        })
        
    except Exception as e:
        logger.error(f"Error in generation: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/queue/status')
def get_queue_status():
    """Get queue status."""
    try:
        status = {
            'total_jobs': len(job_queue['jobs']),
            'pending_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'pending']),
            'running_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'running']),
            'completed_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'completed']),
            'failed_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'failed']),
            'jobs': job_queue['jobs'],
            'current_provider': current_api_type
        }
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """Get system status."""
    try:
        status = {
            'api_connected': api_client.test_connection() if api_client else False,
            'api_provider': current_api_type,
            'available_providers': get_available_providers(),
            'queue_size': len(job_queue['jobs']),
            'active_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'running']),
            'outputs_count': output_manager.get_output_statistics().get('total_outputs', 0),
            'settings_count': len(config_handler.get_all_settings()),
            'wildcards_count': len(prompt_builder.get_available_wildcards()),
            'system_status': 'healthy'
        }
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wildcards')
def get_wildcards():
    """Get all wildcards with enhanced information."""
    try:
        wildcard_info = prompt_builder.get_wildcard_info()
        available_wildcards = prompt_builder.get_available_wildcards()
        
        return jsonify({
            'success': True, 
            'wildcards': wildcard_info,
            'available_wildcards': available_wildcards,
            'total_wildcards': len(available_wildcards)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wildcards/<wildcard_name>')
def get_wildcard_items(wildcard_name):
    """Get items from a specific wildcard file."""
    try:
        manager = prompt_builder.wildcard_manager.get_manager(wildcard_name)
        if not manager:
            return jsonify({'success': False, 'error': 'Wildcard not found'})
        
        return jsonify({
            'success': True,
            'wildcard_name': wildcard_name,
            'items': manager.items,
            'item_count': len(manager.items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wildcards/process', methods=['POST'])
def process_wildcards():
    """Process wildcards in a prompt using enhanced system."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'})
        
        # Validate prompt first
        validation = prompt_builder.validate_prompt(prompt)
        
        # Process the prompt
        processed_prompt = prompt_builder.wildcard_manager.process_prompt(prompt)
        
        # Get preview of multiple variations
        preview_count = data.get('preview_count', 3)
        previews = prompt_builder.wildcard_manager.preview_prompt(prompt, preview_count)
        
        return jsonify({
            'success': True, 
            'original_prompt': prompt,
            'processed_prompt': processed_prompt,
            'previews': previews,
            'validation': validation,
            'replacements_made': prompt != processed_prompt
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/outputs/list')
def list_outputs():
    """List outputs."""
    try:
        outputs = output_manager.get_output_statistics()
        
        # Get detailed file list
        output_dir = output_manager.base_output_dir
        files = []
        
        if os.path.exists(output_dir):
            for root, dirs, filenames in os.walk(output_dir):
                for filename in filenames:
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.txt')):
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, output_dir)
                        
                        stat = os.stat(file_path)
                        files.append({
                            'name': filename,
                            'path': rel_path,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'type': 'image/png' if filename.endswith('.png') else 'text/plain'
                        })
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True, 
            'outputs': outputs,
            'files': files[:50]  # Limit to 50 most recent
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# ============================================================================
# WEBSOCKET HANDLERS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info("Client connected to clean app")
    emit('status', {'message': 'Connected to clean app', 'provider': current_api_type})
    
    # Send initial status
    emit('status_update', {
        'queue_size': len(job_queue['jobs']),
        'active_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'running']),
        'system_health': 'healthy',
        'api_provider': current_api_type,
        'wildcards_count': len(prompt_builder.get_available_wildcards())
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info("Client disconnected from clean app")

@socketio.on('request_status')
def handle_status_request():
    """Handle status request via WebSocket."""
    try:
        status = {
            'api_connected': api_client.test_connection() if api_client else False,
            'api_provider': current_api_type,
            'queue_size': len(job_queue['jobs']),
            'active_jobs': len([j for j in job_queue['jobs'] if j['status'] == 'running']),
            'outputs_count': output_manager.get_output_statistics().get('total_outputs', 0),
            'settings_count': len(config_handler.get_all_settings()),
            'wildcards_count': len(prompt_builder.get_available_wildcards()),
            'system_status': 'healthy'
        }
        emit('status_update', status)
    except Exception as e:
        logger.error(f"Error handling status request: {e}")
        emit('error', {'message': str(e)})

@socketio.on('switch_provider')
def handle_switch_provider(data):
    """Handle provider switch via WebSocket."""
    try:
        provider_type = data.get('provider')
        if provider_type in get_available_providers():
            global api_client, current_api_type
            api_client = initialize_api_client(provider_type)
            
            emit('provider_switched', {
                'provider': provider_type,
                'message': f'Switched to {provider_type} provider'
            })
            
            # Broadcast to all clients
            socketio.emit('provider_update', {
                'provider': provider_type,
                'connected': api_client.test_connection()
            })
        else:
            emit('error', {'message': f'Invalid provider: {provider_type}'})
    except Exception as e:
        logger.error(f"Error switching provider: {e}")
        emit('error', {'message': str(e)})

def open_browser():
    """Open the web browser to the dashboard."""
    import webbrowser
    import time
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Open the browser
    webbrowser.open('http://localhost:8081')
    print("🌐 Browser opened automatically!")

if __name__ == '__main__':
    print("🎯 Starting Forge API Tool - Clean App")
    print("📱 Dashboard will be available at: http://localhost:8081")
    print(f"📡 Current API Provider: {current_api_type}")
    print("✅ Features:")
    print("   • Organized wildcard file management")
    print("   • Multiple API provider support")
    print("   • Real-time generation progress")
    print("   • Configuration management")
    print("   • Advanced wildcard processing")
    print("   • Output management")
    print("   • Clean, organized interface")
    print("⚠️  Note: All images are mock generated - no real API calls")
    
    # Show wildcard information
    available_wildcards = prompt_builder.get_available_wildcards()
    print(f"🎲 Discovered {len(available_wildcards)} wildcard files:")
    for i, wildcard in enumerate(available_wildcards[:10]):  # Show first 10
        print(f"   • {wildcard}")
    if len(available_wildcards) > 10:
        print(f"   • ... and {len(available_wildcards) - 10} more")
    
    print("🌐 Opening browser automatically...")
    
    # Start browser opening in a separate thread
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    socketio.run(app, host='0.0.0.0', port=8081, debug=True, allow_unsafe_werkzeug=True)
