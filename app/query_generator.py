"""
Intelligent Query Generator for Web Search
Uses LLM to analyze user prompts and generate targeted search queries
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """Represents a generated search query with metadata."""
    query: str
    intent: str
    entities: List[str]
    search_type: str  # 'news', 'analysis', 'data', 'general'
    priority: int  # 1-5, higher is more important
    context: str

class IntelligentQueryGenerator:
    """Uses LLM to generate intelligent search queries from user prompts."""
    
    def __init__(self, ollama_base_url: str = "http://ollama:11434"):
        self.ollama_base_url = ollama_base_url
        self.model = "qwen2.5-coder:14b"  # Use the same model as the main system
    
    def generate_search_queries(self, user_prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> List[SearchQuery]:
        """
        Generate intelligent search queries from user prompt using LLM analysis.
        
        Args:
            user_prompt: The user's question/prompt
            conversation_history: Previous conversation context
            
        Returns:
            List of SearchQuery objects with generated queries
        """
        try:
            # Prepare context for the LLM
            context = self._prepare_context(user_prompt, conversation_history)
            
            # Generate queries using LLM
            llm_response = self._call_llm_for_query_generation(context)
            
            # Parse and validate the response
            search_queries = self._parse_llm_response(llm_response)
            
            # Add fallback queries if LLM didn't generate enough
            if len(search_queries) < 3:
                search_queries.extend(self._generate_fallback_queries(user_prompt))
            
            # Sort by priority
            search_queries.sort(key=lambda x: x.priority, reverse=True)
            
            logger.info(f"Generated {len(search_queries)} search queries for prompt: {user_prompt[:100]}...")
            return search_queries
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            # Return fallback queries
            return self._generate_fallback_queries(user_prompt)
    
    def _prepare_context(self, user_prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Prepare context for the LLM including conversation history."""
        context_parts = [
            f"User Prompt: {user_prompt}",
            "",
            "Your task is to generate 3-5 targeted search queries that will help find relevant information to answer this question.",
            "Consider the following:",
            "- Trading symbols and market instruments mentioned",
            "- Time periods (today, this week, this month, etc.)",
            "- Specific concepts or strategies mentioned",
            "- Market conditions or events referenced",
            "- Technical analysis terms",
            "- Economic indicators or news",
            "",
            "Generate queries that will find:",
            "1. Recent news and market updates",
            "2. Technical analysis and charts",
            "3. Economic data and indicators",
            "4. Trading strategies and methodologies",
            "5. Market commentary and expert opinions",
            ""
        ]
        
        if conversation_history:
            context_parts.append("Previous conversation context:")
            for msg in conversation_history[-3:]:  # Last 3 messages for context
                context_parts.append(f"- {msg['role']}: {msg['content'][:200]}...")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _call_llm_for_query_generation(self, context: str) -> str:
        """Call the LLM to generate search queries."""
        prompt = f"""You are an expert trading analyst and search specialist. Analyze the user's question and generate 3-5 targeted search queries that will help find the most relevant information.

{context}

Generate queries that are:
- Specific and targeted
- Include relevant trading symbols (ES, NQ, YM, etc.)
- Include time references when appropriate
- Cover different aspects (news, analysis, data, strategies)
- Use natural language that search engines understand

Return your response as a JSON array with this exact format:
[
  {{
    "query": "specific search query here",
    "intent": "what this query is trying to find",
    "entities": ["symbol1", "symbol2", "concept1"],
    "search_type": "news|analysis|data|general",
    "priority": 1-5,
    "context": "why this query is relevant"
  }}
]

Make sure the JSON is valid and properly formatted."""

        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent results
                        "num_predict": 1000,
                        "top_p": 0.9,
                        "stop": ["Human:", "User:", "Question:"]
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _parse_llm_response(self, llm_response: str) -> List[SearchQuery]:
        """Parse the LLM response and create SearchQuery objects."""
        try:
            # Extract JSON from the response
            json_start = llm_response.find('[')
            json_end = llm_response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = llm_response[json_start:json_end]
            queries_data = json.loads(json_str)
            
            search_queries = []
            for query_data in queries_data:
                search_query = SearchQuery(
                    query=query_data.get('query', ''),
                    intent=query_data.get('intent', ''),
                    entities=query_data.get('entities', []),
                    search_type=query_data.get('search_type', 'general'),
                    priority=query_data.get('priority', 3),
                    context=query_data.get('context', '')
                )
                search_queries.append(search_query)
            
            return search_queries
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.debug(f"LLM response: {llm_response}")
            raise
    
    def _generate_fallback_queries(self, user_prompt: str) -> List[SearchQuery]:
        """Generate fallback queries when LLM fails."""
        # Extract basic entities
        entities = self._extract_basic_entities(user_prompt)
        
        fallback_queries = [
            SearchQuery(
                query=f"{user_prompt} trading analysis",
                intent="Find trading analysis related to the prompt",
                entities=entities,
                search_type="analysis",
                priority=3,
                context="General trading analysis search"
            ),
            SearchQuery(
                query=f"{user_prompt} market news",
                intent="Find recent market news",
                entities=entities,
                search_type="news",
                priority=2,
                context="Market news search"
            ),
            SearchQuery(
                query=f"{user_prompt} futures trading",
                intent="Find futures trading information",
                entities=entities,
                search_type="general",
                priority=1,
                context="Futures trading context"
            )
        ]
        
        return fallback_queries
    
    def _extract_basic_entities(self, text: str) -> List[str]:
        """Extract basic entities from text."""
        entities = []
        text_lower = text.lower()
        
        # Common trading symbols
        if "es" in text_lower or "sp500" in text_lower or "s&p" in text_lower:
            entities.append("ES")
        if "nq" in text_lower or "nasdaq" in text_lower:
            entities.append("NQ")
        if "ym" in text_lower or "dow" in text_lower:
            entities.append("YM")
        if "rty" in text_lower or "russell" in text_lower:
            entities.append("RTY")
        
        # Time references
        if "today" in text_lower:
            entities.append("today")
        if "week" in text_lower:
            entities.append("this week")
        if "month" in text_lower:
            entities.append("this month")
        
        return entities

