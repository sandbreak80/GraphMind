# GraphMind Core Embeddings Service
# Domain-agnostic embedding functionality

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Domain-agnostic embedding service for GraphMind.
    
    This service provides embedding functionality that can be used
    across any domain without trading-specific terminology.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-m3", config: Optional[Dict[str, Any]] = None):
        """Initialize the embedding service."""
        self.model_name = model_name
        self.config = config or {}
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"GraphMind embedding service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector
        """
        try:
            embedding = self.model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            Array of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size)
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            raise
    
    def embed_query(self, query: str, domain: str = "generic") -> np.ndarray:
        """
        Generate embedding for a search query with domain context.
        
        Args:
            query: Search query
            domain: Domain context for embedding
            
        Returns:
            Query embedding vector
        """
        try:
            # Add domain context to query if needed
            if domain != "generic":
                domain_query = f"[{domain}] {query}"
            else:
                domain_query = query
            
            embedding = self.model.encode(domain_query)
            return embedding
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise
    
    def compute_similarity(
        self, 
        query_embedding: np.ndarray, 
        doc_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute similarity between query and document embeddings.
        
        Args:
            query_embedding: Query embedding vector
            doc_embeddings: Document embedding vectors
            
        Returns:
            Similarity scores
        """
        try:
            # Normalize embeddings
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
            
            # Compute cosine similarity
            similarities = np.dot(doc_norms, query_norm)
            return similarities
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "max_seq_length": getattr(self.model, 'max_seq_length', 512),
            "embedding_dimension": getattr(self.model, 'get_sentence_embedding_dimension', lambda: 384)(),
            "model_type": "sentence_transformer"
        }
