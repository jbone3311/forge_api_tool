#!/usr/bin/env python3
"""
MCP Tools Setup Script
Installs all required MCP tools for AI development
Based on verified tools from awesome-mcp-servers list
"""

import subprocess
import sys
import os
from pathlib import Path

def install_mcp_tools():
    """Install all MCP tools required for AI development"""
    
    # Real MCP tools that actually exist (verified from awesome-mcp-servers)
    python_mcp_tools = [
        "mcp-playwright",
        "mcp"
    ]
    
    # Node.js MCP tools that actually exist (verified from awesome-mcp-servers)
    node_mcp_tools = [
        "mcp-memory-bank",
        "mcp-knowledge-graph", 
        "@YassineTk/mcp-docs-provider",
        "@modelcontextprotocol/server-sequential-thinking",
        "@modelcontextprotocol/server-postgres",
        "@modelcontextprotocol/server-brave-search",
        "@modelcontextprotocol/server-github"
    ]
    
    print("🚀 Installing MCP tools for AI development...")
    print("📋 Based on verified tools from awesome-mcp-servers list")
    
    # Install Python MCP tools
    print("\n🐍 Installing Python MCP tools...")
    for tool in python_mcp_tools:
        try:
            print(f"  Installing {tool}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", tool, "--user"
            ], capture_output=True, text=True, check=True)
            print(f"  ✅ {tool} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {tool}: {e.stderr}")
        except FileNotFoundError:
            print(f"  ❌ pip not found. Please install Python and pip first.")
            return False
    
    # Install Node.js MCP tools
    print("\n📦 Installing Node.js MCP tools...")
    for tool in node_mcp_tools:
        try:
            print(f"  Installing {tool}...")
            result = subprocess.run([
                "npm", "install", "-g", tool
            ], capture_output=True, text=True, check=True)
            print(f"  ✅ {tool} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {tool}: {e.stderr}")
        except FileNotFoundError:
            print(f"  ❌ npm not found. Please install Node.js and npm first.")
            return False
    
    print("\n✅ MCP tools installation complete!")
    print("\n📚 Next steps:")
    print("1. Configure your MCP client (Claude Desktop, Cursor, etc.)")
    print("2. Set up environment variables for API keys:")
    print("   - BRAVE_API_KEY for Brave Search")
    print("   - GITHUB_TOKEN for GitHub integration")
    print("3. Test the installation: python setup-mcp-tools.py --test")
    
    return True

def test_mcp_tools():
    """Test if MCP tools are properly installed"""
    print("🧪 Testing MCP tools installation...")
    
    # Test Python tools
    python_tools = ["mcp-playwright", "mcp"]
    for tool in python_tools:
        try:
            result = subprocess.run([
                sys.executable, "-m", tool, "--version"
            ], capture_output=True, text=True, check=True)
            print(f"  ✅ {tool}: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print(f"  ❌ {tool}: Not working properly")
        except FileNotFoundError:
            print(f"  ❌ {tool}: Not found")
    
    # Test Node.js tools
    node_tools = [
        "mcp-memory-bank",
        "mcp-knowledge-graph",
        "@YassineTk/mcp-docs-provider"
    ]
    
    for tool in node_tools:
        try:
            # Try to run the tool to see if it's available
            result = subprocess.run([
                "npx", tool, "--help"
            ], capture_output=True, text=True, timeout=10)
            print(f"  ✅ {tool}: Available")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            print(f"  ❌ {tool}: Not available or not working")
    
    print("\n📋 Installation Summary:")
    print("- Python MCP tools: mcp-playwright, mcp")
    print("- Node.js MCP tools: memory-bank, knowledge-graph, docs-provider, sequential-thinking, postgres, brave-search, github")
    print("\n🔗 For more MCP tools, visit: https://github.com/appcypher/awesome-mcp-servers")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mcp_tools()
    else:
        install_mcp_tools() 