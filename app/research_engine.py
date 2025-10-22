"""
Advanced Research Engine for Comprehensive Information Retrieval
Handles any type of research query, not just trading-focused searches
"""

import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from app.ollama_client import OllamaClient
from app.config import RESEARCH_LLM_MODEL, RESEARCH_TEMPERATURE, MAX_TOKENS

logger = logging.getLogger(__name__)

@dataclass
class ResearchQuery:
    """Represents a research query with metadata."""
    query: str
    search_type: str  # 'company', 'financial', 'news', 'technical', 'competitive'
    priority: int
    context: str

class AdvancedResearchEngine:
    """Advanced research engine that can handle any type of query."""
    
    def __init__(self, searxng_client, query_generator, ollama_client=None):
        self.searxng = searxng_client
        self.query_generator = query_generator
        self.ollama = ollama_client or OllamaClient(default_model=RESEARCH_LLM_MODEL)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def conduct_research(self, user_query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive research on any topic.
        
        Args:
            user_query: The user's research question
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with comprehensive research results
        """
        try:
            # Generate intelligent research queries
            research_queries = self._generate_research_queries(user_query, conversation_history)
            
            # Perform comprehensive searches
            all_results = []
            search_metadata = {
                "total_queries": len(research_queries),
                "successful_queries": 0,
                "search_types": [],
                "sources_found": 0
            }
            
            for research_query in research_queries:
                try:
                    # Perform search based on query type
                    results = self._perform_research_search(research_query)
                    all_results.extend(results)
                    search_metadata["successful_queries"] += 1
                    search_metadata["search_types"].append(research_query.search_type)
                    search_metadata["sources_found"] += len(results)
                    
                    logger.info(f"Research query '{research_query.query}' returned {len(results)} results")
                    
                except Exception as e:
                    logger.warning(f"Research search failed for query '{research_query.query}': {e}")
                    continue
            
            # Remove duplicates and rank results
            unique_results = self._deduplicate_and_rank(all_results)
            
            return {
                'results': unique_results[:30],  # Top 30 results
                'search_metadata': search_metadata,
                'research_queries': [rq.query for rq in research_queries],
                'total_sources': len(unique_results)
            }
            
        except Exception as e:
            logger.error(f"Research engine failed: {e}")
            return {
                'results': [],
                'search_metadata': {'error': str(e)},
                'research_queries': [],
                'total_sources': 0
            }
    
    def _generate_research_queries(self, user_query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> List[ResearchQuery]:
        """Generate comprehensive research queries for any topic."""
        
        # Analyze the query to determine research approach
        query_lower = user_query.lower()
        
        research_queries = []
        
        # Company/Financial Research
        if any(word in query_lower for word in ['company', 'corporation', 'business', 'financial', 'revenue', 'market cap', 'stock', 'earnings']):
            research_queries.extend(self._generate_company_queries(user_query))
        
        # News and Current Events
        if any(word in query_lower for word in ['news', 'recent', 'latest', 'update', 'announcement', 'development']):
            research_queries.extend(self._generate_news_queries(user_query))
        
        # Technical Analysis
        if any(word in query_lower for word in ['technology', 'technical', 'infrastructure', 'platform', 'software', 'system']):
            research_queries.extend(self._generate_technical_queries(user_query))
        
        # Competitive Analysis
        if any(word in query_lower for word in ['competitor', 'competition', 'market share', 'competitive', 'vs', 'versus']):
            research_queries.extend(self._generate_competitive_queries(user_query))
        
        # General Research (fallback)
        if not research_queries:
            research_queries.extend(self._generate_general_queries(user_query))
        
        # Add some general queries regardless
        research_queries.extend(self._generate_general_queries(user_query))
        
        # Remove duplicates and sort by priority
        unique_queries = []
        seen_queries = set()
        for rq in research_queries:
            if rq.query not in seen_queries:
                unique_queries.append(rq)
                seen_queries.add(rq.query)
        
        unique_queries.sort(key=lambda x: x.priority, reverse=True)
        return unique_queries[:8]  # Limit to 8 queries
    
    def _generate_company_queries(self, user_query: str) -> List[ResearchQuery]:
        """Generate company-specific research queries."""
        queries = []
        
        # Extract company name if possible
        company_name = self._extract_company_name(user_query)
        
        if company_name:
            queries.extend([
                ResearchQuery(
                    query=f"{company_name} company overview financial performance",
                    search_type="company",
                    priority=5,
                    context="Company financial overview and performance metrics"
                ),
                ResearchQuery(
                    query=f"{company_name} revenue earnings market cap stock price",
                    search_type="financial",
                    priority=4,
                    context="Financial data and stock performance"
                ),
                ResearchQuery(
                    query=f"{company_name} products services offerings",
                    search_type="company",
                    priority=3,
                    context="Company products and services"
                ),
                ResearchQuery(
                    query=f"{company_name} recent news developments 2024",
                    search_type="news",
                    priority=2,
                    context="Recent company news and developments"
                )
            ])
        
        return queries
    
    def _generate_news_queries(self, user_query: str) -> List[ResearchQuery]:
        """Generate news-focused research queries."""
        company_name = self._extract_company_name(user_query)
        
        queries = []
        if company_name:
            queries.extend([
                ResearchQuery(
                    query=f"{company_name} latest news 2024",
                    search_type="news",
                    priority=5,
                    context="Latest news and developments"
                ),
                ResearchQuery(
                    query=f"{company_name} recent announcements press releases",
                    search_type="news",
                    priority=4,
                    context="Recent company announcements"
                ),
                ResearchQuery(
                    query=f"{company_name} industry news market updates",
                    search_type="news",
                    priority=3,
                    context="Industry-related news and market updates"
                )
            ])
        
        return queries
    
    def _generate_technical_queries(self, user_query: str) -> List[ResearchQuery]:
        """Generate technology-focused research queries."""
        company_name = self._extract_company_name(user_query)
        
        queries = []
        if company_name:
            queries.extend([
                ResearchQuery(
                    query=f"{company_name} technology infrastructure platform",
                    search_type="technical",
                    priority=5,
                    context="Technology infrastructure and platform details"
                ),
                ResearchQuery(
                    query=f"{company_name} AI artificial intelligence machine learning",
                    search_type="technical",
                    priority=4,
                    context="AI and machine learning capabilities"
                ),
                ResearchQuery(
                    query=f"{company_name} cloud computing software architecture",
                    search_type="technical",
                    priority=3,
                    context="Cloud computing and software architecture"
                )
            ])
        
        return queries
    
    def _generate_competitive_queries(self, user_query: str) -> List[ResearchQuery]:
        """Generate competitive analysis queries."""
        company_name = self._extract_company_name(user_query)
        
        queries = []
        if company_name:
            queries.extend([
                ResearchQuery(
                    query=f"{company_name} competitors market share",
                    search_type="competitive",
                    priority=5,
                    context="Competitive landscape and market share"
                ),
                ResearchQuery(
                    query=f"{company_name} vs competitors comparison",
                    search_type="competitive",
                    priority=4,
                    context="Direct competitor comparison"
                ),
                ResearchQuery(
                    query=f"{company_name} industry analysis market position",
                    search_type="competitive",
                    priority=3,
                    context="Industry analysis and market position"
                )
            ])
        
        return queries
    
    def _generate_general_queries(self, user_query: str) -> List[ResearchQuery]:
        """Generate general research queries."""
        return [
            ResearchQuery(
                query=user_query,
                search_type="general",
                priority=3,
                context="General research query"
            ),
            ResearchQuery(
                query=f"{user_query} analysis report",
                search_type="general",
                priority=2,
                context="Analysis and reporting"
            ),
            ResearchQuery(
                query=f"{user_query} comprehensive overview",
                search_type="general",
                priority=1,
                context="Comprehensive overview"
            )
        ]
    
    def _extract_company_name(self, user_query: str) -> Optional[str]:
        """Extract company name from user query."""
        # Simple extraction - look for common company indicators
        query_lower = user_query.lower()
        
        # Look for "on [Company]" pattern
        if " on " in query_lower:
            parts = query_lower.split(" on ")
            if len(parts) > 1:
                company_part = parts[1].split()[0]
                return company_part.title()
        
        # Look for company names in the query
        common_companies = [
            'intuit', 'microsoft', 'google', 'apple', 'amazon', 'meta', 'tesla',
            'netflix', 'nvidia', 'salesforce', 'adobe', 'oracle', 'ibm'
        ]
        
        for company in common_companies:
            if company in query_lower:
                return company.title()
        
        return None
    
    def _perform_research_search(self, research_query: ResearchQuery) -> List[Dict[str, Any]]:
        """Perform search based on research query type."""
        try:
            # Use SearXNG for web search
            results = self.searxng.search(
                research_query.query,
                categories=['news', 'general'],
                engines=['google', 'bing', 'duckduckgo'],
                num_results=5
            )
            
            # Add metadata to results
            for result in results:
                result['research_type'] = research_query.search_type
                result['research_priority'] = research_query.priority
                result['research_context'] = research_query.context
                result['search_timestamp'] = time.time()
            
            return results
            
        except Exception as e:
            logger.warning(f"Research search failed: {e}")
            return []
    
    def _deduplicate_and_rank(self, all_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank results by relevance."""
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # Sort by priority and score
        unique_results.sort(
            key=lambda x: (x.get('research_priority', 1), x.get('score', 0)), 
            reverse=True
        )
        
        return unique_results
    
    def generate_research_response(self, user_query: str, research_data: Dict[str, Any], conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a high-quality research response using the research-specific LLM.
        
        Args:
            user_query: The user's research question
            research_data: Comprehensive research data from web and documents
            conversation_history: Previous conversation context
            
        Returns:
            High-quality research response
        """
        try:
            # Prepare context from research data
            doc_context = "\n".join([r.get('text', '') for r in research_data.get('document_results', [])])
            web_context = "\n".join([r.get('content', r.get('title', '')) for r in research_data.get('web_results', [])])
            
            # Prepare conversation context
            conversation_context = ""
            if conversation_history:
                recent_context = conversation_history[-3:]  # Last 3 messages
                conversation_context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in recent_context
                ])
            
            # Create simple prompt with just the data
            prompt = f"""RESEARCH QUESTION: {user_query}

DOCUMENT CONTEXT:
{doc_context}

WEB RESEARCH DATA:
{web_context}

{conversation_context}"""

            # Generate response using research-optimized LLM
            response = self.ollama.generate(
                prompt=prompt,
                model=RESEARCH_LLM_MODEL,
                temperature=RESEARCH_TEMPERATURE,
                max_tokens=MAX_TOKENS,
                timeout=300
            )
            
            logger.info(f"Generated research response using {RESEARCH_LLM_MODEL}")
            return response
            
        except Exception as e:
            logger.error(f"Research response generation failed: {e}")
            return f"I apologize, but I encountered an error while generating the research response. The research data was collected successfully, but the analysis could not be completed. Error: {str(e)}"

class ComprehensiveResearchSystem:
    """Comprehensive research system that combines multiple sources."""
    
    def __init__(self, retriever, searxng_client, query_generator):
        self.retriever = retriever
        self.research_engine = AdvancedResearchEngine(searxng_client, query_generator)
    
    def conduct_comprehensive_research(self, user_query: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive research combining document retrieval and web search.
        
        Args:
            user_query: The user's research question
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with comprehensive research results
        """
        try:
            # Get document-based results
            doc_results = self.retriever.retrieve(user_query, top_k=10)
            
            # Conduct web research
            web_research = self.research_engine.conduct_research(user_query, conversation_history)
            
            # Combine results
            combined_results = {
                'document_results': doc_results,
                'web_results': web_research['results'],
                'total_sources': len(doc_results) + len(web_research['results']),
                'research_metadata': web_research['search_metadata'],
                'research_queries': web_research['research_queries']
            }
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Comprehensive research failed: {e}")
            return {
                'document_results': [],
                'web_results': [],
                'total_sources': 0,
                'research_metadata': {'error': str(e)},
                'research_queries': []
            }
