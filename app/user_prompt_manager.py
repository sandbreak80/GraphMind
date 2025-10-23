"""
User Prompt Manager for TradingAI Research Platform
Manages user-specific customizations of system prompts
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class UserPromptManager:
    """Manages user-specific system prompt customizations."""
    
    def __init__(self, storage_dir: str = "/workspace/user_prompts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        """Get the file path for a user's prompts."""
        user_dir = self.storage_dir / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir / "custom_prompts.json"
    
    def get_user_prompt(self, user_id: str, mode: str) -> Optional[str]:
        """Get user's custom prompt for a mode."""
        try:
            user_file = self._get_user_file(user_id)
            if not user_file.exists():
                return None
            
            with open(user_file, 'r') as f:
                user_prompts = json.load(f)
            
            return user_prompts.get(mode)
            
        except Exception as e:
            logger.error(f"Failed to get user prompt for {user_id} mode {mode}: {e}")
            return None
    
    def set_user_prompt(self, user_id: str, mode: str, prompt: str) -> bool:
        """Set user's custom prompt for a mode."""
        try:
            user_file = self._get_user_file(user_id)
            
            # Load existing prompts or create new structure
            if user_file.exists():
                with open(user_file, 'r') as f:
                    user_prompts = json.load(f)
            else:
                user_prompts = {}
            
            # Update prompt
            user_prompts[mode] = {
                "prompt": prompt,
                "updated_at": datetime.now().isoformat(),
                "hash": hashlib.md5(prompt.encode()).hexdigest()[:8]
            }
            
            # Save to file
            with open(user_file, 'w') as f:
                json.dump(user_prompts, f, indent=2)
            
            logger.info(f"Saved custom prompt for user {user_id} mode {mode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user prompt for {user_id} mode {mode}: {e}")
            return False
    
    def reset_user_prompt(self, user_id: str, mode: str) -> bool:
        """Reset user's custom prompt to default."""
        try:
            user_file = self._get_user_file(user_id)
            if not user_file.exists():
                return True
            
            with open(user_file, 'r') as f:
                user_prompts = json.load(f)
            
            # Remove the mode
            if mode in user_prompts:
                del user_prompts[mode]
                
                # Save updated prompts
                with open(user_file, 'w') as f:
                    json.dump(user_prompts, f, indent=2)
            
            logger.info(f"Reset custom prompt for user {user_id} mode {mode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset user prompt for {user_id} mode {mode}: {e}")
            return False
    
    def get_user_prompts(self, user_id: str) -> Dict[str, Any]:
        """Get all user's custom prompts."""
        try:
            user_file = self._get_user_file(user_id)
            if not user_file.exists():
                return {}
            
            with open(user_file, 'r') as f:
                user_prompts = json.load(f)
            
            return user_prompts
            
        except Exception as e:
            logger.error(f"Failed to get user prompts for {user_id}: {e}")
            return {}
    
    def clear_user_prompts(self, user_id: str) -> bool:
        """Clear all user's custom prompts."""
        try:
            user_file = self._get_user_file(user_id)
            if user_file.exists():
                user_file.unlink()
            
            logger.info(f"Cleared all custom prompts for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear user prompts for {user_id}: {e}")
            return False
    
    def get_prompt_with_fallback(self, user_id: str, mode: str, default_prompt: str) -> str:
        """Get user's custom prompt or fallback to default."""
        user_prompt = self.get_user_prompt(user_id, mode)
        return user_prompt if user_prompt else default_prompt

# Global instance
user_prompt_manager = UserPromptManager()