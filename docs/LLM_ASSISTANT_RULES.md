# LLM Coding Assistant Rules
## Mandatory Rules and Guidelines for Consistent, High-Quality Development

### Overview
This document establishes mandatory rules that every LLM coding assistant must follow. These rules ensure consistency, quality, and comprehensive documentation across all development sessions.

### Core Rules (MANDATORY)

#### Rule 1: Documentation-First Development
**ALWAYS** update documentation before, during, and after any code changes.
- [ ] Update README.md for any new features or significant changes
- [ ] Update CHANGELOG.md for every functional change
- [ ] Create/update feature documentation for new functionality
- [ ] Update API documentation for any API changes
- [ ] Add usage examples for new features

#### Rule 2: Session Management
**ALWAYS** follow the session management protocol.
- [ ] Read `LLM_CODING_ASSISTANT_FRAMEWORK.md` at session start
- [ ] Review previous session summaries before starting work
- [ ] Create comprehensive session summary before ending
- [ ] Document all decisions, issues, and progress
- [ ] Plan next session priorities

#### Rule 3: Quality Assurance
**ALWAYS** maintain high quality standards.
- [ ] Run tests after any significant code change
- [ ] Verify code follows style guidelines
- [ ] Check for security vulnerabilities
- [ ] Ensure performance is acceptable
- [ ] Validate user experience

#### Rule 4: Communication Standards
**ALWAYS** communicate clearly and proactively.
- [ ] Explain what you're doing and why
- [ ] Provide regular progress updates
- [ ] Report issues immediately with proposed solutions
- [ ] Ask for clarification when needed
- [ ] Document all technical decisions

#### Rule 5: Code Standards
**ALWAYS** follow established coding standards.
- [ ] Use consistent naming conventions
- [ ] Add comprehensive error handling
- [ ] Include inline documentation
- [ ] Follow the project's code style
- [ ] Write maintainable, readable code

### Development Workflow Rules

#### Rule 6: Pre-Development Planning
**BEFORE** starting any development work:
- [ ] Understand the requirements completely
- [ ] Break down complex tasks into manageable steps
- [ ] Identify dependencies and prerequisites
- [ ] Plan testing strategy
- [ ] Consider backward compatibility

#### Rule 7: Implementation Standards
**DURING** development:
- [ ] Implement with comprehensive error handling
- [ ] Add appropriate logging and debugging
- [ ] Include inline documentation
- [ ] Test each component as you build it
- [ ] Consider edge cases and error conditions

#### Rule 8: Post-Development Verification
**AFTER** completing development:
- [ ] Run all tests and verify they pass
- [ ] Check code quality and style
- [ ] Verify documentation is complete and accurate
- [ ] Test user experience and functionality
- [ ] Ensure no regressions were introduced

### Documentation Rules

#### Rule 9: README Maintenance
**ALWAYS** keep README.md current and comprehensive:
- [ ] Update project overview when features change
- [ ] Add installation instructions for new dependencies
- [ ] Update usage examples for new features
- [ ] Keep feature list current
- [ ] Maintain links to detailed documentation

#### Rule 10: CHANGELOG Standards
**ALWAYS** update CHANGELOG.md for any functional changes:
- [ ] Use semantic versioning
- [ ] Categorize changes (Added, Changed, Deprecated, Removed, Fixed, Security)
- [ ] Provide clear, concise descriptions
- [ ] Include breaking changes prominently
- [ ] Add dates for all entries

#### Rule 11: Feature Documentation
**ALWAYS** create comprehensive feature documentation:
- [ ] Document purpose and benefits
- [ ] Provide usage examples
- [ ] Include configuration options
- [ ] Document troubleshooting procedures
- [ ] Add performance considerations

#### Rule 12: API Documentation
**ALWAYS** maintain complete API documentation:
- [ ] Document all endpoints and parameters
- [ ] Provide request/response examples
- [ ] Include error codes and handling
- [ ] Document authentication requirements
- [ ] Keep examples current and working

### Testing Rules

#### Rule 13: Test Coverage
**ALWAYS** maintain comprehensive test coverage:
- [ ] Write tests for all new functionality
- [ ] Maintain >80% test coverage
- [ ] Test edge cases and error conditions
- [ ] Include integration tests for complex features
- [ ] Verify tests pass before committing

#### Rule 14: Test Quality
**ALWAYS** write high-quality tests:
- [ ] Use descriptive test names
- [ ] Test one thing per test
- [ ] Include setup and teardown
- [ ] Mock external dependencies
- [ ] Test both success and failure cases

### Security Rules

#### Rule 15: Security Awareness
**ALWAYS** consider security implications:
- [ ] Validate all user inputs
- [ ] Use secure authentication methods
- [ ] Avoid hardcoding sensitive information
- [ ] Follow security best practices
- [ ] Document security considerations

#### Rule 16: Dependency Management
**ALWAYS** manage dependencies securely:
- [ ] Use specific version numbers
- [ ] Regularly update dependencies
- [ ] Check for security vulnerabilities
- [ ] Document dependency purposes
- [ ] Test with updated dependencies

### Performance Rules

#### Rule 17: Performance Optimization
**ALWAYS** consider performance implications:
- [ ] Profile code for bottlenecks
- [ ] Optimize database queries
- [ ] Use efficient algorithms
- [ ] Consider caching strategies
- [ ] Document performance characteristics

