# Forge API Tool

A modern web-based client application for managing and automating image generation using external AI image generation APIs (Automatic1111, ComfyUI, etc.). Features a beautiful Bootstrap 5 dashboard, template management, and comprehensive settings.

## 🚀 Features

- **Modern Web Dashboard**: Beautiful Bootstrap 5 interface for managing image generation
- **Template System**: Create and manage prompt templates with dynamic variables
- **External API Support**: Connect to Automatic1111, ComfyUI, and other image generation APIs
- **Settings Management**: Comprehensive configuration system with import/export
- **Output Gallery**: View and manage generated images with filtering
- **Real-time Status**: Monitor generation progress and system status
- **Template Validation**: Built-in validation and caching for templates
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

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
python run_all_tests.py
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
├── configs/                       # Configuration templates
├── wildcards/                     # Wildcard files
├── outputs/                       # Generated images
├── logs/                          # Application logs
├── tests/                         # Test suite
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

## 📊 Logging

The application uses a centralized logging system with structured output:

### Log Categories
- **Application Events**: System startup, configuration changes
- **API Requests**: External API calls and responses
- **Performance Metrics**: Generation times and throughput
- **Error Tracking**: Detailed error information

## 🔄 Recent Updates

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