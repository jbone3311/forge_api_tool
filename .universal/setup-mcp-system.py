#!/usr/bin/env python3
"""
Universal MCP System Setup
Installs and configures all real MCP tools for AI development
"""

import subprocess
import sys
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class MCPSystemSetup:
    """Comprehensive MCP system setup and configuration"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.universal_dir = self.project_root / ".universal"
        self.mcp_dir = self.universal_dir / "mcp"
        self.memory_dir = self.universal_dir / "memory"
        self.docs_dir = self.universal_dir / "docs"
        
        # Real MCP tools that actually exist
        self.python_tools = [
            "mcp-playwright",
            "mcp"
        ]
        
        self.node_tools = [
            "@modelcontextprotocol/server-sequential-thinking",
            "@modelcontextprotocol/server-postgres",
            "@modelcontextprotocol/server-brave-search",
            "@modelcontextprotocol/server-github"
        ]
        
        self.installation_results = {
            "python_tools": {},
            "node_tools": {},
            "configuration": {},
            "documentation": {}
        }
    
    def setup_directory_structure(self) -> None:
        """Create necessary directories"""
        print("📁 Setting up directory structure...")
        
        directories = [
            self.universal_dir,
            self.mcp_dir,
            self.memory_dir / "main",
            self.memory_dir / "tasks",
            self.memory_dir / "docs-cache",
            self.docs_dir,
            self.docs_dir / "mcp",
            self.docs_dir / "templates"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created {directory}")
    
    def install_python_mcp_tools(self) -> None:
        """Install Python MCP tools"""
        print("\n🐍 Installing Python MCP tools...")
        
        for tool in self.python_tools:
            try:
                print(f"  Installing {tool}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", tool, "--user"
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"    ✅ {tool} installed successfully")
                    self.installation_results["python_tools"][tool] = {
                        "status": "success",
                        "version": self.get_python_tool_version(tool)
                    }
                else:
                    print(f"    ❌ Failed to install {tool}: {result.stderr}")
                    self.installation_results["python_tools"][tool] = {
                        "status": "failed",
                        "error": result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  {tool} installation timed out")
                self.installation_results["python_tools"][tool] = {
                    "status": "timeout",
                    "error": "Installation timed out"
                }
            except Exception as e:
                print(f"    ❌ Error installing {tool}: {e}")
                self.installation_results["python_tools"][tool] = {
                    "status": "error",
                    "error": str(e)
                }
    
    def install_node_mcp_tools(self) -> None:
        """Install Node.js MCP tools"""
        print("\n📦 Installing Node.js MCP tools...")
        
        for tool in self.node_tools:
            try:
                print(f"  Installing {tool}...")
                result = subprocess.run([
                    "npm", "install", "-g", tool
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"    ✅ {tool} installed successfully")
                    self.installation_results["node_tools"][tool] = {
                        "status": "success",
                        "version": self.get_node_tool_version(tool)
                    }
                else:
                    print(f"    ❌ Failed to install {tool}: {result.stderr}")
                    self.installation_results["node_tools"][tool] = {
                        "status": "failed",
                        "error": result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                print(f"    ⚠️  {tool} installation timed out")
                self.installation_results["node_tools"][tool] = {
                    "status": "timeout",
                    "error": "Installation timed out"
                }
            except Exception as e:
                print(f"    ❌ Error installing {tool}: {e}")
                self.installation_results["node_tools"][tool] = {
                    "status": "error",
                    "error": str(e)
                }
    
    def get_python_tool_version(self, tool: str) -> str:
        """Get version of installed Python tool"""
        try:
            result = subprocess.run([
                sys.executable, "-m", tool, "--version"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "Unknown"
        except:
            return "Unknown"
    
    def get_node_tool_version(self, tool: str) -> str:
        """Get version of installed Node.js tool"""
        try:
            result = subprocess.run([
                "npx", tool, "--version"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "Unknown"
        except:
            return "Unknown"
    
    def create_mcp_configuration(self) -> None:
        """Create MCP configuration file"""
        print("\n⚙️  Creating MCP configuration...")
        
        mcp_config = {
            "mcpServers": {
                "playwright": {
                    "command": "mcp-playwright",
                    "args": []
                },
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-sequential-thinking"
                    ]
                },
                "postgres": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-postgres",
                        "--connection-string",
                        "postgresql://localhost:5432/your_database"
                    ]
                },
                "brave-search": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-brave-search",
                        "--api-key",
                        "${BRAVE_API_KEY}"
                    ]
                },
                "github": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-github",
                        "--token",
                        "${GITHUB_TOKEN}"
                    ]
                }
            }
        }
        
        config_file = self.mcp_dir / "mcp.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"  ✅ Created {config_file}")
        self.installation_results["configuration"]["mcp.json"] = {
            "status": "created",
            "path": str(config_file)
        }
    
    def create_mcp_documentation(self) -> None:
        """Create comprehensive MCP documentation"""
        print("\n📚 Creating MCP documentation...")
        
        # MCP Tools Reference
        tools_reference = """# MCP Tools Reference

