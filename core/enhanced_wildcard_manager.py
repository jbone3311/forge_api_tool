import random
import json
import os
import re
from typing import List, Dict, Optional, Set, Any
from pathlib import Path


class EnhancedWildcardManager:
    """
    Enhanced wildcard manager that automatically discovers and uses all .txt files
    in the wildcards directory structure.
    """

    def __init__(self, wildcards_base_dir: str = "wildcards", usage_file: str = "wildcard_usage.json"):
        self.wildcards_base_dir = wildcards_base_dir
        self.usage_file = usage_file
        self.wildcard_files = self._discover_wildcard_files()
        self.managers: Dict[str, 'WildcardManager'] = {}
        self.usage_stats = self._load_usage_stats()
        
        # Initialize managers for all discovered files
        for file_path in self.wildcard_files:
            wildcard_name = self._get_wildcard_name(file_path)
            self.managers[wildcard_name] = WildcardManager(file_path, self.usage_file)

    def _discover_wildcard_files(self) -> List[str]:
        """Discover all .txt files in the wildcards directory structure."""
        wildcard_files = []
        
        if not os.path.exists(self.wildcards_base_dir):
            return wildcard_files
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.wildcards_base_dir):
            for file in files:
                if file.endswith('.txt') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    wildcard_files.append(file_path)
        
        return sorted(wildcard_files)

    def _get_wildcard_name(self, file_path: str) -> str:
        """Convert file path to wildcard name for use in prompts."""
        # Remove base directory and .txt extension
        rel_path = os.path.relpath(file_path, self.wildcards_base_dir)
        name = rel_path.replace('.txt', '')
        
        # Convert path separators to underscores and make uppercase
        name = name.replace(os.sep, '_').upper()
        
        return name

    def _load_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Load usage statistics from JSON file."""
        if not os.path.exists(self.usage_file):
            return {}

        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading usage stats: {e}")
            return {}

    def _save_usage_stats(self):
        """Save usage statistics to JSON file."""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving usage stats: {e}")

    def get_wildcard_names(self) -> List[str]:
        """Get all available wildcard names."""
        return list(self.managers.keys())

    def get_wildcard_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all wildcards."""
        info = {}
        for name, manager in self.managers.items():
            info[name] = {
                'file_path': manager.wildcard_path,
                'item_count': len(manager.items),
                'wildcard_name': name,
                'usage_stats': manager.get_usage_stats()
            }
        return info

    def get_manager(self, wildcard_name: str) -> Optional['WildcardManager']:
        """Get wildcard manager by name."""
        return self.managers.get(wildcard_name)

    def process_prompt(self, prompt: str) -> str:
        """Process a prompt by replacing all wildcards with values."""
        processed_prompt = prompt
        
        # Find all wildcard patterns in the prompt
        wildcard_patterns = re.findall(r'__([A-Z_]+)__', prompt)
        
        for wildcard_name in wildcard_patterns:
            manager = self.managers.get(wildcard_name)
            if manager:
                value = manager.get_next()
                processed_prompt = processed_prompt.replace(f"__{wildcard_name}__", value)
            else:
                print(f"Warning: Wildcard '{wildcard_name}' not found in available wildcards")
        
        return processed_prompt

    def preview_prompt(self, prompt: str, count: int = 5) -> List[str]:
        """Preview multiple versions of a prompt without consuming wildcards."""
        previews = []
        wildcard_patterns = re.findall(r'__([A-Z_]+)__', prompt)
        
        # Get preview values for each wildcard
        wildcard_previews = {}
        for wildcard_name in wildcard_patterns:
            manager = self.managers.get(wildcard_name)
            if manager:
                wildcard_previews[wildcard_name] = manager.get_preview(count)
            else:
                wildcard_previews[wildcard_name] = [f"__{wildcard_name}__"] * count
        
        # Generate preview prompts
        for i in range(count):
            preview_prompt = prompt
            for wildcard_name in wildcard_patterns:
                values = wildcard_previews.get(wildcard_name, [])
                if i < len(values):
                    preview_prompt = preview_prompt.replace(f"__{wildcard_name}__", values[i])
                else:
                    preview_prompt = preview_prompt.replace(f"__{wildcard_name}__", values[0] if values else f"__{wildcard_name}__")
            previews.append(preview_prompt)
        
        return previews

    def get_usage_statistics(self) -> Dict[str, Dict[str, any]]:
        """Get comprehensive usage statistics."""
        stats = {}
        for name, manager in self.managers.items():
            usage_stats = manager.get_usage_stats()
            total_uses = sum(usage_stats.values()) if usage_stats else 0
            
            stats[name] = {
                'total_uses': total_uses,
                'item_count': len(manager.items),
                'usage_stats': usage_stats,
                'least_used_items': manager.get_least_used_items(5),
                'file_path': manager.wildcard_path
            }
        
        return stats

    def reset_all_wildcards(self):
        """Reset all wildcard managers."""
        for manager in self.managers.values():
            manager.reset()

    def reload_wildcards(self):
        """Reload all wildcard files from disk."""
        self.wildcard_files = self._discover_wildcard_files()
        self.managers.clear()
        
        for file_path in self.wildcard_files:
            wildcard_name = self._get_wildcard_name(file_path)
            self.managers[wildcard_name] = WildcardManager(file_path, self.usage_file)

    def validate_prompt(self, prompt: str) -> Dict[str, any]:
        """Validate a prompt against available wildcards."""
        wildcard_patterns = re.findall(r'__([A-Z_]+)__', prompt)
        
        available = []
        missing = []
        
        for wildcard_name in wildcard_patterns:
            if wildcard_name in self.managers:
                available.append(wildcard_name)
            else:
                missing.append(wildcard_name)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'available': available,
            'total_wildcards': len(wildcard_patterns),
            'available_wildcards': self.get_wildcard_names()
        }


