# Universal AI Development System - Installation Guide

## 🎯 Overview

This guide provides step-by-step instructions for installing and setting up the Universal AI Development System in any new project. The system provides AI-native development capabilities with memory-first workflows, dependency analysis, and automated testing.

---

## 📋 Prerequisites

### Required Software
```bash
# Core requirements
- Python 3.8 or higher
- Node.js 16 or higher (for MCP tools)
- Git
- Cursor IDE (recommended) or VS Code

# Verify installations
python --version
node --version
git --version
```

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space for tools and dependencies
- **Network**: Internet connection for tool installation

---

## 🚀 Installation Steps

### Step 1: Install MCP Tools

```bash
# Install MCP tools globally (Real tools that exist)
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github

# Install Python MCP tools
pip install mcp-playwright mcp --user

# Verify installations
npx @modelcontextprotocol/server-sequential-thinking --version
npx @modelcontextprotocol/server-postgres --version
mcp-playwright --version
mcp --version
```

**Expected Output:**
```
Sequential Thinking MCP Server running on stdio
PostgreSQL MCP Server running on stdio
mcp-playwright version 0.1.1
mcp version 1.10.1
```

### Step 2: Copy Universal System

```bash
# Create .universal directory
mkdir .universal

# Copy universal system files
# (Copy from existing project or download from repository)
```

**Directory Structure:**
```
.universal/
├── rules/                    # Cursor AI rules
├── templates/                # Universal templates
├── mcp/                     # MCP configurations
├── memory/                  # Project memory
├── extensions/              # Future extensions
├── hooks/                   # Git hooks
└── test-system/            # Testing framework
```

### Step 3: Set Up Cursor Rules

```bash
# Create .cursor directory
mkdir .cursor
mkdir .cursor/rules

# Copy Cursor rules
# (Copy from .universal/rules/ to .cursor/rules/)
```

**Required Rules:**
- `10-memory.mdc` - Memory-first development
- `30-docs.mdc` - Documentation automation
- `40-graphs.mdc` - Dependency analysis
- `branch.mdc` - Branch context switching
- `refactor-rule.mdc` - AI-assisted refactoring

### Step 4: Configure MCP

```bash
# Update MCP configuration
# Edit .universal/mcp/mcp.json with correct paths
```

**MCP Configuration:**
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

### Step 5: Initialize Memory System

```bash
# Create initial memory structure
mkdir -p .universal/memory/main
mkdir -p .universal/memory/tasks
mkdir -p .universal/memory/docs-cache

# Create initial progress file
touch .universal/memory/main/progress.md
```

**Initial Progress Content:**
```markdown
# Project Progress

## Current State
- Universal AI Development System installed
- MCP tools configured
- Memory system initialized

## Recent Decisions
- Installed Universal AI Development System
- Configured MCP tools for AI-native development
- Set up memory-first workflow

## Next Steps
- Test system functionality
- Begin first feature development
- Document project-specific requirements
```

### Step 6: Set Up Git Hooks

```bash
# Make pre-commit hook executable
chmod +x .universal/hooks/pre-commit

# Install pre-commit hook
cp .universal/hooks/pre-commit .git/hooks/
```

### Step 7: Test Installation

```bash
# Run comprehensive test suite
python .universal/test-system/test-universal-system.py

# Run quick test
python test-universal-system.py
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export UNIVERSAL_PROJECT_ROOT="$(pwd)"
export UNIVERSAL_MEMORY_DIR=".universal/memory"
export UNIVERSAL_TEMPLATES_DIR=".universal/templates"
```

### Cursor IDE Configuration

```json
// .vscode/settings.json (if using VS Code)
{
  "mcp.servers": {
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

### Python Dependencies

```bash
# Install Python dependencies
pip install pytest pytest-cov

# Create requirements.txt
echo "pytest>=7.0.0" > requirements.txt
echo "pytest-cov>=4.0.0" >> requirements.txt
```

---

## 🧪 Verification

### Test MCP Tools

```bash
# Test memory bank
memory-bank: list_projects

# Test knowledge graph
knowledge-graph: "Show all files in the project"

# Test docs provider
docs-provider: "Generate a summary of the universal system"

# Test sequential thinking
sequential-thinking: "Create a 3-step plan for testing the system"
```

### Test Cursor Rules

```bash
# Verify rules are loaded
# Check Cursor IDE shows AI suggestions based on rules

# Test memory-first workflow
# Try: "Check project memory before making changes"
```

### Test Git Hooks

```bash
# Make a test commit
echo "Test commit" > test.txt
git add test.txt
git commit -m "Test commit"

