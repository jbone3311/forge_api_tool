# AI-Assisted Refactoring Framework Template

A systematic, safe, and AI-powered approach to refactoring codebases using MCP tools (memory-bank, knowledge-graph, sequential-thinking).

## 🎯 Core Principles

- **Safety-First**: Branch isolation, baseline tests, incremental commits
- **AI-Native**: Use LLMs for generation, analysis, and documentation
- **Cognitive Offloading**: AI handles complexity, you handle decisions
- **Knowledge Preservation**: Everything documented automatically
- **Iterative Safety**: Small steps, easy recovery

---

## 📋 Pre-Refactor Setup

### 0. Preparation (do once)

| Why | What to do |
|-----|------------|
| Safer refactor | Create a branch: `git checkout -b refactor/[description]` |
| Baseline tests | Run tests: `pytest` (ensure everything is green) |
| Knowledge mapping | Populate knowledge graph with current codebase |
| Auto-documentation | Ensure git hooks update `.cursorMEM` automatically |

### Pre-Step Validation Script
```bash
#!/bin/bash
# validate_step.sh
echo "🔍 Running pre-step validation..."
pytest --quiet && echo "✅ Tests pass" || exit 1
git status --porcelain | wc -l | grep -q "^0$" && echo "✅ Clean working tree" || exit 1
echo "📊 Current metrics:"
knowledge-graph: "Show dependency complexity metrics"
```

---

## 🔄 Refactoring Steps Template

### Step N: [Description]

**Goal**: [What you want to achieve]

**Impact Analysis**:
```
▶ knowledge-graph: "Show all files affected by [change]"
▶ memory-bank: "Document design decision for [approach]"
```

**Implementation**:
```
▶ sequential-thinking: "Generate code for [specific change] - provide stubs and updated imports"
```

**Validation**:
```bash
# Test the change
pytest [relevant_test_files]
# Quick smoke test
python -m app --test-mode
```

**Commit**:
```bash
git add .
git commit -m "Step N: [description]"
```

**Mark Complete**:
```
▶ sequential-thinking: done N
```

---

## 🔧 MCP Tools Deep Dive

### Memory Bank (`mcp-memory-bank`)
**Purpose**: Document decisions, store templates, track progress

**Key Operations**:
```bash
# Project management
▶ memory-bank: list_projects
▶ memory-bank: create_project "refactor-decisions"

# File operations
▶ memory-bank: update_file_content project="main" path="adr/step-1-blueprints.md" content="..."
▶ memory-bank: get_file_content project="main" path="progress.md"

# Common use cases:
▶ memory-bank: "Document ADR: Why Flask blueprints over monolithic routes"
▶ memory-bank: "Record rollback plan for Step 3 driver factory"
▶ memory-bank: "Store baseline performance metrics before refactor"
▶ memory-bank: "Update progress: completed step 2, effects registry working"
```

### Knowledge Graph (`mcp-knowledge-graph`)
**Purpose**: Track code relationships, analyze dependencies, impact analysis

**Key Operations**:
```bash
# Entity management
▶ knowledge-graph: create_entities [{"name": "FlaskApp", "entityType": "Component", "observations": ["Main application class"]}]
▶ knowledge-graph: create_relations [{"from": "app.py", "to": "effects/__init__.py", "relationType": "imports"}]

# Search and analysis
▶ knowledge-graph: search_nodes query="Flask"
▶ knowledge-graph: open_nodes names=["app.py", "effects.py"]

# Common refactor queries:
▶ knowledge-graph: "Show all files that import app.py"
▶ knowledge-graph: "Find circular dependencies in current codebase"
▶ knowledge-graph: "List all components that use LED drivers"
▶ knowledge-graph: "Compare dependency complexity before/after refactor"
```

### Sequential Thinking (`mcp-sequential-thinking`)
**Purpose**: Plan, generate code, track refactor steps

