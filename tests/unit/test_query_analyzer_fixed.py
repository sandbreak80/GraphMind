"""
Unit tests for query analyzer - Fixed version
Tests only the classes that actually exist in the module
"""

import pytest
from app.query_analyzer import QueryAnalyzer, QueryAnalysis

class TestQueryAnalyzer:
    """Test QueryAnalyzer functionality"""
    
    def test_query_analyzer_init(self):
        """Test QueryAnalyzer initialization"""
        analyzer = QueryAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_query_analyzer_has_required_methods(self):
        """Test that QueryAnalyzer has required methods"""
        analyzer = QueryAnalyzer()
        assert hasattr(analyzer, 'analyze')
    
    def test_analyze_simple_query(self):
        """Test analyzing a simple query"""
        analyzer = QueryAnalyzer()
        query = "What is the price of AAPL?"
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
        assert hasattr(result, 'complexity')
        assert hasattr(result, 'entities')
        assert hasattr(result, 'intent')
    
    def test_analyze_empty_query(self):
        """Test analyzing an empty query"""
        analyzer = QueryAnalyzer()
        query = ""
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
    
    def test_analyze_complex_query(self):
        """Test analyzing a complex query"""
        analyzer = QueryAnalyzer()
        query = "Compare the performance of AAPL and MSFT over the last 6 months and analyze the technical indicators"
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
        assert hasattr(result, 'complexity')
        assert hasattr(result, 'entities')
        assert hasattr(result, 'intent')

class TestQueryAnalysis:
    """Test QueryAnalysis data class"""
    
    def test_query_analysis_creation(self):
        """Test QueryAnalysis object creation"""
        analysis = QueryAnalysis(
            complexity="medium",
            entities=["AAPL", "MSFT"],
            intent="comparison",
            confidence=0.8
        )
        
        assert analysis.complexity == "medium"
        assert analysis.entities == ["AAPL", "MSFT"]
        assert analysis.intent == "comparison"
        assert analysis.confidence == 0.8
    
    def test_query_analysis_default_values(self):
        """Test QueryAnalysis with default values"""
        analysis = QueryAnalysis()
        
        assert hasattr(analysis, 'complexity')
        assert hasattr(analysis, 'entities')
        assert hasattr(analysis, 'intent')
        assert hasattr(analysis, 'confidence')

class TestQueryAnalyzerIntegration:
    """Test QueryAnalyzer integration scenarios"""
    
    def test_analyze_trading_query(self):
        """Test analyzing a trading-related query"""
        analyzer = QueryAnalyzer()
        query = "Show me the RSI and MACD for AAPL"
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
    
    def test_analyze_research_query(self):
        """Test analyzing a research query"""
        analyzer = QueryAnalyzer()
        query = "What are the latest earnings reports for technology companies?"
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
    
    def test_analyze_long_query(self):
        """Test analyzing a very long query"""
        analyzer = QueryAnalyzer()
        query = "I need a comprehensive analysis of the current market conditions including S&P 500 trends, sector rotation patterns, volatility indicators, and recommendations for portfolio rebalancing based on risk tolerance and investment horizon"
        
        result = analyzer.analyze(query)
        assert result is not None
        assert isinstance(result, QueryAnalysis)
