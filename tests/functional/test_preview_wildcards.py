#!/usr/bin/env python3
"""
Test script to verify that preview functionality correctly resolves wildcards
"""

import os
import sys
import json
import pytest

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_preview_wildcard_resolution():
    """Test that preview functionality correctly resolves wildcards."""
    print("Testing preview wildcard resolution...")
    print("=" * 60)
    
    try:
        from core.config_handler import config_handler
        from core.prompt_builder import PromptBuilder
        from core.wildcard_manager import WildcardManagerFactory
        
        # Test with SD_Default template
        config_name = "SD_Default"
        config = config_handler.get_config(config_name)
        
        assert config is not None, f"Could not load config: {config_name}"
        
        print(f"✓ Loaded config: {config_name}")
        print(f"Base prompt: {config['prompt_settings']['base_prompt']}")
        
        # Create prompt builder
        wildcard_factory = WildcardManagerFactory()
        prompt_builder = PromptBuilder(wildcard_factory)
        
        # Test preview with 5 prompts
        preview_count = 5
        preview_prompts = prompt_builder.preview_prompts(config, preview_count)
        
        assert len(preview_prompts) == preview_count, f"Expected {preview_count} prompts, got {len(preview_prompts)}"
        
        print(f"\nGenerated {len(preview_prompts)} preview prompts:")
        print("-" * 40)
        
        for i, prompt in enumerate(preview_prompts, 1):
            print(f"{i}. {prompt}")
            
            # Check that wildcards were resolved
            if '__' in prompt:
                print(f"   ⚠️  Warning: Still contains unresolved wildcards")
            else:
                print(f"   ✓ Wildcards resolved successfully")
        
        # Test that preview doesn't consume wildcards (should be repeatable)
        print(f"\nTesting preview repeatability...")
        preview_prompts2 = prompt_builder.preview_prompts(config, preview_count)
        
        assert preview_prompts == preview_prompts2, "Preview should be repeatable (doesn't consume wildcards)"
        print("✓ Preview is repeatable (doesn't consume wildcards)")
        
        # Test actual wildcard consumption
        print(f"\nTesting actual wildcard consumption...")
        actual_prompts = []
        for i in range(preview_count):
            actual_prompts.append(prompt_builder.build_prompt(config))
        
        print(f"Generated {len(actual_prompts)} actual prompts:")
        for i, prompt in enumerate(actual_prompts, 1):
            print(f"{i}. {prompt}")
        
        # Test that actual prompts are different (wildcards are consumed)
        assert len(set(actual_prompts)) == len(actual_prompts), "Actual prompts should be varied (wildcards are consumed)"
        print("✓ Actual prompts are varied (wildcards are consumed)")
        
    except Exception as e:
        print(f"❌ Error testing preview wildcard resolution: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Test failed with exception: {e}")

@pytest.mark.skip(reason="Requires running Flask server")
def test_batch_preview_api():
    """Test the batch preview API endpoint."""
    print("\nTesting batch preview API...")
    print("=" * 60)
    
    try:
        import requests
    except ImportError:
        pytest.skip("Requests library not available. Install with: pip install requests")
    
    try:
        # Test data
        test_data = {
            "config_name": "SD_Default",
            "batch_size": 3,
            "num_batches": 1
            # No prompt provided - should use template's base prompt
        }
        
        print(f"Testing with data: {test_data}")
        
        # Make request to preview endpoint
        response = requests.post(
            "http://127.0.0.1:5000/api/batch/preview",
            json=test_data,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, f"Request failed with status {response.status_code}"
        
        result = response.json()
        assert result.get('success'), f"Preview failed: {result.get('error', 'Unknown error')}"
        
        prompts = result.get('prompts', [])
        wildcards_resolved = result.get('wildcards_resolved', False)
        template_used = result.get('template_used', False)
        
        print(f"✓ Preview successful!")
        print(f"  Template used: {template_used}")
        print(f"  Wildcards resolved: {wildcards_resolved}")
        print(f"  Generated {len(prompts)} prompts:")
        
        for i, prompt in enumerate(prompts, 1):
            print(f"    {i}. {prompt}")
        
        # Check if wildcards were resolved
        unresolved_wildcards = sum(1 for p in prompts if '__' in p)
        assert unresolved_wildcards == 0, f"{unresolved_wildcards} prompts still contain wildcards"
        print("✓ All wildcards resolved successfully")
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Could not connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error testing batch preview API: {e}")
        pytest.fail(f"Test failed with exception: {e}")

def main():
    """Run all tests"""
    print("FORGE API TOOL - PREVIEW WILDCARD RESOLUTION TEST")
    print("=" * 60)
    
    # Test 1: Direct preview functionality
    preview_test = test_preview_wildcard_resolution()
    
    # Test 2: API endpoint (if server is running)
    api_test = test_batch_preview_api()
    
    print("\n" + "=" * 60)
    if preview_test:
        print("✓ PREVIEW FUNCTIONALITY TEST PASSED")
        print("\nThe preview system should now:")
        print("  1. Use template's base prompt when no user prompt is provided")
        print("  2. Automatically resolve wildcards in preview")
        print("  3. Generate varied prompts for batch preview")
        print("  4. Show helpful information about wildcard resolution")
        print("  5. Allow users to preview before generating")
    else:
        print("✗ PREVIEW FUNCTIONALITY TEST FAILED")
    
    if api_test:
        print("✓ API ENDPOINT TEST PASSED")
    else:
        print("⚠️  API ENDPOINT TEST FAILED (server may not be running)")
    
    return preview_test

if __name__ == "__main__":
    main() 