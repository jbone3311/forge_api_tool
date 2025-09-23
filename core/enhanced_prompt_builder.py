import re
import os
from typing import Dict, List, Any
from .enhanced_wildcard_manager import EnhancedWildcardManager


class EnhancedPromptBuilder:
    """Enhanced prompt builder that automatically uses all wildcard files."""

    def __init__(self, wildcards_base_dir: str = "wildcards", usage_file: str = "wildcard_usage.json"):
        self.wildcard_manager = EnhancedWildcardManager(wildcards_base_dir, usage_file)

    def build_prompt(self, config: Dict[str, Any]) -> str:
        """Build a single prompt by substituting wildcards."""
        template = config['prompt_settings']['base_prompt']
        return self.wildcard_manager.process_prompt(template)

    def build_prompt_batch(self, config: Dict[str, Any], count: int) -> List[str]:
        """Build multiple prompts for a batch."""
        return [self.build_prompt(config) for _ in range(count)]

    def preview_prompts(self, config: Dict[str, Any], count: int = 5) -> List[str]:
        """Preview prompts without consuming wildcards."""
        template = config['prompt_settings']['base_prompt']
        return self.wildcard_manager.preview_prompt(template, count)

    def get_wildcard_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available wildcards."""
        return self.wildcard_manager.get_wildcard_info()

    def get_available_wildcards(self) -> List[str]:
        """Get list of all available wildcard names."""
        return self.wildcard_manager.get_wildcard_names()

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt against available wildcards."""
        return self.wildcard_manager.validate_prompt(prompt)

    def get_usage_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive usage statistics for all wildcards."""
        return self.wildcard_manager.get_usage_statistics()

    def reset_all_wildcards(self):
        """Reset all wildcard managers."""
        self.wildcard_manager.reset_all_wildcards()

    def reload_wildcards(self):
        """Reload all wildcard files from disk."""
        self.wildcard_manager.reload_wildcards()

    def export_prompt_list(self, config: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Export a list of prompts with their wildcard values."""
        template = config['prompt_settings']['base_prompt']
        previews = self.wildcard_manager.preview_prompt(template, count)
        
        prompts = []
        for i, prompt in enumerate(previews):
            # Extract wildcard values from the processed prompt
            wildcard_values = {}
            original_wildcards = re.findall(r'__([A-Z_]+)__', template)
            
            # This is a simplified extraction - in a real implementation,
            # you'd want to track which values were used for each wildcard
            for wildcard_name in original_wildcards:
                # Find the value that replaced this wildcard
                # This is a placeholder - actual implementation would be more complex
                wildcard_values[wildcard_name] = f"extracted_value_{i}"
            
            prompts.append({
                'index': i + 1,
                'prompt': prompt,
                'wildcard_values': wildcard_values
            })
        
        return prompts

    def generate_prompts(self, config: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Generate multiple prompts with metadata."""
        return [{
            'prompt': self.build_prompt(config),
            'index': i,
            'seed': config.get('generation_settings', {}).get('seed', 'random')
        } for i in range(count)]

    def get_prompt_statistics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the prompt template and wildcards."""
        template = config['prompt_settings']['base_prompt']
        validation = self.validate_prompt(template)
        
        # Count wildcard items
        wildcard_info = self.get_wildcard_info()
        total_wildcard_items = 0
        wildcard_item_counts = {}
        
        wildcard_patterns = re.findall(r'__([A-Z_]+)__', template)
        for wildcard_name in wildcard_patterns:
            if wildcard_name in wildcard_info:
                item_count = wildcard_info[wildcard_name]['item_count']
                wildcard_item_counts[wildcard_name] = item_count
                total_wildcard_items += item_count

        return {
            'template': template,
            'wildcard_count': len(wildcard_patterns),
            'total_wildcard_items': total_wildcard_items,
            'wildcard_item_counts': wildcard_item_counts,
            'validation': validation,
            'estimated_combinations': self._calculate_combinations(wildcard_item_counts),
            'available_wildcards': self.get_available_wildcards()
        }

    def _calculate_combinations(self, wildcard_counts: Dict[str, int]) -> int:
        """Calculate estimated number of unique prompt combinations."""
        if not wildcard_counts:
            return 0

        combinations = 1
        for count in wildcard_counts.values():
            combinations *= count

        return combinations

    def create_sample_prompts(self, count: int = 10) -> List[str]:
        """Create sample prompts using available wildcards."""
        # Get some common wildcards that are likely to be available
        available_wildcards = self.get_available_wildcards()
        
        # Create a simple template using some common wildcards
        common_wildcards = ['SUBJECT', 'SETTING', 'STYLE', 'MOOD', 'CAMERA']
        template_parts = []
        
        for wildcard in common_wildcards:
            if wildcard in available_wildcards:
                template_parts.append(f"__{wildcard}__")
        
        if not template_parts:
            return [f"Sample prompt {i+1}" for i in range(count)]
        
        # Create a simple template
        template = ", ".join(template_parts)
        
        # Generate sample prompts
        sample_config = {
            'prompt_settings': {
                'base_prompt': template
            }
        }
        
        return self.preview_prompts(sample_config, count)

    def get_wildcard_suggestions(self, partial_name: str = "") -> List[str]:
        """Get wildcard name suggestions based on partial input."""
        available_wildcards = self.get_available_wildcards()
        
        if not partial_name:
            return available_wildcards[:10]  # Return first 10
        
        # Filter wildcards that contain the partial name
        suggestions = [name for name in available_wildcards if partial_name.upper() in name.upper()]
        return suggestions[:10]  # Return first 10 matches
