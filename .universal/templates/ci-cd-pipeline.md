# CI/CD Pipeline Template (Universal)

## 🚀 Overview

This template provides a complete CI/CD pipeline configuration that can be adapted for any project. It includes testing, security scanning, code quality checks, and deployment stages.

## 📋 Pipeline Stages

### 1. **Build & Test Stage**
- Environment setup
- Dependency installation
- Code quality checks
- Unit and integration tests
- Test coverage reporting

### 2. **Security Stage**
- Static code analysis
- Dependency vulnerability scanning
- Security linting
- Secrets detection

### 3. **Deployment Stage**
- Environment-specific deployments
- Health checks
- Rollback procedures
- Monitoring setup

## 🔧 GitHub Actions Configuration

### Main Workflow
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.9'
  PIP_CACHE_DIR: ~/.cache/pip

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black . --check
        isort . --check-only
    
    - name: Run security checks
      run: |
        bandit -r . -f json -o bandit-report.json
        safety check --json --output safety-report.json
    
    - name: Run tests
      run: |
        python cli.py tests run all
        pytest --cov=. --cov-report=xml --cov-report=html
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          test-results/
          coverage/
          bandit-report.json
          safety-report.json

  security:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install security tools
      run: |
        pip install bandit safety semgrep
    
    - name: Run Semgrep
      run: |
        semgrep --config=auto --json --output semgrep-report.json
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          semgrep-report.json
          bandit-report.json
          safety-report.json

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/develop'
    environment: staging
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add your staging deployment commands here
    
    - name: Run health checks
      run: |
        echo "Running health checks"
        # Add health check commands here

  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add your production deployment commands here
    
    - name: Run health checks
      run: |
        echo "Running health checks"
        # Add health check commands here
    
    - name: Notify deployment
      run: |
        echo "Deployment completed successfully"
        # Add notification commands here
```

## 🔒 Security Pipeline

### Security Workflow
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install security tools
      run: |
        pip install bandit safety semgrep
    
    - name: Run Bandit security scan
      run: |
        bandit -r . -f json -o bandit-report.json
        bandit -r . -f txt -o bandit-report.txt
    
    - name: Run Safety dependency check
      run: |
        safety check --json --output safety-report.json
        safety check --full-report --output safety-report.txt
    
    - name: Run Semgrep scan
      run: |
        semgrep --config=auto --json --output semgrep-report.json
        semgrep --config=auto --text --output semgrep-report.txt
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports-${{ github.run_number }}
        path: |
          bandit-report.*
          safety-report.*
          semgrep-report.*
    
    - name: Create security summary
      run: |
        echo "## Security Scan Results" >> $GITHUB_STEP_SUMMARY
        echo "### Bandit Results" >> $GITHUB_STEP_SUMMARY
        cat bandit-report.txt >> $GITHUB_STEP_SUMMARY
        echo "### Safety Results" >> $GITHUB_STEP_SUMMARY
        cat safety-report.txt >> $GITHUB_STEP_SUMMARY
        echo "### Semgrep Results" >> $GITHUB_STEP_SUMMARY
        cat semgrep-report.txt >> $GITHUB_STEP_SUMMARY
```

## 🧪 Testing Pipeline

### Test Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run unit tests
      run: |
        python cli.py tests run unit
        pytest tests/unit/ --cov=core --cov-report=xml
    
    - name: Upload unit test coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unit-tests

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run integration tests
      run: |
        python cli.py tests run functional
        pytest tests/functional/ --cov=core --cov-report=xml
    
    - name: Upload integration test coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: integration-tests

  stress-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run stress tests
      run: |
        python cli.py tests run stress
        pytest tests/stress/ --timeout=300
    
    - name: Upload stress test results
      uses: actions/upload-artifact@v3
      with:
        name: stress-test-results
        path: test-results/
```

## 🚀 Deployment Pipeline

### Deployment Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'staging' }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run pre-deployment tests
      run: |
        python cli.py tests run all
        python cli.py status
    
    - name: Deploy to ${{ github.event.inputs.environment || 'staging' }}
      run: |
        echo "Deploying to ${{ github.event.inputs.environment || 'staging' }}"
        # Add deployment commands here
    
    - name: Run health checks
      run: |
        echo "Running health checks"
        # Add health check commands here
    
    - name: Notify deployment
      run: |
        echo "Deployment to ${{ github.event.inputs.environment || 'staging' }} completed"
        # Add notification commands here
```