## Overview
This document provides a comprehensive reference for all MCP (Model Context Protocol) tools used in the Universal AI Development System.

## Python MCP Tools

### mcp-playwright
**Purpose**: Browser automation and web testing
**Installation**: `pip install mcp-playwright --user`
**Usage**: `mcp-playwright --help`
**Features**:
- Web page automation
- Screenshot capture
- Form filling
- Navigation testing

### mcp (Core Framework)
**Purpose**: Core MCP framework and CLI tools
**Installation**: `pip install mcp --user`
**Usage**: `mcp --help`
**Features**:
- MCP server management
- Tool validation
- Configuration management

## Node.js MCP Tools

### @modelcontextprotocol/server-sequential-thinking
**Purpose**: Sequential thinking and problem solving
**Installation**: `npm install -g @modelcontextprotocol/server-sequential-thinking`
**Usage**: `npx @modelcontextprotocol/server-sequential-thinking --help`
**Features**:
- Step-by-step problem solving
- Task planning and execution
- Progress tracking
- Decision documentation

### @modelcontextprotocol/server-postgres
**Purpose**: PostgreSQL database integration
**Installation**: `npm install -g @modelcontextprotocol/server-postgres`
**Usage**: `npx @modelcontextprotocol/server-postgres --help`
**Features**:
- Database queries
- Schema management
- Data analysis
- Knowledge storage

### @modelcontextprotocol/server-brave-search
**Purpose**: Web search integration
**Installation**: `npm install -g @modelcontextprotocol/server-brave-search`
**Usage**: `npx @modelcontextprotocol/server-brave-search --help`
**Features**:
- Web search queries
- Information retrieval
- Research assistance
- Knowledge discovery

### @modelcontextprotocol/server-github
**Purpose**: GitHub API integration
**Installation**: `npm install -g @modelcontextprotocol/server-github`
**Usage**: `npx @modelcontextprotocol/server-github --help`
**Features**:
- Repository access
- Issue management
- Documentation retrieval
- Code analysis

## Configuration

### Environment Variables
```bash
# Database connection
export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/your_database"

# API Keys
export BRAVE_API_KEY="your_brave_api_key"
export GITHUB_TOKEN="your_github_token"
```

### MCP Configuration File
Location: `.universal/mcp/mcp.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "mcp-playwright",
      "args": []
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-postgres",
        "--connection-string",
        "postgresql://localhost:5432/your_database"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-brave-search",
        "--api-key",
        "${BRAVE_API_KEY}"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-github",
        "--token",
        "${GITHUB_TOKEN}"
      ]
    }
  }
}
```

## Usage Examples

### Sequential Thinking
```bash
# Create a plan
sequential-thinking: "Create 5-step plan for implementing user authentication"

# Execute step
sequential-thinking: "Generate code for step 1: database schema design"

# Mark step complete
sequential-thinking: done 1
```

### Database Operations
```bash
# Query dependencies
postgres: "SELECT * FROM dependencies WHERE component = 'auth'"

# Store knowledge
postgres: "INSERT INTO knowledge (topic, content) VALUES ('auth', 'OAuth2 implementation')"
```

### Web Search
```bash
# Research topic
brave-search: "latest React authentication patterns 2024"

# Find documentation
brave-search: "MCP protocol specification"
```

### GitHub Integration
```bash
# Access repository
github: "get repository content for user/repo"

# Create issue
github: "create issue: 'Implement user authentication'"
```

## Troubleshooting

### Common Issues

**Tool not found**
```bash
# Python tools
pip install mcp-playwright mcp --user

# Node.js tools
npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Permission errors**
```bash
# Use --user flag for Python
pip install mcp-playwright --user

# Use sudo for global npm (Linux/Mac)
sudo npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Connection errors**
```bash
# Check if tools are running
mcp-playwright --version
npx @modelcontextprotocol/server-sequential-thinking --version
```

## Best Practices

