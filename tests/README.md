# Forge API Tool - Test Suite

This directory contains the comprehensive test suite for the Forge API Tool, organized by test type for better maintainability and clarity.

## Directory Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_imports.py     # Core module import tests
│   ├── test_config_handler.py
│   ├── test_wildcard_manager.py
│   ├── test_output_manager.py
│   └── test_image_analyzer.py
├── integration/            # Integration tests for API and external services
│   ├── test_forge_api.py
│   ├── test_forge_endpoints.py
│   ├── test_forge_direct.py
│   ├── test_integration.py
│   ├── test_api.py
│   ├── test_api_simple.py
│   ├── test_api_comprehensive.py
│   ├── test_dashboard_ui.py
│   ├── test_endpoint_coverage.py
│   ├── test_performance.py
│   ├── test_error_handling.py
│   ├── test_permissions.py
│   └── test_realtime_events.py
├── functional/             # Functional tests for user workflows
│   ├── test_config_loading.py
│   ├── test_template_loading.py
│   ├── test_template_prompt_loading.py
│   ├── test_templates.py
│   ├── test_preview_wildcards.py
│   ├── test_completed_prompts.py
│   ├── test_generation.py
│   └── test_status_indicators.py
├── debug/                  # Debug and development tests
│   └── quick_test.py
├── fixtures/               # Test fixtures and data
├── run_all_tests.py        # Main test runner
├── run_tests.py           # Legacy test runner
└── README.md              # This file
```

## Test Categories

### Unit Tests (`unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single functions, classes, or modules
- **Dependencies**: Minimal external dependencies
- **Speed**: Fast execution
- **Examples**: Import tests, configuration parsing, utility functions

### Integration Tests (`integration/`)
- **Purpose**: Test interactions between components and external services
- **Scope**: API endpoints, database operations, external API calls
- **Dependencies**: May require running services (Forge API, database)
- **Speed**: Medium execution time
- **Examples**: Forge API communication, web dashboard functionality

### Functional Tests (`functional/`)
- **Purpose**: Test complete user workflows and business logic
- **Scope**: End-to-end scenarios, user stories
- **Dependencies**: May require full application stack
- **Speed**: Slower execution
- **Examples**: Configuration workflows, template processing, image generation

### Debug Tests (`debug/`)
- **Purpose**: Development and debugging utilities
- **Scope**: Quick validation, troubleshooting
- **Dependencies**: Minimal
- **Speed**: Very fast
- **Examples**: Quick validation scripts, development helpers

## Running Tests

### Quick Validation
```bash
python run_tests.py --quick
```

### All Tests
```bash
python run_tests.py
```

### Specific Category
```bash
python run_tests.py --category unit
python run_tests.py --category integration
python run_tests.py --category functional
python run_tests.py --category debug
```

### Direct Test Runner
```bash
python tests/run_all_tests.py [options]
```

## Test Development Guidelines

### Adding New Tests
1. **Choose the appropriate category** based on the test type
2. **Follow naming convention**: `test_<component>_<functionality>.py`
3. **Include proper imports** and error handling
4. **Add docstrings** explaining what the test validates
5. **Return boolean** indicating success/failure

### Test Structure
```python
#!/usr/bin/env python3
"""
Test description and purpose.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_functionality():
    """Test specific functionality."""
    try:
        # Test implementation
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def main():
    """Main test runner."""
    success = test_functionality()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### Best Practices
- **Isolation**: Tests should be independent and not rely on other tests
- **Cleanup**: Clean up any resources created during testing
- **Error Handling**: Provide clear error messages for failures
- **Performance**: Keep tests fast, especially unit tests
- **Documentation**: Document complex test scenarios

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:
- **Unit tests** run on every commit
- **Integration tests** run on pull requests
- **Functional tests** run on releases
- **Debug tests** run manually as needed

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure project root is in Python path
2. **Missing dependencies**: Install required packages from `requirements.txt`
3. **API connection failures**: Check if Forge server is running
4. **Permission errors**: Ensure proper file permissions

### Debug Mode
For detailed debugging, run tests with verbose output:
```bash
python tests/run_all_tests.py --verbose
``` 