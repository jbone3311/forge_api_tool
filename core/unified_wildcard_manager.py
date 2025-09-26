#!/usr/bin/env python3
"""
Unified Wildcard Manager

A streamlined wildcard management system that can work with individual files
or automatically discover and manage all wildcard files in a directory structure.
"""

import random
import json
import os
import re
from typing import List, Dict, Optional, Any
from pathlib import Path


class UnifiedWildcardManager:
    """
    Unified wildcard manager that can work with individual files or automatically
    discover and manage all wildcard files in a directory structure.
    """

    def __init__(self, wildcards_base_dir: str = "wildcards", usage_file: str = "wildcard_usage.json", 
                 auto_discover: bool = True, single_file: Optional[str] = None):
        """
        Initialize the unified wildcard manager.
        
        Args:
            wildcards_base_dir: Base directory for wildcard files (when auto_discover=True)
            usage_file: File to store usage statistics
            auto_discover: Whether to automatically discover all wildcard files
            single_file: Specific wildcard file to manage (when auto_discover=False)
        """
        self.wildcards_base_dir = wildcards_base_dir
        self.usage_file = usage_file
        self.auto_discover = auto_discover
        
        if auto_discover:
            self.wildcard_files = self._discover_wildcard_files()
            self.managers: Dict[str, '_WildcardFileManager'] = {}
            self._initialize_managers()
        else:
            if single_file is None:
                raise ValueError("single_file must be provided when auto_discover=False")
            self.single_manager = _WildcardFileManager(single_file, usage_file)
        
        self.usage_stats = self._load_usage_stats()

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

    def _initialize_managers(self):
        """Initialize managers for all discovered files."""
        for file_path in self.wildcard_files:
            wildcard_name = self._get_wildcard_name(file_path)
            self.managers[wildcard_name] = _WildcardFileManager(file_path, self.usage_file)

    def get_wildcard_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available wildcards."""
        info = {}
        
        if self.auto_discover:
            for name, manager in self.managers.items():
                info[name] = {
                    'file_path': manager.file_path,
                    'item_count': len(manager.items),
                    'usage_count': manager.usage_stats.get('total_usage', 0),
                    'last_used': manager.usage_stats.get('last_used'),
                    'items': manager.items[:10]  # First 10 items as preview
                }
        else:
            info[self.single_manager.wildcard_name] = {
                'file_path': self.single_manager.file_path,
                'item_count': len(self.single_manager.items),
                'usage_count': self.single_manager.usage_stats.get('total_usage', 0),
                'last_used': self.single_manager.usage_stats.get('last_used'),
                'items': self.single_manager.items[:10]
            }
        
        return info

    def process_prompt(self, prompt: str) -> str:
        """Process a prompt by substituting all wildcards."""
        if self.auto_discover:
            return self._process_prompt_auto(prompt)
        else:
            return self._process_prompt_single(prompt)

    def _process_prompt_auto(self, prompt: str) -> str:
        """Process prompt with auto-discovered wildcards."""
        result = prompt
        
        # Find all wildcard patterns
        wildcard_pattern = r'__(\w+)__'
        matches = re.findall(wildcard_pattern, result)
        
        for wildcard_name in matches:
            if wildcard_name in self.managers:
                value = self.managers[wildcard_name].get_next()
                result = result.replace(f'__{wildcard_name}__', value, 1)
        
        return result

    def _process_prompt_single(self, prompt: str) -> str:
        """Process prompt with single wildcard manager."""
        return self.single_manager.process_prompt(prompt)

    def preview_prompt(self, prompt: str, count: int = 5) -> List[str]:
        """Preview prompts without consuming wildcards."""
        if self.auto_discover:
            return self._preview_prompt_auto(prompt, count)
        else:
            return self._preview_prompt_single(prompt, count)

    def _preview_prompt_auto(self, prompt: str, count: int) -> List[str]:
        """Preview prompt with auto-discovered wildcards."""
        # Find all wildcard patterns
        wildcard_pattern = r'__(\w+)__'
        wildcard_names = re.findall(wildcard_pattern, prompt)
        
        # Get preview values for each wildcard
        wildcard_previews = {}
        for wildcard_name in wildcard_names:
            if wildcard_name in self.managers:
                wildcard_previews[wildcard_name] = self.managers[wildcard_name].get_preview(count)
        
        # Generate preview prompts
        preview_prompts = []
        for i in range(count):
            result = prompt
            for wildcard_name in wildcard_names:
                values = wildcard_previews.get(wildcard_name, [])
                if i < len(values):
                    result = result.replace(f'__{wildcard_name}__', values[i], 1)
            preview_prompts.append(result)
        
        return preview_prompts

    def _preview_prompt_single(self, prompt: str, count: int) -> List[str]:
        """Preview prompt with single wildcard manager."""
        return self.single_manager.preview_prompt(prompt, count)

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt against available wildcards."""
        wildcard_pattern = r'__(\w+)__'
        wildcards = re.findall(wildcard_pattern, prompt)
        
        valid_wildcards = []
        invalid_wildcards = []
        
        available_names = self.get_wildcard_names()
        
        for wildcard in wildcards:
            if wildcard in available_names:
                valid_wildcards.append(wildcard)
            else:
                invalid_wildcards.append(wildcard)
        
        return {
            'valid_wildcards': valid_wildcards,
            'invalid_wildcards': invalid_wildcards,
            'total_wildcards': len(wildcards),
            'validation_passed': len(invalid_wildcards) == 0
        }

    def get_wildcard_names(self) -> List[str]:
        """Get list of all available wildcard names."""
        if self.auto_discover:
            return list(self.managers.keys())
        else:
            return [self.single_manager.wildcard_name]

    def get_usage_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive usage statistics."""
        if self.auto_discover:
            stats = {}
            for name, manager in self.managers.items():
                stats[name] = manager.usage_stats.copy()
                stats[name]['item_count'] = len(manager.items)
            return stats
        else:
            stats = self.single_manager.usage_stats.copy()
            stats['item_count'] = len(self.single_manager.items)
            return {self.single_manager.wildcard_name: stats}

    def reset_all_wildcards(self):
        """Reset all wildcard managers."""
        if self.auto_discover:
            for manager in self.managers.values():
                manager.reset()
        else:
            self.single_manager.reset()

    def reload_wildcards(self):
        """Reload all wildcard files from disk."""
        if self.auto_discover:
            self.wildcard_files = self._discover_wildcard_files()
            self.managers.clear()
            self._initialize_managers()
        else:
            self.single_manager.reload()

    def _load_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Load usage statistics from JSON file."""
        if not os.path.exists(self.usage_file):
            return {}
        
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}


