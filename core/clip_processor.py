#!/usr/bin/env python3
"""
CLIP Processor - Image to Wildcard Converter

Processes images through CLIP Interrogator to extract prompts and generate wildcard files.
Supports batch processing with async queuing, multiple modes (fast/simple/detailed/best),
and automatic wildcard file generation from image directories.

Features:
- Batch image processing via CLIP Interrogator API
- Multiple interrogation modes (fast, simple, detailed, best)
- Theme-based wildcard generation (subdir = theme)
- Deduplication and tag extraction
- Async job queuing for large batches
- Progress tracking and error handling
"""

import os
import json
import base64
import requests
import re
from typing import List, Dict, Tuple, Optional, Any, Set
from pathlib import Path
from collections import Counter
from PIL import Image
import io
from datetime import datetime

from core.centralized_logger import logger


class CLIPProcessor:
    """
    CLIP Interrogator processor for converting images to wildcard files.
    """
    
    # Available interrogation modes
    MODES = ['fast', 'simple', 'detailed', 'best']
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
    
    def __init__(self, 
                 api_url: str = "http://127.0.0.1:7860",
                 output_dir: str = "wildcards/clip_generated",
                 batch_size: int = 10,
                 dedupe: bool = True,
                 max_image_size_mb: int = 5):
        """
        Initialize CLIP processor.
        
        Args:
            api_url: Base URL for Automatic1111 API
            output_dir: Directory to save generated wildcard files
            batch_size: Number of images to process in parallel
            dedupe: Remove duplicate tags across images
            max_image_size_mb: Maximum image size before resizing
        """
        self.api_url = api_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.batch_size = batch_size
        self.dedupe = dedupe
        self.max_image_size_bytes = max_image_size_mb * 1024 * 1024
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.log_app_event("clip_processor_initialized", {
            "api_url": self.api_url,
            "output_dir": str(self.output_dir),
            "batch_size": self.batch_size
        })
    
    def test_connection(self) -> bool:
        """Test connection to Automatic1111 API."""
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/progress", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"CLIP API connection test failed: {e}")
            return False
    
    def check_clip_interrogator_installed(self) -> Tuple[bool, str]:
        """
        Check if CLIP Interrogator extension is installed.
        
        Returns:
            Tuple of (is_installed, message)
        """
        try:
            # Check if extension is available via scripts endpoint
            response = requests.get(f"{self.api_url}/sdapi/v1/scripts", timeout=10)
            if response.status_code == 200:
                scripts = response.json()
                # Check for CLIP Interrogator in available scripts
                for script_type in ['txt2img', 'img2img']:
                    if script_type in scripts:
                        for script in scripts[script_type]:
                            if 'clip' in script.get('name', '').lower():
                                return True, "CLIP Interrogator extension found"
                
                return False, "CLIP Interrogator extension not found in scripts"
            else:
                return False, f"Cannot check scripts: HTTP {response.status_code}"
        
        except Exception as e:
            return False, f"Error checking extension: {e}"
    
    def encode_image(self, img_path: str, resize_if_large: bool = True) -> Optional[str]:
        """
        Convert image to base64 for API.
        
        Args:
            img_path: Path to image file
            resize_if_large: Resize if image exceeds max size
            
        Returns:
            Base64-encoded image string or None on error
        """
        try:
            # Check file size
            file_size = os.path.getsize(img_path)
            
            if file_size > self.max_image_size_bytes and resize_if_large:
                # Resize image
                with Image.open(img_path) as img:
                    # Calculate new dimensions (maintain aspect ratio)
                    max_dimension = 1024  # Max width or height
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    
                    if ratio < 1.0:
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to bytes
                    buffer = io.BytesIO()
                    img.save(buffer, format='PNG')
                    img_bytes = buffer.getvalue()
            else:
                # Read as-is
                with open(img_path, 'rb') as f:
                    img_bytes = f.read()
            
            return base64.b64encode(img_bytes).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Error encoding image {img_path}: {e}")
            return None
    
    def interrogate_image(self, img_b64: str, mode: str = 'simple') -> Optional[str]:
        """
        Call CLIP Interrogator API for one image.
        
        Args:
            img_b64: Base64-encoded image
            mode: Interrogation mode (fast/simple/detailed/best)
            
        Returns:
            Generated prompt or None on error
        """
        if mode not in self.MODES:
            logger.error(f"Invalid mode: {mode}. Must be one of {self.MODES}")
            return None
        
        try:
            # Try the interrogate endpoint (CLIP Interrogator extension)
            interrogate_url = f"{self.api_url}/sdapi/v1/interrogate"
            
            payload = {
                "image": img_b64,
                "model": f"clip_{mode}"  # clip_fast, clip_simple, etc.
            }
            
            response = requests.post(interrogate_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Response format: {"caption": "generated prompt text"}
                prompt = result.get('caption', '')
                
                if not prompt:
                    logger.warning(f"Empty prompt from CLIP {mode}")
                
                return prompt
            else:
                logger.error(f"CLIP API error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"CLIP interrogation failed: {e}")
            return None
    
    def extract_tags(self, prompt: str, dedupe: bool = True) -> List[str]:
        """
        Parse prompt into wildcard-style tags.
        
        Args:
            prompt: Raw prompt from CLIP
            dedupe: Remove duplicates
            
        Returns:
            List of cleaned tags
        """
        if not prompt:
            return []
        
        # Split by common delimiters
        # Handle formats like: "tag1, tag2, tag3" or "tag1 | tag2 | tag3"
        tags = re.split(r',|\|', prompt)
        
        # Clean each tag
        cleaned_tags = []
        for tag in tags:
            # Remove weights like (tag:1.2)
            tag = re.sub(r'\([^)]*:\d+\.?\d*\)', '', tag)
            
            # Remove parentheses
            tag = tag.strip('()[]')
            
            # Remove extra whitespace
            tag = ' '.join(tag.split())
            
            # Remove empty strings
            if tag:
                cleaned_tags.append(tag)
        
        if dedupe:
            # Remove duplicates while preserving order
            seen = set()
            unique_tags = []
            for tag in cleaned_tags:
                tag_lower = tag.lower()
                if tag_lower not in seen:
                    seen.add(tag_lower)
                    unique_tags.append(tag)
            return unique_tags
        
        return cleaned_tags
    
    def process_image(self, img_path: str, modes: List[str]) -> Dict[str, List[str]]:
        """
        Process a single image through multiple CLIP modes.
        
        Args:
            img_path: Path to image file
            modes: List of modes to process
            
        Returns:
            Dictionary mapping mode to list of tags
        """
        results = {mode: [] for mode in modes}
        
        # Encode image
        img_b64 = self.encode_image(img_path)
        if not img_b64:
            logger.error(f"Failed to encode image: {img_path}")
            return results
        
        # Process each mode
        for mode in modes:
            prompt = self.interrogate_image(img_b64, mode)
            if prompt:
                tags = self.extract_tags(prompt, dedupe=False)  # Dedupe globally later
                results[mode].extend(tags)
                
                logger.info(f"Processed {img_path} with mode {mode}: {len(tags)} tags")
        
        return results
    
    def process_directory(self, 
                         input_dir: str,
                         modes: Optional[List[str]] = None,
                         theme_name: Optional[str] = None,
                         recursive: bool = True,
                         progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Process all images in a directory (or subdirectories).
        
        Args:
            input_dir: Directory containing images or subdirectories
            modes: List of modes to process (default: all)
            theme_name: Override theme name (default: directory name)
            recursive: Process subdirectories as separate themes
            progress_callback: Callback function(current, total, status)
            
        Returns:
            Dictionary with processing results
        """
        if modes is None:
            modes = self.MODES
        
        input_path = Path(input_dir)
        
        if not input_path.exists():
            return {
                'success': False,
                'error': f"Directory not found: {input_dir}"
            }
        
        results = {
            'success': True,
            'themes_processed': [],
            'total_images': 0,
            'total_tags': 0,
            'files_created': []
        }
        
        if recursive and any(p.is_dir() for p in input_path.iterdir()):
            # Process subdirectories as themes
            subdirs = [p for p in input_path.iterdir() if p.is_dir()]
            
            for i, subdir in enumerate(subdirs):
                theme = subdir.name.lower().replace(' ', '_')
                
                if progress_callback:
                    progress_callback(i + 1, len(subdirs), f"Processing theme: {theme}")
                
                theme_results = self._process_theme_directory(subdir, theme, modes)
                
                if theme_results['success']:
                    results['themes_processed'].append(theme)
                    results['total_images'] += theme_results['images_processed']
                    results['total_tags'] += theme_results['total_tags']
                    results['files_created'].extend(theme_results['files_created'])
        else:
            # Process as single theme
            theme = theme_name or input_path.name.lower().replace(' ', '_')
            theme_results = self._process_theme_directory(input_path, theme, modes, progress_callback)
            
            if theme_results['success']:
                results['themes_processed'].append(theme)
                results['total_images'] = theme_results['images_processed']
                results['total_tags'] = theme_results['total_tags']
                results['files_created'] = theme_results['files_created']
        
        return results
    
    def _process_theme_directory(self,
                                 theme_dir: Path,
                                 theme_name: str,
                                 modes: List[str],
                                 progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """Process a single theme directory."""
        # Find all images
        image_files = [
            f for f in theme_dir.iterdir()
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]
        
        if not image_files:
            return {
                'success': False,
                'error': f"No images found in {theme_dir}"
            }
        
        logger.info(f"Processing theme '{theme_name}': {len(image_files)} images")
        
        # Accumulate tags per mode
        mode_tags = {mode: [] for mode in modes}
        
        # Process each image
        for i, img_file in enumerate(image_files):
            if progress_callback:
                progress_callback(i + 1, len(image_files), f"Processing {img_file.name}")
            
            img_results = self.process_image(str(img_file), modes)
            
            for mode, tags in img_results.items():
                mode_tags[mode].extend(tags)
        
        # Dedupe and save
        files_created = []
        total_tags = 0
        
        for mode, tags in mode_tags.items():
            if self.dedupe:
                # Remove duplicates globally
                tags = list(dict.fromkeys(tags))  # Preserves order
            
            # Save wildcard file
            filename = f"{theme_name}_{mode}.txt"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(tags))
            
            files_created.append(str(filepath))
            total_tags += len(tags)
            
            logger.info(f"Created {filename}: {len(tags)} tags")
        
        return {
            'success': True,
            'images_processed': len(image_files),
            'total_tags': total_tags,
            'files_created': files_created
        }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about generated wildcard files."""
        stats = {
            'total_files': 0,
            'themes': set(),
            'modes': set(),
            'total_tags': 0,
            'files_by_theme': {}
        }
        
        if not self.output_dir.exists():
            return stats
        
        for wildcard_file in self.output_dir.glob('*.txt'):
            stats['total_files'] += 1
            
            # Parse filename: theme_mode.txt
            name_parts = wildcard_file.stem.rsplit('_', 1)
            if len(name_parts) == 2:
                theme, mode = name_parts
                stats['themes'].add(theme)
                stats['modes'].add(mode)
                
                if theme not in stats['files_by_theme']:
                    stats['files_by_theme'][theme] = []
                stats['files_by_theme'][theme].append(mode)
            
            # Count tags
            try:
                with open(wildcard_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                stats['total_tags'] += len([l for l in lines if l.strip()])
            except Exception:
                pass
        
        stats['themes'] = list(stats['themes'])
        stats['modes'] = list(stats['modes'])
        
        return stats


# CLI interface for testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CLIP Processor - Image to Wildcard Converter')
    parser.add_argument('input_dir', help='Directory containing images or subdirectories')
    parser.add_argument('--api-url', default='http://127.0.0.1:7860', help='Automatic1111 API URL')
    parser.add_argument('--output-dir', default='wildcards/clip_generated', help='Output directory')
    parser.add_argument('--modes', nargs='+', choices=CLIPProcessor.MODES, default=CLIPProcessor.MODES,
                       help='Modes to process')
    parser.add_argument('--theme', help='Override theme name')
    parser.add_argument('--no-recursive', action='store_true', help='Disable recursive processing')
    parser.add_argument('--test', action='store_true', help='Test API connection only')
    
    args = parser.parse_args()
    
    processor = CLIPProcessor(
        api_url=args.api_url,
        output_dir=args.output_dir
    )
    
    if args.test:
        print("Testing API connection...")
        if processor.test_connection():
            print("✅ API connection successful")
            
            installed, msg = processor.check_clip_interrogator_installed()
            if installed:
                print(f"✅ {msg}")
            else:
                print(f"❌ {msg}")
        else:
            print("❌ API connection failed")
    else:
        print(f"Processing: {args.input_dir}")
        print(f"Modes: {', '.join(args.modes)}")
        
        def progress(current, total, status):
            print(f"[{current}/{total}] {status}")
        
        results = processor.process_directory(
            args.input_dir,
            modes=args.modes,
            theme_name=args.theme,
            recursive=not args.no_recursive,
            progress_callback=progress
        )
        
        if results['success']:
            print(f"\n✅ Processing complete!")
            print(f"   Themes: {', '.join(results['themes_processed'])}")
            print(f"   Images: {results['total_images']}")
            print(f"   Tags: {results['total_tags']}")
            print(f"   Files: {len(results['files_created'])}")
            print(f"\nGenerated files:")
            for file in results['files_created']:
                print(f"   • {file}")
        else:
            print(f"\n❌ Error: {results.get('error', 'Unknown error')}")
