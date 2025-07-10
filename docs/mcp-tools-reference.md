# MCP Tools Reference

This document provides a comprehensive reference for all MCP (Model Context Protocol) tools used in the Forge-API-Tool project, based on verified tools from the [awesome-mcp-servers](https://github.com/appcypher/awesome-mcp-servers) list.

## Overview

MCP (Model Context Protocol) enables AI models to securely interact with local and remote resources through standardized server implementations. This reference covers tools specifically selected for AI development workflows.

## Core MCP Tools

### Python MCP Tools

#### mcp-playwright
**Purpose**: Browser automation and testing
**Installation**: `pip install mcp-playwright --user`
**Usage**: `mcp-playwright --help`
**Features**:
- Web scraping and automation
- Browser testing
- Screenshot capture
- Form filling and interaction

#### mcp (Core Framework)
**Purpose**: Core MCP framework and CLI tools
**Installation**: `pip install mcp --user`
**Usage**: `mcp --help`
**Features**:
- MCP server management
- Protocol utilities
- Development tools

### Node.js MCP Tools

#### mcp-memory-bank
**Purpose**: Project memory and context management
**Installation**: `npm install -g mcp-memory-bank`
**Usage**: `npx mcp-memory-bank --help`
**Features**:
- Store and retrieve project context
- Memory persistence across sessions
- Context-aware AI assistance

#### mcp-knowledge-graph
**Purpose**: Code dependency analysis and relationships
**Installation**: `npm install -g mcp-knowledge-graph`
**Usage**: `npx mcp-knowledge-graph --help`
**Features**:
- Analyze code dependencies
- Visualize relationships
- Track code changes

#### @YassineTk/mcp-docs-provider
**Purpose**: Documentation management and generation
**Installation**: `npm install -g @YassineTk/mcp-docs-provider`
**Usage**: `npx @YassineTk/mcp-docs-provider --help`
**Features**:
- Auto-generate documentation
- Maintain doc consistency
- Version control integration

#### @modelcontextprotocol/server-sequential-thinking
**Purpose**: Complex task planning and execution
**Installation**: `npm install -g @modelcontextprotocol/server-sequential-thinking`
**Usage**: `npx @modelcontextprotocol/server-sequential-thinking --help`
**Features**:
- Break down complex tasks
- Sequential execution planning
- Progress tracking

## Database & API Integration

#### @modelcontextprotocol/server-postgres
**Purpose**: PostgreSQL database integration
**Installation**: `npm install -g @modelcontextprotocol/server-postgres`
**Configuration**: Requires connection string
**Features**:
- Database queries
- Schema analysis
- Data manipulation

#### @modelcontextprotocol/server-brave-search
**Purpose**: Web search capabilities
**Installation**: `npm install -g @modelcontextprotocol/server-brave-search`
**Configuration**: Requires BRAVE_API_KEY
**Features**:
- Web search
- Real-time information
- Research assistance

#### @modelcontextprotocol/server-github
**Purpose**: GitHub integration
**Installation**: `npm install -g @modelcontextprotocol/server-github`
**Configuration**: Requires GITHUB_TOKEN
**Features**:
- Repository management
- Issue tracking
- Code review assistance

## Installation Commands

### Quick Installation
```bash
# Install Python MCP tools
pip install mcp-playwright mcp --user

# Install Node.js MCP tools
npm install -g mcp-memory-bank mcp-knowledge-graph @YassineTk/mcp-docs-provider @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-postgres @modelcontextprotocol/server-brave-search @modelcontextprotocol/server-github
```

### Using the Setup Script
```bash
# Install all tools
python setup-mcp-tools.py

# Test installation
python setup-mcp-tools.py --test
```

## Configuration

### Environment Variables
Set these environment variables for full functionality:

```bash
# Brave Search API
export BRAVE_API_KEY="your_brave_api_key"

# GitHub Integration
export GITHUB_TOKEN="your_github_token"

# PostgreSQL (if using)
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
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
    "memory-bank": {
      "command": "npx",
      "args": ["-y", "mcp-memory-bank"]
    },
    "knowledge-graph": {
      "command": "npx",
      "args": ["-y", "mcp-knowledge-graph"]
    },
    "docs-provider": {
      "command": "npx",
      "args": ["-y", "@YassineTk/mcp-docs-provider"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

## Usage Examples

### Memory Management
```python
# Store project context
memory_bank.store("project_context", {
    "current_feature": "user_authentication",
    "dependencies": ["flask", "sqlalchemy"],
    "next_steps": ["implement_login", "add_password_reset"]
})

# Retrieve context
context = memory_bank.retrieve("project_context")
```

### Knowledge Graph Analysis
```python
# Analyze code dependencies
dependencies = knowledge_graph.analyze_dependencies("src/")
relationships = knowledge_graph.get_relationships("UserService")
```

### Documentation Generation
```python
# Generate API documentation
docs_provider.generate_api_docs("src/api/", "docs/api/")

# Update README
docs_provider.update_readme("README.md", project_info)
```

### Sequential Task Planning
```python
# Plan complex refactoring
plan = sequential_thinking.plan_task("Refactor authentication system", [
    "Analyze current implementation",
    "Design new architecture", 
    "Implement changes",
    "Update tests",
    "Deploy and monitor"
])
```

## Troubleshooting

### Common Issues

1. **MCP tools not found**
   - Ensure tools are installed globally: `npm install -g <tool-name>`
   - Check PATH environment variable
   - Restart your IDE/terminal

2. **Permission errors**
   - Use `--user` flag for pip installations
   - Run npm install with appropriate permissions
   - Check file system permissions

3. **API key errors**
   - Verify environment variables are set
   - Check API key validity
   - Ensure proper permissions

### Testing Installation
```bash
# Test Python tools
python -m mcp-playwright --version
python -m mcp --version

# Test Node.js tools
npx mcp-memory-bank --help
npx mcp-knowledge-graph --help
npx @YassineTk/mcp-docs-provider --help
```

## Additional Resources

- [Awesome MCP Servers](https://github.com/appcypher/awesome-mcp-servers) - Complete list of MCP tools
- [MCP Protocol Documentation](https://modelcontextprotocol.io/) - Official protocol docs
- [Claude Desktop MCP Guide](https://modelcontextprotocol.io/quickstart) - Setup guide
- [Cursor MCP Documentation](https://docs.cursor.com/advanced/model-context-protocol) - Cursor integration

## Contributing

When adding new MCP tools:
1. Verify the tool exists and is maintained
2. Test installation and functionality
3. Update this reference document
4. Add to the setup script
5. Update MCP configuration

## Version History

- **v1.0**: Initial setup with core tools
- **v1.1**: Added verified tools from awesome-mcp-servers
- **v1.2**: Comprehensive documentation and testing 