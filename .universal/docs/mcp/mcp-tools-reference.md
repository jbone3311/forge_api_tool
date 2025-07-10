# MCP Tools Reference

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
