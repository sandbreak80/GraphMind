# GraphMind RAG System
# Domain-agnostic RAG system for GraphMind

import logging
from typing import Dict, List, Any, Optional
import asyncio
from pathlib import Path

from .retrieval import HybridRetriever
from .embeddings import EmbeddingService
from .reranking import RerankingService
from ..adapters.domain_registry import DomainRegistry
from ..connectors.connector_registry import ConnectorRegistry

logger = logging.getLogger(__name__)

class GraphMindRAGSystem:
    """
    Domain-agnostic RAG system for GraphMind.
    
    This class provides the main interface for the GraphMind RAG framework,
    integrating domain adapters, connectors, and retrieval components.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the GraphMind RAG system."""
        self.config = config
        self.domain_registry = DomainRegistry()
        self.connector_registry = ConnectorRegistry()
        self.retriever = None
        self.embedding_service = None
        self.reranking_service = None
        self.current_domain = None
        self.current_adapter = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize RAG system components."""
        try:
            # Initialize retrieval components
            self.retriever = HybridRetriever(self.config.get('retrieval', {}))
            self.embedding_service = EmbeddingService(
                self.config.get('embedding_model', 'BAAI/bge-m3'),
                self.config.get('embedding', {})
            )
            self.reranking_service = RerankingService(
                self.config.get('reranking_model', 'BAAI/bge-reranker-large'),
                self.config.get('reranking', {})
            )
            
            # Initialize connectors
            self._initialize_connectors()
            
            logger.info("GraphMind RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GraphMind RAG system: {e}")
            raise
    
    def _initialize_connectors(self):
        """Initialize data connectors."""
        try:
            connector_configs = self.config.get('connectors', {})
            
            for connector_name, connector_config in connector_configs.items():
                connector = self.connector_registry.create_connector(
                    connector_name, 
                    connector_config
                )
                if connector:
                    logger.info(f"Initialized connector: {connector_name}")
                else:
                    logger.warning(f"Failed to initialize connector: {connector_name}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize connectors: {e}")
    
    async def set_domain(self, domain: str) -> bool:
        """
        Set the current domain for RAG operations.
        
        Args:
            domain: Domain name
            
        Returns:
            True if domain set successfully, False otherwise
        """
        try:
            # Get domain adapter
            adapter = self.domain_registry.get_adapter(domain)
            if not adapter:
                # Create adapter if it doesn't exist
                adapter = self.domain_registry.create_adapter(domain)
                if not adapter:
                    logger.error(f"Failed to create adapter for domain: {domain}")
                    return False
            
            self.current_domain = domain
            self.current_adapter = adapter
            
            logger.info(f"Set domain to: {domain}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set domain {domain}: {e}")
            return False
    
    async def search(
        self, 
        query: str, 
        domain: Optional[str] = None,
        top_k: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search across all available sources.
        
        Args:
            query: Search query
            domain: Domain context (optional)
            top_k: Number of results to return
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        try:
            # Set domain if provided
            if domain and domain != self.current_domain:
                await self.set_domain(domain)
            
            if not self.current_adapter:
                logger.error("No domain adapter set")
                return []
            
            # Get required connectors for current domain
            required_connectors = self.current_adapter.get_connectors()
            optional_connectors = self.current_adapter.get_optional_connectors()
            
            # Search across all connectors
            all_results = []
            
            for connector_name in required_connectors + optional_connectors:
                connector = self.connector_registry.get_connector(connector_name)
                if connector and connector.enabled:
                    try:
                        results = await connector.search(query, **kwargs)
                        all_results.extend(results)
                    except Exception as e:
                        logger.error(f"Search failed for connector {connector_name}: {e}")
                        continue
            
            if not all_results:
                logger.warning("No results found from any connector")
                return []
            
            # Process results with domain adapter
            processed_results = self.current_adapter.process_sources(all_results)
            
            # Rerank results
            if self.reranking_service:
                reranked_results = self.reranking_service.rerank_documents(
                    query, 
                    processed_results, 
                    top_k=top_k,
                    domain=self.current_domain
                )
            else:
                reranked_results = processed_results[:top_k]
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_context(
        self, 
        query: str, 
        domain: Optional[str] = None,
        max_tokens: int = 4000
    ) -> str:
        """
        Get context for a query.
        
        Args:
            query: Search query
            domain: Domain context (optional)
            max_tokens: Maximum context tokens
            
        Returns:
            Formatted context string
        """
        try:
            # Set domain if provided
            if domain and domain != self.current_domain:
                await self.set_domain(domain)
            
            if not self.current_adapter:
                logger.error("No domain adapter set")
                return "No domain adapter available."
            
            # Get search results
            results = await self.search(query, top_k=10)
            
            if not results:
                return "No relevant documents found."
            
            # Get context using retriever
            context = await self.retriever.get_context(
                query, 
                domain=self.current_domain,
                max_tokens=max_tokens
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Context generation failed: {e}")
            return "Error generating context."
    
    async def get_citations(
        self, 
        query: str, 
        domain: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get citations for a query.
        
        Args:
            query: Search query
            domain: Domain context (optional)
            top_k: Number of citations
            
        Returns:
            List of citation objects
        """
        try:
            # Set domain if provided
            if domain and domain != self.current_domain:
                await self.set_domain(domain)
            
            if not self.current_adapter:
                logger.error("No domain adapter set")
                return []
            
            # Get search results
            results = await self.search(query, top_k=top_k)
            
            if not results:
                return []
            
            # Format citations
            citations = []
            for result in results:
                metadata = result.get('metadata', {})
                doc_type = metadata.get('doc_type', 'Document')
                file_name = metadata.get('file_name', 'Unknown')
                source = metadata.get('source', 'unknown')
                
                # Format source display based on type
                if doc_type == 'pdf':
                    source_display = f"PDF: {file_name}"
                elif doc_type == 'obsidian_note':
                    source_display = f"Obsidian: {file_name}"
                elif doc_type == 'web_result':
                    source_display = f"Web: {file_name}"
                elif doc_type == 'database_record':
                    source_display = f"Database: {file_name}"
                else:
                    source_display = f"{doc_type.title()}: {file_name}"
                
                citations.append({
                    'text': result.get('text', '')[:200] + "...",
                    'doc_id': metadata.get('doc_id', 'unknown'),
                    'page': metadata.get('page'),
                    'section': source_display,
                    'score': result.get('rerank_score', 0.0),
                    'source': source
                })
            
            return citations
            
        except Exception as e:
            logger.error(f"Citation generation failed: {e}")
            return []
    
    async def get_system_prompt(self, domain: Optional[str] = None) -> str:
        """
        Get system prompt for current domain.
        
        Args:
            domain: Domain context (optional)
            
        Returns:
            System prompt string
        """
        try:
            # Set domain if provided
            if domain and domain != self.current_domain:
                await self.set_domain(domain)
            
            if not self.current_adapter:
                logger.error("No domain adapter set")
                return "You are a helpful research assistant."
            
            return self.current_adapter.get_system_prompt()
            
        except Exception as e:
            logger.error(f"Failed to get system prompt: {e}")
            return "You are a helpful research assistant."
    
    async def get_web_search_prompt(self, domain: Optional[str] = None) -> str:
        """
        Get web search prompt for current domain.
        
        Args:
            domain: Domain context (optional)
            
        Returns:
            Web search prompt string
        """
        try:
            # Set domain if provided
            if domain and domain != self.current_domain:
                await self.set_domain(domain)
            
            if not self.current_adapter:
                logger.error("No domain adapter set")
                return "Search for information related to: {query}"
            
            return self.current_adapter.get_web_search_prompt()
            
        except Exception as e:
            logger.error(f"Failed to get web search prompt: {e}")
            return "Search for information related to: {query}"
    
    async def get_domain_info(self) -> Dict[str, Any]:
        """Get information about the current domain."""
        if not self.current_adapter:
            return {'domain': None, 'adapter': None}
        
        return self.current_adapter.get_domain_info()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            # Get connector health
            connector_health = await self.connector_registry.health_check_all()
            
            # Get domain info
            domain_info = await self.get_domain_info()
            
            # Get system statistics
            stats = {
                'domain': self.current_domain,
                'adapter': domain_info.get('name') if domain_info else None,
                'connectors': connector_health,
                'retriever_available': self.retriever is not None,
                'embedding_available': self.embedding_service is not None,
                'reranking_available': self.reranking_service is not None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close the RAG system and clean up resources."""
        try:
            # Close all connectors
            await self.connector_registry.close_all_connectors()
            
            # Close retriever
            if self.retriever:
                # Add any cleanup needed for retriever
                pass
            
            logger.info("GraphMind RAG system closed")
            
        except Exception as e:
            logger.error(f"Error closing RAG system: {e}")
