# Project Onboarding Guide - Universal AI Development System

## 🎯 Overview
This guide provides comprehensive onboarding instructions for the Universal AI Development System. The system provides AI-enhanced development with MCP tools, memory management, and automated workflows.

## 📋 System Architecture

### Directory Structure
```
.universal/           # Universal files (copy to new projects)
├── rules/           # Cursor AI rules with metadata
├── templates/       # Universal templates
├── mcp/            # MCP tool configurations
├── memory/         # Project memory and context
├── extensions/     # IDE extensions
├── hooks/          # Git hooks
└── test-system/    # System testing

docs/               # Project-specific documentation
├── project-specific/ # Project-specific docs
└── features/       # Feature documentation
```

### Key Principles
- **Universal templates:** Never change `.universal/` - Copy to new projects
- **Project-specific docs:** Update `docs/project-specific/` for current project
- **AI-Native:** Use MCP tools for context, memory, and planning
- **Memory-First:** Always check project history before decisions
- **Automated Documentation:** Use docs-provider for all doc updates

## 🚀 Quick Setup

### 1. Copy Universal System
```bash
# Copy the entire .universal directory to your new project
cp -r .universal/ /path/to/your/new/project/
```

### 2. Install MCP Tools
```bash
# Install required MCP tools globally (one-time setup)
npm install -g mcp-memory-bank mcp-knowledge-graph mcp-docs-provider mcp-sequential-thinking
```

### 3. Run Setup Script
```bash
# Run the automated setup script
python .universal/setup-new-project.py [project-name]
```

### 4. Verify Installation
```bash
# Test the system
python .universal/test-system/test-universal-system.py

# Test MCP tools
▶ memory-bank: "Test connection"
▶ knowledge-graph: "Test connection"
▶ sequential-thinking: "Test connection"
▶ docs-provider: "Test connection"
```

## 📚 Essential Templates

### Development Workflow
- **AI Development Workflow:** `.universal/templates/ai-development-workflow.md`
- **AI-Enhanced Testing:** `.universal/templates/ai-enhanced-testing.md`
- **AI-Assisted Refactoring:** `.universal/templates/ai-assisted-refactoring.md`

### Project Management
- **Project Onboarding:** `.universal/templates/project-onboarding.md`
- **Security Checklist:** `.universal/templates/security-checklist.md`
- **CI/CD Pipeline:** `.universal/templates/ci-cd-pipeline.md`

### Quick References
- **LLM Setup Instructions:** `.universal/templates/llm-setup-instructions.md`
- **Printable Quick Sheet:** `.universal/templates/printable-quick-sheet.md`

## 🔧 MCP Tools Deep Dive

### Memory Bank (`mcp-memory-bank`)
**Purpose**: Document decisions, store templates, track progress

**Key Operations**:
```bash
# Project management
▶ memory-bank: list_projects
▶ memory-bank: create_project "project-decisions"

# File operations
▶ memory-bank: update_file_content project="main" path="adr/decision.md" content="..."
▶ memory-bank: get_file_content project="main" path="progress.md"

# Common use cases:
▶ memory-bank: "Document ADR: Why we chose this architecture"
▶ memory-bank: "Record rollback plan for feature X"
▶ memory-bank: "Store baseline performance metrics"
▶ memory-bank: "Update progress: completed feature Y"
```

### Knowledge Graph (`mcp-knowledge-graph`)
**Purpose**: Track code relationships, analyze dependencies, impact analysis

**Key Operations**:
```bash
# Entity management
▶ knowledge-graph: create_entities [{"name": "MainApp", "entityType": "Component", "observations": ["Main application class"]}]
▶ knowledge-graph: create_relations [{"from": "app.py", "to": "core/__init__.py", "relationType": "imports"}]

# Search and analysis
▶ knowledge-graph: search_nodes query="API"
▶ knowledge-graph: open_nodes names=["app.py", "core.py"]

# Common queries:
▶ knowledge-graph: "Show all files that import app.py"
▶ knowledge-graph: "Find circular dependencies in current codebase"
▶ knowledge-graph: "List all components that use database"
▶ knowledge-graph: "Compare dependency complexity before/after refactor"
```

### Sequential Thinking (`mcp-sequential-thinking`)
**Purpose**: Plan, generate code, track development steps

