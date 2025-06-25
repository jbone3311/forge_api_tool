#!/usr/bin/env python3
"""
Simple API test script that tests the core functionality directly
"""

import sys
import os

# Add the core directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(current_dir, 'core')
sys.path.insert(0, core_path)

from forge_api import ForgeAPIClient
import json

def test_forge_client():
    """Test the Forge API client directly."""
    print("🔧 Testing Forge API Client Directly")
    print("=" * 40)
    
    # Test client initialization
    print("\n1. Testing client initialization...")
    client = ForgeAPIClient("http://127.0.0.1:7860")
    print(f"   ✅ Client created with URL: {client.server_url}")
    
    # Test server_url property
    print("\n2. Testing server_url property...")
    print(f"   Current URL: {client.server_url}")
    client.server_url = "http://localhost:7860"
    print(f"   Updated URL: {client.server_url}")
    client.server_url = "http://127.0.0.1:7860"
    print(f"   Reset URL: {client.server_url}")
    print("   ✅ server_url property works correctly")
    
    # Test connection
    print("\n3. Testing connection...")
    try:
        connected = client.test_connection()
        if connected:
            print("   ✅ Successfully connected to Forge API")
        else:
            print("   ⚠️  Could not connect to Forge API (server may not be running)")
    except Exception as e:
        print(f"   ❌ Connection test failed: {e}")
    
    # Test getting models
    print("\n4. Testing get_models()...")
    try:
        models = client.get_models()
        if models:
            print(f"   ✅ Found {len(models)} models")
            for model in models[:3]:  # Show first 3 models
                print(f"      - {model.get('title', 'Unknown')}")
        else:
            print("   ⚠️  No models found (server may not be running)")
    except Exception as e:
        print(f"   ❌ Error getting models: {e}")
    
    # Test getting samplers
    print("\n5. Testing get_samplers()...")
    try:
        samplers = client.get_samplers()
        if samplers:
            print(f"   ✅ Found {len(samplers)} samplers")
            for sampler in samplers[:3]:  # Show first 3 samplers
                print(f"      - {sampler.get('name', 'Unknown')}")
        else:
            print("   ⚠️  No samplers found (server may not be running)")
    except Exception as e:
        print(f"   ❌ Error getting samplers: {e}")
    
    print("\n✅ Forge API Client test completed!")

def test_config_loading():
    """Test configuration loading."""
    print("\n📁 Testing Configuration Loading")
    print("=" * 40)
    
    try:
        from config_handler import ConfigHandler
        
        handler = ConfigHandler()
        configs = handler.list_configs()
        
        print(f"   Found {len(configs)} configurations:")
        for config_name in configs:
            print(f"      - {config_name}")
            
            try:
                config = handler.load_config(config_name)
                summary = handler.get_config_summary(config)
                print(f"        ✅ Loaded successfully")
                print(f"        📊 Total images: {summary.get('total_images', 'Unknown')}")
            except Exception as e:
                print(f"        ❌ Error loading: {e}")
                
    except Exception as e:
        print(f"   ❌ Error testing config loading: {e}")

def main():
    """Run all tests."""
    print("🚀 Forge API Tool - Direct API Test")
    print("=" * 50)
    
    test_forge_client()
    test_config_loading()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n💡 If you want to test the web dashboard:")
    print("   1. Start the dashboard: cd web_dashboard && python app.py")
    print("   2. Run the web API test: python test_api.py")

if __name__ == "__main__":
    main() 