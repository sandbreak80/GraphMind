"""
Unit tests for memory system
"""

import pytest
import json
from pathlib import Path
from app.memory_system import UserMemory

class TestUserMemory:
    """Test UserMemory class"""
    
    def test_init(self, temp_dir):
        """Test UserMemory initialization"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        assert memory.storage_dir == temp_dir
        assert temp_dir.exists()
    
    def test_store_preference(self, temp_dir):
        """Test storing user preference"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        success = memory.store_preference("user123", "model", "qwen2.5:14b")
        assert success is True
        
        # Verify stored
        value = memory.get_preference("user123", "model")
        assert value == "qwen2.5:14b"
    
    def test_get_nonexistent_preference(self, temp_dir):
        """Test getting non-existent preference returns default"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        value = memory.get_preference("user123", "nonexistent", default="default_value")
        assert value == "default_value"
    
    def test_store_insight(self, temp_dir):
        """Test storing user insight"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        insight = "User prefers momentum trading strategies"
        success = memory.store_insight("user123", insight)
        assert success is True
        
        insights = memory.get_insights("user123")
        assert len(insights) > 0
        assert any(insight in i for i in insights)
    
    def test_store_context(self, temp_dir):
        """Test storing conversation context"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        context = {
            "topic": "momentum_trading",
            "indicators": ["RSI", "MACD"],
            "timestamp": "2025-10-30T10:00:00"
        }
        
        success = memory.store_context("user123", "chat123", context)
        assert success is True
        
        retrieved = memory.get_context("user123", "chat123")
        assert retrieved is not None
        assert retrieved["topic"] == "momentum_trading"
        assert "RSI" in retrieved["indicators"]
    
    def test_clear_category(self, temp_dir):
        """Test clearing a specific memory category"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        # Store some data
        memory.store_preference("user123", "model", "llama3.1")
        memory.store_insight("user123", "Test insight")
        
        # Clear preferences
        success = memory.clear_category("user123", "preferences")
        assert success is True
        
        # Preferences should be cleared
        value = memory.get_preference("user123", "model")
        assert value is None
        
        # Insights should still exist
        insights = memory.get_insights("user123")
        assert len(insights) > 0
    
    def test_get_memory_stats(self, temp_dir):
        """Test getting memory statistics"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        # Store various types of data
        memory.store_preference("user123", "model", "qwen2.5:14b")
        memory.store_preference("user123", "temperature", "0.1")
        memory.store_insight("user123", "Insight 1")
        memory.store_insight("user123", "Insight 2")
        
        stats = memory.get_memory_stats("user123")
        
        assert stats is not None
        assert stats["preferences"] >= 2
        assert stats["insights"] >= 2
    
    def test_persistence_across_instances(self, temp_dir):
        """Test that memory persists across different instances"""
        # First instance
        memory1 = UserMemory(storage_dir=str(temp_dir))
        memory1.store_preference("user123", "model", "qwen2.5:14b")
        
        # Second instance (simulates restart)
        memory2 = UserMemory(storage_dir=str(temp_dir))
        value = memory2.get_preference("user123", "model")
        
        assert value == "qwen2.5:14b"
    
    def test_multiple_users(self, temp_dir):
        """Test memory isolation between users"""
        memory = UserMemory(storage_dir=str(temp_dir))
        
        memory.store_preference("user1", "model", "llama3.1")
        memory.store_preference("user2", "model", "qwen2.5:14b")
        
        user1_model = memory.get_preference("user1", "model")
        user2_model = memory.get_preference("user2", "model")
        
        assert user1_model == "llama3.1"
        assert user2_model == "qwen2.5:14b"
        assert user1_model != user2_model

