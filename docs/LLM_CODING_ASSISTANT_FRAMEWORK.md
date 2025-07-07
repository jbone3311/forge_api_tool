# LLM Coding Assistant Framework
## Comprehensive Guidelines for Consistent, High-Quality Development

### Overview
This document establishes a systematic approach for LLM coding assistants to maintain consistency, quality, and comprehensive documentation across all development sessions. It serves as the "memory" and "operating system" for AI-assisted development.

### Core Principles
1. **Documentation-First Development**: Every code change must be accompanied by documentation updates
2. **Comprehensive Tracking**: All changes, decisions, and progress must be recorded
3. **Quality Assurance**: Multiple layers of verification and testing
4. **User-Centric Communication**: Clear, actionable feedback and explanations
5. **Proactive Maintenance**: Anticipate and address potential issues before they arise

### Required Documentation Structure

#### 1. Project Documentation Hierarchy
```
docs/
├── LLM_CODING_ASSISTANT_FRAMEWORK.md          # This document
├── DEVELOPMENT_GUIDELINES.md                  # Development standards
├── DOCUMENTATION_STANDARDS.md                 # Documentation requirements
├── SESSION_MANAGEMENT.md                      # Session tracking and continuity
├── QUALITY_ASSURANCE.md                       # Testing and verification protocols
├── REFACTORING_GUIDELINES.md                  # Code improvement standards
├── FEATURE_DEVELOPMENT.md                     # Feature implementation workflow
├── TROUBLESHOOTING.md                         # Common issues and solutions
├── development/
│   ├── CODE_REVIEWS/                          # Code review summaries
│   ├── ARCHITECTURE_DECISIONS/                # Design decision records
│   ├── PERFORMANCE_ANALYSIS/                  # Performance optimization records
│   └── SECURITY_REVIEWS/                      # Security assessment records
├── features/
│   ├── FEATURE_SUMMARIES/                     # High-level feature documentation
│   ├── IMPLEMENTATION_GUIDES/                 # Detailed implementation docs
│   └── USER_GUIDES/                           # End-user documentation
├── testing/
│   ├── TEST_COVERAGE_REPORTS/                 # Test coverage summaries
│   ├── TEST_PLANS/                            # Testing strategies
│   └── QUALITY_METRICS/                       # Quality measurement reports
└── maintenance/
    ├── CLEANUP_LOGS/                          # Code cleanup records
    ├── DEPENDENCY_UPDATES/                    # Dependency management
    └── PERFORMANCE_OPTIMIZATIONS/             # Performance improvement logs
```

#### 2. Session Documentation Requirements
Every development session must create/update:
- **Session Summary**: What was accomplished, decisions made, next steps
- **Change Log**: Detailed list of all modifications
- **Documentation Updates**: What docs were created/modified
- **Testing Status**: What tests were added/modified
- **Quality Metrics**: Performance, security, maintainability improvements

### Mandatory Workflow Steps

#### Phase 1: Session Initialization
1. **Project Assessment**
   - Review existing documentation structure
   - Identify current state and pending tasks
   - Check for incomplete work from previous sessions
   - Verify project health and dependencies

2. **Goal Clarification**
   - Understand user requirements clearly
   - Break down complex tasks into manageable steps
   - Identify dependencies and prerequisites
   - Create task list with priorities

3. **Documentation Review**
   - Read relevant existing documentation
   - Identify documentation gaps
   - Plan documentation updates needed

#### Phase 2: Development Execution
1. **Implementation Planning**
   - Design solution architecture
   - Identify affected components
   - Plan testing strategy
   - Consider backward compatibility

2. **Code Development**
   - Follow established coding standards
   - Implement with comprehensive error handling
   - Add appropriate logging and debugging
   - Include inline documentation

3. **Quality Assurance**
   - Run existing tests
   - Add new tests for new functionality
   - Perform code review
   - Check for security vulnerabilities

#### Phase 3: Documentation and Cleanup
1. **Documentation Updates**
   - Update README files
   - Modify CHANGELOG
   - Create/update feature documentation
   - Update API documentation if applicable
   - Add usage examples

2. **Session Summary**
   - Record what was accomplished
   - Document any issues encountered
   - Note decisions made and rationale
   - Plan next steps