1. **Always use --user flag** for Python tool installation
2. **Set environment variables** for API keys and connections
3. **Test tools individually** before using in workflows
4. **Document decisions** using sequential-thinking
5. **Store knowledge** in postgres for future reference
6. **Use web search** for research and problem solving
7. **Integrate with GitHub** for documentation and issues

## Support

For issues or questions:
1. Check tool documentation: `tool-name --help`
2. Review this reference guide
3. Check installation status: `python .universal/setup-mcp-system.py --test`
4. Run comprehensive tests: `python .universal/test-system/test-universal-system.py`
"""
        
        # Write tools reference
        tools_file = self.docs_dir / "mcp" / "mcp-tools-reference.md"
        with open(tools_file, "w", encoding="utf-8") as f:
            f.write(tools_reference)
        
        print(f"  ✅ Created {tools_file}")
        
        # Installation Guide
        installation_guide = """# MCP System Installation Guide

## Quick Installation

```bash
# Run the automated setup
python .universal/setup-mcp-system.py

# Or install manually
python .universal/setup-mcp-system.py --manual
```

## Manual Installation Steps

### 1. Install Python MCP Tools
```bash
pip install mcp-playwright mcp --user
```

### 2. Install Node.js MCP Tools
```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
```

### 3. Verify Installation
```bash
# Test Python tools
mcp-playwright --version
mcp --version

# Test Node.js tools
npx @modelcontextprotocol/server-sequential-thinking --version
npx @modelcontextprotocol/server-postgres --version
```

### 4. Configure Environment
```bash
# Set up environment variables
export BRAVE_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/your_db"
```

## Testing

### Quick Test
```bash
python .universal/setup-mcp-system.py --test
```

### Comprehensive Test
```bash
python .universal/test-system/test-universal-system.py
```

## Troubleshooting

See the troubleshooting section in `mcp-tools-reference.md` for common issues and solutions.
"""
        
        # Write installation guide
        install_file = self.docs_dir / "mcp" / "installation-guide.md"
        with open(install_file, "w", encoding="utf-8") as f:
            f.write(installation_guide)
        
        print(f"  ✅ Created {install_file}")
        
        self.installation_results["documentation"] = {
            "tools_reference": str(tools_file),
            "installation_guide": str(install_file)
        }
    
    def create_mcp_templates(self) -> None:
        """Create MCP-specific templates"""
        print("\n📋 Creating MCP templates...")
        
        # Sequential Thinking Template
        sequential_template = """# Sequential Thinking Template

## Task: [TASK_NAME]

### Step 1: [STEP_1_DESCRIPTION]
- [ ] Define requirements
- [ ] Research existing solutions
- [ ] Document approach

### Step 2: [STEP_2_DESCRIPTION]
- [ ] Create implementation plan
- [ ] Set up development environment
- [ ] Begin implementation

### Step 3: [STEP_3_DESCRIPTION]
- [ ] Implement core functionality
- [ ] Write tests
- [ ] Document code

### Step 4: [STEP_4_DESCRIPTION]
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Security review

### Step 5: [STEP_5_DESCRIPTION]
- [ ] Final testing
- [ ] Documentation update
- [ ] Deployment preparation

## Commands
```bash
# Start planning
sequential-thinking: "Create 5-step plan for [TASK_NAME]"

# Execute step
sequential-thinking: "Generate code for step [N]: [DESCRIPTION]"

# Mark complete
sequential-thinking: done [N]
```

## Progress Tracking
- [ ] Step 1 complete
- [ ] Step 2 complete
- [ ] Step 3 complete
- [ ] Step 4 complete
- [ ] Step 5 complete

## Notes
- Decision points:
- Challenges encountered:
- Solutions implemented:
- Lessons learned:
"""
        
        # Database Knowledge Template
        knowledge_template = """# Database Knowledge Template

## Topic: [TOPIC_NAME]

### Overview
Brief description of the topic and its importance.

### Key Concepts
- Concept 1: [Description]
- Concept 2: [Description]
- Concept 3: [Description]

### Implementation Details
```sql
-- Example queries
SELECT * FROM knowledge WHERE topic = '[TOPIC_NAME]';
INSERT INTO knowledge (topic, content, created_at) VALUES ('[TOPIC_NAME]', '[CONTENT]', NOW());
```

### Related Topics
- [Related Topic 1]
- [Related Topic 2]
- [Related Topic 3]

