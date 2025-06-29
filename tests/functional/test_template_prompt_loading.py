#!/usr/bin/env python3
"""
Test script to verify template prompt loading functionality
"""

import os
import sys
import json
import pytest

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_template_prompt_loading():
    """Test that templates have base prompts and they can be loaded."""
    print("Testing template prompt loading functionality...")
    print("=" * 60)
    
    # Test 1: Check config directory
    config_dir = os.path.join(project_root, "..", "..", "configs")
    print(f"Config directory: {config_dir}")
    print(f"Config directory exists: {os.path.exists(config_dir)}")
    
    assert os.path.exists(config_dir), "Config directory does not exist!"
    
    # Test 2: List JSON files
    json_files = [f for f in os.listdir(config_dir) if f.endswith('.json')]
    print(f"JSON files found: {json_files}")
    
    assert len(json_files) > 0, "No JSON files found in config directory!"
    
    # Test 3: Test loading each file and check for base prompts
    successful_loads = 0
    templates_with_prompts = 0
    
    for json_file in json_files:
        config_name = json_file[:-5]  # Remove .json extension
        config_path = os.path.join(config_dir, json_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check required fields
            has_name = 'name' in config
            has_model_type = 'model_type' in config
            has_prompt_settings = 'prompt_settings' in config
            has_base_prompt = has_prompt_settings and 'base_prompt' in config['prompt_settings']
            
            print(f"\n  {config_name}:")
            print(f"    ✓ Valid JSON")
            print(f"    {'✓' if has_name else '✗'} Has name: {config.get('name', 'MISSING')}")
            print(f"    {'✓' if has_model_type else '✗'} Has model_type: {config.get('model_type', 'MISSING')}")
            print(f"    {'✓' if has_prompt_settings else '✗'} Has prompt_settings")
            
            if has_base_prompt:
                base_prompt = config['prompt_settings']['base_prompt']
                print(f"    ✓ Has base_prompt: {base_prompt[:50]}...")
                templates_with_prompts += 1
                
                # Check for wildcards
                wildcard_count = base_prompt.count('__')
                if wildcard_count > 0:
                    print(f"    ✓ Contains {wildcard_count//2} wildcards (__WILDCARD__ format)")
                else:
                    print(f"    ⚠️  No wildcards found in base prompt")
            else:
                print(f"    ✗ Missing base_prompt in prompt_settings")
            
            if has_name and has_model_type and has_base_prompt:
                successful_loads += 1
            else:
                print(f"    ⚠️  Missing required fields")
                
        except Exception as e:
            print(f"  {config_name}: ✗ Error loading: {e}")
            pytest.fail(f"Error loading {config_name}: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Templates loaded successfully: {successful_loads}/{len(json_files)}")
    print(f"  Templates with base prompts: {templates_with_prompts}/{len(json_files)}")
    
    assert templates_with_prompts > 0, "No templates have base prompts - prompt loading will not work"
    print(f"  ✓ Template prompt loading should work correctly")

def test_wildcard_files():
    """Test that wildcard files exist for the templates."""
    print("\nTesting wildcard file availability...")
    print("=" * 60)
    
    config_dir = os.path.join(project_root, "..", "..", "configs")
    wildcards_dir = os.path.join(project_root, "..", "..", "wildcards")
    
    print(f"Wildcards directory: {wildcards_dir}")
    print(f"Wildcards directory exists: {os.path.exists(wildcards_dir)}")
    
    assert os.path.exists(wildcards_dir), "Wildcards directory does not exist!"
    
    # Get all wildcard files
    wildcard_files = []
    for root, dirs, files in os.walk(wildcards_dir):
        for file in files:
            if file.endswith('.txt'):
                rel_path = os.path.relpath(os.path.join(root, file), wildcards_dir)
                wildcard_files.append(rel_path)
    
    print(f"Found {len(wildcard_files)} wildcard files")
    
    # Test a few templates for wildcard availability
    test_templates = ['SD_Default', 'SDXL_Default']
    
    for template_name in test_templates:
        config_path = os.path.join(config_dir, f"{template_name}.json")
        if not os.path.exists(config_path):
            continue
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'prompt_settings' in config and 'base_prompt' in config['prompt_settings']:
                base_prompt = config['prompt_settings']['base_prompt']
                
                # Extract wildcards
                import re
                wildcards = re.findall(r'__([A-Z_]+)__', base_prompt)
                
                print(f"\n  {template_name}:")
                print(f"    Base prompt: {base_prompt[:50]}...")
                print(f"    Wildcards found: {wildcards}")
                
                # Check if wildcard files exist
                missing_wildcards = []
                for wildcard in wildcards:
                    wildcard_file = f"{wildcard.lower()}.txt"
                    if wildcard_file not in wildcard_files:
                        missing_wildcards.append(wildcard)
                
                if missing_wildcards:
                    print(f"    ⚠️  Missing wildcard files: {missing_wildcards}")
                else:
                    print(f"    ✓ All wildcard files available")
                    
        except Exception as e:
            print(f"  {template_name}: ✗ Error: {e}")
            pytest.fail(f"Error testing {template_name}: {e}")

def main():
    """Run all tests"""
    print("FORGE API TOOL - TEMPLATE PROMPT LOADING TEST")
    print("=" * 60)
    
    # Test 1: Template loading
    template_test = test_template_prompt_loading()
    
    # Test 2: Wildcard files
    wildcard_test = test_wildcard_files()
    
    print("\n" + "=" * 60)
    if template_test and wildcard_test:
        print("✓ ALL TESTS PASSED - Template prompt loading should work correctly")
        print("\nThe web dashboard should now:")
        print("  1. Automatically load the first template's base prompt on page load")
        print("  2. Load a template's base prompt when clicking on template cards")
        print("  3. Load a template's base prompt when selecting from the dropdown")
        print("  4. Show helpful notifications when templates are loaded")
        print("  5. Display wildcards in the prompt field for user editing")
    else:
        print("✗ SOME TESTS FAILED - Check the issues above")
    
    return template_test and wildcard_test

if __name__ == "__main__":
    main() 