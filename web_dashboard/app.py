#!/usr/bin/env python3
"""
Forge API Tool Web Dashboard

A Flask-based web interface for managing Forge API configurations,
generating images, and monitoring the system.
"""

import os
import sys
# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import time
import threading
import webbrowser
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_socketio import SocketIO, emit
import re

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

# Import new modular components
from services.generation_service import GenerationService
from services.queue_service import QueueService
from services.output_service import OutputService
from services.logging_service import LoggingService
from services.settings_service import SettingsService
from services.status_service import StatusService
from routes.generation import generation_bp, init_generation_service
from routes.queue import queue_bp, init_queue_service
from routes.output import output_bp, output_files_bp, init_output_service
from routes.logging import logging_bp, init_logging_service
from routes.settings import settings_bp, init_settings_service
from routes.status import status_bp, handle_status_request, handle_connect, handle_disconnect
from web_dashboard.routes.rundiffusion import rundiffusion_bp
from web_dashboard.routes.config import config_bp
from web_dashboard.routes.image_analysis import image_analysis_bp
from web_dashboard.routes.api_connection import api_connection_bp
from web_dashboard.routes.api_metadata import api_metadata_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forge-api-tool-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
logger = logger

# Initialize output manager with centralized structure
output_manager = OutputManager(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"))

# Initialize Generation Service
generation_service = GenerationService(
    config_handler_instance=config_handler,
    forge_api_client_instance=forge_api_client,
    output_manager_instance=output_manager,
    job_queue_instance=job_queue,
    logger_instance=logger,
    socketio_instance=socketio
)

# Initialize Queue Service
queue_service = QueueService(
    job_queue_instance=job_queue,
    logger_instance=logger
)

# Initialize Output Service
output_service = OutputService(
    output_manager=output_manager,
    logger=logger
)

# Initialize Logging Service
logging_service = LoggingService(
    logger_instance=logger
)

# Initialize Settings Service
settings_service = SettingsService(
    logger_instance=logger,
    forge_api_client_instance=forge_api_client
)

# Initialize Status Service
status_service = StatusService(
    forge_api_client=forge_api_client,
    job_queue=job_queue,
    output_manager=output_manager,
    logger=logger
)

# Initialize the service routes
init_generation_service(generation_service)
init_queue_service(queue_service)
init_output_service(output_service)
init_logging_service(logging_service)
init_settings_service(settings_service)

# Register blueprints
app.register_blueprint(generation_bp)
app.register_blueprint(queue_bp)
app.register_blueprint(output_bp)
app.register_blueprint(output_files_bp)
app.register_blueprint(logging_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(status_bp)
app.register_blueprint(rundiffusion_bp)
app.register_blueprint(config_bp)
app.register_blueprint(image_analysis_bp)
app.register_blueprint(api_connection_bp)
app.register_blueprint(api_metadata_bp)

# Add status service to app context
app.status_service = status_service

# Global state for tracking current generation (legacy - will be removed)
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
        try:
            logger.info("About to call config_handler.get_all_configs()")
            configs = config_handler.get_all_configs()
            logger.info(f"Loaded {len(configs)} configurations")
            logger.info(f"Configs keys: {list(configs.keys())}")
        except Exception as e:
            logger.log_error(f"Error loading configs: {e}")
            import traceback
            logger.log_error(f"Config loading traceback: {traceback.format_exc()}")
            configs = {}
        
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
        
        # Get API connection status (don't let this fail the dashboard)
        try:
            api_status = status_service.get_api_status()
        except Exception as e:
            logger.warning(f"Failed to get API status: {e}")
            api_status = {'connected': False, 'error': str(e)}
        
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

@app.route('/test-dashboard')
def test_dashboard():
    """Test dashboard interface."""
    try:
        return render_template('test-dashboard.html')
    except Exception as e:
        logger.log_error(f"Error loading test dashboard: {e}")
        return f"Error loading test dashboard: {e}", 500

@app.route('/api/test-results')
def get_test_results():
    """Get test results for the test dashboard."""
    try:
        # Get test results from various sources
        test_results = {
            'unit_tests': get_unit_test_results(),
            'integration_tests': get_integration_test_results(),
            'e2e_tests': get_e2e_test_results(),
            'coverage': get_test_coverage(),
            'last_run': get_last_test_run()
        }
        return jsonify(test_results)
    except Exception as e:
        logger.log_error(f"Error getting test results: {e}")
        return jsonify({'error': str(e)}), 500

def get_unit_test_results():
    """Get unit test results."""
    try:
        # Check if test results exist
        test_results_file = os.path.join(os.path.dirname(__file__), 'test-results', 'unit-test-results.json')
        if os.path.exists(test_results_file):
            with open(test_results_file, 'r') as f:
                return json.load(f)
        return {'status': 'not_run', 'tests': 0, 'passed': 0, 'failed': 0}
    except Exception as e:
        logger.log_error(f"Error reading unit test results: {e}")
        return {'status': 'error', 'error': str(e)}

def get_integration_test_results():
    """Get integration test results."""
    try:
        test_results_file = os.path.join(os.path.dirname(__file__), 'test-results', 'integration-test-results.json')
        if os.path.exists(test_results_file):
            with open(test_results_file, 'r') as f:
                return json.load(f)
        return {'status': 'not_run', 'tests': 0, 'passed': 0, 'failed': 0}
    except Exception as e:
        logger.log_error(f"Error reading integration test results: {e}")
        return {'status': 'error', 'error': str(e)}

def get_e2e_test_results():
    """Get E2E test results."""
    try:
        test_results_file = os.path.join(os.path.dirname(__file__), 'test-results', 'e2e-test-results.json')
        if os.path.exists(test_results_file):
            with open(test_results_file, 'r') as f:
                return json.load(f)
        return {'status': 'not_run', 'tests': 0, 'passed': 0, 'failed': 0}
    except Exception as e:
        logger.log_error(f"Error reading E2E test results: {e}")
        return {'status': 'error', 'error': str(e)}

def get_test_coverage():
    """Get test coverage data."""
    try:
        coverage_file = os.path.join(os.path.dirname(__file__), 'coverage', 'coverage-final.json')
        if os.path.exists(coverage_file):
            with open(coverage_file, 'r') as f:
                coverage_data = json.load(f)
            # Calculate coverage percentage
            total_lines = 0
            covered_lines = 0
            for file_data in coverage_data.values():
                for line_num, hits in file_data.get('s', {}).items():
                    total_lines += 1
                    if hits > 0:
                        covered_lines += 1
            coverage_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            return {
                'percentage': round(coverage_percentage, 2),
                'covered_lines': covered_lines,
                'total_lines': total_lines
            }
        return {'percentage': 0, 'covered_lines': 0, 'total_lines': 0}
    except Exception as e:
        logger.log_error(f"Error reading coverage data: {e}")
        return {'percentage': 0, 'error': str(e)}

def get_last_test_run():
    """Get last test run information."""
    try:
        # Check for test report files
        test_report_dir = os.path.join(os.path.dirname(__file__), 'test-reports')
        if os.path.exists(test_report_dir):
            files = [f for f in os.listdir(test_report_dir) if f.endswith('.json')]
            if files:
                latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(test_report_dir, x)))
                with open(os.path.join(test_report_dir, latest_file), 'r') as f:
                    return json.load(f)
        return {'timestamp': None, 'duration': 0}
    except Exception as e:
        logger.log_error(f"Error reading last test run: {e}")
        return {'timestamp': None, 'error': str(e)}

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