**Key Operations**:
```bash
# Planning phase
▶ sequential-thinking: "Create 6-step plan to refactor app.py into modular blueprints"
▶ sequential-thinking: "Analyze impact of splitting effects into plugin registry"

# Implementation phase
▶ sequential-thinking: "Generate Flask blueprint code for API routes with proper imports"
▶ sequential-thinking: "Create driver factory pattern with environment variable selection"

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
▶ docs-provider: "How to structure Flask blueprints with WebSocket support?"
▶ docs-provider: "Best practices for Python plugin architecture?"

# During refactor:
▶ docs-provider: "Generate API documentation for new driver factory"
▶ docs-provider: "Update README with new project structure"
```

### MCP Integration Patterns

**1. Cross-Tool Workflows**:
```bash
# Planning → Implementation → Documentation
▶ sequential-thinking: "Plan step 1: split app.py"
▶ knowledge-graph: "Show current dependencies of app.py"
▶ sequential-thinking: "Generate blueprint code based on dependencies"
▶ memory-bank: "Document why we chose this blueprint structure"
```

**2. Validation Chains**:
```bash
# Before each step
▶ knowledge-graph: "Verify no circular dependencies"
▶ memory-bank: "Record current test coverage baseline"

# After each step  
▶ knowledge-graph: "Show what changed in dependency graph"
▶ sequential-thinking: "Generate tests for new boundaries"
▶ memory-bank: "Update progress and document any issues"
```

**3. Decision Support**:
```bash
# When facing choices
▶ docs-provider: "Compare Flask-SocketIO blueprint vs. separate app approaches"
▶ memory-bank: "Record pros/cons of each approach"
▶ sequential-thinking: "Recommend best option based on our constraints"
▶ knowledge-graph: "Show impact of chosen approach on existing code"
```

---

## 🛠 Common Refactoring Patterns

### 1. Split Monolithic File

**Example**: Breaking up `app.py` into modules

```
▶ sequential-thinking: "Generate Flask blueprints (api, sockets, ui) and rewrite app.py with create_app() factory"
```

**Target Structure**:
```
your-repo/
├─ api/           ← Flask blueprint: JSON routes
│  ├─ __init__.py
│  └─ routes.py
├─ sockets/       ← Flask-SocketIO blueprint
│  ├─ __init__.py
│  └─ events.py
├─ ui/            ← HTML templates & static files
│  ├─ __init__.py
│  └─ views.py
├─ app.py         ← now just "create_app()" that registers blueprints
```

### 2. Driver/Factory Pattern

**Goal**: Abstract hardware vs. mock implementations

```
▶ memory-bank: "Add design note describing driver_factory pattern (env var LED_DRIVER)"
▶ sequential-thinking: "Generate code for driver_factory.py and update imports"
```

**Target Structure**:
```
drivers/
├─ __init__.py
├─ hardware.py
├─ mock.py
└─ factory.py
```

### 3. Plugin/Registry System

**Goal**: Extensible effect system

```python
# Pattern:
EFFECTS = {}
def register(name):
    def wrapper(cls):
        EFFECTS[name] = cls
        return cls
    return wrapper

@register("fade")
class Fade(Effect):
    ...
```

```
▶ sequential-thinking: "Refactor effects/ with register() decorator – generate updated code stubs"
```

### 4. Configuration/Validation Layer

**Goal**: JSON schema validation for data files

```
▶ memory-bank: "Document JSON schema for scene files – fields, types, ranges"
▶ sequential-thinking: "Generate scene_io.py with load_scene(), save_scene(), and validate(schema)"
```

### 5. Test Infrastructure

**Focus**: Test new boundaries you just carved out

```
tests/
├─ test_effects.py   # registry returns correct class
├─ test_driver.py    # factory selects mock vs hardware
├─ test_scene.py     # invalid JSON raises ValidationError
```

```
▶ sequential-thinking: "Generate pytest stubs for effects, driver factory, scene validation"
```

### 6. Documentation & Naming Sweep

**Goal**: Consistent naming and comprehensive docs

```
▶ memory-bank: "Add note: adopted snake_case for modules, CamelCase for classes"
```

Use Cursor's multi-file rename: `Shift ⌘ R` (Mac) or `Shift Alt R` (Win)

---

## 📊 Enhanced Process Features

