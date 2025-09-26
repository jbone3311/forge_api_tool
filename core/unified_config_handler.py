#!/usr/bin/env python3
"""
Unified Configuration Handler

A streamlined configuration management system that handles loading, saving,
and validation of JSON configuration files with wildcard support.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from core.centralized_logger import logger


class UnifiedConfigHandler:
    """
    Unified configuration handler that supports both basic configuration management
    and enhanced validation with wildcard checking.
    """

    def __init__(self, config_dir: str = "configs"):
        """
        Initialize the unified configuration handler.
        
        Args:
            config_dir: Directory containing configuration files
        """
        # Set up config directory with absolute path handling
        if not os.path.isabs(config_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
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
            
            # Validate configuration
            self._validate_config(config, config_name)
            
            # Check for missing wildcards (non-blocking)
            try:
                wildcards_info = self.validate_wildcards(config)
                config['missing_wildcards'] = wildcards_info['missing']
                config['missing_wildcard_files'] = wildcards_info['missing_files']
            except Exception as e:
                config['missing_wildcards'] = []
                config['missing_wildcard_files'] = []
                logger.warning(f"Wildcard validation failed for {config_name}: {e}")
            
            return config
            
        except Exception as e:
            logger.error(f"Error loading config {config_name}: {e}")
            raise

    def save_config(self, config_name: str, config: Dict[str, Any]) -> bool:
        """Save a configuration to file."""
        try:
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
            
            # Validate before saving
            self._validate_config(config, config_name)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved: {config_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config {config_name}: {e}")
            return False

    def list_configs(self) -> List[Dict[str, Any]]:
        """List all available configurations."""
        configs = []
        
        if not os.path.exists(self.config_dir):
            return configs
        
        for config_file in os.listdir(self.config_dir):
            if config_file.endswith('.json'):
                config_name = config_file[:-5]  # Remove .json extension
                try:
                    config = self.load_config(config_name)
                    config_info = {
                        'name': config_name,
                        'description': config.get('description', ''),
                        'model': config.get('model', 'unknown'),
                        'tags': config.get('tags', []),
                        'has_issues': len(config.get('missing_wildcards', [])) > 0
                    }
                    configs.append(config_info)
                    
                except Exception as e:
                    logger.warning(f"Could not load config {config_name}: {e}")
                    configs.append({
                        'name': config_name,
                        'description': 'Error loading config',
                        'model': 'unknown',
                        'tags': [],
                        'has_issues': True
                    })
        
        return sorted(configs, key=lambda x: x['name'])

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations as a dictionary."""
        configs = {}
        
        if not os.path.exists(self.config_dir):
            return configs
        
        for config_file in os.listdir(self.config_dir):
            if config_file.endswith('.json'):
                config_name = config_file[:-5]
                
                try:
                    config = self.load_config(config_name)
                    configs[config_name] = {
                        'config': config,
                        'settings_file': os.path.join(self.config_dir, config_file),
                        'description': config.get('description', ''),
                        'tags': config.get('tags', [])
                    }
                    
                except Exception as e:
                    logger.error(f"Error loading config {config_name}: {e}")
        
        return configs

    def _set_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Set default values for missing configuration fields."""
        defaults = {
            'model': 'sd',
            'description': '',
            'tags': [],
            'prompt_settings': {
                'base_prompt': '',
                'negative_prompt': '',
                'wildcards': {}
            },
            'generation_settings': {
                'steps': 20,
                'cfg_scale': 7.0,
                'width': 512,
                'height': 512,
                'sampler': 'Euler a',
                'seed': -1
            },
            'batch_settings': {
                'batch_size': 1,
                'batch_count': 1
            }
        }
        
        return self._merge_defaults(config, defaults)

    def _merge_defaults(self, config: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge defaults into config."""
        result = defaults.copy()
        
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_defaults(value, result[key])
            else:
                result[key] = value
        
        return result

    def _validate_config(self, config: Dict[str, Any], config_name: str) -> None:
        """Validate configuration structure."""
        required_fields = ['prompt_settings', 'generation_settings']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in config '{config_name}'")
        
        # Validate prompt settings
        prompt_settings = config['prompt_settings']
        if 'base_prompt' not in prompt_settings:
            raise ValueError(f"Missing 'base_prompt' in prompt_settings for config '{config_name}'")
        
        # Validate generation settings
        gen_settings = config['generation_settings']
        required_gen_fields = ['steps', 'cfg_scale', 'width', 'height']
        for field in required_gen_fields:
            if field not in gen_settings:
                raise ValueError(f"Missing required field '{field}' in generation_settings for config '{config_name}'")

    def validate_wildcards(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate wildcards in configuration."""
        missing_wildcards = []
        missing_files = []
        
        base_prompt = config.get('prompt_settings', {}).get('base_prompt', '')
        wildcard_pattern = r'__(\w+)__'
        wildcards = re.findall(wildcard_pattern, base_prompt)
        
        for wildcard in wildcards:
            wildcard_file = os.path.join('wildcards', f'{wildcard.lower()}.txt')
            if not os.path.exists(wildcard_file):
                missing_wildcards.append(wildcard)
                missing_files.append(wildcard_file)
        
        return {
            'missing': missing_wildcards,
            'missing_files': missing_files,
            'total_wildcards': len(wildcards),
            'valid_wildcards': len(wildcards) - len(missing_wildcards)
        }

    def create_template_config(self) -> Dict[str, Any]:
        """Create a template configuration."""
        return {
            'model': 'sd',
            'description': 'Template configuration - modify as needed',
            'tags': ['template'],
            'prompt_settings': {
                'base_prompt': 'A beautiful __subject__ in __style__, __mood__, __lighting__',
                'negative_prompt': 'blurry, low quality, distorted',
                'wildcards': {}
            },
            'generation_settings': {
                'steps': 20,
                'cfg_scale': 7.0,
                'width': 512,
                'height': 512,
                'sampler': 'Euler a',
                'seed': -1
            },
            'batch_settings': {
                'batch_size': 1,
                'batch_count': 1
            }
        }

    def config_exists(self, config_name: str) -> bool:
        """Check if a configuration exists."""
        config_path = os.path.join(self.config_dir, f"{config_name}.json")
        return os.path.exists(config_path)

    def delete_config(self, config_name: str) -> bool:
        """Delete a configuration file."""
        try:
            config_path = os.path.join(self.config_dir, f"{config_name}.json")
            if os.path.exists(config_path):
                os.remove(config_path)
                logger.info(f"Configuration deleted: {config_name}")
                return True
            else:
                logger.warning(f"Config file not found for deletion: {config_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete config {config_name}: {e}")
            return False

    def create_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Create a new configuration file."""
        try:
            # Validate the config structure
            self._validate_config(config_data, config_name)
            
            # Save the config
            return self.save_config(config_name, config_data)
            
        except Exception as e:
            logger.error(f"Failed to create config {config_name}: {e}")
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
            return self.save_config(config_name, config_data)
            
        except Exception as e:
            logger.error(f"Failed to update config {config_name}: {e}")
            return False