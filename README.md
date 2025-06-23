# Forge API Tool - Web Dashboard

A web-based dashboard for managing batch image generation using Forge's API with intelligent wildcard management and smart randomization.

## Features

- 🎯 **Smart Wildcard Management**: Starts from random position, cycles through all items before repeating
- 📊 **Wildcard Usage Stats**: Track usage frequency and avoid overuse
- 👀 **Wildcard Preview**: Preview generated prompts before execution
- 📁 **Config Management**: Upload, edit, and manage JSON configuration files
- 🔄 **Batch Processing**: Sequential execution of multiple config files
- 📈 **Real-time Monitoring**: Live status updates and progress tracking
- 🖼️ **Image Analysis**: Drag-and-drop to extract settings from existing images

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Wildcards**:
   - Place your wildcard `.txt` files in the `wildcards/` directory
   - Example: `wildcards/animals.txt`, `wildcards/locations.txt`

3. **Create Configs**:
   - Add JSON configuration files to `configs/` directory
   - Use `configs/template.json` as a starting point

4. **Run the Dashboard**:
   ```bash
   python web_dashboard/app.py
   ```

5. **Access Dashboard**:
   - Open browser to `http://localhost:5000`

## Directory Structure

```
Forge-API-Tool/
├── web_dashboard/          # Flask web application
│   ├── static/            # CSS, JS, images
│   ├── templates/         # HTML templates
│   └── app.py            # Main Flask app
├── configs/              # JSON configuration files
├── wildcards/            # Wildcard .txt files
├── outputs/              # Generated images and logs
├── core/                 # Core Python modules
├── queue.json           # Persistent job queue
├── wildcard_usage.json  # Usage statistics
└── requirements.txt     # Python dependencies
```

## Configuration

Each JSON config file supports:
- Model settings (SD, SDXL, Flux)
- Prompt templates with wildcards
- Generation parameters
- Output settings
- ControlNet and LoRA support

## Wildcard System

The smart wildcard system:
- Starts from a random position in each wildcard file
- Cycles through all items once before repeating
- Tracks usage statistics to avoid overuse
- Provides preview functionality

## API Integration

Connects directly to Forge's API for:
- Text-to-image generation
- Image-to-image processing
- Batch processing with proper error handling

## License

MIT License - see LICENSE file for details 