3. **Quality Verification**
   - Verify all tests pass
   - Check documentation completeness
   - Ensure code follows standards
   - Validate user experience

### Required Tools and Commands

#### Documentation Management
```bash
# Create new documentation
touch docs/features/NEW_FEATURE.md
touch docs/development/ARCHITECTURE_DECISIONS/DECISION_YYYYMMDD.md

# Update existing documentation
# Always update README.md, CHANGELOG.md, and relevant feature docs

# Generate documentation summaries
# Create comprehensive summaries after major changes
```

#### Quality Assurance Commands
```bash
# Run tests
python -m pytest tests/
python -m pytest tests/ --cov=core --cov-report=html

# Code quality checks
flake8 core/ web_dashboard/
black --check core/ web_dashboard/

# Security checks
bandit -r core/ web_dashboard/

# Performance profiling
python -m cProfile -o profile.stats main_script.py
```

### Communication Standards

#### User Interaction
1. **Clear Explanations**: Explain what you're doing and why
2. **Progress Updates**: Regular status updates during long tasks
3. **Issue Reporting**: Immediately report problems with proposed solutions
4. **Decision Documentation**: Explain decisions and alternatives considered

#### Documentation Quality
1. **Completeness**: Cover all aspects of functionality
2. **Clarity**: Use clear, concise language
3. **Examples**: Include practical usage examples
4. **Maintenance**: Keep documentation current with code

### Session Continuity Protocol

#### Session Start Checklist
- [ ] Review previous session summaries
- [ ] Check for incomplete tasks
- [ ] Verify current project state
- [ ] Read relevant documentation
- [ ] Understand current user goals

#### Session End Checklist
- [ ] Update all relevant documentation
- [ ] Create session summary
- [ ] Commit and push changes
- [ ] Verify project health
- [ ] Plan next session priorities

### Quality Metrics and Standards

#### Code Quality
- Test coverage > 80%
- No critical security vulnerabilities
- Performance benchmarks met
- Code follows style guidelines
- Comprehensive error handling

#### Documentation Quality
- All new features documented
- README and CHANGELOG updated
- API documentation current
- Usage examples provided
- Architecture decisions recorded

#### User Experience
- Clear error messages
- Intuitive interfaces
- Comprehensive help text
- Smooth installation process
- Good performance

### Emergency Protocols

#### When Things Go Wrong
1. **Immediate Assessment**: Identify the problem scope
2. **User Communication**: Explain the issue and proposed solution
3. **Rollback Plan**: Have a plan to revert changes if needed
4. **Documentation**: Record what went wrong and how it was resolved
5. **Prevention**: Update procedures to prevent recurrence

#### Recovery Procedures
1. **Code Recovery**: Use git to revert problematic changes
2. **Documentation Recovery**: Restore from backups if needed
3. **Testing Recovery**: Re-run all tests to verify stability
4. **User Communication**: Keep user informed of recovery progress

### Continuous Improvement

#### Framework Updates
- Record successful patterns and techniques
- Identify areas for improvement
- Update guidelines based on experience
- Share lessons learned across sessions

#### Knowledge Management
- Maintain comprehensive documentation
- Create reusable templates
- Build knowledge base of common solutions
- Document best practices and anti-patterns

### Implementation Checklist for New Sessions

#### Initial Setup
- [ ] Read this framework document
- [ ] Review project documentation structure
- [ ] Understand current project state
- [ ] Identify documentation gaps
- [ ] Plan documentation updates

#### During Development
- [ ] Follow mandatory workflow steps
- [ ] Update documentation continuously
- [ ] Maintain quality standards
- [ ] Communicate progress regularly
- [ ] Record decisions and rationale

#### Session Completion
- [ ] Complete all documentation updates
- [ ] Verify quality standards met
- [ ] Create comprehensive session summary
- [ ] Plan next session priorities
- [ ] Commit and push all changes

### Success Metrics

#### Short-term Success
- All tasks completed successfully
- Documentation updated and accurate
- Tests passing and coverage adequate
- User requirements met
- Code quality maintained

#### Long-term Success
- Project maintainability improved
- Documentation comprehensive and current
- Development velocity increased
- User satisfaction high
- Technical debt reduced

---

**Remember**: This framework is a living document. Update it based on experience and lessons learned. The goal is continuous improvement in development quality and consistency. 