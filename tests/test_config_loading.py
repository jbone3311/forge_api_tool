#!/usr/bin/env python3
"""
Comprehensive test script for config loading and validation.
Tests encoding, JSON parsing, structure validation, and wildcard checking.
"""

import json
import os
import sys
import chardet
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_encoding(file_path):
    """Test file encoding and detect issues."""
    print(f"\n🔍 Testing file encoding: {file_path}")
    print("=" * 60)
    
    try:
        # Read raw bytes to detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        # Detect encoding
        detected = chardet.detect(raw_data)
        print(f"Detected encoding: {detected}")
        
        # Try different encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']
        
        for encoding in encodings_to_try:
            try:
                content = raw_data.decode(encoding)
                print(f"✅ Successfully decoded with {encoding}")
                return content, encoding
            except UnicodeDecodeError as e:
                print(f"❌ Failed to decode with {encoding}: {e}")
        
        print("❌ Could not decode with any encoding!")
        return None, None
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None, None

def test_json_parsing(content, file_path):
    """Test JSON parsing."""
    print(f"\n📄 Testing JSON parsing: {file_path}")
    print("=" * 60)
    
    try:
        # Try to parse JSON
        data = json.loads(content)
        print("✅ JSON parsing successful")
        return data
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Error at line {e.lineno}, column {e.colno}")
        
        # Show the problematic line
        lines = content.split('\n')
        if e.lineno <= len(lines):
            print(f"Problematic line {e.lineno}: {lines[e.lineno-1]}")
        
        return None
    except Exception as e:
        print(f"❌ Unexpected error parsing JSON: {e}")
        return None

def test_config_structure(config_data, file_path):
    """Test config structure and required fields."""
    print(f"\n🏗️ Testing config structure: {file_path}")
    print("=" * 60)
    
    required_fields = ['name', 'model_type', 'model_settings', 'generation_settings', 
                      'prompt_settings', 'output_settings']
    
    missing_fields = []
    for field in required_fields:
        if field not in config_data:
            missing_fields.append(field)
            print(f"❌ Missing required field: {field}")
        else:
            print(f"✅ Found field: {field}")
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    # Test specific field types
    try:
        if not isinstance(config_data['name'], str):
            print("❌ 'name' must be a string")
            return False
        
        if config_data['model_type'] not in ['sd', 'xl', 'flux']:
            print(f"❌ Invalid model_type: {config_data['model_type']}")
            return False
        
        if not isinstance(config_data['prompt_settings'], dict):
            print("❌ 'prompt_settings' must be a dictionary")
            return False
        
        if 'base_prompt' not in config_data['prompt_settings']:
            print("❌ Missing 'base_prompt' in prompt_settings")
            return False
        
        print("✅ Config structure validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Error validating structure: {e}")
        return False

def test_wildcard_extraction(config_data, file_path):
    """Test wildcard extraction from prompt template."""
    print(f"\n🎯 Testing wildcard extraction: {file_path}")
    print("=" * 60)
    
    try:
        import re
        template = config_data['prompt_settings']['base_prompt']
        print(f"Prompt template: {template}")
        
        # Extract wildcards using Automatic1111 format
        pattern = r'__([A-Z_]+)__'
        wildcards = re.findall(pattern, template)
        
        print(f"Found wildcards: {wildcards}")
        
        # Check if wildcard files exist
        missing_wildcards = []
        available_wildcards = []
        
        for wildcard in wildcards:
            wildcard_file = f"wildcards/{wildcard.lower()}.txt"
            if os.path.exists(wildcard_file):
                available_wildcards.append(wildcard)
                print(f"✅ Wildcard file exists: {wildcard_file}")
            else:
                missing_wildcards.append(wildcard)
                print(f"❌ Missing wildcard file: {wildcard_file}")
        
        print(f"\nSummary:")
        print(f"Available wildcards: {available_wildcards}")
        print(f"Missing wildcards: {missing_wildcards}")
        
        return wildcards, available_wildcards, missing_wildcards
        
    except Exception as e:
        print(f"❌ Error extracting wildcards: {e}")
        return [], [], []

