#!/usr/bin/env python3
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_paths():
    print("=== PATH TEST ===")
    print(f"Project root: {project_root}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test config directory
    config_dir = os.path.join(project_root, "configs")
    print(f"Config directory: {config_dir}")
    print(f"Config directory exists: {os.path.exists(config_dir)}")
    
    if os.path.exists(config_dir):
        files = os.listdir(config_dir)
        json_files = [f for f in files if f.endswith('.json')]
        print(f"JSON files: {json_files}")
        
        # Test loading one file
        if json_files:
            test_file = json_files[0]
            test_path = os.path.join(config_dir, test_file)
            print(f"Testing file: {test_path}")
            
            try:
                import json
                with open(test_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✓ Successfully loaded {test_file}")
                print(f"  Name: {data.get('name', 'N/A')}")
                print(f"  Model: {data.get('model_type', 'N/A')}")
                print(f"  Checkpoint: {data.get('model_settings', {}).get('checkpoint', 'N/A')}")
            except Exception as e:
                print(f"✗ Failed to load {test_file}: {e}")

def test_config_handler():
    print("\n=== CONFIG HANDLER TEST ===")
    try:
        from core.config_handler import config_handler
        print("✓ Config handler imported")
        print(f"Config handler config_dir: {config_handler.config_dir}")
        
        configs = config_handler.get_all_configs()
        print(f"✓ Loaded {len(configs)} configs")
        
        for name, config in configs.items():
            print(f"  {name}: {config.get('name', 'N/A')} ({config.get('model_type', 'N/A')})")
            
    except Exception as e:
        print(f"✗ Config handler test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paths()
    test_config_handler() 