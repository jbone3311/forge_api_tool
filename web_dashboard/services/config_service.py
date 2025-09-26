#!/usr/bin/env python3
"""
Configuration Service

Handles configuration management business logic.
"""

from typing import Dict, Any, List, Optional
from core.centralized_logger import logger


class ConfigService:
    """Service for handling configuration management."""
    
    def __init__(self, app_context):
        """
        Initialize the configuration service.
        
        Args:
            app_context: Application context containing dependencies
        """
        self.context = app_context
        
        logger.log_app_event("config_service_initialized", {
            "service": "ConfigService"
        })
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configurations with enhanced information."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.get_all_settings()
        except Exception as e:
            logger.error(f"Error getting all configs: {e}")
            return {}
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific configuration."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.get_setting(config_name)
        except Exception as e:
            logger.error(f"Error getting config {config_name}: {e}")
            return None
    
    def get_config_list(self) -> List[Dict[str, Any]]:
        """Get a list of all configurations."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.list_configs()
        except Exception as e:
            logger.error(f"Error getting config list: {e}")
            return []
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Save a configuration."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.save_config(config_name, config_data)
        except Exception as e:
            logger.error(f"Error saving config {config_name}: {e}")
            return False
    
    def create_template_config(self, config_name: str) -> bool:
        """Create a new template configuration."""
        try:
            config_handler = self.context.get_config_handler()
            template_config = config_handler.create_template_config()
            return config_handler.save_config(config_name, template_config)
        except Exception as e:
            logger.error(f"Error creating template config {config_name}: {e}")
            return False
    
    def export_config(self, config_name: str, output_path: str) -> bool:
        """Export a configuration to a file."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.export_config(config_name, output_path)
        except Exception as e:
            logger.error(f"Error exporting config {config_name}: {e}")
            return False
    
    def import_config(self, input_path: str, config_name: str) -> bool:
        """Import a configuration from a file."""
        try:
            config_handler = self.context.get_config_handler()
            return config_handler.import_config(input_path, config_name)
        except Exception as e:
            logger.error(f"Error importing config from {input_path}: {e}")
            return False
    
    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """Validate a configuration."""
        try:
            config = self.get_config(config_name)
            if not config:
                return {
                    'valid': False,
                    'error': f"Configuration '{config_name}' not found"
                }
            
            config_data = config['config']
            prompt_builder = self.context.get_prompt_builder()
            
            # Validate prompt
            validation_result = prompt_builder.validate_config_prompt(config_data)
            
            return {
                'valid': validation_result['validation_passed'],
                'wildcard_info': validation_result,
                'config': config_data,
                'has_thumbnail': config.get('has_thumbnail', False)
            }
            
        except Exception as e:
            logger.error(f"Error validating config {config_name}: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_config_thumbnail(self, config_name: str) -> Optional[str]:
        """Get the thumbnail path for a configuration."""
        try:
            config = self.get_config(config_name)
            if config and config.get('has_thumbnail'):
                return config.get('thumbnail')
            return None
        except Exception as e:
            logger.error(f"Error getting thumbnail for {config_name}: {e}")
            return None
    
    def search_configs(self, query: str) -> List[Dict[str, Any]]:
        """Search configurations by name, description, or tags."""
        try:
            all_configs = self.get_config_list()
            query_lower = query.lower()
            
            matching_configs = []
            for config in all_configs:
                # Search in name, description, and tags
                if (query_lower in config['name'].lower() or
                    query_lower in config['description'].lower() or
                    any(query_lower in tag.lower() for tag in config.get('tags', []))):
                    matching_configs.append(config)
            
            return matching_configs
            
        except Exception as e:
            logger.error(f"Error searching configs with query '{query}': {e}")
            return []
    
    def get_config_stats(self) -> Dict[str, Any]:
        """Get statistics about configurations."""
        try:
            configs = self.get_config_list()
            
            total_configs = len(configs)
            configs_with_issues = sum(1 for config in configs if config.get('has_issues', False))
            configs_with_thumbnails = sum(1 for config in configs if config.get('has_thumbnail', False))
            
            # Count by model type
            model_counts = {}
            for config in configs:
                model = config.get('model', 'unknown')
                model_counts[model] = model_counts.get(model, 0) + 1
            
            # Count by tags
            tag_counts = {}
            for config in configs:
                for tag in config.get('tags', []):
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            return {
                'total_configs': total_configs,
                'configs_with_issues': configs_with_issues,
                'configs_with_thumbnails': configs_with_thumbnails,
                'model_counts': model_counts,
                'tag_counts': tag_counts,
                'health_percentage': ((total_configs - configs_with_issues) / total_configs * 100) if total_configs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting config stats: {e}")
            return {}


