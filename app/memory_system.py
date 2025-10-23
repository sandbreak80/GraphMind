"""
User Memory System for Chat Context and Preferences
Stores and retrieves user-specific information across sessions
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class UserMemory:
    """User memory system for storing chat context and preferences."""
    
    def __init__(self, storage_dir: str = "/workspace/user_memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Memory categories
        self.categories = {
            'preferences': 'user_preferences.json',
            'chat_history': 'chat_history.json', 
            'strategies': 'trading_strategies.json',
            'insights': 'key_insights.json',
            'context': 'conversation_context.json'
        }
    
    def get_user_file(self, user_id: str, category: str) -> Path:
        """Get the file path for a user's memory category."""
        user_dir = self.storage_dir / user_id
        user_dir.mkdir(exist_ok=True)
        return user_dir / self.categories[category]
    
    def store_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Store a user preference."""
        try:
            file_path = self.get_user_file(user_id, 'preferences')
            preferences = self._load_json(file_path) or {}
            preferences[key] = value
            preferences['updated_at'] = time.time()
            self._save_json(file_path, preferences)
            return True
        except Exception as e:
            logger.error(f"Failed to store preference for {user_id}: {e}")
            return False
    
    def get_preference(self, user_id: str, key: str, default: Any = None) -> Any:
        """Get a user preference."""
        try:
            file_path = self.get_user_file(user_id, 'preferences')
            preferences = self._load_json(file_path) or {}
            return preferences.get(key, default)
        except Exception as e:
            logger.error(f"Failed to get preference for {user_id}: {e}")
            return default
    
    def store_chat_context(self, user_id: str, chat_id: str, context: Dict[str, Any]) -> bool:
        """Store chat context for a user."""
        try:
            file_path = self.get_user_file(user_id, 'context')
            contexts = self._load_json(file_path) or {}
            contexts[chat_id] = {
                **context,
                'updated_at': time.time()
            }
            self._save_json(file_path, contexts)
            return True
        except Exception as e:
            logger.error(f"Failed to store chat context for {user_id}: {e}")
            return False
    
    def get_chat_context(self, user_id: str, chat_id: str) -> Dict[str, Any]:
        """Get chat context for a user."""
        try:
            file_path = self.get_user_file(user_id, 'context')
            contexts = self._load_json(file_path) or {}
            return contexts.get(chat_id, {})
        except Exception as e:
            logger.error(f"Failed to get chat context for {user_id}: {e}")
            return {}
    
    def store_strategy_insight(self, user_id: str, strategy: str, insight: str, importance: float = 0.5) -> bool:
        """Store a trading strategy insight."""
        try:
            file_path = self.get_user_file(user_id, 'strategies')
            strategies = self._load_json(file_path) or {}
            
            if strategy not in strategies:
                strategies[strategy] = {
                    'insights': [],
                    'created_at': time.time(),
                    'updated_at': time.time()
                }
            
            strategies[strategy]['insights'].append({
                'insight': insight,
                'importance': importance,
                'created_at': time.time()
            })
            strategies[strategy]['updated_at'] = time.time()
            
            self._save_json(file_path, strategies)
            return True
        except Exception as e:
            logger.error(f"Failed to store strategy insight for {user_id}: {e}")
            return False
    
    def get_strategy_insights(self, user_id: str, strategy: str) -> List[Dict[str, Any]]:
        """Get insights for a specific strategy."""
        try:
            file_path = self.get_user_file(user_id, 'strategies')
            strategies = self._load_json(file_path) or {}
            return strategies.get(strategy, {}).get('insights', [])
        except Exception as e:
            logger.error(f"Failed to get strategy insights for {user_id}: {e}")
            return []
    
    def store_key_insight(self, user_id: str, insight: str, category: str = 'general') -> bool:
        """Store a key insight about the user's trading approach."""
        try:
            file_path = self.get_user_file(user_id, 'insights')
            insights = self._load_json(file_path) or {}
            
            if category not in insights:
                insights[category] = []
            
            insights[category].append({
                'insight': insight,
                'created_at': time.time()
            })
            
            # Keep only last 50 insights per category
            insights[category] = insights[category][-50:]
            
            self._save_json(file_path, insights)
            return True
        except Exception as e:
            logger.error(f"Failed to store key insight for {user_id}: {e}")
            return False
    
    def get_key_insights(self, user_id: str, category: str = 'general', limit: int = 10) -> List[Dict[str, Any]]:
        """Get key insights for a user."""
        try:
            file_path = self.get_user_file(user_id, 'insights')
            insights = self._load_json(file_path) or {}
            return insights.get(category, [])[-limit:]
        except Exception as e:
            logger.error(f"Failed to get key insights for {user_id}: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get a comprehensive user profile."""
        try:
            profile = {
                'user_id': user_id,
                'preferences': self._load_json(self.get_user_file(user_id, 'preferences')) or {},
                'strategies': list((self._load_json(self.get_user_file(user_id, 'strategies')) or {}).keys()),
                'recent_insights': self.get_key_insights(user_id, limit=5),
                'created_at': self._get_oldest_file_time(user_id),
                'updated_at': time.time()
            }
            return profile
        except Exception as e:
            logger.error(f"Failed to get user profile for {user_id}: {e}")
            return {'user_id': user_id, 'error': str(e)}
    
    def get_memory_context(self, user_id: str, current_query: str) -> str:
        """Get relevant memory context for a query."""
        try:
            context_parts = []
            
            # Get user preferences
            preferences = self._load_json(self.get_user_file(user_id, 'preferences')) or {}
            if preferences:
                context_parts.append(f"User Preferences: {json.dumps(preferences, indent=2)}")
            
            # Get recent insights
            recent_insights = self.get_key_insights(user_id, limit=3)
            if recent_insights:
                insights_text = "\n".join([i['insight'] for i in recent_insights])
                context_parts.append(f"Recent Insights: {insights_text}")
            
            # Get strategy insights if query mentions strategies
            if any(word in current_query.lower() for word in ['strategy', 'setup', 'fade', 'trade']):
                strategies = self._load_json(self.get_user_file(user_id, 'strategies')) or {}
                for strategy, data in strategies.items():
                    if data.get('insights'):
                        strategy_insights = "\n".join([i['insight'] for i in data['insights'][-3:]])
                        context_parts.append(f"{strategy} Insights: {strategy_insights}")
            
            return "\n\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"Failed to get memory context for {user_id}: {e}")
            return ""
    
    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """Load JSON data from file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON from {file_path}: {e}")
        return None
    
    def _save_json(self, file_path: Path, data: Dict) -> bool:
        """Save JSON data to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save JSON to {file_path}: {e}")
            return False
    
    def _get_oldest_file_time(self, user_id: str) -> float:
        """Get the creation time of the oldest file for a user."""
        try:
            user_dir = self.storage_dir / user_id
            if user_dir.exists():
                files = list(user_dir.glob('*.json'))
                if files:
                    return min(f.stat().st_mtime for f in files)
        except Exception as e:
            logger.error(f"Failed to get oldest file time for {user_id}: {e}")
        return time.time()

class MemoryAwareRAG:
    """RAG system with user memory integration."""
    
    def __init__(self, retriever, memory_system: UserMemory):
        self.retriever = retriever
        self.memory = memory_system
    
    def generate_with_memory(self, user_id: str, query: str, context: str, conversation_history: Optional[List[Dict[str, str]]] = None, 
                             model: Optional[str] = None, temperature: Optional[float] = None, 
                             max_tokens: Optional[int] = None, top_k_sampling: Optional[int] = None) -> str:
        """Generate response with user memory context."""
        try:
            # Get memory context
            memory_context = self.memory.get_memory_context(user_id, query)
            
            # Combine all context
            full_context = f"""USER MEMORY CONTEXT:
{memory_context}

RETRIEVED DOCUMENT CONTEXT:
{context}

{conversation_history or ''}

USER QUESTION: {query}"""
            
            # Generate response using the retriever's LLM
            from app.ollama_client import OllamaClient
            from app.config import PRODUCTION_LLM_MODEL, TEMPERATURE, MAX_TOKENS, OLLAMA_TOP_K
            
            llm_model = model or PRODUCTION_LLM_MODEL
            llm_temperature = temperature if temperature is not None else TEMPERATURE
            llm_max_tokens = max_tokens if max_tokens is not None else MAX_TOKENS
            llm_top_k = top_k_sampling if top_k_sampling is not None else OLLAMA_TOP_K
            
            ollama = OllamaClient(default_model=llm_model)
            response = ollama.generate(
                prompt=full_context,
                model=llm_model,
                temperature=llm_temperature,
                max_tokens=llm_max_tokens,
                top_k=llm_top_k,
                timeout=300
            )
            
            # Store insights if the response contains strategy information
            if any(word in response.lower() for word in ['strategy', 'setup', 'fade', 'trade', 'entry', 'exit']):
                self.memory.store_key_insight(
                    user_id, 
                    f"Query: {query[:100]}... | Response: {response[:200]}...",
                    'strategy_discussion'
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Memory-aware generation failed: {e}")
            # Fallback to regular generation
            return self.retriever._generate_answer(query, context, conversation_history)

