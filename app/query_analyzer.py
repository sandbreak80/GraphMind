"""Query complexity analyzer for intelligent model selection and parameter tuning."""

import re
import math
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class QueryAnalysis:
    """Results of query complexity analysis."""
    complexity_score: float  # 0.0 to 1.0
    complexity_level: str    # 'simple', 'medium', 'complex', 'research'
    word_count: int
    technical_terms: int
    question_count: int
    has_multiple_questions: bool
    trading_indicators: int
    research_indicators: int
    complexity_indicators: int
    suggested_model: str
    suggested_retrieval_params: Dict[str, int]

class QueryAnalyzer:
    """Analyzes query complexity and suggests optimal parameters."""
    
    def __init__(self):
        # Technical trading terms
        self.trading_terms = [
            'moving average', 'rsi', 'macd', 'bollinger bands', 'support', 'resistance',
            'trend line', 'breakout', 'breakdown', 'volume', 'liquidity', 'volatility',
            'momentum', 'mean reversion', 'arbitrage', 'hedging', 'leverage', 'margin',
            'futures', 'options', 'swaps', 'derivatives', 'portfolio', 'diversification',
            'risk management', 'stop loss', 'take profit', 'position sizing', 'backtesting',
            'algorithmic trading', 'high frequency', 'market making', 'arbitrage',
            'technical analysis', 'fundamental analysis', 'quantitative', 'strategy'
        ]
        
        # Research complexity indicators
        self.research_indicators = [
            'comprehensive', 'detailed', 'thorough', 'in-depth', 'extensive', 'complete',
            'full analysis', 'comprehensive study', 'detailed examination', 'thorough research',
            'extensive analysis', 'complete overview', 'deep dive', 'comprehensive review'
        ]
        
        # General complexity indicators
        self.complexity_indicators = [
            'analyze', 'compare', 'explain', 'evaluate', 'research', 'strategy',
            'technical', 'fundamental', 'backtest', 'correlation', 'regression',
            'optimization', 'implementation', 'development', 'architecture',
            'framework', 'methodology', 'approach', 'technique', 'algorithm'
        ]
        
        # Question words that indicate multiple questions
        self.question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'who']
        
        # Model recommendations based on complexity
        self.model_mapping = {
            'simple': 'llama3.2:3b',
            'medium': 'llama3.1:latest', 
            'complex': 'qwen2.5-coder:14b',
            'research': 'deepseek-r1:latest'
        }
        
        # Retrieval parameter recommendations
        self.retrieval_params = {
            'simple': {'bm25_top_k': 10, 'embedding_top_k': 10, 'rerank_top_k': 3},
            'medium': {'bm25_top_k': 20, 'embedding_top_k': 20, 'rerank_top_k': 5},
            'complex': {'bm25_top_k': 30, 'embedding_top_k': 30, 'rerank_top_k': 8},
            'research': {'bm25_top_k': 50, 'embedding_top_k': 50, 'rerank_top_k': 12}
        }
    
    def analyze(self, query: str) -> QueryAnalysis:
        """Analyze query complexity and return recommendations."""
        query_lower = query.lower().strip()
        
        # Basic metrics
        word_count = len(query_lower.split())
        technical_terms = self._count_technical_terms(query_lower)
        question_count = self._count_questions(query_lower)
        has_multiple_questions = question_count > 1
        
        # Indicator counts
        trading_indicators = self._count_indicators(query_lower, self.trading_terms)
        research_indicators = self._count_indicators(query_lower, self.research_indicators)
        complexity_indicators = self._count_indicators(query_lower, self.complexity_indicators)
        
        # Calculate complexity score (0.0 to 1.0)
        complexity_score = self._calculate_complexity_score(
            word_count, technical_terms, question_count, has_multiple_questions,
            trading_indicators, research_indicators, complexity_indicators
        )
        
        # Determine complexity level
        complexity_level = self._determine_complexity_level(complexity_score, research_indicators, word_count)
        
        # Get recommendations
        suggested_model = self.model_mapping[complexity_level]
        suggested_retrieval_params = self.retrieval_params[complexity_level].copy()
        
        return QueryAnalysis(
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            word_count=word_count,
            technical_terms=technical_terms,
            question_count=question_count,
            has_multiple_questions=has_multiple_questions,
            trading_indicators=trading_indicators,
            research_indicators=research_indicators,
            complexity_indicators=complexity_indicators,
            suggested_model=suggested_model,
            suggested_retrieval_params=suggested_retrieval_params
        )
    
    def _count_technical_terms(self, query: str) -> int:
        """Count technical trading terms in query."""
        count = 0
        for term in self.trading_terms:
            if term in query:
                count += 1
        return count
    
    def _count_questions(self, query: str) -> int:
        """Count number of questions in query."""
        # Count question marks
        question_marks = query.count('?')
        
        # Count question words
        question_words = 0
        for word in self.question_words:
            question_words += query.count(f' {word} ')
        
        return max(question_marks, question_words)
    
    def _count_indicators(self, query: str, indicators: List[str]) -> int:
        """Count specific indicators in query."""
        count = 0
        for indicator in indicators:
            if indicator in query:
                count += 1
        return count
    
    def _calculate_complexity_score(self, word_count: int, technical_terms: int, 
                                  question_count: int, has_multiple_questions: bool,
                                  trading_indicators: int, research_indicators: int, 
                                  complexity_indicators: int) -> float:
        """Calculate overall complexity score (0.0 to 1.0)."""
        
        # Base score from word count (0.0 to 0.3)
        word_score = min(word_count / 50.0, 0.3)
        
        # Technical terms score (0.0 to 0.2)
        tech_score = min(technical_terms / 10.0, 0.2)
        
        # Question complexity score (0.0 to 0.2)
        question_score = 0.0
        if question_count > 0:
            question_score = min(question_count / 5.0, 0.2)
        if has_multiple_questions:
            question_score += 0.1
        
        # Indicator scores
        trading_score = min(trading_indicators / 15.0, 0.1)
        research_score = min(research_indicators / 5.0, 0.2)
        complexity_score = min(complexity_indicators / 10.0, 0.1)
        
        # Combine all scores
        total_score = (word_score + tech_score + question_score + 
                      trading_score + research_score + complexity_score)
        
        # Normalize to 0.0-1.0 range
        return min(total_score, 1.0)
    
    def _determine_complexity_level(self, complexity_score: float, 
                                  research_indicators: int, word_count: int) -> str:
        """Determine complexity level based on score and indicators."""
        
        # Research level (highest complexity)
        if (research_indicators > 0 or 
            word_count > 30 or 
            complexity_score > 0.7):
            return 'research'
        
        # Complex level
        elif (complexity_score > 0.5 or 
              word_count > 15 or 
              research_indicators > 0):
            return 'complex'
        
        # Medium level
        elif (complexity_score > 0.2 or 
              word_count > 5 or 
              research_indicators > 0):
            return 'medium'
        
        # Simple level (lowest complexity)
        else:
            return 'simple'
    
    def get_model_recommendation(self, query: str) -> str:
        """Get recommended model for query."""
        analysis = self.analyze(query)
        return analysis.suggested_model
    
    def get_retrieval_params(self, query: str) -> Dict[str, int]:
        """Get recommended retrieval parameters for query."""
        analysis = self.analyze(query)
        return analysis.suggested_retrieval_params
    
    def get_detailed_analysis(self, query: str) -> Dict[str, Any]:
        """Get detailed analysis results."""
        analysis = self.analyze(query)
        return {
            'query': query,
            'complexity_score': analysis.complexity_score,
            'complexity_level': analysis.complexity_level,
            'metrics': {
                'word_count': analysis.word_count,
                'technical_terms': analysis.technical_terms,
                'question_count': analysis.question_count,
                'has_multiple_questions': analysis.has_multiple_questions,
                'trading_indicators': analysis.trading_indicators,
                'research_indicators': analysis.research_indicators,
                'complexity_indicators': analysis.complexity_indicators
            },
            'recommendations': {
                'suggested_model': analysis.suggested_model,
                'retrieval_params': analysis.suggested_retrieval_params
            }
        }

# Global instance
query_analyzer = QueryAnalyzer()