#!/usr/bin/env python3
"""
Debug script to identify import issues.
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_import(module_name, import_name=None):
    """Debug a specific import."""
    print(f"\n=== Testing {module_name} ===")
    try:
        if import_name:
            exec(f"from {module_name} import {import_name}")
            print(f"✓ Successfully imported {import_name} from {module_name}")
        else:
            exec(f"import {module_name}")
            print(f"✓ Successfully imported {module_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to import {module_name}: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def main():
    print("Debugging Forge API Tool imports...")
    
    # Test basic imports first
    debug_import("core")
    debug_import("core.config_handler")
    debug_import("core.config_handler", "ConfigHandler")
    debug_import("core.config_handler", "config_handler")
    
    # Test other core modules
    debug_import("core.forge_api", "forge_api_client")
    debug_import("core.centralized_logger", "centralized_logger")
    debug_import("core.output_manager", "output_manager")
    debug_import("core.job_queue", "job_queue")
    debug_import("core.batch_runner", "batch_runner")

if __name__ == "__main__":
    main() 