### A. Architecture Decision Records (ADRs)
```
▶ memory-bank: "Record ADR: Why we chose Flask blueprints over FastAPI routers"
▶ memory-bank: "Document rollback procedure for Step 3 if plugin registry breaks"
```

### B. Dependency Impact Analysis
```
▶ knowledge-graph: "Compare dependency complexity before/after refactor"
▶ knowledge-graph: "Verify no circular dependencies after Step 2"
▶ knowledge-graph: "Show import chain depth before/after"
```

### C. Performance Monitoring
```
▶ memory-bank: "Baseline performance metrics before refactor"
▶ memory-bank: "Compare performance impact after refactor"
```

### D. Test-Driven Validation
```bash
# Before each step:
pytest --cov=. --cov-report=term-missing
# Ensure coverage doesn't drop

# After each step:
▶ sequential-thinking: "Generate integration test for [new component]"
```

---

## 🎯 Finishing the Refactor

### 7. Final Validation

1. **Full System Test**:
   ```bash
   # Run the full app locally
   python app.py
   # Click through UI, watch logs
   ```

2. **Integration Verification**:
   ```
   ▶ knowledge-graph: "Generate final dependency map"
   ▶ memory-bank: "Document all changes made during refactor"
   ```

3. **Documentation Update**:
   ```
   ▶ docs-provider: "Regenerate docs and update CHANGELOG for v[X.Y.Z]"
   ```

4. **Create PR**:
   - Include knowledge graph dependency comparison
   - Reference memory bank design decisions
   - Paste auto-generated documentation

5. **Cleanup**:
   ```bash
   git push origin refactor/[description]
   # Create PR, merge, delete branch
   # Diary & checklist remain as historical record
   ```

---

## 📝 Post-Refactor Review

### Questions to Ask:
1. **Complexity**: Did we reduce cognitive load?
2. **Testability**: Are new boundaries easier to test?
3. **Maintainability**: Will this be easier to extend?
4. **Performance**: Any regression in speed/memory?
5. **Documentation**: Is the new architecture clear?

### Metrics to Track:
```
▶ knowledge-graph: "Count total dependencies before/after"
▶ knowledge-graph: "Show coupling metrics improvement"
▶ memory-bank: "List all design decisions made"
```

---

## 🚀 Usage Examples

### Starting a Refactor:
```bash
git checkout -b refactor/modular-split
▶ sequential-thinking: "Create 6-step plan to refactor monolithic app.py into modular Flask blueprints"
```

### Each Step:
```
▶ sequential-thinking: "Generate code for step 1 – create Flask blueprints (api, sockets, ui) and rewrite app.py with create_app() factory"
# Accept/tweak generated code
git add . && git commit -m "Step 1: split app.py into blueprints"
▶ sequential-thinking: done 1
```

### Verification:
```
▶ knowledge-graph: "Show what changed in dependency graph"
▶ memory-bank: "Document why we chose this approach"
```

---

## 🎁 Benefits of This Framework

1. **🧠 Cognitive Offloading**: AI handles complexity, you handle decisions
2. **📚 Knowledge Preservation**: Everything documented automatically  
3. **🔄 Iterative Safety**: Small steps, easy recovery
4. **🎯 Goal-Oriented**: Each step has clear deliverable
5. **🤖 AI-Native**: Uses LLMs for their strengths (generation, analysis)
6. **📊 Data-Driven**: Metrics guide decisions
7. **🔍 Transparent**: Full audit trail of changes and reasoning

---

## 📋 Checklist Template

- [ ] Branch created
- [ ] Baseline tests pass
- [ ] Knowledge graph populated
- [ ] Step 1: [Description]
- [ ] Step 2: [Description]
- [ ] Step 3: [Description]
- [ ] Step 4: [Description]
- [ ] Step 5: [Description]
- [ ] Step 6: [Description]
- [ ] Final validation
- [ ] Documentation updated
- [ ] PR created and merged

---

**This framework is production-ready and can be adapted for any refactoring project. The key is consistent use of AI tools for planning, generation, and documentation while maintaining engineering best practices.** 