"""Web search integration for real-time market data and news."""
import logging
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class WebSearchProvider:
    """Base class for web search providers."""
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web and return results."""
        raise NotImplementedError


class SerperWebSearch(WebSearchProvider):
    """Serper.dev web search provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search using Serper.dev API."""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results,
                "gl": "us",  # Country
                "hl": "en",  # Language
                "safe": "off"
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": "web_search",
                    "timestamp": datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []


class TradingNewsSearch:
    """Specialized trading news and market data search."""
    
    def __init__(self, web_search_provider: WebSearchProvider):
        self.web_search = web_search_provider
    
    def search_market_news(self, symbol: str = "ES", timeframe: str = "today") -> List[Dict[str, Any]]:
        """Search for market news related to specific symbols."""
        queries = [
            f"{symbol} futures news {timeframe}",
            f"E-mini {symbol} market analysis {timeframe}",
            f"{symbol} trading news market update",
            f"futures market news {symbol} {timeframe}"
        ]
        
        all_results = []
        for query in queries:
            results = self.web_search.search(query, num_results=3)
            all_results.extend(results)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        return unique_results[:10]  # Limit to top 10
    
    def search_economic_events(self, date: str = "today") -> List[Dict[str, Any]]:
        """Search for economic events and calendar."""
        queries = [
            f"economic calendar {date}",
            f"Fed news {date}",
            f"market moving events {date}",
            f"trading calendar {date}"
        ]
        
        all_results = []
        for query in queries:
            results = self.web_search.search(query, num_results=2)
            all_results.extend(results)
        
        return all_results[:8]
    
    def search_strategy_analysis(self, strategy_name: str) -> List[Dict[str, Any]]:
        """Search for additional strategy analysis and research."""
        queries = [
            f"{strategy_name} trading strategy analysis",
            f"{strategy_name} futures trading research",
            f"{strategy_name} quantitative trading",
            f"{strategy_name} algorithmic trading"
        ]
        
        all_results = []
        for query in queries:
            results = self.web_search.search(query, num_results=2)
            all_results.extend(results)
        
        return all_results[:6]


class EnhancedRAGWithWebSearch:
    """Enhanced RAG system with web search integration."""
    
    def __init__(self, retriever, web_search_provider: Optional[WebSearchProvider] = None):
        self.retriever = retriever
        self.web_search = web_search_provider
        self.trading_news = TradingNewsSearch(web_search_provider) if web_search_provider else None
    
    def search_with_web_context(self, query: str, include_web: bool = True) -> Dict[str, Any]:
        """Enhanced search with web context for real-time information."""
        # Get document-based results
        doc_results = self.retriever.retrieve(query, top_k=10)
        
        web_results = []
        if include_web and self.trading_news:
            try:
                # Extract potential trading symbols from query
                symbols = self._extract_trading_symbols(query)
                
                # Search for relevant market news
                for symbol in symbols:
                    news_results = self.trading_news.search_market_news(symbol)
                    web_results.extend(news_results)
                
                # Search for economic events
                econ_results = self.trading_news.search_economic_events()
                web_results.extend(econ_results)
                
                # Search for strategy-specific analysis
                strategy_results = self.trading_news.search_strategy_analysis(query)
                web_results.extend(strategy_results)
                
            except Exception as e:
                logger.warning(f"Web search failed: {e}")
        
        return {
            "document_results": doc_results,
            "web_results": web_results[:15],  # Limit web results
            "total_sources": len(doc_results) + len(web_results)
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


def create_web_search_provider() -> Optional[WebSearchProvider]:
    """Create web search provider based on available API keys."""
    serper_key = os.getenv("SERPER_API_KEY")
    
    if serper_key:
        return SerperWebSearch(serper_key)
    
    logger.warning("No web search API key found. Web search disabled.")
    return None