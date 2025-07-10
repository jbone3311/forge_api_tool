# MCP System Setup Template

## Overview
This template provides a step-by-step guide for setting up the Model Context Protocol (MCP) system in your Universal AI Development Environment.

## Prerequisites
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git repository initialized
- [ ] Universal AI Development System installed

## Step 1: Directory Structure Setup
- [ ] Create `.universal/mcp/` directory
- [ ] Create `.universal/memory/main/` directory
- [ ] Create `.universal/memory/tasks/` directory
- [ ] Create `.universal/memory/docs-cache/` directory
- [ ] Create `.universal/docs/mcp/` directory
- [ ] Create `.universal/docs/templates/` directory

**Commands:**
```bash
mkdir -p .universal/mcp
mkdir -p .universal/memory/main
mkdir -p .universal/memory/tasks
mkdir -p .universal/memory/docs-cache
mkdir -p .universal/docs/mcp
mkdir -p .universal/docs/templates
```

## Step 2: Install Python MCP Tools
- [ ] Install mcp-playwright
- [ ] Install mcp (core framework)
- [ ] Verify installations

**Commands:**
```bash
pip install mcp-playwright mcp --user
mcp-playwright --version
mcp --version
```

## Step 3: Install Node.js MCP Tools
- [ ] Install @modelcontextprotocol/server-sequential-thinking
- [ ] Install @modelcontextprotocol/server-postgres
- [ ] Install @modelcontextprotocol/server-brave-search
- [ ] Install @modelcontextprotocol/server-github
- [ ] Verify installations

**Commands:**
```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github

npx @modelcontextprotocol/server-sequential-thinking --version
npx @modelcontextprotocol/server-postgres --version
```

## Step 4: Create MCP Configuration
- [ ] Create `.universal/mcp/mcp.json` file
- [ ] Configure playwright server
- [ ] Configure sequential-thinking server
- [ ] Configure postgres server
- [ ] Configure brave-search server
- [ ] Configure github server

**Configuration:**
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

## Step 5: Set Environment Variables
- [ ] Set BRAVE_API_KEY
- [ ] Set GITHUB_TOKEN
- [ ] Set POSTGRES_CONNECTION_STRING
- [ ] Add to shell profile

**Commands:**
```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export BRAVE_API_KEY="your_brave_api_key"
export GITHUB_TOKEN="your_github_token"
export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/your_database"
```

## Step 6: Create Documentation
- [ ] Create MCP tools reference
- [ ] Create installation guide
- [ ] Create usage examples
- [ ] Create troubleshooting guide

**Files to create:**
- `.universal/docs/mcp/mcp-tools-reference.md`
- `.universal/docs/mcp/installation-guide.md`
- `.universal/docs/mcp/usage-examples.md`
- `.universal/docs/mcp/troubleshooting.md`

## Step 7: Create Templates
- [ ] Create sequential thinking template
- [ ] Create knowledge storage template
- [ ] Create research template
- [ ] Create debugging template

**Files to create:**
- `.universal/docs/templates/sequential-thinking-template.md`
- `.universal/docs/templates/knowledge-template.md`
- `.universal/docs/templates/research-template.md`
- `.universal/docs/templates/debugging-template.md`

## Step 8: Update Project Files
- [ ] Update requirements.txt
- [ ] Update setup scripts
- [ ] Update test system
- [ ] Update documentation

**Files to update:**
- `requirements.txt` - Add MCP tools
- `setup-mcp-tools.py` - Update with real tools
- `.universal/test-system/test-universal-system.py` - Update tests
- `QUICK_START.md` - Update commands

## Step 9: Test Installation
- [ ] Run MCP system tests
- [ ] Test individual tools
- [ ] Test configuration
- [ ] Verify documentation

**Commands:**
```bash
# Run automated setup and test
python .universal/setup-mcp-system.py

# Test individual tools
mcp-playwright --help
npx @modelcontextprotocol/server-sequential-thinking --help

# Run comprehensive tests
python .universal/test-system/test-universal-system.py
```

## Step 10: Integration Testing
- [ ] Test sequential thinking workflow
- [ ] Test database operations
- [ ] Test web search functionality
- [ ] Test GitHub integration
- [ ] Test browser automation

**Test Commands:**
```bash
# Sequential thinking
sequential-thinking: "Create 3-step plan for testing MCP system"

# Database operations
postgres: "SELECT version()"

# Web search
brave-search: "MCP protocol documentation"

# GitHub integration
github: "get repository info"

# Browser automation
playwright: "Take screenshot of https://example.com"
```

## Verification Checklist
- [ ] All Python MCP tools installed and working
- [ ] All Node.js MCP tools installed and working
- [ ] MCP configuration file created and valid
- [ ] Environment variables set correctly
- [ ] Documentation created and accessible
- [ ] Templates created and usable
- [ ] Test suite passes
- [ ] Integration tests successful

## Troubleshooting

### Common Issues

**Python tools not found**
```bash
# Solution: Reinstall with --user flag
pip install mcp-playwright mcp --user --force-reinstall
```

**Node.js tools not found**
```bash
# Solution: Reinstall globally
npm install -g @modelcontextprotocol/server-sequential-thinking --force
```

**Permission errors**
```bash
# Python: Use --user flag
pip install mcp-playwright --user

# Node.js: Use sudo (Linux/Mac)
sudo npm install -g @modelcontextprotocol/server-sequential-thinking
```

**Configuration errors**
```bash
# Check MCP config syntax
cat .universal/mcp/mcp.json | python -m json.tool

# Validate configuration
python .universal/setup-mcp-system.py --test
```

## Success Criteria
- [ ] All MCP tools respond to --help command
- [ ] MCP configuration loads without errors
- [ ] Test suite reports all tools as "working"
- [ ] Documentation is complete and accurate
- [ ] Templates are functional and useful
- [ ] Environment variables are properly set
- [ ] Integration tests pass successfully

## Next Steps
1. **Configure API keys** for external services
2. **Set up database** for knowledge storage
3. **Test workflows** with real projects
4. **Document lessons learned** in project memory
5. **Share templates** with team members

## Support Resources
- MCP Tools Reference: `.universal/docs/mcp/mcp-tools-reference.md`
- Installation Guide: `.universal/docs/mcp/installation-guide.md`
- Troubleshooting: `.universal/docs/mcp/troubleshooting.md`
- Test Suite: `python .universal/test-system/test-universal-system.py`

---

**Template Version:** 1.0  
**Last Updated:** [Current Date]  
**Compatible with:** Universal AI Development System v2.0+ 