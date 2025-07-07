# Forge API Tool

A modern web-based client application for managing and automating image generation using external AI image generation APIs (Automatic1111, ComfyUI, etc.). Features a beautiful Bootstrap 5 dashboard, template management, and comprehensive settings. Features advanced wildcard management with encoding fix utilities.

## 🚀 Features

- **Modern Web Dashboard**: Beautiful Bootstrap 5 interface for managing image generation
- **Template System**: Create and manage prompt templates with dynamic variables
- **External API Support**: Connect to Automatic1111, ComfyUI, and other image generation APIs
- **Settings Management**: Comprehensive configuration system with import/export
- **Output Gallery**: View and manage generated images with filtering
- **Real-time Status**: Monitor generation progress and system status
- **Template Validation**: Built-in validation and caching for templates
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Wildcard Management**: Advanced wildcard system with encoding fix utilities
- **Maintenance Tools**: Built-in utilities for system maintenance and troubleshooting

## 📋 Requirements

- Python 3.8+
- External image generation API (Automatic1111, ComfyUI, etc.)
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Forge-API-Tool
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start your image generation API**
   - Automatic1111: `http://127.0.0.1:7860`
   - ComfyUI: `http://127.0.0.1:8188`
   - Or any other compatible API

## 🚀 Quick Start

### 1. Start the Bootstrap Dashboard
```bash
cd web_dashboard
python app_bootstrap.py
```
The dashboard will be available at `http://localhost:5000`

### 2. Alternative: Use the Startup Script
```bash
cd web_dashboard
python run_bootstrap.py
```

### 3. Test the Installation
```bash
# Test all imports
python simple_test.py

# Run comprehensive test suite
python tests/run_enhanced_tests.py

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/security/      # Security tests only
python -m pytest tests/performance/   # Performance tests only
```

### 4. Fix Wildcard Encoding (if needed)
```bash
# Check for encoding issues
python cli.py wildcards fix-encoding --dry-run

# Fix encoding issues
python cli.py wildcards fix-encoding
```

## 📁 Project Structure

```
Forge-API-Tool/
├── core/                          # Core application modules
│   ├── __init__.py               # Package initialization
│   ├── config_handler.py         # Configuration management
│   ├── forge_api.py              # External API client
│   ├── centralized_logger.py     # Centralized logging system
│   ├── output_manager.py         # Output file management
│   ├── job_queue.py              # Job queue management
│   ├── batch_runner.py           # Batch processing
│   ├── wildcard_manager.py       # Wildcard management
│   ├── prompt_builder.py         # Prompt generation
│   └── image_analyzer.py         # Image analysis utilities
├── web_dashboard/                 # Web interface
│   ├── app_bootstrap.py          # Bootstrap 5 Flask application
│   ├── run_bootstrap.py          # Startup script
│   ├── BOOTSTRAP_README.md       # Bootstrap dashboard documentation
│   ├── templates/                # HTML templates
│   │   ├── dashboard_bootstrap.html
│   │   └── modals/              # Modal templates
│   └── static/                   # CSS/JS assets
│       └── js/
│           └── dashboard_bootstrap.js
├── scripts/                       # Utility scripts
│   └── fix_wildcard_encoding.py  # Wildcard encoding fix utility
├── configs/                       # Configuration templates
├── wildcards/                     # Wildcard files
├── outputs/                       # Generated images
├── logs/                          # Application logs
├── tests/                         # Comprehensive test suite
│   ├── unit/                     # Unit tests
│   ├── functional/               # Integration tests
│   ├── security/                 # Security tests
│   ├── performance/              # Performance tests
│   ├── property/                 # Property-based tests
│   ├── stress/                   # Stress tests
│   └── run_enhanced_tests.py     # Enhanced test runner
└── docs/                          # Documentation
```

## 🎨 Dashboard Features

### Modern Bootstrap 5 Interface
- **Responsive Design**: Works on all devices
- **Dark/Light Theme**: Toggle between themes
- **Real-time Updates**: Live status and progress monitoring
- **Modal System**: Clean, organized interface with modal dialogs

### Template Management
- **Create Templates**: Build reusable prompt templates
- **Variable System**: Use `{{variable}}` syntax for dynamic content
- **Import/Export**: Share templates with JSON import/export
- **Validation**: Built-in template validation and error checking
- **Cache Management**: Optimize performance with template caching

