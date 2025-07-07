# LLM Setup Instructions for Universal AI Development System

## 🎯 Overview
This document provides step-by-step instructions for setting up the Universal AI Development System in any new project. The system provides AI-enhanced development with MCP tools, memory management, and automated workflows.

## 📋 Setup Instructions

### 1. **Copy Universal System**
```bash
# Copy the entire .universal directory to your new project
cp -r .universal/ /path/to/your/new/project/
```

**Key Rule:** Universal templates in `.universal/` are for copying to new projects. Only update `docs/project-specific/` for the current project.

### 2. **Set Up the Complete Documentation Structure**

#### Step 1: Create Directory Structure
```bash
mkdir -p .universal/templates
mkdir -p .universal/rules
mkdir -p docs/project-specific
mkdir -p .cursor/rules
mkdir -p .universal/memory/main
mkdir -p .universal/memory/tasks
mkdir -p .universal/memory/docs-cache
mkdir -p .universal/mcp
mkdir -p .universal/extensions
```

#### Step 2: Copy Essential Templates
Copy these templates to `.universal/templates/`:
- `.universal/templates/ai-enhanced-testing.md`
- `.universal/templates/security-checklist.md`
- `.universal/templates/project-onboarding.md`
- `.universal/templates/ci-cd-pipeline.md`
- `.universal/templates/printable-quick-sheet.md`

#### Step 3: Copy Cursor Rules
Copy these rules to `.cursor/rules/`:
- `.universal/rules/memory.mdc`
- `.universal/rules/docs.mdc`
- `.universal/rules/graphs.mdc`
- `.universal/rules/refactor.mdc`
- `.universal/rules/performance.mdc`
- `.universal/rules/security.mdc`
- `.universal/rules/testing.mdc`

### 3. **Install MCP Tools**
```bash
# Install required MCP tools globally
npm install -g mcp-memory-bank mcp-knowledge-graph mcp-docs-provider mcp-sequential-thinking
```

### 4. **Configure MCP Tools**
Create `.universal/mcp/mcp.json`:
```json
{
  "mcpServers": {
    "memory-bank": {
      "command": "npx",
      "args": [
        "-y", "mcp-memory-bank",
        "--path", ".universal/memory/${GIT_BRANCH}"
      ]
    },
    "knowledge-graph": {
      "command": "npx",
      "args": [
        "-y", "mcp-knowledge-graph",
        "--port", "4280",
        "--store-path", ".universal/memory/${GIT_BRANCH}/graph"
      ]
    },
    "docs-provider": {
      "command": "npx",
      "args": [
        "-y", "mcp-docs-provider", "docs",
        "--port", "5050", "--watch",
        "--cache-dir", ".universal/memory/docs-cache"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y", "mcp-sequential-thinking",
        "--log-dir", ".universal/memory/tasks"
      ]
    }
  }
}
```

### 5. **Set Up Cursor AI Rules**
Create `.cursorrules`:
```json
{
  "terminal": {
    "shell": "powershell.exe",
    "args": [
      "-NoProfile",
      "-ExecutionPolicy", "Bypass",
      "-Command", "& { . $PROFILE; Clear-Host }"
    ]
  },
  "terminal.integrated.shell.windows": "powershell.exe",
  "terminal.integrated.shellArgs.windows": [
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "& { . $PROFILE; Clear-Host }"
  ],
  "rules": [
    {
      "name": "AI-Native Development",
      "description": "Core AI development workflow with MCP tools",
      "content": "Always use MCP tools for context, memory, and planning. Check memory-bank for project history, use knowledge-graph for dependencies, sequential-thinking for planning, and docs-provider for documentation."
    },
    {
      "name": "Memory-First Development",
      "description": "Always check project memory before making decisions",
      "content": "Before making architectural decisions or significant changes, always read .universal/memory/${GIT_BRANCH}/progress.md via memory-bank to understand project context and previous decisions."
    },
    {
      "name": "Dependency Analysis",
      "description": "Use knowledge graph for dependency queries",
      "content": "For questions about 'callers', 'callees', 'depends on', 'used by' or 'dependency', query knowledge-graph first rather than manual codebase searches."
    },
    {
      "name": "Refactoring Safety",
      "description": "AI-assisted refactoring with safety measures",
      "content": "When refactoring, splitting, or reorganizing code, use the ai-assisted-refactoring.md template, create feature branches, and document decisions in memory-bank."
    },
    {
      "name": "Documentation Automation",
      "description": "Use docs-provider for all documentation updates",
      "content": "Never hand-edit docs/ files directly. Use docs-provider for documentation generation and updates to ensure proper version control and consistency."
    },
    {
      "name": "Sequential Planning",
      "description": "Use sequential-thinking for complex tasks",
      "content": "For complex features, debugging, or multi-step processes, use sequential-thinking to break down tasks and track progress systematically."
    }
  ]
}
```

