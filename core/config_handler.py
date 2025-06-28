import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import re
from core.centralized_logger import logger


class ConfigHandler:
    """Handles loading, validation, and management of JSON configuration files."""
    
    def __init__(self, config_dir: str = "configs"):
        # Use absolute path to ensure it works from web dashboard
        if not os.path.isabs(config_dir):
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(current_dir)
            # Set config directory relative to project root
            self.config_dir = os.path.join(project_root, config_dir)
        else:
            self.config_dir = config_dir
            
        self.template_path = os.path.join(self.config_dir, "template.json")
        os.makedirs(self.config_dir, exist_ok=True)
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load a configuration file by name."""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Set default values
            config = self._set_defaults(config)
            # Validate configuration (structure only)
            self._validate_config(config, config_name)
            # Check for missing wildcards (but don't fail if there are issues)
            try:
                wildcards_info = self.validate_wildcards(config)
                config['missing_wildcards'] = wildcards_info['missing']
                config['missing_wildcard_files'] = wildcards_info['missing_files']
            except Exception as e:
                # If wildcard validation fails, just set empty lists and continue
                config['missing_wildcards'] = []
                config['missing_wildcard_files'] = []
                try:
                    logger.warning(f"Wildcard validation failed for {config_name}: {e}")
                except:
                    pass
            return config
        except Exception as e:
            raise ValueError(f"Error loading config '{config_name}': {e}")
    
    def save_config(self, config_name: str, config: Dict[str, Any]):
        """Save a configuration to file."""
        try:
            # Ensure config directory exists
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Set defaults and validate
            config = self._set_defaults(config)
            self._validate_config(config)
            
            # Save to file
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            raise ValueError(f"Error saving config {config_name}: {e}")
    
    def list_configs(self) -> List[str]:
        """List all available configuration names."""
        configs = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                configs.append(filename[:-5])  # Remove .json extension
        return sorted(configs)
    
    def config_exists(self, config_name: str) -> bool:
        """Check if a configuration exists."""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        return os.path.exists(config_path)
    
    def create_config_from_template(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new configuration from template."""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError("Template file not found")
        
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            # Update template with new name and description
            template['name'] = name
            template['description'] = description
            
            return template
        except Exception as e:
            raise ValueError(f"Error loading template: {e}")
    
    def _set_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for missing configuration options."""
        model_type = config.get('model_type', 'sd')
        
        # Only apply defaults if sections are missing
        if 'model_settings' not in config:
            if model_type == 'sd':
                config['model_settings'] = {
                    'checkpoint': 'sd-v1-5.safetensors',
                    'vae': 'vae-ft-mse-840000-ema-pruned.safetensors',
                    'text_encoder': 'openai/clip-vit-large-patch14'
                }
            elif model_type == 'sdxl':
                config['model_settings'] = {
                    'checkpoint': 'sd_xl_base_1.0.safetensors',
                    'vae': 'sdxl_vae.safetensors',
                    'text_encoder': 'openai/clip-vit-large-patch14',
                    'text_encoder_2': 'laion/CLIP-ViT-bigG-14-laion2B-39B-b160k'
                }
            elif model_type == 'xl':
                config['model_settings'] = {
                    'checkpoint': 'sd_xl_base_1.0.safetensors',
                    'vae': 'sdxl_vae.safetensors',
                    'text_encoder': 'openai/clip-vit-large-patch14',
                    'text_encoder_2': 'laion/CLIP-ViT-bigG-14-laion2B-39B-b160k'
                }
            elif model_type == 'flux':
                config['model_settings'] = {
                    'checkpoint': 'flux1-dev-bnb-nf4-v2.safetensors',
                    'vae': '',
                    'text_encoder': 't5xxl_fp16.safetensors'
                }
        
        if 'generation_settings' not in config:
            if model_type in ['sd', 'sdxl', 'xl']:
                config['generation_settings'] = {
                    'steps': 20,
                    'sampler': 'Euler a',
                    'width': 512,
                    'height': 512,
                    'batch_size': 1,
                    'batch_count': 1,
                    'cfg_scale': 7.0,
                    'seed': -1,
                    'subseed': -1,
                    'subseed_strength': 0.0,
                    'seed_resize_from_h': -1,
                    'seed_resize_from_w': -1,
                    'denoising_strength': 0.75,
                    'restore_faces': False,
                    'tiling': False,
                    'enable_hr': False,
                    'hr_scale': 2.0,
                    'hr_upscaler': 'Latent',
                    'hr_second_pass_steps': 20,
                    'hr_resize_x': 0,
                    'hr_resize_y': 0,
                    'hr_sampler_name': 'Euler a',
                    'hr_prompt': '',
                    'hr_negative_prompt': '',
                    'hr_denoising_strength': 0.7
                }
            elif model_type == 'flux':
                config['generation_settings'] = {
                    'steps': 20,
                    'sampler': 'Euler',
                    'width': 1024,
                    'height': 1024,
                    'batch_size': 1,
                    'batch_count': 1,
                    'cfg_scale': None,
                    'distilled_cfg_scale': 3.5,
                    'seed': -1
                }
        
        if 'prompt_settings' not in config:
            config['prompt_settings'] = {
                'base_prompt': 'a beautiful __SUBJECT__ in __STYLE__, __LIGHTING__, __COMPOSITION__, __MEDIUM__, high quality, detailed',
                'negative_prompt': 'low quality, blurry, pixelated, distorted, ugly, deformed, bad anatomy, watermark, signature, text, logo, oversaturated, overexposed, underexposed',
                'prompt_styles': [],
                'sampler_name': 'Euler a'
            }
        
        if 'output_settings' not in config:
            config['output_settings'] = {
                'output_dir': f"outputs/{config.get('name', 'default').lower().replace(' ', '_')}",
                'filename_pattern': '{prompt}_{seed}_{timestamp}',
                'save_images': True,
                'save_grid': False,
                'save_info': True,
                'save_metadata': True,
                'grid_format': 'png',
                'grid_extended_filename': False,
                'grid_only_if_multiple': True,
                'grid_prevent_empty_spots': False,
                'n_rows': -1,
                'enable_pnginfo': True,
                'pnginfo': '',
                'jpeg_quality': 80,
                'webp_lossless': False,
                'webp_quality': 80,
                'webp_method': 4,
                'webp_effort': 6
            }
        
        if 'script_settings' not in config:
            config['script_settings'] = {
                'script_name': None,
                'script_args': []
            }
        
        if 'alwayson_scripts' not in config:
            config['alwayson_scripts'] = {
                'controlnet': {
                    'args': []
                }
            }
        
        if 'api_settings' not in config:
            config['api_settings'] = {
                'base_url': 'http://127.0.0.1:7860',
                'timeout': 300,
                'retry_attempts': 3
            }
        
        return config
    
    def _merge_dicts(self, defaults: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge default values with config values."""
        result = defaults.copy()
        
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_config(self, config: Dict[str, Any], config_name: str = "<unknown>"):
        """Validate configuration structure and values."""
        # Basic required fields
        required_fields = ['name', 'model_type']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Config '{config_name}': Missing required field: {field}")
        
        # Validate model type
        if config['model_type'] not in ['sd', 'sdxl', 'xl', 'flux']:
            raise ValueError(f"Config '{config_name}': Invalid model type: {config['model_type']}")
        
        # Check for generation settings (required for image generation)
        if 'generation_settings' not in config:
            raise ValueError(f"Config '{config_name}': Missing generation_settings")
        
        gen_settings = config['generation_settings']
        
        # Validate generation settings if present
        if 'steps' in gen_settings:
            if gen_settings['steps'] < 1 or gen_settings['steps'] > 100:
                raise ValueError(f"Config '{config_name}': Steps must be between 1 and 100 (got {gen_settings['steps']})")
        
        if 'width' in gen_settings and 'height' in gen_settings:
            if gen_settings['width'] < 64 or gen_settings['height'] < 64:
                raise ValueError(f"Config '{config_name}': Width and height must be at least 64 (got {gen_settings['width']}x{gen_settings['height']})")
            
            if gen_settings['width'] > 2048 or gen_settings['height'] > 2048:
                raise ValueError(f"Config '{config_name}': Width and height must be at most 2048 (got {gen_settings['width']}x{gen_settings['height']})")
        
        # Check for prompt settings (required for generation)
        if 'prompt_settings' not in config:
            raise ValueError(f"Config '{config_name}': Missing prompt_settings")
        
        prompt_settings = config['prompt_settings']
        if 'base_prompt' not in prompt_settings:
            raise ValueError(f"Config '{config_name}': Missing base_prompt in prompt_settings")
    
    def extract_wildcards_from_template(self, template: str) -> List[str]:
        """Extract wildcard names from prompt template using Automatic1111 format."""
        pattern = r'__([A-Z_]+)__'
        return re.findall(pattern, template)
    
    def validate_wildcards(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate that all wildcards in template have corresponding files."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self.extract_wildcards_from_template(template)
        
        missing_wildcards = []
        available_wildcards = []
        missing_files = []
        
        for wildcard_name in wildcard_names:
            wildcard_path = os.path.join('wildcards', f'{wildcard_name.lower()}.txt')
            if os.path.exists(wildcard_path):
                available_wildcards.append(wildcard_name)
            else:
                missing_wildcards.append(wildcard_name)
                missing_files.append(wildcard_path)
        
        return {
            'missing': missing_wildcards,
            'available': available_wildcards,
            'missing_files': missing_files
        }
    
    def delete_config(self, config_name: str):
        """Delete a configuration file."""
        try:
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
            if os.path.exists(config_path):
                os.remove(config_path)
                logger.log_app_event("config_deleted", {"config_name": config_name})
                return True
            else:
                logger.warning(f"Config file not found for deletion: {config_path}")
                return False
        except Exception as e:
            logger.log_error(f"Failed to delete config {config_name}: {e}")
            return False
    
    def create_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Create a new configuration file."""
        try:
            # Validate the config structure
            self._validate_config(config_data, config_name)
            
            # Save the config
            self.save_config(config_name, config_data)
            
            logger.log_app_event("config_created", {
                "config_name": config_name,
                "model_type": config_data.get('model_type', 'unknown')
            })
            
            return True
        except Exception as e:
            logger.log_error(f"Failed to create config {config_name}: {e}")
            return False
    
    def update_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Update an existing configuration file."""
        try:
            # Check if config exists
            if not self.config_exists(config_name):
                raise FileNotFoundError(f"Config {config_name} not found")
            
            # Validate the config structure
            self._validate_config(config_data, config_name)
            
            # Save the updated config
            self.save_config(config_name, config_data)
            
            logger.log_app_event("config_updated", {
                "config_name": config_name,
                "model_type": config_data.get('model_type', 'unknown')
            })
            
            return True
        except Exception as e:
            logger.log_error(f"Failed to update config {config_name}: {e}")
            return False
    
    def get_config_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of configuration for display."""
        wildcard_validation = self.validate_wildcards(config)
        summary = {
            'name': config['name'],
            'description': config.get('description', ''),
            'model_type': config['model_type'],
            'checkpoint': config['model_settings']['checkpoint'],
            'steps': config['generation_settings']['steps'],
            'width': config['generation_settings']['width'],
            'height': config['generation_settings']['height'],
            'batch_size': config['generation_settings']['batch_size'],
            'num_batches': config['generation_settings'].get('num_batches', 1),
            'total_images': config['generation_settings']['batch_size'] * config['generation_settings'].get('num_batches', 1),
            'wildcards': {
                'available': len(wildcard_validation['available']),
                'missing': len(wildcard_validation['missing']),
                'missing_list': wildcard_validation['missing'],
                'missing_files': wildcard_validation['missing_files']
            },
            'prompt_template': config['prompt_settings']['base_prompt']
        }
        if wildcard_validation['missing']:
            summary['error'] = f"Missing wildcard files: {', '.join(wildcard_validation['missing_files'])} for wildcards: {', '.join(wildcard_validation['missing'])}"
        return summary 

    def get_missing_wildcards(self, config_name: str):
        """Return missing wildcards and files for a config name."""
        config = self.load_config(config_name)
        return {
            'missing_wildcards': config.get('missing_wildcards', []),
            'missing_wildcard_files': config.get('missing_wildcard_files', [])
        }

    def create_missing_wildcard_files(self, config_name: str, default_items: int = 10):
        """Create missing wildcard files for a config, with placeholder content."""
        missing = self.get_missing_wildcards(config_name)
        for wildcard, path in zip(missing['missing_wildcards'], missing['missing_wildcard_files']):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                for i in range(1, default_items+1):
                    f.write(f"{wildcard.lower()}_{i}\n")
        return missing['missing_wildcard_files']

    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations as a dictionary."""
        configs = {}
        config_dir = self.config_dir
        
        # Try to log if logger is available, but don't fail if it's not
        try:
            logger.info(f"Loading all configs from {config_dir}")
        except:
            pass  # Logger not available, continue without logging
        
        if not os.path.exists(config_dir):
            try:
                logger.warning(f"Config directory {config_dir} does not exist.")
            except:
                pass
            return configs
            
        for fname in os.listdir(config_dir):
            if fname.endswith('.json'):
                config_name = os.path.splitext(fname)[0]
                try:
                    config = self.load_config(config_name)
                    configs[config_name] = config
                    try:
                        logger.info(f"Successfully loaded config: {config_name}")
                    except:
                        pass
                except Exception as e:
                    try:
                        logger.log_error(f"Failed to load config {config_name}: {e}")
                    except:
                        pass
                    # Continue loading other configs even if one fails
                    try:
                        print(f"Warning: Failed to load config {config_name}: {e}")
                    except:
                        pass
                    
        if not configs:
            try:
                logger.warning(f"No configuration templates found in {config_dir}.")
            except:
                pass
            try:
                print(f"Warning: No configuration templates found in {config_dir}.")
            except:
                pass
            
        return configs

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get a specific configuration."""
        return self.load_config(config_name)


# Create a global instance for easy importing
config_handler = ConfigHandler() 