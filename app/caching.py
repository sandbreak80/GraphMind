"""Advanced query caching with Redis and TTL."""
import hashlib
import json
import time
import os
from functools import lru_cache
from typing import Optional, Dict, Any
import redis
import aioredis

class QueryCache:
    """Simple query caching with TTL."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _get_cache_key(self, query: str, model: str, **kwargs) -> str:
        """Generate cache key from query and parameters."""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Create hash of query + model + relevant parameters
        cache_data = {
            'query': normalized_query,
            'model': model,
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        cache_key = self._get_cache_key(query, model, **kwargs)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # Check TTL
            if time.time() - cached_data['timestamp'] < self.ttl_seconds:
                self.hits += 1
                return cached_data['response']
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        
        self.misses += 1
        return None
    
    def set(self, query: str, model: str, response: Dict[str, Any], **kwargs):
        """Cache response."""
        cache_key = self._get_cache_key(query, model, **kwargs)
        
        # Simple LRU: remove oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / max(1, total_requests)
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }


class RedisQueryCache:
    """Redis-based query caching with TTL and async support."""
    
    def __init__(self, redis_url: str = None, ttl_seconds: int = 3600):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
        self.redis_client = None
        self.async_redis_client = None
        
    def _get_cache_key(self, query: str, model: str, **kwargs) -> str:
        """Generate cache key from query and parameters."""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Create hash of query + model + relevant parameters
        cache_data = {
            'query': normalized_query,
            'model': model,
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 2000),
            'mode': kwargs.get('mode', 'qa')
        }
        
        # Create deterministic hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"query_cache:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_redis_client(self):
        """Get or create Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        return self.redis_client
    
    async def _get_async_redis_client(self):
        """Get or create async Redis client."""
        if self.async_redis_client is None:
            self.async_redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
        return self.async_redis_client
    
    def get(self, query: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            redis_client = self._get_redis_client()
            cache_key = self._get_cache_key(query, model, **kwargs)
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                self.hits += 1
                return json.loads(cached_data)
            else:
                self.misses += 1
                return None
                
        except Exception as e:
            print(f"Redis cache get error: {e}")
            self.misses += 1
            return None
    
    async def get_async(self, query: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response asynchronously."""
        try:
            redis_client = await self._get_async_redis_client()
            cache_key = self._get_cache_key(query, model, **kwargs)
            cached_data = await redis_client.get(cache_key)
            
            if cached_data:
                self.hits += 1
                return json.loads(cached_data)
            else:
                self.misses += 1
                return None
                
        except Exception as e:
            print(f"Redis cache get_async error: {e}")
            self.misses += 1
            return None
    
    def set(self, query: str, model: str, response: Dict[str, Any], **kwargs) -> bool:
        """Cache response."""
        try:
            redis_client = self._get_redis_client()
            cache_key = self._get_cache_key(query, model, **kwargs)
            
            # Add metadata
            cache_data = {
                'response': response,
                'cached_at': time.time(),
                'query': query,
                'model': model
            }
            
            redis_client.setex(cache_key, self.ttl_seconds, json.dumps(cache_data))
            return True
            
        except Exception as e:
            print(f"Redis cache set error: {e}")
            return False
    
    async def set_async(self, query: str, model: str, response: Dict[str, Any], **kwargs) -> bool:
        """Cache response asynchronously."""
        try:
            redis_client = await self._get_async_redis_client()
            cache_key = self._get_cache_key(query, model, **kwargs)
            
            # Add metadata
            cache_data = {
                'response': response,
                'cached_at': time.time(),
                'query': query,
                'model': model
            }
            
            await redis_client.setex(cache_key, self.ttl_seconds, json.dumps(cache_data))
            return True
            
        except Exception as e:
            print(f"Redis cache set_async error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cached queries."""
        try:
            redis_client = self._get_redis_client()
            keys = redis_client.keys("query_cache:*")
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis cache clear error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            redis_client = self._get_redis_client()
            keys = redis_client.keys("query_cache:*")
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0.0,
                'cached_queries': len(keys),
                'redis_connected': True
            }
        except Exception as e:
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0.0,
                'cached_queries': 0,
                'redis_connected': False,
                'error': str(e)
            }


# Global instances
query_cache = QueryCache()
redis_query_cache = RedisQueryCache()