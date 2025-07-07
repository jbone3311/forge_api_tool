# Project-Specific Setup Guide

## 🎯 Overview
This guide explains how to set up and organize project-specific content in the `.project-specific/` directory structure.

## 📁 Directory Structure

```
.project-specific/
├── docs/                   # Project documentation
│   ├── integration-guide.md
│   ├── troubleshooting-guide.md
│   ├── deployment-guide.md
│   ├── test-coverage.md
│   ├── cli-commands.md
│   └── REFACTORING_PLAN.md
├── config/                 # Project configuration
│   ├── api_preference.json
│   ├── rundiffusion_config.json
│   └── project-settings.json
├── templates/              # Project-specific templates
│   ├── api-documentation.md
│   ├── deployment-checklist.md
│   └── testing-procedures.md
└── README.md               # Project-specific overview
```

## 🚀 Setup Process

### **1. Create Project-Specific Structure**
```bash
# Create directories
mkdir -p .project-specific/docs
mkdir -p .project-specific/config
mkdir -p .project-specific/templates

# Move existing project-specific content
cp docs/project-specific/* .project-specific/docs/
cp config/* .project-specific/config/
```

### **2. Create Project-Specific README**
Create `.project-specific/README.md`:
```markdown
# Project-Specific Content

## Overview
This directory contains all project-specific content for [Project Name].

## Structure
- **docs/**: Project documentation
- **config/**: Project configuration files
- **templates/**: Project-specific templates

## Usage
- Update docs/ for project-specific documentation
- Modify config/ for project settings
- Create templates/ for project-specific workflows

## Integration with Universal System
- Universal templates in `.universal/templates/` remain unchanged
- Project-specific content here can be customized
- Use MCP tools to manage and update content
```

### **3. Organize Project Documentation**
Move and organize project-specific documentation:

#### **Essential Project Docs:**
- `integration-guide.md` - External service integration
- `troubleshooting-guide.md` - Common issues and solutions
- `deployment-guide.md` - Deployment procedures
- `test-coverage.md` - Testing strategies and coverage
- `cli-commands.md` - Command-line interface usage
- `REFACTORING_PLAN.md` - Code refactoring strategies

#### **Configuration Files:**
- `api_preference.json` - API configuration
- `rundiffusion_config.json` - External service config
- `project-settings.json` - Project-specific settings

#### **Project Templates:**
- `api-documentation.md` - API documentation template
- `deployment-checklist.md` - Deployment checklist
- `testing-procedures.md` - Testing procedures

## 🔧 Integration with Universal System

### **MCP Tool Integration**
```bash
# Update docs provider to include project-specific docs
▶ docs-provider: "Update configuration to include .project-specific/docs"

# Store project-specific decisions
▶ memory-bank: "Record project-specific architecture decisions"

# Analyze project dependencies
▶ knowledge-graph: "Map project-specific component relationships"
```

### **Cursor Rules Integration**
Update `.cursor/rules/` to include project-specific rules:
- Project-specific coding standards
- Domain-specific patterns
- Technology stack guidelines

## 📋 Maintenance

### **Regular Updates**
- Update project documentation as features change
- Maintain configuration files for current settings
- Keep templates up-to-date with best practices

### **Version Control**
- Include `.project-specific/` in version control
- Use meaningful commit messages for changes
- Document major changes in project memory

### **Backup and Migration**
- Backup project-specific content regularly
- Document migration procedures
- Maintain compatibility with universal system

## 🎯 Best Practices

### **1. Documentation Standards**
- Use consistent formatting and structure
- Include code examples where appropriate
- Keep documentation up-to-date with code changes

### **2. Configuration Management**
- Use environment variables for sensitive data
- Document configuration options
- Maintain configuration versioning

### **3. Template Development**
- Create reusable templates for common tasks
- Include placeholders for customization
- Document template usage and customization

### **4. Integration**
- Maintain clear separation from universal content
- Use MCP tools for automation
- Follow established patterns and conventions

## 📊 Monitoring and Analytics

### **Content Usage**
- Track which documentation is most accessed
- Monitor configuration changes
- Analyze template usage patterns

### **Effectiveness Metrics**
- Measure documentation completeness
- Track issue resolution time
- Monitor deployment success rates

## 🚀 Advanced Features

### **1. Automated Documentation**
```bash
# Generate API documentation
▶ docs-provider: "Generate API documentation from code"

# Update deployment guides
▶ docs-provider: "Update deployment guide with latest changes"
```

### **2. Configuration Validation**
```bash
# Validate configuration files
▶ memory-bank: "Validate project configuration"

# Check configuration consistency
▶ knowledge-graph: "Analyze configuration dependencies"
```

### **3. Template Automation**
```bash
# Generate project-specific templates
▶ docs-provider: "Create template for new feature documentation"

# Update existing templates
▶ docs-provider: "Update templates with latest best practices"
```

## 📞 Support

- **Universal System:** Use `.universal/templates/` for general guidance
- **MCP Tools:** Use MCP tools for automation and management
- **Project Memory:** Store project-specific decisions and context

---

**This project-specific setup provides a clean, organized structure for project-specific content while maintaining integration with the universal system.** 