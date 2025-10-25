# GraphMind Core Retrieval System
# Domain-agnostic hybrid retrieval implementation

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

# Import existing retrieval components
from app.retrieval import HybridRetriever as TradingHybridRetriever
from app.advanced_retrieval import AdvancedHybridRetriever
from app.query_analyzer import QueryAnalyzer
from app.query_expansion import QueryExpansion
from app.context_compression import ContextCompression
from app.metadata_enhancement import MetadataEnhancement

logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Domain-agnostic hybrid retrieval system for GraphMind.
    
    This class provides a clean interface for hybrid retrieval that can be
    used across any domain without trading-specific terminology or logic.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the hybrid retriever with configuration."""
        self.config = config or {}
        self.trading_retriever = None
        self.advanced_retriever = None
        self.query_analyzer = None
        self.query_expansion = None
        self.context_compression = None
        self.metadata_enhancement = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all retrieval components."""
        try:
            # Initialize core retriever
            self.trading_retriever = TradingHybridRetriever()
            
            # Initialize advanced components
            self.query_analyzer = QueryAnalyzer()
            self.query_expansion = QueryExpansion()
            self.context_compression = ContextCompression()
            self.metadata_enhancement = MetadataEnhancement()
            
            logger.info("GraphMind hybrid retriever initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GraphMind retriever: {e}")
            raise
    
    async def retrieve_async(
        self, 
        query: str, 
        top_k: int = 5,
        domain: str = "generic",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using hybrid search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            domain: Domain context for retrieval
            **kwargs: Additional parameters
            
        Returns:
            List of retrieved documents with metadata
        """
        try:
            # Analyze query for domain-specific optimization
            if self.query_analyzer:
                query_analysis = await self.query_analyzer.analyze_query(query, domain)
                query = query_analysis.get('optimized_query', query)
            
            # Expand query for better retrieval
            if self.query_expansion:
                expanded_queries = await self.query_expansion.expand_query(query, domain)
                # Use expanded queries for retrieval
                all_results = []
                for expanded_query in expanded_queries:
                    results = await self.trading_retriever.retrieve_async(
                        expanded_query, 
                        top_k=top_k,
                        **kwargs
                    )
                    all_results.extend(results)
                
                # Deduplicate and rank results
                unique_results = self._deduplicate_results(all_results)
                return unique_results[:top_k]
            
            # Standard retrieval
            results = await self.trading_retriever.retrieve_async(
                query, 
                top_k=top_k,
                **kwargs
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on document ID."""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            doc_id = result.get('metadata', {}).get('doc_id')
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_results.append(result)
        
        return unique_results
    
    async def get_context(
        self, 
        query: str, 
        domain: str = "generic",
        max_tokens: int = 4000
    ) -> str:
        """
        Get context for a query with domain-specific optimization.
        
        Args:
            query: Search query
            domain: Domain context
            max_tokens: Maximum context tokens
            
        Returns:
            Formatted context string
        """
        try:
            # Retrieve documents
            results = await self.retrieve_async(query, top_k=10, domain=domain)
            
            if not results:
                return "No relevant documents found."
            
            # Compress context if needed
            if self.context_compression:
                context = await self.context_compression.compress_context(
                    results, 
                    max_tokens=max_tokens,
                    domain=domain
                )
            else:
                # Basic context formatting
                context_parts = []
                for i, result in enumerate(results[:5], 1):
                    text = result.get('text', '')
                    metadata = result.get('metadata', {})
                    source = metadata.get('file_name', 'Unknown')
                    
                    context_parts.append(f"Source {i} ({source}):\n{text}\n")
                
                context = "\n".join(context_parts)
            
            return context
            
        except Exception as e:
            logger.error(f"Context generation failed: {e}")
            return "Error generating context."
    
    async def get_citations(
        self, 
        query: str, 
        domain: str = "generic",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get citations for a query.
        
        Args:
            query: Search query
            domain: Domain context
            top_k: Number of citations
            
        Returns:
            List of citation objects
        """
        try:
            results = await self.retrieve_async(query, top_k=top_k, domain=domain)
            
            citations = []
            for result in results:
                metadata = result.get('metadata', {})
                doc_type = metadata.get('doc_type', 'Document')
                file_name = metadata.get('file_name', 'Unknown')
                
                # Format source based on document type
                if doc_type == 'video_transcript':
                    source_display = f"Video: {file_name}"
                elif doc_type == 'pdf':
                    source_display = f"PDF: {file_name}"
                elif doc_type == 'text_document':
                    source_display = f"Document: {file_name}"
                elif doc_type == 'llm_processed':
                    source_display = f"AI Processed: {file_name}"
                else:
                    source_display = f"{doc_type.title()}: {file_name}"
                
                citations.append({
                    'text': result.get('text', '')[:200] + "...",
                    'doc_id': metadata.get('doc_id', 'unknown'),
                    'page': metadata.get('page'),
                    'section': source_display,
                    'score': result.get('rerank_score', 0.0)
                })
            
            return citations
            
        except Exception as e:
            logger.error(f"Citation generation failed: {e}")
            return []
    
    async def search_with_filters(
        self,
        query: str,
        domain: str = "generic",
        doc_types: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search with domain-specific filters.
        
        Args:
            query: Search query
            domain: Domain context
            doc_types: Filter by document types
            date_range: Filter by date range
            **kwargs: Additional filters
            
        Returns:
            Filtered search results
        """
        try:
            # Get base results
            results = await self.retrieve_async(query, domain=domain, **kwargs)
            
            # Apply filters
            filtered_results = []
            for result in results:
                metadata = result.get('metadata', {})
                
                # Filter by document type
                if doc_types:
                    doc_type = metadata.get('doc_type', '')
                    if doc_type not in doc_types:
                        continue
                
                # Filter by date range
                if date_range:
                    doc_date = metadata.get('date', '')
                    if doc_date:
                        # Implement date filtering logic here
                        pass
                
                filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Filtered search failed: {e}")
            return []
