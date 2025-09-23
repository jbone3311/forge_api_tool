import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class EnhancedConfigHandler:
    """
    Enhanced configuration handler that supports image settings with thumbnails.
    """

    def __init__(self, settings_dir: str = "image_settings", images_dir: str = "image_settings/images"):
        self.settings_dir = Path(settings_dir)
        self.images_dir = Path(images_dir)
        
        # Ensure directories exist
        self.settings_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)

    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all image settings with thumbnail information."""
        settings = {}
        
        if not self.settings_dir.exists():
            return settings
        
        for settings_file in self.settings_dir.glob("*.json"):
            if settings_file.name == "README.md":
                continue
                
            settings_name = settings_file.stem
            
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Look for thumbnail
                thumbnail_path = self._find_thumbnail(settings_name)
                
                settings[settings_name] = {
                    'config': config_data,
                    'thumbnail': thumbnail_path,
                    'has_thumbnail': thumbnail_path is not None,
                    'settings_file': str(settings_file),
                    'description': config_data.get('description', ''),
                    'tags': config_data.get('tags', [])
                }
                
            except Exception as e:
                print(f"Error loading settings file {settings_file}: {e}")
                continue
        
        return settings

    def get_setting(self, settings_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific setting by name."""
        settings_file = self.settings_dir / f"{settings_name}.json"
        
        if not settings_file.exists():
            return None
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            thumbnail_path = self._find_thumbnail(settings_name)
            
            return {
                'config': config_data,
                'thumbnail': thumbnail_path,
                'has_thumbnail': thumbnail_path is not None,
                'settings_file': str(settings_file),
                'description': config_data.get('description', ''),
                'tags': config_data.get('tags', [])
            }
            
        except Exception as e:
            print(f"Error loading settings file {settings_file}: {e}")
            return None

    def _find_thumbnail(self, settings_name: str) -> Optional[str]:
        """Find thumbnail for a settings file."""
        if not self.images_dir.exists():
            return None
        
        # Look for thumbnail with various extensions
        extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        
        for ext in extensions:
            thumbnail_file = self.images_dir / f"{settings_name}{ext}"
            if thumbnail_file.exists():
                return str(thumbnail_file)
        
        return None

    def save_setting(self, settings_name: str, config_data: Dict[str, Any]) -> bool:
        """Save a settings configuration."""
        try:
            settings_file = self.settings_dir / f"{settings_name}.json"
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving settings file {settings_name}: {e}")
            return False

    def delete_setting(self, settings_name: str) -> bool:
        """Delete a settings configuration and its thumbnail."""
        try:
            # Delete settings file
            settings_file = self.settings_dir / f"{settings_name}.json"
            if settings_file.exists():
                settings_file.unlink()
            
            # Delete thumbnail if it exists
            thumbnail_path = self._find_thumbnail(settings_name)
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)
            
            return True
            
        except Exception as e:
            print(f"Error deleting settings {settings_name}: {e}")
            return False

    def get_thumbnail_info(self, settings_name: str) -> Optional[Dict[str, Any]]:
        """Get thumbnail information for a settings file."""
        thumbnail_path = self._find_thumbnail(settings_name)
        
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            return None
        
        try:
            stat = os.stat(thumbnail_path)
            return {
                'path': thumbnail_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'exists': True
            }
        except Exception as e:
            print(f"Error getting thumbnail info for {settings_name}: {e}")
            return None

    def list_available_settings(self) -> List[str]:
        """Get list of available settings names."""
        settings = []
        
        if not self.settings_dir.exists():
            return settings
        
        for settings_file in self.settings_dir.glob("*.json"):
            if settings_file.name != "README.md":
                settings.append(settings_file.stem)
        
        return sorted(settings)

    def get_settings_with_thumbnails(self) -> Dict[str, Dict[str, Any]]:
        """Get settings that have thumbnails."""
        all_settings = self.get_all_settings()
        
        return {
            name: info for name, info in all_settings.items() 
            if info['has_thumbnail']
        }

    def get_settings_without_thumbnails(self) -> Dict[str, Dict[str, Any]]:
        """Get settings that don't have thumbnails."""
        all_settings = self.get_all_settings()
        
        return {
            name: info for name, info in all_settings.items() 
            if not info['has_thumbnail']
        }

    def add_thumbnail(self, settings_name: str, image_path: str) -> bool:
        """Add a thumbnail for a settings file."""
        try:
            if not os.path.exists(image_path):
                print(f"Source image file not found: {image_path}")
                return False
            
            # Determine file extension
            source_ext = Path(image_path).suffix.lower()
            if source_ext not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                print(f"Unsupported image format: {source_ext}")
                return False
            
            # Copy to images directory
            target_file = self.images_dir / f"{settings_name}{source_ext}"
            
            import shutil
            shutil.copy2(image_path, target_file)
            
            return True
            
        except Exception as e:
            print(f"Error adding thumbnail for {settings_name}: {e}")
            return False

    def get_settings_summary(self) -> Dict[str, Any]:
        """Get a summary of all settings."""
        all_settings = self.get_all_settings()
        
        total_settings = len(all_settings)
        with_thumbnails = len([s for s in all_settings.values() if s['has_thumbnail']])
        without_thumbnails = total_settings - with_thumbnails
        
        return {
            'total_settings': total_settings,
            'with_thumbnails': with_thumbnails,
            'without_thumbnails': without_thumbnails,
            'thumbnail_percentage': (with_thumbnails / total_settings * 100) if total_settings > 0 else 0,
            'settings_names': list(all_settings.keys())
        }