**Key Operations**:
```bash
# Planning phase
▶ sequential-thinking: "Create 6-step plan to implement user authentication"
▶ sequential-thinking: "Analyze impact of adding caching layer"

# Implementation phase
▶ sequential-thinking: "Generate code for user authentication with proper imports"
▶ sequential-thinking: "Create caching factory pattern with environment variable selection"

# Progress tracking
▶ sequential-thinking: done 1
▶ sequential-thinking: "Review completed steps and plan next iteration"

# Code generation patterns:
▶ sequential-thinking: "Generate pytest stubs for [component] with proper fixtures"
▶ sequential-thinking: "Create __init__.py files with proper exports for [module]"
▶ sequential-thinking: "Generate error handling wrapper for [function]"
```

### Docs Provider (`mcp-docs-provider`)
**Purpose**: Query documentation, generate API docs

**Key Operations**:
```bash
# Documentation queries
▶ docs-provider: "How to structure Flask application with blueprints?"
▶ docs-provider: "Best practices for Python plugin architecture?"

# During development:
▶ docs-provider: "Generate API documentation for new authentication system"
▶ docs-provider: "Update README with new project structure"
```

## 🎯 Development Workflow

### Starting New Feature
1. **Check Project Memory**
   ```bash
   ▶ memory-bank: "Show recent project decisions"
   ▶ memory-bank: "Show architecture decisions for [feature]"
   ```

2. **Plan with Sequential Thinking**
   ```bash
   ▶ sequential-thinking: "Create 5-step plan for [feature]"
   ▶ sequential-thinking: "Analyze dependencies for [feature]"
   ```

3. **Analyze Dependencies**
   ```bash
   ▶ knowledge-graph: "Show files that will be affected by [feature]"
   ▶ knowledge-graph: "Find existing components similar to [feature]"
   ```

4. **Implement Following Templates**
   - Use `.universal/templates/ai-development-workflow.md`
   - Follow security checklist from `.universal/templates/security-checklist.md`
   - Use testing framework from `.universal/templates/ai-enhanced-testing.md`

5. **Document Decisions**
   ```bash
   ▶ memory-bank: "Record decision: [description]"
   ▶ memory-bank: "Update progress: completed [step]"
   ```

### Refactoring Code
1. **Use Refactoring Template**
   - Follow `.universal/templates/ai-assisted-refactoring.md`
   - Create feature branch: `git checkout -b refactor/[description]`

2. **Analyze Impact**
   ```bash
   ▶ knowledge-graph: "Show all dependencies of [file]"
   ▶ knowledge-graph: "Find circular dependencies"
   ```

3. **Document Decisions**
   ```bash
   ▶ memory-bank: "Record refactoring decisions"
   ▶ memory-bank: "Document rollback plan"
   ```

4. **Test Thoroughly**
   ```bash
   python .universal/test-system/test-universal-system.py
   # Run project-specific tests
   ```

### Documentation Updates
1. **Use Docs Provider**
   ```bash
   ▶ docs-provider: "Update README with new features"
   ▶ docs-provider: "Generate API documentation"
   ```

2. **Never Edit Docs Directly**
   - All documentation updates go through docs-provider
   - Maintains version control and consistency

3. **Update Project Memory**
   ```bash
   ▶ memory-bank: "Record documentation changes"
   ```

## 🧪 Testing Framework

### System Tests
```bash
# Test entire universal system
python .universal/test-system/test-universal-system.py

# Quick test
python .universal/test-system/quick-test.py
```

### MCP Tool Tests
```bash
# Test memory bank
▶ memory-bank: "Test connection and basic operations"

# Test knowledge graph
▶ knowledge-graph: "Test connection and basic queries"

# Test sequential thinking
▶ sequential-thinking: "Test connection and planning"

# Test docs provider
▶ docs-provider: "Test connection and documentation queries"
```

### Project-Specific Tests
```bash
# Run project tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 🔒 Security Practices

### Security Checklist
Follow `.universal/templates/security-checklist.md` for all changes:

- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] Sensitive data encrypted
- [ ] Dependencies updated
- [ ] Security tests written
- [ ] Error handling secure
- [ ] Logging without sensitive data

### Security Tools
```bash
# Check dependencies for vulnerabilities
npm audit
pip-audit

# Run security linters
bandit -r .
safety check
```

## 📊 Monitoring and Metrics

### Performance Monitoring
```bash
# Monitor memory usage
▶ memory-bank: "Record performance metrics"

# Analyze dependencies
▶ knowledge-graph: "Show dependency complexity metrics"
```

### Progress Tracking
```bash
# Update progress regularly
▶ memory-bank: "Update progress: [current status]"

