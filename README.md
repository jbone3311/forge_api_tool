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

### API Provider Selection & Testing Mode
The application supports seamless switching between **Mock** (testing) and **Real** API providers:

#### **Using Mock Mode (Recommended for Testing)**
1. Click on the **🔌 API** status in the header
2. Select **Mock (Testing Mode)** from the dropdown
3. Test your prompts, wildcards, and settings **without** calling real APIs
4. Perfect for:
   - 🧪 Testing prompt templates before production
   - 🎨 Validating wildcard combinations
   - ⚙️ Verifying configuration settings
   - 💰 Avoiding API costs during development

#### **Switching to Real APIs**
1. Click on the **🔌 API** status in the header
2. Choose your API provider:
   - **Local**: Automatic1111/Forge running locally
   - **RunDiffusion**: Cloud-based service
   - **ComfyUI**: Node-based interface
   - **Automatic1111 WebUI**: Popular web interface
3. Configure output folder and additional settings
4. Click **Save Settings** to apply changes

#### **Why This Approach Works**
✅ **Same Code Path**: Mock and real APIs use identical interfaces  
✅ **Safe Testing**: Validate everything before hitting real APIs  
✅ **Instant Switching**: Toggle between providers with one click  
✅ **Cost Control**: Test extensively in mock mode before production  
✅ **Debug Friendly**: See exactly what data would be sent to APIs  

#### **Configuration Options**
- **Output Folder**: Customize where images are saved (default: `outputs/`)
- **Auto-save Metadata**: Embed generation parameters in PNG files
- **Show API Logs**: Display request/response logs for debugging
- **Verify Before Send**: Show confirmation dialog before API calls

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
- **Advanced Linting**: Comprehensive validation and analysis (see below)

### Wildcard Linter & Analyzer 🆕
**Enterprise-grade wildcard validation with deep analysis capabilities:**

#### Features
- 🔍 **Empty Wildcard Detection**: Identifies files with no content or only whitespace
- 🔄 **Cycle Detection**: Finds circular references between wildcards (A → B → A)
- ⚖️ **Weight Sum Validation**: Verifies weighted wildcards sum to 1.0 for proper probability
- 📝 **Encoding Validation**: Detects UTF-8/UTF-16/BOM issues, mixed line endings, Windows CRLF
- 📊 **Frequency Analysis**: Per-token frequency reports with diversity metrics
- 🔧 **Auto-Fix Capability**: Automatically fixes encoding and formatting issues
- 💯 **Health Score**: Overall wildcard system health (0-100)
- 📈 **Dry-Run Mode**: Preview changes without applying them

#### CLI Usage
```bash
# Basic linting
python cli.py wildcards lint

# Verbose output with frequency reports
python cli.py wildcards lint --verbose

# Auto-fix issues
python cli.py wildcards lint --fix

# Strict mode (treat warnings as errors)
python cli.py wildcards lint --strict

# JSON output for automation
python cli.py wildcards lint --json

# Custom directory
python cli.py wildcards lint --wildcards-dir custom_wildcards
```

#### What It Detects

**Errors (Critical):**
- ❌ Empty wildcard files
- ❌ Non-UTF-8 encoding (UTF-16, etc.)
- ❌ Circular reference cycles
- ❌ Weight sums far from 1.0 (>0.1 difference)

**Warnings:**
- ⚠️ UTF-8 BOM markers (unnecessary)
- ⚠️ Mixed line endings (CRLF + LF)
- ⚠️ Duplicate items
- ⚠️ Weight sums slightly off (~0.9-1.1)

**Info:**
- ℹ️ Windows line endings (CRLF)
- ℹ️ Low diversity ratios

#### Example Output
```
🔍 WILDCARD LINTER RESULTS
================================================================================

💚 Health Score: 87/100
📁 Files Analyzed: 45
🚨 Total Issues: 8
   ❌ Errors: 2
   ⚠️  Warnings: 5
   ℹ️  Info: 1

📊 Issues by Category:
   • encoding: 3
   • format: 4
   • weight: 1

📈 Token Frequency Reports:
   📄 ACTIONS
      Total tokens: 156
      Unique tokens: 142
      Diversity: 91.03%
      Most common:
         • walking: 3x
         • running: 2x
         • jumping: 2x
```

#### Integration with Fix-Encoding
The linter extends the original encoding fix utility:
```bash
# Old: Just fix encoding
python cli.py wildcards fix-encoding

# New: Comprehensive linting + analysis
python cli.py wildcards lint --fix
```

## 🎨 CLIP Image to Wildcard Processor

### Overview
Convert inspiration images into wildcard files automatically using CLIP Interrogator. Perfect for building wildcard collections from reference images!

### Prerequisites
1. **Automatic1111 WebUI** running (default: `http://127.0.0.1:7860`)
2. **CLIP Interrogator Extension** installed:
   ```bash
   cd stable-diffusion-webui/extensions
   git clone https://github.com/pharmapsychotic/clip-interrogator-ext
   ```
3. Restart Automatic1111 WebUI

### Quick Start

#### Web Dashboard
1. Navigate to **CLIP Processor** page: `http://localhost:8081/clip`
2. Test API connection
3. Select input directory with images
4. Choose interrogation modes
5. Process images
6. Download generated wildcard files

#### CLI Usage
```bash
# Process a directory with subdirectories as themes
python -m core.clip_processor /path/to/images

# Single theme
python -m core.clip_processor /path/to/dog_images --theme dogs

# Specific modes only
python -m core.clip_processor /path/to/images --modes fast simple

# Test connection
python -m core.clip_processor --test
```

### Interrogation Modes

