# Documentation Organization System

This directory contains an organized documentation system that separates SYSTEM templates and instructions from PROJECT-SPECIFIC details. This makes it easy to copy and adapt documentation for other projects.

## Directory Structure

```
docs/
├── README.md                    # This file - explains the organization
├── SYSTEM/                   # SYSTEM templates and instructions
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
│   └── instructions/            # SYSTEM setup instructions
│       ├── cursor-ai-setup.md
│       ├── daily-practices.md
│       ├── user-setup-guide.md
│       ├── LLM_ASSISTANT_RULES.md
│       ├── SESSION_MANAGEMENT.md
│       ├── DOCUMENTATION_STANDARDS.md
│       └── LLM_CODING_ASSISTANT_FRAMEWORK.md
├── PROJECT-SPECIFIC/            # PROJECT-SPECIFIC documentation
│   ├── cli-commands.md
│   ├── test-coverage.md
│   ├── REFACTORING_PLAN.md
│   └── FORGE_API_TEST_SUMMARY.md
├── features/                    # PROJECT-SPECIFIC feature docs
├── testing/                     # PROJECT-SPECIFIC test reports/coverage
├── cleanup/                     # PROJECT-SPECIFIC cleanup logs
├── development/                 # PROJECT-SPECIFIC development docs
├── SESSION_SUMMARIES/           # PROJECT-SPECIFIC session logs
└── ... (other PROJECT-SPECIFIC docs)
```

## Quick Start

### For New Projects
1. Copy `docs/SYSTEM/` to your new project
2. Copy `docs/PROJECT-SPECIFIC/` and update the details
3. Copy `.cursor/rules/testing.mdc` and update PROJECT-SPECIFIC section

### For Existing Projects
1. Follow `docs/SYSTEM/instructions/user-setup-guide.md`
2. Set up Cursor AI rules using `docs/SYSTEM/instructions/cursor-ai-setup.md`
3. Organize your existing documentation using the templates

## SYSTEM vs PROJECT-SPECIFIC

### SYSTEM (docs/SYSTEM/)
- **Never change these files** - they work for any project
- Contains templates and instructions that apply to all projects
- Copy these unchanged to new projects

#### SYSTEM Templates
- `project-onboarding.md`, `llm-setup-instructions.md`, `printable-quick-sheet.md`, `ci-cd-pipeline.md`, `security-checklist.md`, `quick-reference.md`, `testing-documentation-template.md`, `LLM_ASSISTANT_QUICK_REFERENCE.md`, `COMMUNITY_SOLUTIONS.md`, `TERMINAL_FIX_GUIDE.md`

#### SYSTEM Instructions
- `cursor-ai-setup.md`, `daily-practices.md`, `user-setup-guide.md`, `LLM_ASSISTANT_RULES.md`, `SESSION_MANAGEMENT.md`, `DOCUMENTATION_STANDARDS.md`, `LLM_CODING_ASSISTANT_FRAMEWORK.md`

### PROJECT-SPECIFIC (docs/PROJECT-SPECIFIC/ and others)
- **Update these for each project** - contains PROJECT-SPECIFIC details
- Lists custom directories, scripts, and workflows
- Adapt these to match your project's structure

#### PROJECT-SPECIFIC Docs
- `cli-commands.md` - All CLI commands for this project
- `test-coverage.md` - Test structure and coverage details
- `REFACTORING_PLAN.md` - Refactoring and cleanup plan
- `FORGE_API_TEST_SUMMARY.md` - Project test summary
- `features/`, `testing/`, `cleanup/`, `development/` - PROJECT-SPECIFIC documentation for features, tests, cleanup, and development
- `SESSION_SUMMARIES/` - PROJECT-SPECIFIC session logs

#### Optional PROJECT-SPECIFIC Docs
- `DEPLOYMENT.md` - Deployment instructions
- `INTEGRATION_GUIDES.md` - Integration with other tools/services
- `TROUBLESHOOTING.md` - PROJECT-SPECIFIC troubleshooting
- `SECURITY.md` - PROJECT-SPECIFIC security practices
- `CHANGELOG.md` - Project change log (if not in project root)

## Cursor AI Integration

The `.cursor/rules/testing.mdc` file contains rules that help Cursor AI understand:
- SYSTEM testing and documentation practices
- PROJECT-SPECIFIC details and workflows
- How to separate SYSTEM from PROJECT-SPECIFIC content

## Benefits

1. **Easy Copying** - SYSTEM templates work for any project
2. **Better AI Assistance** - Cursor AI understands your project structure
3. **Maintainable** - Clear separation of SYSTEM vs PROJECT-SPECIFIC
4. **Team Collaboration** - Consistent approach across team members

## Getting Started

1. Read `docs/SYSTEM/instructions/user-setup-guide.md` for complete instructions
2. Set up Cursor AI rules following `docs/SYSTEM/instructions/cursor-ai-setup.md`
3. Use the templates in `docs/SYSTEM/templates/` as starting points
4. Update PROJECT-SPECIFIC documentation in `docs/PROJECT-SPECIFIC/`

## Support

- Check `docs/SYSTEM/instructions/` for setup guides
- Review `docs/PROJECT-SPECIFIC/` for project details
- Test your setup with `python cli.py tests run all` 