# test-project - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js (for MCP tools)
- python 3.8+
- Git

### Initial Setup
```bash
# Install MCP tools (Real tools that exist)
npm install -g @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-postgres @modelcontextprotocol/server-brave-search @modelcontextprotocol/server-github

# Install Python MCP tools
pip install mcp-playwright mcp --user

# Install Python dependencies
pip install -r requirements.txt

# Or if using pip:
pip install -e .

# Initialize git (if not already done)
git init

# Create initial commit
git add .
git commit -m "Initial setup: AI-enhanced development environment"
```

### Daily Development Workflow
```bash
# Check project context
sequential-thinking: "Create plan for current task"

# Start new feature
git checkout -b feature/[description]
sequential-thinking: "Create 5-step plan for [feature]"

# Analyze dependencies
postgres: "Query project dependencies"

# Generate documentation
github: "Access project documentation"
```

## 🧠 Memory-First Development

Before making any significant decisions:
1. Check project history: `sequential-thinking: "Review project progress"`
2. Document decisions: `sequential-thinking: "Record decision: [description] with rationale: [reasoning]"`
3. Update progress: `sequential-thinking: "Update progress: completed [task]"`

## 🔍 Dependency Analysis

For dependency questions:
- `postgres: "Query files that import [module]"`
- `postgres: "Find circular dependencies in [component]"`
- `postgres: "List all components that use [functionality]"`

## 📋 Sequential Planning

For complex tasks:
- `sequential-thinking: "Create 6-step plan for [task]"`
- `sequential-thinking: "Generate code for step 1: [description]"`
- `sequential-thinking: done 1`

## 📚 Documentation

For documentation:
- `github: "Access API documentation for [endpoint]"`
- `github: "Update README with new [feature] information"`
- `github: "Create troubleshooting guide for [issue]"`

## 🎯 Common Commands

### Feature Development
```bash
# Plan feature
sequential-thinking: "Create plan for [feature]"

# Implement step by step
sequential-thinking: "Generate code for step [N]: [description]"
git commit -m "Step [N]: [description]"
sequential-thinking: done [N]

# Document decisions
sequential-thinking: "Record final decisions for [feature]"
```

### Debugging
```bash
# Analyze problem
postgres: "Query components involved in [error]"
sequential-thinking: "Check if this issue occurred before"

# Create debugging plan
sequential-thinking: "Create debugging checklist for [issue]"

# Document solution
sequential-thinking: "Document solution for [issue]"
```

## 📊 Project Structure

```
test-project/
├── .universal/          # AI development environment
│   ├── rules/          # Cursor AI rules
│   ├── templates/      # Universal templates
│   ├── mcp/           # MCP tool configurations
│   ├── memory/        # Project memory and context
│   └── extensions/    # Future extensions
├── docs/              # Project documentation
├── src/               # Source code
├── tests/             # Test files
├── .cursorrules       # Cursor AI configuration
└── README.md          # Project readme
```

## 🎁 Benefits

1. **🧠 Cognitive Offloading**: AI handles complexity, you handle decisions
2. **📚 Knowledge Preservation**: Everything documented automatically
3. **🔄 Iterative Safety**: Small steps, easy recovery
4. **🎯 Goal-Oriented**: Each step has clear deliverable
5. **🤖 AI-Native**: Uses LLMs for their strengths

## 📞 Support

For issues or questions:
1. Check sequential thinking for similar problems
2. Use postgres for dependency analysis
3. Create debugging plan with sequential-thinking
4. Document solutions for future reference

---

**Happy AI-enhanced coding! 🚀**