# Status routes moved to routes/status.py

# Generation status route and progress function moved to routes/generation.py

# Configuration routes moved to routes/config.py

# Generation routes moved to routes/generation.py

# Batch generation route moved to routes/generation.py

# Batch preview route moved to routes/generation.py

# Queue routes moved to routes/queue.py

# Output routes moved to routes/output.py

# Logging Endpoints
# Logging routes moved to routes/logging.py

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
    handle_connect(socketio)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.log_app_event("websocket_disconnected", {"client_id": request.sid})
    handle_disconnect(socketio)

@socketio.on('request_status')
def handle_status_request():
    """Handle status request."""
    handle_status_request(socketio, status_service)

def start_background_processor():
    """Start the background job processor."""
    status_service.start_background_processor()

# API Connection routes moved to routes/api_connection.py

# Generation Control
# Stop generation route moved to routes/generation.py

# Output directory routes moved to routes/output.py

# Image Analysis routes moved to routes/image_analysis.py

# Config settings routes moved to routes/config.py

# Config create-from-image route moved to routes/config.py

# API Metadata routes moved to routes/api_metadata.py

# Config thumbnail routes moved to routes/config.py

# ============================================================================
# SETTINGS API ENDPOINTS
# ============================================================================

# Settings routes moved to routes/settings.py

# Logging and cache routes moved to routes/logging.py

# JavaScript Error Logging
@app.route('/api/log-js-error', methods=['POST'])
def log_js_error():
    """Log JavaScript errors from the frontend."""
    try:
        data = request.get_json()
        if data:
            logger.log_error(f"JavaScript Error: {data.get('type', 'Unknown')} - {data.get('message', 'No message')}", {
                'source': data.get('source', 'Unknown'),
                'line': data.get('lineno', 'Unknown'),
                'column': data.get('colno', 'Unknown'),
                'stack': data.get('stack', 'No stack trace'),
                'url': data.get('url', 'Unknown'),
                'user_agent': data.get('userAgent', 'Unknown'),
                'timestamp': data.get('timestamp', 'Unknown')
            })
        return jsonify({'success': True})
    except Exception as e:
        logger.log_error(f"Failed to log JavaScript error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

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