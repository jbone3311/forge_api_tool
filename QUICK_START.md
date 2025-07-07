# --help - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js (for MCP tools)
- Python 3.8+
- Git

### Initial Setup
```bash
# Install MCP tools
npm install -g mcp-memory-bank mcp-knowledge-graph mcp-docs-provider mcp-sequential-thinking

# Initialize git (if not already done)
git init

# Create initial commit
git add .
git commit -m "Initial setup: AI-enhanced development environment"
```

### Daily Development Workflow
```bash
# Check project context
memory-bank: get_file_content project="main" path="progress.md"

# Start new feature
git checkout -b feature/[description]
sequential-thinking: "Create 5-step plan for [feature]"

# Analyze dependencies
knowledge-graph: "Show all files affected by [component]"

# Generate documentation
docs-provider: "Generate API documentation for [new feature]"
```

## 🧠 Memory-First Development

Before making any significant decisions:
1. Check project history: `memory-bank: get_file_content project="main" path="progress.md"`
2. Document decisions: `memory-bank: "Record decision: [description] with rationale: [reasoning]"`
3. Update progress: `memory-bank: "Update progress: completed [task]"`

## 🔍 Dependency Analysis

For dependency questions:
- `knowledge-graph: "Show all files that import [module]"`
- `knowledge-graph: "Find circular dependencies in [component]"`
- `knowledge-graph: "List all components that use [functionality]"`

## 📋 Sequential Planning

For complex tasks:
- `sequential-thinking: "Create 6-step plan for [task]"`
- `sequential-thinking: "Generate code for step 1: [description]"`
- `sequential-thinking: done 1`

## 📚 Documentation

For documentation:
- `docs-provider: "Generate API documentation for [endpoint]"`
- `docs-provider: "Update README with new [feature] information"`
- `docs-provider: "Create troubleshooting guide for [issue]"`

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
memory-bank: "Record final decisions for [feature]"
```

### Debugging
```bash
# Analyze problem
knowledge-graph: "Show all components involved in [error]"
memory-bank: "Check if this issue occurred before"

# Create debugging plan
sequential-thinking: "Create debugging checklist for [issue]"

# Document solution
memory-bank: "Document solution for [issue]"
```

## 📊 Project Structure

```
--help/
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
1. Check memory bank for similar problems
2. Use knowledge graph for dependency analysis
3. Create debugging plan with sequential-thinking
4. Document solutions for future reference

---

**Happy AI-enhanced coding! 🚀**
