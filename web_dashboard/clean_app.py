#!/usr/bin/env python3
"""
Clean Forge API Tool - Organized interface with wildcard file management.

This is now a simple wrapper that uses the new modular architecture.
"""

from app_factory import create_development_app

# Create the application using the new modular factory
app, socketio = create_development_app()

if __name__ == '__main__':
    # Run the application
    from core.centralized_logger import logger
    
    logger.info("🎯 Starting Forge API Tool - Clean App")
    logger.info("📱 Dashboard will be available at: http://localhost:8081")
    logger.info("✅ Features:")
    logger.info("   • Organized wildcard file management")
    logger.info("   • Multiple API provider support")
    logger.info("   • Real-time generation progress")
    logger.info("   • Configuration management")
    logger.info("   • Advanced wildcard processing")
    logger.info("   • Output management")
    logger.info("   • Clean, organized interface")
    logger.info("⚠️  Note: All images are mock generated - no real API calls")
    logger.info("🌐 Opening browser automatically...")
    
    # Run the application
    socketio.run(app, host='0.0.0.0', port=8081, debug=True, allow_unsafe_werkzeug=True)