# Verify progress.md was updated
cat .universal/memory/main/progress.md
```

---

## 🚀 Quick Start

### First Feature Development

```bash
# 1. Check project context
memory-bank: get_file_content project="main" path="progress.md"

# 2. Create feature branch
git checkout -b feature/first-feature

# 3. Plan implementation
sequential-thinking: "Create 4-step plan for [your feature]"

# 4. Analyze dependencies
knowledge-graph: "Show all files that will be affected by [feature]"

# 5. Generate code
sequential-thinking: "Generate code for step 1: [description]"

# 6. Generate tests
sequential-thinking: "Generate pytest test cases for [component]"

# 7. Update documentation
docs-provider: "Generate documentation for [feature]"

# 8. Document decisions
memory-bank: "Record implementation decision for [feature]"

# 9. Commit changes
git add .
git commit -m "Add [feature] with AI assistance"
```

---

## 🔧 Troubleshooting

### Common Issues

#### MCP Tools Not Found
```bash
# Error: Command not found: mcp-playwright
# Solution: Install Python MCP tools
pip install mcp-playwright mcp --user

# Error: Command not found: @modelcontextprotocol/server-sequential-thinking
# Solution: Install Node.js MCP tools
npm install -g @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-postgres @modelcontextprotocol/server-brave-search @modelcontextprotocol/server-github
```

#### Cursor Rules Not Working
```bash
# Error: AI not following rules
# Solution: Restart Cursor IDE
# Verify rules are in .cursor/rules/ directory
# Check rule syntax is correct
```

#### Memory Not Updating
```bash
# Error: Memory bank not responding
# Solution: Check file permissions
chmod -R 755 .universal/memory/
# Verify MCP configuration paths are correct
```

#### Tests Failing
```bash
# Error: Test suite failures
# Solution: Run diagnostic test
python debug-test.py
# Check Python dependencies
pip install -r requirements.txt
```

### Debug Commands

```bash
# Check system status
python .universal/test-system/test-universal-system.py --verbose

# Test individual components
python -c "import sys; print('Python:', sys.version)"
node --version
git --version

# Check MCP tool status
mcp-memory-bank --help
mcp-knowledge-graph --help
mcp-docs-provider --help
mcp-sequential-thinking --help
```

---

## 📚 Next Steps

### Learning Resources

1. **Complete Guide**: Read `UNIVERSAL_SYSTEM_COMPLETE_GUIDE.md`
2. **Quick Reference**: Use `UNIVERSAL_SYSTEM_QUICK_REFERENCE.md`
3. **Live Demo**: Follow `UNIVERSAL_SYSTEM_DEMO.md`
4. **Templates**: Explore `.universal/templates/`

### Advanced Setup

```bash
# Customize templates for your project
cp .universal/templates/ai-development-workflow.md .universal/templates/custom-workflow.md

# Add project-specific rules
cp .cursor/rules/10-memory.mdc .cursor/rules/50-project-specific.mdc

# Configure additional MCP tools
# Add to .universal/mcp/mcp.json
```

### Integration with Existing Projects

```bash
# For existing projects, run setup script
python .universal/setup-new-project.py

# This will:
# - Initialize memory system
# - Set up Git hooks
# - Configure MCP tools
# - Create initial documentation
```

---

## 🎉 Success Indicators

### Installation Complete When:

- [ ] MCP tools respond to commands
- [ ] Cursor IDE shows AI suggestions based on rules
- [ ] Test suite passes all checks
- [ ] Git hooks update progress.md on commits
- [ ] Memory bank can store and retrieve information
- [ ] Knowledge graph can analyze project structure
- [ ] Sequential thinking can create plans
- [ ] Docs provider can generate documentation

### Ready for Development When:

- [ ] You can start a new feature with memory-first workflow
- [ ] AI can generate code, tests, and documentation
- [ ] Dependencies are automatically analyzed
- [ ] Decisions are automatically documented
- [ ] Quality assurance is automated
- [ ] System provides full audit trail

---

## 🆘 Getting Help

### Documentation
- **Complete Guide**: `UNIVERSAL_SYSTEM_COMPLETE_GUIDE.md`
- **Quick Reference**: `UNIVERSAL_SYSTEM_QUICK_REFERENCE.md`
- **Live Demo**: `UNIVERSAL_SYSTEM_DEMO.md`

### Support
- Check troubleshooting section above
- Run diagnostic tests: `python debug-test.py`
- Review test results for specific issues
- Check memory bank for similar problems

### Community
- Share experiences and improvements
- Contribute templates and rules
- Report issues and suggest enhancements

---

**🎯 Your Universal AI Development System is now ready for AI-native development!**

*Start with the Quick Reference guide and work through the Live Demo to experience the full power of AI-enhanced development.* 