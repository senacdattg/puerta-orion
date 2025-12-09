"""
Simple in-memory cache utility for static catalog data.

This module provides a lightweight caching mechanism for frequently accessed
but rarely changed data like catalogs (categories, event types, etc.).

Following functional programming principles: pure functions with no side effects
on input parameters.
"""

from typing import Any, Callable, Dict, Optional
from datetime import datetime, timedelta
import threading

# Thread-safe cache storage
_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.Lock()


def get_cached(key: str, max_age_seconds: int = 3600) -> Optional[Any]:
    """
    Retrieve a value from cache if it exists and hasn't expired.
    
    Args:
        key: Cache key identifier
        max_age_seconds: Maximum age of cached data in seconds (default: 1 hour)
        
    Returns:
        Cached value if found and valid, None otherwise
    """
    with _cache_lock:
        if key not in _cache:
            return None
        
        entry = _cache[key]
        age = datetime.now() - entry['timestamp']
        
        if age > timedelta(seconds=max_age_seconds):
            del _cache[key]
            return None
        
        return entry['value']


def set_cached(key: str, value: Any) -> None:
    """
    Store a value in cache with current timestamp.
    
    Args:
        key: Cache key identifier
        value: Value to cache
    """
    with _cache_lock:
        _cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }


def clear_cache(key: Optional[str] = None) -> None:
    """
    Clear cache entry or entire cache.
    
    Args:
        key: Specific cache key to clear, or None to clear all cache
    """
    with _cache_lock:
        if key is None:
            _cache.clear()
        elif key in _cache:
            del _cache[key]


def get_or_set(key: str, fetch_fn: Callable[[], Any], max_age_seconds: int = 3600) -> Any:
    """
    Get value from cache or fetch and cache it if not found.
    
    This is a convenience function that combines get_cached and set_cached.
    
    Args:
        key: Cache key identifier
        fetch_fn: Function to call if cache miss (must be callable with no args)
        max_age_seconds: Maximum age of cached data in seconds
        
    Returns:
        Cached or freshly fetched value
    """
    cached_value = get_cached(key, max_age_seconds)
    if cached_value is not None:
        return cached_value
    
    value = fetch_fn()
    set_cached(key, value)
    return value

