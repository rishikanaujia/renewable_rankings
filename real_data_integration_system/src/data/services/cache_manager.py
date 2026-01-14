"""Cache manager for data integration system."""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

from src.core.logger import get_logger

from ..base import (
    CacheStrategy, DataResponse, TimeSeries,
    CacheError, CACHE_TTL_SECONDS, DataFrequency
)

logger = get_logger(__name__)


class CacheManager:
    """Manages caching for data requests."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cache manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Cache strategy
        strategy_str = self.config.get('strategy', 'memory')
        self.strategy = CacheStrategy(strategy_str)
        
        # Cache directory for disk cache
        self.cache_dir = Path(self.config.get('cache_dir', './data/cache'))
        if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._memory_cache: Dict[str, tuple[DataResponse, datetime]] = {}
        
        # Cache settings
        self.enabled = self.config.get('enabled', True)
        self.max_size = self.config.get('max_size_mb', 100)
        self.default_ttl = self.config.get('default_ttl_seconds', 86400)  # 1 day
        
        logger.info(f"Cache manager initialized with {self.strategy.value} strategy")
    
    def get(
        self, 
        country: str, 
        indicator: str, 
        source: str = "any"
    ) -> Optional[DataResponse]:
        """Get cached data.
        
        Args:
            country: Country name
            indicator: Indicator name
            source: Data source name
            
        Returns:
            Cached DataResponse or None
        """
        if not self.enabled:
            return None
        
        cache_key = self._generate_key(country, indicator, source)
        
        try:
            if self.strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
                # Check memory cache
                result = self._get_from_memory(cache_key)
                if result:
                    logger.debug(f"Cache HIT (memory): {cache_key}")
                    return result
            
            if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
                # Check disk cache
                result = self._get_from_disk(cache_key)
                if result:
                    logger.debug(f"Cache HIT (disk): {cache_key}")
                    # Store in memory for faster future access
                    if self.strategy == CacheStrategy.HYBRID:
                        self._store_in_memory(cache_key, result)
                    return result
            
            logger.debug(f"Cache MISS: {cache_key}")
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    def set(
        self, 
        response: DataResponse,
        ttl: Optional[int] = None,
        frequency: Optional[DataFrequency] = None
    ):
        """Store data in cache.
        
        Args:
            response: Data response to cache
            ttl: Time to live in seconds
            frequency: Data frequency for auto TTL
        """
        if not self.enabled or not response.success:
            return
        
        # Determine TTL
        if ttl is None:
            if frequency:
                ttl = CACHE_TTL_SECONDS.get(frequency, self.default_ttl)
            else:
                ttl = self.default_ttl
        
        cache_key = self._generate_key(
            response.data.country if response.data else "",
            response.data.indicator if response.data else "",
            response.source
        )
        
        try:
            # Mark as cached
            response.cached = True
            
            if self.strategy in [CacheStrategy.MEMORY, CacheStrategy.HYBRID]:
                self._store_in_memory(cache_key, response, ttl)
            
            if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
                self._store_on_disk(cache_key, response, ttl)
            
            logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")
            
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
    
    def clear(self):
        """Clear all caches."""
        # Clear memory
        self._memory_cache.clear()
        
        # Clear disk
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Error deleting cache file: {e}")
        
        logger.info("Cache cleared")
    
    def _generate_key(self, country: str, indicator: str, source: str) -> str:
        """Generate cache key."""
        raw_key = f"{country}|{indicator}|{source}"
        return hashlib.md5(raw_key.encode()).hexdigest()
    
    def _get_from_memory(self, key: str) -> Optional[DataResponse]:
        """Get from memory cache."""
        if key not in self._memory_cache:
            return None
        
        response, expires_at = self._memory_cache[key]
        
        # Check if expired
        if datetime.now() > expires_at:
            del self._memory_cache[key]
            return None
        
        return response
    
    def _store_in_memory(
        self, 
        key: str, 
        response: DataResponse, 
        ttl: int = None
    ):
        """Store in memory cache."""
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self._memory_cache[key] = (response, expires_at)
    
    def _get_from_disk(self, key: str) -> Optional[DataResponse]:
        """Get from disk cache."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check expiration
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                cache_file.unlink()
                return None
            
            # Reconstruct response
            ts_data = data['response']['data']
            if ts_data:
                time_series = TimeSeries(
                    country=ts_data['country'],
                    indicator=ts_data['indicator'],
                    source=ts_data.get('source', '')
                )
                # Add data points (simplified - could be enhanced)
                
                response = DataResponse(
                    data=time_series,
                    success=data['response']['success'],
                    source=data['response']['source'],
                    cached=True
                )
            else:
                response = DataResponse(
                    data=None,
                    success=data['response']['success'],
                    error=data['response'].get('error'),
                    source=data['response']['source'],
                    cached=True
                )
            
            return response
            
        except Exception as e:
            logger.warning(f"Error reading cache file: {e}")
            return None
    
    def _store_on_disk(
        self, 
        key: str, 
        response: DataResponse, 
        ttl: int = None
    ):
        """Store on disk cache."""
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            # Serialize response (simplified)
            data = {
                'key': key,
                'expires_at': expires_at.isoformat(),
                'response': {
                    'success': response.success,
                    'source': response.source,
                    'error': response.error,
                    'data': response.data.to_dict() if response.data else None
                }
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.warning(f"Error writing cache file: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'enabled': self.enabled,
            'strategy': self.strategy.value,
            'memory_entries': len(self._memory_cache),
        }
        
        if self.strategy in [CacheStrategy.DISK, CacheStrategy.HYBRID]:
            disk_files = list(self.cache_dir.glob('*.json'))
            stats['disk_entries'] = len(disk_files)
            stats['disk_size_mb'] = sum(f.stat().st_size for f in disk_files) / (1024 * 1024)
        
        return stats
