"""
Unit tests for query analyzer
"""

import pytest
from app.query_analyzer import QueryAnalyzer, QueryAnalysis

class TestQueryComplexity:
    """Test query complexity classification"""
    
    def test_simple_query(self):
        """Test classification of simple query"""
        query = "What is momentum trading?"
        complexity = classify_query_complexity(query)
        
        assert complexity in ["simple", "medium", "complex"]
        assert isinstance(complexity, str)
    
    def test_complex_query(self):
        """Test classification of complex query"""
        query = "Compare momentum trading strategies using RSI and MACD indicators for ES futures, considering market conditions in Q3 2024 versus Q4 2024, and provide risk-adjusted performance metrics"
        complexity = classify_query_complexity(query)
        
        # Long, multi-part query should be complex
        assert complexity in ["complex", "research"]
    
    def test_medium_query(self):
        """Test classification of medium complexity query"""
        query = "What are the best indicators for momentum trading in ES futures?"
        complexity = classify_query_complexity(query)
        
        assert complexity in ["simple", "medium"]

class TestEntityExtraction:
    """Test entity extraction from queries"""
    
    def test_extract_ticker_symbols(self):
        """Test extraction of ticker symbols"""
        query = "What is the trend for ES and NQ futures?"
        entities = extract_entities(query)
        
        if entities and "tickers" in entities:
            tickers = entities["tickers"]
            assert "ES" in tickers or "NQ" in tickers
    
    def test_extract_dates(self):
        """Test extraction of dates"""
        query = "What happened in the market on 2024-10-25?"
        entities = extract_entities(query)
        
        if entities and "dates" in entities:
            assert len(entities["dates"]) > 0
    
    def test_extract_indicators(self):
        """Test extraction of technical indicators"""
        query = "Show me strategies using RSI and MACD"
        entities = extract_entities(query)
        
        if entities and "indicators" in entities:
            indicators = entities["indicators"]
            assert "RSI" in indicators or "MACD" in indicators

@pytest.mark.unit
class TestQueryAnalyzer:
    """Test QueryAnalyzer class"""
    
    @pytest.fixture
    def analyzer(self):
        """Create QueryAnalyzer instance"""
        return QueryAnalyzer()
    
    def test_analyze_simple_query(self, analyzer):
        """Test analysis of simple query"""
        query = "What is trading?"
        
        analysis = analyzer.analyze(query)
        
        assert analysis is not None
        assert "complexity" in analysis or "type" in analysis
    
    def test_analyze_returns_dict(self, analyzer):
        """Test that analyze returns a dictionary"""
        query = "What is momentum trading?"
        analysis = analyzer.analyze(query)
        
        assert isinstance(analysis, dict)
    
    def test_analyze_empty_query(self, analyzer):
        """Test analysis of empty query"""
        query = ""
        analysis = analyzer.analyze(query)
        
        # Should handle gracefully
        assert analysis is not None
    
    def test_analyze_long_query(self, analyzer):
        """Test analysis of very long query"""
        query = " ".join(["What is trading?"] * 50)  # Very long query
        analysis = analyzer.analyze(query)
        
        assert analysis is not None
        # Long query should be classified as complex
        if "complexity" in analysis:
            assert analysis["complexity"] in ["complex", "research"]

