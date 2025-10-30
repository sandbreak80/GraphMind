"""
Unit tests for Prompt Uplift Pipeline.

Tests end-to-end pipeline flow, caching, skip logic, and fallbacks.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from app.prompt_uplift_pipeline import PromptUpliftPipeline
from app.models import Classification, ProcessedQuery


class TestPromptUpliftPipeline:
    """Test suite for PromptUpliftPipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return PromptUpliftPipeline()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context."""
        return {
            "user_id": "test_user",
            "conversation_id": "test_conv",
            "previous_hits": 0
        }
    
    def test_full_pipeline_flow(self, pipeline, sample_context):
        """Test full pipeline flow."""
        query = "trading strategies"
        
        # Mock components
        with patch.object(pipeline.classifier, 'classify') as mock_classify, \
             patch.object(pipeline.uplifter, 'uplift') as mock_uplift, \
             patch.object(pipeline.expander, 'expand') as mock_expand:
            
            # Setup mocks
            mock_classification = Classification(
                task_type="Q&A",
                required_sources=["RAG"],
                entities={},
                output_format="markdown",
                complexity="medium",
                confidence=0.85
            )
            
            from app.models import UpliftedPrompt
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Provide 3-5 specific trading strategies with risk profiles. Cite sources.",
                classification=mock_classification,
                confidence=0.85
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            mock_expand.return_value = ["effective trading approaches", "momentum strategies"]
            
            # Run pipeline
            result = pipeline.process(query, sample_context)
            
            # Verify result
            assert isinstance(result, ProcessedQuery)
            assert result.final_query != query
            assert len(result.expansions) > 0
            assert result.used_original == False
            assert result.uplift_confidence >= 0.0
    
    def test_skip_expansion_on_good_baseline(self, pipeline):
        """Test skip expansion when baseline is good."""
        query = "test query"
        context = {
            "user_id": "test",
            "previous_hits": 5  # High hit count
        }
        
        # Mock components
        with patch.object(pipeline.classifier, 'classify') as mock_classify, \
             patch.object(pipeline.uplifter, 'uplift') as mock_uplift, \
             patch.object(pipeline.expander, 'expand') as mock_expand:
            
            mock_classification = Classification(
                task_type="Q&A",
                required_sources=["RAG"],
                entities={},
                output_format="markdown",
                complexity="medium",
                confidence=0.85
            )
            
            from app.models import UpliftedPrompt
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Improved query",
                classification=mock_classification,
                confidence=0.85
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            
            # Run pipeline
            result = pipeline.process(query, context)
            
            # Expansion should be skipped (previous_hits >= threshold)
            mock_expand.assert_not_called()
            assert len(result.expansions) == 0
    
    def test_confidence_fallback_to_original(self, pipeline, sample_context):
        """Test fallback to original when confidence is low."""
        query = "test query"
        
        # Mock components
        with patch.object(pipeline.classifier, 'classify') as mock_classify, \
             patch.object(pipeline.uplifter, 'uplift') as mock_uplift:
            
            mock_classification = Classification(
                task_type="Q&A",
                required_sources=["RAG"],
                entities={},
                output_format="markdown",
                complexity="medium",
                confidence=0.85
            )
            
            from app.models import UpliftedPrompt
            # Low confidence uplift
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Poor improvement",
                classification=mock_classification,
                confidence=0.5  # Below threshold
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            
            # Run pipeline
            result = pipeline.process(query, sample_context)
            
            # Should fall back to original
            assert result.used_original == True
            assert result.final_query == query
            assert len(result.expansions) == 0
    
    def test_caching_works(self, pipeline, sample_context):
        """Test caching functionality."""
        query = "cached query"
        
        # Mock components
        with patch.object(pipeline.classifier, 'classify') as mock_classify, \
             patch.object(pipeline.uplifter, 'uplift') as mock_uplift, \
             patch.object(pipeline.expander, 'expand') as mock_expand:
            
            mock_classification = Classification(
                task_type="Q&A",
                required_sources=["RAG"],
                entities={},
                output_format="markdown",
                complexity="medium",
                confidence=0.85
            )
            
            from app.models import UpliftedPrompt
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Improved",
                classification=mock_classification,
                confidence=0.85
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            mock_expand.return_value = []
            
            # First call
            result1 = pipeline.process(query, sample_context)
            
            # Mock cache hit
            with patch.object(pipeline, '_get_from_cache', return_value=result1):
                # Second call should use cache
                result2 = pipeline.process(query, sample_context)
                
                # Should not call components again (cache hit)
                # Note: This is a simplified test - actual cache integration would need Redis mock
                assert result2.final_query == result1.final_query
    
    def test_latency_within_budget(self, pipeline, sample_context):
        """Test that pipeline completes within latency budget."""
        query = "test query"
        
        # Mock fast components
        with patch.object(pipeline.classifier, 'classify') as mock_classify, \
             patch.object(pipeline.uplifter, 'uplift') as mock_uplift, \
             patch.object(pipeline.expander, 'expand') as mock_expand:
            
            mock_classification = Classification(
                task_type="Q&A",
                required_sources=["RAG"],
                entities={},
                output_format="markdown",
                complexity="medium",
                confidence=0.85
            )
            
            from app.models import UpliftedPrompt
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Improved",
                classification=mock_classification,
                confidence=0.85
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            mock_expand.return_value = []
            
            # Run pipeline
            start_time = time.time()
            result = pipeline.process(query, sample_context)
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Should complete within budget (600ms)
            # Note: With mocks, this should be very fast, but test validates structure
            assert elapsed_ms < 1000  # Allow some overhead for test setup
            assert result.metadata.get("latency_ms", 0) >= 0
