"""Dynamic retrieval parameter optimization based on query characteristics."""
import re
from typing import Dict, Any, Tuple
from app.model_selector import model_selector

class RetrievalOptimizer:
    """Optimizes retrieval parameters based on query characteristics."""
    
    def __init__(self):
        # Base retrieval parameters
        self.base_params = {
            'bm25_top_k': 30,
            'embedding_top_k': 30,
            'rerank_top_k': 8,
            'top_k': 20
        }
        
        # Parameter profiles for different query types
        self.profiles = {
            'simple': {
                'bm25_top_k': 10,
                'embedding_top_k': 10,
                'rerank_top_k': 3,
                'top_k': 8,
                'description': 'Fast retrieval for simple queries'
            },
            'medium': {
                'bm25_top_k': 20,
                'embedding_top_k': 20,
                'rerank_top_k': 5,
                'top_k': 12,
                'description': 'Balanced retrieval for medium queries'
            },
            'complex': {
                'bm25_top_k': 30,
                'embedding_top_k': 30,
                'rerank_top_k': 8,
                'top_k': 20,
                'description': 'Comprehensive retrieval for complex queries'
            },
            'research': {
                'bm25_top_k': 50,
                'embedding_top_k': 50,
                'rerank_top_k': 12,
                'top_k': 30,
                'description': 'Extensive retrieval for research queries'
            }
        }
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine optimal retrieval strategy."""
        query_lower = query.lower()
        words = query.split()
        
        # Basic metrics
        word_count = len(words)
        char_count = len(query)
        
        # Complexity indicators
        complexity_indicators = [
            'analyze', 'compare', 'evaluate', 'research', 'comprehensive',
            'detailed', 'thorough', 'extensive', 'multiple', 'various'
        ]
        
        research_indicators = [
            'comprehensive', 'detailed', 'thorough', 'extensive',
            'complete', 'full analysis', 'in-depth'
        ]
        
        # Technical terms (trading-specific)
        technical_terms = [
            'rsi', 'macd', 'bollinger', 'vwap', 'support', 'resistance',
            'momentum', 'volatility', 'trend', 'breakout', 'reversal',
            'strategy', 'strategies', 'analysis', 'technical', 'fundamental'
        ]
        
        # Question complexity
        question_marks = query.count('?')
        has_multiple_questions = question_marks > 1
        
        # Count indicators
        complexity_count = sum(1 for indicator in complexity_indicators 
                             if indicator in query_lower)
        research_count = sum(1 for indicator in research_indicators 
                           if indicator in query_lower)
        technical_count = sum(1 for term in technical_terms 
                            if term in query_lower)
        
        # Determine complexity level
        if (research_count > 0 or word_count > 30 or has_multiple_questions):
            complexity_level = 'research'
        elif (complexity_count > 1 or word_count > 15 or technical_count > 2):
            complexity_level = 'complex'
        elif (word_count > 5 or complexity_count > 0 or technical_count > 0):
            complexity_level = 'medium'
        else:
            complexity_level = 'simple'
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'complexity_indicators': complexity_count,
            'research_indicators': research_count,
            'technical_terms': technical_count,
            'has_multiple_questions': has_multiple_questions,
            'question_marks': question_marks,
            'complexity_level': complexity_level
        }
    
    def get_retrieval_params(self, query: str) -> Dict[str, Any]:
        """Get optimized retrieval parameters for a query."""
        analysis = self.analyze_query_complexity(query)
        complexity_level = analysis['complexity_level']
        
        # Get base parameters for this complexity level
        params = self.profiles[complexity_level].copy()
        
        # Remove description for actual use
        params.pop('description', None)
        
        # Add analysis metadata
        params['complexity_analysis'] = analysis
        params['profile_used'] = complexity_level
        
        return params
    
    def get_retrieval_summary(self, query: str) -> Dict[str, Any]:
        """Get a summary of retrieval optimization for a query."""
        analysis = self.analyze_query_complexity(query)
        params = self.get_retrieval_params(query)
        
        return {
            'query': query,
            'complexity_level': analysis['complexity_level'],
            'word_count': analysis['word_count'],
            'technical_terms': analysis['technical_terms'],
            'retrieval_params': {k: v for k, v in params.items() 
                               if k not in ['complexity_analysis', 'profile_used']},
            'profile_description': self.profiles[analysis['complexity_level']]['description']
        }
    
    def compare_profiles(self) -> Dict[str, Any]:
        """Compare all retrieval profiles for analysis."""
        comparison = {}
        for profile_name, profile in self.profiles.items():
            comparison[profile_name] = {
                'description': profile['description'],
                'total_docs_retrieved': profile['bm25_top_k'] + profile['embedding_top_k'],
                'final_docs': profile['top_k'],
                'rerank_docs': profile['rerank_top_k'],
                'efficiency_ratio': profile['top_k'] / (profile['bm25_top_k'] + profile['embedding_top_k'])
            }
        return comparison

# Global instance
retrieval_optimizer = RetrievalOptimizer()