import re
import os
from typing import Dict, List, Any, Tuple
from wildcard_manager import WildcardManagerFactory


class PromptBuilder:
    """Builds prompts by substituting wildcards with values from WildcardManager."""
    
    def __init__(self, wildcard_factory: WildcardManagerFactory):
        self.wildcard_factory = wildcard_factory
    
    def _wildcard_path(self, wildcard_name: str) -> str:
        return os.path.join('wildcards', f'{wildcard_name.lower()}.txt')
    
    def build_prompt(self, config: Dict[str, Any]) -> str:
        """Build a single prompt by substituting wildcards."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        prompt = template
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            value = manager.get_next()
            prompt = prompt.replace(f"__{wildcard_name}__", value)
        return prompt
    
    def build_prompt_batch(self, config: Dict[str, Any], count: int) -> List[str]:
        """Build multiple prompts for a batch."""
        return [self.build_prompt(config) for _ in range(count)]
    
    def preview_prompts(self, config: Dict[str, Any], count: int = 5) -> List[str]:
        """Preview prompts without consuming wildcards."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        wildcard_previews = {}
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            preview_values = manager.get_preview(count)
            wildcard_previews[wildcard_name] = preview_values
        preview_prompts = []
        for i in range(count):
            prompt = template
            for wildcard_name in wildcard_names:
                values = wildcard_previews.get(wildcard_name, [])
                if i < len(values):
                    prompt = prompt.replace(f"__{wildcard_name}__", values[i])
                else:
                    prompt = prompt.replace(f"__{wildcard_name}__", values[0] if values else f"__{wildcard_name}__")
            preview_prompts.append(prompt)
        return preview_prompts
    
    def get_wildcard_usage_info(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get usage information for all wildcards in the config."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        usage_info = {}
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            stats = manager.get_usage_stats()
            total_uses = sum(stats.values()) if stats else 0
            usage_percentages = {}
            for item, count in stats.items():
                percentage = (count / total_uses) * 100 if total_uses > 0 else 0.0
                usage_percentages[item] = {
                    'count': count,
                    'percentage': percentage,
                    'status': self._get_usage_status(percentage)
                }
            usage_info[wildcard_name] = {
                'total_uses': total_uses,
                'items': usage_percentages,
                'least_used': manager.get_least_used_items(5)
            }
        return usage_info
    
    def _extract_wildcards(self, template: str) -> List[str]:
        """Extract wildcard names from template string using Automatic1111 format."""
        # Automatic1111 uses __WILDCARD_NAME__ format
        pattern = r'__([A-Z_]+)__'
        return re.findall(pattern, template)
    
    def _get_usage_status(self, percentage: float) -> str:
        """Get usage status based on percentage."""
        if percentage == 0:
            return 'unused'
        elif percentage < 50:
            return 'low'
        elif percentage < 90:
            return 'medium'
        else:
            return 'high'
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a prompt template against available wildcards."""
        wildcard_names = self._extract_wildcards(template)
        
        missing = []
        available = []
        
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            if os.path.exists(wildcard_path):
                available.append(wildcard_name)
            else:
                missing.append(wildcard_name)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'available': available,
            'total_wildcards': len(wildcard_names)
        }
    
    def get_prompt_stats(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the prompt template and wildcards."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        validation = self.validate_template(template)
        
        # Count wildcard items
        total_wildcard_items = 0
        wildcard_item_counts = {}
        
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            item_count = len(manager.items)
            wildcard_item_counts[wildcard_name] = item_count
            total_wildcard_items += item_count
        
        return {
            'template': template,
            'wildcard_count': len(wildcard_names),
            'total_wildcard_items': total_wildcard_items,
            'wildcard_item_counts': wildcard_item_counts,
            'validation': validation,
            'estimated_combinations': self._calculate_combinations(wildcard_item_counts)
        }
    
    def _calculate_combinations(self, wildcard_counts: Dict[str, int]) -> int:
        """Calculate estimated number of unique prompt combinations."""
        if not wildcard_counts:
            return 0
        
        combinations = 1
        for count in wildcard_counts.values():
            combinations *= count
        
        return combinations
    
    def reset_wildcards(self, config: Dict[str, Any]):
        """Reset all wildcard managers for this config."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            manager.reset()
    
    def export_prompt_list(self, config: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Export a list of prompts with their wildcard values."""
        template = config['prompt_settings']['base_prompt']
        wildcard_names = self._extract_wildcards(template)
        wildcard_previews = {}
        for wildcard_name in wildcard_names:
            wildcard_path = self._wildcard_path(wildcard_name)
            manager = self.wildcard_factory.get_manager(wildcard_path)
            preview_values = manager.get_preview(count)
            wildcard_previews[wildcard_name] = preview_values
        prompts = []
        for i in range(count):
            prompt = template
            wildcard_values = {}
            for wildcard_name in wildcard_names:
                values = wildcard_previews.get(wildcard_name, [])
                if i < len(values):
                    value = values[i]
                else:
                    value = values[0] if values else f"__{wildcard_name}__"
                wildcard_values[wildcard_name] = value
                prompt = prompt.replace(f"__{wildcard_name}__", value)
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