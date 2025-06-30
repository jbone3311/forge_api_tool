import os
import json
import hashlib
import shutil
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import base64
from PIL import Image, PngImagePlugin
import io
from .centralized_logger import logger


class OutputManager:
    """Manages output directories and file operations for the Forge API Tool.
    
    Uses Automatic1111-style structure:
    - outputs/YYYY-MM-DD/ (date-based folders)
    - Metadata embedded directly in PNG files
    - Simple, clean organization
    """
    
    def __init__(self, base_output_dir: str = "outputs"):
        """Initialize the output manager with a base directory."""
        self.base_output_dir = base_output_dir
        
        # Create base output directory
        os.makedirs(base_output_dir, exist_ok=True)
        
        # Log initialization
        logger.log_app_event("output_manager_initialized", {
            "base_output_dir": base_output_dir,
            "structure": "date_based_with_embedded_metadata"
        })
    
    def get_output_directory(self, date: str = None) -> str:
        """Get the output directory for a specific date or today."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        output_dir = os.path.join(self.base_output_dir, date)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def save_image(self, image_data: str, config_name: str, prompt: str, seed: int, 
                   generation_settings: Dict[str, Any] = None, model_settings: Dict[str, Any] = None) -> str:
        """Save image data to file with embedded metadata like Automatic1111."""
        try:
            # Decode base64 image data
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Get output directory for today
            output_dir = self.get_output_directory()
            
            # Create filename with timestamp and seed
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Ensure seed is an integer for formatting
            seed_int = int(seed) if seed is not None else -1
            filename = f"{timestamp}_{seed_int:08d}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Prepare metadata in Automatic1111 format
            metadata = {
                # Core generation parameters (exactly like A1111)
                'prompt': prompt,
                'negative_prompt': generation_settings.get('negative_prompt', '') if generation_settings else '',
                'seed': int(seed) if seed is not None else -1,
                'subseed': generation_settings.get('subseed', -1) if generation_settings else -1,
                'subseed_strength': generation_settings.get('subseed_strength', 0.0) if generation_settings else 0.0,
                'width': generation_settings.get('width', 512) if generation_settings else 512,
                'height': generation_settings.get('height', 512) if generation_settings else 512,
                'sampler_name': generation_settings.get('sampler', 'Euler a') if generation_settings else 'Euler a',
                'cfg_scale': generation_settings.get('cfg_scale', 7.0) if generation_settings else 7.0,
                'steps': generation_settings.get('steps', 20) if generation_settings else 20,
                'batch_size': generation_settings.get('batch_size', 1) if generation_settings else 1,
                'restore_faces': generation_settings.get('restore_faces', False) if generation_settings else False,
                'face_restoration_model': generation_settings.get('face_restoration_model', 'CodeFormer') if generation_settings else 'CodeFormer',
                'sd_model_name': model_settings.get('checkpoint', '') if model_settings else '',
                'sd_model_hash': model_settings.get('model_hash', '') if model_settings else '',
                'sd_vae_name': model_settings.get('vae', '') if model_settings else '',
                'sd_vae_hash': model_settings.get('vae_hash', '') if model_settings else '',
                'clip_skip': generation_settings.get('clip_skip', 1) if generation_settings else 1,
                'is_using_inpainting_conditioning': generation_settings.get('is_using_inpainting_conditioning', False) if generation_settings else False,
                
                # Hires fix parameters
                'hires_fix': generation_settings.get('hires_fix', False) if generation_settings else False,
                'hires_upscaler': generation_settings.get('hires_upscaler', 'Latent') if generation_settings else 'Latent',
                'hires_steps': generation_settings.get('hires_steps', 20) if generation_settings else 20,
                'hires_denoising': generation_settings.get('hires_denoising', 0.5) if generation_settings else 0.5,
                'hires_resize_x': generation_settings.get('hires_resize_x', 0) if generation_settings else 0,
                'hires_resize_y': generation_settings.get('hires_resize_y', 0) if generation_settings else 0,
                
                # Denoising strength (for img2img)
                'denoising_strength': generation_settings.get('denoising_strength', 0.7) if generation_settings else 0.7,
                
                # Tiling
                'tiling': generation_settings.get('tiling', False) if generation_settings else False,
                
                # Additional generation settings
                'eta': generation_settings.get('eta', 0.0) if generation_settings else 0.0,
                's_churn': generation_settings.get('s_churn', 0.0) if generation_settings else 0.0,
                's_tmin': generation_settings.get('s_tmin', 0.0) if generation_settings else 0.0,
                's_tmax': generation_settings.get('s_tmax', 1.0) if generation_settings else 1.0,
                's_noise': generation_settings.get('s_noise', 1.0) if generation_settings else 1.0,
                
                # ControlNet settings (if present)
                'controlnet_0_model': generation_settings.get('controlnet_0_model', '') if generation_settings else '',
                'controlnet_0_preprocessor': generation_settings.get('controlnet_0_preprocessor', '') if generation_settings else '',
                'controlnet_0_guidance_start': generation_settings.get('controlnet_0_guidance_start', 0.0) if generation_settings else 0.0,
                'controlnet_0_guidance_end': generation_settings.get('controlnet_0_guidance_end', 1.0) if generation_settings else 1.0,
                'controlnet_0_control_mode': generation_settings.get('controlnet_0_control_mode', 'Balanced') if generation_settings else 'Balanced',
                'controlnet_0_pixel_perfect': generation_settings.get('controlnet_0_pixel_perfect', False) if generation_settings else False,
                
                # LoRA settings (if present)
                'lora_hashes': generation_settings.get('lora_hashes', '') if generation_settings else '',
                'lora_weights': generation_settings.get('lora_weights', '') if generation_settings else '',
                
                # Script settings (if present)
                'script_name': generation_settings.get('script_name', '') if generation_settings else '',
                'script_args': generation_settings.get('script_args', []) if generation_settings else [],
                
                # Forge API Tool specific metadata
                'config_name': config_name,
                'generation_time': datetime.now().isoformat(),
                'software': 'Forge API Tool',
                'version': '1.0.0',
                'api_type': 'forge'
            }
            
            # Add any additional generation settings not covered above
            if generation_settings:
                for key, value in generation_settings.items():
                    if key not in metadata:
                        metadata[f'gen_{key}'] = value
            
            # Add any additional model settings not covered above
            if model_settings:
                for key, value in model_settings.items():
                    if key not in metadata:
                        metadata[f'model_{key}'] = value
            
            # Embed metadata in PNG
            pnginfo = PngImagePlugin.PngInfo()
            
            # Add all metadata as text chunks (exactly like A1111)
            for key, value in metadata.items():
                if isinstance(value, (dict, list)):
                    # Convert complex objects to JSON strings
                    pnginfo.add_text(key, json.dumps(value, ensure_ascii=False))
                else:
                    # Convert simple values to strings
                    pnginfo.add_text(key, str(value))
            
            # Save image with embedded metadata
            image.save(filepath, 'PNG', pnginfo=pnginfo)
            
            # Log successful save
            logger.log_output_created(config_name, filepath, prompt, seed)
            
            return filepath
            
        except Exception as e:
            error_msg = f"Failed to save image: {str(e)}"
            logger.log_output_error(config_name, error_msg, prompt)
            raise Exception(error_msg)
    
    def get_outputs_for_date(self, date: str = None) -> List[Dict[str, Any]]:
        """Get all outputs for a specific date or today."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        outputs = []
        output_dir = self.get_output_directory(date)
        
        if not os.path.exists(output_dir):
            return outputs
        
        try:
            # Get all PNG files in the directory
            png_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
            
            for filename in png_files:
                filepath = os.path.join(output_dir, filename)
                metadata = self.extract_metadata_from_image(filepath)
                
                if metadata:
                    metadata['filename'] = filename
                    metadata['filepath'] = filepath
                    metadata['date'] = date
                    outputs.append(metadata)
            
            # Sort by timestamp (newest first)
            outputs.sort(key=lambda x: x.get('generation_time', ''), reverse=True)
            
        except Exception as e:
            logger.log_error(f"Failed to get outputs for date {date}: {e}")
        
        return outputs
    
    def get_outputs_for_config(self, config_name: str) -> List[Dict[str, Any]]:
        """Get all outputs for a specific configuration across all dates."""
        outputs = []
        
        try:
            # Get all date directories
            if not os.path.exists(self.base_output_dir):
                return outputs
            
            date_dirs = [d for d in os.listdir(self.base_output_dir) 
                        if os.path.isdir(os.path.join(self.base_output_dir, d)) and 
                        re.match(r'\d{4}-\d{2}-\d{2}', d)]
            
            # Sort dates (newest first)
            date_dirs.sort(reverse=True)
            
            for date_dir in date_dirs:
                date_outputs = self.get_outputs_for_date(date_dir)
                # Filter by config name
                config_outputs = [o for o in date_outputs if o.get('config_name') == config_name]
                outputs.extend(config_outputs)
            
        except Exception as e:
            logger.log_error(f"Failed to get outputs for config {config_name}: {e}")
        
        return outputs
    
    def extract_metadata_from_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from a PNG image file."""
        try:
            with Image.open(image_path) as image:
                metadata = {}
                
                # Extract text chunks from PNG
                for key, value in image.text.items():
                    try:
                        # Try to parse as JSON first
                        metadata[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, use as string
                        metadata[key] = value
                
                return metadata if metadata else None
                
        except Exception as e:
            logger.log_error(f"Failed to extract metadata from {image_path}: {e}")
            return None
    
    def get_output_statistics(self) -> Dict[str, Any]:
        """Get comprehensive output statistics."""
        try:
            total_outputs = 0
            configs_with_outputs = set()
            recent_outputs = []
            total_size_bytes = 0
            date_breakdown = {}
            
            # Get all date directories
            if os.path.exists(self.base_output_dir):
                date_dirs = [d for d in os.listdir(self.base_output_dir) 
                            if os.path.isdir(os.path.join(self.base_output_dir, d)) and 
                            re.match(r'\d{4}-\d{2}-\d{2}', d)]
                
                # Sort dates (newest first)
                date_dirs.sort(reverse=True)
                
                for date_dir in date_dirs:
                    date_outputs = self.get_outputs_for_date(date_dir)
                    total_outputs += len(date_outputs)
                    
                    # Add to date breakdown
                    date_breakdown[date_dir] = len(date_outputs)
                    
                    # Add configs
                    for output in date_outputs:
                        config_name = output.get('config_name')
                        if config_name:
                            configs_with_outputs.add(config_name)
                        
                        # Add to recent outputs (limit to 10)
                        if len(recent_outputs) < 10:
                            recent_outputs.append(output)
                        
                        # Calculate file size
                        filepath = output.get('filepath')
                        if filepath and os.path.exists(filepath):
                            total_size_bytes += os.path.getsize(filepath)
            
            return {
                'total_outputs': total_outputs,
                'config_count': len(configs_with_outputs),
                'total_size_bytes': total_size_bytes,
                'total_size_mb': round(total_size_bytes / (1024 * 1024), 2),
                'recent_outputs': recent_outputs,
                'configs_with_outputs': list(configs_with_outputs),
                'date_breakdown': date_breakdown
            }
            
        except Exception as e:
            logger.log_error(f"Failed to get output statistics: {e}")
            return {
                'total_outputs': 0,
                'config_count': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'recent_outputs': [],
                'configs_with_outputs': [],
                'date_breakdown': {}
            }
    
    def cleanup_old_outputs(self, days_to_keep: int = 30) -> int:
        """Clean up outputs older than specified days."""
        try:
            if not os.path.exists(self.base_output_dir):
                return 0
            
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
            
            date_dirs = [d for d in os.listdir(self.base_output_dir) 
                        if os.path.isdir(os.path.join(self.base_output_dir, d)) and 
                        re.match(r'\d{4}-\d{2}-\d{2}', d)]
            
            deleted_count = 0
            
            for date_dir in date_dirs:
                try:
                    dir_date = datetime.strptime(date_dir, "%Y-%m-%d")
                    if dir_date < cutoff_date:
                        dir_path = os.path.join(self.base_output_dir, date_dir)
                        shutil.rmtree(dir_path)
                        deleted_count += 1
                        logger.log_app_event("old_outputs_cleaned", {
                            "date_dir": date_dir,
                            "days_old": (datetime.now() - dir_date).days
                        })
                except Exception as e:
                    logger.log_error(f"Failed to clean up directory {date_dir}: {e}")
            
            return deleted_count
            
        except Exception as e:
            logger.log_error(f"Failed to cleanup old outputs: {e}")
            return 0
    
    def delete_output(self, filepath: str) -> bool:
        """Delete an output file."""
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                logger.warning(f"File not found for deletion: {filepath}")
                return False
            
            # Delete the file
            filepath.unlink()
            
            logger.log_app_event("output_deleted", {
                "filepath": str(filepath)
            })
            
            return True
            
        except Exception as e:
            logger.log_error(f"Failed to delete output {filepath}: {e}")
            return False
    
    def export_outputs(self, export_path: str, date: str = None, config_name: str = None) -> str:
        """Export outputs to a new directory."""
        try:
            export_dir = Path(export_path)
            export_dir.mkdir(parents=True, exist_ok=True)
            
            if date:
                # Export specific date
                outputs = self.get_outputs_for_date(date)
            elif config_name:
                # Export specific config
                outputs = self.get_outputs_for_config(config_name)
            else:
                # Export all outputs
                outputs = []
                if os.path.exists(self.base_output_dir):
                    date_dirs = [d for d in os.listdir(self.base_output_dir) 
                                if os.path.isdir(os.path.join(self.base_output_dir, d)) and 
                                re.match(r'\d{4}-\d{2}-\d{2}', d)]
                    for date_dir in date_dirs:
                        outputs.extend(self.get_outputs_for_date(date_dir))
            
            exported_count = 0
            
            for output in outputs:
                try:
                    source_path = Path(output.get('filepath', ''))
                    if source_path.exists():
                        # Copy image with metadata embedded
                        dest_path = export_dir / source_path.name
                        shutil.copy2(source_path, dest_path)
                        exported_count += 1
                        
                except Exception as e:
                    logger.log_error(f"Failed to export output {output.get('filepath', '')}: {e}")
                    continue
            
            logger.log_output_export(
                f"date_{date}" if date else f"config_{config_name}" if config_name else "all", 
                str(export_dir), 
                exported_count
            )
            
            return str(export_dir)
            
        except Exception as e:
            logger.log_error(f"Failed to export outputs: {e}")
            raise Exception(f"Export failed: {str(e)}")

# Create a default instance
output_manager = OutputManager() 