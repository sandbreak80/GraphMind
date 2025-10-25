# GraphMind Finance Domain Adapter
# Finance and trading research domain adapter

from typing import Dict, List, Any
import logging

from .base_adapter import BaseDomainAdapter

logger = logging.getLogger(__name__)

class FinanceAdapter(BaseDomainAdapter):
    """
    Finance domain adapter for GraphMind.
    
    This adapter provides finance and trading-specific functionality
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the finance adapter."""
        super().__init__(config)
        self.domain = "finance"
        self.name = "Finance Research"
        self.description = "Financial analysis and trading research assistant"
        
        # Finance-specific settings
        self.trading_terms = [
            'trading', 'market', 'stock', 'bond', 'option', 'futures',
            'portfolio', 'investment', 'risk', 'volatility', 'trend',
            'analysis', 'strategy', 'technical', 'fundamental'
        ]
        
        self.financial_indicators = [
            'RSI', 'MACD', 'EMA', 'SMA', 'EMA', 'Bollinger', 'ATR',
            'volume', 'price', 'support', 'resistance', 'breakout'
        ]
    
    def get_system_prompt(self) -> str:
        """Get the finance system prompt."""
        return """You are a financial research assistant specializing in market analysis, trading strategies, and financial data interpretation. 
You help users understand market trends, analyze trading opportunities, and provide insights based on financial documents and real-time market data.

Key capabilities:
- Market analysis and trend identification
- Trading strategy development and evaluation
- Risk assessment and portfolio management
- Financial document analysis
- Real-time market data interpretation

Always provide accurate, data-driven insights and cite your sources appropriately."""
    
    def get_web_search_prompt(self) -> str:
        """Get the finance web search prompt."""
        return """Search for current financial news, market data, and trading information related to: {query}

Focus on:
- Market trends and analysis
- Trading opportunities
- Economic indicators
- Company financials
- Sector performance"""
    
    def get_connectors(self) -> List[str]:
        """Get required connectors for finance domain."""
        return ['pdf_connector', 'web_connector', 'obsidian_connector']
    
    def get_optional_connectors(self) -> List[str]:
        """Get optional connectors for finance domain."""
        return ['database_connector', 'api_connector']
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate a finance query."""
        domain_terms = self._extract_domain_terms(query)
        
        # Check if query contains finance-related terms
        has_finance_terms = any(term.lower() in query.lower() for term in self.trading_terms)
        
        suggestions = []
        if not has_finance_terms:
            suggestions.append("Consider adding finance-specific terms like 'trading', 'market', 'investment'")
        
        return {
            'valid': True,
            'suggestions': suggestions,
            'domain_terms': domain_terms,
            'has_finance_terms': has_finance_terms
        }
    
    def _extract_domain_terms(self, query: str) -> List[str]:
        """Extract finance-specific terms from query."""
        query_lower = query.lower()
        found_terms = []
        
        for term in self.trading_terms:
            if term.lower() in query_lower:
                found_terms.append(term)
        
        for indicator in self.financial_indicators:
            if indicator.lower() in query_lower:
                found_terms.append(indicator)
        
        return found_terms
    
    def enhance_query(self, query: str) -> str:
        """Enhance a finance query with domain context."""
        domain_terms = self._extract_domain_terms(query)
        
        if not domain_terms:
            # Add general finance context if no specific terms found
            return f"[Finance Research] {query}"
        
        # Add specific context based on terms found
        if any(term in domain_terms for term in ['trading', 'strategy']):
            return f"[Trading Strategy] {query}"
        elif any(term in domain_terms for term in ['market', 'analysis']):
            return f"[Market Analysis] {query}"
        elif any(term in domain_terms for term in ['investment', 'portfolio']):
            return f"[Investment Research] {query}"
        else:
            return f"[Finance Research] {query}"
    
    def format_response(self, response: str, sources: List[Dict[str, Any]]) -> str:
        """Format a finance response with domain-specific formatting."""
        # Add finance-specific formatting
        formatted_response = response
        
        # Add risk disclaimer for trading advice
        if any(term in response.lower() for term in ['buy', 'sell', 'trade', 'investment']):
            formatted_response += "\n\n**Disclaimer**: This information is for educational purposes only and should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions."
        
        return formatted_response
    
    def get_domain_filters(self) -> Dict[str, Any]:
        """Get finance-specific filters for retrieval."""
        return {
            'doc_types': ['pdf', 'video_transcript', 'text_document'],
            'categories': ['finance', 'trading', 'market', 'investment'],
            'priority_sources': ['financial_reports', 'market_data', 'trading_guides']
        }
    
    def process_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process sources with finance-specific logic."""
        processed_sources = []
        
        for source in sources:
            metadata = source.get('metadata', {})
            doc_type = metadata.get('doc_type', '')
            
            # Add finance-specific metadata
            if 'trading' in doc_type.lower() or 'market' in doc_type.lower():
                metadata['finance_category'] = 'trading'
            elif 'investment' in doc_type.lower() or 'portfolio' in doc_type.lower():
                metadata['finance_category'] = 'investment'
            elif 'analysis' in doc_type.lower() or 'research' in doc_type.lower():
                metadata['finance_category'] = 'analysis'
            else:
                metadata['finance_category'] = 'general'
            
            source['metadata'] = metadata
            processed_sources.append(source)
        
        return processed_sources
    
    def get_domain_metadata(self) -> Dict[str, Any]:
        """Get finance-specific metadata."""
        base_metadata = super().get_domain_metadata()
        base_metadata.update({
            'trading_terms': self.trading_terms,
            'financial_indicators': self.financial_indicators,
            'domain_specific': True
        })
        return base_metadata
