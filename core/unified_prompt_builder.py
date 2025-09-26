#!/usr/bin/env python3
"""
Unified Prompt Builder

A streamlined prompt building system that handles wildcard substitution
with support for both auto-discovery and single-file modes.
"""

import re
import os
from typing import Dict, List, Any, Optional
from .unified_wildcard_manager import UnifiedWildcardManager


class UnifiedPromptBuilder:
    """
    Unified prompt builder that can work with individual wildcard files
    or automatically discover and use all wildcard files.
    """

    def __init__(self, wildcard_manager: Optional[UnifiedWildcardManager] = None, 
                 wildcards_base_dir: str = "wildcards", usage_file: str = "wildcard_usage.json",
                 auto_discover: bool = True, single_file: Optional[str] = None):
        """
        Initialize the unified prompt builder.
        
        Args:
            wildcard_manager: Existing wildcard manager instance (optional)
            wildcards_base_dir: Base directory for wildcard files (when auto_discover=True)
            usage_file: File to store usage statistics
            auto_discover: Whether to automatically discover all wildcard files
            single_file: Specific wildcard file to manage (when auto_discover=False)
        """
        if wildcard_manager is not None:
            self.wildcard_manager = wildcard_manager
        else:
            self.wildcard_manager = UnifiedWildcardManager(
                wildcards_base_dir=wildcards_base_dir,
                usage_file=usage_file,
                auto_discover=auto_discover,
                single_file=single_file
            )

    def build_prompt(self, config: Dict[str, Any]) -> str:
        """Build a single prompt by substituting wildcards."""
        template = config.get('prompt_settings', {}).get('base_prompt', '')
        if not template:
            return ""
        
        return self.wildcard_manager.process_prompt(template)

    def build_prompts(self, config: Dict[str, Any], count: int) -> List[str]:
        """Build multiple prompts for a batch."""
        return [self.build_prompt(config) for _ in range(count)]

    def preview_prompts(self, config: Dict[str, Any], count: int = 5) -> List[str]:
        """Preview prompts without consuming wildcards."""
        template = config.get('prompt_settings', {}).get('base_prompt', '')
        if not template:
            return []
        
        return self.wildcard_manager.preview_prompt(template, count)

    def build_prompt_with_negative(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Build a prompt with both positive and negative prompts."""
        base_prompt = self.build_prompt(config)
        
        # Process negative prompt if it exists
        negative_template = config.get('prompt_settings', {}).get('negative_prompt', '')
        negative_prompt = ""
        if negative_template:
            negative_prompt = self.wildcard_manager.process_prompt(negative_template)
        
        return {
            'positive': base_prompt,
            'negative': negative_prompt
        }

    def build_prompts_with_negative(self, config: Dict[str, Any], count: int) -> List[Dict[str, str]]:
        """Build multiple prompts with both positive and negative prompts."""
        return [self.build_prompt_with_negative(config) for _ in range(count)]

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt against available wildcards."""
        return self.wildcard_manager.validate_prompt(prompt)

    def validate_config_prompt(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a configuration's prompt against available wildcards."""
        template = config.get('prompt_settings', {}).get('base_prompt', '')
        if not template:
            return {
                'valid_wildcards': [],
                'invalid_wildcards': [],
                'total_wildcards': 0,
                'validation_passed': True,
                'error': 'No base prompt found in configuration'
            }
        
        return self.wildcard_manager.validate_prompt(template)

    def get_wildcard_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available wildcards."""
        return self.wildcard_manager.get_wildcard_info()

    def get_usage_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive usage statistics for all wildcards."""
        return self.wildcard_manager.get_usage_statistics()

    def reset_all_wildcards(self):
        """Reset all wildcard managers."""
        self.wildcard_manager.reset_all_wildcards()

    def reload_wildcards(self):
        """Reload all wildcard files from disk."""
        self.wildcard_manager.reload_wildcards()

    def extract_wildcards_from_prompt(self, prompt: str) -> List[str]:
        """Extract all wildcard names from a prompt template."""
        wildcard_pattern = r'__(\w+)__'
        return re.findall(wildcard_pattern, prompt)