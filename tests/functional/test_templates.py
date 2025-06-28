#!/usr/bin/env python3
"""
Simple template loading test
"""

import os
import sys
import json

def test_templates():
    print("Testing template loading...")
    
    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(project_root, "configs")
    
    print(f"Project root: {project_root}")
    print(f"Config directory: {config_dir}")
    print(f"Config directory exists: {os.path.exists(config_dir)}")
    
    if not os.path.exists(config_dir):
        print("ERROR: Config directory does not exist!")
        return False
    
    # List JSON files
    files = os.listdir(config_dir)
    json_files = [f for f in files if f.endswith('.json')]
    print(f"JSON files: {json_files}")
    
    if not json_files:
        print("ERROR: No JSON files found!")
        return False
    
    # Test loading each file
    successful = 0
    for json_file in json_files:
        config_path = os.path.join(config_dir, json_file)
        config_name = json_file[:-5]
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required fields
            has_name = 'name' in config
            has_model_type = 'model_type' in config
            has_model_settings = 'model_settings' in config
            has_checkpoint = has_model_settings and 'checkpoint' in config['model_settings']
            
            print(f"\n{config_name}:")
            print(f"  Name: {config.get('name', 'MISSING')}")
            print(f"  Model: {config.get('model_type', 'MISSING')}")
            print(f"  Checkpoint: {config.get('model_settings', {}).get('checkpoint', 'MISSING')}")
            print(f"  Description: {config.get('description', 'No description')}")
            
            if has_name and has_model_type and has_checkpoint:
                successful += 1
                print(f"  ✓ Valid template")
            else:
                print(f"  ✗ Missing required fields")
                
        except Exception as e:
            print(f"\n{config_name}: ✗ Error: {e}")
    
    print(f"\nSummary: {successful}/{len(json_files)} templates are valid")
    return successful == len(json_files)

if __name__ == "__main__":
    test_templates() 