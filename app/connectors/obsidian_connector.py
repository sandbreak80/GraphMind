# GraphMind Obsidian Connector
# Obsidian vault connector for GraphMind

import logging
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import asyncio
import json

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class ObsidianConnector(BaseConnector):
    """
    Obsidian vault connector for GraphMind.
    
    This connector handles Obsidian vault access and retrieval
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Obsidian connector."""
        super().__init__(config)
        self.name = "Obsidian Connector"
        self.vault_path = config.get('vault_path', './obsidian_vault')
        self.supported_formats = ['.md', '.txt']
        self.connection = None
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields for Obsidian connector."""
        return ['name', 'vault_path']
    
    async def connect(self) -> bool:
        """Test connection to Obsidian vault."""
        try:
            vault_path = Path(self.vault_path)
            if not vault_path.exists():
                logger.error(f"Obsidian vault path does not exist: {self.vault_path}")
                return False
            
            # Check if it's a valid Obsidian vault
            if not (vault_path / '.obsidian').exists():
                logger.warning(f"Path does not appear to be an Obsidian vault: {self.vault_path}")
            
            # Check for markdown files
            md_files = list(vault_path.glob("**/*.md"))
            if not md_files:
                logger.warning(f"No markdown files found in vault: {self.vault_path}")
                return False
            
            self.connection = True
            logger.info(f"Obsidian connector connected to {len(md_files)} markdown files")
            return True
            
        except Exception as e:
            logger.error(f"Obsidian connector connection failed: {e}")
            return False
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search Obsidian vault."""
        try:
            if not self.connection:
                await self.connect()
            
            if not self.connection:
                return []
            
            results = []
            vault_path = Path(self.vault_path)
            
            # Search through all markdown files
            for md_file in vault_path.glob("**/*.md"):
                try:
                    file_results = await self._search_markdown_file(md_file, query, **kwargs)
                    results.extend(file_results)
                except Exception as e:
                    logger.error(f"Error searching markdown file {md_file}: {e}")
                    continue
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Obsidian search failed: {e}")
            return []
    
    async def _search_markdown_file(self, md_file: Path, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search a single markdown file."""
        try:
            # Read markdown file
            content = md_file.read_text(encoding='utf-8')
            
            # Simple text search
            if query.lower() in content.lower():
                # Extract relevant content around the query
                context = self._extract_context(content, query)
                
                # Get file metadata
                metadata = await self._get_file_metadata(md_file)
                
                results = [{
                    'text': context,
                    'metadata': {
                        'doc_id': str(md_file.relative_to(Path(self.vault_path))),
                        'file_name': md_file.name,
                        'file_path': str(md_file.relative_to(Path(self.vault_path))),
                        'doc_type': 'obsidian_note',
                        'source': 'obsidian_connector',
                        'vault_path': str(md_file.relative_to(Path(self.vault_path))),
                        'file_size': md_file.stat().st_size,
                        'modified_time': md_file.stat().st_mtime,
                        **metadata
                    },
                    'score': self._calculate_relevance_score(content, query)
                }]
                
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Error processing markdown file {md_file}: {e}")
            return []
    
    def _extract_context(self, content: str, query: str, context_length: int = 300) -> str:
        """Extract context around the query."""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Find query position
        query_pos = content_lower.find(query_lower)
        if query_pos == -1:
            return content[:context_length] + "..."
        
        # Extract context around query
        start = max(0, query_pos - context_length // 2)
        end = min(len(content), query_pos + len(query) + context_length // 2)
        
        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."
        
        return context
    
    def _calculate_relevance_score(self, content: str, query: str) -> float:
        """Calculate relevance score for content."""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Simple scoring based on query frequency
        query_count = content_lower.count(query_lower)
        content_length = len(content_lower)
        
        if content_length == 0:
            return 0.0
        
        # Normalize score
        score = min(1.0, query_count / (content_length / 1000))
        return score
    
    async def _get_file_metadata(self, md_file: Path) -> Dict[str, Any]:
        """Get metadata for a markdown file."""
        try:
            metadata = {}
            
            # Read file content to extract frontmatter
            content = md_file.read_text(encoding='utf-8')
            
            # Extract frontmatter if present
            if content.startswith('---'):
                lines = content.split('\n')
                frontmatter_end = -1
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == '---':
                        frontmatter_end = i
                        break
                
                if frontmatter_end > 0:
                    frontmatter_lines = lines[1:frontmatter_end]
                    for line in frontmatter_lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip().strip('"\'')
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {md_file}: {e}")
            return {}
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get Obsidian connector metadata."""
        try:
            vault_path = Path(self.vault_path)
            md_files = list(vault_path.glob("**/*.md"))
            
            total_size = 0
            total_notes = len(md_files)
            
            for md_file in md_files:
                try:
                    total_size += md_file.stat().st_size
                except Exception as e:
                    logger.error(f"Error getting size for {md_file}: {e}")
                    continue
            
            return {
                'connector': self.name,
                'vault_path': str(self.vault_path),
                'total_notes': total_notes,
                'total_size_bytes': total_size,
                'supported_formats': self.supported_formats
            }
            
        except Exception as e:
            logger.error(f"Failed to get Obsidian metadata: {e}")
            return {
                'connector': self.name,
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return self.supported_formats
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get search capabilities."""
        return {
            'text_search': True,
            'metadata_search': True,
            'faceted_search': False,
            'full_text_search': True,
            'frontmatter_search': True,
            'link_search': True
        }
    
    async def close(self):
        """Close the Obsidian connector."""
        self.connection = False
        logger.info("Obsidian connector closed")
