"""
Unit tests for caching system
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from app.caching import QueryCache, RedisQueryCache

class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    def test_get_cache_key_basic(self):
        """Test basic cache key generation"""
        query = "What is momentum trading?"
        key = get_cache_key(query)
        
        assert key is not None
        assert isinstance(key, str)
        assert len(key) > 0
    
    def test_get_cache_key_deterministic(self):
        """Test that same query generates same key"""
        query = "What is momentum trading?"
        key1 = get_cache_key(query)
        key2 = get_cache_key(query)
        
        assert key1 == key2
    
    def test_get_cache_key_different_queries(self):
        """Test that different queries generate different keys"""
        key1 = get_cache_key("What is momentum trading?")
        key2 = get_cache_key("What is swing trading?")
        
        assert key1 != key2
    
    def test_get_cache_key_with_params(self):
        """Test cache key with additional parameters"""
        query = "What is trading?"
        key1 = get_cache_key(query, mode="rag")
        key2 = get_cache_key(query, mode="web")
        
        # Same query, different mode should have different keys
        assert key1 != key2

@pytest.mark.unit
class TestQueryCache:
    """Test QueryCache class"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        mock = MagicMock()
        mock.get.return_value = None
        mock.setex.return_value = True
        mock.ping.return_value = True
        return mock
    
    def test_init_with_redis_available(self, mock_redis):
        """Test initialization when Redis is available"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache(redis_url="redis://localhost:6379")
            assert cache.enabled is True
            assert cache.redis is not None
    
    def test_init_without_redis(self):
        """Test initialization when Redis is not available"""
        with patch('app.caching.redis.Redis', side_effect=Exception("Connection failed")):
            cache = QueryCache(redis_url="redis://localhost:6379")
            assert cache.enabled is False
            assert cache.redis is None
    
    def test_get_nonexistent_key(self, mock_redis):
        """Test getting non-existent cache key"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            mock_redis.get.return_value = None
            
            result = cache.get("test_key")
            assert result is None
    
    def test_set_and_get(self, mock_redis):
        """Test setting and getting cache value"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            test_data = {"answer": "Test response", "sources": []}
            
            # Mock Redis to return the serialized data
            import json
            mock_redis.get.return_value = json.dumps(test_data).encode()
            
            # Set value
            cache.set("test_key", test_data, ttl=3600)
            
            # Get value
            result = cache.get("test_key")
            
            assert result is not None
            assert result["answer"] == "Test response"
    
    def test_set_with_ttl(self, mock_redis):
        """Test setting cache with custom TTL"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            data = {"test": "value"}
            cache.set("test_key", data, ttl=300)
            
            # Verify setex was called with correct TTL
            assert mock_redis.setex.called
            call_args = mock_redis.setex.call_args
            assert call_args[0][0] == "test_key"
            assert call_args[0][2] == 300  # TTL
    
    def test_cache_disabled_fallback(self):
        """Test that operations work when cache is disabled"""
        with patch('app.caching.redis.Redis', side_effect=Exception("No Redis")):
            cache = QueryCache()
            
            assert cache.enabled is False
            
            # Should not raise errors
            cache.set("key", {"data": "value"})
            result = cache.get("key")
            assert result is None
    
    def test_delete_key(self, mock_redis):
        """Test deleting cache key"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            cache.delete("test_key")
            assert mock_redis.delete.called
    
    def test_clear_pattern(self, mock_redis):
        """Test clearing cache by pattern"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            mock_redis.keys.return_value = [b"query:1", b"query:2", b"query:3"]
            cache.clear_pattern("query:*")
            
            assert mock_redis.keys.called
            assert mock_redis.delete.called
    
    def test_get_stats(self, mock_redis):
        """Test getting cache statistics"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            mock_redis.info.return_value = {
                "used_memory": 1024000,
                "total_keys": 150
            }
            
            stats = cache.get_stats()
            
            assert stats is not None
            if cache.enabled:
                assert "memory" in stats or "keys" in stats

class TestCacheIntegration:
    """Test cache integration scenarios"""
    
    def test_cache_hit_scenario(self, mock_redis):
        """Test successful cache hit"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            # Simulate cache hit
            cached_data = {"answer": "Cached answer", "sources": []}
            import json
            mock_redis.get.return_value = json.dumps(cached_data).encode()
            
            result = cache.get("test_query")
            assert result is not None
            assert result["answer"] == "Cached answer"
    
    def test_cache_miss_scenario(self, mock_redis):
        """Test cache miss"""
        with patch('app.caching.redis.Redis', return_value=mock_redis):
            cache = QueryCache()
            
            mock_redis.get.return_value = None
            result = cache.get("test_query")
            
            assert result is None

