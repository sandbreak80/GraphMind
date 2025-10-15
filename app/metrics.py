"""Retrieval metrics and evaluation for recall tracking."""
import logging
from typing import List, Dict, Any, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class RetrievalMetrics:
    """Track and compute retrieval metrics."""
    
    def __init__(self):
        """Initialize metrics tracker."""
        self.queries = []
        self.results = []
    
    def compute_recall_at_k(
        self,
        retrieved_ids: List[str],
        relevant_ids: Set[str],
        k: int
    ) -> float:
        """
        Compute Recall@K.
        
        Recall@K = (# relevant docs in top K) / (# total relevant docs)
        """
        if not relevant_ids:
            return 0.0
        
        top_k_ids = set(retrieved_ids[:k])
        retrieved_relevant = top_k_ids.intersection(relevant_ids)
        
        recall = len(retrieved_relevant) / len(relevant_ids)
        return recall
    
    def compute_precision_at_k(
        self,
        retrieved_ids: List[str],
        relevant_ids: Set[str],
        k: int
    ) -> float:
        """
        Compute Precision@K.
        
        Precision@K = (# relevant docs in top K) / K
        """
        if k == 0:
            return 0.0
        
        top_k_ids = set(retrieved_ids[:k])
        retrieved_relevant = top_k_ids.intersection(relevant_ids)
        
        precision = len(retrieved_relevant) / k
        return precision
    
    def compute_mrr(
        self,
        retrieved_ids: List[str],
        relevant_ids: Set[str]
    ) -> float:
        """
        Compute Mean Reciprocal Rank.
        
        MRR = 1 / (rank of first relevant document)
        """
        for rank, doc_id in enumerate(retrieved_ids, start=1):
            if doc_id in relevant_ids:
                return 1.0 / rank
        return 0.0
    
    def compute_ndcg_at_k(
        self,
        retrieved_ids: List[str],
        relevance_scores: Dict[str, float],
        k: int
    ) -> float:
        """
        Compute Normalized Discounted Cumulative Gain@K.
        
        Measures ranking quality with graded relevance.
        """
        if not relevance_scores:
            return 0.0
        
        # DCG: sum of (relevance / log2(rank + 1))
        dcg = 0.0
        for rank, doc_id in enumerate(retrieved_ids[:k], start=1):
            relevance = relevance_scores.get(doc_id, 0.0)
            dcg += relevance / (rank + 1)  # log2(rank + 1) in base 2
        
        # IDCG: DCG of perfect ranking
        sorted_relevance = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = sum(rel / (rank + 1) for rank, rel in enumerate(sorted_relevance, start=1))
        
        if idcg == 0:
            return 0.0
        
        ndcg = dcg / idcg
        return ndcg
    
    def evaluate_retrieval(
        self,
        query: str,
        retrieved_results: List[Dict[str, Any]],
        relevant_doc_ids: Set[str],
        k_values: List[int] = [5, 10, 20, 50, 100]
    ) -> Dict[str, float]:
        """
        Evaluate retrieval performance for a single query.
        
        Returns metrics at various K values.
        """
        retrieved_ids = [r['id'] for r in retrieved_results]
        
        metrics = {}
        
        for k in k_values:
            if k <= len(retrieved_ids):
                metrics[f"recall@{k}"] = self.compute_recall_at_k(retrieved_ids, relevant_doc_ids, k)
                metrics[f"precision@{k}"] = self.compute_precision_at_k(retrieved_ids, relevant_doc_ids, k)
        
        metrics["mrr"] = self.compute_mrr(retrieved_ids, relevant_doc_ids)
        
        return metrics
    
    def log_metrics(self, metrics: Dict[str, float], query: str = ""):
        """Log metrics in a readable format."""
        logger.info(f"Retrieval Metrics for query: '{query[:50]}...'")
        logger.info("=" * 60)
        
        # Group by metric type
        recall_metrics = {k: v for k, v in metrics.items() if k.startswith("recall")}
        precision_metrics = {k: v for k, v in metrics.items() if k.startswith("precision")}
        other_metrics = {k: v for k, v in metrics.items() 
                        if not (k.startswith("recall") or k.startswith("precision"))}
        
        if recall_metrics:
            logger.info("Recall Metrics:")
            for k, v in sorted(recall_metrics.items()):
                logger.info(f"  {k}: {v:.3f} ({v*100:.1f}%)")
        
        if precision_metrics:
            logger.info("Precision Metrics:")
            for k, v in sorted(precision_metrics.items()):
                logger.info(f"  {k}: {v:.3f} ({v*100:.1f}%)")
        
        if other_metrics:
            logger.info("Other Metrics:")
            for k, v in sorted(other_metrics.items()):
                logger.info(f"  {k}: {v:.3f}")
        
        logger.info("=" * 60)
    
    def aggregate_metrics(self, all_query_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """Aggregate metrics across multiple queries."""
        if not all_query_metrics:
            return {}
        
        aggregated = defaultdict(list)
        
        for query_metrics in all_query_metrics:
            for metric_name, value in query_metrics.items():
                aggregated[metric_name].append(value)
        
        # Compute averages
        avg_metrics = {
            f"avg_{metric}": sum(values) / len(values)
            for metric, values in aggregated.items()
        }
        
        return avg_metrics


def estimate_relevant_docs(
    query: str,
    all_chunks: List[Dict[str, Any]],
    method: str = "keyword"
) -> Set[str]:
    """
    Estimate relevant documents for a query (ground truth approximation).
    
    In production, you'd have labeled test sets. This is a heuristic for monitoring.
    """
    relevant_ids = set()
    
    if method == "keyword":
        # Simple keyword matching
        query_terms = set(query.lower().split())
        
        for chunk in all_chunks:
            chunk_text = chunk.get("text", "").lower()
            chunk_terms = set(chunk_text.split())
            
            # If query has significant overlap with chunk
            overlap = query_terms.intersection(chunk_terms)
            if len(overlap) >= min(3, len(query_terms) * 0.5):
                relevant_ids.add(chunk['id'])
    
    return relevant_ids
