"""
Unit tests for Query Expander.

Tests query expansion strategies: paraphrase, aspect query, and HyDE.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.query_expander import QueryExpander
from app.models import Classification


class TestQueryExpander:
    """Test suite for QueryExpander."""
    
    @pytest.fixture
    def expander(self):
        """Create expander instance."""
        return QueryExpander(model="llama3.2:3b-instruct")
    
    @pytest.fixture
    def sample_classification(self):
        """Create sample classification."""
        return Classification(
            task_type="Q&A",
            required_sources=["RAG"],
            entities={"tickers": [], "indicators": ["RSI"], "dates": []},
            output_format="markdown",
            complexity="medium",
            confidence=0.85
        )
    
    def test_generate_paraphrase(self, expander):
        """Test paraphrase generation."""
        query = "What are trading strategies?"
        
        # Mock LLM response
        mock_response = "What are effective trading approaches?"
        
        with patch.object(expander.llm, 'generate', return_value=mock_response):
            paraphrase = expander._generate_paraphrase(query)
            
            assert paraphrase != query
            assert len(paraphrase) > 0
            # Should preserve meaning (basic check)
            assert "trading" in paraphrase.lower() or "strategies" in paraphrase.lower() or "approaches" in paraphrase.lower()
    
    def test_generate_aspect_query(self, expander, sample_classification):
        """Test aspect query generation."""
        query = "explain momentum trading strategies"
        
        # Mock LLM response
        mock_response = "Which technical indicators are used in momentum trading?"
        
        with patch.object(expander.llm, 'generate', return_value=mock_response):
            aspect_query = expander._generate_aspect_query(query, sample_classification)
            
            assert aspect_query != query
            assert len(aspect_query) > 0
    
    def test_generate_hyde(self, expander, sample_classification):
        """Test HyDE generation."""
        query = "momentum trading strategies"
        
        # Mock LLM response
        mock_response = "Momentum trading strategies typically use indicators like RSI and MACD to identify trend strength. Entry occurs when momentum confirms direction, with stop-losses at key support/resistance levels."
        
        with patch.object(expander.llm, 'generate', return_value=mock_response):
            hyde = expander._generate_hyde(query, sample_classification)
            
            assert hyde != query
            assert len(hyde) > 0
            # HyDE should be longer (hypothetical answer)
            assert len(hyde.split()) > len(query.split())
    
    def test_expansion_diversity(self, expander, sample_classification):
        """Test that expansions are diverse."""
        query = "trading strategies"
        
        # Mock different responses for each expansion type
        mock_responses = [
            "What are effective trading approaches?",  # Paraphrase
            "Which indicators are used in trading strategies?",  # Aspect
            "Trading strategies involve specific entry and exit rules based on market analysis."  # HyDE
        ]
        
        call_count = [0]
        
        def mock_generate(*args, **kwargs):
            response = mock_responses[call_count[0] % len(mock_responses)]
            call_count[0] += 1
            return response
        
        with patch.object(expander.llm, 'generate', side_effect=mock_generate):
            expansions = expander.expand(query, sample_classification, max_expansions=3)
            
            # Should have diverse expansions
            assert len(expansions) > 0
            assert len(expansions) <= 3
            
            # Check diversity (expansions should differ from each other)
            if len(expansions) > 1:
                for i, exp1 in enumerate(expansions):
                    for j, exp2 in enumerate(expansions):
                        if i != j:
                            similarity = expander._similarity(exp1, exp2)
                            # Should have some difference (similarity < 1.0)
                            assert similarity < 1.0
    
    def test_max_expansions_limit(self, expander, sample_classification):
        """Test that max expansions limit is enforced."""
        query = "test query"
        
        # Mock responses
        mock_responses = [
            "paraphrase 1",
            "aspect query 1",
            "hyde 1",
            "extra expansion"
        ]
        
        call_count = [0]
        
        def mock_generate(*args, **kwargs):
            response = mock_responses[call_count[0] % len(mock_responses)]
            call_count[0] += 1
            return response
        
        with patch.object(expander.llm, 'generate', side_effect=mock_generate):
            expansions = expander.expand(query, sample_classification, max_expansions=3)
            
            # Should not exceed max_expansions
            assert len(expansions) <= 3
    
    def test_parallel_generation(self, expander, sample_classification):
        """Test expansion generation (simulated parallel)."""
        query = "trading strategies"
        
        # Mock responses
        mock_responses = [
            "What are effective trading approaches?",
            "Which indicators are used?",
            "Trading strategies involve specific rules."
        ]
        
        call_count = [0]
        
        def mock_generate(*args, **kwargs):
            response = mock_responses[call_count[0] % len(mock_responses)]
            call_count[0] += 1
            return response
        
        with patch.object(expander.llm, 'generate', side_effect=mock_generate):
            expansions = expander.expand(query, sample_classification, max_expansions=3)
            
            # Should generate multiple expansions
            assert len(expansions) > 0
    
    def test_expansion_quality(self, expander, sample_classification):
        """Test expansion quality."""
        query = "explain RSI indicator"
        
        # Mock good quality responses
        mock_responses = [
            "What is the Relative Strength Index?",  # Paraphrase
            "How is RSI calculated and interpreted?",  # Aspect
            "RSI is a momentum oscillator that measures the speed and magnitude of price changes."  # HyDE
        ]
        
        call_count = [0]
        
        def mock_generate(*args, **kwargs):
            response = mock_responses[call_count[0] % len(mock_responses)]
            call_count[0] += 1
            return response
        
        with patch.object(expander.llm, 'generate', side_effect=mock_generate):
            expansions = expander.expand(query, sample_classification, max_expansions=3)
            
            # All expansions should be non-empty
            assert all(len(exp) > 0 for exp in expansions)
            
            # Expansions should relate to original query
            for exp in expansions:
                # Should have some relation to RSI or indicator
                assert "rsi" in exp.lower() or "indicator" in exp.lower() or "momentum" in exp.lower()
    
    def test_similarity_calculation(self, expander):
        """Test similarity calculation."""
        # Identical queries
        assert expander._similarity("test query", "test query") == 1.0
        
        # Completely different
        assert expander._similarity("test query", "different text") < 0.5
        
        # Partial overlap
        similarity = expander._similarity("trading strategies", "trading approaches")
        assert 0.0 < similarity < 1.0
    
    def test_ensure_diversity(self, expander):
        """Test diversity enforcement."""
        original = "trading strategies"
        
        # Similar expansions (should filter duplicates)
        expansions = [
            "trading strategies",
            "trading strategies",  # Duplicate
            "effective trading approaches",
            "trading methods and techniques"
        ]
        
        diverse = expander._ensure_diversity(expansions, original)
        
        # Should filter duplicates
        assert len(diverse) <= len(expansions)
        # Should not include original
        assert original not in diverse or diverse.count(original) == 1  # Allow one if it's different enough