# Review completed work
▶ sequential-thinking: "Review completed steps"
```

## 🚨 Troubleshooting

### Common Issues

#### MCP Tools Not Working
```bash
# Reinstall MCP tools
npm install -g mcp-memory-bank mcp-knowledge-graph mcp-docs-provider mcp-sequential-thinking

# Check configuration
cat .universal/mcp/mcp.json

# Test individual tools
▶ memory-bank: "Test connection"
```

#### Memory Issues
```bash
# Check memory structure
ls -la .universal/memory/

# Reinitialize memory
mkdir -p .universal/memory/main
echo "# Project Progress" > .universal/memory/main/progress.md
```

#### Cursor Rules Not Working
```bash
# Check .cursorrules file
cat .cursorrules

# Restart Cursor
# Reload window in Cursor
```

### Getting Help
1. **Check project memory** for similar issues
2. **Use sequential thinking** to plan troubleshooting
3. **Document the issue** in memory bank
4. **Follow troubleshooting templates**

## 📞 Support Resources

### Documentation
- **Universal Templates:** `.universal/templates/` - Never change, copy to new projects
- **Project-Specific Docs:** `docs/project-specific/` - Update for current project
- **LLM Setup Instructions:** `.universal/templates/llm-setup-instructions.md`

### Tools
- **MCP Tools:** Use for context, memory, and planning
- **Cursor AI Rules:** Guide AI behavior and development patterns
- **Test System:** Validate system functionality

### Workflows
- **AI Development Workflow:** `.universal/templates/ai-development-workflow.md`
- **Security Checklist:** `.universal/templates/security-checklist.md`
- **Project Onboarding:** `.universal/templates/project-onboarding.md`
- **CI/CD Pipeline:** `.universal/templates/ci-cd-pipeline.md`

## ✅ Onboarding Checklist

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
- [ ] MCP tools tested and working
- [ ] Security checklist reviewed
- [ ] Development workflow understood
- [ ] Documentation standards reviewed

## 🎯 Next Steps

1. **Customize project-specific documentation** in `docs/project-specific/`
2. **Set up project-specific tests** following the testing template
3. **Configure CI/CD pipeline** using the CI/CD template
4. **Set up security scanning** using the security checklist
5. **Begin development** following the AI development workflow

## 📚 Additional Resources

### Learning Path
1. **Start with:** `.universal/templates/printable-quick-sheet.md`
2. **Read:** `.universal/templates/llm-setup-instructions.md`
3. **Follow:** `.universal/templates/ai-development-workflow.md`
4. **Use:** `.universal/templates/ai-assisted-refactoring.md` for code changes
5. **Maintain:** `.universal/templates/security-checklist.md` for all changes

### Best Practices
- **Daily:** Check project memory before starting work
- **Weekly:** Review and update project memory
- **Monthly:** Review universal templates for improvements
- **Always:** Use MCP tools for context and planning

---

**This system provides a complete AI-enhanced development environment that can be copied to any new project for consistent, productive development workflows.**

### Quick Commands Reference

```bash
# Check project memory
▶ memory-bank: "Show recent decisions"

# Analyze dependencies
▶ knowledge-graph: "Show files that import [module]"

# Plan complex task
▶ sequential-thinking: "Create plan for [feature]"

# Generate documentation
▶ docs-provider: "Update README"

# Test system
python .universal/test-system/test-universal-system.py
```

### Key Directories
- `.universal/` - Never change (copy to new projects)
- `docs/project-specific/` - Update for this project
- `tests/` - All test files
- `.cursor/rules/` - Cursor AI rules

### Essential Templates
- **AI Development Workflow:** `.universal/templates/ai-development-workflow.md`
- **Security Checklist:** `.universal/templates/security-checklist.md`
- **Project Onboarding:** `.universal/templates/project-onboarding.md`
- **CI/CD Pipeline:** `.universal/templates/ci-cd-pipeline.md`

### Daily Practices
- **Follow daily practices** from `.universal/templates/ai-development-workflow.md`
- **Use security checklist** from `.universal/templates/security-checklist.md`
- **Update project memory** after significant changes
- **Use MCP tools** for context and planning

### Copying to New Projects
1. Copy entire `.universal/` directory
2. Run setup script: `python .universal/setup-new-project.py [project-name]`
3. Install MCP tools: `npm install -g mcp-memory-bank mcp-knowledge-graph mcp-docs-provider mcp-sequential-thinking`
4. Test system: `python .universal/test-system/test-universal-system.py`
5. Begin development following templates

**Remember:** Universal templates in `.universal/` are for copying to new projects. Only update `docs/project-specific/` for this project.