# GraphMind Web Connector
# Web search connector for GraphMind

import logging
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import json

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class WebConnector(BaseConnector):
    """
    Web search connector for GraphMind.
    
    This connector handles web search functionality
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the web connector."""
        super().__init__(config)
        self.name = "Web Connector"
        self.search_url = config.get('search_url', 'http://localhost:8080/search')
        self.api_key = config.get('api_key', '')
        self.max_results = config.get('max_results', 10)
        self.timeout = config.get('timeout', 30)
        self.session = None
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields for web connector."""
        return ['name', 'search_url']
    
    async def connect(self) -> bool:
        """Test connection to web search service."""
        try:
            # Create aiohttp session
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
            
            # Test connection with a simple search
            test_query = "test"
            test_results = await self._perform_search(test_query)
            
            if test_results is not None:
                self.connection = True
                logger.info("Web connector connected successfully")
                return True
            else:
                logger.error("Web connector connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Web connector connection failed: {e}")
            return False
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search the web."""
        try:
            if not self.connection:
                await self.connect()
            
            if not self.connection:
                return []
            
            # Perform web search
            results = await self._perform_search(query, **kwargs)
            
            if not results:
                return []
            
            # Format results for GraphMind
            formatted_results = []
            for result in results:
                formatted_result = {
                    'text': result.get('content', result.get('snippet', '')),
                    'metadata': {
                        'doc_id': result.get('url', ''),
                        'file_name': result.get('title', 'Web Result'),
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'doc_type': 'web_result',
                        'source': 'web_connector',
                        'published_date': result.get('published_date', ''),
                        'engine': result.get('engine', 'searxng')
                    },
                    'score': result.get('score', 0.5)
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    async def _perform_search(self, query: str, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """Perform the actual web search."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
            
            # Prepare search parameters
            params = {
                'q': query,
                'format': 'json',
                'categories': kwargs.get('categories', 'general'),
                'engines': kwargs.get('engines', 'google,bing,duckduckgo'),
                'language': kwargs.get('language', 'en'),
                'time_range': kwargs.get('time_range', ''),
                'safesearch': kwargs.get('safesearch', '1')
            }
            
            # Add API key if provided
            if self.api_key:
                params['api_key'] = self.api_key
            
            # Perform search request
            async with self.session.get(self.search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
                else:
                    logger.error(f"Web search failed with status: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Web search request failed: {e}")
            return None
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get web connector metadata."""
        return {
            'connector': self.name,
            'search_url': self.search_url,
            'max_results': self.max_results,
            'timeout': self.timeout,
            'api_key_configured': bool(self.api_key)
        }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported formats (web results are text-based)."""
        return ['text', 'html', 'json']
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get search capabilities."""
        return {
            'text_search': True,
            'metadata_search': True,
            'faceted_search': True,
            'full_text_search': True,
            'web_search': True,
            'image_search': True,
            'news_search': True
        }
    
    async def close(self):
        """Close the web connector."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connection = False
        logger.info("Web connector closed")
