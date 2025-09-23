# Cursor.ai MCP Setup Guide

## 🚀 Quick Setup

Your MCP system is now ready for Cursor.ai! Follow these steps to get everything working.

## 📋 Prerequisites

✅ **Already Done:**
- MCP tools installed
- Cursor.ai MCP configuration created
- Environment variables template ready

## 🔧 Step 1: Configure Cursor.ai

### 1.1 Open Cursor.ai Settings
1. Open Cursor.ai
2. Go to **Settings** (Ctrl/Cmd + ,)
3. Search for "MCP" or "Model Context Protocol"

### 1.2 Add MCP Configuration
The MCP configuration is already created at `.cursor/mcp.json`. Cursor.ai should automatically detect this file.

If not, manually add the MCP configuration in Cursor.ai settings:

```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "npx",
      "args": ["-y", "mcp-memory-bank"]
    },
    "knowledge-graph": {
      "command": "npx",
      "args": ["-y", "mcp-knowledge-graph"]
    },
    "package-docs": {
      "command": "npx",
      "args": ["-y", "mcp-package-docs"],
      "env": {
        "ENABLE_LSP": "true"
      }
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-brave-search",
        "--api-key",
        "${BRAVE_API_KEY}"
      ]
    },
    "github": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-github",
        "--token",
        "${GITHUB_TOKEN}"
      ]
    }
  }
}
```

## 🔑 Step 2: Set Up Environment Variables

### 2.1 Create .env File
Copy the sample environment file:
```bash
cp .SYSTEM/env-sample.txt .env
```

### 2.2 Get API Keys

#### Brave Search API Key (Optional but Recommended)
1. Go to https://serper.dev/
2. Sign up for a free account
3. Get your API key
4. Add to `.env`:
   ```
   BRAVE_API_KEY=your_actual_key_here
   ```

#### GitHub Token (Optional but Recommended)
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the token
5. Add to `.env`:
   ```
   GITHUB_TOKEN=your_actual_token_here
   ```

#### PostgreSQL Database (Optional)
If you want database integration:
1. Install PostgreSQL locally or use a cloud service
2. Create a database
3. Add to `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/your_database
   ```

## 🧪 Step 3: Test the Setup

### 3.1 Test MCP Tools
Run the test script:
```bash
python .SYSTEM/setup-mcp-tools.py --test
```

### 3.2 Test in Cursor.ai
1. Restart Cursor.ai
2. Open a chat with Claude
3. Try these commands:

#### Test Memory Bank:
```
memory-bank: "Store this project context: Working on a Python API with FastAPI"
```

#### Test Package Docs:
```
package-docs: "Get documentation for FastAPI authentication"
```

#### Test Sequential Thinking:
```
sequential-thinking: "Create a 5-step plan for implementing user authentication"
```

## 🎯 Step 4: Usage Examples

### Memory Management
```bash
# Store project context
memory-bank: "Current task: Implementing user authentication with JWT tokens"

# Retrieve context
memory-bank: "What was I working on last session?"
```

### Documentation Access
```bash
# Get package documentation
package-docs: "Show me FastAPI middleware examples"

# Search specific topics
package-docs: "Find React state management patterns"
```

### Task Planning
```bash
# Create a plan
sequential-thinking: "Plan the implementation of a REST API with authentication"

# Execute steps
sequential-thinking: "Generate code for step 1: database schema design"
```

### Web Search
```bash
# Search for current information
brave-search: "Latest React 18 features and best practices"
```

### GitHub Integration
```bash
# Access repository information
github: "Get the README for my current project"
```

## 🔧 Troubleshooting

### MCP Tools Not Working
1. Check if tools are installed:
   ```bash
   python .SYSTEM/setup-mcp-tools.py --test
   ```