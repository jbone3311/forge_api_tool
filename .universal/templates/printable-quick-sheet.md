# 🚀 Daily Development Quick Sheet (Printable)

## 📋 Morning Routine
```bash
git status                    # Check current state
git fetch origin             # Get latest remote info
git pull origin main         # Pull latest changes
venv\Scripts\activate        # Activate environment (Windows)
# or source venv/bin/activate # Linux/Mac
python cli.py tests run all  # Run all tests
python cli.py status         # Check system status
```

## 🔒 Daily Security Checks
```bash
bandit -r .                  # Code security scan
safety check                 # Dependency vulnerabilities
grep -r "password\|secret\|key\|token" . --exclude-dir=venv --exclude-dir=.git
```

## 🧪 Testing Commands
```bash
python cli.py tests run all      # All tests
python cli.py tests run unit     # Unit tests only
python cli.py tests run functional # Integration tests
python cli.py tests run stress   # Performance tests
python -m pytest --cov=.         # Coverage report
```

## 📝 Documentation Updates
- **Before committing:** Update `docs/project-specific/` if needed
- **Universal templates:** Never change `.universal/`
- **New features:** Update relevant project-specific docs
- **Weekly:** Review universal templates for improvements

## 🔧 Code Quality
```bash
black .                     # Format code
isort .                     # Sort imports
flake8 .                    # Lint code
python cli.py status        # System health check
```

## 🚨 Emergency Procedures
```bash
git status                  # Check current state
git stash                   # Save work if needed
git checkout main           # Switch to stable branch
git reset --hard HEAD~1     # Rollback last commit (careful!)
```

## 📊 End of Day
```bash
git add .                   # Stage changes
git commit -m "feat: description"  # Commit with clear message
git push origin main        # Push to remote
```

## 🔍 Quick Status Check
```bash
python cli.py status        # System status
python cli.py test          # API connection test
git log --oneline -5        # Recent commits
df -h                       # Disk space (Linux/Mac)
# or dir                     # Windows
```

## 📁 Key Directories
- `.universal/` - Never change (copy to new projects)
- `docs/project-specific/` - Update for this project
- `tests/` - All test files
- `core/` - Main application code
- `config/` - Configuration files
- `logs/` - Application logs

## 🛡️ Security Reminders
- [ ] No secrets in code or commits
- [ ] Use .env files for sensitive data
- [ ] Run security scans daily
- [ ] Check for vulnerable dependencies
- [ ] Review access permissions

## 🧪 Testing Checklist
- [ ] All tests pass before committing
- [ ] Add tests for new features
- [ ] Update tests when changing functionality
- [ ] Check test coverage weekly
- [ ] Fix failing tests immediately

## 📚 Documentation Checklist
- [ ] Update project-specific docs for new features
- [ ] Keep universal templates unchanged
- [ ] Use clear, concise language
- [ ] Include code examples where relevant
- [ ] Link to related documentation

## 🔄 Git Workflow
```bash
# Feature development
git checkout -b feature/new-feature
# ... make changes ...
python cli.py tests run all
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request
```

## 🚀 Multi-Computer Setup
```bash
# Before switching computers
git add docs/
git commit -m "docs: update project-specific documentation"
git push origin main

# On new computer
git pull origin main
# Review any documentation conflicts
```

## 📞 Quick Commands Reference
| Task | Command |
|------|---------|
| Run all tests | `python cli.py tests run all` |
| Check status | `python cli.py status` |
| Security scan | `bandit -r .` |
| Format code | `black .` |
| Lint code | `flake8 .` |
| Check coverage | `python -m pytest --cov=.` |
| Update deps | `pip install -r requirements.txt` |

## 🎯 Daily Goals
- [ ] All tests passing
- [ ] Security scans clean
- [ ] Code properly formatted
- [ ] Documentation updated
- [ ] Changes committed and pushed
- [ ] No secrets in code
- [ ] System status healthy

---

**Remember:** Universal templates in `.universal/` are for copying to new projects. Only update `docs/project-specific/` for this project. 