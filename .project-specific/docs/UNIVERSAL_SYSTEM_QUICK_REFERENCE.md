# Universal AI Development System - Quick Reference

## 🚀 Daily Commands

### Start New Feature
```bash
# Check context
memory-bank: get_file_content project="main" path="progress.md"

# Create branch
git checkout -b feature/[description]

# Plan implementation
sequential-thinking: "Create 5-step plan for [feature]"
```

### Analyze Dependencies
```bash
# Show affected files
knowledge-graph: "Show all files that import [module]"

# Find circular dependencies
knowledge-graph: "Find circular dependencies in [component]"

# Show usage
knowledge-graph: "List all components that use [functionality]"
```

### Generate Code
```bash
# Generate implementation
sequential-thinking: "Generate code for step 1: [description]"

# Generate tests
sequential-thinking: "Generate pytest test cases for [component]"

# Generate docs
docs-provider: "Generate API documentation for [endpoint]"
```

### Document Decisions
```bash
# Record decision
memory-bank: "Record decision: [description] with rationale: [reasoning]"

# Update progress
memory-bank: "Update progress: completed [task]"

# Store lessons learned
memory-bank: "Document lessons learned for [feature]"
```

---

## 🧠 Memory-First Development

### Before Every Decision
1. `memory-bank: get_file_content project="main" path="progress.md"`
2. `memory-bank: "Show recent architectural decisions for [component]"`
3. `memory-bank: "Record decision: [description] with rationale: [reasoning]"`

### Memory Operations
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

### Impact Analysis
```bash
knowledge-graph: "Show all files affected by [change]"
knowledge-graph: "Find circular dependencies in [component]"
knowledge-graph: "Show dependency chain for [feature]"
```

### Code Relationships
```bash
knowledge-graph: "Show all files that import [module]"
knowledge-graph: "List all components that use [functionality]"
knowledge-graph: "Compare dependency complexity before/after [change]"
```

### Graph Operations
```bash
knowledge-graph: create_entities [{"name": "NewComponent", "entityType": "Component"}]
knowledge-graph: create_relations [{"from": "file1.py", "to": "file2.py", "relationType": "imports"}]
knowledge-graph: search_nodes query="authentication"
```

---

## 📋 Sequential Planning

### Feature Development
```bash
# Create plan
sequential-thinking: "Create 6-step plan to implement [feature]"

# Execute steps
sequential-thinking: "Generate code for step 1: [description]"
git add . && git commit -m "Step 1: [description]"
sequential-thinking: done 1

# Track progress
sequential-thinking: "Review completed steps and plan next iteration"
```

### Debugging
```bash
# Analyze problem
sequential-thinking: "Create debugging checklist for [issue]"

# Investigate
knowledge-graph: "Show all components involved in [error]"
memory-bank: "Check if this issue occurred before"

# Solve & document
sequential-thinking: "Generate solution steps for [issue]"
memory-bank: "Document solution for [issue]"
```

### Planning Operations
```bash
sequential-thinking: "Plan refactor of [component] into [architecture]"
sequential-thinking: "Create testing strategy for [feature]"
sequential-thinking: "Generate Flask route code for [endpoint]"
sequential-thinking: "Create pytest fixtures for [component]"
```

---

## 📚 Documentation Automation

### API Documentation
```bash
docs-provider: "Generate OpenAPI spec for [endpoint]"
docs-provider: "Create usage examples for [API]"
docs-provider: "Update README with new [feature] information"
docs-provider: "Generate CHANGELOG entry for [version]"
```

### Code Documentation
```bash
docs-provider: "Generate docstring for [function] with examples"
docs-provider: "Create class documentation for [class]"
docs-provider: "Document the [component] architecture and design decisions"
docs-provider: "Create deployment guide for [environment]"
```

### Documentation Queries
```bash
docs-provider: "How to structure [pattern] in [language]?"
docs-provider: "Best practices for [technology] integration?"
docs-provider: "Generate API documentation for [new feature]"
docs-provider: "Update README with new project structure"
```

---

## 🧪 AI-Enhanced Testing

### Test Generation
```bash
# Analyze component
knowledge-graph: "Show all dependencies of [component]"

# Generate test plan
sequential-thinking: "Create comprehensive test plan for [component]"

# Generate test code
sequential-thinking: "Generate pytest test cases for [component]"

# Document approach
memory-bank: "Record testing approach for [component]"
```

### Test Execution
```bash
# Run tests
pytest --cov=. --cov-report=term-missing

# Analyze coverage
knowledge-graph: "Show test coverage gaps for [component]"
sequential-thinking: "Generate tests for uncovered code paths"

# Update docs
docs-provider: "Generate test documentation with coverage reports"
```

### Test Quality
```bash
# Performance
pytest --durations=10  # Show slowest tests
pytest --lf  # Run last failed tests

# Analysis
knowledge-graph: "Show test complexity metrics"
sequential-thinking: "Identify and simplify complex test cases"
```

