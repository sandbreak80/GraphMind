"""SearXNG web search client for real-time market data and news."""
import logging
import requests
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)


class SearXNGClient:
    """High-performance SearXNG client for web search integration."""
    
    def __init__(self, base_url: str = "http://searxng:8080", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GraphMind-Research-Platform/2.0',
            'Accept': 'application/json',
            'X-Forwarded-For': '127.0.0.1',  # Required for SearXNG botdetection
            'X-Real-IP': '127.0.0.1'  # Required for SearXNG botdetection
        })
    
    def search(self, query: str, categories: List[str] = None, 
               engines: List[str] = None, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using SearXNG with JSON output."""
        try:
            params = {
                'q': query,
                'format': 'json',
                'pageno': 1,
                'results_on_new_tab': 1,
                'safesearch': 0,
                'time_range': None
            }
            
            if categories:
                params['categories'] = ','.join(categories)
            if engines:
                params['engines'] = ','.join(engines)
            
            response = self.session.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get('results', [])[:num_results]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'engine': result.get('engine', 'unknown'),
                    'parsed_url': result.get('parsed_url', []),
                    'template': result.get('template', ''),
                    'engines': result.get('engines', []),
                    'positions': result.get('positions', []),
                    'score': result.get('score', 0.0),
                    'category': result.get('category', 'general'),
                    'timestamp': datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"SearXNG search failed: {e}")
            return []
    
    async def search_async(self, query: str, categories: List[str] = None, 
                          engines: List[str] = None, num_results: int = 10) -> List[Dict[str, Any]]:
        """Async search using SearXNG."""
        try:
            params = {
                'q': query,
                'format': 'json',
                'pageno': 1,
                'results_on_new_tab': 1,
                'safesearch': 0,
                'time_range': None
            }
            
            if categories:
                params['categories'] = ','.join(categories)
            if engines:
                params['engines'] = ','.join(engines)
            
            headers = {
                'User-Agent': 'GraphMind-Research-Platform/2.0',
                'Accept': 'application/json',
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    results = []
                    for result in data.get('results', [])[:num_results]:
                        results.append({
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'content': result.get('content', ''),
                            'engine': result.get('engine', 'unknown'),
                            'parsed_url': result.get('parsed_url', []),
                            'template': result.get('template', ''),
                            'engines': result.get('engines', []),
                            'positions': result.get('positions', []),
                            'score': result.get('score', 0.0),
                            'category': result.get('category', 'general'),
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Async SearXNG search failed: {e}")
            return []
    
    def search_trading_news(self, symbol: str = "ES", timeframe: str = "today") -> List[Dict[str, Any]]:
        """Search for trading-specific news and market data."""
        queries = [
            f"{symbol} futures news {timeframe}",
            f"E-mini {symbol} market analysis {timeframe}",
            f"{symbol} trading news market update",
            f"futures market news {symbol} {timeframe}",
            f"{symbol} price action analysis {timeframe}",
            f"E-mini {symbol} technical analysis {timeframe}"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(
                query, 
                categories=['news', 'general'],
                engines=['google', 'bing', 'duckduckgo'],
                num_results=3
            )
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        return unique_results[:15]  # Limit to top 15
    
    def search_economic_events(self, date: str = "today") -> List[Dict[str, Any]]:
        """Search for economic events and calendar."""
        queries = [
            f"economic calendar {date}",
            f"Fed news {date}",
            f"market moving events {date}",
            f"trading calendar {date}",
            f"FOMC meeting {date}",
            f"inflation data {date}"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(
                query,
                categories=['news', 'general'],
                engines=['google', 'bing'],
                num_results=2
            )
            all_results.extend(results)
        
        return all_results[:10]
    
    def search_strategy_analysis(self, strategy_name: str) -> List[Dict[str, Any]]:
        """Search for additional strategy analysis and research."""
        queries = [
            f"{strategy_name} trading strategy analysis",
            f"{strategy_name} futures trading research",
            f"{strategy_name} quantitative trading",
            f"{strategy_name} algorithmic trading",
            f"{strategy_name} backtesting results",
            f"{strategy_name} trading performance"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(
                query,
                categories=['general'],
                engines=['google', 'bing', 'duckduckgo'],
                num_results=2
            )
            all_results.extend(results)
        
        return all_results[:8]
    
    def get_engines(self) -> List[Dict[str, Any]]:
        """Get available search engines from SearXNG."""
        try:
            response = self.session.get(f"{self.base_url}/engines", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get engines: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get SearXNG statistics."""
        try:
            # Test with a simple search to verify SearXNG is working
            response = self.session.get(
                f"{self.base_url}/search",
                params={'q': 'test', 'format': 'json'},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return {
                'status': 'connected',
                'engines_available': len(data.get('engines', [])),
                'results_count': len(data.get('results', []))
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


class EnhancedRAGWithSearXNG:
    """Enhanced RAG system with SearXNG web search integration."""
    
    def __init__(self, retriever, searxng_client: Optional[SearXNGClient] = None):
        self.retriever = retriever
        self.searxng = searxng_client
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes
    
    async def search_with_web_context(self, query: str, include_web: bool = True) -> Dict[str, Any]:
        """Enhanced search with web context for real-time information."""
        # Get document-based results
        doc_results = await self.retriever.retrieve_async(query, top_k=15)
        
        web_results = []
        if include_web and self.searxng:
            try:
                # Check cache first
                cache_key = f"web_{hash(query)}"
                if cache_key in self.cache:
                    cached_time, cached_results = self.cache[cache_key]
                    if time.time() - cached_time < self.cache_ttl:
                        web_results = cached_results
                    else:
                        del self.cache[cache_key]
                
                if not web_results:
                    # Extract potential trading symbols from query
                    symbols = self._extract_trading_symbols(query)
                    
                    # Search for relevant market news
                    for symbol in symbols:
                        news_results = self.searxng.search_trading_news(symbol)
                        web_results.extend(news_results)
                    
                    # Search for economic events
                    econ_results = self.searxng.search_economic_events()
                    web_results.extend(econ_results)
                    
                    # Search for strategy-specific analysis
                    strategy_results = self.searxng.search_strategy_analysis(query)
                    web_results.extend(strategy_results)
                    
                    # Cache results
                    self.cache[cache_key] = (time.time(), web_results)
                
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
        
        return {
            "document_results": doc_results,
            "web_results": web_results[:20],  # Limit web results
            "total_sources": len(doc_results) + len(web_results),
            "web_enabled": self.searxng is not None
        }
    
    def _extract_trading_symbols(self, query: str) -> List[str]:
        """Extract potential trading symbols from query."""
        symbols = []
        query_lower = query.lower()
        
        # Common Emini symbols
        if "es" in query_lower or "sp500" in query_lower or "s&p" in query_lower:
            symbols.append("ES")
        if "nq" in query_lower or "nasdaq" in query_lower:
            symbols.append("NQ")
        if "ym" in query_lower or "dow" in query_lower:
            symbols.append("YM")
        if "rt" in query_lower or "russell" in query_lower:
            symbols.append("RT")
        
        # Default to ES if no specific symbol found
        if not symbols:
            symbols = ["ES"]
        
        return symbols


def create_searxng_client(searxng_url: str = "http://localhost:8888") -> Optional[SearXNGClient]:
    """Create SearXNG client if available with retry logic."""
    import time
    
    # Retry up to 3 times with increasing timeout
    for attempt in range(3):
        try:
            timeout = 5 + (attempt * 5)  # 5s, 10s, 15s
            logger.info(f"Attempting to connect to SearXNG (attempt {attempt+1}/3, timeout={timeout}s)...")
            
            client = SearXNGClient(searxng_url, timeout=timeout)
            
            # Simple connectivity test instead of stats
            test_response = requests.get(
                f"{searxng_url}/search?q=test&format=json",
                timeout=timeout,
                headers={
                    'X-Forwarded-For': '127.0.0.1',
                    'X-Real-IP': '127.0.0.1'
                }
            )
            
            if test_response.status_code == 200:
                logger.info(f"✅ SearXNG client connected to {searxng_url} on attempt {attempt+1}")
                return client
            else:
                logger.warning(f"SearXNG returned status {test_response.status_code}, retrying...")
                time.sleep(2)
                
        except Exception as e:
            logger.warning(f"SearXNG attempt {attempt+1} failed: {e}")
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(3)
    
    logger.error(f"❌ SearXNG not available at {searxng_url} after 3 attempts")
    return None