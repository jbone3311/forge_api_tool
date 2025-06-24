import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import re


class ConfigHandler:
    """Handles loading, validation, and management of JSON configuration files."""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.template_path = os.path.join(config_dir, "template.json")
        os.makedirs(config_dir, exist_ok=True)
        
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
            # Check for missing wildcards
            wildcards_info = self.validate_wildcards(config)
            config['missing_wildcards'] = wildcards_info['missing']
            config['missing_wildcard_files'] = wildcards_info['missing_files']
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
        
        # Model-specific defaults
        if model_type == 'sd':
            defaults = {
                'model_settings': {
                    'checkpoint': 'sd-v1-5.safetensors',
                    'vae': '',
                    'text_encoder': '',
                    'gpu_weight': None,
                    'swap_method': 'queue',
                    'swap_location': 'cpu'
                },
                'generation_settings': {
                    'sampler': 'Euler a',
                    'scheduler': 'Simple',
                    'steps': 20,
                    'cfg_scale': 7.0,
                    'distilled_cfg_scale': None,
                    'width': 512,
                    'height': 512,
                    'batch_size': 1,
                    'num_batches': 10,
                    'seed': 'random'
                }
            }
        elif model_type == 'xl':
            defaults = {
                'model_settings': {
                    'checkpoint': 'sd_xl_base_1.0.safetensors',
                    'vae': 'sdxl_vae.safetensors',
                    'text_encoder': '',
                    'gpu_weight': None,
                    'swap_method': 'queue',
                    'swap_location': 'cpu'
                },
                'generation_settings': {
                    'sampler': 'DPM++ 2M Karras',
                    'scheduler': 'Simple',
                    'steps': 25,
                    'cfg_scale': 7.0,
                    'distilled_cfg_scale': None,
                    'width': 1024,
                    'height': 1024,
                    'batch_size': 1,
                    'num_batches': 10,
                    'seed': 'random'
                }
            }
        elif model_type == 'flux':
            defaults = {
                'model_settings': {
                    'checkpoint': 'flux1-dev-bnb-nf4-v2.safetensors',
                    'vae': '',
                    'text_encoder': 't5xxl_fp16.safetensors',
                    'gpu_weight': None,
                    'swap_method': 'queue',
                    'swap_location': 'cpu'
                },
                'generation_settings': {
                    'sampler': 'Euler',
                    'scheduler': 'Simple',
                    'steps': 20,
                    'cfg_scale': None,
                    'distilled_cfg_scale': 3.5,
                    'width': 1024,
                    'height': 1024,
                    'batch_size': 1,
                    'num_batches': 10,
                    'seed': 'random'
                }
            }
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Merge defaults with config
        config = self._merge_dicts(defaults, config)
        
        # General defaults
        general_defaults = {
            'prompt_settings': {
                'base_prompt': 'a photo of a __ANIMAL__ in __LOCATION__, __STYLE__, cinematic lighting',
                'negative_prompt': 'low quality, blurry, distorted, ugly, bad anatomy'
            },
            'wildcards': {},
            'output_settings': {
                'dir': f"./outputs/{config.get('name', 'default')}/{{timestamp}}/",
                'format': 'png',
                'save_metadata': True,
                'save_prompts': True
            },
            'controlnet': [],
            'alwayson_scripts': {
                'Lora': []
            },
            'forge_api': {
                'base_url': 'http://127.0.0.1:7860',
                'timeout': 300,
                'retry_attempts': 3
            }
        }
        
        config = self._merge_dicts(general_defaults, config)
        
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
        required_fields = ['name', 'model_type', 'model_settings', 'generation_settings', 
                          'prompt_settings', 'output_settings']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Config '{config_name}': Missing required field: {field}")
        
        # Validate model type
        if config['model_type'] not in ['sd', 'xl', 'flux']:
            raise ValueError(f"Config '{config_name}': Invalid model type: {config['model_type']}")
        
        # Validate generation settings
        gen_settings = config['generation_settings']
        if gen_settings['steps'] < 1 or gen_settings['steps'] > 100:
            raise ValueError(f"Config '{config_name}': Steps must be between 1 and 100 (got {gen_settings['steps']})")
        
        if gen_settings['width'] < 64 or gen_settings['height'] < 64:
            raise ValueError(f"Config '{config_name}': Width and height must be at least 64 (got {gen_settings['width']}x{gen_settings['height']})")
        
        if gen_settings['width'] > 2048 or gen_settings['height'] > 2048:
            raise ValueError(f"Config '{config_name}': Width and height must be at most 2048 (got {gen_settings['width']}x{gen_settings['height']})")
    
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
            else:
                raise FileNotFoundError(f"Config {config_name} not found")
        except Exception as e:
            raise ValueError(f"Error deleting config {config_name}: {e}")
    
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