import random
import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class WildcardManager:
    """
    Manages wildcard files with smart randomization.
    Starts from a random position and cycles through all items before repeating.
    """
    
    def __init__(self, wildcard_path: str, usage_file: str = "wildcard_usage.json"):
        self.wildcard_path = wildcard_path
        self.usage_file = usage_file
        self.items = self._load_items()
        self.index = random.randint(0, len(self.items) - 1) if self.items else 0
        self.shuffled = self._shuffle_from_index()
        self.usage_stats = self._load_usage_stats()
        
    def _load_items(self) -> List[str]:
        """Load wildcard items from file or list."""
        if isinstance(self.wildcard_path, list):
            return [str(item).strip() for item in self.wildcard_path if str(item).strip()]
        
        if not os.path.exists(self.wildcard_path):
            return []
            
        try:
            with open(self.wildcard_path, 'r', encoding='utf-8') as f:
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


class WildcardManagerFactory:
    """Factory for creating and managing multiple WildcardManager instances."""
    
    def __init__(self, usage_file: str = "wildcard_usage.json"):
        self.usage_file = usage_file
        self.managers: Dict[str, WildcardManager] = {}
    
    def get_manager(self, wildcard_path: str) -> WildcardManager:
        """Get or create a WildcardManager for the given path."""
        if wildcard_path not in self.managers:
            self.managers[wildcard_path] = WildcardManager(wildcard_path, self.usage_file)
        return self.managers[wildcard_path]
    
    def reset_all(self):
        """Reset all managers."""
        for manager in self.managers.values():
            manager.reset()
    
    def get_all_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Get usage statistics for all managers."""
        all_stats = {}
        for manager in self.managers.values():
            wildcard_name = os.path.basename(manager.wildcard_path).replace('.txt', '')
            all_stats[wildcard_name] = manager.get_usage_stats()
        return all_stats 