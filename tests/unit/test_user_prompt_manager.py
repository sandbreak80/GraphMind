"""
Unit tests for user prompt manager
"""

import pytest
import json
from pathlib import Path
from app.user_prompt_manager import UserPromptManager

class TestUserPromptManager:
    """Test UserPromptManager class"""
    
    def test_init(self, temp_dir):
        """Test UserPromptManager initialization"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        assert manager.storage_dir == temp_dir
        assert temp_dir.exists()
    
    def test_get_user_file_creates_directory(self, temp_dir):
        """Test that user directory is created"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        user_file = manager._get_user_file("testuser")
        assert user_file.parent.exists()
        assert user_file.parent.name == "testuser"
    
    def test_set_user_prompt(self, temp_dir):
        """Test setting a user prompt"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = "You are a helpful assistant. Your role is to help users. Guidelines: Be clear and concise. Response format: Markdown."
        success = manager.set_user_prompt("user123", "rag_only", prompt)
        
        assert success is True
        
        # Verify file was created
        user_file = manager._get_user_file("user123")
        assert user_file.exists()
    
    def test_get_user_prompt_returns_string(self, temp_dir):
        """Test that get_user_prompt returns just the prompt string"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = "You are a helpful assistant. Your role is to help users. Guidelines: Be clear. Response format: Markdown."
        manager.set_user_prompt("user123", "rag_only", prompt)
        
        retrieved = manager.get_user_prompt("user123", "rag_only")
        
        assert isinstance(retrieved, str)
        assert retrieved == prompt
        assert "updated_at" not in retrieved  # Should not return metadata
        assert "hash" not in retrieved
    
    def test_get_nonexistent_prompt(self, temp_dir):
        """Test getting prompt that doesn't exist"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = manager.get_user_prompt("user123", "rag_only")
        assert prompt is None
    
    def test_reset_user_prompt(self, temp_dir):
        """Test resetting a user prompt"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = "Custom prompt with role and guidelines and response format"
        manager.set_user_prompt("user123", "rag_only", prompt)
        
        # Verify it's set
        assert manager.get_user_prompt("user123", "rag_only") == prompt
        
        # Reset
        success = manager.reset_user_prompt("user123", "rag_only")
        assert success is True
        
        # Should return None now
        assert manager.get_user_prompt("user123", "rag_only") is None
    
    def test_get_user_prompts_all(self, temp_dir):
        """Test getting all user prompts"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt1 = "Prompt 1 with role and guidelines and format"
        prompt2 = "Prompt 2 with role and guidelines and format"
        
        manager.set_user_prompt("user123", "rag_only", prompt1)
        manager.set_user_prompt("user123", "web_search_only", prompt2)
        
        all_prompts = manager.get_user_prompts("user123")
        
        assert len(all_prompts) == 2
        assert "rag_only" in all_prompts
        assert "web_search_only" in all_prompts
    
    def test_clear_all_user_prompts(self, temp_dir):
        """Test clearing all user prompts"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        manager.set_user_prompt("user123", "rag_only", "Prompt with role guidelines format")
        manager.set_user_prompt("user123", "web_search_only", "Another prompt with role guidelines format")
        
        success = manager.clear_user_prompts("user123")
        assert success is True
        
        all_prompts = manager.get_user_prompts("user123")
        assert len(all_prompts) == 0
    
    def test_prompt_metadata_stored(self, temp_dir):
        """Test that prompt metadata is stored correctly"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = "Test prompt with role and guidelines and format"
        manager.set_user_prompt("user123", "rag_only", prompt)
        
        # Read file directly to verify structure
        user_file = manager._get_user_file("user123")
        with open(user_file, 'r') as f:
            data = json.load(f)
        
        assert "rag_only" in data
        assert "prompt" in data["rag_only"]
        assert "updated_at" in data["rag_only"]
        assert "hash" in data["rag_only"]
        assert data["rag_only"]["prompt"] == prompt
    
    def test_file_sync_on_save(self, temp_dir):
        """Test that file is synced to disk immediately"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        prompt = "Test prompt with role and guidelines and format for sync test"
        manager.set_user_prompt("user123", "rag_only", prompt)
        
        # Immediately read file (no time for buffering)
        user_file = manager._get_user_file("user123")
        with open(user_file, 'r') as f:
            data = json.load(f)
        
        # Data should be there immediately
        assert data["rag_only"]["prompt"] == prompt
    
    def test_multiple_users_isolation(self, temp_dir):
        """Test that different users have isolated prompts"""
        manager = UserPromptManager(storage_dir=str(temp_dir))
        
        manager.set_user_prompt("user1", "rag_only", "User 1 prompt with role guidelines format")
        manager.set_user_prompt("user2", "rag_only", "User 2 prompt with role guidelines format")
        
        user1_prompt = manager.get_user_prompt("user1", "rag_only")
        user2_prompt = manager.get_user_prompt("user2", "rag_only")
        
        assert "User 1" in user1_prompt
        assert "User 2" in user2_prompt
        assert user1_prompt != user2_prompt

