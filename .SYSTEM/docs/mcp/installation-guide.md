# MCP System Installation Guide

## Quick Installation

```bash
# Run the automated setup
python .SYSTEM/setup-mcp-system.py

# Or install manually
python .SYSTEM/setup-mcp-system.py --manual
```

## Manual Installation Steps

### 1. Install Node.js MCP Tools
```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
npm install -g @executeautomation/playwright-mcp-server
```

### 2. Verify Installation
```bash
npx @modelcontextprotocol/server-sequential-thinking --version
npx @modelcontextprotocol/server-postgres --version
npx @executeautomation/playwright-mcp-server --version
```

### 3. Configure Environment
```bash
# Set up environment variables
export BRAVE_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
export POSTGRES_CONNECTION_STRING="postgresql://localhost:5432/your_db"
```

## Testing

### Quick Test
```bash
python .SYSTEM/setup-mcp-system.py --test
```

### Comprehensive Test
```bash
python .SYSTEM/test-system/test-universal-system.py
```

## Troubleshooting

See the troubleshooting section in `mcp-tools-reference.md` for common issues and solutions.
