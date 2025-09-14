import hashlib
import inspect
from functools import wraps
from django.core.cache import cache
from asgiref.sync import sync_to_async

cache_timeout_seconds = 300 # this can be propagated using ENV variable

def _make_cache_key(func, args, kwargs):
    """
    Build a stable cache key from function name + args + kwargs.
    """
    key_raw = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
    return hashlib.md5(key_raw.encode()).hexdigest()

def cache_result(timeout=cache_timeout_seconds):
    """
    Decorator for sync functions using Django's cache.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_cache_key(func, args, kwargs)
            value = cache.get(key)
            if value is not None:
                return value
            value = func(*args, **kwargs)
            cache.set(key, value, timeout=timeout)
            return value
        return wrapper
    return decorator

def async_cache_result(timeout=cache_timeout_seconds):
    """
    Decorator for async functions using Django's cache.
    Cache calls are wrapped with sync_to_async since Django cache is sync.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = _make_cache_key(func, args, kwargs)
            cached = await sync_to_async(cache.get)(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            await sync_to_async(cache.set)(key, result, timeout=timeout)
            return result
        return wrapper
    return decorator

def cached(timeout=cache_timeout_seconds):
    """
    Auto-detect sync vs async function and apply correct caching.
    Since the server definitions don't change frequently, the cache can be maintained in a database too for certain keys.
    """
    def decorator(func):
        if inspect.iscoroutinefunction(func):
            return async_cache_result(timeout)(func)
        else:
            return cache_result(timeout)(func)
    return decorator
