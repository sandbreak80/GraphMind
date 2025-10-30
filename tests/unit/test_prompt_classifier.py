"""
Unit tests for Prompt Classifier.

Tests query classification, entity extraction, and LLM fallback.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from app.prompt_classifier import PromptClassifier
from app.models import Classification


class TestPromptClassifier:
    """Test suite for PromptClassifier."""
    
    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return PromptClassifier(model="llama3.2:3b-instruct")
    
    def test_extract_tickers(self, classifier):
        """Test ticker symbol extraction."""
        # Test valid tickers
        query1 = "What is the price of AAPL and ES?"
        tickers = classifier._extract_tickers(query1)
        assert "AAPL" in tickers
        assert "ES" in tickers
        
        # Test common words are filtered
        query2 = "THE AND OR trading strategies"
        tickers = classifier._extract_tickers(query2)
        assert "THE" not in tickers
        assert "AND" not in tickers
        assert "OR" not in tickers
        
        # Test trading terms are filtered
        query3 = "RSI and MACD indicators"
        tickers = classifier._extract_tickers(query3)
        assert "RSI" not in tickers
        assert "MACD" not in tickers
    
    def test_extract_indicators(self, classifier):
        """Test technical indicator extraction."""
        # Test various indicator formats
        query1 = "explain RSI and MACD indicators"
        indicators = classifier._extract_indicators(query1.lower())
        assert "RSI" in indicators
        assert "MACD" in indicators
        
        query2 = "moving average and relative strength index"
        indicators = classifier._extract_indicators(query2.lower())
        assert "MA" in indicators or "RSI" in indicators
        
        # Test case insensitivity
        query3 = "What is RSI?"
        indicators = classifier._extract_indicators(query3.lower())
        assert "RSI" in indicators
    
    def test_classify_qa_query(self, classifier):
        """Test Q&A query classification."""
        queries = [
            "What is momentum trading?",
            "How do I use RSI?",
            "Why is MACD important?",
            "Explain trading strategies"
        ]
        
        for query in queries:
            classification = classifier.classify(query)
            assert classification.task_type == "Q&A"
            assert classification.complexity in ["simple", "medium", "complex"]
            assert classification.confidence >= 0.0
            assert classification.confidence <= 1.0
    
    def test_classify_summary_query(self, classifier):
        """Test summary query classification."""
        queries = [
            "Summarize trading strategies",
            "Give me an overview of RSI",
            "Brief summary of momentum trading"
        ]
        
        for query in queries:
            classification = classifier.classify(query)
            assert classification.task_type == "summarize"
    
    def test_classify_comparison_query(self, classifier):
        """Test comparison query classification."""
        queries = [
            "Compare RSI vs MACD",
            "What is the difference between ES and NQ?",
            "RSI versus Stochastic oscillator"
        ]
        
        for query in queries:
            classification = classifier.classify(query)
            assert classification.task_type == "compare"
            assert classification.output_format in ["table", "markdown"]
    
    def test_classify_code_query(self, classifier):
        """Test code query classification."""
        queries = [
            "Write code for RSI calculation",
            "Implement a trading function",
            "Debug this script"
        ]
        
        for query in queries:
            classification = classifier.classify(query)
            assert classification.task_type == "code"
    
    def test_ambiguous_query_uses_llm(self, classifier):
        """Test that ambiguous queries use LLM fallback."""
        # Mock LLM response
        mock_response = '{"task_type": "Q&A", "output_format": "markdown", "confidence": 0.8}'
        
        with patch.object(classifier.llm, 'generate', return_value=mock_response):
            # Very vague query with no clear signals
            query = "something interesting"
            classification = classifier.classify(query)
            
            # Should call LLM
            assert classifier.llm.generate.called
            assert classification.task_type == "Q&A"
            assert classification.confidence == 0.8
    
    def test_confidence_scoring(self, classifier):
        """Test confidence scoring."""
        # Clear queries should have high confidence
        clear_query = "Compare RSI and MACD for ES futures trading"
        classification = classifier.classify(clear_query)
        assert classification.confidence >= 0.75  # High confidence
        
        # Ambiguous queries might have lower confidence
        # (but we'll test with mocked LLM to control this)
        mock_response = '{"task_type": "Q&A", "output_format": "markdown", "confidence": 0.6}'
        with patch.object(classifier.llm, 'generate', return_value=mock_response):
            vague_query = "tell me something"
            classification = classifier.classify(vague_query)
            # Confidence comes from LLM in this case
            assert classification.confidence >= 0.0
            assert classification.confidence <= 1.0
        
        # Test that all classifications have valid confidence
        test_queries = [
            "What is RSI?",
            "Compare strategies",
            "Summarize trading",
            "Code implementation"
        ]
        
        for query in test_queries:
            classification = classifier.classify(query)
            assert 0.0 <= classification.confidence <= 1.0
    
    def test_performance_under_100ms(self, classifier):
        """Test that classification completes in <100ms for rule-based queries."""
        # Test with clear queries (should be fast, rule-based)
        query = "Compare RSI and MACD for ES futures"
        
        start_time = time.time()
        classification = classifier.classify(query)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Rule-based queries should be very fast (<50ms)
        # But we allow up to 100ms as per spec
        assert elapsed_ms < 100, f"Classification took {elapsed_ms}ms, should be <100ms"
        assert classification.task_type == "compare"
    
    def test_entity_extraction(self, classifier):
        """Test entity extraction in classification."""
        query = "What are the best RSI settings for ES futures trading?"
        classification = classifier.classify(query)
        
        # Should extract indicators
        assert "RSI" in classification.entities.get("indicators", [])
        
        # Should extract tickers
        assert "ES" in classification.entities.get("tickers", [])
        
        # Check structure
        assert isinstance(classification.entities, dict)
        assert "tickers" in classification.entities
        assert "indicators" in classification.entities
        assert "dates" in classification.entities
    
    def test_source_determination(self, classifier):
        """Test required sources determination."""
        # Query with doc references should require RAG
        query1 = "What does the PDF say about trading?"
        classification = classifier.classify(query1)
        assert "RAG" in classification.required_sources
        
        # Query with Obsidian tags should require Obsidian
        query2 = "What are the #trading strategies?"
        classification = classifier.classify(query2)
        assert "Obsidian" in classification.required_sources
        
        # Query with realtime keywords should require Web
        query3 = "What is the latest news about ES?"
        classification = classifier.classify(query3)
        assert "Web" in classification.required_sources
        
        # Default should include RAG
        query4 = "tell me something"
        classification = classifier.classify(query4)
        assert "RAG" in classification.required_sources