---

## 🔄 AI-Assisted Refactoring

### Pre-Refactor
```bash
# Safety check
git checkout -b refactor/[component]
pytest  # Ensure baseline tests pass

# Load template
docs-provider: "Get ai-assisted-refactoring.md template"

# Analyze impact
knowledge-graph: "Show all dependencies of [component]"

# Plan refactor
sequential-thinking: "Create 5-step refactor plan for [component]"
```

### During Refactor
```bash
# Execute safely
sequential-thinking: "Generate code for step 1: [description]"
# Test each step before proceeding

# Validate changes
knowledge-graph: "Verify no circular dependencies introduced"
pytest  # Ensure tests still pass
```

### Post-Refactor
```bash
# Document changes
memory-bank: "Document refactor decisions and lessons learned"

# Generate docs
docs-provider: "Generate documentation for refactored [component]"

# Create PR
sequential-thinking: "Generate comprehensive PR description"
```

---

## 🎯 Common Scenarios

### New API Endpoint
```bash
# 1. Check context
memory-bank: "Show existing API patterns"

# 2. Analyze dependencies
knowledge-graph: "Show all files that handle API routing"

# 3. Plan implementation
sequential-thinking: "Create 4-step plan for new [endpoint]"

# 4. Generate code
sequential-thinking: "Generate Flask route code for [endpoint]"

# 5. Generate tests
sequential-thinking: "Generate pytest test cases for [endpoint]"

# 6. Update docs
docs-provider: "Generate API documentation for [endpoint]"

# 7. Document decision
memory-bank: "Record API design decision for [endpoint]"
```

### Debugging Issue
```bash
# 1. Gather context
memory-bank: "Check if similar issues occurred before"
knowledge-graph: "Show all components involved in [error]"

# 2. Create plan
sequential-thinking: "Create debugging checklist for [issue]"

# 3. Investigate
knowledge-graph: "Show dependency chain for [failing component]"

# 4. Solve & document
sequential-thinking: "Generate solution steps for [issue]"
memory-bank: "Document solution for [issue]"
```

### Performance Optimization
```bash
# 1. Baseline
memory-bank: "Store baseline performance metrics"

# 2. Identify bottlenecks
knowledge-graph: "Show performance-critical components"
sequential-thinking: "Create optimization strategy"

# 3. Implement
sequential-thinking: "Generate optimized code for [component]"

# 4. Measure
memory-bank: "Compare performance before/after optimization"

# 5. Document
memory-bank: "Document optimization decisions"
```

---

## 🔗 Cross-Tool Workflows

### Planning → Implementation → Documentation
```bash
sequential-thinking: "Plan step 1: split app.py"
knowledge-graph: "Show current dependencies of app.py"
sequential-thinking: "Generate blueprint code based on dependencies"
memory-bank: "Document why we chose this blueprint structure"
```

### Validation Chains
```bash
# Before each step
knowledge-graph: "Verify no circular dependencies"
memory-bank: "Record current test coverage baseline"

# After each step  
knowledge-graph: "Show what changed in dependency graph"
sequential-thinking: "Generate tests for new boundaries"
memory-bank: "Update progress and document any issues"
```

### Decision Support
```bash
docs-provider: "Compare Flask-SocketIO blueprint vs. separate app approaches"
memory-bank: "Record pros/cons of each approach"
sequential-thinking: "Recommend best option based on our constraints"
knowledge-graph: "Show impact of chosen approach on existing code"
```

---

## 🧪 Testing Your System

### Quick Test
```bash
python test-universal-system.py
```

### Comprehensive Test
```bash
python .universal/test-system/test-universal-system.py
```

### Manual Tests
```bash
# Test memory
memory-bank: get_file_content project="main" path="progress.md"

# Test graph
knowledge-graph: "Show all files in the project"

# Test planning
sequential-thinking: "Create a 3-step plan for testing"

# Test docs
docs-provider: "Generate a summary of the system"
```

---

## 📊 Quality Assurance

### Before Committing
```bash
# 1. Check memory
memory-bank: "Verify this change aligns with project decisions"

# 2. Analyze dependencies
knowledge-graph: "Verify no circular dependencies introduced"

# 3. Generate tests
sequential-thinking: "Generate test cases for [new code]"

# 4. Update docs
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

## 🎁 Key Benefits

1. **🧠 Cognitive Offloading**: AI handles complexity, you handle decisions
2. **📚 Knowledge Preservation**: Everything documented automatically
3. **🔄 Iterative Safety**: Small steps, easy recovery
4. **🎯 Goal-Oriented**: Each step has clear deliverable
5. **🤖 AI-Native**: Uses LLMs for their strengths
6. **📊 Data-Driven**: Metrics guide decisions
7. **🔍 Transparent**: Full audit trail of changes
8. **🛡️ Safety-First**: Comprehensive testing and validation

---

**Happy AI-enhanced coding! 🚀**

*Keep this reference handy for daily development with your Universal AI Development System.* 