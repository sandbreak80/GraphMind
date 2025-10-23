"""
Advanced web page parser using Crawl4AI for enhanced search results
LLM-friendly web crawling optimized for RAG and AI applications
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import time
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

logger = logging.getLogger(__name__)

class WebPageParser:
    """Advanced web page parser using Crawl4AI for AI-ready content."""
    
    def __init__(self, timeout: int = 30, max_content_length: int = 100000):
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.crawler = None
    
    async def _get_crawler(self):
        """Get or create crawler instance."""
        if self.crawler is None:
            self.crawler = AsyncWebCrawler(
                headless=True,
                browser_type="chromium",
                verbose=True
            )
        return self.crawler
    
    async def parse_url(self, url: str) -> Dict[str, Any]:
        """
        Parse a single URL using Crawl4AI for AI-ready content.
        
        Args:
            url: URL to parse
            
        Returns:
            Dictionary with parsed content
        """
        try:
            crawler = await self._get_crawler()
            
            # Use Crawl4AI for intelligent content extraction
            result = await crawler.arun(
                url=url,
                word_count_threshold=50,  # Minimum content length
                extraction_strategy=LLMExtractionStrategy(
                    provider="ollama/llama3.1:latest",  # Use your local LLM
                    api_base="http://host.docker.internal:11434",
                    instruction="Extract the main content, focusing on trading, finance, and business information. Remove navigation, ads, and irrelevant content."
                ),
                wait_for="networkidle",
                delay_before_return_html=2.0
            )
            
            if result.success:
                return {
                    'url': url,
                    'title': result.metadata.get('title', 'No title found'),
                    'description': result.metadata.get('description', ''),
                    'content': result.markdown or result.cleaned_html,
                    'word_count': len((result.markdown or '').split()),
                    'parsed_at': time.time(),
                    'status': 'success',
                    'links': result.links,
                    'media': result.media
                }
            else:
                logger.warning(f"Crawl4AI failed for {url}: {result.error_message}")
                return {
                    'url': url,
                    'title': 'Failed to parse',
                    'description': '',
                    'content': '',
                    'word_count': 0,
                    'parsed_at': time.time(),
                    'status': 'error',
                    'error': result.error_message
                }
                
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            return {
                'url': url,
                'title': 'Failed to parse',
                'description': '',
                'content': '',
                'word_count': 0,
                'parsed_at': time.time(),
                'status': 'error',
                'error': str(e)
            }
    
    async def parse_multiple_urls(self, urls: List[str], max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """
        Parse multiple URLs with concurrency control using Crawl4AI.
        
        Args:
            urls: List of URLs to parse
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of parsed results
        """
        results = []
        
        # Process URLs in batches to avoid overwhelming servers
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i:i + max_concurrent]
            
            # Create tasks for concurrent processing
            tasks = [self.parse_url(url) for url in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Exception parsing {batch[j]}: {result}")
                    results.append({
                        'url': batch[j],
                        'title': 'Failed to parse',
                        'description': '',
                        'content': '',
                        'word_count': 0,
                        'parsed_at': time.time(),
                        'status': 'error',
                        'error': str(result)
                    })
                else:
                    results.append(result)
            
            # Be respectful to servers
            if i + max_concurrent < len(urls):
                await asyncio.sleep(1)
        
        return results
    
    async def close(self):
        """Close the crawler instance."""
        if self.crawler:
            await self.crawler.close()
            self.crawler = None

class EnhancedWebSearch:
    """Enhanced web search with Crawl4AI content parsing."""
    
    def __init__(self, searxng_client, parser: Optional[WebPageParser] = None):
        self.searxng = searxng_client
        self.parser = parser or WebPageParser()
    
    async def search_with_parsing(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search and parse the results using Crawl4AI for AI-ready content.
        
        Args:
            query: Search query
            num_results: Number of results to parse
            
        Returns:
            List of enhanced search results with parsed content
        """
        try:
            # Get search results from SearXNG
            search_results = self.searxng.search(query, num_results=num_results)
            
            if not search_results:
                return []
            
            # Extract URLs
            urls = [result.get('url') for result in search_results if result.get('url')]
            
            if not urls:
                return search_results
            
            # Parse the URLs using Crawl4AI
            parsed_results = await self.parser.parse_multiple_urls(urls)
            
            # Combine search results with parsed content
            enhanced_results = []
            for i, search_result in enumerate(search_results):
                if i < len(parsed_results):
                    parsed = parsed_results[i]
                    
                    enhanced_result = {
                        **search_result,
                        'parsed_title': parsed.get('title', search_result.get('title', '')),
                        'parsed_content': parsed.get('content', ''),
                        'parsed_description': parsed.get('description', ''),
                        'word_count': parsed.get('word_count', 0),
                        'parsing_status': parsed.get('status', 'unknown'),
                        'links': parsed.get('links', []),
                        'media': parsed.get('media', [])
                    }
                    
                    # Use parsed content if available and substantial
                    if parsed.get('content') and len(parsed['content']) > 100:
                        enhanced_result['content'] = parsed['content']
                    
                    enhanced_results.append(enhanced_result)
                else:
                    enhanced_results.append(search_result)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Enhanced search with parsing failed: {e}")
            return search_results or []
    
    async def close(self):
        """Close the parser instance."""
        await self.parser.close()
