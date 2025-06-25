#!/usr/bin/env python3
"""
Comprehensive Forge API testing and data discovery script.
Discovers all available models, samplers, VAE, embeddings, loras, controlnets, and other settings.
Caches the data for use in the dashboard.
"""

import requests
import json
import os
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

class ForgeAPITester:
    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.cache_dir = "cache"
        self.cache_file = os.path.join(self.cache_dir, "forge_api_data.json")
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def test_connection(self) -> bool:
        """Test if Forge API is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Forge API is accessible")
                return True
            else:
                print(f"❌ Forge API returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to Forge API: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get basic API information."""
        print("\n🔍 Getting API information...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ API info retrieved")
                return {"status": "connected", "url": self.base_url}
            else:
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models."""
        print("\n🤖 Getting available models...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/sd-models")
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Found {len(models)} models")
                return {
                    "status": "success",
                    "count": len(models),
                    "models": models
                }
            else:
                print(f"❌ Failed to get models: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_samplers(self) -> Dict[str, Any]:
        """Get available samplers."""
        print("\n🎲 Getting available samplers...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/samplers")
            if response.status_code == 200:
                samplers = response.json()
                print(f"✅ Found {len(samplers)} samplers")
                return {
                    "status": "success",
                    "count": len(samplers),
                    "samplers": samplers
                }
            else:
                print(f"❌ Failed to get samplers: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting samplers: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_upscalers(self) -> Dict[str, Any]:
        """Get available upscalers."""
        print("\n🔍 Getting available upscalers...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/upscalers")
            if response.status_code == 200:
                upscalers = response.json()
                print(f"✅ Found {len(upscalers)} upscalers")
                return {
                    "status": "success",
                    "count": len(upscalers),
                    "upscalers": upscalers
                }
            else:
                print(f"❌ Failed to get upscalers: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting upscalers: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_embeddings(self) -> Dict[str, Any]:
        """Get available embeddings."""
        print("\n📝 Getting available embeddings...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/embeddings")
            if response.status_code == 200:
                embeddings = response.json()
                print(f"✅ Found {len(embeddings)} embeddings")
                return {
                    "status": "success",
                    "count": len(embeddings),
                    "embeddings": embeddings
                }
            else:
                print(f"❌ Failed to get embeddings: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting embeddings: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_loras(self) -> Dict[str, Any]:
        """Get available LoRAs."""
        print("\n🎨 Getting available LoRAs...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/loras")
            if response.status_code == 200:
                loras = response.json()
                print(f"✅ Found {len(loras)} LoRAs")
                return {
                    "status": "success",
                    "count": len(loras),
                    "loras": loras
                }
            else:
                print(f"❌ Failed to get LoRAs: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting LoRAs: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_controlnet_models(self) -> Dict[str, Any]:
        """Get available ControlNet models."""
        print("\n🎛️ Getting available ControlNet models...")
        try:
            response = self.session.get(f"{self.base_url}/controlnet/model_list")
            if response.status_code == 200:
                controlnet_models = response.json()
                print(f"✅ Found {len(controlnet_models)} ControlNet models")
                return {
                    "status": "success",
                    "count": len(controlnet_models),
                    "controlnet_models": controlnet_models
                }
            else:
                print(f"❌ Failed to get ControlNet models: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting ControlNet models: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_controlnet_modules(self) -> Dict[str, Any]:
        """Get available ControlNet modules."""
        print("\n🔧 Getting available ControlNet modules...")
        try:
            response = self.session.get(f"{self.base_url}/controlnet/module_list")
            if response.status_code == 200:
                controlnet_modules = response.json()
                print(f"✅ Found {len(controlnet_modules)} ControlNet modules")
                return {
                    "status": "success",
                    "count": len(controlnet_modules),
                    "controlnet_modules": controlnet_modules
                }
            else:
                print(f"❌ Failed to get ControlNet modules: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting ControlNet modules: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_scripts(self) -> Dict[str, Any]:
        """Get available scripts."""
        print("\n📜 Getting available scripts...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/scripts")
            if response.status_code == 200:
                scripts = response.json()
                print(f"✅ Found {len(scripts)} scripts")
                return {
                    "status": "success",
                    "count": len(scripts),
                    "scripts": scripts
                }
            else:
                print(f"❌ Failed to get scripts: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting scripts: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_options(self) -> Dict[str, Any]:
        """Get current options/settings."""
        print("\n⚙️ Getting current options...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/options")
            if response.status_code == 200:
                options = response.json()
                print("✅ Options retrieved")
                return {
                    "status": "success",
                    "options": options
                }
            else:
                print(f"❌ Failed to get options: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting options: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_face_restorers(self) -> Dict[str, Any]:
        """Get available face restorers."""
        print("\n👤 Getting available face restorers...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/face-restorers")
            if response.status_code == 200:
                face_restorers = response.json()
                print(f"✅ Found {len(face_restorers)} face restorers")
                return {
                    "status": "success",
                    "count": len(face_restorers),
                    "face_restorers": face_restorers
                }
            else:
                print(f"❌ Failed to get face restorers: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting face restorers: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_hypernetworks(self) -> Dict[str, Any]:
        """Get available hypernetworks."""
        print("\n🧠 Getting available hypernetworks...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/hypernetworks")
            if response.status_code == 200:
                hypernetworks = response.json()
                print(f"✅ Found {len(hypernetworks)} hypernetworks")
                return {
                    "status": "success",
                    "count": len(hypernetworks),
                    "hypernetworks": hypernetworks
                }
            else:
                print(f"❌ Failed to get hypernetworks: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting hypernetworks: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_vaes(self) -> Dict[str, Any]:
        """Get available VAEs."""
        print("\n🎨 Getting available VAEs...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/sd-vae")
            if response.status_code == 200:
                vaes = response.json()
                print(f"✅ Found {len(vaes)} VAEs")
                return {
                    "status": "success",
                    "count": len(vaes),
                    "vaes": vaes
                }
            else:
                print(f"❌ Failed to get VAEs: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting VAEs: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_style_presets(self) -> Dict[str, Any]:
        """Get available style presets."""
        print("\n🎭 Getting available style presets...")
        try:
            response = self.session.get(f"{self.base_url}/sdapi/v1/prompt-styles")
            if response.status_code == 200:
                style_presets = response.json()
                print(f"✅ Found {len(style_presets)} style presets")
                return {
                    "status": "success",
                    "count": len(style_presets),
                    "style_presets": style_presets
                }
            else:
                print(f"❌ Failed to get style presets: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error getting style presets: {e}")
            return {"status": "error", "error": str(e)}
    
    def discover_all_data(self) -> Dict[str, Any]:
        """Discover all available data from the Forge API."""
        print("🚀 Starting comprehensive Forge API data discovery...")
        print("=" * 80)
        
        # Test connection first
        if not self.test_connection():
            return {"error": "Cannot connect to Forge API"}
        
        # Collect all data
        data = {
            "timestamp": time.time(),
            "api_info": self.get_api_info(),
            "models": self.get_models(),
            "samplers": self.get_samplers(),
            "upscalers": self.get_upscalers(),
            "embeddings": self.get_embeddings(),
            "loras": self.get_loras(),
            "controlnet_models": self.get_controlnet_models(),
            "controlnet_modules": self.get_controlnet_modules(),
            "scripts": self.get_scripts(),
            "options": self.get_options(),
            "face_restorers": self.get_face_restorers(),
            "hypernetworks": self.get_hypernetworks(),
            "vaes": self.get_vaes(),
            "style_presets": self.get_style_presets()
        }
        
        return data
    
    def save_cache(self, data: Dict[str, Any]):
        """Save data to cache file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Data cached to {self.cache_file}")
        except Exception as e:
            print(f"❌ Error saving cache: {e}")
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load data from cache file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ Loaded cached data from {self.cache_file}")
                return data
            else:
                print("❌ No cache file found")
                return None
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return None
    
    def print_summary(self, data: Dict[str, Any]):
        """Print a summary of discovered data."""
        print("\n" + "=" * 80)
        print("📊 DISCOVERED DATA SUMMARY")
        print("=" * 80)
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return
        
        print(f"Timestamp: {time.ctime(data.get('timestamp', 0))}")
        print()
        
        # Count successful discoveries
        successful = 0
        total = 0
        
        for key, value in data.items():
            if key == "timestamp":
                continue
                
            total += 1
            if isinstance(value, dict) and value.get("status") == "success":
                successful += 1
                count = value.get("count", "N/A")
                print(f"✅ {key.replace('_', ' ').title()}: {count}")
            elif isinstance(value, dict) and value.get("status") == "error":
                print(f"❌ {key.replace('_', ' ').title()}: {value.get('error', 'Unknown error')}")
            else:
                print(f"⚠️  {key.replace('_', ' ').title()}: Unknown status")
        
        print(f"\nSuccess Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    def test_simple_generation(self) -> Dict[str, Any]:
        """Test a simple image generation to verify API functionality."""
        print("\n🎨 Testing simple image generation...")
        try:
            payload = {
                "prompt": "a simple test image",
                "negative_prompt": "",
                "steps": 1,
                "width": 64,
                "height": 64,
                "sampler_name": "Euler a",
                "cfg_scale": 7.0,
                "seed": 12345
            }
            
            response = self.session.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload)
            if response.status_code == 200:
                print("✅ Simple generation test successful")
                return {"status": "success", "message": "Generation test passed"}
            else:
                print(f"❌ Generation test failed: {response.status_code}")
                return {"status": "error", "error": f"Status {response.status_code}"}
        except Exception as e:
            print(f"❌ Error in generation test: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main function to run the API discovery."""
    print("🔍 Forge API Data Discovery Tool")
    print("=" * 80)
    
    # Initialize tester
    tester = ForgeAPITester()
    
    # Check if we should use cache or discover fresh
    use_cache = input("Use cached data if available? (y/n): ").lower().startswith('y')
    
    if use_cache:
        cached_data = tester.load_cache()
        if cached_data:
            tester.print_summary(cached_data)
            return
    
    # Discover all data
    data = tester.discover_all_data()
    
    # Test generation
    generation_test = tester.test_simple_generation()
    data["generation_test"] = generation_test
    
    # Save to cache
    tester.save_cache(data)
    
    # Print summary
    tester.print_summary(data)
    
    # Save a simplified version for the dashboard
    dashboard_data = {
        "models": [model["title"] for model in data.get("models", {}).get("models", [])],
        "samplers": [sampler["name"] for sampler in data.get("samplers", {}).get("samplers", [])],
        "vaes": [vae["model_name"] for vae in data.get("vaes", {}).get("vaes", [])],
        "loras": [lora["name"] for lora in data.get("loras", {}).get("loras", [])],
        "embeddings": [emb["name"] for emb in data.get("embeddings", {}).get("embeddings", [])],
        "controlnet_models": [cn["model"] for cn in data.get("controlnet_models", {}).get("controlnet_models", [])],
        "controlnet_modules": [cn["module"] for cn in data.get("controlnet_modules", {}).get("controlnet_modules", [])],
        "face_restorers": [fr["name"] for fr in data.get("face_restorers", {}).get("face_restorers", [])],
        "upscalers": [up["name"] for up in data.get("upscalers", {}).get("upscalers", [])]
    }
    
    dashboard_cache_file = os.path.join(tester.cache_dir, "dashboard_data.json")
    with open(dashboard_cache_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Dashboard data saved to {dashboard_cache_file}")

if __name__ == "__main__":
    main() 