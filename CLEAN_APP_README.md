# 🎯 Forge API Tool - Clean Application

A clean, organized interface for the Forge API Tool with enhanced wildcard management and automatic browser launching.

## ✨ Features

- **🎲 Enhanced Wildcard Management**: Automatically discovers all `.txt` files in the wildcards directory
- **🌐 Clean Web Interface**: Modern, organized dashboard with wildcard file browser
- **📡 Multiple API Providers**: Support for Local Forge, RunDiffusion, ComfyUI, and Automatic1111
- **⚡ Real-time Progress**: Live generation progress tracking
- **🔧 Configuration Management**: Easy config switching and management
- **📁 Output Management**: Organized output file management
- **🚀 Auto-Launch**: Automatically opens browser when starting

## 🚀 Quick Start

### Option 1: Direct Launch (Recommended)
```bash
cd web_dashboard
python clean_app.py
```
The browser will open automatically at `http://localhost:8080`

### Option 2: Using Launcher Script
```bash
python launch_app.py
```

### Option 3: Windows Batch File
Double-click `launch_app.bat`

## 🎲 Wildcard System

The enhanced wildcard system automatically discovers all `.txt` files in the `wildcards/` directory:

- **Automatic Discovery**: Scans all subdirectories for `.txt` files
- **Smart Naming**: Converts file paths to wildcard variables (e.g., `wildcards/subject.txt` → `__SUBJECT__`)
- **Interactive Interface**: Click on wildcard files to view contents and use in prompts
- **Live Preview**: See prompt variations before generation
- **Usage Tracking**: Track which wildcard items have been used

### Using Wildcards in Prompts

1. **View Available Wildcards**: The dashboard shows all discovered wildcard files
2. **Browse Contents**: Click "View Items" to see all options in a wildcard file
3. **Use in Prompts**: Click "Use in Prompt" to add the wildcard variable
4. **Select Specific Items**: Click on individual items to replace wildcard variables
5. **Process Prompts**: Use "Process Wildcards" to see variations

Example prompt template:
```
A beautiful __SUBJECT__ in a __SETTING__ with __MOOD__ lighting, __CAMERA__ shot
```

## 🎨 Interface Features

### Wildcard Management Panel
- **Grid View**: All wildcard files displayed in organized cards
- **Search**: Filter wildcard files by name
- **Preview**: See sample items from each wildcard file
- **Quick Actions**: View items or add to prompt with one click

### Prompt Builder
- **Template Input**: Enter prompts with wildcard variables
- **Live Processing**: See processed prompts with actual values
- **Preview Variations**: Generate multiple prompt variations
- **Validation**: Check if wildcard variables are available

### Generation Controls
- **Configuration Selection**: Choose from available configs
- **Parameter Adjustment**: Fine-tune steps, CFG scale, dimensions
- **Real-time Queue**: See generation progress and status

## 📁 File Organization

```
Forge-API-Tool/
├── web_dashboard/
│   ├── clean_app.py          # Main application
│   ├── templates/
│   │   └── clean_dashboard.html  # Clean interface
│   └── static/               # CSS/JS files
├── core/                     # Core modules
│   ├── enhanced_wildcard_manager.py
│   ├── enhanced_prompt_builder.py
│   ├── mock_forge_api.py
│   └── ...
├── wildcards/                # Wildcard files (auto-discovered)
├── configs/                  # Configuration files
├── outputs/                  # Generated images
└── launch_app.py            # Launcher script
```

## 🔧 API Providers

The application supports multiple mock API providers:

- **Local Forge**: Local Forge installation simulation
- **RunDiffusion**: RunDiffusion cloud service simulation  
- **ComfyUI**: ComfyUI workflow simulation
- **Automatic1111**: Automatic1111 web UI simulation

Switch providers using the interface or API calls.

## ⚠️ Important Notes

- **Mock Mode**: All image generation is simulated - no real API calls are made
- **Development Server**: Uses Flask development server (not for production)
- **Auto-Browser**: Automatically opens browser when starting (configurable)

## 🎯 Usage Examples

### Basic Prompt Generation
1. Open the application
2. Enter a prompt template: `A __SUBJECT__ in __SETTING__`
3. Click "Process Wildcards" to see variations
4. Adjust generation parameters
5. Click "Generate Image"

### Advanced Wildcard Usage
1. Browse wildcard files in the grid
2. Click "View Items" on any wildcard
3. Select specific items to use
4. Build complex prompts with multiple wildcards
5. Generate with different configurations

### Batch Generation
- Use the prompt builder to create multiple variations
- Switch between different configurations
- Monitor progress in the queue panel

## 🛠️ Development

The clean application focuses on core functionality:

- **No Test Files**: All testing infrastructure removed
- **Organized Structure**: Clean, minimal file organization
- **Enhanced Wildcards**: Automatic discovery and management
- **Modern Interface**: Clean, responsive web design
- **Real-time Updates**: WebSocket-based live updates

## 📞 Support

The application is designed to be self-explanatory with:
- **Intuitive Interface**: Clear labels and organization
- **Helpful Tooltips**: Context-sensitive information
- **Error Handling**: Graceful error messages
- **Live Feedback**: Real-time status updates

---

**🎯 Enjoy your clean, organized Forge API Tool experience!**
