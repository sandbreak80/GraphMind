# GraphMind Legal Domain Adapter
# Legal research domain adapter

from typing import Dict, List, Any
import logging

from .base_adapter import BaseDomainAdapter

logger = logging.getLogger(__name__)

class LegalAdapter(BaseDomainAdapter):
    """
    Legal domain adapter for GraphMind.
    
    This adapter provides legal research-specific functionality
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the legal adapter."""
        super().__init__(config)
        self.domain = "legal"
        self.name = "Legal Research"
        self.description = "Legal research and case law analysis assistant"
        
        # Legal-specific terms
        self.legal_terms = [
            'law', 'legal', 'case', 'court', 'judge', 'ruling', 'precedent',
            'statute', 'regulation', 'contract', 'liability', 'damages',
            'plaintiff', 'defendant', 'attorney', 'counsel', 'jurisdiction'
        ]
        
        self.legal_areas = [
            'contract', 'tort', 'criminal', 'civil', 'constitutional',
            'administrative', 'corporate', 'intellectual property',
            'family', 'employment', 'real estate', 'tax'
        ]
    
    def get_system_prompt(self) -> str:
        """Get the legal system prompt."""
        return """You are a legal research assistant specializing in case law analysis, legal document interpretation, and legal research. 
You help users understand legal concepts, analyze case law, and provide insights based on legal documents and precedents.

Key capabilities:
- Case law analysis and interpretation
- Legal document review and analysis
- Precedent identification and analysis
- Legal research and citation
- Statutory interpretation

Always provide accurate, well-cited legal insights and reference relevant cases, statutes, and legal authorities."""
    
    def get_web_search_prompt(self) -> str:
        """Get the legal web search prompt."""
        return """Search for current legal news, case law updates, and legal information related to: {query}

Focus on:
- Recent case law decisions
- Legal news and updates
- Statutory changes
- Regulatory updates
- Legal precedents"""
    
    def get_connectors(self) -> List[str]:
        """Get required connectors for legal domain."""
        return ['pdf_connector', 'web_connector', 'database_connector']
    
    def get_optional_connectors(self) -> List[str]:
        """Get optional connectors for legal domain."""
        return ['api_connector', 'obsidian_connector']
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a legal query."""
        domain_terms = self._extract_domain_terms(query)
        
        # Check if query contains legal-related terms
        has_legal_terms = any(term.lower() in query.lower() for term in self.legal_terms)
        
        suggestions = []
        if not has_legal_terms:
            suggestions.append("Consider adding legal-specific terms like 'case', 'law', 'court', 'statute'")
        
        return {
            'valid': True,
            'suggestions': suggestions,
            'domain_terms': domain_terms,
            'has_legal_terms': has_legal_terms
        }
    
    def _extract_domain_terms(self, query: str) -> List[str]:
        """Extract legal-specific terms from query."""
        query_lower = query.lower()
        found_terms = []
        
        for term in self.legal_terms:
            if term.lower() in query_lower:
                found_terms.append(term)
        
        for area in self.legal_areas:
            if area.lower() in query_lower:
                found_terms.append(area)
        
        return found_terms
    
    def enhance_query(self, query: str) -> str:
        """Enhance a legal query with domain context."""
        domain_terms = self._extract_domain_terms(query)
        
        if not domain_terms:
            # Add general legal context if no specific terms found
            return f"[Legal Research] {query}"
        
        # Add specific context based on terms found
        if any(term in domain_terms for term in ['case', 'court', 'ruling']):
            return f"[Case Law Analysis] {query}"
        elif any(term in domain_terms for term in ['statute', 'regulation']):
            return f"[Statutory Research] {query}"
        elif any(term in domain_terms for term in ['contract', 'liability']):
            return f"[Contract Law] {query}"
        else:
            return f"[Legal Research] {query}"
    
    def format_response(self, response: str, sources: List[Dict[str, Any]]) -> str:
        """Format a legal response with domain-specific formatting."""
        # Add legal-specific formatting
        formatted_response = response
        
        # Add legal disclaimer
        formatted_response += "\n\n**Legal Disclaimer**: This information is for educational and research purposes only and should not be considered as legal advice. Always consult with a qualified attorney for legal matters."
        
        return formatted_response
    
    def get_domain_filters(self) -> Dict[str, Any]:
        """Get legal-specific filters for retrieval."""
        return {
            'doc_types': ['pdf', 'text_document'],
            'categories': ['legal', 'case_law', 'statutes', 'regulations'],
            'priority_sources': ['case_law', 'statutes', 'legal_documents']
        }
    
    def process_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sources with legal-specific logic."""
        processed_sources = []
        
        for source in sources:
            metadata = source.get('metadata', {})
            doc_type = metadata.get('doc_type', '')
            
            # Add legal-specific metadata
            if 'case' in doc_type.lower() or 'court' in doc_type.lower():
                metadata['legal_category'] = 'case_law'
            elif 'statute' in doc_type.lower() or 'regulation' in doc_type.lower():
                metadata['legal_category'] = 'statutory'
            elif 'contract' in doc_type.lower() or 'agreement' in doc_type.lower():
                metadata['legal_category'] = 'contract'
            else:
                metadata['legal_category'] = 'general'
            
            source['metadata'] = metadata
            processed_sources.append(source)
        
        return processed_sources
    
    def get_domain_metadata(self) -> Dict[str, Any]:
        """Get legal-specific metadata."""
        base_metadata = super().get_domain_metadata()
        base_metadata.update({
            'legal_terms': self.legal_terms,
            'legal_areas': self.legal_areas,
            'domain_specific': True
        })
        return base_metadata
