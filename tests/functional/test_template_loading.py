#!/usr/bin/env python3
"""
Simple test script to verify template loading
"""

import os
import sys
import json

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_template_loading():
    """Test loading templates directly"""
    print("Testing template loading...")
    
    # Test 1: Check config directory
    config_dir = os.path.join(project_root, "configs")
    print(f"Config directory: {config_dir}")
    print(f"Config directory exists: {os.path.exists(config_dir)}")
    
    if not os.path.exists(config_dir):
        print("ERROR: Config directory does not exist!")
        return False
    
    # Test 2: List JSON files
    json_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    print(f"JSON files found: {json_files}")
    
    if not json_files:
        print("ERROR: No JSON files found in config directory!")
        return False
    
    # Test 3: Test loading each file
    successful_loads = 0
    for json_file in json_files:
        config_name = json_file[:-5]  # Remove .json extension
        config_path = os.path.join(config_dir, json_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required fields
            has_name = 'name' in config
            has_model_type = 'model_type' in config
            has_model_settings = 'model_settings' in config
            has_checkpoint = has_model_settings and 'checkpoint' in config['model_settings']
            
            print(f"  {config_name}:")
            print(f"    ✓ Valid JSON")
            print(f"    {'✓' if has_name else '✗'} Has name: {config.get('name', 'MISSING')}")
            print(f"    {'✓' if has_model_type else '✗'} Has model_type: {config.get('model_type', 'MISSING')}")
            print(f"    {'✓' if has_checkpoint else '✗'} Has checkpoint: {config.get('model_settings', {}).get('checkpoint', 'MISSING')}")
            print(f"    Description: {config.get('description', 'No description')}")
            
            if has_name and has_model_type and has_checkpoint:
                successful_loads += 1
            else:
                print(f"    ⚠️  Missing required fields")
                
        except Exception as e:
            print(f"  {config_name}: ✗ Error loading: {e}")
    
    print(f"\nSummary: {successful_loads}/{len(json_files)} templates loaded successfully")
    return successful_loads == len(json_files)

def test_config_handler():
    """Test the config handler"""
    print("\nTesting config handler...")
    
    try:
        from core.config_handler import config_handler
        print("✓ Config handler imported successfully")
        
        # Test get_all_configs
        configs = config_handler.get_all_configs()
        print(f"✓ Loaded {len(configs)} configurations")
        
        for config_name, config in configs.items():
            print(f"  {config_name}: {config.get('name', 'N/A')} ({config.get('model_type', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"✗ Config handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("FORGE API TOOL - TEMPLATE LOADING TEST")
    print("=" * 50)
    
    # Test 1: Direct file loading
    file_test = test_template_loading()
    
    # Test 2: Config handler
    handler_test = test_config_handler()
    
    print("\n" + "=" * 50)
    if file_test and handler_test:
        print("✓ ALL TESTS PASSED - Templates should load correctly")
    else:
        print("✗ SOME TESTS FAILED - Check the issues above")
    
    return file_test and handler_test

if __name__ == "__main__":
    main() 