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
            
            # Validate configuration
            self._validate_config(config)
            
            return config
        except Exception as e:
            raise ValueError(f"Error loading config {config_name}: {e}")
    
    def save_config(self, config: Dict[str, Any], config_name: str):
        """Save a configuration to file."""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            raise ValueError(f"Error saving config {config_name}: {e}")
    
    def list_configs(self) -> List[str]:
        """List all available configuration files."""
        configs = []
        if os.path.exists(self.config_dir):
            for file in os.listdir(self.config_dir):
                if file.endswith('.json') and file != 'template.json':
                    configs.append(file.replace('.json', ''))
        return sorted(configs)
    
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
                    'steps': 30,
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
                    'checkpoint': 'sdxl-v1.safetensors',
                    'vae': '',
                    'text_encoder': 'clip_l.safetensors',
                    'gpu_weight': None,
                    'swap_method': 'queue',
                    'swap_location': 'cpu'
                },
                'generation_settings': {
                    'sampler': 'Euler a',
                    'scheduler': 'Karras',
                    'steps': 30,
                    'cfg_scale': 7.0,
                    'distilled_cfg_scale': None,
                    'width': 512,
                    'height': 768,
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
                'prompt_template': 'a photo of a {animal} in {location}, {style}, cinematic lighting',
                'negative_prompt': 'low quality, blurry, distorted, ugly, bad anatomy'
            },
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
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure and values."""
        required_fields = ['name', 'model_type', 'model_settings', 'generation_settings', 
                          'prompt_settings', 'wildcards', 'output_settings']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate model type
        if config['model_type'] not in ['sd', 'xl', 'flux']:
            raise ValueError(f"Invalid model type: {config['model_type']}")
        
        # Validate wildcard files exist
        for wildcard_name, wildcard_path in config['wildcards'].items():
            if isinstance(wildcard_path, str) and not os.path.exists(wildcard_path):
                print(f"Warning: Wildcard file not found: {wildcard_path}")
        
        # Validate generation settings
        gen_settings = config['generation_settings']
        if gen_settings['steps'] < 1 or gen_settings['steps'] > 100:
            raise ValueError("Steps must be between 1 and 100")
        
        if gen_settings['width'] < 64 or gen_settings['height'] < 64:
            raise ValueError("Width and height must be at least 64")
        
        if gen_settings['width'] > 2048 or gen_settings['height'] > 2048:
            raise ValueError("Width and height must be at most 2048")
    
    def extract_wildcards_from_template(self, template: str) -> List[str]:
        """Extract wildcard names from prompt template."""
        pattern = r'\{([^}]+)\}'
        return re.findall(pattern, template)
    
    def validate_wildcards(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate that all wildcards in template have corresponding files/lists."""
        template = config['prompt_settings']['prompt_template']
        wildcard_names = self.extract_wildcards_from_template(template)
        
        missing_wildcards = []
        available_wildcards = []
        
        for wildcard_name in wildcard_names:
            if wildcard_name not in config['wildcards']:
                missing_wildcards.append(wildcard_name)
            else:
                available_wildcards.append(wildcard_name)
        
        return {
            'missing': missing_wildcards,
            'available': available_wildcards
        }
    
    def get_config_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of configuration for display."""
        wildcard_validation = self.validate_wildcards(config)
        
        return {
            'name': config['name'],
            'description': config.get('description', ''),
            'model_type': config['model_type'],
            'checkpoint': config['model_settings']['checkpoint'],
            'steps': config['generation_settings']['steps'],
            'width': config['generation_settings']['width'],
            'height': config['generation_settings']['height'],
            'batch_size': config['generation_settings']['batch_size'],
            'num_batches': config['generation_settings']['num_batches'],
            'total_images': config['generation_settings']['batch_size'] * config['generation_settings']['num_batches'],
            'wildcards': {
                'available': len(wildcard_validation['available']),
                'missing': len(wildcard_validation['missing']),
                'missing_list': wildcard_validation['missing']
            },
            'prompt_template': config['prompt_settings']['prompt_template']
        } 