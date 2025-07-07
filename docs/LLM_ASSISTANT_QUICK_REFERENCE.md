# LLM Coding Assistant Quick Reference
## Essential Information for Every Development Session

### Session Start Checklist (MANDATORY)
1. **Read Framework**: `docs/LLM_CODING_ASSISTANT_FRAMEWORK.md`
2. **Review Rules**: `docs/LLM_ASSISTANT_RULES.md`
3. **Check Previous Session**: Look for session summaries
4. **Verify Project State**: Check git status and recent changes
5. **Understand Goals**: Clarify user requirements

### Core Rules (ALWAYS FOLLOW)
- **Documentation-First**: Update docs before, during, and after code changes
- **Quality Assurance**: Run tests, check code quality, verify user experience
- **Communication**: Explain what you're doing, provide regular updates
- **Session Management**: Create comprehensive session summaries
- **Code Standards**: Follow established patterns and best practices

### Required Documentation Updates
**For EVERY code change**:
- [ ] README.md (if features change)
- [ ] CHANGELOG.md (for functional changes)
- [ ] Feature documentation (for new features)
- [ ] API documentation (for API changes)
- [ ] Inline code comments

### Quality Standards
- **Test Coverage**: >80% for new code
- **Code Quality**: Follow style guidelines, comprehensive error handling
- **Documentation**: Complete, accurate, current
- **Security**: No vulnerabilities, secure practices
- **Performance**: No regressions, efficient code

### Session End Checklist (MANDATORY)
1. **Update Documentation**: All relevant docs current
2. **Run Tests**: Verify all tests pass
3. **Create Session Summary**: Document accomplishments and next steps
4. **Commit Changes**: Git add, commit, push
5. **Verify Quality**: Code quality, documentation, user experience

### Common Commands
```bash
# Quality Assurance
python -m pytest tests/
python -m pytest tests/ --cov=core --cov-report=html
flake8 core/ web_dashboard/
black --check core/ web_dashboard/

# Documentation
# Always update README.md, CHANGELOG.md, and feature docs

# Git Workflow
git add .
git commit -m "descriptive message"
git push origin master
```

### Communication Template
**Progress Update**:
- **Current Task**: [What you're working on]
- **Progress**: [What's been accomplished]
- **Next Steps**: [What's coming next]
- **Issues**: [Any problems encountered]
- **Decisions**: [Technical decisions made]

### Emergency Procedures
**When Things Go Wrong**:
1. **Stop**: Pause current work
2. **Assess**: Identify the problem
3. **Communicate**: Explain issue to user
4. **Plan**: Propose solution
5. **Execute**: Implement fix carefully
6. **Document**: Record what happened

### Documentation Templates
**Session Summary**:
```markdown
# Session Summary - [Date]

## Accomplishments
- [ ] Task 1: Description
- [ ] Task 2: Description

## Issues Encountered
- Issue: Description and resolution

## Next Session Priorities
1. High Priority: [Tasks]
2. Medium Priority: [Tasks]

## Files Modified
- `path/to/file`: [Changes]
```

**Feature Documentation**:
```markdown
# Feature Name

## Overview
Brief description

## Usage
Examples and instructions

## Configuration
Options and settings

## Troubleshooting
Common issues and solutions
```

### Key Files to Always Check
- `README.md` - Project overview and setup
- `CHANGELOG.md` - Recent changes and versions
- `docs/LLM_CODING_ASSISTANT_FRAMEWORK.md` - Main framework
- `docs/LLM_ASSISTANT_RULES.md` - Mandatory rules
- `docs/SESSION_MANAGEMENT.md` - Session protocols
- `docs/DOCUMENTATION_STANDARDS.md` - Documentation requirements

### Success Metrics
- **Task Completion**: 80% of planned tasks
- **Documentation**: All changes documented
- **Testing**: All new code tested
- **Quality**: No critical issues introduced
- **User Satisfaction**: Requirements met

### Remember
- **Always document everything**
- **Maintain high quality standards**
- **Communicate clearly and regularly**
- **Follow established procedures**
- **Learn and improve continuously**

---

**This is your quick reference. Use it at the start of every session and refer to it throughout development.** 