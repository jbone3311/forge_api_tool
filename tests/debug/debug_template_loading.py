#!/usr/bin/env python3
"""
Debug script to test template loading and identify issues
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_paths():
    """Test all relevant paths"""
    print("=== PATH TESTING ===")
    
    # Current working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    print(f"Project root: {project_root}")
    
    # Config directory paths
    config_dir_relative = "configs"
    config_dir_absolute = os.path.join(project_root, config_dir_relative)
    
    print(f"Config dir (relative): {config_dir_relative}")
    print(f"Config dir (absolute): {config_dir_absolute}")
    print(f"Config dir exists: {os.path.exists(config_dir_absolute)}")
    
    if os.path.exists(config_dir_absolute):
        files = os.listdir(config_dir_absolute)
        print(f"Files in config dir: {files}")
        
        # Check each JSON file
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(config_dir_absolute, file)
                print(f"  {file}: {os.path.exists(file_path)}")
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                        print(f"    Valid JSON: ✓")
                        print(f"    Has 'name': {'name' in content}")
                        print(f"    Has 'model_type': {'model_type' in content}")
                    except Exception as e:
                        print(f"    JSON Error: {e}")
    
    # Wildcards directory
    wildcards_dir = os.path.join(project_root, "wildcards")
    print(f"Wildcards dir: {wildcards_dir}")
    print(f"Wildcards dir exists: {os.path.exists(wildcards_dir)}")
    
    if os.path.exists(wildcards_dir):
        wildcard_files = [f for f in os.listdir(wildcards_dir) if f.endswith('.txt')]
        print(f"Wildcard files: {wildcard_files[:10]}...")  # Show first 10

def test_config_handler_import():
    """Test importing the config handler"""
    print("\n=== CONFIG HANDLER IMPORT TEST ===")
    
    try:
        from core.config_handler import config_handler
        print("✓ Config handler imported successfully")
        print(f"Config handler config_dir: {config_handler.config_dir}")
        print(f"Config handler config_dir exists: {os.path.exists(config_handler.config_dir)}")
        return config_handler
    except Exception as e:
        print(f"✗ Config handler import failed: {e}")
        return None

def test_config_loading(config_handler):
    """Test loading configurations"""
    print("\n=== CONFIG LOADING TEST ===")
    
    if not config_handler:
        print("✗ No config handler available")
        return
    
    try:
        # Test list_configs
        config_list = config_handler.list_configs()
        print(f"Available configs: {config_list}")
        
        # Test get_all_configs
        all_configs = config_handler.get_all_configs()
        print(f"All configs loaded: {len(all_configs)}")
        
        for config_name, config in all_configs.items():
            print(f"\nConfig: {config_name}")
            print(f"  Name: {config.get('name', 'N/A')}")
            print(f"  Model Type: {config.get('model_type', 'N/A')}")
            print(f"  Description: {config.get('description', 'N/A')}")
            
            # Check model settings
            model_settings = config.get('model_settings', {})
            checkpoint = model_settings.get('checkpoint', 'N/A')
            print(f"  Checkpoint: {checkpoint}")
            
            # Check generation settings
            gen_settings = config.get('generation_settings', {})
            print(f"  Steps: {gen_settings.get('steps', 'N/A')}")
            print(f"  Width: {gen_settings.get('width', 'N/A')}")
            print(f"  Height: {gen_settings.get('height', 'N/A')}")
            
            # Check wildcards
            missing_wildcards = config.get('missing_wildcards', [])
            if missing_wildcards:
                print(f"  Missing wildcards: {missing_wildcards}")
            else:
                print(f"  Wildcards: ✓ All available")
                
    except Exception as e:
        print(f"✗ Config loading failed: {e}")
        import traceback
        traceback.print_exc()

def test_web_dashboard_import():
    """Test web dashboard imports"""
    print("\n=== WEB DASHBOARD IMPORT TEST ===")
    
    try:
        # Test importing the app
        sys.path.append(os.path.join(project_root, 'web_dashboard'))
        from web_dashboard.app import app, config_handler as dashboard_config_handler
        print("✓ Web dashboard app imported successfully")
        
        # Test config handler in dashboard context
        configs = dashboard_config_handler.get_all_configs()
        print(f"Dashboard configs: {len(configs)}")
        
        return True
    except Exception as e:
        print(f"✗ Web dashboard import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_structure():
    """Test the structure of template files"""
    print("\n=== TEMPLATE STRUCTURE TEST ===")
    
    config_dir = os.path.join(project_root, "configs")
    if not os.path.exists(config_dir):
        print("✗ Config directory does not exist")
        return
    
    for file in os.listdir(config_dir):
        if file.endswith('.json'):
            file_path = os.path.join(config_dir, file)
            print(f"\nTesting: {file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                # Check required fields
                required_fields = ['name', 'model_type']
                for field in required_fields:
                    if field in content:
                        print(f"  ✓ {field}: {content[field]}")
                    else:
                        print(f"  ✗ Missing {field}")
                
                # Check model settings
                model_settings = content.get('model_settings', {})
                if model_settings:
                    checkpoint = model_settings.get('checkpoint', 'N/A')
                    print(f"  ✓ Checkpoint: {checkpoint}")
                else:
                    print(f"  ✗ Missing model_settings")
                
                # Check generation settings
                gen_settings = content.get('generation_settings', {})
                if gen_settings:
                    print(f"  ✓ Generation settings present")
                else:
                    print(f"  ✗ Missing generation_settings")
                
                # Check prompt settings
                prompt_settings = content.get('prompt_settings', {})
                if prompt_settings:
                    base_prompt = prompt_settings.get('base_prompt', 'N/A')
                    print(f"  ✓ Base prompt: {base_prompt[:50]}...")
                else:
                    print(f"  ✗ Missing prompt_settings")
                    
            except Exception as e:
                print(f"  ✗ Error reading {file}: {e}")

def main():
    """Run all tests"""
    print("FORGE API TOOL - TEMPLATE LOADING DEBUG")
    print("=" * 50)
    
    # Test 1: Paths
    test_paths()
    
    # Test 2: Config handler import
    config_handler = test_config_handler_import()
    
    # Test 3: Config loading
    test_config_loading(config_handler)
    
    # Test 4: Web dashboard import
    test_web_dashboard_import()
    
    # Test 5: Template structure
    test_template_structure()
    
    print("\n" + "=" * 50)
    print("DEBUG COMPLETE")

if __name__ == "__main__":
    main() 