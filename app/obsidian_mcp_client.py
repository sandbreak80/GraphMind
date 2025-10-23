"""Obsidian MCP integration for accessing personal notes and knowledge."""
import logging
import json
import asyncio
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class ObsidianMCPClient:
    """Obsidian MCP client for accessing personal notes and knowledge."""
    
    def __init__(self, obsidian_vault_path: str, obsidian_api_url: str = "https://localhost:27124", api_key: str = None):
        self.vault_path = obsidian_vault_path
        self.api_url = obsidian_api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'TradingAI-Research-Platform/2.0'
        })
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        # Disable SSL verification for self-signed certificates
        self.session.verify = False
    
    async def search_notes(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for notes containing the query."""
        try:
            # First get all files from vault
            response = self.session.get(f"{self.api_url}/vault/")
            response.raise_for_status()
            vault_data = response.json()
            files = vault_data.get("files", [])
            
            # Filter files that match the query
            matching_files = []
            for file in files:
                if query.lower() in file.lower():
                    # Get file content
                    try:
                        content_response = self.session.get(f"{self.api_url}/vault/{file}")
                        content_response.raise_for_status()
                        content = content_response.text
                        
                        matching_files.append({
                            "path": file,
                            "title": file.replace(".md", ""),
                            "content": content,
                            "text": content[:500] + "..." if len(content) > 500 else content
                        })
                    except Exception as e:
                        logger.warning(f"Failed to get content for {file}: {e}")
                        matching_files.append({
                            "path": file,
                            "title": file.replace(".md", ""),
                            "content": "",
                            "text": file
                        })
            
            return matching_files[:limit]
            
        except Exception as e:
            logger.error(f"Obsidian search failed: {e}")
            return []
    
    async def get_note_content(self, note_path: str) -> Optional[str]:
        """Get the content of a specific note."""
        try:
            response = self.session.get(
                f"{self.api_url}/vault/{note_path}",
                timeout=10
            )
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to get note content: {e}")
            return None
    
    async def get_note_metadata(self, note_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific note."""
        try:
            response = self.session.get(
                f"{self.api_url}/notes/{note_path}/metadata",
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get note metadata: {e}")
            return None
    
    async def get_notes_by_tag(self, tag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get notes with a specific tag."""
        try:
            response = self.session.get(
                f"{self.api_url}/tags/{tag}/notes",
                params={'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            
            return response.json().get('notes', [])
            
        except Exception as e:
            logger.error(f"Failed to get notes by tag: {e}")
            return []
    
    async def get_recent_notes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently modified notes."""
        try:
            response = self.session.get(
                f"{self.api_url}/notes/recent",
                params={'limit': limit},
                timeout=10
            )
            response.raise_for_status()
            
            return response.json().get('notes', [])
            
        except Exception as e:
            logger.error(f"Failed to get recent notes: {e}")
            return []
    
    async def search_trading_notes(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Search for trading-related notes."""
        # Search for trading-related terms
        trading_terms = [
            "trading", "strategy", "setup", "entry", "exit", "risk", "position",
            "futures", "ES", "NQ", "YM", "RT", "fade", "breakout", "pullback",
            "support", "resistance", "trend", "momentum", "volatility"
        ]
        
        all_results = []
        
        # Search with original query
        results = await self.search_notes(query, limit)
        all_results.extend(results)
        
        # Search with trading terms
        for term in trading_terms:
            if term.lower() in query.lower():
                term_results = await self.search_notes(term, 5)
                all_results.extend(term_results)
        
        # Remove duplicates and limit results
        seen_paths = set()
        unique_results = []
        for result in all_results:
            if result.get('path') not in seen_paths:
                seen_paths.add(result['path'])
                unique_results.append(result)
        
        return unique_results[:limit]
    
    async def get_note_links(self, note_path: str) -> List[str]:
        """Get all links from a note."""
        try:
            content = await self.get_note_content(note_path)
            if not content:
                return []
            
            # Simple link extraction ([[link]] format)
            import re
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            return links
            
        except Exception as e:
            logger.error(f"Failed to get note links: {e}")
            return []
    
    async def get_backlinks(self, note_path: str) -> List[Dict[str, Any]]:
        """Get notes that link to this note."""
        try:
            response = self.session.get(
                f"{self.api_url}/notes/{note_path}/backlinks",
                timeout=10
            )
            response.raise_for_status()
            
            return response.json().get('backlinks', [])
            
        except Exception as e:
            logger.error(f"Failed to get backlinks: {e}")
            return []


class ObsidianKnowledgeProvider:
    """Knowledge provider that integrates Obsidian notes with RAG system."""
    
    def __init__(self, obsidian_client: ObsidianMCPClient):
        self.obsidian = obsidian_client
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_relevant_notes(self, query: str, context: str = "") -> List[Dict[str, Any]]:
        """Get relevant notes for a trading query."""
        # Check cache first
        cache_key = f"notes_{hash(query + context)}"
        if cache_key in self.cache:
            cached_time, cached_results = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_results
        
        # Search for trading-related notes
        notes = await self.obsidian.search_trading_notes(query, 15)
        
        # Enrich notes with content
        enriched_notes = []
        for note in notes:
            try:
                content = await self.obsidian.get_note_content(note['path'])
                metadata = await self.obsidian.get_note_metadata(note['path'])
                
                enriched_note = {
                    'path': note['path'],
                    'title': note.get('title', os.path.basename(note['path'])),
                    'content': content or '',
                    'metadata': metadata or {},
                    'last_modified': note.get('last_modified'),
                    'tags': note.get('tags', []),
                    'score': note.get('score', 0.0)
                }
                enriched_notes.append(enriched_note)
                
            except Exception as e:
                logger.warning(f"Failed to enrich note {note['path']}: {e}")
                continue
        
        # Cache results
        self.cache[cache_key] = (time.time(), enriched_notes)
        
        return enriched_notes
    
    async def get_note_context(self, note_path: str, context_radius: int = 2) -> Dict[str, Any]:
        """Get context around a note including linked notes."""
        try:
            # Get the main note
            main_content = await self.obsidian.get_note_content(note_path)
            main_metadata = await self.obsidian.get_note_metadata(note_path)
            
            # Get linked notes
            links = await self.obsidian.get_note_links(note_path)
            linked_notes = []
            
            for link in links[:context_radius]:  # Limit to avoid too much data
                try:
                    link_content = await self.obsidian.get_note_content(link)
                    if link_content:
                        linked_notes.append({
                            'path': link,
                            'content': link_content[:1000],  # Truncate for context
                            'title': os.path.basename(link)
                        })
                except Exception as e:
                    logger.warning(f"Failed to get linked note {link}: {e}")
                    continue
            
            # Get backlinks
            backlinks = await self.obsidian.get_backlinks(note_path)
            
            return {
                'main_note': {
                    'path': note_path,
                    'content': main_content,
                    'metadata': main_metadata
                },
                'linked_notes': linked_notes,
                'backlinks': backlinks,
                'context_radius': context_radius
            }
            
        except Exception as e:
            logger.error(f"Failed to get note context: {e}")
            return {}


class EnhancedRAGWithObsidian:
    """Enhanced RAG system with Obsidian integration for personal knowledge."""
    
    def __init__(self, retriever, obsidian_client: Optional[ObsidianMCPClient] = None):
        self.retriever = retriever
        self.obsidian = obsidian_client
        self.knowledge_provider = ObsidianKnowledgeProvider(obsidian_client) if obsidian_client else None
    
    async def search_with_personal_knowledge(self, query: str, include_obsidian: bool = True) -> Dict[str, Any]:
        """Enhanced search combining document knowledge with personal Obsidian notes."""
        # Get document-based results
        doc_results = self.retriever.retrieve(query, top_k=15)
        
        obsidian_results = []
        if include_obsidian and self.knowledge_provider:
            try:
                # Get relevant personal notes
                obsidian_results = await self.knowledge_provider.get_relevant_notes(query)
                
                # Format for consistency with document results
                formatted_obsidian = []
                for note in obsidian_results:
                    formatted_obsidian.append({
                        'text': note['content'],
                        'metadata': {
                            'doc_id': f"obsidian_{note['path']}",
                            'title': note['title'],
                            'path': note['path'],
                            'tags': note['tags'],
                            'last_modified': note['last_modified'],
                            'source': 'obsidian'
                        },
                        'score': note['score'],
                        'rerank_score': note['score']
                    })
                
                obsidian_results = formatted_obsidian
                
            except Exception as e:
                logger.warning(f"Obsidian search failed: {e}")
        
        return {
            "document_results": doc_results,
            "obsidian_results": obsidian_results,
            "total_sources": len(doc_results) + len(obsidian_results),
            "obsidian_enabled": self.obsidian is not None
        }
    
    async def search_obsidian_only(self, query: str) -> Dict[str, Any]:
        """Search ONLY Obsidian notes (no document retrieval)."""
        obsidian_results = []
        if self.knowledge_provider:
            try:
                # Get relevant personal notes
                obsidian_results = await self.knowledge_provider.get_relevant_notes(query)
                
                # Format for consistency with document results
                formatted_obsidian = []
                for note in obsidian_results:
                    formatted_obsidian.append({
                        'text': note['content'],
                        'metadata': {
                            'doc_id': f"obsidian_{note['path']}",
                            'title': note['title'],
                            'path': note['path'],
                            'tags': note['tags'],
                            'last_modified': note['last_modified'],
                            'source': 'obsidian'
                        },
                        'score': note['score'],
                        'rerank_score': note['score']
                    })
                
                obsidian_results = formatted_obsidian
                
            except Exception as e:
                logger.warning(f"Obsidian search failed: {e}")
        
        return {
            "document_results": [],  # No document results
            "obsidian_results": obsidian_results,
            "total_sources": len(obsidian_results),
            "obsidian_enabled": self.obsidian is not None
        }
    
    async def get_comprehensive_knowledge(self, query: str) -> Dict[str, Any]:
        """Get comprehensive knowledge from both documents and personal notes."""
        # Get combined results
        search_results = await self.search_with_personal_knowledge(query)
        
        # Combine contexts
        doc_context = "\n".join([r['text'] for r in search_results["document_results"]])
        obsidian_context = "\n".join([r['text'] for r in search_results["obsidian_results"]])
        
        combined_context = f"DOCUMENT KNOWLEDGE:\n{doc_context}\n\nPERSONAL KNOWLEDGE (OBSIDIAN):\n{obsidian_context}"
        
        return {
            "query": query,
            "combined_context": combined_context,
            "document_results": search_results["document_results"],
            "obsidian_results": search_results["obsidian_results"],
            "total_sources": search_results["total_sources"],
            "obsidian_enabled": search_results["obsidian_enabled"],
            "timestamp": datetime.now().isoformat()
        }


def create_obsidian_client(vault_path: str, api_url: str = "https://localhost:27124", api_key: str = None) -> Optional[ObsidianMCPClient]:
    """Create Obsidian MCP client if configuration is available."""
    if not vault_path or not os.path.exists(vault_path):
        logger.warning(f"Obsidian vault path not found: {vault_path}")
        return None
    
    try:
        client = ObsidianMCPClient(vault_path, api_url, api_key)
        # Test connection
        response = client.session.get(f"{api_url}/", timeout=5)
        if response.status_code == 200:
            logger.info(f"Obsidian MCP client connected to {api_url}")
            return client
        else:
            logger.warning(f"Obsidian API not responding at {api_url}: {response.status_code}")
            return None
    except Exception as e:
        logger.warning(f"Failed to create Obsidian MCP client: {e}")
        return None