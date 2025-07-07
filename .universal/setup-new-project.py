#!/usr/bin/env python3
"""
Universal AI Development Environment Setup Script

This script sets up the .universal directory structure and MCP tools
in any new project for AI-enhanced development.

Usage:
    python setup-new-project.py [project-name]
"""

import os
import sys
import shutil
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional

class UniversalSetup:
    def __init__(self, project_name: str = None):
        self.project_name = project_name or "new-project"
        self.current_dir = Path.cwd()
        self.universal_dir = self.current_dir / ".universal"
        self.platform = platform.system().lower()
        
    def setup_directory_structure(self) -> None:
        """Create the .universal directory structure"""
        print("📁 Creating .universal directory structure...")
        
        # Create main directories
        directories = [
            ".universal/rules",
            ".universal/templates", 
            ".universal/mcp",
            ".universal/memory/main",
            ".universal/memory/tasks",
            ".universal/memory/docs-cache",
            ".universal/extensions",
            ".universal/hooks"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            if dir_path.exists():
                print(f"  ⚠️  {directory} already exists, skipping...")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"  ✅ Created {directory}")
    
    def create_cursor_rules(self) -> None:
        """Create enhanced .cursorrules file"""
        print("🎯 Creating Cursor AI rules...")
        
        # Platform-specific terminal configuration
        if self.platform == "windows":
            terminal_config = {
                "shell": "powershell.exe",
                "args": [
                    "-NoProfile",
                    "-ExecutionPolicy", "Bypass", 
                    "-Command", "& { . $PROFILE; Clear-Host }"
                ]
            }
            terminal_integrated = "powershell.exe"
            terminal_args = [
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-Command",
                "& { . $PROFILE; Clear-Host }"
            ]
        elif self.platform == "darwin":  # macOS
            terminal_config = {
                "shell": "/bin/zsh",
                "args": ["-l"]
            }
            terminal_integrated = "/bin/zsh"
            terminal_args = ["-l"]
        else:  # Linux and others
            terminal_config = {
                "shell": "/bin/bash",
                "args": ["-l"]
            }
            terminal_integrated = "/bin/bash"
            terminal_args = ["-l"]
        
        cursor_rules = {
            "terminal": terminal_config,
            "terminal.integrated.shell.windows": terminal_integrated if self.platform == "windows" else None,
            "terminal.integrated.shellArgs.windows": terminal_args if self.platform == "windows" else None,
            "terminal.integrated.shell.osx": terminal_integrated if self.platform == "darwin" else None,
            "terminal.integrated.shellArgs.osx": terminal_args if self.platform == "darwin" else None,
            "terminal.integrated.shell.linux": terminal_integrated if self.platform == "linux" else None,
            "terminal.integrated.shellArgs.linux": terminal_args if self.platform == "linux" else None,
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
        
        # Remove None values for cleaner JSON
        cursor_rules = {k: v for k, v in cursor_rules.items() if v is not None}
        
        with open(".cursorrules", "w", encoding="utf-8") as f:
            json.dump(cursor_rules, f, indent=2)
        
        print("  ✅ Created .cursorrules")
    
    def create_mcp_config(self) -> None:
        """Create MCP configuration file"""
        print("🔧 Creating MCP configuration...")
        
        mcp_config = {
            "mcpServers": {
                "memory-bank": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-memory-bank",
                        "--path", ".universal/memory/${GIT_BRANCH}"
                    ]
                },
                "knowledge-graph": {
                    "command": "npx", 
                    "args": [
                        "-y", "@modelcontextprotocol/server-knowledge-graph",
                        "--port", "4280",
                        "--store-path", ".universal/memory/${GIT_BRANCH}/graph"
                    ]
                },
                "docs-provider": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-docs-provider", "docs",
                        "--port", "5050", "--watch",
                        "--cache-dir", ".universal/memory/docs-cache"
                    ]
                },
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-sequential-thinking", 
                        "--log-dir", ".universal/memory/tasks"
                    ]
                }
            }
        }
        
        with open(".universal/mcp/mcp.json", "w", encoding="utf-8") as f:
            json.dump(mcp_config, f, indent=2)
        
        print("  ✅ Created .universal/mcp/mcp.json")
    
    def copy_universal_templates(self) -> None:
        """Copy universal templates to the new project"""
        print("📋 Copying universal templates...")
        
        # Define source template directory (this script's location)
        script_dir = Path(__file__).parent
        source_templates_dir = script_dir / "templates"
        
        if not source_templates_dir.exists():
            print(f"  ⚠️  Source templates directory not found: {source_templates_dir}")
            print("  📝 Creating basic templates...")
            self.create_basic_templates()
            return
        
        # Copy templates
        target_templates_dir = Path(".universal/templates")
        try:
            if target_templates_dir.exists():
                shutil.rmtree(target_templates_dir)
            shutil.copytree(source_templates_dir, target_templates_dir)
            print("  ✅ Copied universal templates")
        except Exception as e:
            print(f"  ⚠️  Failed to copy templates: {e}")
            print("  📝 Creating basic templates...")
            self.create_basic_templates()
    
    def create_basic_templates(self) -> None:
        """Create basic templates if copying fails"""
        templates_dir = Path(".universal/templates")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a basic AI development workflow template
        workflow_template = """# AI Development Workflow Template

## Feature Development Process

### 1. Planning Phase
- [ ] Define feature requirements
- [ ] Check project memory for similar features
- [ ] Create sequential thinking plan
- [ ] Document architectural decisions

### 2. Implementation Phase
- [ ] Create feature branch
- [ ] Implement step by step
- [ ] Use knowledge graph for dependency analysis
- [ ] Document code changes

### 3. Testing Phase
- [ ] Write tests for new functionality
- [ ] Run existing test suite
- [ ] Document test results

### 4. Documentation Phase
- [ ] Update API documentation
- [ ] Update README if needed
- [ ] Document lessons learned

### 5. Review Phase
- [ ] Code review
- [ ] Update project memory
- [ ] Merge to main branch

## Memory Commands
- `memory-bank: "Record decision: [description]"`
- `memory-bank: "Update progress: [status]"`
- `memory-bank: "Document lesson: [insight]"`

## Knowledge Graph Commands
- `knowledge-graph: "Show dependencies for [component]"`
- `knowledge-graph: "Find files using [functionality]"`

## Sequential Thinking Commands
- `sequential-thinking: "Create plan for [task]"`
- `sequential-thinking: "Generate code for step [N]"`
- `sequential-thinking: done [N]`
"""
        
        with open(templates_dir / "ai-development-workflow.md", "w", encoding="utf-8") as f:
            f.write(workflow_template)
        
        print("  ✅ Created basic templates")
    
    def create_initial_memory(self) -> None:
        """Create initial project memory"""
        print("🧠 Creating initial project memory...")
        
        progress_content = f"""# {self.project_name} - Project Progress & Decisions

## Project Overview
**Project**: {self.project_name}  
**Branch**: main  
**Goal**: [Describe your project goal]  
**Architecture**: [Describe your architecture]

## Recent Decisions & Changes

### {self.get_current_date()}: Project Initialization
- **Decision**: Set up AI-enhanced development environment
- **Rationale**: Improve productivity with MCP tools and AI assistance
- **Changes**: 
  - Created .universal directory structure
  - Configured MCP tools (memory-bank, knowledge-graph, docs-provider, sequential-thinking)
  - Set up Cursor AI rules
  - Initialized memory structure

## Architecture Decisions

### AI-Native Development Workflow
- **Memory-First**: Always check project history before decisions
- **Dependency Analysis**: Use knowledge graph for relationship queries
- **Automated Documentation**: Use docs-provider for all doc updates
- **Sequential Planning**: Use sequential-thinking for complex tasks
- **Refactoring Safety**: AI-assisted refactoring with templates

### Project Structure
```
.universal/           # Universal files (copyable to new projects)
├── rules/           # Cursor AI rules
├── templates/       # Universal templates
├── mcp/            # MCP tool configurations
├── memory/         # Project memory and context
└── extensions/     # Future extensions

.project-specific/   # Project-specific content
├── docs/          # Project documentation
├── config/        # Project configuration
└── templates/     # Project-specific templates

docs/               # Legacy documentation (to be cleaned)
├── project-specific/ # Project-specific docs
└── features/       # Feature documentation
```

## Current Status
- ✅ Universal system setup complete
- ✅ MCP tools configured
- ✅ Cursor rules integrated
- ✅ Memory structure initialized
- 🔄 Ready for development

## Next Steps
1. Define project requirements and architecture
2. Set up development environment
3. Create initial codebase structure
4. Begin feature development with AI assistance

## Lessons Learned
- AI-native workflows require careful rule design
- Memory-first development prevents decision conflicts
- MCP tools provide excellent context preservation

@progress @decisions @architecture @setup
"""
        
        with open(".universal/memory/main/progress.md", "w", encoding="utf-8") as f:
            f.write(progress_content)
        
        print("  ✅ Created .universal/memory/main/progress.md")
    
    def create_quick_start_guide(self) -> None:
        """Create quick start guide for the project"""
        print("📖 Creating quick start guide...")
        
        guide_content = f"""# {self.project_name} - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js (for MCP tools)
- Python 3.8+
- Git

### Initial Setup
```bash
# Install MCP tools
npm install -g @modelcontextprotocol/server-memory-bank @modelcontextprotocol/server-knowledge-graph @modelcontextprotocol/server-docs-provider @modelcontextprotocol/server-sequential-thinking

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
{self.project_name}/
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
"""
        
        with open("QUICK_START.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        print("  ✅ Created QUICK_START.md")
    
    def create_gitignore_updates(self) -> None:
        """Update .gitignore for universal system"""
        print("🔒 Updating .gitignore...")
        
        gitignore_additions = """

# Universal AI Development Environment
.universal/memory/*/graph/
.universal/memory/docs-cache/
.universal/memory/tasks/
.universal/extensions/

# MCP Tool Caches
.cursorMEM/
.mcp-cache/

# Node modules for MCP tools (if installed locally)
node_modules/
"""
        
        gitignore_path = Path(".gitignore")
        if gitignore_path.exists():
            # Check if already contains universal entries
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "Universal AI Development Environment" not in content:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(gitignore_additions)
                    print("  ✅ Updated .gitignore")
                else:
                    print("  ⚠️  .gitignore already contains universal entries")
        else:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(gitignore_additions)
            print("  ✅ Created .gitignore")
    
    def get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def run_setup(self) -> None:
        """Run the complete setup process"""
        print(f"🚀 Setting up AI-enhanced development environment for '{self.project_name}'")
        print("=" * 60)
        
        try:
            self.setup_directory_structure()
            self.create_cursor_rules()
            self.create_mcp_config()
            self.copy_universal_templates()
            self.create_initial_memory()
            self.create_quick_start_guide()
            self.create_gitignore_updates()
            
            print("\n" + "=" * 60)
            print("✅ Setup complete! Your AI-enhanced development environment is ready.")
            print("\n📖 Next steps:")
            print("1. Read QUICK_START.md for usage instructions")
            print("2. Install MCP tools: npm install -g @modelcontextprotocol/server-memory-bank @modelcontextprotocol/server-knowledge-graph @modelcontextprotocol/server-docs-provider @modelcontextprotocol/server-sequential-thinking")
            print("3. Initialize git: git init && git add . && git commit -m 'Initial setup'")
            print("4. Start developing with AI assistance!")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def main():
    """Main function"""
    project_name = sys.argv[1] if len(sys.argv) > 1 else None
    
    setup = UniversalSetup(project_name)
    setup.run_setup()

if __name__ == "__main__":
    main() 