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
cp .universal/env-sample.txt .env
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
python .universal/setup-mcp-tools.py --test
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
   python .universal/setup-mcp-tools.py --test
   ```

2. Restart Cursor.ai after configuration changes

3. Check Cursor.ai logs for MCP errors

### Environment Variables Not Working
1. Ensure `.env` file is in project root
2. Restart Cursor.ai after adding environment variables
3. Check that API keys are valid

### Specific Tool Issues
- **Memory Bank**: Should work without API keys
- **Package Docs**: Should work without API keys
- **Brave Search**: Requires `BRAVE_API_KEY`
- **GitHub**: Requires `GITHUB_TOKEN`
- **PostgreSQL**: Requires `DATABASE_URL`

## 📚 Available Tools

| Tool | Purpose | Requires API Key |
|------|---------|------------------|
| memory-bank | Store/retrieve project context | No |
| knowledge-graph | Analyze code dependencies | No |
| package-docs | Access documentation | No |
| sequential-thinking | Plan complex tasks | No |
| brave-search | Web search | Yes (BRAVE_API_KEY) |
| github | GitHub integration | Yes (GITHUB_TOKEN) |
| postgres | Database queries | Yes (DATABASE_URL) |
| playwright | Browser automation | No |

## 🎉 Success!

Once configured, you'll have:
- ✅ **Persistent project memory** across sessions
- ✅ **Documentation access** for any package
- ✅ **Task planning** with step-by-step execution
- ✅ **Web search** for current information
- ✅ **GitHub integration** for repository management
- ✅ **Database queries** for project data

Your AI development workflow is now significantly enhanced! 🚀 