### Commands
```bash
# Store knowledge
postgres: "INSERT INTO knowledge (topic, content) VALUES ('[TOPIC_NAME]', '[CONTENT]')"

# Query knowledge
postgres: "SELECT * FROM knowledge WHERE topic LIKE '%[TOPIC_NAME]%'"

# Update knowledge
postgres: "UPDATE knowledge SET content = '[NEW_CONTENT]' WHERE topic = '[TOPIC_NAME]'"
```

### References
- [Reference 1]
- [Reference 2]
- [Reference 3]

### Last Updated
[Date]
"""
        
        # Web Research Template
        research_template = """# Web Research Template

## Research Topic: [TOPIC_NAME]

### Research Questions
1. [Question 1]
2. [Question 2]
3. [Question 3]

### Search Queries
```bash
# Primary search
brave-search: "[PRIMARY_SEARCH_TERM]"

# Related searches
brave-search: "[RELATED_SEARCH_1]"
brave-search: "[RELATED_SEARCH_2]"
brave-search: "[RELATED_SEARCH_3]"
```

### Key Findings
- Finding 1: [Description]
- Finding 2: [Description]
- Finding 3: [Description]

### Sources
- [Source 1]: [URL]
- [Source 2]: [URL]
- [Source 3]: [URL]

### Analysis
[Analysis of findings and their relevance]

### Next Steps
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

### Commands
```bash
# Store research findings
postgres: "INSERT INTO research (topic, findings, sources) VALUES ('[TOPIC_NAME]', '[FINDINGS]', '[SOURCES]')"

# Create sequential thinking plan
sequential-thinking: "Create plan based on research findings for [TOPIC_NAME]"
```

### Research Date
[Date]
"""
        
        # Write templates
        templates_dir = self.docs_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        template_files = {
            "sequential-thinking-template.md": sequential_template,
            "knowledge-template.md": knowledge_template,
            "research-template.md": research_template
        }
        
        for filename, content in template_files.items():
            template_file = templates_dir / filename
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created {template_file}")
        
        self.installation_results["documentation"]["templates"] = list(template_files.keys())
    
    def test_mcp_system(self) -> Dict:
        """Test the MCP system installation"""
        print("\n🧪 Testing MCP system...")
        
        test_results = {
            "python_tools": {},
            "node_tools": {},
            "configuration": {},
            "overall_status": "unknown"
        }
        
        # Test Python tools
        for tool in self.python_tools:
            try:
                result = subprocess.run([
                    sys.executable, "-m", tool, "--version"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"  ✅ {tool} - Working")
                    test_results["python_tools"][tool] = "working"
                else:
                    print(f"  ⚠️  {tool} - Installed but may have issues")
                    test_results["python_tools"][tool] = "warning"
                    
            except Exception as e:
                print(f"  ❌ {tool} - Error: {e}")
                test_results["python_tools"][tool] = "error"
        
        # Test Node.js tools
        for tool in self.node_tools:
            try:
                result = subprocess.run([
                    "npx", tool, "--version"
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"  ✅ {tool} - Working")
                    test_results["node_tools"][tool] = "working"
                else:
                    print(f"  ⚠️  {tool} - Installed but may have issues")
                    test_results["node_tools"][tool] = "warning"
                    
            except Exception as e:
                print(f"  ❌ {tool} - Error: {e}")
                test_results["node_tools"][tool] = "error"
        
        # Test configuration
        config_file = self.mcp_dir / "mcp.json"
        if config_file.exists():
            print(f"  ✅ MCP configuration - Found")
            test_results["configuration"]["mcp.json"] = "found"
        else:
            print(f"  ❌ MCP configuration - Missing")
            test_results["configuration"]["mcp.json"] = "missing"
        
        # Determine overall status
        all_tools = list(test_results["python_tools"].values()) + list(test_results["node_tools"].values())
        if all(status == "working" for status in all_tools):
            test_results["overall_status"] = "success"
        elif any(status == "error" for status in all_tools):
            test_results["overall_status"] = "error"
        else:
            test_results["overall_status"] = "warning"
        
        return test_results
    
    def create_installation_report(self) -> None:
        """Create comprehensive installation report"""
        print("\n📊 Creating installation report...")
        
        # Test the system
        test_results = self.test_mcp_system()
        
        # Generate report
        report = f"""# MCP System Installation Report

## Installation Summary

### Python MCP Tools
"""
        
        for tool, result in self.installation_results["python_tools"].items():
            status = result["status"]
            version = result.get("version", "Unknown")
            report += f"- **{tool}**: {status} (Version: {version})\n"
        
        report += "\n### Node.js MCP Tools\n"
        
        for tool, result in self.installation_results["node_tools"].items():
            status = result["status"]
            version = result.get("version", "Unknown")
            report += f"- **{tool}**: {status} (Version: {version})\n"
        
        report += f"""
