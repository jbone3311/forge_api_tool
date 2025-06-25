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
from .centralized_logger import centralized_logger


class OutputManager:
    """Manages output files, organization, and metadata."""
    
    def __init__(self, base_output_dir: str = "outputs"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories (removed logs_dir - now handled by centralized logger)
        self.images_dir = self.base_output_dir / "images"
        self.metadata_dir = self.base_output_dir / "metadata"
        self.prompts_dir = self.base_output_dir / "prompts"
        
        for directory in [self.images_dir, self.metadata_dir, self.prompts_dir]:
            directory.mkdir(exist_ok=True)
        
        # Log initialization
        centralized_logger.log_app_event("output_manager_initialized", {
            "base_output_dir": str(self.base_output_dir),
            "images_dir": str(self.images_dir),
            "metadata_dir": str(self.metadata_dir),
            "prompts_dir": str(self.prompts_dir)
        })
    
    def save_image(self, image_data: str, config_name: str, prompt: str, seed: int) -> str:
        """Save image data to file and return the file path."""
        try:
            # Decode base64 image data
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Create dated subdirectory structure: outputs/config_name/YYYY-MM-DD/
            current_date = datetime.now().strftime("%Y-%m-%d")
            config_output_dir = self.base_output_dir / config_name / current_date
            config_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for this config/date
            config_images_dir = config_output_dir / "images"
            config_metadata_dir = config_output_dir / "metadata"
            config_prompts_dir = config_output_dir / "prompts"
            
            for directory in [config_images_dir, config_metadata_dir, config_prompts_dir]:
                directory.mkdir(exist_ok=True)
            
            # Create filename with timestamp and seed
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{config_name}_{timestamp}_seed{seed}.png"
            filepath = config_images_dir / filename
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            # Save metadata
            metadata = {
                'config_name': config_name,
                'prompt': prompt,
                'seed': seed,
                'timestamp': datetime.now().isoformat(),
                'filename': filename,
                'filepath': str(filepath),
                'date': current_date
            }
            
            metadata_filename = f"{config_name}_{timestamp}_seed{seed}_metadata.json"
            metadata_filepath = config_metadata_dir / metadata_filename
            
            with open(metadata_filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Save prompt
            prompt_filename = f"{config_name}_{timestamp}_seed{seed}_prompt.txt"
            prompt_filepath = config_prompts_dir / prompt_filename
            
            with open(prompt_filepath, 'w', encoding='utf-8') as f:
                f.write(prompt)
            
            # Log successful save
            centralized_logger.log_output_created(config_name, str(filepath), prompt, seed)
            
            return str(filepath)
            
        except Exception as e:
            error_msg = f"Failed to save image: {str(e)}"
            centralized_logger.log_output_error(config_name, error_msg, prompt)
            raise Exception(error_msg)
    
    def get_outputs_for_config(self, config_name: str) -> List[Dict[str, Any]]:
        """Get all outputs for a specific configuration."""
        outputs = []
        
        try:
            # Look for outputs in the new dated subdirectory structure
            config_dir = self.base_output_dir / config_name
            if not config_dir.exists():
                return outputs
            
            # Search through all date subdirectories
            for date_dir in config_dir.iterdir():
                if date_dir.is_dir() and date_dir.name.match(r'\d{4}-\d{2}-\d{2}'):
                    metadata_dir = date_dir / "metadata"
                    if metadata_dir.exists():
                        # Find all metadata files for this config/date
                        metadata_files = list(metadata_dir.glob(f"{config_name}_*_metadata.json"))
                        
                        for metadata_file in metadata_files:
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                
                                # Check if image file exists
                                image_path = Path(metadata.get('filepath', ''))
                                if image_path.exists():
                                    outputs.append(metadata)
                                else:
                                    # Log missing image file
                                    centralized_logger.warning(f"Image file not found: {image_path}")
                                    
                            except Exception as e:
                                centralized_logger.log_error(f"Failed to read metadata file {metadata_file}: {e}")
                                continue
            
            # Sort by timestamp (newest first)
            outputs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            centralized_logger.log_app_event("outputs_retrieved", {
                "config_name": config_name,
                "output_count": len(outputs)
            })
            
            return outputs
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to get outputs for config {config_name}: {e}")
            return []
    
    def get_all_outputs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all outputs organized by configuration."""
        all_outputs = {}
        
        try:
            # Search through all config directories
            for config_dir in self.base_output_dir.iterdir():
                if config_dir.is_dir() and config_dir.name != "__pycache__":
                    config_name = config_dir.name
                    
                    # Get outputs for this config
                    config_outputs = self.get_outputs_for_config(config_name)
                    if config_outputs:
                        all_outputs[config_name] = config_outputs
            
            centralized_logger.log_app_event("all_outputs_retrieved", {
                "config_count": len(all_outputs),
                "total_outputs": sum(len(outputs) for outputs in all_outputs.values())
            })
            
            return all_outputs
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to get all outputs: {e}")
            return {}
    
    def delete_output(self, filepath: str) -> bool:
        """Delete an output and its associated files."""
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                centralized_logger.warning(f"File not found for deletion: {filepath}")
                return False
            
            # Find associated metadata and prompt files
            filename = filepath.name
            base_name = filename.replace('.png', '')
            
            metadata_file = self.metadata_dir / f"{base_name}_metadata.json"
            prompt_file = self.prompts_dir / f"{base_name}_prompt.txt"
            
            # Delete files
            filepath.unlink()
            
            if metadata_file.exists():
                metadata_file.unlink()
            
            if prompt_file.exists():
                prompt_file.unlink()
            
            centralized_logger.log_app_event("output_deleted", {
                "filepath": str(filepath),
                "metadata_deleted": metadata_file.exists(),
                "prompt_deleted": prompt_file.exists()
            })
            
            return True
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to delete output {filepath}: {e}")
            return False
    
    def delete_config_outputs(self, config_name: str) -> int:
        """Delete all outputs for a specific configuration."""
        try:
            outputs = self.get_outputs_for_config(config_name)
            deleted_count = 0
            
            for output in outputs:
                filepath = output.get('filepath', '')
                if filepath and self.delete_output(filepath):
                    deleted_count += 1
            
            centralized_logger.log_app_event("config_outputs_deleted", {
                "config_name": config_name,
                "deleted_count": deleted_count,
                "total_outputs": len(outputs)
            })
            
            return deleted_count
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to delete outputs for config {config_name}: {e}")
            return 0
    
    def export_config_outputs(self, config_name: str, export_path: str) -> str:
        """Export all outputs for a configuration to a new directory."""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            outputs = self.get_outputs_for_config(config_name)
            exported_count = 0
            
            for output in outputs:
                try:
                    source_path = Path(output.get('filepath', ''))
                    if source_path.exists():
                        # Copy image
                        dest_path = export_dir / source_path.name
                        shutil.copy2(source_path, dest_path)
                        
                        # Copy metadata
                        metadata_file = Path(output.get('filepath', '')).parent.parent / "metadata" / f"{source_path.stem}_metadata.json"
                        if metadata_file.exists():
                            shutil.copy2(metadata_file, export_dir / metadata_file.name)
                        
                        # Copy prompt
                        prompt_file = Path(output.get('filepath', '')).parent.parent / "prompts" / f"{source_path.stem}_prompt.txt"
                        if prompt_file.exists():
                            shutil.copy2(prompt_file, export_dir / prompt_file.name)
                        
                        exported_count += 1
                        
                except Exception as e:
                    centralized_logger.log_error(f"Failed to export output {output.get('filepath', '')}: {e}")
                    continue
            
            centralized_logger.log_output_export(config_name, str(export_dir), exported_count)
            
            return str(export_dir)
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to export outputs for config {config_name}: {e}")
            raise Exception(f"Export failed: {str(e)}")
    
    def get_output_statistics(self) -> Dict[str, Any]:
        """Get statistics about all outputs."""
        try:
            all_outputs = self.get_all_outputs()
            
            total_outputs = sum(len(outputs) for outputs in all_outputs.values())
            config_count = len(all_outputs)
            
            # Calculate total size
            total_size = 0
            for config_outputs in all_outputs.values():
                for output in config_outputs:
                    filepath = Path(output.get('filepath', ''))
                    if filepath.exists():
                        total_size += filepath.stat().st_size
            
            # Get recent outputs (last 10)
            all_outputs_flat = []
            for config_name, outputs in all_outputs.items():
                for output in outputs:
                    output['config_name'] = config_name
                    all_outputs_flat.append(output)
            
            all_outputs_flat.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            recent_outputs = all_outputs_flat[:10]
            
            stats = {
                'total_outputs': total_outputs,
                'config_count': config_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'recent_outputs': recent_outputs,
                'configs_with_outputs': list(all_outputs.keys())
            }
            
            centralized_logger.log_app_event("output_statistics_retrieved", stats)
            
            return stats
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to get output statistics: {e}")
            return {
                'total_outputs': 0,
                'config_count': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'recent_outputs': [],
                'configs_with_outputs': [],
                'error': str(e)
            }
    
    def cleanup_old_outputs(self, days_to_keep: int = 30) -> int:
        """Clean up outputs older than specified days."""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            all_outputs = self.get_all_outputs()
            
            for config_name, outputs in all_outputs.items():
                for output in outputs:
                    try:
                        filepath = Path(output.get('filepath', ''))
                        if filepath.exists() and filepath.stat().st_mtime < cutoff_date:
                            if self.delete_output(str(filepath)):
                                deleted_count += 1
                    except Exception as e:
                        centralized_logger.log_error(f"Failed to check/delete old output {output.get('filepath', '')}: {e}")
                        continue
            
            centralized_logger.log_app_event("old_outputs_cleaned", {
                "days_to_keep": days_to_keep,
                "deleted_count": deleted_count
            })
            
            return deleted_count
            
        except Exception as e:
            centralized_logger.log_error(f"Failed to cleanup old outputs: {e}")
            return 0


# Global output manager instance
output_manager = OutputManager() 