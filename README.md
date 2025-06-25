# Forge API Tool

A comprehensive tool for managing and automating image generation using the Forge API (Stable Diffusion WebUI). Features a web dashboard, batch processing, wildcard management, and centralized logging.

## 🚀 Features

- **Web Dashboard**: Modern Flask-based interface for managing configurations and monitoring generation
- **Batch Processing**: Queue-based system for processing multiple image generation jobs
- **Wildcard Management**: Dynamic prompt generation using wildcard substitution
- **Configuration Management**: JSON-based configuration system with validation
- **Centralized Logging**: Comprehensive logging system with structured output
- **API Integration**: Full integration with Forge/Stable Diffusion WebUI API
- **Output Management**: Organized file management with metadata tracking

## 📋 Requirements

- Python 3.8+
- Forge/Stable Diffusion WebUI running on `http://127.0.0.1:7860`
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

4. **Start Forge/Stable Diffusion WebUI**
   - Ensure your Forge server is running on `http://127.0.0.1:7860`
   - The tool will automatically connect to the API

## 🚀 Quick Start

### 1. Start the Web Dashboard
```bash
python web_dashboard/app.py
```
The dashboard will be available at `http://localhost:5000`

### 2. Test the Installation
```bash
# Test all imports
python simple_test.py

# Run comprehensive test suite
python run_all_tests.py
```

### 3. Create Your First Configuration
1. Open the web dashboard
2. Navigate to the Configurations section
3. Create a new configuration or use the provided templates
4. Ensure your wildcard files are in the `wildcards/` directory

## 📁 Project Structure

```
Forge-API-Tool/
├── core/                          # Core application modules
│   ├── __init__.py               # Package initialization
│   ├── config_handler.py         # Configuration management
│   ├── forge_api.py              # Forge API client
│   ├── centralized_logger.py     # Centralized logging system
│   ├── output_manager.py         # Output file management
│   ├── job_queue.py              # Job queue management
│   ├── batch_runner.py           # Batch processing
│   ├── wildcard_manager.py       # Wildcard management
│   ├── prompt_builder.py         # Prompt generation
│   └── image_analyzer.py         # Image analysis utilities
├── web_dashboard/                 # Web interface
│   ├── app.py                    # Flask application
│   ├── templates/                # HTML templates
│   └── static/                   # CSS/JS assets
├── configs/                       # Configuration templates
├── wildcards/                     # Wildcard files
├── outputs/                       # Generated images
├── logs/                          # Application logs
├── tests/                         # Test suite
└── docs/                          # Documentation
```

## 🔧 Configuration

### Configuration Files
Configuration files are stored in JSON format in the `configs/` directory. Each configuration includes:

- **Model Settings**: Checkpoint, VAE, text encoder
- **Generation Settings**: Steps, sampler, dimensions, batch size
- **Prompt Settings**: Base prompt template with wildcards
- **Output Settings**: Directory structure and file formats
- **API Settings**: Connection parameters

### Wildcard System
The tool uses a wildcard system for dynamic prompt generation:

- Wildcard files are stored in `wildcards/` directory
- Format: `__WILDCARD_NAME__` in prompt templates
- Automatic rotation and usage tracking
- Support for nested wildcard directories

### Example Configuration
```json
{
  "name": "Portrait Art",
  "model_type": "sd",
  "model_settings": {
    "checkpoint": "sd-v1-5.safetensors"
  },
  "generation_settings": {
    "steps": 20,
    "sampler": "Euler a",
    "width": 512,
    "height": 512
  },
  "prompt_settings": {
    "base_prompt": "a portrait of __PERSON__ in __STYLE__, __LIGHTING__",
    "negative_prompt": "low quality, blurry"
  }
}
```

## 🎯 Usage

### Web Dashboard
1. **Dashboard Overview**: View system status, queue, and recent outputs
2. **Configuration Management**: Create, edit, and validate configurations
3. **Batch Generation**: Queue and monitor batch jobs
4. **Output Management**: Browse, export, and manage generated images
5. **Logs**: View application logs and system events

### API Endpoints
The web dashboard provides RESTful API endpoints:

- `GET /api/status` - System status
- `GET /api/configs` - List configurations
- `POST /api/generate` - Generate single image
- `POST /api/batch` - Start batch generation
- `GET /api/outputs` - List outputs
- `GET /api/logs` - View logs

### Command Line
```bash
# Test API connection
python -c "from core.forge_api import forge_api_client; print(forge_api_client.test_connection())"

# List configurations
python -c "from core.config_handler import config_handler; print(config_handler.list_configs())"

# Generate test image
python -c "from core.forge_api import forge_api_client; from core.config_handler import config_handler; config = config_handler.load_config('Quick Start'); success, image, info = forge_api_client.generate_image(config, 'a beautiful landscape'); print('Success:', success)"
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

## 📊 Logging

The application uses a centralized logging system with structured output:

### Log Categories
- **Application Events**: System startup, configuration changes
- **API Requests**: Forge API calls and responses
- **Performance Metrics**: Generation times and throughput
- **Error Tracking**: Detailed error information
- **Output Events**: File creation and management

### Log Locations
- `logs/app/` - Application logs
- `logs/api/` - API request logs
- `logs/performance/` - Performance metrics
- `logs/errors/` - Error logs
- `logs/outputs/` - Output-related logs

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   - ✅ **Fixed**: All import issues have been resolved
   - Run `python simple_test.py` to verify

2. **API Connection Issues**
   - Ensure Forge server is running on `http://127.0.0.1:7860`
   - Check firewall settings
   - Verify API endpoints are accessible

3. **Configuration Errors**
   - Validate configuration files using the web dashboard
   - Check wildcard file paths
   - Ensure all required fields are present

4. **Performance Issues**
   - Monitor logs in `logs/performance/`
   - Adjust batch sizes and generation parameters
   - Check system resources

### Debug Mode
```bash
# Enable debug logging
export FORGE_API_DEBUG=1
python web_dashboard/app.py
```

## 🚀 Recent Improvements

### Import System Overhaul (Latest)
- ✅ Fixed all "cannot import name" errors
- ✅ Added proper package structure with `__init__.py`
- ✅ Implemented relative imports within core package
- ✅ Added global instances for all core modules
- ✅ Fixed constructor parameter issues
- ✅ Updated logger references to use centralized logger

### Centralized Logging System
- ✅ Structured logging with categories
- ✅ Performance metrics tracking
- ✅ Error tracking and debugging
- ✅ Output event logging

### Web Dashboard Enhancements
- ✅ Real-time status updates
- ✅ Configuration management interface
- ✅ Batch job monitoring
- ✅ Output browsing and management
- ✅ Log viewing and cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `logs/` directory
3. Run the test suite to identify issues
4. Create an issue with detailed information

## 📈 Roadmap

- [ ] Advanced wildcard management with GUI
- [ ] Template sharing and import/export
- [ ] Advanced scheduling and automation
- [ ] Multi-server support
- [ ] Performance optimization
- [ ] Mobile-responsive dashboard
- [ ] Plugin system for custom functionality

---

**Last Updated**: June 2024
**Version**: 2.0.0
**Status**: ✅ Production Ready 