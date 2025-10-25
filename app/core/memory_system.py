# GraphMind Memory System
# Domain-agnostic memory system for GraphMind

import logging
from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class GraphMindMemorySystem:
    """
    Domain-agnostic memory system for GraphMind.
    
    This class provides memory functionality that can be used
    across any domain without trading-specific terminology.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the memory system."""
        self.config = config
        self.memory_dir = Path(config.get('memory_dir', './memory'))
        self.memory_file = self.memory_dir / 'user_memory.json'
        self.max_memory_size = config.get('max_memory_size', 1000)
        self.memory = {}
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize memory system."""
        try:
            # Create memory directory if it doesn't exist
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing memory
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded memory with {len(self.memory)} entries")
            else:
                self.memory = {}
                logger.info("Initialized new memory system")
                
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            self.memory = {}
    
    async def add_memory(
        self, 
        key: str, 
        value: Any, 
        domain: str = "generic",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a memory entry.
        
        Args:
            key: Memory key
            value: Memory value
            domain: Domain context
            metadata: Additional metadata
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Create memory entry
            memory_entry = {
                'value': value,
                'domain': domain,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Add to memory
            self.memory[key] = memory_entry
            
            # Save to file
            await self._save_memory()
            
            logger.info(f"Added memory entry: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory entry {key}: {e}")
            return False
    
    async def get_memory(self, key: str) -> Optional[Any]:
        """
        Get a memory entry.
        
        Args:
            key: Memory key
            
        Returns:
            Memory value or None
        """
        try:
            if key in self.memory:
                # Update access time
                self.memory[key]['updated_at'] = datetime.now().isoformat()
                await self._save_memory()
                return self.memory[key]['value']
            return None
            
        except Exception as e:
            logger.error(f"Failed to get memory entry {key}: {e}")
            return None
    
    async def update_memory(
        self, 
        key: str, 
        value: Any, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a memory entry.
        
        Args:
            key: Memory key
            value: New memory value
            metadata: Additional metadata
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if key not in self.memory:
                logger.warning(f"Memory entry {key} not found for update")
                return False
            
            # Update memory entry
            self.memory[key]['value'] = value
            self.memory[key]['updated_at'] = datetime.now().isoformat()
            
            if metadata:
                self.memory[key]['metadata'].update(metadata)
            
            # Save to file
            await self._save_memory()
            
            logger.info(f"Updated memory entry: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory entry {key}: {e}")
            return False
    
    async def delete_memory(self, key: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            key: Memory key
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if key in self.memory:
                del self.memory[key]
                await self._save_memory()
                logger.info(f"Deleted memory entry: {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory entry {key}: {e}")
            return False
    
    async def search_memory(
        self, 
        query: str, 
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memory entries.
        
        Args:
            query: Search query
            domain: Domain filter (optional)
            limit: Maximum results
            
        Returns:
            List of matching memory entries
        """
        try:
            results = []
            query_lower = query.lower()
            
            for key, entry in self.memory.items():
                # Filter by domain if specified
                if domain and entry.get('domain') != domain:
                    continue
                
                # Search in key and value
                key_match = query_lower in key.lower()
                value_match = False
                
                # Search in value if it's a string
                if isinstance(entry.get('value'), str):
                    value_match = query_lower in entry['value'].lower()
                
                if key_match or value_match:
                    results.append({
                        'key': key,
                        'value': entry['value'],
                        'domain': entry.get('domain'),
                        'created_at': entry.get('created_at'),
                        'updated_at': entry.get('updated_at'),
                        'metadata': entry.get('metadata', {})
                    })
            
            # Sort by updated_at (most recent first)
            results.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []
    
    async def get_domain_memory(self, domain: str) -> Dict[str, Any]:
        """
        Get all memory entries for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary of domain memory entries
        """
        try:
            domain_memory = {}
            
            for key, entry in self.memory.items():
                if entry.get('domain') == domain:
                    domain_memory[key] = entry
            
            return domain_memory
            
        except Exception as e:
            logger.error(f"Failed to get domain memory for {domain}: {e}")
            return {}
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """
        Get memory system statistics.
        
        Returns:
            Memory statistics
        """
        try:
            total_entries = len(self.memory)
            domains = set()
            total_size = 0
            
            for entry in self.memory.values():
                domains.add(entry.get('domain', 'unknown'))
                total_size += len(str(entry.get('value', '')))
            
            return {
                'total_entries': total_entries,
                'domains': list(domains),
                'domain_count': len(domains),
                'total_size_bytes': total_size,
                'memory_file_size': self.memory_file.stat().st_size if self.memory_file.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {'error': str(e)}
    
    async def clear_domain_memory(self, domain: str) -> bool:
        """
        Clear all memory entries for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            keys_to_delete = []
            
            for key, entry in self.memory.items():
                if entry.get('domain') == domain:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory[key]
            
            if keys_to_delete:
                await self._save_memory()
                logger.info(f"Cleared {len(keys_to_delete)} memory entries for domain: {domain}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear domain memory for {domain}: {e}")
            return False
    
    async def export_memory(self, file_path: str) -> bool:
        """
        Export memory to a file.
        
        Args:
            file_path: Export file path
            
        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported memory to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")
            return False
    
    async def import_memory(self, file_path: str) -> bool:
        """
        Import memory from a file.
        
        Args:
            file_path: Import file path
            
        Returns:
            True if imported successfully, False otherwise
        """
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                logger.error(f"Import file not found: {file_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_memory = json.load(f)
            
            # Merge with existing memory
            self.memory.update(imported_memory)
            
            # Save to file
            await self._save_memory()
            
            logger.info(f"Imported memory from: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import memory: {e}")
            return False
    
    async def _save_memory(self):
        """Save memory to file."""
        try:
            # Create backup
            if self.memory_file.exists():
                backup_file = self.memory_file.with_suffix('.json.backup')
                self.memory_file.rename(backup_file)
            
            # Save memory
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
            # Remove backup if save successful
            backup_file = self.memory_file.with_suffix('.json.backup')
            if backup_file.exists():
                backup_file.unlink()
                
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            # Restore backup if save failed
            backup_file = self.memory_file.with_suffix('.json.backup')
            if backup_file.exists():
                backup_file.rename(self.memory_file)
    
    async def close(self):
        """Close the memory system and save data."""
        try:
            await self._save_memory()
            logger.info("Memory system closed")
        except Exception as e:
            logger.error(f"Error closing memory system: {e}")
