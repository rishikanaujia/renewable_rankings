"""Extraction Cache - Cache management for AI extraction results.

This module provides caching functionality to avoid redundant LLM calls
and reduce costs.

Features:
    - In-memory caching with TTL
    - Persistent storage (Redis, file-based)
    - Cache invalidation
    - Statistics tracking
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class ExtractionCache:
    """Cache for storing extraction results.
    
    Supports both in-memory and persistent storage.
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        default_ttl: int = 86400  # 24 hours
    ):
        """Initialize cache.
        
        Args:
            cache_dir: Optional directory for persistent cache
            default_ttl: Default time-to-live in seconds
        """
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Create cache directory if needed
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        
        logger.info(f"Initialized ExtractionCache (TTL: {default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                del self._memory_cache[key]
                self.misses += 1
                return None
            
            self.hits += 1
            return entry['value']
        
        # Check persistent cache
        if self.cache_dir:
            cached = self._load_from_disk(key)
            if cached and not self._is_expired(cached):
                # Promote to memory cache
                self._memory_cache[key] = cached
                self.hits += 1
                return cached['value']
        
        self.misses += 1
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live in seconds
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        entry = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        
        # Store in memory
        self._memory_cache[key] = entry
        
        # Store on disk if enabled
        if self.cache_dir:
            self._save_to_disk(key, entry)
        
        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        # Remove from memory
        if key in self._memory_cache:
            del self._memory_cache[key]
        
        # Remove from disk
        if self.cache_dir:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
        
        logger.debug(f"Deleted key: {key}")
    
    def clear(self):
        """Clear all cache entries."""
        self._memory_cache.clear()
        
        if self.cache_dir:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        
        logger.info("Cleared all cache entries")
    
    def cleanup_expired(self):
        """Remove expired entries from cache."""
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if self._is_expired(entry)
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'memory_entries': len(self._memory_cache)
        }
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired.
        
        Args:
            entry: Cache entry dictionary
            
        Returns:
            True if expired, False otherwise
        """
        expires_at = entry.get('expires_at')
        if not expires_at:
            return True
        
        return datetime.now() > expires_at
    
    def _save_to_disk(self, key: str, entry: Dict[str, Any]):
        """Save entry to disk.
        
        Args:
            key: Cache key
            entry: Entry to save
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            # Convert datetime objects for JSON serialization
            serializable_entry = {
                'value': entry['value'].__dict__ if hasattr(entry['value'], '__dict__') else entry['value'],
                'expires_at': entry['expires_at'].isoformat(),
                'created_at': entry['created_at'].isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(serializable_entry, f)
        
        except Exception as e:
            logger.error(f"Error saving cache to disk: {e}")
    
    def _load_from_disk(self, key: str) -> Optional[Dict[str, Any]]:
        """Load entry from disk.
        
        Args:
            key: Cache key
            
        Returns:
            Cache entry or None if not found
        """
        try:
            cache_file = self.cache_dir / f"{key}.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Convert ISO format strings back to datetime
            return {
                'value': data['value'],
                'expires_at': datetime.fromisoformat(data['expires_at']),
                'created_at': datetime.fromisoformat(data['created_at'])
            }
        
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")
            return None