def test_config_handler_loading(config_name):
    """Test loading config using ConfigHandler."""
    print(f"\n🔧 Testing ConfigHandler loading: {config_name}")
    print("=" * 60)
    
    try:
        from core.config_handler import ConfigHandler
        handler = ConfigHandler()
        
        # Test loading
        config = handler.load_config(config_name)
        print("✅ ConfigHandler.load_config() successful")
        
        # Test summary
        summary = handler.get_config_summary(config)
        print("✅ ConfigHandler.get_config_summary() successful")
        print(f"Summary: {summary}")
        
        return True, config, summary
        
    except Exception as e:
        print(f"❌ ConfigHandler error: {e}")
        return False, None, None

def fix_config_file(file_path):
    """Fix a config file by re-saving it properly."""
    print(f"\n🔧 Fixing config file: {file_path}")
    print("=" * 60)
    
    try:
        # Read and parse the content
        content, encoding = test_file_encoding(file_path)
        if not content:
            print("❌ Cannot read file content")
            return False
        
        config_data = test_json_parsing(content, file_path)
        if not config_data:
            print("❌ Cannot parse JSON")
            return False
        
        # Ensure proper structure
        if not test_config_structure(config_data, file_path):
            print("❌ Config structure is invalid")
            return False
        
        # Re-save with proper UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Config file fixed and re-saved")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing config file: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting comprehensive config loading test")
    print("=" * 80)
    
    # Test all config files
    config_dir = "configs"
    config_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    
    print(f"Found {len(config_files)} config files:")
    for f in config_files:
        print(f"  - {f}")
    
    results = {}
    
    for config_file in config_files:
        config_path = os.path.join(config_dir, config_file)
        config_name = config_file.replace('.json', '')
        
        print(f"\n{'='*80}")
        print(f"Testing: {config_file}")
        print(f"{'='*80}")
        
        # Test 1: File encoding
        content, encoding = test_file_encoding(config_path)
        if not content:
            print(f"❌ Skipping {config_file} due to encoding issues")
            results[config_name] = {'status': 'failed', 'error': 'encoding'}
            continue
        
        # Test 2: JSON parsing
        config_data = test_json_parsing(content, config_path)
        if not config_data:
            print(f"❌ Skipping {config_file} due to JSON parsing issues")
            results[config_name] = {'status': 'failed', 'error': 'json'}
            continue
        
        # Test 3: Config structure
        if not test_config_structure(config_data, config_path):
            print(f"❌ Skipping {config_file} due to structure issues")
            results[config_name] = {'status': 'failed', 'error': 'structure'}
            continue
        
        # Test 4: Wildcard extraction
        wildcards, available, missing = test_wildcard_extraction(config_data, config_path)
        
        # Test 5: ConfigHandler loading
        success, loaded_config, summary = test_config_handler_loading(config_name)
        
        if success:
            results[config_name] = {
                'status': 'success',
                'wildcards': wildcards,
                'available': available,
                'missing': missing,
                'summary': summary
            }
            print(f"✅ {config_name}: All tests passed")
        else:
            results[config_name] = {'status': 'failed', 'error': 'handler'}
            print(f"❌ {config_name}: ConfigHandler test failed")
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    successful = 0
    failed = 0
    
    for config_name, result in results.items():
        if result['status'] == 'success':
            successful += 1
            print(f"✅ {config_name}: SUCCESS")
            if result['missing']:
                print(f"   ⚠️  Missing wildcards: {result['missing']}")
        else:
            failed += 1
            print(f"❌ {config_name}: FAILED ({result.get('error', 'unknown')})")
    
    print(f"\nTotal: {successful} successful, {failed} failed")
    
    if failed > 0:
        print(f"\n🔧 Attempting to fix failed configs...")
        for config_name, result in results.items():
            if result['status'] == 'failed':
                config_path = os.path.join(config_dir, f"{config_name}.json")
                if fix_config_file(config_path):
                    print(f"✅ Fixed {config_name}")
                else:
                    print(f"❌ Could not fix {config_name}")

if __name__ == "__main__":
    main() 