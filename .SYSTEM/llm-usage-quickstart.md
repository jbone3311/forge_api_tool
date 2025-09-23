# LLM/AI Usage Quickstart for MCP System

## 🚀 Getting Started

1. **Install MCP tools**
   ```bash
   python .SYSTEM/setup-mcp-tools.py
   ```
2. **Copy and fill out your `.env` file**
   ```bash
   cp .SYSTEM/env-sample.txt .env
   # Edit .env and add your API keys
   ```
3. **Start Cursor.ai** (or Claude Desktop)
4. **Use LLM commands** (see below) to manage context, docs, planning, and more
5. **(Optional) See .SYSTEM/cursor-setup-guide.md for full onboarding**

---

## 🧠 **Useful LLM/AI Commands**

| Command Example | What it Does |
|-----------------|--------------|
| `memory-bank: "Store this: Working on API auth"` | Store project context |
| `memory-bank: "What was I working on last?"` | Retrieve last context |
| `package-docs: "Get documentation for FastAPI"` | Fetch package docs |
| `package-docs: "Show me React state management"` | Search docs |
| `sequential-thinking: "Create a 5-step plan for user login"` | Plan a workflow |
| `sequential-thinking: "Generate code for step 1"` | Execute a plan step |
| `brave-search: "Latest Python security best practices"` | Web search |
| `github: "Get the README for this repo"` | Fetch GitHub docs |
| `postgres: "SELECT * FROM users"` | Query your database (if configured) |

---

## 🛠️ **Regular Steps for a New Project or Session**

1. **Install MCP tools** (if not already):
   ```bash
   python .SYSTEM/setup-mcp-tools.py
   ```
2. **Copy and fill out your `.env` file**:
   ```bash
   cp .SYSTEM/env-sample.txt .env
   # Edit .env and add your API keys
   ```
3. **Start Cursor.ai** (or Claude Desktop).
4. **Use LLM commands** (see table above) to:
   - Store/retrieve project context
   - Fetch documentation
   - Plan and execute tasks
   - Search the web
   - Query your database
   - Access GitHub info
5. **(Optional) Use .SYSTEM/cursor-setup-guide.md** for detailed onboarding and troubleshooting.

---

## 💡 **Tips for Effective Use**

- **Always start your session by recalling project context:**  
  `memory-bank: "What was I working on last?"`
- **Document decisions and progress as you go:**  
  `memory-bank: "Record: Finished implementing user login"`
- **Break down complex tasks:**  
  `sequential-thinking: "Create a 5-step plan for adding OAuth"`
- **Fetch docs and code examples as needed:**  
  `package-docs: "Show me FastAPI middleware examples"`
- **Use web search for up-to-date info:**  
  `brave-search: "Compare FastAPI vs Flask performance"`
- **Query your database or GitHub as needed:**  
  `postgres: "SELECT * FROM migrations"`  
  `github: "List open issues"`

---

## 📚 **See Also**
- .SYSTEM/cursor-setup-guide.md — Full setup and troubleshooting
- .SYSTEM/env-sample.txt — Environment variable template
- .PROJECT-SPECIFIC/mcp.json — Cursor MCP configuration 

---

## 🪟 Windows: Create PostgreSQL User & Database for MCP

### 1. **Copy the script below into a file named**  
`create_mcp_db.bat`  
(You can do this in Notepad: paste, then Save As, set “Save as type” to “All Files”, and name it `create_mcp_db.bat`)

```bat
@echo off
REM This script creates a PostgreSQL user and database for MCP tools.
REM You will be prompted for the postgres (admin) password.

set /p PGPASSWORD="Enter your postgres admin password: "

REM Change these if you want a different user/password/db name
set MCPUSER=mcpuser
set MCPPASS=mcppassword123
set MCPDB=mcp_db

REM Run the SQL commands
echo Creating user and database...
psql -U postgres -h localhost -p 5432 -c "CREATE USER %MCPUSER% WITH PASSWORD '%MCPPASS%';"
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE %MCPDB% OWNER %MCPUSER%;"
psql -U postgres -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE %MCPDB% TO %MCPUSER%;"

echo.
echo Done! Add this to your .env file:
echo DATABASE_URL=postgresql://%MCPUSER%:%MCPPASS%@localhost:5432/%MCPDB%
pause
``` 