# CLIP Image to Wildcard Processor - Complete Guide

## 🎯 Overview

The **CLIP Image to Wildcard Processor** is a powerful tool that converts inspiration images into usable wildcard files automatically. It uses CLIP Interrogator to extract semantic information from images and generate descriptive tags perfect for prompt engineering.

**Perfect for:**
- 🎨 Building themed wildcard collections from reference images
- 📸 Converting Pinterest/ArtStation boards into prompt libraries
- 🔄 Automating wildcard creation from existing image datasets
- 🧪 Testing different CLIP modes for optimal results

## 🏗️ Architecture

```
User Images → CLIP Processor → CLIP Interrogator API → Tagged Prompts → Wildcard Files
```

**Components:**
1. **CLIPProcessor** (`core/clip_processor.py`): Core processing engine
2. **CLIPService** (`web_dashboard/services/clip_service.py`): Service layer for web dashboard
3. **CLIP Routes** (`web_dashboard/routes/clip_routes.py`): Flask API endpoints
4. **CLIP Dashboard** (`templates/clip_dashboard.html`): Web UI

## 🚀 Installation

### Prerequisites

1. **Automatic1111 WebUI** must be running
2. **CLIP Interrogator Extension** must be installed

```bash
# Install CLIP Interrogator extension
cd /path/to/stable-diffusion-webui/extensions
git clone https://github.com/pharmapsychotic/clip-interrogator-ext

# Restart Automatic1111 WebUI
```

### First-Time Setup

When you first run CLIP Interrogator, it will download ~4-6GB of models:
- CLIP ViT-L/14 (~1GB)
- BLIP base (~1GB)
- Additional model weights

This is a one-time download. Subsequent runs are much faster.

## 📖 Usage Guide

### Web Dashboard Method (Recommended)

1. **Start the Dashboard**
   ```bash
   python web_dashboard/clean_app.py
   ```

2. **Navigate to CLIP Processor**
   - Open `http://localhost:8081/clip`
   - Or click "CLIP Processor" link from main dashboard

3. **Test Connection**
   - Click "Test Connection" button
   - Verify:
     - ✅ API Connected
     - ✅ CLIP Interrogator Installed

4. **Prepare Your Images**
   ```
   inspiration/
   ├── dogs/
   │   ├── img1.jpg
   │   └── img2.jpg
   └── cars/
       ├── img1.jpg
       └── img2.jpg
   ```

5. **Process Images**
   - Enter path: `/path/to/inspiration`
   - Select modes: Fast, Simple, Detailed, Best
   - Check "Process subdirectories as separate themes"
   - Click "🚀 Process Images"

6. **Download Wildcards**
   - View generated files in dashboard
   - Click "⬇️ Download" for each wildcard file
   - Files saved to `wildcards/clip_generated/`

### CLI Method

#### Basic Usage

```bash
# Process directory with subdirectories as themes
python -m core.clip_processor /path/to/inspiration

# Output:
# wildcards/clip_generated/dogs_fast.txt
# wildcards/clip_generated/dogs_simple.txt
# wildcards/clip_generated/dogs_detailed.txt
# wildcards/clip_generated/dogs_best.txt
# ...
```

#### Advanced Options

```bash
# Single theme (no subdirectories)
python -m core.clip_processor /path/to/dog_images \
    --theme dogs \
    --no-recursive

# Specific modes only
python -m core.clip_processor /path/to/images \
    --modes fast simple

# Custom API URL
python -m core.clip_processor /path/to/images \
    --api-url http://192.168.1.100:7860

# Custom output directory
python -m core.clip_processor /path/to/images \
    --output-dir ./custom_wildcards

# Test connection only
python -m core.clip_processor --test
```

## 🎨 Interrogation Modes Explained

### fast
- **Speed**: ⚡⚡⚡ ~2-5 seconds per image
- **Detail**: Basic captions only (BLIP)
- **Output**: `"a dog playing in a park"`
- **Best for**: 
  - Quick previews
  - Large batches (100+ images)
  - Getting general themes
  - Initial testing

### simple
- **Speed**: 🚀🚀 ~5-10 seconds per image
- **Detail**: BLIP + basic CLIP tags
- **Output**: `"a dog playing in a park, outdoor scene, daytime"`
- **Best for**:
  - General purpose use
  - Balanced speed/quality
  - Most common use case
  - Production wildcards

### detailed
- **Speed**: 🐌 ~15-30 seconds per image
- **Detail**: BLIP + full CLIP vocabulary scan
- **Output**: `"a golden retriever playing fetch in a park, outdoor scene, daytime, vibrant colors, detailed fur"`
- **Best for**:
  - High-quality wildcards
  - Style-focused collections
  - Artistic references
  - Final output