class WildcardManager:
    """
    Individual wildcard manager for a single file.
    """

    def __init__(self, wildcard_path: str, usage_file: str = "wildcard_usage.json"):
        self.wildcard_path = wildcard_path
        self.usage_file = usage_file
        self.items = self._load_items()
        self.index = random.randint(0, len(self.items) - 1) if self.items else 0
        self.shuffled = self._shuffle_from_index()
        self.usage_stats = self._load_usage_stats()

    def _load_items(self) -> List[str]:
        """Load wildcard items from file."""
        if not os.path.exists(self.wildcard_path):
            return []

        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(self.wildcard_path, 'r', encoding=encoding) as f:
                        items = [line.strip() for line in f.readlines() if line.strip()]
                    return items
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with errors='ignore'
            with open(self.wildcard_path, 'r', encoding='utf-8', errors='ignore') as f:
                items = [line.strip() for line in f.readlines() if line.strip()]
            return items
            
        except Exception as e:
            print(f"Error loading wildcard file {self.wildcard_path}: {e}")
            return []

    def _shuffle_from_index(self) -> List[str]:
        """Create a shuffled list starting from random index."""
        if not self.items:
            return []

        # Create list starting from random index, wrapping around
        shuffled = self.items[self.index:] + self.items[:self.index]
        return shuffled

    def _load_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Load usage statistics from JSON file."""
        if not os.path.exists(self.usage_file):
            return {}

        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading usage stats: {e}")
            return {}

    def _save_usage_stats(self):
        """Save usage statistics to JSON file."""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_stats, f, indent=2)
        except Exception as e:
            print(f"Error saving usage stats: {e}")

    def _update_usage(self, item: str):
        """Update usage statistics for an item."""
        wildcard_name = os.path.basename(self.wildcard_path).replace('.txt', '')

        if wildcard_name not in self.usage_stats:
            self.usage_stats[wildcard_name] = {}

        if item not in self.usage_stats[wildcard_name]:
            self.usage_stats[wildcard_name][item] = 0

        self.usage_stats[wildcard_name][item] += 1
        self._save_usage_stats()

    def get_next(self) -> str:
        """Get next item in shuffled list, reshuffle if exhausted."""
        if not self.items:
            return ""

        if not self.shuffled:
            self._reshuffle()

        item = self.shuffled.pop(0)
        self._update_usage(item)
        return item

    def _reshuffle(self):
        """Reshuffle the list with a new random starting point."""
        if not self.items:
            self.index = 0
            self.shuffled = []
        else:
            self.index = random.randint(0, len(self.items) - 1)
            self.shuffled = self._shuffle_from_index()

    def reset(self):
        """Force a full reshuffle from new random point."""
        self._reshuffle()

    def get_preview(self, count: int = 5) -> List[str]:
        """Get preview of next N items without consuming them."""
        if not self.items:
            return []

        # Create a temporary copy of current state
        temp_index = self.index
        temp_shuffled = self._shuffle_from_index()

        preview = []
        for i in range(min(count, len(temp_shuffled))):
            preview.append(temp_shuffled[i])

        return preview

    def get_usage_stats(self) -> Dict[str, int]:
        """Get usage statistics for this wildcard."""
        wildcard_name = os.path.basename(self.wildcard_path).replace('.txt', '')
        return self.usage_stats.get(wildcard_name, {})

    def get_usage_percentage(self, item: str) -> float:
        """Get usage percentage for a specific item."""
        stats = self.get_usage_stats()
        if not stats:
            return 0.0

        total_uses = sum(stats.values())
        if total_uses == 0:
            return 0.0

        return (stats.get(item, 0) / total_uses) * 100

    def get_least_used_items(self, count: int = 5) -> List[str]:
        """Get items that have been used the least."""
        stats = self.get_usage_stats()
        if not stats:
            return self.items[:count]

        # Sort by usage count (ascending)
        sorted_items = sorted(stats.items(), key=lambda x: x[1])
        least_used = [item for item, _ in sorted_items[:count]]

        # Add items that haven't been used at all
        unused_items = [item for item in self.items if item not in stats]
        least_used.extend(unused_items[:count - len(least_used)])

        return least_used[:count]

    def reset_usage_stats(self):
        """Reset usage statistics for this wildcard."""
        wildcard_name = os.path.basename(self.wildcard_path).replace('.txt', '')
        if wildcard_name in self.usage_stats:
            del self.usage_stats[wildcard_name]
            self._save_usage_stats()