### Settings & Configuration
- **API Connections**: Configure multiple external APIs
- **Output Management**: Set output directories and file formats
- **System Preferences**: Customize dashboard behavior
- **Template Settings**: Manage template collections and defaults

### Output Gallery
- **Image Filtering**: View only image files
- **Thumbnail Preview**: Quick image previews
- **Download Management**: Easy file downloads
- **Metadata Display**: View generation parameters

## 🔧 Configuration

### Template System
The dashboard uses a modern template system for dynamic prompt generation:

```json
{
  "name": "Portrait Template",
  "description": "Professional portrait generation",
  "prompt": "a professional portrait of {{person}} in {{style}} style, {{lighting}} lighting, high quality, detailed",
  "negative_prompt": "low quality, blurry, distorted",
  "variables": {
    "person": ["man", "woman", "child"],
    "style": ["realistic", "artistic", "photographic"],
    "lighting": ["studio", "natural", "dramatic"]
  }
}
```

### API Configuration
Connect to external image generation APIs:

```json
{
  "api_type": "automatic1111",
  "base_url": "http://127.0.0.1:7860",
  "timeout": 300,
  "retry_attempts": 3
}
```

## 🎯 Usage

### Dashboard Navigation
1. **Home**: Overview of system status and recent activity
2. **Generate**: Create images using templates and custom prompts
3. **Templates**: Manage your prompt templates
4. **Outputs**: Browse generated images
5. **Settings**: Configure APIs, preferences, and system options

### Template Creation
1. Navigate to Templates section
2. Click "Create New Template"
3. Define your prompt with variables using `{{variable}}` syntax
4. Add variable options and descriptions
5. Save and use for generation

### Image Generation
1. Select a template or create a custom prompt
2. Fill in variable values
3. Configure generation parameters
4. Click "Generate" to start the process
5. Monitor progress in real-time

## 🧪 Testing

### Comprehensive Test Suite
The project includes an enterprise-grade testing infrastructure with multiple testing methodologies:

#### **Test Categories**
- **Unit Tests**: Core functionality testing (71% success rate)
- **Integration Tests**: End-to-end functionality testing
- **Security Tests**: Vulnerability and security validation
- **Performance Tests**: Performance regression detection
- **Property-Based Tests**: Edge case testing with Hypothesis
- **Stress Tests**: System stability under load
- **Accessibility Tests**: Web accessibility compliance (100% success rate)
- **Load Tests**: Performance under concurrent load (91% success rate)
- **Mutation Tests**: Code quality verification

#### **Advanced Testing Features**
- **Enhanced Test Runner**: Comprehensive test orchestration with detailed reporting
- **Benchmark Tracking**: Historical performance comparison
- **Timeout Handling**: Graceful test timeout management
- **Parallel Execution**: Support for concurrent test execution
- **Detailed Analytics**: JSON-based test results with metrics

#### **Running Tests**
```bash
# Run all tests with enhanced reporting
python tests/run_enhanced_tests.py

# Run specific test categories
python -m pytest tests/unit/          # Unit tests
python -m pytest tests/security/      # Security tests
python -m pytest tests/performance/   # Performance tests
python -m pytest tests/functional/    # Integration tests

# Run with coverage
python -m pytest --cov=core --cov-report=html tests/
```

#### **Test Results**
- **Detailed Results**: `tests/enhanced_test_results.json`
- **Coverage Reports**: `htmlcov/` (when using coverage)
- **Test Summary**: `tests/ENHANCED_TESTING_SUMMARY.md`

## 🔧 Wildcard Management

### Wildcard System
The application includes a comprehensive wildcard management system for dynamic prompt generation:

- **Automatic1111 Format**: Uses `__WILDCARD_NAME__` syntax
- **File-based Wildcards**: Each wildcard is stored in `wildcards/wildcard_name.txt`
- **Recursive Scanning**: Automatically finds all wildcard files in subdirectories
- **Encoding Support**: Handles UTF-8, UTF-16, and UTF-16-BE encodings

### Wildcard Encoding Fix Utility
Built-in utility to fix encoding issues in wildcard files:

