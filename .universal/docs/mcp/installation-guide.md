# MCP System Installation Guide

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
