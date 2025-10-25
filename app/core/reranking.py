# GraphMind Core Reranking Service
# Domain-agnostic reranking functionality

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

class RerankingService:
    """
    Domain-agnostic reranking service for GraphMind.
    
    This service provides reranking functionality that can be used
    across any domain without trading-specific terminology.
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-large", config: Optional[Dict[str, Any]] = None):
        """Initialize the reranking service."""
        self.model_name = model_name
        self.config = config or {}
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the reranking model."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"GraphMind reranking service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize reranking model: {e}")
            raise
    
    def rerank_documents(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 5,
        domain: str = "generic"
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top documents to return
            domain: Domain context for reranking
            
        Returns:
            Reranked documents with scores
        """
        try:
            if not documents:
                return []
            
            # Prepare query-document pairs
            pairs = []
            for doc in documents:
                text = doc.get('text', '')
                pairs.append((query, text))
            
            # Compute reranking scores
            scores = self._compute_rerank_scores(pairs)
            
            # Add scores to documents and sort
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
            
            # Sort by rerank score (descending)
            reranked_docs = sorted(documents, key=lambda x: x.get('rerank_score', 0), reverse=True)
            
            return reranked_docs[:top_k]
            
        except Exception as e:
            logger.error(f"Document reranking failed: {e}")
            return documents[:top_k]  # Return original order if reranking fails
    
    def _compute_rerank_scores(self, pairs: List[tuple]) -> np.ndarray:
        """Compute reranking scores for query-document pairs."""
        try:
            # Tokenize pairs
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Compute scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.sigmoid(outputs.logits).squeeze(-1)
            
            return scores.cpu().numpy()
            
        except Exception as e:
            logger.error(f"Score computation failed: {e}")
            # Return uniform scores if computation fails
            return np.ones(len(pairs)) * 0.5
    
    def rerank_with_domain_context(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        domain: str = "generic",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents with domain-specific context.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            domain: Domain context
            top_k: Number of top documents to return
            
        Returns:
            Reranked documents with domain-aware scores
        """
        try:
            # Add domain context to query
            if domain != "generic":
                domain_query = f"[{domain}] {query}"
            else:
                domain_query = query
            
            return self.rerank_documents(domain_query, documents, top_k, domain)
            
        except Exception as e:
            logger.error(f"Domain-aware reranking failed: {e}")
            return self.rerank_documents(query, documents, top_k, domain)
    
    def get_rerank_scores(
        self, 
        query: str, 
        documents: List[Dict[str, Any]]
    ) -> List[float]:
        """
        Get reranking scores for documents without reranking.
        
        Args:
            query: Search query
            documents: List of documents
            
        Returns:
            List of reranking scores
        """
        try:
            pairs = [(query, doc.get('text', '')) for doc in documents]
            scores = self._compute_rerank_scores(pairs)
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"Score extraction failed: {e}")
            return [0.5] * len(documents)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranking model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": 512,
            "model_type": "cross_encoder"
        }
