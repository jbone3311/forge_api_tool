# AI-Enhanced Development Workflow Template

## 🚀 Quick Start Commands

### Initialize New Feature
```bash
# Create feature branch
git checkout -b feature/[description]

# Initialize memory for this branch
memory-bank: create_project "feature-[description]"

# Start sequential thinking plan
sequential-thinking: "Create 5-step plan for [feature description]"
```

### Daily Development Routine
```bash
# Check project context
memory-bank: get_file_content project="main" path="progress.md"

# Analyze dependencies for changes
knowledge-graph: "Show all files affected by [component]"

# Plan next steps
sequential-thinking: "Review current progress and plan next iteration"
```

### Complete Feature
```bash
# Update memory with decisions
memory-bank: "Document final decisions and lessons learned for [feature]"

# Generate documentation
docs-provider: "Generate API documentation for [new feature]"

# Create PR description
sequential-thinking: "Generate comprehensive PR description with context"
```

---

## 🧠 Memory-First Development

### Before Every Decision
1. **Check Project History**
   ```
   memory-bank: get_file_content project="main" path="progress.md"
   ```

2. **Review Recent Decisions**
   ```
   memory-bank: "Show recent architectural decisions for [component]"
   ```

3. **Document New Decision**
   ```
   memory-bank: "Record decision: [description] with rationale: [reasoning]"
   ```

### Memory Bank Operations
```bash
# Project management
memory-bank: list_projects
memory-bank: create_project "project-name"

# File operations
memory-bank: update_file_content project="main" path="decisions/feature-x.md" content="..."
memory-bank: get_file_content project="main" path="progress.md"

# Decision tracking
memory-bank: "Document ADR: Why we chose [approach] over [alternative]"
memory-bank: "Record rollback plan for [feature]"
memory-bank: "Store baseline performance metrics before [change]"
```

---

## 🔍 Dependency Analysis

### Before Making Changes
1. **Impact Analysis**
   ```
   knowledge-graph: "Show all files that import [module]"
   knowledge-graph: "Find circular dependencies in [component]"
   ```

2. **Dependency Mapping**
   ```
   knowledge-graph: "List all components that use [functionality]"
   knowledge-graph: "Show dependency chain for [feature]"
   ```

3. **Complexity Analysis**
   ```
   knowledge-graph: "Compare dependency complexity before/after [change]"
   knowledge-graph: "Show coupling metrics for [module]"
   ```

### Knowledge Graph Operations
```bash
# Entity management
knowledge-graph: create_entities [{"name": "NewComponent", "entityType": "Component"}]
knowledge-graph: create_relations [{"from": "file1.py", "to": "file2.py", "relationType": "imports"}]

# Search and analysis
knowledge-graph: search_nodes query="authentication"
knowledge-graph: open_nodes names=["auth.py", "middleware.py"]

# Common queries
knowledge-graph: "Show all API endpoints and their dependencies"
knowledge-graph: "Find unused imports in [directory]"
knowledge-graph: "Show test coverage gaps for [component]"
```

---

## 📋 Sequential Planning

### Feature Development
1. **Create Plan**
   ```
   sequential-thinking: "Create 6-step plan to implement [feature]"
   ```

2. **Execute Steps**
   ```
   sequential-thinking: "Generate code for step 1: [description]"
   # Accept/tweak generated code
   git add . && git commit -m "Step 1: [description]"
   sequential-thinking: done 1
   ```

3. **Track Progress**
   ```
   sequential-thinking: "Review completed steps and plan next iteration"
   ```

### Debugging Workflow
1. **Analyze Problem**
   ```
   sequential-thinking: "Create debugging checklist for [issue]"
   ```

2. **Investigate**
   ```
   knowledge-graph: "Show all components involved in [error]"
   memory-bank: "Check if this issue was encountered before"
   ```

3. **Solve & Document**
   ```
   sequential-thinking: "Generate solution steps for [issue]"
   memory-bank: "Document solution for [issue] for future reference"
   ```

### Sequential Thinking Operations
```bash
# Planning
sequential-thinking: "Plan refactor of [component] into [architecture]"
sequential-thinking: "Create testing strategy for [feature]"

# Implementation
sequential-thinking: "Generate Flask route code for [endpoint]"
sequential-thinking: "Create pytest fixtures for [component]"

# Progress tracking
sequential-thinking: done [step_number]
sequential-thinking: "Review progress and adjust plan"
```

---

## 📚 Documentation Automation

### API Documentation
```bash
# Generate API docs
docs-provider: "Generate OpenAPI spec for [endpoint]"
docs-provider: "Create usage examples for [API]"

# Update existing docs
docs-provider: "Update README with new [feature] information"
docs-provider: "Generate CHANGELOG entry for [version]"
```

### Code Documentation
```bash
# Function documentation
docs-provider: "Generate docstring for [function] with examples"
docs-provider: "Create class documentation for [class]"

# Architecture documentation
docs-provider: "Document the [component] architecture and design decisions"
docs-provider: "Create deployment guide for [environment]"
```

### Docs Provider Operations
```bash
# Documentation queries
docs-provider: "How to structure [pattern] in [language]?"
docs-provider: "Best practices for [technology] integration?"

# Generation
docs-provider: "Generate API documentation for [new feature]"
docs-provider: "Update README with new project structure"
docs-provider: "Create troubleshooting guide for [common issue]"
```

