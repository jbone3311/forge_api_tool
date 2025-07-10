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
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import ast

class UniversalSetup:
    def __init__(self, project_name: str = None):
        self.project_name = project_name or "new-project"
        self.current_dir = Path.cwd()
        self.universal_dir = self.current_dir / ".universal"
        self.platform = platform.system().lower()
        self.project_info = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze existing project to extract information"""
        print("🔍 Analyzing existing project...")
        
        project_info = {
            "name": self.project_name,
            "type": "unknown",
            "language": "unknown",
            "framework": "unknown",
            "dependencies": [],
            "structure": {},
            "readme": "",
            "config_files": [],
            "entry_points": [],
            "test_files": [],
            "documentation": []
        }
        
        # Detect project type and language
        project_info.update(self.detect_project_type())
        
        # Extract README content
        project_info["readme"] = self.extract_readme()
        
        # Analyze project structure
        project_info["structure"] = self.analyze_project_structure()
        
        # Find configuration files
        project_info["config_files"] = self.find_config_files()
        
        # Find entry points
        project_info["entry_points"] = self.find_entry_points()
        
        # Find test files
        project_info["test_files"] = self.find_test_files()
        
        # Find documentation
        project_info["documentation"] = self.find_documentation()
        
        # Extract dependencies
        project_info["dependencies"] = self.extract_dependencies()
        
        self.project_info = project_info
        print("  ✅ Project analysis complete")
        return project_info
    
    def detect_project_type(self) -> Dict[str, str]:
        """Detect project type and primary language"""
        project_type = "unknown"
        language = "unknown"
        framework = "unknown"
        
        # Check for common project files
        if Path("package.json").exists():
            project_type = "nodejs"
            language = "javascript"
            try:
                with open("package.json", "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                    if "dependencies" in pkg_data:
                        deps = list(pkg_data["dependencies"].keys())
                        if "react" in deps:
                            framework = "react"
                        elif "vue" in deps:
                            framework = "vue"
                        elif "angular" in deps:
                            framework = "angular"
                        elif "express" in deps:
                            framework = "express"
                        elif "next" in deps:
                            framework = "next.js"
            except:
                pass
                
        elif Path("requirements.txt").exists() or Path("pyproject.toml").exists():
            project_type = "python"
            language = "python"
            if Path("pyproject.toml").exists():
                try:
                    import tomllib
                    with open("pyproject.toml", "rb") as f:
                        toml_data = tomllib.load(f)
                        if "tool" in toml_data and "poetry" in toml_data["tool"]:
                            framework = "poetry"
                        elif "build-system" in toml_data:
                            framework = "setuptools"
                except:
                    pass
            elif Path("requirements.txt").exists():
                framework = "pip"
                
        elif Path("Cargo.toml").exists():
            project_type = "rust"
            language = "rust"
            framework = "cargo"
            
        elif Path("go.mod").exists():
            project_type = "go"
            language = "go"
            framework = "go modules"
            
        elif Path("pom.xml").exists():
            project_type = "java"
            language = "java"
            framework = "maven"
            
        elif Path("build.gradle").exists():
            project_type = "java"
            language = "java"
            framework = "gradle"
            
        elif Path("Gemfile").exists():
            project_type = "ruby"
            language = "ruby"
            framework = "bundler"
            
        elif Path("composer.json").exists():
            project_type = "php"
            language = "php"
            framework = "composer"
            
        return {
            "type": project_type,
            "language": language,
            "framework": framework
        }
    
    def extract_readme(self) -> str:
        """Extract README content"""
        readme_files = ["README.md", "README.txt", "README.rst", "readme.md"]
        
        for readme_file in readme_files:
            if Path(readme_file).exists():
                try:
                    with open(readme_file, "r", encoding="utf-8") as f:
                        return f.read()
                except:
                    continue
        
        return ""
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure"""
        structure = {
            "directories": [],
            "files": [],
            "code_files": [],
            "config_files": [],
            "test_files": [],
            "doc_files": []
        }
        
        # Common patterns to ignore
        ignore_patterns = [
            ".git", ".svn", ".hg", "__pycache__", "node_modules", 
            ".venv", "venv", "env", ".env", "dist", "build",
            ".universal", ".project-specific"
        ]
        
        for root, dirs, files in os.walk(self.current_dir):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns and not d.startswith('.')]
            
            rel_root = Path(root).relative_to(self.current_dir)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = rel_root / file
                structure["files"].append(str(file_path))
                
                # Categorize files
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.rs', '.go', '.php', '.rb')):
                    structure["code_files"].append(str(file_path))
                elif file.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf')):
                    structure["config_files"].append(str(file_path))
                elif file.endswith(('.md', '.txt', '.rst', '.adoc')):
                    structure["doc_files"].append(str(file_path))
                elif 'test' in file.lower() or file.endswith(('_test.py', '.test.js', '.spec.js')):
                    structure["test_files"].append(str(file_path))
            
            # Add directories
            for dir_name in dirs:
                structure["directories"].append(str(rel_root / dir_name))
        
        return structure
    
    def find_config_files(self) -> List[str]:
        """Find configuration files"""
        config_files = []
        config_patterns = [
            "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf",
            "package.json", "pyproject.toml", "requirements.txt", "Cargo.toml",
            "go.mod", "pom.xml", "build.gradle", "Gemfile", "composer.json"
        ]
        
        for pattern in config_patterns:
            config_files.extend([str(f) for f in Path(".").glob(pattern)])
        
        return list(set(config_files))
    
    def find_entry_points(self) -> List[str]:
        """Find entry points based on project type"""
        entry_points = []
        
        if self.project_info.get("type") == "python":
            # Look for common Python entry points
            entry_patterns = ["main.py", "app.py", "run.py", "server.py", "cli.py"]
            for pattern in entry_patterns:
                if Path(pattern).exists():
                    entry_points.append(pattern)
                    
        elif self.project_info.get("type") == "nodejs":
            # Look for package.json scripts and common entry points
            if Path("package.json").exists():
                try:
                    with open("package.json", "r", encoding="utf-8") as f:
                        pkg_data = json.load(f)
                        if "main" in pkg_data:
                            entry_points.append(pkg_data["main"])
                        if "scripts" in pkg_data:
                            for script_name, script_cmd in pkg_data["scripts"].items():
                                if "start" in script_name or "dev" in script_name:
                                    entry_points.append(f"npm run {script_name}")
                except:
                    pass
            
            # Common Node.js entry points
            entry_patterns = ["index.js", "app.js", "server.js", "main.js"]
            for pattern in entry_patterns:
                if Path(pattern).exists():
                    entry_points.append(pattern)
        
        return entry_points
    
    def find_test_files(self) -> List[str]:
        """Find test files"""
        test_files = []
        test_patterns = [
            "test_*.py", "*_test.py", "*.test.js", "*.spec.js", "test/*",
            "tests/*", "__tests__/*", "spec/*", "test/**/*.py", "tests/**/*.py"
        ]
        
        for pattern in test_patterns:
            test_files.extend([str(f) for f in Path(".").glob(pattern)])
        
        return list(set(test_files))
    
    def find_documentation(self) -> List[str]:
        """Find documentation files"""
        doc_files = []
        doc_patterns = [
            "*.md", "*.txt", "*.rst", "*.adoc", "docs/*", "documentation/*",
            "README*", "CHANGELOG*", "LICENSE*"
        ]
        
        for pattern in doc_patterns:
            doc_files.extend([str(f) for f in Path(".").glob(pattern)])
        
        return list(set(doc_files))
    
    def extract_dependencies(self) -> List[str]:
        """Extract project dependencies"""
        dependencies = []
        
        if self.project_info.get("type") == "python":
            if Path("requirements.txt").exists():
                try:
                    with open("requirements.txt", "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                dependencies.append(line.split('==')[0].split('>=')[0].split('<=')[0])
                except:
                    pass
                    
        elif self.project_info.get("type") == "nodejs":
            if Path("package.json").exists():
                try:
                    with open("package.json", "r", encoding="utf-8") as f:
                        pkg_data = json.load(f)
                        if "dependencies" in pkg_data:
                            dependencies.extend(list(pkg_data["dependencies"].keys()))
                        if "devDependencies" in pkg_data:
                            dependencies.extend(list(pkg_data["devDependencies"].keys()))
                except:
                    pass
        
        return dependencies
    
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
                "playwright": {
                    "command": "mcp-playwright",
                    "args": []
                },
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-sequential-thinking"
                    ]
                },
                "postgres": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-postgres",
                        "--connection-string",
                        "postgresql://localhost:5432/your_database"
                    ]
                },
                "brave-search": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-brave-search",
                        "--api-key",
                        "${BRAVE_API_KEY}"
                    ]
                },
                "github": {
                    "command": "npx",
                    "args": [
                        "-y", "@modelcontextprotocol/server-github",
                        "--token",
                        "${GITHUB_TOKEN}"
                    ]
                }
            }
        }
        
        with open(".universal/mcp/mcp.json", "w", encoding="utf-8") as f:
            json.dump(mcp_config, f, indent=2)
        
        print("  ✅ Created .universal/mcp/mcp.json")
    
    def copy_universal_templates(self) -> None:
        """Copy universal templates to the new project"""
        print("📋 Setting up universal templates...")
        
        # Define source template directory (this script's location)
        script_dir = Path(__file__).parent
        source_templates_dir = script_dir / "templates"
        
        if not source_templates_dir.exists():
            print(f"  ℹ️  No source templates found, creating comprehensive templates...")
            self.create_comprehensive_templates()
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
            print("  📝 Creating comprehensive templates...")
            self.create_comprehensive_templates()
    
    def create_comprehensive_templates(self) -> None:
        """Create comprehensive templates for AI-enhanced development"""
        templates_dir = Path(".universal/templates")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create AI development workflow template
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
        
        # Create AI-assisted refactoring template
        refactoring_template = """# AI-Assisted Refactoring Template

## Pre-Refactoring Checklist
- [ ] Check project memory for previous refactoring attempts
- [ ] Use knowledge graph to understand dependencies
- [ ] Create sequential thinking plan
- [ ] Document current architecture

## Refactoring Plan
### Step 1: Analysis
- [ ] Identify code smells and technical debt
- [ ] Map dependencies and relationships
- [ ] Document current behavior

### Step 2: Planning
- [ ] Define refactoring goals
- [ ] Create step-by-step plan
- [ ] Identify risks and mitigation strategies

### Step 3: Implementation
- [ ] Create feature branch
- [ ] Implement changes incrementally
- [ ] Run tests after each change
- [ ] Document decisions

### Step 4: Validation
- [ ] Run full test suite
- [ ] Performance testing
- [ ] Code review
- [ ] Update documentation

## Memory Commands for Refactoring
- `memory-bank: "Record refactoring decision: [description]"`
- `memory-bank: "Document refactoring risk: [risk]"`
- `memory-bank: "Update refactoring progress: [status]"`

## Knowledge Graph Commands for Refactoring
- `knowledge-graph: "Show all files affected by [component]"`
- `knowledge-graph: "Find circular dependencies"`
- `knowledge-graph: "List all usages of [function/class]"`

## Sequential Thinking for Refactoring
- `sequential-thinking: "Create 6-step refactoring plan for [component]"`
- `sequential-thinking: "Generate safe refactoring code for step [N]"`
- `sequential-thinking: done [N]`
"""
        
        # Create project onboarding template
        onboarding_template = """# Project Onboarding Template

## New Developer Setup

### 1. Environment Setup
- [ ] Install required tools and dependencies
- [ ] Set up development environment
- [ ] Configure IDE/editor
- [ ] Install MCP tools

### 2. Project Understanding
- [ ] Read project documentation
- [ ] Review architecture decisions
- [ ] Understand codebase structure
- [ ] Check project memory for context

### 3. First Contribution
- [ ] Pick a simple issue/task
- [ ] Create feature branch
- [ ] Implement solution
- [ ] Write tests
- [ ] Submit pull request

## Memory Commands for Onboarding
- `memory-bank: "Record onboarding question: [question]"`
- `memory-bank: "Document learning: [insight]"`
- `memory-bank: "Update onboarding progress: [status]"`

## Knowledge Graph Commands for Onboarding
- `knowledge-graph: "Show project architecture"`
- `knowledge-graph: "Find entry points"`
- `knowledge-graph: "List main components"`

## Sequential Thinking for Onboarding
- `sequential-thinking: "Create onboarding checklist for [role]"`
- `sequential-thinking: "Generate learning path for [technology]"`

## Common Onboarding Tasks
1. **Environment Setup**: Follow QUICK_START.md
2. **Code Review**: Review recent commits and decisions
3. **Documentation**: Read project analysis and progress files
4. **First Task**: Pick a simple bug fix or documentation update
"""
        
        # Create debugging template
        debugging_template = """# AI-Enhanced Debugging Template

## Problem Analysis
- [ ] Reproduce the issue
- [ ] Check project memory for similar problems
- [ ] Use knowledge graph to understand affected components
- [ ] Create debugging plan with sequential thinking

## Debugging Process

### Step 1: Problem Definition
- [ ] Describe the issue clearly
- [ ] Identify symptoms and error messages
- [ ] Determine scope and impact

### Step 2: Investigation
- [ ] Use knowledge graph to map dependencies
- [ ] Check project memory for similar issues
- [ ] Analyze logs and error messages
- [ ] Create hypothesis

### Step 3: Testing Hypothesis
- [ ] Create minimal reproduction case
- [ ] Test hypothesis systematically
- [ ] Document findings

### Step 4: Solution Implementation
- [ ] Implement fix
- [ ] Write tests
- [ ] Document solution
- [ ] Update project memory

## Memory Commands for Debugging
- `memory-bank: "Record debugging issue: [description]"`
- `memory-bank: "Document debugging hypothesis: [hypothesis]"`
- `memory-bank: "Record debugging solution: [solution]"`

## Knowledge Graph Commands for Debugging
- `knowledge-graph: "Show components involved in [error]"`
- `knowledge-graph: "Find files that use [functionality]"`
- `knowledge-graph: "Map dependencies for [component]"`

## Sequential Thinking for Debugging
- `sequential-thinking: "Create debugging checklist for [issue]"`
- `sequential-thinking: "Generate debugging steps for [error]"`
- `sequential-thinking: "Plan debugging investigation for [problem]"`

## Common Debugging Patterns
1. **Error Analysis**: Check logs, stack traces, error messages
2. **Dependency Mapping**: Use knowledge graph to understand relationships
3. **Historical Context**: Check project memory for similar issues
4. **Systematic Testing**: Use sequential thinking for structured investigation
"""
        
        # Create feature development template
        feature_template = """# Feature Development Template

## Feature Planning

### Requirements Analysis
- [ ] Define feature requirements
- [ ] Check project memory for similar features
- [ ] Use knowledge graph to understand impact
- [ ] Create sequential thinking plan

### Architecture Design
- [ ] Design feature architecture
- [ ] Identify affected components
- [ ] Plan integration points
- [ ] Document design decisions

## Implementation Process

### Phase 1: Setup
- [ ] Create feature branch
- [ ] Set up development environment
- [ ] Create implementation plan
- [ ] Document initial approach

### Phase 2: Core Implementation
- [ ] Implement core functionality
- [ ] Write unit tests
- [ ] Use knowledge graph for dependency analysis
- [ ] Document code changes

### Phase 3: Integration
- [ ] Integrate with existing codebase
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Document integration decisions

### Phase 4: Testing & Validation
- [ ] Write comprehensive tests
- [ ] Run full test suite
- [ ] Performance testing
- [ ] Security review

### Phase 5: Documentation & Review
- [ ] Update API documentation
- [ ] Update user documentation
- [ ] Code review
- [ ] Update project memory

## Memory Commands for Features
- `memory-bank: "Record feature decision: [decision]"`
- `memory-bank: "Document feature progress: [status]"`
- `memory-bank: "Record feature lesson: [lesson]"`

## Knowledge Graph Commands for Features
- `knowledge-graph: "Show files affected by [feature]"`
- `knowledge-graph: "Find integration points for [feature]"`
- `knowledge-graph: "Map dependencies for [feature]"`

## Sequential Thinking for Features
- `sequential-thinking: "Create 8-step plan for [feature]"`
- `sequential-thinking: "Generate code for step [N]: [description]"`
- `sequential-thinking: done [N]`

## Feature Checklist
- [ ] Requirements documented
- [ ] Architecture designed
- [ ] Tests written
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Project memory updated
"""
        
        # Write all templates
        templates = {
            "ai-development-workflow.md": workflow_template,
            "ai-assisted-refactoring.md": refactoring_template,
            "project-onboarding.md": onboarding_template,
            "ai-enhanced-debugging.md": debugging_template,
            "feature-development.md": feature_template
        }
        
        for filename, content in templates.items():
            with open(templates_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)
        
        print("  ✅ Created comprehensive templates")
        print(f"     - {len(templates)} templates created")
        for filename in templates.keys():
            print(f"       • {filename}")
    
    def create_basic_templates(self) -> None:
        """Create basic templates if copying fails (legacy method)"""
        self.create_comprehensive_templates()
    
    def create_initial_memory(self) -> None:
        """Create initial project memory with real project information"""
        print("🧠 Creating initial project memory...")
        
        # Extract project goal from README
        project_goal = "[Describe your project goal]"
        if self.project_info.get("readme"):
            # Try to extract goal from README
            readme_lines = self.project_info["readme"].split('\n')
            for line in readme_lines[:20]:  # Check first 20 lines
                if any(keyword in line.lower() for keyword in ['goal', 'purpose', 'objective', 'aim']):
                    project_goal = line.strip()
                    break
        
        # Create architecture description
        arch_desc = f"{self.project_info.get('language', 'Unknown')} project using {self.project_info.get('framework', 'Unknown')} framework"
        
        # Create project structure summary
        structure = self.project_info.get("structure", {})
        code_files = len(structure.get("code_files", []))
        test_files = len(structure.get("test_files", []))
        doc_files = len(structure.get("doc_files", []))
        
        progress_content = f"""# {self.project_name} - Project Progress & Decisions

## Project Overview
**Project**: {self.project_name}  
**Type**: {self.project_info.get('type', 'Unknown')}  
**Language**: {self.project_info.get('language', 'Unknown')}  
**Framework**: {self.project_info.get('framework', 'Unknown')}  
**Branch**: main  
**Goal**: {project_goal}  
**Architecture**: {arch_desc}

## Project Analysis Summary
- **Code Files**: {code_files} files
- **Test Files**: {test_files} files  
- **Documentation**: {doc_files} files
- **Dependencies**: {len(self.project_info.get('dependencies', []))} packages
- **Entry Points**: {', '.join(self.project_info.get('entry_points', []))}

## Recent Decisions & Changes

### {self.get_current_date()}: Project Initialization & Analysis
- **Decision**: Set up AI-enhanced development environment with project analysis
- **Rationale**: Improve productivity with MCP tools and AI assistance, leveraging existing project context
- **Changes**: 
  - Created .universal directory structure
  - Configured MCP tools (memory-bank, knowledge-graph, docs-provider, sequential-thinking)
  - Set up Cursor AI rules
  - Initialized memory structure
  - Analyzed existing project structure and dependencies
  - Extracted project metadata and documentation

## Architecture Decisions

### AI-Native Development Workflow
- **Memory-First**: Always check project history before decisions
- **Dependency Analysis**: Use knowledge graph for relationship queries
- **Automated Documentation**: Use docs-provider for all doc updates
- **Sequential Planning**: Use sequential-thinking for complex tasks
- **Refactoring Safety**: AI-assisted refactoring with templates

### Project Structure Analysis
```
{self.project_name}/
├── .universal/          # AI development environment
│   ├── rules/          # Cursor AI rules
│   ├── templates/      # Universal templates
│   ├── mcp/           # MCP tool configurations
│   ├── memory/        # Project memory and context
│   └── extensions/    # Future extensions

Code Structure:
├── Entry Points: {', '.join(self.project_info.get('entry_points', ['None found']))}
├── Configuration: {len(self.project_info.get('config_files', []))} files
├── Tests: {test_files} files
└── Documentation: {doc_files} files
```

### Key Dependencies
{self.format_dependencies()}

### Configuration Files
{self.format_config_files()}

## Current Status
- ✅ Universal system setup complete
- ✅ MCP tools configured
- ✅ Cursor rules integrated
- ✅ Memory structure initialized
- ✅ Project analysis complete
- 🔄 Ready for development

## Next Steps
1. Review project analysis and architecture decisions
2. Set up development environment with identified dependencies
3. Begin feature development with AI assistance
4. Use knowledge graph to understand code relationships

## Lessons Learned
- AI-native workflows require careful rule design
- Memory-first development prevents decision conflicts
- MCP tools provide excellent context preservation
- Project analysis reveals hidden dependencies and patterns

@progress @decisions @architecture @setup @analysis
"""
        
        with open(".universal/memory/main/progress.md", "w", encoding="utf-8") as f:
            f.write(progress_content)
        
        print("  ✅ Created .universal/memory/main/progress.md")
    
    def format_dependencies(self) -> str:
        """Format dependencies for display"""
        deps = self.project_info.get("dependencies", [])
        if not deps:
            return "- No dependencies found"
        
        # Group by type if possible
        if self.project_info.get("type") == "python":
            return "\n".join([f"- {dep}" for dep in deps[:10]]) + ("\n- ... (and more)" if len(deps) > 10 else "")
        elif self.project_info.get("type") == "nodejs":
            return "\n".join([f"- {dep}" for dep in deps[:10]]) + ("\n- ... (and more)" if len(deps) > 10 else "")
        else:
            return "\n".join([f"- {dep}" for dep in deps])
    
    def format_config_files(self) -> str:
        """Format configuration files for display"""
        config_files = self.project_info.get("config_files", [])
        if not config_files:
            return "- No configuration files found"
        
        return "\n".join([f"- {f}" for f in config_files[:5]]) + ("\n- ... (and more)" if len(config_files) > 5 else "")
    
    def create_project_analysis_report(self) -> None:
        """Create detailed project analysis report"""
        print("📊 Creating project analysis report...")
        
        report_content = f"""# {self.project_name} - Project Analysis Report

## Executive Summary
This report provides a comprehensive analysis of the {self.project_name} project structure, dependencies, and architecture patterns.

## Project Metadata
- **Name**: {self.project_name}
- **Type**: {self.project_info.get('type', 'Unknown')}
- **Language**: {self.project_info.get('language', 'Unknown')}
- **Framework**: {self.project_info.get('framework', 'Unknown')}
- **Analysis Date**: {self.get_current_date()}

## File Structure Analysis

### Code Files ({len(self.project_info.get('structure', {}).get('code_files', []))})
{self.format_file_list(self.project_info.get('structure', {}).get('code_files', []))}

### Test Files ({len(self.project_info.get('structure', {}).get('test_files', []))})
{self.format_file_list(self.project_info.get('structure', {}).get('test_files', []))}

### Documentation Files ({len(self.project_info.get('structure', {}).get('doc_files', []))})
{self.format_file_list(self.project_info.get('structure', {}).get('doc_files', []))}

### Configuration Files ({len(self.project_info.get('config_files', []))})
{self.format_file_list(self.project_info.get('config_files', []))}

## Dependencies Analysis
{self.format_dependencies()}

## Entry Points
{self.format_entry_points()}

## Recommendations

### For AI-Enhanced Development
1. **Use knowledge graph** to understand code relationships
2. **Leverage memory bank** for architectural decisions
3. **Apply sequential thinking** for complex features
4. **Document with docs-provider** for consistency

### For Project Maintenance
1. **Regular dependency updates** - {len(self.project_info.get('dependencies', []))} packages to maintain
2. **Test coverage** - {len(self.project_info.get('structure', {}).get('test_files', []))} test files identified
3. **Documentation** - {len(self.project_info.get('structure', {}).get('doc_files', []))} documentation files

## Architecture Patterns Detected
- **Project Type**: {self.project_info.get('type', 'Unknown')}
- **Framework**: {self.project_info.get('framework', 'Unknown')}
- **Entry Points**: {len(self.project_info.get('entry_points', []))} identified
- **Configuration**: {len(self.project_info.get('config_files', []))} config files

---
*Generated by Universal AI Development Environment Setup*
"""
        
        with open(".universal/memory/main/project-analysis.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        print("  ✅ Created .universal/memory/main/project-analysis.md")
    
    def format_file_list(self, files: List[str]) -> str:
        """Format file list for display"""
        if not files:
            return "- No files found"
        
        # Group by directory
        by_dir = {}
        for file in files:
            dir_name = str(Path(file).parent)
            if dir_name == ".":
                dir_name = "root"
            if dir_name not in by_dir:
                by_dir[dir_name] = []
            by_dir[dir_name].append(Path(file).name)
        
        result = []
        for dir_name, file_list in sorted(by_dir.items()):
            if dir_name == "root":
                result.append("**Root Directory:**")
            else:
                result.append(f"**{dir_name}/:**")
            for file_name in sorted(file_list)[:5]:  # Show first 5 files per directory
                result.append(f"  - {file_name}")
            if len(file_list) > 5:
                result.append(f"  - ... (and {len(file_list) - 5} more)")
        
        return "\n".join(result)
    
    def format_entry_points(self) -> str:
        """Format entry points for display"""
        entry_points = self.project_info.get("entry_points", [])
        if not entry_points:
            return "- No entry points identified"
        
        return "\n".join([f"- {ep}" for ep in entry_points])
    
    def create_quick_start_guide(self) -> None:
        """Create quick start guide for the project"""
        print("📖 Creating quick start guide...")
        
        # Customize guide based on project type
        setup_commands = self.get_setup_commands()
        
        guide_content = f"""# {self.project_name} - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js (for MCP tools)
- {self.project_info.get('language', 'Python')} {self.get_language_version()}
- Git

### Initial Setup
```bash
# Install MCP tools (Real tools that exist)
npm install -g @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-postgres @modelcontextprotocol/server-brave-search @modelcontextprotocol/server-github

# Install Python MCP tools
pip install mcp-playwright mcp --user

{setup_commands}

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
1. Check sequential thinking for similar problems
2. Use postgres for dependency analysis
3. Create debugging plan with sequential-thinking
4. Document solutions for future reference

---

**Happy AI-enhanced coding! 🚀**
"""
        
        with open("QUICK_START.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        print("  ✅ Created QUICK_START.md")
    
    def get_setup_commands(self) -> str:
        """Get project-specific setup commands"""
        project_type = self.project_info.get("type", "")
        
        if project_type == "python":
            return """# Install Python dependencies
pip install -r requirements.txt

# Or if using pip:
pip install -e ."""
        elif project_type == "nodejs":
            return """# Install Node.js dependencies
npm install

# Or if using yarn:
yarn install"""
        elif project_type == "rust":
            return """# Install Rust dependencies
cargo build"""
        elif project_type == "go":
            return """# Install Go dependencies
go mod download"""
        else:
            return """# Install project dependencies
# (Check project documentation for specific setup instructions)"""
    
    def get_language_version(self) -> str:
        """Get language version requirement"""
        project_type = self.project_info.get("type", "")
        
        if project_type == "python":
            return "3.8+"
        elif project_type == "nodejs":
            return "16+"
        elif project_type == "rust":
            return "1.70+"
        elif project_type == "go":
            return "1.19+"
        else:
            return ""
    
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
            # First analyze the project
            self.analyze_project()
            
            # Then set up the universal system
            self.setup_directory_structure()
            self.create_cursor_rules()
            self.create_mcp_config()
            self.copy_universal_templates()
            self.create_initial_memory()
            self.create_project_analysis_report()
            self.create_quick_start_guide()
            self.create_gitignore_updates()
            
            print("\n" + "=" * 60)
            print("✅ Setup complete! Your AI-enhanced development environment is ready.")
            print(f"\n📊 Project Analysis Summary:")
            print(f"   - Type: {self.project_info.get('type', 'Unknown')}")
            print(f"   - Language: {self.project_info.get('language', 'Unknown')}")
            print(f"   - Framework: {self.project_info.get('framework', 'Unknown')}")
            print(f"   - Code Files: {len(self.project_info.get('structure', {}).get('code_files', []))}")
            print(f"   - Dependencies: {len(self.project_info.get('dependencies', []))}")
            print(f"   - Entry Points: {len(self.project_info.get('entry_points', []))}")
            print("\n📖 Next steps:")
            print("1. Read QUICK_START.md for usage instructions")
            print("2. Review .universal/memory/main/project-analysis.md for detailed analysis")
            print("3. Install MCP tools: npm install -g @modelcontextprotocol/server-memory-bank @modelcontextprotocol/server-knowledge-graph @modelcontextprotocol/server-docs-provider @modelcontextprotocol/server-sequential-thinking")
            print("4. Initialize git: git init && git add . && git commit -m 'Initial setup'")
            print("5. Start developing with AI assistance!")
            
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