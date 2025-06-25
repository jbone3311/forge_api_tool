#!/usr/bin/env python3
"""
Test script for image generation with wildcard processing
"""

import requests
import json
import time

def test_image_generation():
    """Test image generation with wildcard processing."""
    
    # Test data - using Quick Start template with wildcards
    test_data = {
        "config_name": "Quick Start",
        "prompt": "",  # Empty prompt to test wildcard substitution
        "seed": 42
    }
    
    print("Testing image generation with wildcard processing...")
    print(f"Config: {test_data['config_name']}")
    print(f"User prompt: '{test_data['prompt']}' (will use template with wildcards)")
    print(f"Seed: {test_data['seed']}")
    print("-" * 50)
    
    try:
        # Send request to Flask app
        response = requests.post(
            "http://127.0.0.1:5000/api/generate",
            json=test_data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Image generation successful!")
                print(f"Prompt used: {result.get('prompt_used', 'N/A')}")
                print(f"Output path: {result.get('output_path', 'N/A')}")
                print(f"Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
            else:
                print("❌ Image generation failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The generation might be taking too long.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_batch_preview():
    """Test batch preview with wildcard processing."""
    
    test_data = {
        "config_name": "Quick Start",
        "prompt": "",  # Empty prompt to test wildcard substitution
        "batch_size": 3,
        "num_batches": 2
    }
    
    print("\nTesting batch preview with wildcard processing...")
    print(f"Config: {test_data['config_name']}")
    print(f"Batch size: {test_data['batch_size']}")
    print(f"Num batches: {test_data['num_batches']}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/batch/preview",
            json=test_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Batch preview successful!")
                prompts = result.get('prompts', [])
                print(f"Generated {len(prompts)} prompts:")
                for i, prompt in enumerate(prompts, 1):
                    print(f"  {i}. {prompt}")
            else:
                print("❌ Batch preview failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Forge API Tool - Image Generation Test")
    print("=" * 50)
    
    # Test single image generation
    test_image_generation()
    
    # Test batch preview
    test_batch_preview()
    
    print("\nTest completed!") 