class _WildcardFileManager:
    """
    Internal class for managing individual wildcard files.
    """

    def __init__(self, file_path: str, usage_file: str):
        self.file_path = file_path
        self.usage_file = usage_file
        self.wildcard_name = os.path.splitext(os.path.basename(file_path))[0]
        self.items = self._load_items()
        self.index = random.randint(0, len(self.items) - 1) if self.items else 0
        self.shuffled = self._shuffle_from_index()
        self.usage_stats = self._load_usage_stats()

    def _load_items(self) -> List[str]:
        """Load wildcard items from file."""
        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                items = [line.strip() for line in f.readlines() if line.strip()]
            return items
        except Exception as e:
            print(f"Error loading wildcard file {self.file_path}: {e}")
            return []

    def _shuffle_from_index(self) -> List[str]:
        """Create a shuffled list starting from random index."""
        if not self.items:
            return []
        
        # Create list starting from random index, wrapping around
        shuffled = self.items[self.index:] + self.items[:self.index]
        return shuffled

    def _load_usage_stats(self) -> Dict[str, Any]:
        """Load usage statistics from JSON file."""
        if not os.path.exists(self.usage_file):
            return {'total_usage': 0, 'last_used': None}
        
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            return stats.get(self.wildcard_name, {'total_usage': 0, 'last_used': None})
        except Exception:
            return {'total_usage': 0, 'last_used': None}

    def _save_usage_stats(self):
        """Save usage statistics to JSON file."""
        try:
            # Load existing stats
            all_stats = {}
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            
            # Update stats for this wildcard
            all_stats[self.wildcard_name] = self.usage_stats
            
            # Save back to file
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving usage stats: {e}")

    def get_next(self) -> str:
        """Get the next wildcard value."""
        if not self.items:
            return ""
        
        # Get next item from shuffled list
        if not self.shuffled:
            self.shuffled = self._shuffle_from_index()
        
        value = self.shuffled.pop(0)
        
        # Update usage stats
        self.usage_stats['total_usage'] += 1
        self.usage_stats['last_used'] = value
        
        # Save stats periodically
        if self.usage_stats['total_usage'] % 10 == 0:
            self._save_usage_stats()
        
        return value

    def get_preview(self, count: int = 5) -> List[str]:
        """Get preview values without consuming them."""
        if not self.items:
            return []
        
        # Return random sample for preview
        return random.sample(self.items, min(count, len(self.items)))

    def process_prompt(self, prompt: str) -> str:
        """Process a prompt by substituting wildcards."""
        result = prompt
        wildcard_pattern = r'__(\w+)__'
        
        while re.search(wildcard_pattern, result):
            match = re.search(wildcard_pattern, result)
            if match:
                wildcard_name = match.group(1)
                if wildcard_name.lower() == self.wildcard_name.lower():
                    value = self.get_next()
                    result = result.replace(f'__{wildcard_name}__', value, 1)
                else:
                    break
        
        return result

    def preview_prompt(self, prompt: str, count: int) -> List[str]:
        """Preview prompts without consuming wildcards."""
        wildcard_pattern = r'__(\w+)__'
        
        if not re.search(wildcard_pattern, prompt):
            return [prompt] * count
        
        preview_prompts = []
        for _ in range(count):
            result = prompt
            match = re.search(wildcard_pattern, result)
            if match:
                wildcard_name = match.group(1)
                if wildcard_name.lower() == self.wildcard_name.lower():
                    value = random.choice(self.items)
                    result = result.replace(f'__{wildcard_name}__', value, 1)
            preview_prompts.append(result)
        
        return preview_prompts

    def reset(self):
        """Reset the wildcard manager."""
        self.index = random.randint(0, len(self.items) - 1) if self.items else 0
        self.shuffled = self._shuffle_from_index()

    def reload(self):
        """Reload wildcard items from file."""
        self.items = self._load_items()
        self.reset()