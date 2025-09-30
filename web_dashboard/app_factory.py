#!/usr/bin/env python3
"""
Application Factory

Creates and configures the Flask application with proper dependency injection.
"""

import os
import sys
from flask import Flask, g
from flask_socketio import SocketIO

# Add the parent directory to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.app_context import AppContext
from services.generation_service import GenerationService
from services.config_service import ConfigService
from services.wildcard_service import WildcardService
from routes.main_routes import main_bp
from routes.generation_routes import generation_bp, register_socketio_events
from routes.config_routes import config_bp
from routes.batch_routes import batch_bp
from routes.clip_routes import clip_bp
from core.centralized_logger import logger


def create_app(project_root: str = None) -> tuple[Flask, SocketIO]:
    """
    Create and configure the Flask application.
    
    Args:
        project_root: Root directory of the project (auto-detected if None)
        
    Returns:
        Tuple of (Flask app, SocketIO instance)
    """
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'forge-api-tool-clean-app-secret'
    
    # Create SocketIO instance
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize application context
    app_context = AppContext(project_root)
    
    # Initialize services
    generation_service = GenerationService(app_context)
    config_service = ConfigService(app_context)
    wildcard_service = WildcardService(app_context)
    
    # Add services to app context
    app_context._components['generation_service'] = generation_service
    app_context._components['config_service'] = config_service
    app_context._components['wildcard_service'] = wildcard_service
    
    # Make app context available to all routes
    @app.before_request
    def before_request():
        g.app_context = app_context
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(generation_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(clip_bp)
    
    # Register Socket.IO events
    register_socketio_events(socketio, app_context)
    
    # Add error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    logger.log_app_event("app_factory_created", {
        "project_root": app_context.project_root,
        "services": list(app_context._components.keys()),
        "blueprints": [bp.name for bp in app.blueprints.values()]
    })
    
    return app, socketio


def create_development_app() -> tuple[Flask, SocketIO]:
    """Create application for development."""
    return create_app()


if __name__ == '__main__':
    # Create application
    app, socketio = create_development_app()
    
    # Run application
    logger.info("🎯 Starting Forge API Tool - Clean App")
    logger.info("📱 Dashboard will be available at: http://localhost:8081")
    
    # Get app info
    with app.app_context():
        from flask import g
        app_info = g.app_context.get_app_info()
        logger.info(f"📡 Current API Provider: {app_info['current_api_type']}")
        
        # Get configuration handler for wildcard info
        config_handler = g.app_context.get_config_handler()
        prompt_builder = g.app_context.get_prompt_builder()
        
        logger.info("✅ Features:")
        logger.info("   • Organized wildcard file management")
        logger.info("   • Multiple API provider support")
        logger.info("   • Real-time generation progress")
        logger.info("   • Configuration management")
        logger.info("   • Advanced wildcard processing")
        logger.info("   • Output management")
        logger.info("   • Clean, organized interface")
        logger.info("⚠️  Note: All images are mock generated - no real API calls")
        
        # Get wildcard info
        wildcard_names = prompt_builder.get_available_wildcards()
        logger.info(f"🎲 Discovered {len(wildcard_names)} wildcard files:")
        for i, name in enumerate(wildcard_names[:10]):
            logger.info(f"   • {name}")
        if len(wildcard_names) > 10:
            logger.info(f"   • ... and {len(wildcard_names) - 10} more")
        
        logger.info("🌐 Opening browser automatically...")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=8081, debug=True, allow_unsafe_werkzeug=True)


