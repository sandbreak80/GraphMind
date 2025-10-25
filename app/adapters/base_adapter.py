# GraphMind Base Domain Adapter
# Base class for domain-specific adapters

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseDomainAdapter(ABC):
    """
    Base class for domain-specific adapters in GraphMind.
    
    This class provides the interface that all domain adapters must implement
    to integrate with the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the domain adapter."""
        self.config = config
        self.domain = config.get('domain', 'generic')
        self.name = config.get('name', 'Unknown Domain')
        self.description = config.get('description', '')
        self.version = config.get('version', '1.0.0')
        
        # Initialize domain-specific settings
        self._initialize_domain_settings()
    
    def _initialize_domain_settings(self):
        """Initialize domain-specific settings."""
        self.settings = self.config.get('settings', {})
        self.connectors = self.config.get('connectors', [])
        self.optional_connectors = self.config.get('optional_connectors', [])
        self.metadata = self.config.get('metadata', {})
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this domain.
        
        Returns:
            Domain-specific system prompt
        """
        pass
    
    @abstractmethod
    def get_web_search_prompt(self) -> str:
        """
        Get the web search prompt for this domain.
        
        Returns:
            Domain-specific web search prompt
        """
        pass
    
    @abstractmethod
    def get_connectors(self) -> List[str]:
        """
        Get the required connectors for this domain.
        
        Returns:
            List of required connector names
        """
        pass
    
    def get_optional_connectors(self) -> List[str]:
        """
        Get the optional connectors for this domain.
        
        Returns:
            List of optional connector names
        """
        return self.optional_connectors
    
    def get_domain_info(self) -> Dict[str, Any]:
        """
        Get information about this domain.
        
        Returns:
            Domain information dictionary
        """
        return {
            'name': self.name,
            'domain': self.domain,
            'description': self.description,
            'version': self.version,
            'connectors': self.connectors,
            'optional_connectors': self.optional_connectors,
            'metadata': self.metadata
        }
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Get domain-specific settings.
        
        Returns:
            Domain settings dictionary
        """
        return self.settings
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """
        Validate a query for this domain.
        
        Args:
            query: Query to validate
            
        Returns:
            Validation result with suggestions
        """
        return {
            'valid': True,
            'suggestions': [],
            'domain_terms': self._extract_domain_terms(query)
        }
    
    def _extract_domain_terms(self, query: str) -> List[str]:
        """
        Extract domain-specific terms from a query.
        
        Args:
            query: Query to analyze
            
        Returns:
            List of domain-specific terms
        """
        # Override in subclasses for domain-specific term extraction
        return []
    
    def enhance_query(self, query: str) -> str:
        """
        Enhance a query with domain-specific context.
        
        Args:
            query: Original query
            
        Returns:
            Enhanced query
        """
        # Override in subclasses for domain-specific query enhancement
        return query
    
    def format_response(self, response: str, sources: List[Dict[str, Any]]) -> str:
        """
        Format a response with domain-specific formatting.
        
        Args:
            response: Generated response
            sources: Source documents
            
        Returns:
            Formatted response
        """
        # Override in subclasses for domain-specific response formatting
        return response
    
    def get_domain_filters(self) -> Dict[str, Any]:
        """
        Get domain-specific filters for retrieval.
        
        Returns:
            Dictionary of filters to apply
        """
        return {}
    
    def process_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process sources with domain-specific logic.
        
        Args:
            sources: List of source documents
            
        Returns:
            Processed sources
        """
        # Override in subclasses for domain-specific source processing
        return sources
    
    def get_domain_metadata(self) -> Dict[str, Any]:
        """
        Get domain-specific metadata for responses.
        
        Returns:
            Domain metadata dictionary
        """
        return {
            'domain': self.domain,
            'adapter_version': self.version,
            'connectors_used': self.connectors
        }
