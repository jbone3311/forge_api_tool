#!/usr/bin/env python3
"""
Add sample thumbnails to image settings for demonstration.
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_sample_thumbnail(width=300, height=300, text="Sample", bg_color=(100, 150, 200), text_color=(255, 255, 255)):
    """Create a sample thumbnail image."""
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)
    
    return img

def add_sample_thumbnails():
    """Add sample thumbnails for existing settings files."""
    image_settings_dir = Path("image_settings")
    images_dir = image_settings_dir / "images"
    
    if not image_settings_dir.exists():
        print("❌ image_settings directory not found!")
        return
    
    # Ensure images directory exists
    images_dir.mkdir(exist_ok=True)
    
    # Colors for different setting types
    color_map = {
        "concept_art": (255, 100, 150),
        "cyberpunk": (100, 255, 150),
        "landscape_photography": (150, 200, 255),
        "portrait_art": (255, 200, 100),
        "Quick Start": (200, 100, 255),
        "SD_Default": (100, 255, 200),
        "SDXL_Default": (255, 150, 100),
        "template": (150, 150, 150)
    }
    
    # Find all settings files
    settings_files = list(image_settings_dir.glob("*.json"))
    
    print(f"🎨 Creating sample thumbnails for {len(settings_files)} settings...")
    
    for settings_file in settings_files:
        settings_name = settings_file.stem
        thumbnail_path = images_dir / f"{settings_name}.png"
        
        # Skip if thumbnail already exists
        if thumbnail_path.exists():
            print(f"⏭️  Thumbnail already exists for {settings_name}")
            continue
        
        # Get color for this setting type
        bg_color = color_map.get(settings_name, (100, 150, 200))
        
        # Create thumbnail
        thumbnail = create_sample_thumbnail(
            text=settings_name.replace("_", " ").title(),
            bg_color=bg_color
        )
        
        # Save thumbnail
        thumbnail.save(thumbnail_path)
        print(f"✅ Created thumbnail for {settings_name}")
        
        # Also update the settings file to add description and tags if missing
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            # Add description if missing
            if 'description' not in settings_data:
                descriptions = {
                    "concept_art": "Artistic concept illustrations with creative styling",
                    "cyberpunk": "Futuristic cyberpunk aesthetic with neon colors",
                    "landscape_photography": "Natural landscape photography settings",
                    "portrait_art": "Artistic portrait settings with enhanced details",
                    "Quick Start": "Quick start configuration for beginners",
                    "SD_Default": "Default Stable Diffusion 1.5 settings",
                    "SDXL_Default": "Default Stable Diffusion XL settings",
                    "template": "Template configuration for custom settings"
                }
                settings_data['description'] = descriptions.get(settings_name, f"{settings_name} configuration")
            
            # Add tags if missing
            if 'tags' not in settings_data:
                tag_map = {
                    "concept_art": ["art", "concept", "creative"],
                    "cyberpunk": ["futuristic", "neon", "cyberpunk"],
                    "landscape_photography": ["nature", "landscape", "photography"],
                    "portrait_art": ["portrait", "people", "artistic"],
                    "Quick Start": ["beginner", "simple", "quick"],
                    "SD_Default": ["stable-diffusion", "default", "1.5"],
                    "SDXL_Default": ["stable-diffusion", "xl", "high-res"],
                    "template": ["template", "custom", "example"]
                }
                settings_data['tags'] = tag_map.get(settings_name, [settings_name])
            
            # Save updated settings
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
            
            print(f"📝 Updated settings file for {settings_name}")
            
        except Exception as e:
            print(f"⚠️  Could not update settings file for {settings_name}: {e}")
    
    print(f"\n🎉 Sample thumbnails created successfully!")
    print(f"📁 Thumbnails saved in: {images_dir}")
    print(f"🌐 You can now see them in the web interface!")

if __name__ == "__main__":
    add_sample_thumbnails()