---

## 🔧 Common Development Scenarios

### Scenario 1: Adding New API Endpoint
```bash
# 1. Check context
memory-bank: "Show existing API patterns and conventions"

# 2. Analyze dependencies
knowledge-graph: "Show all files that handle API routing"

# 3. Plan implementation
sequential-thinking: "Create 4-step plan for new [endpoint] endpoint"

# 4. Generate code
sequential-thinking: "Generate Flask route code for [endpoint] with validation"

# 5. Update docs
docs-provider: "Generate API documentation for [endpoint]"

# 6. Document decision
memory-bank: "Record API design decision for [endpoint]"
```

### Scenario 2: Refactoring Component
```bash
# 1. Safety check
git checkout -b refactor/[component]
pytest  # Ensure baseline tests pass

# 2. Load refactor template
docs-provider: "Get ai-assisted-refactoring.md template"

# 3. Analyze impact
knowledge-graph: "Show all dependencies of [component]"

# 4. Plan refactor
sequential-thinking: "Create 5-step refactor plan for [component]"

# 5. Execute safely
sequential-thinking: "Generate code for step 1: [description]"
# Test each step before proceeding

# 6. Document changes
memory-bank: "Document refactor decisions and lessons learned"
```

### Scenario 3: Debugging Production Issue
```bash
# 1. Gather context
memory-bank: "Check if similar issues occurred before"
knowledge-graph: "Show all components involved in [error]"

# 2. Create debugging plan
sequential-thinking: "Create systematic debugging checklist for [issue]"

# 3. Investigate
knowledge-graph: "Show dependency chain for [failing component]"
memory-bank: "Check recent changes that might affect [component]"

# 4. Solve and document
sequential-thinking: "Generate solution steps for [issue]"
memory-bank: "Document solution and prevention measures for [issue]"
```

---

## 🎯 Quality Assurance

### Before Committing
```bash
# 1. Check memory for context
memory-bank: "Verify this change aligns with project decisions"

# 2. Analyze dependencies
knowledge-graph: "Verify no circular dependencies introduced"

# 3. Generate tests
sequential-thinking: "Generate test cases for [new code]"

# 4. Update documentation
docs-provider: "Update relevant documentation for [changes]"

# 5. Document decision
memory-bank: "Record final implementation decision for [feature]"
```

### Code Review Checklist
- [ ] Memory bank consulted for context
- [ ] Dependencies analyzed with knowledge graph
- [ ] Tests generated and passing
- [ ] Documentation updated
- [ ] Decisions recorded in memory bank
- [ ] No circular dependencies introduced
- [ ] Performance impact considered

---

## 🚀 Advanced Workflows

### Multi-Step Feature Development
```bash
# Phase 1: Planning
sequential-thinking: "Create comprehensive plan for [major feature]"
memory-bank: "Document high-level architecture decisions"

# Phase 2: Implementation
for step in plan:
    sequential-thinking: "Generate code for step [N]: [description]"
    knowledge-graph: "Verify dependencies for step [N]"
    git commit -m "Step [N]: [description]"
    sequential-thinking: done [N]

# Phase 3: Integration
knowledge-graph: "Show integration points for [feature]"
sequential-thinking: "Generate integration tests"

# Phase 4: Documentation
docs-provider: "Generate comprehensive documentation for [feature]"
memory-bank: "Document lessons learned and future improvements"
```

### Performance Optimization
```bash
# 1. Baseline measurement
memory-bank: "Store baseline performance metrics"

# 2. Identify bottlenecks
knowledge-graph: "Show performance-critical components"
sequential-thinking: "Create optimization strategy"

# 3. Implement optimizations
sequential-thinking: "Generate optimized code for [component]"

# 4. Measure improvement
memory-bank: "Compare performance before/after optimization"

# 5. Document decisions
memory-bank: "Document optimization decisions and trade-offs"
```

---

## 📊 Metrics & Tracking

### Development Metrics
- **Memory Usage**: Track how often memory bank is consulted
- **Dependency Analysis**: Monitor knowledge graph query frequency
- **Planning Efficiency**: Measure sequential thinking step completion
- **Documentation Coverage**: Track docs-provider usage

### Quality Metrics
- **Decision Consistency**: Check memory bank for conflicting decisions
- **Dependency Health**: Monitor knowledge graph for complexity trends
- **Documentation Freshness**: Track docs-provider update frequency

---

## 🎁 Benefits

1. **🧠 Cognitive Offloading**: AI handles complexity, you handle decisions
2. **📚 Knowledge Preservation**: Everything documented automatically
3. **🔄 Iterative Safety**: Small steps, easy recovery
4. **🎯 Goal-Oriented**: Each step has clear deliverable
5. **🤖 AI-Native**: Uses LLMs for their strengths (generation, analysis)
6. **📊 Data-Driven**: Metrics guide decisions
7. **🔍 Transparent**: Full audit trail of changes and reasoning

---

**This workflow template provides a comprehensive framework for AI-enhanced solo development, integrating all MCP tools for maximum productivity and code quality.** 