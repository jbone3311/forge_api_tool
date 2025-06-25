#!/usr/bin/env python3
"""
Simple import test script to verify all core modules can be imported.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test importing all core modules."""
    print("Testing imports...")
    
    try:
        print("1. Testing config_handler...")
        from core.config_handler import config_handler
        print("   ✓ config_handler imported successfully")
        
        print("2. Testing forge_api...")
        from core.forge_api import forge_api_client
        print("   ✓ forge_api_client imported successfully")
        
        print("3. Testing centralized_logger...")
        from core.centralized_logger import centralized_logger
        print("   ✓ centralized_logger imported successfully")
        
        print("4. Testing output_manager...")
        from core.output_manager import output_manager
        print("   ✓ output_manager imported successfully")
        
        print("5. Testing job_queue...")
        from core.job_queue import job_queue
        print("   ✓ job_queue imported successfully")
        
        print("6. Testing batch_runner...")
        from core.batch_runner import batch_runner
        print("   ✓ batch_runner imported successfully")
        
        print("7. Testing wildcard_manager...")
        from core.wildcard_manager import WildcardManagerFactory
        print("   ✓ WildcardManagerFactory imported successfully")
        
        print("8. Testing prompt_builder...")
        from core.prompt_builder import PromptBuilder
        print("   ✓ PromptBuilder imported successfully")
        
        print("9. Testing image_analyzer...")
        from core.image_analyzer import ImageAnalyzer
        print("   ✓ ImageAnalyzer imported successfully")
        
        print("\nAll imports successful! ✓")
        return True
        
    except Exception as e:
        print(f"\nImport failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 