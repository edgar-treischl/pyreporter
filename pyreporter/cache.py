"""
Cache management for pyreporter pipeline.

Provides caching for raw LimeSurvey responses and prepared plot data
to speed up development and avoid repeated API calls.
"""

import pickle
from pathlib import Path
from typing import Any, Optional
import hashlib
import json


class CacheManager:
    """Manages caching for pipeline data."""
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize cache manager.
        
        Parameters
        ----------
        cache_dir : str
            Directory to store cache files (relative to project root)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _make_key(self, **params) -> str:
        """
        Generate a cache key from parameters.
        
        Parameters
        ----------
        **params
            Parameters to hash
            
        Returns
        -------
        str
            Hash-based cache key
        """
        # Sort params for consistent hashing
        sorted_params = json.dumps(params, sort_keys=True)
        hash_obj = hashlib.sha256(sorted_params.encode())
        return hash_obj.hexdigest()[:16]
    
    def get_path(self, prefix: str, **params) -> Path:
        """
        Get cache file path for given parameters.
        
        Parameters
        ----------
        prefix : str
            Cache type prefix (e.g., 'raw', 'prepared')
        **params
            Parameters to identify the cache
            
        Returns
        -------
        Path
            Path to cache file
        """
        key = self._make_key(**params)
        return self.cache_dir / f"{prefix}_{key}.pkl"
    
    def exists(self, prefix: str, **params) -> bool:
        """
        Check if cache exists for given parameters.
        
        Parameters
        ----------
        prefix : str
            Cache type prefix
        **params
            Parameters to identify the cache
            
        Returns
        -------
        bool
            True if cache exists
        """
        return self.get_path(prefix, **params).exists()
    
    def save(self, data: Any, prefix: str, **params) -> Path:
        """
        Save data to cache.
        
        Parameters
        ----------
        data : Any
            Data to cache (must be picklable)
        prefix : str
            Cache type prefix
        **params
            Parameters to identify the cache
            
        Returns
        -------
        Path
            Path where data was saved
        """
        cache_path = self.get_path(prefix, **params)
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"💾 Cached {prefix} data: {cache_path.name}")
        return cache_path
    
    def load(self, prefix: str, **params) -> Optional[Any]:
        """
        Load data from cache.
        
        Parameters
        ----------
        prefix : str
            Cache type prefix
        **params
            Parameters to identify the cache
            
        Returns
        -------
        Any or None
            Cached data if exists, None otherwise
        """
        cache_path = self.get_path(prefix, **params)
        if not cache_path.exists():
            return None
        
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        print(f"♻️  Loaded {prefix} from cache: {cache_path.name}")
        return data
    
    def clear(self, prefix: Optional[str] = None) -> int:
        """
        Clear cache files.
        
        Parameters
        ----------
        prefix : str, optional
            If provided, only clear files with this prefix.
            If None, clear all cache files.
            
        Returns
        -------
        int
            Number of files deleted
        """
        count = 0
        pattern = f"{prefix}_*.pkl" if prefix else "*.pkl"
        for cache_file in self.cache_dir.glob(pattern):
            cache_file.unlink()
            count += 1
        
        if count > 0:
            print(f"🗑️  Cleared {count} cache file(s)")
        return count


# Global cache instance
_cache = CacheManager()


def get_cache() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache
