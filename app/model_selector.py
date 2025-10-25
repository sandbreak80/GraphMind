"""Smart model selection based on query characteristics."""
import re
from typing import Dict, List, Any

class ModelSelector:
    """Smart model selection based on query characteristics."""
    
    def __init__(self):
        self.models = {
            'simple': 'deepseek-r1:7b',         # Fastest available
            'medium': 'deepseek-r1:7b',          # Balanced
            'complex': 'deepseek-r1:14b',       # More capable
            'research': 'deepseek-r1:14b'       # Most capable
        }
        
        # Query complexity indicators
        self.complex_indicators = [
            'analyze', 'compare', 'explain', 'evaluate', 'research',
            'strategy', 'technical', 'fundamental', 'backtest',
            'correlation', 'regression', 'optimization'
        ]
        
        self.research_indicators = [
            'comprehensive', 'detailed', 'thorough', 'in-depth',
            'extensive', 'complete', 'full analysis'
        ]
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine complexity."""
        query_lower = query.lower()
        words = query.split()
        
        # Basic metrics
        word_count = len(words)
        char_count = len(query)
        
        # Complexity indicators
        complex_count = sum(1 for indicator in self.complex_indicators 
                           if indicator in query_lower)
        research_count = sum(1 for indicator in self.research_indicators 
                            if indicator in query_lower)
        
        # Question complexity
        question_marks = query.count('?')
        has_multiple_questions = question_marks > 1
        
        # Technical terms (trading-specific)
        technical_terms = [
            'rsi', 'macd', 'bollinger', 'vwap', 'support', 'resistance',
            'momentum', 'volatility', 'trend', 'breakout', 'reversal'
        ]
        technical_count = sum(1 for term in technical_terms 
                             if term in query_lower)
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'complex_indicators': complex_count,
            'research_indicators': research_count,
            'technical_terms': technical_count,
            'has_multiple_questions': has_multiple_questions,
            'question_marks': question_marks
        }
    
    def select_model(self, query: str) -> str:
        """Select best model for query."""
        analysis = self.analyze_query_complexity(query)
        
        # Research queries (highest complexity)
        if (analysis['research_indicators'] > 0 or 
            analysis['word_count'] > 30 or 
            analysis['has_multiple_questions']):
            return self.models['research']
        
        # Complex queries
        elif (analysis['complex_indicators'] > 1 or 
              analysis['word_count'] > 15 or 
              analysis['technical_terms'] > 2):
            return self.models['complex']
        
        # Medium queries
        elif (analysis['word_count'] > 5 or 
              analysis['complex_indicators'] > 0 or 
              analysis['technical_terms'] > 0):
            return self.models['medium']
        
        # Simple queries
        else:
            return self.models['simple']
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        model_info = {
            'llama3.2:3b': {
                'name': 'Llama 3.2 3B',
                'speed': 'Fastest',
                'capability': 'Basic',
                'use_case': 'Simple questions'
            },
            'llama3.1:latest': {
                'name': 'Llama 3.1 Latest',
                'speed': 'Fast',
                'capability': 'Balanced',
                'use_case': 'General questions'
            },
            'qwen2.5-coder:14b': {
                'name': 'Qwen 2.5 Coder 14B',
                'speed': 'Medium',
                'capability': 'High',
                'use_case': 'Complex analysis'
            },
            'gpt-oss:20b': {
                'name': 'GPT-OSS 20B',
                'speed': 'Slowest',
                'capability': 'Highest',
                'use_case': 'Research & analysis'
            }
        }
        return model_info.get(model, {'name': 'Unknown', 'speed': 'Unknown'})

# Global instance
model_selector = ModelSelector()