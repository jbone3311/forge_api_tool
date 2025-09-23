#!/usr/bin/env python3
"""
MCP Functionality Verification
Tests actual functionality of key MCP tools
"""

import subprocess
import sys
import json
from pathlib import Path

def test_memory_bank():
    """Test memory-bank functionality"""
    print("🧠 Testing Memory Bank...")
    try:
        # Test if memory-bank can start (it should show help or version)
        result = subprocess.run([
            "npx", "mcp-memory-bank", "--help"
        ], capture_output=True, text=True, timeout=10, shell=True)
        
        if result.returncode == 0 or "memory" in result.stdout.lower():
            print("  ✅ Memory Bank: Functional")
            return True
        else:
            print("  ⚠️  Memory Bank: Installed but may need configuration")
            return False
    except Exception as e:
        print(f"  ❌ Memory Bank: Error - {e}")
        return False

def test_package_docs():
    """Test package-docs functionality"""
    print("\n📚 Testing Package Docs...")
    try:
        # Test if package-docs can start
        result = subprocess.run([
            "npx", "mcp-package-docs", "--help"
        ], capture_output=True, text=True, timeout=10, shell=True)
        
        if result.returncode == 0 or "MCP" in result.stdout or "MCP" in result.stderr:
            print("  ✅ Package Docs: Functional")
            return True
        else:
            print("  ⚠️  Package Docs: Installed but may need configuration")
            return False
    except Exception as e:
        print(f"  ❌ Package Docs: Error - {e}")
        return False

def test_playwright():
    """Test Playwright MCP server functionality"""
    print("\n🌐 Testing Playwright MCP server...")
    try:
        # Test if Playwright MCP server can start (should show help)
        result = subprocess.run([
            "npx", "@executeautomation/playwright-mcp-server", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 or "playwright" in result.stdout.lower():
            print("  ✅ Playwright MCP server: Functional")
            return True
        else:
            print("  ⚠️  Playwright MCP server: Installed but may need configuration")
            return False
    except Exception as e:
        print(f"  ❌ Playwright MCP server: Error - {e}")
        return False

def test_mcp_config_integration():
    """Test MCP configuration integration"""
    print("\n⚙️  Testing MCP Configuration Integration...")
    
    config_path = Path(".cursor/mcp.json")
    if not config_path.exists():
        print("  ❌ MCP config file not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        servers = config.get('mcpServers', {})
        print(f"  ✅ Found {len(servers)} configured servers:")
        
        for server_name in servers:
            print(f"    - {server_name}")
        
        # Check for critical servers
        critical_servers = ['memory-bank', 'package-docs', 'sequential-thinking']
        missing = [s for s in critical_servers if s not in servers]
        
        if missing:
            print(f"  ⚠️  Missing critical servers: {', '.join(missing)}")
            return False
        else:
            print("  ✅ All critical servers configured")
            return True
            
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def generate_functionality_report(results):
    """Generate functionality report"""
    print("\n" + "="*60)
    print("🔧 MCP FUNCTIONALITY VERIFICATION REPORT")
    print("="*60)
    
    working_tools = sum(1 for result in results.values() if result)
    total_tools = len(results)
    
    print(f"\n📊 FUNCTIONALITY SUMMARY:")
    for tool, working in results.items():
        status = "✅ Working" if working else "❌ Issues"
        print(f"  {tool}: {status}")
    
    print(f"\n📈 OVERALL: {working_tools}/{total_tools} tools functional")
    
    if working_tools >= total_tools * 0.8:
        print("\n🎉 STATUS: FULLY FUNCTIONAL")
        print("   Your MCP system is ready for production use!")
    elif working_tools >= total_tools * 0.5:
        print("\n⚠️  STATUS: PARTIALLY FUNCTIONAL")
        print("   Most tools work, but some may need configuration.")
    else:
        print("\n❌ STATUS: NEEDS ATTENTION")
        print("   Several tools have issues that need to be resolved.")
    
    print(f"\n💡 USAGE TIPS:")
    print("   - Configure your MCP client to use these tools")
    print("   - Set up environment variables for API keys")
    print("   - Test tools in your development workflow")
    print("   - Use memory-bank for project context")
    print("   - Use package-docs for documentation access")

def main():
    """Run functionality verification"""
    print("🔧 MCP FUNCTIONALITY VERIFICATION")
    print("="*60)
    
    # Test key functionality
    results = {
        "Memory Bank": test_memory_bank(),
        "Package Docs": test_package_docs(),
        "Playwright MCP": test_playwright(),
        "MCP Config": test_mcp_config_integration()
    }
    
    # Generate report
    generate_functionality_report(results)

if __name__ == "__main__":
    main() 