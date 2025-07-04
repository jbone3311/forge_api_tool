#!/usr/bin/env python3
"""
Simple Forge API Tool - No Complex Services
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_handler import config_handler
from core.output_manager import OutputManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-forge-api-tool'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simple output manager
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))

@app.route('/')
def dashboard():
    """Simple dashboard page."""
    try:
        # Get configurations
        configs = config_handler.get_all_configs()
        
        # Get output statistics
        output_stats = output_manager.get_output_statistics()
        
        return render_template('simple_dashboard.html', 
                             configs=configs, 
                             output_stats=output_stats)
    except Exception as e:
        return render_template('simple_dashboard.html', 
                             configs={}, 
                             output_stats={'total_outputs': 0},
                             error=str(e))

@app.route('/api/configs')
def get_configs():
    """Get all configurations."""
    try:
        configs = config_handler.get_all_configs()
        return jsonify({'success': True, 'configs': configs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/configs/<config_name>')
def get_config(config_name):
    """Get specific configuration."""
    try:
        config = config_handler.get_config(config_name)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/outputs/list')
def list_outputs():
    """List outputs."""
    try:
        outputs = output_manager.list_outputs()
        return jsonify({'success': True, 'outputs': outputs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_status():
    """Simple status endpoint."""
    return jsonify({
        'success': True,
        'status': {
            'api_connected': False,  # Don't try to connect to external APIs
            'queue_size': 0,
            'outputs_count': output_manager.get_output_statistics().get('total_outputs', 0)
        }
    })

@app.route('/api/logs')
def get_logs():
    """Get application logs."""
    try:
        # This is a simple implementation - in a real app you'd want proper logging
        return jsonify({
            'success': True,
            'logs': [
                {
                    'timestamp': '2025-07-02 08:51:00',
                    'level': 'INFO',
                    'message': 'Simple Forge API Tool started successfully'
                },
                {
                    'timestamp': '2025-07-02 08:51:01',
                    'level': 'INFO', 
                    'message': f'Loaded {len(config_handler.get_all_configs())} configurations'
                }
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    print("🚀 Starting Simple Forge API Tool...")
    print("📱 Dashboard will be available at: http://localhost:4000")
    print("⚠️  Note: This is a simplified version without external API dependencies")
    
    socketio.run(app, host='0.0.0.0', port=4000, debug=True) 