### best
- **Speed**: 🐌🐌 ~30-60 seconds per image
- **Detail**: BLIP + CLIP + DeepDanbooru tags
- **Output**: `"a golden retriever playing fetch in a park, outdoor scene, daytime, vibrant colors, detailed fur, 1dog, solo, outdoor"`
- **Best for**:
  - Maximum detail needed
  - Anime/character art
  - Tag-heavy collections
  - When quality > speed

## 📁 Directory Organization

### Recommended Structure

```
inspiration/
├── animals/
│   ├── dogs/
│   │   ├── golden_retriever_1.jpg
│   │   ├── golden_retriever_2.jpg
│   │   └── labrador_1.jpg
│   └── cats/
│       ├── persian_1.jpg
│       └── siamese_1.jpg
├── vehicles/
│   ├── sports_cars/
│   │   ├── ferrari_1.jpg
│   │   └── lamborghini_1.jpg
│   └── vintage/
│       ├── classic_1.jpg
│       └── retro_1.jpg
└── art_styles/
    ├── watercolor/
    │   ├── example_1.jpg
    │   └── example_2.jpg
    └── oil_painting/
        ├── example_1.jpg
        └── example_2.jpg
```

### Generated Output

```
wildcards/clip_generated/
├── animals_dogs_fast.txt
├── animals_dogs_simple.txt
├── animals_dogs_detailed.txt
├── animals_dogs_best.txt
├── animals_cats_fast.txt
├── animals_cats_simple.txt
├── animals_cats_detailed.txt
├── animals_cats_best.txt
├── vehicles_sports_cars_fast.txt
└── ...
```

**Note**: Subdirectory names become part of the theme name.

## 🔄 Complete Workflow Example

### Step 1: Collect Inspiration

```bash
mkdir -p inspiration/cyberpunk
cd inspiration/cyberpunk

# Download reference images from Pinterest, ArtStation, etc.
# Save as: cyber1.jpg, cyber2.jpg, cyber3.jpg, ...
```

### Step 2: Process Images

```bash
# Option A: Web Dashboard
# Navigate to http://localhost:8081/clip
# Enter path: /path/to/inspiration
# Select modes: detailed, best
# Process

# Option B: CLI
python -m core.clip_processor inspiration/ --modes detailed best
```

### Step 3: Review Generated Wildcards

```bash
cat wildcards/clip_generated/cyberpunk_detailed.txt
```

Example output:
```
neon lights
futuristic cityscape
cyberpunk aesthetic
urban environment
night scene
holographic displays
tech noir
dystopian city
rain-slicked streets
neon signs
```

### Step 4: Use in Prompts

```python
# In your prompt templates
prompt = "a character in __CYBERPUNK_DETAILED__ setting, detailed"

# Expands to:
# "a character in neon lights setting, detailed"
# "a character in futuristic cityscape setting, detailed"
# "a character in holographic displays setting, detailed"
# etc.
```

### Step 5: Iterate & Refine

```bash
# If tags are too generic, try best mode
python -m core.clip_processor inspiration/cyberpunk --theme cyberpunk --modes best

# If too many tags, use simple mode
python -m core.clip_processor inspiration/cyberpunk --theme cyberpunk --modes simple

# Manually edit generated files to add/remove tags
nano wildcards/clip_generated/cyberpunk_detailed.txt
```

## ⚙️ Advanced Features

### Custom Tag Extraction

The processor automatically:
- Removes weight syntax: `(tag:1.2)` → `tag`
- Removes parentheses: `(tag)` → `tag`
- Splits by commas and pipes: `tag1, tag2 | tag3`
- Deduplicates across all images
- Preserves original order where possible

### Progress Tracking

```python
# In Python API
from core.clip_processor import CLIPProcessor

processor = CLIPProcessor()

def progress_callback(current, total, status):
    print(f"[{current}/{total}] {status}")

results = processor.process_directory(
    "inspiration/",
    progress_callback=progress_callback
)
```

### Batch Processing

```python
# Process multiple directories
directories = [
    "/path/to/animals",
    "/path/to/vehicles",
    "/path/to/landscapes"
]

for directory in directories:
    results = processor.process_directory(directory)
    print(f"Processed {directory}: {results['total_images']} images")
```

### Custom Output Formats

```python
# Process and get results programmatically
results = processor.process_directory("inspiration/")

for theme in results['themes_processed']:
    print(f"Theme: {theme}")
    print(f"  Images: {results['total_images']}")
    print(f"  Tags: {results['total_tags']}")
    print(f"  Files: {results['files_created']}")
```

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "API connection failed"

**Solutions**:
1. Check Automatic1111 is running:
   ```bash
   curl http://127.0.0.1:7860/sdapi/v1/progress
   ```

2. Verify API URL in settings

3. Check firewall settings

