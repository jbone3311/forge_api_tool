# Documentation Organization System

This directory contains an organized documentation system that separates universal templates and instructions from project-specific details. This makes it easy to copy and adapt documentation for other projects.

## Directory Structure

```
docs/
├── README.md                    # This file - explains the organization
├── universal/                   # Universal templates and instructions
│   ├── templates/               # Reusable documentation templates
│   │   ├── project-onboarding.md
│   │   ├── llm-setup-instructions.md
│   │   ├── printable-quick-sheet.md
│   │   ├── ci-cd-pipeline.md
│   │   ├── security-checklist.md
│   │   ├── quick-reference.md
│   │   ├── testing-documentation-template.md
│   │   ├── LLM_ASSISTANT_QUICK_REFERENCE.md
│   │   ├── COMMUNITY_SOLUTIONS.md
│   │   └── TERMINAL_FIX_GUIDE.md
│   └── instructions/            # Universal setup instructions
│       ├── cursor-ai-setup.md
│       ├── daily-practices.md
│       ├── user-setup-guide.md
│       ├── LLM_ASSISTANT_RULES.md
│       ├── SESSION_MANAGEMENT.md
│       ├── DOCUMENTATION_STANDARDS.md
│       └── LLM_CODING_ASSISTANT_FRAMEWORK.md
├── project-specific/            # Project-specific documentation
│   ├── cli-commands.md
│   ├── test-coverage.md
│   ├── REFACTORING_PLAN.md
│   └── FORGE_API_TEST_SUMMARY.md
├── features/                    # Project-specific feature docs
├── testing/                     # Project-specific test reports/coverage
├── cleanup/                     # Project-specific cleanup logs
├── development/                 # Project-specific development docs
├── SESSION_SUMMARIES/           # Project-specific session logs
└── ... (other project-specific docs)
```

## Quick Start

### For New Projects
1. Copy `docs/universal/` to your new project
2. Copy `docs/project-specific/` and update the details
3. Copy `.cursor/rules/testing.mdc` and update project-specific section

### For Existing Projects
1. Follow `docs/universal/instructions/user-setup-guide.md`
2. Set up Cursor AI rules using `docs/universal/instructions/cursor-ai-setup.md`
3. Organize your existing documentation using the templates

## Universal vs Project-Specific

### Universal (docs/universal/)
- **Never change these files** - they work for any project
- Contains templates and instructions that apply to all projects
- Copy these unchanged to new projects

#### Universal Templates
- `project-onboarding.md`, `llm-setup-instructions.md`, `printable-quick-sheet.md`, `ci-cd-pipeline.md`, `security-checklist.md`, `quick-reference.md`, `testing-documentation-template.md`, `LLM_ASSISTANT_QUICK_REFERENCE.md`, `COMMUNITY_SOLUTIONS.md`, `TERMINAL_FIX_GUIDE.md`

#### Universal Instructions
- `cursor-ai-setup.md`, `daily-practices.md`, `user-setup-guide.md`, `LLM_ASSISTANT_RULES.md`, `SESSION_MANAGEMENT.md`, `DOCUMENTATION_STANDARDS.md`, `LLM_CODING_ASSISTANT_FRAMEWORK.md`

### Project-Specific (docs/project-specific/ and others)
- **Update these for each project** - contains project-specific details
- Lists custom directories, scripts, and workflows
- Adapt these to match your project's structure

#### Project-Specific Docs
- `cli-commands.md` - All CLI commands for this project
- `test-coverage.md` - Test structure and coverage details
- `REFACTORING_PLAN.md` - Refactoring and cleanup plan
- `FORGE_API_TEST_SUMMARY.md` - Project test summary
- `features/`, `testing/`, `cleanup/`, `development/` - Project-specific documentation for features, tests, cleanup, and development
- `SESSION_SUMMARIES/` - Project-specific session logs

#### Optional Project-Specific Docs
- `DEPLOYMENT.md` - Deployment instructions
- `INTEGRATION_GUIDES.md` - Integration with other tools/services
- `TROUBLESHOOTING.md` - Project-specific troubleshooting
- `SECURITY.md` - Project-specific security practices
- `CHANGELOG.md` - Project change log (if not in project root)

## Cursor AI Integration

The `.cursor/rules/testing.mdc` file contains rules that help Cursor AI understand:
- Universal testing and documentation practices
- Project-specific details and workflows
- How to separate universal from project-specific content

## Benefits

1. **Easy Copying** - Universal templates work for any project
2. **Better AI Assistance** - Cursor AI understands your project structure
3. **Maintainable** - Clear separation of universal vs project-specific
4. **Team Collaboration** - Consistent approach across team members

## Getting Started

1. Read `docs/universal/instructions/user-setup-guide.md` for complete instructions
2. Set up Cursor AI rules following `docs/universal/instructions/cursor-ai-setup.md`
3. Use the templates in `docs/universal/templates/` as starting points
4. Update project-specific documentation in `docs/project-specific/`

## Support

- Check `docs/universal/instructions/` for setup guides
- Review `docs/project-specific/` for project details
- Test your setup with `python cli.py tests run all` 