## 📊 Monitoring and Reporting

### Performance Monitoring
```yaml
# .github/workflows/performance.yml
name: Performance Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install locust  # Performance testing tool
    
    - name: Run performance tests
      run: |
        python cli.py tests run stress
        # Add additional performance tests here
    
    - name: Generate performance report
      run: |
        echo "## Performance Test Results" >> $GITHUB_STEP_SUMMARY
        # Add performance reporting here
    
    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: performance-results/
```

## 🔧 Configuration Files

### Requirements Files
```bash
# requirements.txt (Production dependencies)
requests>=2.25.0
python-dotenv>=0.19.0
# Add other production dependencies

# requirements-dev.txt (Development dependencies)
pytest>=6.0.0
pytest-cov>=2.10.0
black>=21.0.0
flake8>=3.8.0
isort>=5.0.0
bandit>=1.7.0
safety>=1.10.0
semgrep>=0.50.0
# Add other development dependencies
```

### Security Configuration
```yaml
# .bandit
exclude_dirs: ['tests', 'venv', 'env']
skips: ['B101', 'B601']
```

```yaml
# .semgrep.yml
rules:
  - id: python.security.audit.weak-crypto.weak-crypto
    pattern: |
      import hashlib
      hashlib.md5(...)
    message: "Use of weak cryptographic algorithm"
    severity: WARNING
```

### Code Quality Configuration
```ini
# setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,*.egg-info,venv,env

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --strict-config
```

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

## 📋 Pipeline Checklist

### Pre-Deployment
- [ ] **Code Review:** All changes reviewed and approved
- [ ] **Tests Passing:** All tests pass in CI/CD pipeline
- [ ] **Security Scan:** Security scans completed without critical issues
- [ ] **Code Quality:** Code quality checks pass
- [ ] **Documentation:** Documentation updated
- [ ] **Version Update:** Version numbers updated
- [ ] **Changelog:** Changelog updated

### Deployment
- [ ] **Environment Setup:** Target environment prepared
- [ ] **Database Migration:** Database migrations applied
- [ ] **Configuration:** Environment-specific configuration applied
- [ ] **Deployment:** Application deployed successfully
- [ ] **Health Checks:** Health checks pass
- [ ] **Monitoring:** Monitoring and alerting configured
- [ ] **Backup:** Backup procedures verified

### Post-Deployment
- [ ] **Verification:** Application functionality verified
- [ ] **Performance:** Performance metrics within acceptable range
- [ ] **Security:** Security monitoring active
- [ ] **Documentation:** Deployment documentation updated
- [ ] **Team Notification:** Team notified of successful deployment
- [ ] **Rollback Plan:** Rollback procedures documented and tested

## 🚨 Rollback Procedures

### Automatic Rollback
```yaml
# Add to deployment workflow
- name: Rollback on failure
  if: failure()
  run: |
    echo "Deployment failed, initiating rollback"
    # Add rollback commands here
```

### Manual Rollback
```bash
# Manual rollback script
#!/bin/bash
echo "Initiating manual rollback..."

# Stop current deployment
echo "Stopping current deployment..."

# Restore previous version
echo "Restoring previous version..."

# Verify rollback
echo "Verifying rollback..."

# Notify team
echo "Rollback completed"
```

## 📈 Metrics and Monitoring

### Key Metrics
- **Deployment Frequency:** How often deployments occur
- **Lead Time:** Time from commit to deployment
- **Mean Time to Recovery (MTTR):** Time to recover from failures
- **Change Failure Rate:** Percentage of deployments causing failures

### Monitoring Setup
```yaml
# Add to deployment workflow
- name: Set up monitoring
  run: |
    echo "Setting up application monitoring"
    # Add monitoring setup commands here

- name: Configure alerts
  run: |
    echo "Configuring alerting rules"
    # Add alert configuration here
```

This CI/CD pipeline template provides a comprehensive foundation for automated testing, security scanning, and deployment that can be adapted for any project. 