| Mode | Speed | Detail Level | Best For |
|------|-------|--------------|----------|
| **fast** | ⚡ Fastest | Basic | Quick previews, large batches |
| **simple** | 🚀 Fast | Moderate | General use, balanced |
| **detailed** | 🐌 Slow | High | Quality wildcards, styles |
| **best** | 🐌 Slowest | Highest | Maximum detail + tags |

### Directory Structure

Organize images in subdirectories for automatic theme detection:

```
inspiration/
├── dogs/
│   ├── golden_retriever1.jpg
│   ├── labrador1.jpg
│   └── husky1.jpg
├── cars/
│   ├── sports_car1.jpg
│   └── vintage_car1.jpg
└── landscapes/
    ├── mountain1.jpg
    └── sunset1.jpg
```

**Generated Output:**
```
wildcards/clip_generated/
├── dogs_fast.txt
├── dogs_simple.txt
├── dogs_detailed.txt
├── dogs_best.txt
├── cars_fast.txt
├── cars_simple.txt
├── cars_detailed.txt
└── cars_best.txt
```

### Example Workflow

1. **Collect Inspiration Images**
   - Browse Pinterest/ArtStation for reference images
   - Download to themed folders (e.g., `inspiration/cyberpunk/`)

2. **Process Through CLIP**
   ```bash
   python -m core.clip_processor inspiration/ --modes detailed best
   ```

3. **Review Generated Wildcards**
   - Check `wildcards/clip_generated/cyberpunk_detailed.txt`
   - Contains tags like: `neon lights`, `futuristic cityscape`, `cyberpunk aesthetic`

4. **Use in Prompts**
   ```
   __CYBERPUNK_DETAILED__ character in urban setting
   ```

### Features

- ✅ **Batch Processing**: Process hundreds of images automatically
- ✅ **Theme Detection**: Subdirectories become wildcard themes
- ✅ **Mode Selection**: Choose detail level per workflow
- ✅ **Deduplication**: Removes duplicate tags across images
- ✅ **Progress Tracking**: Real-time progress in web UI
- ✅ **Error Handling**: Graceful failures, continues on errors
- ✅ **Image Resizing**: Automatically resizes large images

### API Response Format

CLIP Interrogator returns prompts like:
```
"a golden retriever playing fetch in a sunny park, detailed fur, vibrant colors, outdoor scene"
```

The processor:
1. Splits by commas
2. Cleans tags (removes weights, parens)
3. Deduplicates across all images in theme
4. Saves to `theme_mode.txt`

### Performance Tips

- **GPU Recommended**: CLIP models are faster on GPU
- **Image Size**: Resize large images (>2MB) to speed up processing
- **Batch Size**: Process 10-20 images at a time for responsiveness
- **Mode Selection**: Use `fast` for previews, `detailed`/`best` for final

### Integration with Existing Wildcards

Generated wildcards integrate seamlessly:

```python
# In your prompts
prompt = "a __CLIP_DOGS_DETAILED__ in __ARTISTIC__ style"

# Expands to something like:
# "a golden retriever with playful expression in oil painting style"
```

### Troubleshooting

**"CLIP Interrogator extension not found"**
- Ensure extension is installed in `extensions/` folder
- Restart Automatic1111 WebUI
- Check Settings > CLIP Interrogator for configuration

**"API connection failed"**
- Verify Automatic1111 is running
- Check API URL in settings (default: `http://127.0.0.1:7860`)
- Test with curl: `curl http://127.0.0.1:7860/sdapi/v1/progress`

**"Processing is slow"**
- Use GPU instead of CPU
- Reduce image size
- Use `fast` or `simple` modes
- Process fewer images per batch

**"Generated wildcards have few tags"**
- Images may be too abstract/simple
- Try `detailed` or `best` modes
- Check image quality (low res = poor results)

### Wildcard Encoding Fix Utility
Built-in utility to fix encoding issues in wildcard files (now part of linter):

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

### Version 2.4 - CLIP Image to Wildcard Processor
- **CLIP Interrogator Integration**: Convert images to wildcard files using CLIP + BLIP models
- **Batch Image Processing**: Process entire directories with automatic theme detection
- **Multiple Interrogation Modes**: Fast, simple, detailed, and best modes for varying detail levels
- **Theme-Based Output**: Subdirectories automatically become themed wildcards (e.g., `dogs_fast.txt`)
- **Web Dashboard**: Beautiful UI for image processing with progress tracking
- **API Integration**: Seamless connection to Automatic1111 CLIP Interrogator extension
- **Auto-Deduplication**: Removes duplicate tags across images for cleaner wildcards

### Version 2.3 - Wildcard Linter & Advanced Analysis
- **Comprehensive Wildcard Linter**: Enterprise-grade validation with cycle detection, weight validation, and encoding checks
- **Token Frequency Analysis**: Per-wildcard frequency reports with diversity metrics
- **Auto-Fix Capability**: Automatically fix encoding, line endings, and formatting issues
- **Health Scoring**: Overall wildcard system health score (0-100)
- **Dry-Run Mode**: Preview changes before applying
- **CLI Integration**: New `wildcards lint` command with `--fix`, `--strict`, `--verbose`, and `--json` flags

### Version 2.2 - API Provider Management & Testing Mode
- **API Provider Selection UI**: Easy switching between Mock and Real APIs via dashboard
- **Testing Mode**: Test prompts and settings without calling real APIs (saves money!)
- **Unified API Interface**: Same code path for mock and real providers using Strategy Pattern
- **Output Folder Configuration**: Customize where generated images are saved
- **Enhanced Settings**: Auto-save metadata, API logs, and verification options
- **Smart Architecture**: Perfect for testing before production deployment

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