#### CLI Usage
```bash
# Check for encoding issues (dry run)
python cli.py wildcards fix-encoding --dry-run

# Fix encoding issues
python cli.py wildcards fix-encoding

# Use custom wildcards directory
python cli.py wildcards fix-encoding --wildcards-dir custom_wildcards
```

#### Web Interface
1. Open the web dashboard
2. Click Settings (gear icon)
3. Navigate to "Wildcard Encoding Fix" section
4. Use "Check Encoding" to preview issues
5. Use "Fix Encoding" to apply fixes
6. View detailed results and statistics

#### Features
- **Comprehensive Scanning**: Recursively scans all `.txt` files
- **Multiple Encoding Support**: Detects and fixes UTF-16, UTF-16-BE, and UTF-8
- **Safety Mode**: Dry-run option to preview changes
- **Detailed Reporting**: Shows fixed files, skipped files, and errors
- **Verification**: Confirms files are readable after fixing
- **Real-time Feedback**: Live progress and results display

### Wildcard File Structure
```
wildcards/
├── actions.txt              # Action wildcards
├── artistic.txt             # Artistic style wildcards
├── camera.txt               # Camera and photography wildcards
├── weather.txt              # Weather condition wildcards
├── ClipOutput/              # Clip-specific wildcards
│   ├── Colorful_Photoshoot_best_Prompts.txt
│   └── ...
├── Sort/                    # Organized wildcard collections
│   ├── art_styles/
│   ├── characters/
│   ├── emotions/
│   └── ...
└── PromptSets/              # Prompt set collections
    └── RavenSky/
```

## 🛠️ Maintenance Tools

### System Maintenance
The application includes several maintenance utilities:

- **Wildcard Encoding Fix**: Fix encoding issues in wildcard files
- **Cache Management**: Clear and manage application cache
- **Log Management**: View, download, and clear application logs
- **System Status**: Monitor system health and performance

### CLI Maintenance Commands
```bash
# System status
python cli.py status

# Clear cache
python cli.py cleanup

# View logs
python cli.py logs

# Test API connection
python cli.py test
```

## 🧪 Testing

### Run All Tests
```bash
python run_all_tests.py
```

### Individual Test Suites
```bash
# Test imports
python simple_test.py

# Test specific modules
python tests/test_config_handler.py
python tests/test_forge_api.py
python tests/test_integration.py
```

### Test Coverage
- ✅ Import testing
- ✅ Configuration validation
- ✅ API connectivity
- ✅ Wildcard management
- ✅ Output management
- ✅ Job queue functionality
- ✅ Web dashboard functionality
- ✅ Wildcard encoding fix utilities

## 📊 Logging

The application uses a centralized logging system with structured output:

### Log Categories
- **Application Events**: System startup, configuration changes
- **API Requests**: External API calls and responses
- **Performance Metrics**: Generation times and throughput
- **Error Tracking**: Detailed error information
- **Maintenance Operations**: Wildcard encoding fixes, cache clearing, etc.

## 🔄 Recent Updates

### Version 2.1 - Wildcard Management & Maintenance
- **Wildcard Encoding Fix**: Comprehensive utility to fix encoding issues in wildcard files
- **CLI Integration**: New `wildcards fix-encoding` command with dry-run support
- **Web Interface**: Settings modal with wildcard encoding fix functionality
- **Maintenance Tools**: Enhanced system maintenance and troubleshooting utilities
- **Improved Documentation**: Updated README with wildcard management and maintenance sections

### Version 2.0 - Complete Refactor
- **Removed Internal API**: Now a pure client application
- **Bootstrap 5 Dashboard**: Modern, responsive web interface
- **Template System**: Advanced template management with variables
- **Clean Architecture**: Simplified codebase with better organization
- **Enhanced Testing**: Comprehensive unit test coverage

### Key Improvements
- Modern Bootstrap 5 UI with responsive design
- Template-based prompt generation system
- External API support (Automatic1111, ComfyUI, etc.)
- Comprehensive settings management
- Real-time status monitoring
- Image-only output gallery
- Template validation and caching
- Advanced wildcard management with encoding fix utilities
- Built-in maintenance and troubleshooting tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in the `docs/` directory
- Review the test files for usage examples
- Open an issue on GitHub

---

**Forge API Tool** - Modern image generation management with a beautiful web interface! 🎨✨