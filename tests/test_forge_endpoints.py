#!/usr/bin/env python3
"""
Forge API Endpoint Discovery Script
Tests various API endpoints to find the correct syntax for Forge.
"""

import requests
import json
import time
from typing import Dict, Any, List

class ForgeEndpointTester:
    def __init__(self, base_url: str = "http://127.0.0.1:7860"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test a specific endpoint."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data if data else {})
            else:
                return {"status": "error", "error": f"Unsupported method: {method}"}
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "url": url,
                "method": method,
                "response": response.text[:500] if response.text else "No response body",
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url,
                "method": method
            }
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all possible Forge API endpoints."""
        print("🔍 Testing Forge API Endpoints...")
        print("=" * 60)
        
        # Test basic connectivity first
        print("1. Testing basic connectivity...")
        basic_test = self.test_endpoint("/")
        print(f"   Root endpoint: {basic_test['status_code'] if 'status_code' in basic_test else 'ERROR'}")
        
        # Standard SD WebUI endpoints
        print("\n2. Testing standard SD WebUI endpoints...")
        sd_endpoints = [
            "/sdapi/v1/sd-models",
            "/sdapi/v1/samplers", 
            "/sdapi/v1/upscalers",
            "/sdapi/v1/embeddings",
            "/sdapi/v1/loras",
            "/sdapi/v1/scripts",
            "/sdapi/v1/options",
            "/sdapi/v1/face-restorers",
            "/sdapi/v1/hypernetworks",
            "/sdapi/v1/sd-vae",
            "/sdapi/v1/prompt-styles",
            "/sdapi/v1/progress"
        ]
        
        sd_results = {}
        for endpoint in sd_endpoints:
            result = self.test_endpoint(endpoint)
            sd_results[endpoint] = result
            status = "✅" if result['status'] == "success" else "❌"
            print(f"   {status} {endpoint}: {result.get('status_code', 'ERROR')}")
        
        # Forge-specific endpoints (possible variations)
        print("\n3. Testing Forge-specific endpoints...")
        forge_endpoints = [
            "/api/v1/models",
            "/api/v1/samplers",
            "/api/v1/loras",
            "/api/v1/options",
            "/api/models",
            "/api/samplers",
            "/api/loras",
            "/api/options",
            "/models",
            "/samplers",
            "/loras",
            "/options"
        ]
        
        forge_results = {}
        for endpoint in forge_endpoints:
            result = self.test_endpoint(endpoint)
            forge_results[endpoint] = result
            status = "✅" if result['status'] == "success" else "❌"
            print(f"   {status} {endpoint}: {result.get('status_code', 'ERROR')}")
        
        # ControlNet endpoints
        print("\n4. Testing ControlNet endpoints...")
        controlnet_endpoints = [
            "/controlnet/model_list",
            "/controlnet/module_list",
            "/sdapi/v1/controlnet/model_list",
            "/sdapi/v1/controlnet/module_list",
            "/api/v1/controlnet/models",
            "/api/v1/controlnet/modules"
        ]
        
        controlnet_results = {}
        for endpoint in controlnet_endpoints:
            result = self.test_endpoint(endpoint)
            controlnet_results[endpoint] = result
            status = "✅" if result['status'] == "success" else "❌"
            print(f"   {status} {endpoint}: {result.get('status_code', 'ERROR')}")
        
        # Test image generation endpoint
        print("\n5. Testing image generation endpoint...")
        gen_payload = {
            "prompt": "a beautiful landscape",
            "negative_prompt": "blurry, low quality",
            "steps": 20,
            "width": 512,
            "height": 512,
            "sampler_name": "Euler a",
            "cfg_scale": 7.0,
            "seed": -1
        }
        
        gen_endpoints = [
            ("/sdapi/v1/txt2img", gen_payload),
            ("/api/v1/generate", gen_payload),
            ("/api/generate", gen_payload),
            ("/generate", gen_payload)
        ]
        
        gen_results = {}
        for endpoint, payload in gen_endpoints:
            result = self.test_endpoint(endpoint, "POST", payload)
            gen_results[endpoint] = result
            status = "✅" if result['status'] == "success" else "❌"
            print(f"   {status} {endpoint}: {result.get('status_code', 'ERROR')}")
        
        # Compile results
        all_results = {
            "basic": basic_test,
            "sd_endpoints": sd_endpoints,
            "forge_endpoints": forge_endpoints,
            "controlnet_endpoints": controlnet_endpoints,
            "generation_endpoints": [ep[0] for ep in gen_endpoints],
            "results": {
                "sd": sd_results,
                "forge": forge_results,
                "controlnet": controlnet_results,
                "generation": gen_results
            }
        }
        
        return all_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of the test results."""
        print("\n" + "=" * 60)
        print("📊 ENDPOINT TEST SUMMARY")
        print("=" * 60)
        
        # Count working endpoints
        working_sd = sum(1 for r in results['results']['sd'].values() if r['status'] == 'success')
        working_forge = sum(1 for r in results['results']['forge'].values() if r['status'] == 'success')
        working_controlnet = sum(1 for r in results['results']['controlnet'].values() if r['status'] == 'success')
        working_gen = sum(1 for r in results['results']['generation'].values() if r['status'] == 'success')
        
        print(f"✅ Working SD endpoints: {working_sd}/{len(results['results']['sd'])}")
        print(f"✅ Working Forge endpoints: {working_forge}/{len(results['results']['forge'])}")
        print(f"✅ Working ControlNet endpoints: {working_controlnet}/{len(results['results']['controlnet'])}")
        print(f"✅ Working generation endpoints: {working_gen}/{len(results['results']['generation'])}")
        
        # Show working endpoints
        print("\n🔧 Working endpoints:")
        for category, endpoints in results['results'].items():
            working = [ep for ep, result in endpoints.items() if result['status'] == 'success']
            if working:
                print(f"   {category.upper()}:")
                for ep in working:
                    print(f"     ✅ {ep}")
        
        # Show common error patterns
        print("\n❌ Common errors:")
        error_patterns = {}
        for category, endpoints in results['results'].items():
            for ep, result in endpoints.items():
                if result['status'] == 'error':
                    error_code = result.get('status_code', 'CONNECTION_ERROR')
                    if error_code not in error_patterns:
                        error_patterns[error_code] = []
                    error_patterns[error_code].append(ep)
        
        for error_code, endpoints in error_patterns.items():
            print(f"   {error_code}: {len(endpoints)} endpoints")
            for ep in endpoints[:3]:  # Show first 3
                print(f"     - {ep}")
            if len(endpoints) > 3:
                print(f"     ... and {len(endpoints) - 3} more")

def main():
    print("🚀 Forge API Endpoint Discovery")
    print("=" * 60)
    
    tester = ForgeEndpointTester()
    results = tester.test_all_endpoints()
    tester.print_summary(results)
    
    # Save results to file
    with open('forge_endpoint_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to forge_endpoint_test_results.json")

if __name__ == "__main__":
    main() 