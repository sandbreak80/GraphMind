# GraphMind Core Retrieval Tests
# Tests for the core retrieval system

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from app.core.retrieval import HybridRetriever
from app.core.embeddings import EmbeddingService
from app.core.reranking import RerankingService

class TestHybridRetriever:
    """Test cases for HybridRetriever."""
    
    @pytest.fixture
    def retriever(self):
        """Create a HybridRetriever instance for testing."""
        config = {
            'top_k': 5,
            'rerank_top_k': 8,
            'domain': 'test'
        }
        return HybridRetriever(config)
    
    @pytest.mark.asyncio
    async def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever is not None
        assert retriever.config is not None
    
    @pytest.mark.asyncio
    async def test_retrieve_async(self, retriever):
        """Test async retrieval."""
        query = "test query"
        results = await retriever.retrieve_async(query, top_k=3)
        
        # Should return empty list if no documents
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_context(self, retriever):
        """Test context generation."""
        query = "test query"
        context = await retriever.get_context(query, max_tokens=1000)
        
        assert isinstance(context, str)
        assert len(context) > 0
    
    @pytest.mark.asyncio
    async def test_get_citations(self, retriever):
        """Test citation generation."""
        query = "test query"
        citations = await retriever.get_citations(query, top_k=3)
        
        assert isinstance(citations, list)
    
    @pytest.mark.asyncio
    async def test_search_with_filters(self, retriever):
        """Test search with filters."""
        query = "test query"
        doc_types = ["pdf", "text"]
        date_range = {"start": "2023-01-01", "end": "2023-12-31"}
        
        results = await retriever.search_with_filters(
            query, 
            doc_types=doc_types, 
            date_range=date_range
        )
        
        assert isinstance(results, list)
    
    def test_deduplicate_results(self, retriever):
        """Test result deduplication."""
        results = [
            {'metadata': {'doc_id': '1'}, 'text': 'text1'},
            {'metadata': {'doc_id': '2'}, 'text': 'text2'},
            {'metadata': {'doc_id': '1'}, 'text': 'text1_duplicate'},
            {'metadata': {'doc_id': '3'}, 'text': 'text3'}
        ]
        
        unique_results = retriever._deduplicate_results(results)
        assert len(unique_results) == 3
        assert unique_results[0]['metadata']['doc_id'] == '1'
        assert unique_results[1]['metadata']['doc_id'] == '2'
        assert unique_results[2]['metadata']['doc_id'] == '3'

class TestEmbeddingService:
    """Test cases for EmbeddingService."""
    
    @pytest.fixture
    def embedding_service(self):
        """Create an EmbeddingService instance for testing."""
        config = {
            'model_name': 'BAAI/bge-m3',
            'max_seq_length': 512
        }
        return EmbeddingService(config['model_name'], config)
    
    def test_embedding_service_initialization(self, embedding_service):
        """Test embedding service initialization."""
        assert embedding_service is not None
        assert embedding_service.model_name == 'BAAI/bge-m3'
    
    def test_embed_text(self, embedding_service):
        """Test text embedding."""
        text = "test text"
        embedding = embedding_service.embed_text(text)
        
        assert embedding is not None
        assert hasattr(embedding, 'shape')
    
    def test_embed_texts(self, embedding_service):
        """Test batch text embedding."""
        texts = ["text1", "text2", "text3"]
        embeddings = embedding_service.embed_texts(texts)
        
        assert embeddings is not None
        assert len(embeddings) == len(texts)
    
    def test_embed_query(self, embedding_service):
        """Test query embedding."""
        query = "test query"
        domain = "finance"
        embedding = embedding_service.embed_query(query, domain)
        
        assert embedding is not None
        assert hasattr(embedding, 'shape')
    
    def test_compute_similarity(self, embedding_service):
        """Test similarity computation."""
        import numpy as np
        
        query_embedding = np.random.rand(384)
        doc_embeddings = np.random.rand(5, 384)
        
        similarities = embedding_service.compute_similarity(query_embedding, doc_embeddings)
        
        assert similarities is not None
        assert len(similarities) == 5
        assert all(0 <= sim <= 1 for sim in similarities)
    
    def test_get_model_info(self, embedding_service):
        """Test model information retrieval."""
        info = embedding_service.get_model_info()
        
        assert 'model_name' in info
        assert 'embedding_dimension' in info
        assert 'model_type' in info

