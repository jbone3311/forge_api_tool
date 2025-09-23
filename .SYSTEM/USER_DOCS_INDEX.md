# SYSTEM User Documentation Index

## Getting Started
- [Quickstart Guide](llm-usage-quickstart.md)
- [Cursor Setup Guide](cursor-setup-guide.md)
- [Project Onboarding](templates/project-onboarding.md)
- [AI Development Workflow](templates/ai-development-workflow.md)

## System Setup & Tools
- [Environment Variables Sample](env-sample.txt)
- [MCP Setup Template](templates/mcp-setup-template.md)
- [Documentation Template](templates/documentation-template.md)
- [AI-Assisted Refactoring](templates/ai-assisted-refactoring.md)
- [AI-Enhanced Testing](templates/ai-enhanced-testing.md)

## Advanced Usage
- [Research Template](docs/templates/research-template.md)
- [Knowledge Template](docs/templates/knowledge-template.md)
- [Sequential Thinking Template](docs/templates/sequential-thinking-template.md)
- [MCP Tools Reference](docs/mcp/mcp-tools-reference.md)
- [Installation Guide](docs/mcp/installation-guide.md)

## Cheatsheets & Best Practices
- [Recommended Daily Process & Habits](templates/ai-development-workflow.md)
- [Code Cheatsheets](templates/documentation-template.md)
- [Refactoring Plan](templates/ai-assisted-refactoring.md)

## Scripts
- `setup-mcp-tools.py` — Install and verify MCP tools
- `setup-mcp-system.py` — System setup
- `setup-new-project.py` — Start a new project
- `verify-mcp-functionality.py` — Test MCP system
- `test-mcp-system.py` — Run system tests

---

## Instructions for Starting a New Project

1. **Copy `.SYSTEM` to your new project directory.**
2. **Run the setup script:**
   ```sh
   python .SYSTEM/setup-new-project.py
   ```
3. **Configure your environment:**
   - Copy `.SYSTEM/env-sample.txt` to `.env` and fill in your values.
4. **Initialize the database:**
   - Follow the steps in `.SYSTEM/docs/mcp/installation-guide.md` for database setup and loading.
5. **Review onboarding and workflow docs:**
   - `.SYSTEM/templates/project-onboarding.md`
   - `.SYSTEM/templates/ai-development-workflow.md`
6. **Check the cheatsheets and best practices in the index above.**

---

For more details, see the individual documentation files linked above. If you have questions or need to extend the system, start with the onboarding and workflow guides. 