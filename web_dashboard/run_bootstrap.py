#!/usr/bin/env python3
"""
Startup script for Forge API Tool Bootstrap Dashboard
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Forge API Tool Bootstrap Dashboard...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app_bootstrap.py'):
        print("❌ Error: app_bootstrap.py not found!")
        print("Please run this script from the web_dashboard directory.")
        sys.exit(1)
    
    # Check if required dependencies are installed
    try:
        import flask
        import flask_socketio
        print("✅ Flask and Flask-SocketIO found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install flask flask-socketio")
        sys.exit(1)
    
    # Check if core modules are available
    core_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core")
    if not os.path.exists(core_path):
        print("❌ Error: Core modules not found!")
        print("Please ensure you're running from the correct directory structure.")
        sys.exit(1)
    
    print("✅ Core modules found")
    print("✅ Bootstrap dashboard ready to start")
    print("=" * 50)
    
    # Start the application
    try:
        from app_bootstrap import app, socketio
        
        print("🌐 Dashboard will be available at: http://localhost:5000")
        print("📱 Modern responsive interface with Bootstrap 5")
        print("⚡ Real-time updates with Socket.IO")
        print("🎨 Beautiful UI components and animations")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 