#!/usr/bin/env python3
"""
Cache Manager

Provides intelligent caching for frequently accessed data to improve performance.
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, Union
from pathlib import Path
import threading


class CacheManager:
    """Intelligent caching system with TTL and file-based persistence."""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def _get_cache_key(self, key: Union[str, Dict]) -> str:
        """Generate a cache key from string or dict."""
        if isinstance(key, dict):
            key_str = json.dumps(key, sort_keys=True)
        else:
            key_str = str(key)
        
        # Create hash for consistent key length
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > cache_entry.get('expires_at', 0)
    
    def get(self, key: Union[str, Dict], default: Any = None) -> Any:
        """Get value from cache."""
        with self._lock:
            cache_key = self._get_cache_key(key)
            
            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not self._is_expired(entry):
                    entry['access_count'] = entry.get('access_count', 0) + 1
                    entry['last_accessed'] = time.time()
                    return entry['value']
                else:
                    # Remove expired entry
                    del self.memory_cache[cache_key]
            
            # Check file cache
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        entry = json.load(f)
                    
                    if not self._is_expired(entry):
                        # Move to memory cache for faster access
                        entry['access_count'] = entry.get('access_count', 0) + 1
                        entry['last_accessed'] = time.time()
                        self.memory_cache[cache_key] = entry
                        return entry['value']
                    else:
                        # Remove expired file
                        cache_file.unlink()
                except Exception:
                    pass
            
            return default
    
    def set(self, key: Union[str, Dict], value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self._lock:
            cache_key = self._get_cache_key(key)
            ttl = ttl or self.default_ttl
            
            entry = {
                'value': value,
                'created_at': time.time(),
                'expires_at': time.time() + ttl,
                'access_count': 0,
                'last_accessed': time.time()
            }
            
            # Store in memory cache
            self.memory_cache[cache_key] = entry
            
            # Store in file cache for persistence
            cache_file = self.cache_dir / f"{cache_key}.json"
            try:
                with open(cache_file, 'w') as f:
                    json.dump(entry, f)
            except Exception:
                pass  # Ignore file write errors
    
    def delete(self, key: Union[str, Dict]) -> bool:
        """Delete value from cache."""
        with self._lock:
            cache_key = self._get_cache_key(key)
            
            # Remove from memory cache
            memory_deleted = cache_key in self.memory_cache
            if memory_deleted:
                del self.memory_cache[cache_key]
            
            # Remove from file cache
            cache_file = self.cache_dir / f"{cache_key}.json"
            file_deleted = cache_file.exists()
            if file_deleted:
                cache_file.unlink()
            
            return memory_deleted or file_deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.memory_cache.clear()
            
            # Clear file cache
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception:
                    pass
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from cache."""
        with self._lock:
            expired_count = 0
            
            # Clean memory cache
            expired_keys = [
                key for key, entry in self.memory_cache.items()
                if self._is_expired(entry)
            ]
            for key in expired_keys:
                del self.memory_cache[key]
                expired_count += 1
            
            # Clean file cache
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        entry = json.load(f)
                    
                    if self._is_expired(entry):
                        cache_file.unlink()
                        expired_count += 1
                except Exception:
                    # If we can't read the file, assume it's corrupted and delete it
                    cache_file.unlink()
                    expired_count += 1
            
            return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_entries = len(self.memory_cache)
            expired_entries = sum(1 for entry in self.memory_cache.values() if self._is_expired(entry))
            
            file_count = len(list(self.cache_dir.glob("*.json")))
            
            return {
                'memory_entries': total_entries,
                'expired_memory_entries': expired_entries,
                'file_entries': file_count,
                'cache_dir': str(self.cache_dir)
            }


# Global cache instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def cache_result(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Create cache key from function name and arguments
            cache_key = {
                'func': func.__name__,
                'prefix': key_prefix,
                'args': args,
                'kwargs': kwargs
            }
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
