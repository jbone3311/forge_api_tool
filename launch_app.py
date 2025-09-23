#!/usr/bin/env python3
"""
Forge API Tool Launcher - Automatically opens the web interface.
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

def launch_app():
    """Launch the Forge API Tool with automatic browser opening."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    web_dashboard_dir = project_root / "web_dashboard"
    clean_app_file = web_dashboard_dir / "clean_app.py"
    
    if not clean_app_file.exists():
        print("❌ Error: clean_app.py not found!")
        print(f"Expected location: {clean_app_file}")
        return
    
    print("🚀 Launching Forge API Tool...")
    print("📁 Project directory:", project_root)
    print("🌐 Web dashboard:", web_dashboard_dir)
    
    # Change to the web_dashboard directory
    os.chdir(web_dashboard_dir)
    
    # Start the application
    try:
        print("\n🎯 Starting server...")
        os.system(f"{sys.executable} clean_app.py")
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")

if __name__ == "__main__":
    launch_app()
