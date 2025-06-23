import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import base64
from PIL import Image
import io


class OutputManager:
    """Manages output files, organization, and metadata."""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.images_dir = self.base_output_dir / "images"
        self.metadata_dir = self.base_output_dir / "metadata"
        self.prompts_dir = self.base_output_dir / "prompts"
        self.logs_dir = self.base_output_dir / "logs"
        
        for directory in [self.images_dir, self.metadata_dir, self.prompts_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
    
    def save_image(self, image_data: str, config_name: str, prompt: str, seed: int, 
                   metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
        """Save image and metadata, return paths."""
        try:
            # Decode image data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_hash = self._hash_prompt(prompt)
            filename = f"{config_name}_{prompt_hash}_{seed}_{timestamp}.png"
            
            # Create config-specific directory
            config_dir = self.images_dir / config_name
            config_dir.mkdir(exist_ok=True)
            
            # Save image
            image_path = config_dir / filename
            image.save(image_path, "PNG")
            
            # Save metadata
            metadata_path = self._save_metadata(config_name, filename, prompt, seed, metadata)
            
            return str(image_path), str(metadata_path)
            
        except Exception as e:
            raise Exception(f"Failed to save image: {e}")
    
    def _hash_prompt(self, prompt: str) -> str:
        """Generate a hash for the prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()[:8]
    
    def _save_metadata(self, config_name: str, filename: str, prompt: str, seed: int,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save metadata for an image."""
        metadata_data = {
            'config_name': config_name,
            'filename': filename,
            'prompt': prompt,
            'seed': seed,
            'generated_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Create config-specific metadata directory
        config_metadata_dir = self.metadata_dir / config_name
        config_metadata_dir.mkdir(exist_ok=True)
        
        # Save metadata file
        metadata_filename = filename.replace('.png', '.json')
        metadata_path = config_metadata_dir / metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_data, f, indent=2)
        
        return str(metadata_path)
    
    def save_prompt_list(self, config_name: str, prompts: List[Dict[str, Any]]) -> str:
        """Save a list of prompts for a configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config_name}_prompts_{timestamp}.json"
        
        prompt_data = {
            'config_name': config_name,
            'generated_at': datetime.now().isoformat(),
            'total_prompts': len(prompts),
            'prompts': prompts
        }
        
        prompt_path = self.prompts_dir / filename
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            json.dump(prompt_data, f, indent=2)
        
        return str(prompt_path)
    
    def get_output_summary(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of output files."""
        summary = {
            'total_images': 0,
            'total_configs': 0,
            'configs': {},
            'recent_files': []
        }
        
        # Count images by config
        for config_dir in self.images_dir.iterdir():
            if config_dir.is_dir():
                config_name_dir = config_dir.name
                if config_name and config_name != config_name_dir:
                    continue
                
                image_count = len(list(config_dir.glob("*.png")))
                summary['configs'][config_name_dir] = {
                    'images': image_count,
                    'last_modified': self._get_last_modified(config_dir)
                }
                summary['total_images'] += image_count
                summary['total_configs'] += 1
        
        # Get recent files
        summary['recent_files'] = self._get_recent_files(10)
        
        return summary
    
    def _get_last_modified(self, directory: Path) -> Optional[str]:
        """Get the last modified time of a directory."""
        try:
            files = list(directory.glob("*"))
            if files:
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                return datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
        except Exception:
            pass
        return None
    
    def _get_recent_files(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent files."""
        all_files = []
        
        # Collect all image files
        for config_dir in self.images_dir.iterdir():
            if config_dir.is_dir():
                for image_file in config_dir.glob("*.png"):
                    all_files.append({
                        'path': str(image_file),
                        'config': config_dir.name,
                        'modified': image_file.stat().st_mtime
                    })
        
        # Sort by modification time and return recent ones
        all_files.sort(key=lambda x: x['modified'], reverse=True)
        
        recent_files = []
        for file_info in all_files[:count]:
            recent_files.append({
                'path': file_info['path'],
                'config': file_info['config'],
                'modified': datetime.fromtimestamp(file_info['modified']).isoformat()
            })
        
        return recent_files
    
    def cleanup_old_files(self, days_to_keep: int = 30, config_name: Optional[str] = None):
        """Clean up old output files."""
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        cleaned_files = []
        
        # Clean up images
        for config_dir in self.images_dir.iterdir():
            if config_dir.is_dir():
                if config_name and config_name != config_dir.name:
                    continue
                
                for image_file in config_dir.glob("*.png"):
                    if image_file.stat().st_mtime < cutoff_time:
                        try:
                            image_file.unlink()
                            cleaned_files.append(str(image_file))
                        except Exception as e:
                            print(f"Failed to delete {image_file}: {e}")
        
        # Clean up corresponding metadata files
        for config_dir in self.metadata_dir.iterdir():
            if config_dir.is_dir():
                if config_name and config_name != config_dir.name:
                    continue
                
                for metadata_file in config_dir.glob("*.json"):
                    if metadata_file.stat().st_mtime < cutoff_time:
                        try:
                            metadata_file.unlink()
                        except Exception as e:
                            print(f"Failed to delete {metadata_file}: {e}")
        
        return cleaned_files
    
    def export_config_outputs(self, config_name: str, output_path: str) -> str:
        """Export all outputs for a specific configuration."""
        try:
            # Create export directory
            export_dir = Path(output_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy images
            config_images_dir = self.images_dir / config_name
            if config_images_dir.exists():
                shutil.copytree(config_images_dir, export_dir / "images", dirs_exist_ok=True)
            
            # Copy metadata
            config_metadata_dir = self.metadata_dir / config_name
            if config_metadata_dir.exists():
                shutil.copytree(config_metadata_dir, export_dir / "metadata", dirs_exist_ok=True)
            
            # Create export summary
            summary = {
                'config_name': config_name,
                'exported_at': datetime.now().isoformat(),
                'images_count': len(list(config_images_dir.glob("*.png"))) if config_images_dir.exists() else 0,
                'metadata_count': len(list(config_metadata_dir.glob("*.json"))) if config_metadata_dir.exists() else 0
            }
            
            summary_path = export_dir / "export_summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            return str(export_dir)
            
        except Exception as e:
            raise Exception(f"Failed to export outputs: {e}")
    
    def get_image_metadata(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific image."""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return None
            
            # Find corresponding metadata file
            config_name = image_path.parent.name
            metadata_filename = image_path.stem + ".json"
            metadata_path = self.metadata_dir / config_name / metadata_filename
            
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error getting image metadata: {e}")
            return None
    
    def search_images(self, query: str, config_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for images by prompt content."""
        results = []
        
        search_configs = [config_name] if config_name else [d.name for d in self.images_dir.iterdir() if d.is_dir()]
        
        for config in search_configs:
            config_images_dir = self.images_dir / config
            if not config_images_dir.exists():
                continue
            
            for image_file in config_images_dir.glob("*.png"):
                metadata = self.get_image_metadata(str(image_file))
                if metadata and query.lower() in metadata.get('prompt', '').lower():
                    results.append({
                        'path': str(image_file),
                        'config': config,
                        'prompt': metadata.get('prompt', ''),
                        'seed': metadata.get('seed', 0),
                        'generated_at': metadata.get('generated_at', '')
                    })
        
        return results 