class EnhancedWebSearch:
    """Enhanced web search with intelligent query generation."""
    
    def __init__(self, searxng_client, query_generator: IntelligentQueryGenerator):
        self.searxng = searxng_client
        self.query_generator = query_generator
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def search_with_intelligent_queries(self, user_prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None, 
                                    web_search_results: Optional[int] = None, web_pages_to_parse: Optional[int] = None) -> Dict[str, Any]:
        """
        Perform web search using LLM-generated intelligent queries.
        
        Args:
            user_prompt: The user's question/prompt
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with search results organized by query type
        """
        try:
            # Generate intelligent search queries
            search_queries = self.query_generator.generate_search_queries(user_prompt, conversation_history)
            
            # Perform searches for each query
            all_results = []
            query_results = {}
            
            for search_query in search_queries:
                try:
                    # Search using the generated query
                    num_results = web_search_results if web_search_results is not None else 5
                    results = self.searxng.search(
                        search_query.query,
                        categories=['news', 'general'],
                        engines=['google', 'bing', 'duckduckgo'],
                        num_results=num_results
                    )
                    
                    # Add metadata to results
                    for result in results:
                        result['generated_query'] = search_query.query
                        result['search_intent'] = search_query.intent
                        result['search_type'] = search_query.search_type
                        result['priority'] = search_query.priority
                        result['entities'] = search_query.entities
                    
                    all_results.extend(results)
                    query_results[search_query.query] = results
                    
                    logger.info(f"Search query '{search_query.query}' returned {len(results)} results")
                    
                except Exception as e:
                    logger.warning(f"Search failed for query '{search_query.query}': {e}")
                    continue
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_results = []
            for result in all_results:
                if result.get('url') not in seen_urls:
                    seen_urls.add(result.get('url'))
                    unique_results.append(result)
            
            # Sort by priority and relevance
            unique_results.sort(key=lambda x: (x.get('priority', 1), x.get('score', 0)), reverse=True)
            
            return {
                'results': unique_results[:20],  # Limit to top 20 results
                'query_results': query_results,
                'total_queries': len(search_queries),
                'successful_queries': len(query_results),
                'generated_queries': [sq.query for sq in search_queries],
                'entities_found': list(set([entity for sq in search_queries for entity in sq.entities]))
            }
            
        except Exception as e:
            logger.error(f"Enhanced web search failed: {e}")
            return {
                'results': [],
                'query_results': {},
                'total_queries': 0,
                'successful_queries': 0,
                'generated_queries': [],
                'entities_found': [],
                'error': str(e)
            }
