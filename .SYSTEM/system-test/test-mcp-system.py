#!/usr/bin/env python3
"""
Comprehensive MCP System Test
Tests all installed MCP tools and provides detailed feedback
"""

import subprocess
import sys
import json
import os
from pathlib import Path

def test_python_tools():
    """Test Python MCP tools"""
    print("🐍 Testing Python MCP Tools...")
    
    python_tools = [
        ("mcp", "import mcp; print('mcp available')")
    ]
    
    results = {}
    for tool_name, import_test in python_tools:
        try:
            result = subprocess.run([
                sys.executable, "-c", import_test
            ], capture_output=True, text=True, check=True)
            
            if "available" in result.stdout:
                print(f"  ✅ {tool_name}: Available")
                results[tool_name] = "Available"
            else:
                print(f"  ❌ {tool_name}: Not working properly")
                results[tool_name] = "Not working"
        except subprocess.CalledProcessError:
            print(f"  ❌ {tool_name}: Not found")
            results[tool_name] = "Not found"
    
    return results

def test_node_tools():
    """Test Node.js MCP tools"""
    print("\n📦 Testing Node.js MCP Tools...")
    
    node_tools = [
        "mcp-memory-bank",
        "mcp-knowledge-graph", 
        "mcp-package-docs",
        "@modelcontextprotocol/server-sequential-thinking",
        "@modelcontextprotocol/server-postgres",
        "@modelcontextprotocol/server-brave-search",
        "@modelcontextprotocol/server-github",
        "@executeautomation/playwright-mcp-server"
    ]
    
    results = {}
    for tool in node_tools:
        try:
            # Test if tool can be executed
            result = subprocess.run([
                "npx", tool, "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 or "MCP" in result.stdout or "MCP" in result.stderr:
                print(f"  ✅ {tool}: Available")
                results[tool] = "Available"
            else:
                print(f"  ⚠️  {tool}: Installed but may need configuration")
                results[tool] = "Needs configuration"
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  {tool}: Timeout (may be waiting for input)")
            results[tool] = "Timeout"
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {tool}: Not available")
            results[tool] = "Not available"
    
    return results

def test_mcp_config():
    """Test MCP configuration file"""
    print("\n⚙️  Testing MCP Configuration...")
    
    config_path = Path(".cursor/mcp.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            print(f"  ✅ MCP config found: {len(config.get('mcpServers', {}))} servers configured")
            
            # Check for required environment variables
            env_vars_needed = []
            for server_name, server_config in config.get('mcpServers', {}).items():
                args = server_config.get('args', [])
                for arg in args:
                    if arg.startswith('${') and arg.endswith('}'):
                        env_var = arg[2:-1]
                        env_vars_needed.append(env_var)
            
            if env_vars_needed:
                print(f"  ⚠️  Environment variables needed: {', '.join(env_vars_needed)}")
            else:
                print("  ✅ No environment variables required")
                
            return True
        except json.JSONDecodeError:
            print("  ❌ MCP config is invalid JSON")
            return False
    else:
        print("  ❌ MCP config file not found")
        return False

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing Environment...")
    
    # Check Node.js and npm
    try:
        node_result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"  ✅ Node.js: {node_result.stdout.strip()}")
        print(f"  ✅ npm: {npm_result.stdout.strip()}")
    except FileNotFoundError:
        print("  ❌ Node.js or npm not found")
        return False
    
    # Check Python
    try:
        python_result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"  ✅ Python: {python_result.stdout.strip()}")
    except FileNotFoundError:
        print("  ❌ Python not found")
        return False
    
    return True

def generate_report(python_results, node_results, config_ok, env_ok):
    """Generate a comprehensive report"""
    print("\n" + "="*60)
    print("📊 MCP SYSTEM TEST REPORT")
    print("="*60)
    
    # Summary
    python_available = sum(1 for status in python_results.values() if status == "Available")
    node_available = sum(1 for status in node_results.values() if status == "Available")
    
    print(f"\n📈 SUMMARY:")
    print(f"  Python MCP Tools: {python_available}/{len(python_results)} available")
    print(f"  Node.js MCP Tools: {node_available}/{len(node_results)} available")
    print(f"  MCP Configuration: {'✅ Valid' if config_ok else '❌ Invalid'}")
    print(f"  Environment: {'✅ Ready' if env_ok else '❌ Issues'}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if python_available < len(python_results):
        print("  - Some Python MCP tools need attention")
    
    if node_available < len(node_results):
        print("  - Some Node.js MCP tools may need configuration")
    
    if not config_ok:
        print("  - Fix MCP configuration file")
    
    if not env_ok:
        print("  - Ensure Node.js, npm, and Python are properly installed")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    print("  1. Configure your MCP client (Cursor, Claude Desktop, etc.)")
    print("  2. Set up environment variables for API keys:")
    print("     - BRAVE_API_KEY for Brave Search")
    print("     - GITHUB_TOKEN for GitHub integration")
    print("     - DATABASE_URL for PostgreSQL (if using)")
    print("  3. Test tools in your development workflow")
    
    # Overall status
    total_tools = len(python_results) + len(node_results)
    available_tools = python_available + node_available
    
    if available_tools >= total_tools * 0.8:  # 80% threshold
        print(f"\n🎉 STATUS: READY FOR USE ({available_tools}/{total_tools} tools available)")
    elif available_tools >= total_tools * 0.5:  # 50% threshold
        print(f"\n⚠️  STATUS: PARTIALLY READY ({available_tools}/{total_tools} tools available)")
    else:
        print(f"\n❌ STATUS: NEEDS ATTENTION ({available_tools}/{total_tools} tools available)")

def main():
    """Run comprehensive MCP system test"""
    print("🧪 COMPREHENSIVE MCP SYSTEM TEST")
    print("="*60)
    
    # Test all components
    python_results = test_python_tools()
    node_results = test_node_tools()
    config_ok = test_mcp_config()
    env_ok = test_environment()
    
    # Generate report
    generate_report(python_results, node_results, config_ok, env_ok)

if __name__ == "__main__":
    main() 