#### Rule 18: Resource Management
**ALWAYS** manage resources efficiently:
- [ ] Close file handles and connections
- [ ] Use appropriate data structures
- [ ] Avoid memory leaks
- [ ] Monitor resource usage
- [ ] Document resource requirements

### User Experience Rules

#### Rule 19: User-Centric Design
**ALWAYS** prioritize user experience:
- [ ] Design intuitive interfaces
- [ ] Provide clear error messages
- [ ] Include helpful documentation
- [ ] Consider accessibility requirements
- [ ] Test with real users when possible

#### Rule 20: Error Handling
**ALWAYS** provide comprehensive error handling:
- [ ] Catch and handle all exceptions
- [ ] Provide meaningful error messages
- [ ] Log errors for debugging
- [ ] Implement graceful degradation
- [ ] Document error recovery procedures

### Maintenance Rules

#### Rule 21: Code Maintenance
**ALWAYS** maintain code quality:
- [ ] Refactor complex code
- [ ] Remove dead code
- [ ] Update deprecated features
- [ ] Improve code readability
- [ ] Document maintenance procedures

#### Rule 22: Version Control
**ALWAYS** use version control effectively:
- [ ] Make atomic commits
- [ ] Write clear commit messages
- [ ] Use meaningful branch names
- [ ] Review changes before merging
- [ ] Keep branches up to date

### Communication Rules

#### Rule 23: Progress Reporting
**ALWAYS** keep users informed:
- [ ] Provide regular status updates
- [ ] Explain technical decisions
- [ ] Report issues immediately
- [ ] Ask for feedback when needed
- [ ] Document progress thoroughly

#### Rule 24: Issue Management
**ALWAYS** handle issues professionally:
- [ ] Acknowledge issues immediately
- [ ] Investigate thoroughly
- [ ] Provide clear explanations
- [ ] Propose solutions
- [ ] Follow up on resolutions

### Quality Assurance Rules

#### Rule 25: Code Review
**ALWAYS** review code before completion:
- [ ] Check for bugs and issues
- [ ] Verify code quality
- [ ] Ensure documentation is complete
- [ ] Test functionality
- [ ] Validate user experience

#### Rule 26: Testing Verification
**ALWAYS** verify testing completeness:
- [ ] Run all relevant tests
- [ ] Check test coverage
- [ ] Verify test quality
- [ ] Test edge cases
- [ ] Validate test results

### Emergency Rules

#### Rule 27: Problem Resolution
**ALWAYS** handle problems systematically:
- [ ] Assess the situation quickly
- [ ] Communicate the problem clearly
- [ ] Propose immediate solutions
- [ ] Implement fixes carefully
- [ ] Document the resolution

#### Rule 28: Rollback Procedures
**ALWAYS** have rollback plans:
- [ ] Keep backups of important data
- [ ] Document rollback procedures
- [ ] Test rollback processes
- [ ] Communicate rollback plans
- [ ] Execute rollbacks carefully

### Continuous Improvement Rules

#### Rule 29: Learning and Adaptation
**ALWAYS** learn from experience:
- [ ] Document lessons learned
- [ ] Update procedures based on experience
- [ ] Share knowledge with future sessions
- [ ] Improve processes continuously
- [ ] Adapt to changing requirements

#### Rule 30: Knowledge Management
**ALWAYS** maintain knowledge base:
- [ ] Document successful patterns
- [ ] Record common solutions
- [ ] Update best practices
- [ ] Share insights across sessions
- [ ] Maintain comprehensive documentation

### Rule Enforcement Checklist

#### Daily Compliance
- [ ] All code changes documented
- [ ] Tests run and passing
- [ ] Documentation updated
- [ ] Quality standards met
- [ ] Communication standards followed

#### Session Compliance
- [ ] Session management protocol followed
- [ ] All rules adhered to
- [ ] Quality assurance completed
- [ ] Documentation comprehensive
- [ ] Next session prepared

#### Project Compliance
- [ ] All features documented
- [ ] Test coverage adequate
- [ ] Security standards met
- [ ] Performance acceptable
- [ ] User experience validated

### Rule Violation Procedures

#### Minor Violations
- [ ] Identify the violation
- [ ] Correct immediately
- [ ] Document the correction
- [ ] Learn from the mistake
- [ ] Update procedures if needed

#### Major Violations
- [ ] Stop work immediately
- [ ] Assess the impact
- [ ] Communicate the issue
- [ ] Implement corrective actions
- [ ] Document lessons learned

### Success Metrics

#### Rule Compliance Metrics
- **Compliance Rate**: Percentage of rules followed
- **Violation Frequency**: Number of rule violations per session
- **Correction Time**: Time to correct violations
- **Learning Effectiveness**: Improvement in compliance over time

#### Quality Metrics
- **Code Quality**: Based on standards compliance
- **Documentation Quality**: Completeness and accuracy
- **Test Quality**: Coverage and effectiveness
- **User Satisfaction**: Based on delivered functionality

---

**Remember**: These rules are not optional. They are mandatory requirements for maintaining high-quality, consistent development. Follow them rigorously and update them based on experience and lessons learned. 