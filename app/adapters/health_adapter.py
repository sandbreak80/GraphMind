# GraphMind Health Domain Adapter
# Health and medical research domain adapter

from typing import Dict, List, Any
import logging

from .base_adapter import BaseDomainAdapter

logger = logging.getLogger(__name__)

class HealthAdapter(BaseDomainAdapter):
    """
    Health domain adapter for GraphMind.
    
    This adapter provides health and medical research-specific functionality
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the health adapter."""
        super().__init__(config)
        self.domain = "health"
        self.name = "Health Research"
        self.description = "Medical and health research assistant"
        
        # Health-specific terms
        self.medical_terms = [
            'health', 'medical', 'medicine', 'treatment', 'diagnosis',
            'symptom', 'disease', 'condition', 'patient', 'clinical',
            'therapy', 'drug', 'medication', 'surgery', 'procedure'
        ]
        
        self.medical_specialties = [
            'cardiology', 'neurology', 'oncology', 'pediatrics',
            'psychiatry', 'surgery', 'internal medicine', 'emergency',
            'radiology', 'pathology', 'dermatology', 'orthopedics'
        ]
    
    def get_system_prompt(self) -> str:
        """Get the health system prompt."""
        return """You are a medical research assistant specializing in health research, medical literature analysis, and clinical data interpretation. 
You help users understand medical concepts, analyze research papers, and provide insights based on medical literature and clinical data.

Key capabilities:
- Medical literature analysis
- Clinical data interpretation
- Research paper analysis
- Medical terminology explanation
- Health trend analysis

Always provide accurate, evidence-based medical insights and cite relevant research and clinical studies."""
    
    def get_web_search_prompt(self) -> str:
        """Get the health web search prompt."""
        return """Search for current medical news, research updates, and health information related to: {query}

Focus on:
- Recent medical research
- Clinical trial results
- Medical news and updates
- Health trends
- Medical breakthroughs"""
    
    def get_connectors(self) -> List[str]:
        """Get required connectors for health domain."""
        return ['pdf_connector', 'web_connector', 'database_connector']
    
    def get_optional_connectors(self) -> List[str]:
        """Get optional connectors for health domain."""
        return ['api_connector', 'obsidian_connector']
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a health query."""
        domain_terms = self._extract_domain_terms(query)
        
        # Check if query contains health-related terms
        has_health_terms = any(term.lower() in query.lower() for term in self.medical_terms)
        
        suggestions = []
        if not has_health_terms:
            suggestions.append("Consider adding health-specific terms like 'medical', 'health', 'treatment', 'diagnosis'")
        
        return {
            'valid': True,
            'suggestions': suggestions,
            'domain_terms': domain_terms,
            'has_health_terms': has_health_terms
        }
    
    def _extract_domain_terms(self, query: str) -> List[str]:
        """Extract health-specific terms from query."""
        query_lower = query.lower()
        found_terms = []
        
        for term in self.medical_terms:
            if term.lower() in query_lower:
                found_terms.append(term)
        
        for specialty in self.medical_specialties:
            if specialty.lower() in query_lower:
                found_terms.append(specialty)
        
        return found_terms
    
    def enhance_query(self, query: str) -> str:
        """Enhance a health query with domain context."""
        domain_terms = self._extract_domain_terms(query)
        
        if not domain_terms:
            # Add general health context if no specific terms found
            return f"[Health Research] {query}"
        
        # Add specific context based on terms found
        if any(term in domain_terms for term in ['treatment', 'therapy', 'drug']):
            return f"[Medical Treatment] {query}"
        elif any(term in domain_terms for term in ['diagnosis', 'symptom', 'disease']):
            return f"[Medical Diagnosis] {query}"
        elif any(term in domain_terms for term in ['research', 'study', 'clinical']):
            return f"[Medical Research] {query}"
        else:
            return f"[Health Research] {query}"
    
    def format_response(self, response: str, sources: List[Dict[str, Any]]) -> str:
        """Format a health response with domain-specific formatting."""
        # Add health-specific formatting
        formatted_response = response
        
        # Add medical disclaimer
        formatted_response += "\n\n**Medical Disclaimer**: This information is for educational and research purposes only and should not be considered as medical advice. Always consult with a qualified healthcare professional for medical matters."
        
        return formatted_response
    
    def get_domain_filters(self) -> Dict[str, Any]:
        """Get health-specific filters for retrieval."""
        return {
            'doc_types': ['pdf', 'text_document'],
            'categories': ['medical', 'health', 'clinical', 'research'],
            'priority_sources': ['medical_journals', 'clinical_studies', 'medical_documents']
        }
    
    def process_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sources with health-specific logic."""
        processed_sources = []
        
        for source in sources:
            metadata = source.get('metadata', {})
            doc_type = metadata.get('doc_type', '')
            
            # Add health-specific metadata
            if 'clinical' in doc_type.lower() or 'study' in doc_type.lower():
                metadata['health_category'] = 'clinical_research'
            elif 'treatment' in doc_type.lower() or 'therapy' in doc_type.lower():
                metadata['health_category'] = 'treatment'
            elif 'diagnosis' in doc_type.lower() or 'symptom' in doc_type.lower():
                metadata['health_category'] = 'diagnosis'
            else:
                metadata['health_category'] = 'general'
            
            source['metadata'] = metadata
            processed_sources.append(source)
        
        return processed_sources
    
    def get_domain_metadata(self) -> Dict[str, Any]:
        """Get health-specific metadata."""
        base_metadata = super().get_domain_metadata()
        base_metadata.update({
            'medical_terms': self.medical_terms,
            'medical_specialties': self.medical_specialties,
            'domain_specific': True
        })
        return base_metadata