4. Try restart Automatic1111

### Extension Not Found

**Problem**: "CLIP Interrogator extension not found"

**Solutions**:
1. Reinstall extension:
   ```bash
   cd stable-diffusion-webui/extensions
   rm -rf clip-interrogator-ext
   git clone https://github.com/pharmapsychotic/clip-interrogator-ext
   ```

2. Restart WebUI completely

3. Check Extensions tab in WebUI (should show "CLIP Interrogator")

4. Check Settings > CLIP Interrogator for configuration

### Slow Processing

**Problem**: Processing takes too long

**Solutions**:
1. **Use GPU**: Enable CUDA in Automatic1111 settings
2. **Reduce modes**: Use only `fast` or `simple`
3. **Resize images**: Large images slow down processing
4. **Batch smaller**: Process 10-20 images at a time
5. **Check hardware**: CLIP needs decent GPU/CPU

### Empty or Poor Results

**Problem**: Generated wildcards have few or poor tags

**Solutions**:
1. **Try different mode**: Switch from `fast` to `detailed` or `best`
2. **Check image quality**: Low-res images = poor results
3. **Verify image content**: Abstract/simple images yield fewer tags
4. **Test single image**: Rule out batch processing issues
5. **Review CLIP settings**: Check vocab selection in WebUI

### File Path Issues

**Problem**: "Directory not found"

**Solutions**:
1. Use absolute paths: `/full/path/to/images`
2. Check permissions: Ensure read access
3. Verify directory exists: `ls -la /path/to/images`
4. Check for spaces: Use quotes: `"/path/with spaces/"`

## 📊 Performance Benchmarks

Based on testing with RTX 3080:

| Mode | Speed | Images/Hour | Quality Score |
|------|-------|-------------|---------------|
| fast | 2-5s | 720-1800 | ⭐⭐ |
| simple | 5-10s | 360-720 | ⭐⭐⭐ |
| detailed | 15-30s | 120-240 | ⭐⭐⭐⭐ |
| best | 30-60s | 60-120 | ⭐⭐⭐⭐⭐ |

**CPU-only**: 3-5x slower

## 🎓 Best Practices

1. **Start with fast mode** to verify setup and image quality
2. **Use simple mode** for production wildcards (best speed/quality)
3. **Save best mode** for final, high-quality collections
4. **Organize by theme** using subdirectories
5. **Review and edit** generated wildcards manually
6. **Test wildcards** in prompts before large batches
7. **Keep backup** of original images
8. **Version control** your wildcard files
9. **Document decisions** in README per collection
10. **Iterate based on results** - refine over time

## 🔗 Integration Tips

### With Existing Wildcards

```python
# Combine CLIP-generated with manual wildcards
__CLIP_DOGS_DETAILED__, __ARTISTIC__, __CAMERA__
```

### With Prompt Builder

```python
# Use in templates
template = "a __CLIP_THEME__ in __STYLE__ style"
```

### With Batch Generation

```python
# Generate variations using CLIP wildcards
for i in range(10):
    prompt = prompt_builder.build_from_template(
        "a __CLIP_CYBERPUNK_BEST__ scene"
    )
    generate_image(prompt)
```

## 📚 API Reference

### CLIPProcessor

```python
from core.clip_processor import CLIPProcessor

# Initialize
processor = CLIPProcessor(
    api_url="http://127.0.0.1:7860",
    output_dir="wildcards/clip_generated",
    batch_size=10,
    dedupe=True,
    max_image_size_mb=5
)

# Test connection
if processor.test_connection():
    print("✅ Connected")

# Process directory
results = processor.process_directory(
    input_dir="/path/to/images",
    modes=['simple', 'detailed'],
    theme_name="custom_theme",
    recursive=True,
    progress_callback=lambda c, t, s: print(f"{c}/{t}: {s}")
)

# Get statistics
stats = processor.get_processing_stats()
```

### CLIPService (Web Dashboard)

```python
from web_dashboard.services.clip_service import CLIPService

service = CLIPService(app_context)

# Test connection
status = service.test_connection()

# Process directory
results = service.process_directory(
    input_dir="/path/to/images",
    modes=['fast', 'simple'],
    theme_name=None,
    recursive=True
)

# Get generated wildcards
wildcards = service.get_generated_wildcards()
```

## 🤝 Contributing

Ideas for enhancements:
- [ ] Support for WD14 tagger (anime-focused)
- [ ] Custom tag filtering/weighting
- [ ] Automatic clustering of similar tags
- [ ] Integration with image databases
- [ ] Batch API optimization
- [ ] GPU memory management
- [ ] Custom CLIP model selection

---

**Version**: 2.4  
**Last Updated**: 2025-01-30  
**Author**: Forge API Tool Team  
**License**: MIT
