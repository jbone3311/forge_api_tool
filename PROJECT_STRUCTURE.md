# Forge API Tool - Project Structure

This document outlines the organized structure of the Forge API Tool project.

## Root Directory

### Core Files
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog and version history
- `LICENSE` - Project license
- `requirements.txt` - Python dependencies
- `quick_start.sh` - Quick start script

### Configuration
- `config/` - Configuration files directory
  - `rundiffusion_config.json` - RunDiffusion API configuration
  - `api_preference.json` - API preference settings
  - `wildcard_usage.json` - Wildcard usage statistics
  - `queue.json` - Job queue data

### Documentation
- `docs/` - Comprehensive documentation
  - `README.md` - Documentation index
  - `development/` - Development and refactoring documentation
  - `features/` - Feature-specific documentation
  - `testing/` - Testing documentation
  - `cleanup/` - Cleanup and maintenance documentation

### Core Application
- `core/` - Core application modules
  - `__init__.py`
  - `api_config.py` - API configuration management
  - `batch_runner.py` - Batch processing functionality
  - `centralized_logger.py` - Centralized logging system
  - `config_handler.py` - Configuration handling
  - `exceptions.py` - Custom exception classes
  - `forge_api.py` - Forge API client
  - `image_analyzer.py` - Image analysis functionality
  - `job_queue.py` - Job queue management
  - `logger.py` - Logging utilities
  - `output_manager.py` - Output file management
  - `prompt_builder.py` - Prompt building utilities
  - `wildcard_manager.py` - Wildcard management

### Web Dashboard
- `web_dashboard/` - Web interface
  - `app.py` - Flask application
  - `templates/` - HTML templates
    - `dashboard.html` - Main dashboard
    - `test-dashboard.html` - Test interface
  - `static/` - Static assets
    - `css/` - Stylesheets
    - `js/` - JavaScript files
      - `modules/` - Modular JavaScript components
  - `__tests__/` - JavaScript tests
  - `e2e/` - End-to-end tests
  - `coverage/` - Test coverage reports
  - `test-results/` - Test results
  - `test-reports/` - Test reports
  - `package.json` - Node.js dependencies
  - `README-TESTING.md` - Testing documentation

### Testing
- `tests/` - Python test suite
  - `__init__.py`
  - `unit/` - Unit tests
  - `integration/` - Integration tests
  - `functional/` - Functional tests
  - `fixtures/` - Test fixtures
  - `debug/` - Debug test utilities
  - `logs/` - Test logs
  - `outputs/` - Test outputs
  - `run_tests.py` - Test runner
  - `comprehensive_test_results.json` - Test results

### Templates and Configurations
- `configs/` - Configuration templates
  - Various JSON configuration files for different models and styles

### Wildcards
- `wildcards/` - Wildcard prompt files
  - `actions.txt` - Action wildcards
  - `artistic.txt` - Artistic style wildcards
  - `camera.txt` - Camera settings wildcards
  - `composition.txt` - Composition wildcards
  - `expression.txt` - Expression wildcards
  - `medium.txt` - Medium wildcards
  - `mood.txt` - Mood wildcards
  - `people.txt` - People wildcards
  - `person.txt` - Person wildcards
  - `pose.txt` - Pose wildcards
  - `setting.txt` - Setting wildcards
  - `subject.txt` - Subject wildcards
  - `weather.txt` - Weather wildcards
  - `ClipOutput/` - ClipOutput wildcard sets
  - `PromptSets/` - Prompt set collections
  - `Sort/` - Organized wildcard collections

### Utilities and Scripts
- `scripts/` - Utility scripts
  - `fix_wildcard_encoding.py` - Comprehensive wildcard encoding fix utility

### Data and Outputs
- `outputs/` - Generated images and outputs
- `logs/` - Application logs
- `cache/` - Cache files

### Virtual Environment
- `venv/` - Python virtual environment

## File Organization Principles

### 1. **Separation of Concerns**
- Core application logic in `core/`
- Web interface in `web_dashboard/`
- Configuration in `config/`
- Documentation in `docs/`

### 2. **Testing Structure**
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Functional tests in `tests/functional/`
- JavaScript tests in `web_dashboard/__tests__/`
- E2E tests in `web_dashboard/e2e/`

### 3. **Configuration Management**
- All configuration files in `config/`
- Template configurations in `configs/`
- Environment-specific settings properly isolated

### 4. **Documentation Organization**
- Development docs in `docs/development/`
- Feature docs in `docs/features/`
- Testing docs in `docs/testing/`
- Cleanup docs in `docs/cleanup/`

### 5. **Asset Organization**
- Static assets in `web_dashboard/static/`
- Templates in `web_dashboard/templates/`
- Wildcards organized by category in `wildcards/`

## Maintenance Guidelines

### Adding New Files
1. Place files in the appropriate directory based on their purpose
2. Update this document when adding new directories or major file categories
3. Follow the established naming conventions

### Configuration Files
- All configuration files should go in `config/`
- Use descriptive names with `.json` extension
- Document configuration options in `docs/`

### Testing
- Add tests in the appropriate test directory
- Follow the existing test naming conventions
- Update test documentation as needed

### Documentation
- Add new documentation to the appropriate `docs/` subdirectory
- Update the `docs/README.md` index
- Keep documentation up to date with code changes 