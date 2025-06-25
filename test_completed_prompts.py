#!/usr/bin/env python3
"""
Test script for completed prompt generation with new output structure
"""

import requests
import json
import time

def test_completed_prompt_generation():
    """Test image generation with completed prompts."""
    
    # Test data - using Quick Start template with a completed prompt
    test_data = {
        "config_name": "Quick Start",
        "prompt": "a magnificent warrior in digital art, natural sunlight, close-up shot, oil painting, happy mood, sunny weather, forest setting, standing pose, smiling expression, high quality, detailed, masterpiece, professional, award winning, trending on artstation",
        "seed": 42
    }
    
    print("Testing image generation with completed prompt...")
    print(f"Config: {test_data['config_name']}")
    print(f"Prompt: {test_data['prompt'][:100]}...")
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

def test_empty_prompt_rejection():
    """Test that empty prompts are rejected."""
    
    test_data = {
        "config_name": "Quick Start",
        "prompt": "",  # Empty prompt should be rejected
        "seed": 42
    }
    
    print("\nTesting empty prompt rejection...")
    print(f"Config: {test_data['config_name']}")
    print(f"Prompt: '{test_data['prompt']}' (should be rejected)")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/generate",
            json=test_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print("✅ Empty prompt correctly rejected!")
            print(f"Error message: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_batch_preview_with_completed_prompt():
    """Test batch preview with completed prompt."""
    
    test_data = {
        "config_name": "Quick Start",
        "prompt": "a beautiful landscape in watercolor, golden hour, wide shot, acrylic painting, peaceful mood, cloudy weather, mountain setting, high quality, detailed",
        "batch_size": 3,
        "num_batches": 2
    }
    
    print("\nTesting batch preview with completed prompt...")
    print(f"Config: {test_data['config_name']}")
    print(f"Prompt: {test_data['prompt'][:80]}...")
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
                    print(f"  {i}. {prompt[:60]}...")
            else:
                print("❌ Batch preview failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Forge API Tool - Completed Prompt Test")
    print("=" * 50)
    
    # Test successful generation with completed prompt
    test_completed_prompt_generation()
    
    # Test empty prompt rejection
    test_empty_prompt_rejection()
    
    # Test batch preview with completed prompt
    test_batch_preview_with_completed_prompt()
    
    print("\nTest completed!") 