### 6. **Initialize Project Memory**
Create `.universal/memory/main/progress.md`:
```markdown
# Project Progress & Decisions

## Project Overview
**Project**: [Your Project Name]  
**Branch**: main  
**Goal**: [Describe your project goal]  
**Architecture**: [Describe your architecture]

## Recent Decisions & Changes

### [Date]: Project Initialization
- **Decision**: Set up AI-enhanced development environment
- **Rationale**: Improve productivity with MCP tools and AI assistance
- **Changes**: 
  - Created .universal directory structure
  - Configured MCP tools
  - Set up Cursor AI rules
  - Initialized memory structure

## Current Status
- ✅ Universal system setup complete
- ✅ MCP tools configured
- ✅ Cursor rules integrated
- ✅ Memory structure initialized
- 🔄 Ready for development
```

## 🚀 Usage Instructions

### For LLMs (AI Assistants)
1. **Always check project memory first** before making decisions
2. **Use MCP tools** for context, planning, and documentation
3. **Follow the established patterns** in the templates
4. **Document all decisions** in the memory bank
5. **Use the refactoring template** for any code reorganization

### For Developers
1. **Follow the daily practices** from the templates
2. **Use the security checklist** for all changes
3. **Run tests** before committing changes
4. **Update project memory** after significant changes
5. **Use the quick reference** for common commands

## 📚 Key Templates & Resources

### Development Workflow
- **AI Development Workflow:** `.universal/templates/ai-development-workflow.md`
- **AI-Enhanced Testing:** `.universal/templates/ai-enhanced-testing.md`
- **AI-Assisted Refactoring:** `.universal/templates/ai-assisted-refactoring.md`

### Project Management
- **Project Onboarding:** `.universal/templates/project-onboarding.md`
- **Security Checklist:** `.universal/templates/security-checklist.md`
- **CI/CD Pipeline:** `.universal/templates/ci-cd-pipeline.md`

### Quick References
- **Printable Quick Sheet:** `.universal/templates/printable-quick-sheet.md`

## 🔧 MCP Tool Usage

### Memory Bank
```bash
# Check project history
▶ memory-bank: "Show recent project decisions"

# Document new decision
▶ memory-bank: "Record decision: [description]"

# Update progress
▶ memory-bank: "Update progress: [status]"
```

### Knowledge Graph
```bash
# Analyze dependencies
▶ knowledge-graph: "Show all files that import [module]"

# Find relationships
▶ knowledge-graph: "Find components that use [feature]"
```

### Sequential Thinking
```bash
# Plan complex task
▶ sequential-thinking: "Create 5-step plan for [feature]"

# Track progress
▶ sequential-thinking: done 1
```

### Docs Provider
```bash
# Generate documentation
▶ docs-provider: "Update README with new features"

# Query documentation
▶ docs-provider: "How to implement [pattern]"
```

## ✅ Verification Checklist

- [ ] `.universal/` directory copied to project
- [ ] MCP tools installed globally
- [ ] `.universal/mcp/mcp.json` configured
- [ ] `.cursorrules` created
- [ ] `.universal/memory/main/progress.md` initialized
- [ ] All templates copied to `.universal/templates/`
- [ ] All rules copied to `.cursor/rules/`
- [ ] Project-specific docs directory created
- [ ] Git hooks configured (if applicable)
- [ ] Test system runs successfully

## 🎯 Next Steps

1. **Customize project-specific documentation** in `docs/project-specific/`
2. **Set up project-specific tests** following the testing template
3. **Configure CI/CD pipeline** using the CI/CD template
4. **Set up security scanning** using the security checklist
5. **Begin development** following the AI development workflow

## 📞 Support

- **Universal templates** in `.universal/` - Never change, copy to new projects
- **Project-specific docs** in `docs/project-specific/` - Update for current project
- **MCP tools** - Use for context, memory, and planning
- **Cursor AI rules** - Guide AI behavior and development patterns

---

**This system provides a complete AI-enhanced development environment that can be copied to any new project for consistent, productive development workflows.** 