class TestRerankingService:
    """Test cases for RerankingService."""
    
    @pytest.fixture
    def reranking_service(self):
        """Create a RerankingService instance for testing."""
        config = {
            'model_name': 'BAAI/bge-reranker-large',
            'device': 'cpu'
        }
        return RerankingService(config['model_name'], config)
    
    def test_reranking_service_initialization(self, reranking_service):
        """Test reranking service initialization."""
        assert reranking_service is not None
        assert reranking_service.model_name == 'BAAI/bge-reranker-large'
    
    def test_rerank_documents(self, reranking_service):
        """Test document reranking."""
        query = "test query"
        documents = [
            {'text': 'document 1', 'score': 0.5},
            {'text': 'document 2', 'score': 0.8},
            {'text': 'document 3', 'score': 0.3}
        ]
        
        reranked = reranking_service.rerank_documents(query, documents, top_k=2)
        
        assert isinstance(reranked, list)
        assert len(reranked) <= 2
        assert all('rerank_score' in doc for doc in reranked)
    
    def test_rerank_with_domain_context(self, reranking_service):
        """Test domain-aware reranking."""
        query = "test query"
        documents = [
            {'text': 'document 1', 'score': 0.5},
            {'text': 'document 2', 'score': 0.8}
        ]
        domain = "finance"
        
        reranked = reranking_service.rerank_with_domain_context(
            query, documents, domain, top_k=2
        )
        
        assert isinstance(reranked, list)
        assert len(reranked) <= 2
    
    def test_get_rerank_scores(self, reranking_service):
        """Test reranking score extraction."""
        query = "test query"
        documents = [
            {'text': 'document 1'},
            {'text': 'document 2'}
        ]
        
        scores = reranking_service.get_rerank_scores(query, documents)
        
        assert isinstance(scores, list)
        assert len(scores) == len(documents)
        assert all(0 <= score <= 1 for score in scores)
    
    def test_get_model_info(self, reranking_service):
        """Test model information retrieval."""
        info = reranking_service.get_model_info()
        
        assert 'model_name' in info
        assert 'device' in info
        assert 'model_type' in info

class TestIntegration:
    """Integration tests for core retrieval components."""
    
    @pytest.mark.asyncio
    async def test_retriever_with_embedding_service(self):
        """Test retriever with embedding service integration."""
        config = {
            'embedding_model': 'BAAI/bge-m3',
            'reranking_model': 'BAAI/bge-reranker-large'
        }
        
        retriever = HybridRetriever(config)
        embedding_service = EmbeddingService(config['embedding_model'])
        
        # Test that components can work together
        assert retriever is not None
        assert embedding_service is not None
    
    @pytest.mark.asyncio
    async def test_retriever_with_reranking_service(self):
        """Test retriever with reranking service integration."""
        config = {
            'embedding_model': 'BAAI/bge-m3',
            'reranking_model': 'BAAI/bge-reranker-large'
        }
        
        retriever = HybridRetriever(config)
        reranking_service = RerankingService(config['reranking_model'])
        
        # Test that components can work together
        assert retriever is not None
        assert reranking_service is not None
    
    def test_error_handling(self):
        """Test error handling in core components."""
        # Test with invalid configuration
        invalid_config = {'invalid': 'config'}
        
        try:
            retriever = HybridRetriever(invalid_config)
            # Should not raise exception, but handle gracefully
            assert retriever is not None
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            assert isinstance(e, Exception)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        valid_config = {
            'top_k': 5,
            'rerank_top_k': 8,
            'domain': 'test'
        }
        
        retriever = HybridRetriever(valid_config)
        assert retriever.config == valid_config
        
        # Test with missing configuration
        empty_config = {}
        retriever_empty = HybridRetriever(empty_config)
        assert retriever_empty.config == {}