### Configuration
- **MCP Config**: {self.installation_results["configuration"].get("mcp.json", {}).get("status", "unknown")}

### Documentation
- **Tools Reference**: {self.installation_results["documentation"].get("tools_reference", "Not created")}
- **Installation Guide**: {self.installation_results["documentation"].get("installation_guide", "Not created")}
- **Templates**: {len(self.installation_results["documentation"].get("templates", []))} created

## Test Results

### Overall Status: {test_results["overall_status"].upper()}

### Python Tools Test Results
"""
        
        for tool, status in test_results["python_tools"].items():
            report += f"- **{tool}**: {status}\n"
        
        report += "\n### Node.js Tools Test Results\n"
        
        for tool, status in test_results["node_tools"].items():
            report += f"- **{tool}**: {status}\n"
        
        report += f"""
### Configuration Test Results
"""
        
        for config, status in test_results["configuration"].items():
            report += f"- **{config}**: {status}\n"
        
        report += """
## Next Steps

1. **Configure Environment Variables**:
   ```bash
   export BRAVE_API_KEY="your_api_key"
   export GITHUB_TOKEN="your_github_token"
   export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/your_db"
   ```

2. **Test Individual Tools**:
   ```bash
   mcp-playwright --help
   npx @modelcontextprotocol/server-sequential-thinking --help
   ```

3. **Run Comprehensive Tests**:
   ```bash
   python .universal/test-system/test-universal-system.py
   ```

4. **Review Documentation**:
   - `.universal/docs/mcp/mcp-tools-reference.md`
   - `.universal/docs/mcp/installation-guide.md`

## Troubleshooting

If any tools failed to install or test:

1. **Python Tools**: Try `pip install tool-name --user --force-reinstall`
2. **Node.js Tools**: Try `npm install -g tool-name --force`
3. **Permission Issues**: Use `--user` flag for Python, `sudo` for npm (Linux/Mac)
4. **Network Issues**: Check internet connection and try again

## Support

For additional help:
1. Check the troubleshooting section in the tools reference
2. Review the installation guide
3. Run the test suite for detailed diagnostics
"""
        
        # Write report
        report_file = self.memory_dir / "main" / "mcp-installation-report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"  ✅ Created {report_file}")
        
        # Also save as JSON for programmatic access
        json_report = {
            "installation_results": self.installation_results,
            "test_results": test_results,
            "timestamp": str(Path().stat().st_mtime)
        }
        
        json_file = self.memory_dir / "main" / "mcp-installation-report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_report, f, indent=2)
        
        print(f"  ✅ Created {json_file}")
    
    def run_setup(self, manual: bool = False, test_only: bool = False) -> None:
        """Run the complete MCP system setup"""
        print("🚀 Universal MCP System Setup")
        print("=" * 50)
        
        if test_only:
            print("🧪 Running MCP system tests only...")
            test_results = self.test_mcp_system()
            self.create_installation_report()
            return
        
        # Setup directory structure
        self.setup_directory_structure()
        
        if not manual:
            # Automated installation
            self.install_python_mcp_tools()
            self.install_node_mcp_tools()
        else:
            print("\n📋 Manual installation mode - skipping tool installation")
            print("Please install tools manually using the commands in the documentation")
        
        # Create configuration and documentation
        self.create_mcp_configuration()
        self.create_mcp_documentation()
        self.create_mcp_templates()
        
        # Create installation report
        self.create_installation_report()
        
        print("\n" + "=" * 50)
        print("✅ MCP System Setup Complete!")
        print("=" * 50)
        print("\n📚 Documentation created:")
        print(f"  - {self.docs_dir}/mcp/mcp-tools-reference.md")
        print(f"  - {self.docs_dir}/mcp/installation-guide.md")
        print(f"  - {self.memory_dir}/main/mcp-installation-report.md")
        print("\n🎯 Next steps:")
        print("  1. Configure environment variables")
        print("  2. Test individual tools")
        print("  3. Run comprehensive test suite")
        print("  4. Start using MCP tools in your workflow")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal MCP System Setup")
    parser.add_argument("--manual", action="store_true", help="Manual installation mode")
    parser.add_argument("--test", action="store_true", help="Test only mode")
    
    args = parser.parse_args()
    
    setup = MCPSystemSetup()
    setup.run_setup(manual=args.manual, test_only=args.test)

if __name__ == "__main__":
    main() 