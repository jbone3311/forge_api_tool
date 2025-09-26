#!/usr/bin/env python3
"""
Wildcard Service

Handles wildcard management business logic.
"""

from typing import Dict, Any, List, Optional
from core.centralized_logger import logger


class WildcardService:
    """Service for handling wildcard management."""
    
    def __init__(self, app_context):
        """
        Initialize the wildcard service.
        
        Args:
            app_context: Application context containing dependencies
        """
        self.context = app_context
        
        logger.log_app_event("wildcard_service_initialized", {
            "service": "WildcardService"
        })
    
    def get_all_wildcards(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all wildcards."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.get_wildcard_info()
        except Exception as e:
            logger.error(f"Error getting wildcard info: {e}")
            return {}
    
    def get_wildcard_names(self) -> List[str]:
        """Get list of all wildcard names."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.get_wildcard_info().keys()
        except Exception as e:
            logger.error(f"Error getting wildcard names: {e}")
            return []
    
    def get_wildcard_details(self, wildcard_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific wildcard."""
        try:
            all_wildcards = self.get_all_wildcards()
            return all_wildcards.get(wildcard_name)
        except Exception as e:
            logger.error(f"Error getting wildcard details for {wildcard_name}: {e}")
            return None
    
    def preview_wildcard_values(self, wildcard_name: str, count: int = 5) -> List[str]:
        """Preview values for a specific wildcard."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.preview_wildcard_values(wildcard_name, count)
        except Exception as e:
            logger.error(f"Error previewing wildcard {wildcard_name}: {e}")
            return []
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt against available wildcards."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.validate_prompt(prompt)
        except Exception as e:
            logger.error(f"Error validating prompt: {e}")
            return {
                'valid_wildcards': [],
                'invalid_wildcards': [],
                'total_wildcards': 0,
                'validation_passed': False,
                'error': str(e)
            }
    
    def get_usage_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all wildcards."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.get_usage_statistics()
        except Exception as e:
            logger.error(f"Error getting usage statistics: {e}")
            return {}
    
    def reset_wildcards(self):
        """Reset all wildcard managers."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            prompt_builder.reset_all_wildcards()
            logger.info("All wildcards reset")
        except Exception as e:
            logger.error(f"Error resetting wildcards: {e}")
    
    def reload_wildcards(self):
        """Reload all wildcard files from disk."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            prompt_builder.reload_wildcards()
            logger.info("Wildcards reloaded from disk")
        except Exception as e:
            logger.error(f"Error reloading wildcards: {e}")
    
    def search_wildcards(self, query: str) -> List[str]:
        """Search wildcards by name."""
        try:
            all_wildcards = self.get_wildcard_names()
            query_lower = query.lower()
            
            matching_wildcards = [
                wildcard for wildcard in all_wildcards
                if query_lower in wildcard.lower()
            ]
            
            return matching_wildcards
            
        except Exception as e:
            logger.error(f"Error searching wildcards with query '{query}': {e}")
            return []
    
    def get_wildcard_stats(self) -> Dict[str, Any]:
        """Get statistics about wildcards."""
        try:
            all_wildcards = self.get_all_wildcards()
            usage_stats = self.get_usage_statistics()
            
            total_wildcards = len(all_wildcards)
            total_items = sum(info.get('item_count', 0) for info in all_wildcards.values())
            total_usage = sum(stats.get('total_usage', 0) for stats in usage_stats.values())
            
            # Find most and least used wildcards
            most_used = max(usage_stats.items(), key=lambda x: x[1].get('total_usage', 0), default=('None', {'total_usage': 0}))
            least_used = min(usage_stats.items(), key=lambda x: x[1].get('total_usage', 0), default=('None', {'total_usage': 0}))
            
            # Find wildcards with most items
            most_items = max(all_wildcards.items(), key=lambda x: x[1].get('item_count', 0), default=('None', {'item_count': 0}))
            
            return {
                'total_wildcards': total_wildcards,
                'total_items': total_items,
                'total_usage': total_usage,
                'average_items_per_wildcard': total_items / total_wildcards if total_wildcards > 0 else 0,
                'average_usage_per_wildcard': total_usage / total_wildcards if total_wildcards > 0 else 0,
                'most_used_wildcard': {
                    'name': most_used[0],
                    'usage_count': most_used[1].get('total_usage', 0)
                },
                'least_used_wildcard': {
                    'name': least_used[0],
                    'usage_count': least_used[1].get('total_usage', 0)
                },
                'wildcard_with_most_items': {
                    'name': most_items[0],
                    'item_count': most_items[1].get('item_count', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting wildcard stats: {e}")
            return {}
    
    def analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze the complexity of a prompt."""
        try:
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.analyze_prompt_complexity(prompt)
        except Exception as e:
            logger.error(f"Error analyzing prompt complexity: {e}")
            return {
                'total_wildcards': 0,
                'unique_wildcards': 0,
                'valid_wildcards': 0,
                'invalid_wildcards': 0,
                'estimated_combinations': 0,
                'complexity_score': 0,
                'validation_passed': False,
                'error': str(e)
            }
    
    def generate_prompt_variations(self, config_name: str, count: int = 10) -> List[str]:
        """Generate multiple variations of a prompt for a configuration."""
        try:
            config_service = self.context.get_component('config_service')
            if not config_service:
                # Fallback to direct access
                config_handler = self.context.get_config_handler()
                settings_info = config_handler.get_setting(config_name)
                if not settings_info:
                    return []
                config = settings_info['config']
            else:
                config = config_service.get_config(config_name)
                if not config:
                    return []
                config = config['config']
            
            prompt_builder = self.context.get_prompt_builder()
            return prompt_builder.generate_prompt_variations(config, count)
            
        except Exception as e:
            logger.error(f"Error generating prompt variations for {config_name}: {e}")
            return []


