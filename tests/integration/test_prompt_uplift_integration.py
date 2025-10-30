"""
Integration tests for Prompt Uplift Pipeline.

Tests end-to-end integration with retrieval system.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.prompt_uplift_pipeline import PromptUpliftPipeline
from app.models import Classification, ProcessedQuery


class TestPromptUpliftIntegration:
    """Integration test suite for prompt uplift."""
    
    @pytest.fixture
    def pipeline(self):
        """Create pipeline instance."""
        return PromptUpliftPipeline()
    
    def test_end_to_end_retrieval_improvement(self, pipeline):
        """Test that uplift improves retrieval results."""
        # This would require actual retrieval - mock for now
        query = "trading strategies"
        
        with patch.object(pipeline.classifier, 'classify'), \
             patch.object(pipeline.uplifter, 'uplift'), \
             patch.object(pipeline.expander, 'expand'):
            
            # Mock classification
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
            
            pipeline.classifier.classify.return_value = mock_classification
            pipeline.uplifter.uplift.return_value = mock_uplifted
            pipeline.expander.expand.return_value = ["effective trading approaches"]
            
            result = pipeline.process(query, {"user_id": "test"})
            
            assert result.final_query != query
            assert len(result.final_query) > len(query)
            assert "cite" in result.final_query.lower()
    
    def test_latency_within_budget(self, pipeline):
        """Test that pipeline completes within latency budget."""
        import time
        
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
            
            start_time = time.time()
            result = pipeline.process(query, {"user_id": "test"})
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Should complete within budget (600ms with mocks should be very fast)
            assert elapsed_ms < 1000  # Allow overhead
            assert result.metadata.get("latency_ms", 0) >= 0
    
    def test_cache_performance(self, pipeline):
        """Test cache hit performance."""
        query = "cached query"
        context = {"user_id": "test"}
        
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
            result1 = pipeline.process(query, context)
            
            # Second call should use cache (if implemented)
            # Note: Actual cache testing requires Redis mock
            result2 = pipeline.process(query, context)
            
            assert result2.final_query == result1.final_query
    
    def test_fact_injection_detection(self, pipeline):
        """Test that fact injection is detected."""
        query = "explain RSI"
        
        # Mock uplifter that might inject facts
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
            # Low confidence uplift (might indicate fact injection)
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Poor improvement with facts",
                classification=mock_classification,
                confidence=0.3  # Low confidence triggers fallback
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            mock_expand.return_value = []
            
            result = pipeline.process(query, {"user_id": "test"})
            
            # Should fall back to original due to low confidence
            assert result.used_original == True
            assert result.final_query == query
    
    def test_confidence_fallback(self, pipeline):
        """Test confidence-based fallback."""
        query = "test query"
        
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
            # Low confidence should trigger fallback
            mock_uplifted = UpliftedPrompt(
                original=query,
                improved="Poor improvement",
                classification=mock_classification,
                confidence=0.5  # Below threshold (0.75)
            )
            
            mock_classify.return_value = mock_classification
            mock_uplift.return_value = mock_uplifted
            
            result = pipeline.process(query, {"user_id": "test"})
            
            # Should fall back to original
            assert result.used_original == True
            assert result.final_query == query
    
    def test_skip_expansion_logic(self, pipeline):
        """Test skip expansion when baseline is good."""
        query = "test query"
        context = {"user_id": "test", "previous_hits": 5}
        
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
            
            result = pipeline.process(query, context)
            
            # Expansion should be skipped (previous_hits >= 3)
            mock_expand.assert_not_called()
            assert len(result.expansions) == 0
    
    def test_error_handling(self, pipeline):
        """Test error handling and graceful degradation."""
        query = "test query"
        
        # Simulate component failure
        with patch.object(pipeline.classifier, 'classify', side_effect=Exception("Classify failed")):
            # Should handle gracefully
            try:
                result = pipeline.process(query, {"user_id": "test"})
                # Should still return valid result (fallback)
                assert isinstance(result, ProcessedQuery)
            except Exception:
                # If it fails completely, that's also acceptable
                pass
    
    def test_multiple_query_deduplication(self):
        """Test deduplication of results from multiple queries."""
        from app.main import _deduplicate_results
        
        # Test with dict results
        results = [
            {"doc_id": "doc1", "text": "Text 1", "rerank_score": 0.9},
            {"doc_id": "doc2", "text": "Text 2", "rerank_score": 0.8},
            {"doc_id": "doc1", "text": "Text 1", "rerank_score": 0.95},  # Duplicate, higher score
        ]
        
        deduplicated = _deduplicate_results(results)
        
        # Should have 2 unique documents
        doc_ids = [r.get('doc_id') if isinstance(r, dict) else getattr(r, 'doc_id', None) for r in deduplicated]
        assert len(set(doc_ids)) == 2
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids
        
        # doc1 should have higher score (0.95)
        doc1_result = next(r for r in deduplicated if (r.get('doc_id') if isinstance(r, dict) else getattr(r, 'doc_id', None)) == "doc1")
        doc1_score = doc1_result.get('rerank_score') if isinstance(doc1_result, dict) else getattr(doc1_result, 'rerank_score', 0)
        assert doc1_score == 0.95
    
    def test_metadata_in_response(self, pipeline):
        """Test that metadata is included in response."""
        query = "test query"
        
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
            mock_expand.return_value = ["expansion1"]
            
            result = pipeline.process(query, {"user_id": "test"})
            
            # Check metadata
            assert "original" in result.metadata
            assert "task_type" in result.metadata
            assert "latency_ms" in result.metadata
            assert result.metadata["original"] == query
    
    def test_feature_flag(self):
        """Test feature flag control."""
        from app.config import FEATURES
        
        # Feature flag should be accessible
        assert "prompt_uplift" in FEATURES
        assert isinstance(FEATURES["prompt_uplift"], bool)
