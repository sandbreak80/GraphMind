"""Advanced reranking with multiple scoring methods and fusion techniques."""

import logging
import time
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import re
from collections import Counter
import math

logger = logging.getLogger(__name__)

@dataclass
class RerankResult:
    """Represents a reranked result with multiple scores."""
    text: str
    metadata: Dict[str, Any]
    final_score: float
    individual_scores: Dict[str, float]
    ranking_factors: Dict[str, Any]
    confidence: float

class AdvancedReranker:
    """Advanced reranking system with multiple scoring methods."""
    
    def __init__(self):
        # Scoring weights for different methods
        self.scoring_weights = {
            'semantic_similarity': 0.25,
            'keyword_match': 0.20,
            'trading_relevance': 0.15,
            'recency': 0.10,
            'document_quality': 0.10,
            'position_importance': 0.10,
            'length_penalty': 0.05,
            'diversity_bonus': 0.05
        }
        
        # Trading-specific relevance terms
        self.trading_high_value_terms = {
            'strategy': 0.9, 'implementation': 0.8, 'algorithm': 0.8, 'method': 0.7,
            'risk management': 0.9, 'portfolio': 0.8, 'optimization': 0.8,
            'backtesting': 0.8, 'validation': 0.7, 'performance': 0.7,
            'trading system': 0.9, 'automated': 0.7, 'quantitative': 0.8,
            'technical analysis': 0.8, 'fundamental analysis': 0.8,
            'market conditions': 0.7, 'volatility': 0.7, 'liquidity': 0.6,
            'entry signal': 0.8, 'exit signal': 0.8, 'stop loss': 0.8,
            'position sizing': 0.8, 'leverage': 0.7, 'margin': 0.6
        }
        
        # Quality indicators
        self.quality_indicators = {
            'code_examples': 0.8, 'formulas': 0.7, 'calculations': 0.7,
            'step_by_step': 0.8, 'detailed': 0.6, 'comprehensive': 0.7,
            'examples': 0.6, 'case study': 0.8, 'real world': 0.7,
            'best practices': 0.8, 'common mistakes': 0.6, 'tips': 0.5
        }
        
        # Performance tracking
        self.reranking_stats = {
            'total_reranks': 0,
            'avg_rerank_time': 0.0,
            'score_distributions': {},
            'method_effectiveness': {}
        }
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]], 
                      top_k: int = 10, rerank_strategy: str = 'comprehensive') -> List[RerankResult]:
        """Rerank results using multiple scoring methods."""
        if not results:
            return []
        
        start_time = time.time()
        self.reranking_stats['total_reranks'] += 1
        
        # Apply different reranking strategies
        if rerank_strategy == 'comprehensive':
            reranked = self._comprehensive_rerank(query, results, top_k)
        elif rerank_strategy == 'trading_focused':
            reranked = self._trading_focused_rerank(query, results, top_k)
        elif rerank_strategy == 'quality_focused':
            reranked = self._quality_focused_rerank(query, results, top_k)
        else:
            reranked = self._comprehensive_rerank(query, results, top_k)
        
        # Update performance stats
        rerank_time = time.time() - start_time
        self._update_reranking_stats(rerank_time, reranked)
        
        logger.info(f"Reranked {len(results)} results in {rerank_time:.3f}s, returned {len(reranked)} results")
        
        return reranked
    
    def _comprehensive_rerank(self, query: str, results: List[Dict[str, Any]], 
                            top_k: int) -> List[RerankResult]:
        """Comprehensive reranking using all scoring methods."""
        reranked_results = []
        
        for i, result in enumerate(results):
            text = result.get('text', '')
            metadata = result.get('metadata', {})
            
            # Calculate individual scores
            scores = {}
            
            # 1. Semantic similarity (if available)
            if 'score' in result:
                scores['semantic_similarity'] = result['score']
            else:
                scores['semantic_similarity'] = 0.5
            
            # 2. Keyword matching
            scores['keyword_match'] = self._calculate_keyword_match_score(query, text)
            
            # 3. Trading relevance
            scores['trading_relevance'] = self._calculate_trading_relevance_score(text)
            
            # 4. Recency (if available in metadata)
            scores['recency'] = self._calculate_recency_score(metadata)
            
            # 5. Document quality
            scores['document_quality'] = self._calculate_document_quality_score(text)
            
            # 6. Position importance
            scores['position_importance'] = self._calculate_position_importance_score(text, i, len(results))
            
            # 7. Length penalty
            scores['length_penalty'] = self._calculate_length_penalty_score(text)
            
            # 8. Diversity bonus (calculated after initial ranking)
            scores['diversity_bonus'] = 0.0  # Will be calculated later
            
            # Calculate weighted final score
            final_score = sum(scores[method] * self.scoring_weights[method] 
                            for method in scores if method in self.scoring_weights)
            
            # Calculate confidence
            confidence = self._calculate_confidence(scores)
            
            # Create rerank result
            rerank_result = RerankResult(
                text=text,
                metadata=metadata,
                final_score=final_score,
                individual_scores=scores,
                ranking_factors=self._extract_ranking_factors(query, text, scores),
                confidence=confidence
            )
            
            reranked_results.append(rerank_result)
        
        # Apply diversity bonus
        reranked_results = self._apply_diversity_bonus(reranked_results)
        
        # Sort by final score and return top_k
        reranked_results.sort(key=lambda x: x.final_score, reverse=True)
        
        return reranked_results[:top_k]
    
    def _trading_focused_rerank(self, query: str, results: List[Dict[str, Any]], 
                              top_k: int) -> List[RerankResult]:
        """Trading-focused reranking with emphasis on trading relevance."""
        # Adjust weights for trading focus
        original_weights = self.scoring_weights.copy()
        self.scoring_weights['trading_relevance'] = 0.35
        self.scoring_weights['keyword_match'] = 0.25
        self.scoring_weights['document_quality'] = 0.15
        
        reranked = self._comprehensive_rerank(query, results, top_k)
        
        # Restore original weights
        self.scoring_weights = original_weights
        
        return reranked
    
    def _quality_focused_rerank(self, query: str, results: List[Dict[str, Any]], 
                              top_k: int) -> List[RerankResult]:
        """Quality-focused reranking with emphasis on document quality."""
        # Adjust weights for quality focus
        original_weights = self.scoring_weights.copy()
        self.scoring_weights['document_quality'] = 0.30
        self.scoring_weights['trading_relevance'] = 0.20
        self.scoring_weights['keyword_match'] = 0.20
        
        reranked = self._comprehensive_rerank(query, results, top_k)
        
        # Restore original weights
        self.scoring_weights = original_weights
        
        return reranked
    
    def _calculate_keyword_match_score(self, query: str, text: str) -> float:
        """Calculate keyword matching score."""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        # Exact matches
        exact_matches = len(query_words.intersection(text_words))
        
        # Partial matches (substring)
        partial_matches = 0
        for query_word in query_words:
            for text_word in text_words:
                if query_word in text_word or text_word in query_word:
                    partial_matches += 0.5
        
        # Normalize by query length
        total_matches = exact_matches + partial_matches
        return min(total_matches / len(query_words), 1.0) if query_words else 0.0
    
    def _calculate_trading_relevance_score(self, text: str) -> float:
        """Calculate trading relevance score."""
        text_lower = text.lower()
        score = 0.0
        
        for term, weight in self.trading_high_value_terms.items():
            if term in text_lower:
                score += weight
        
        # Normalize by text length (words)
        word_count = len(text.split())
        if word_count > 0:
            score = min(score / (word_count / 100), 1.0)  # Normalize per 100 words
        
        return score
    
    def _calculate_recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score based on metadata."""
        # This would typically use a timestamp field
        # For now, return a default score
        return 0.5
    
    def _calculate_document_quality_score(self, text: str) -> float:
        """Calculate document quality score."""
        text_lower = text.lower()
        score = 0.0
        
        for indicator, weight in self.quality_indicators.items():
            if indicator in text_lower:
                score += weight
        
        # Length factor (longer documents often more comprehensive)
        word_count = len(text.split())
        if word_count > 100:
            score += 0.1
        if word_count > 500:
            score += 0.1
        
        # Structure indicators
        if any(marker in text for marker in ['1.', '2.', '3.', '•', '-']):
            score += 0.1  # Structured content
        
        return min(score, 1.0)
    
    def _calculate_position_importance_score(self, text: str, position: int, total: int) -> float:
        """Calculate position importance score."""
        # Earlier results get higher scores
        return 1.0 - (position / total)
    
    def _calculate_length_penalty_score(self, text: str) -> float:
        """Calculate length penalty score (shorter is better for some contexts)."""
        word_count = len(text.split())
        
        # Optimal length around 100-300 words
        if 100 <= word_count <= 300:
            return 1.0
        elif word_count < 100:
            return word_count / 100
        else:
            # Penalty for very long texts
            return max(0.3, 300 / word_count)
    
    def _apply_diversity_bonus(self, results: List[RerankResult]) -> List[RerankResult]:
        """Apply diversity bonus to avoid similar results."""
        if len(results) <= 1:
            return results
        
        # Group results by similarity (simple approach)
        diverse_results = []
        used_texts = set()
        
        for result in results:
            text_words = set(result.text.lower().split())
            
            # Check similarity with already selected results
            is_diverse = True
            for used_text in used_texts:
                used_words = set(used_text.lower().split())
                similarity = len(text_words.intersection(used_words)) / len(text_words.union(used_words))
                
                if similarity > 0.7:  # High similarity threshold
                    is_diverse = False
                    break
            
            if is_diverse:
                diverse_results.append(result)
                used_texts.add(result.text)
            else:
                # Apply diversity penalty
                result.final_score *= 0.8
                diverse_results.append(result)
        
        return diverse_results
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence score based on individual scores."""
        # High confidence if multiple scoring methods agree
        score_values = list(scores.values())
        if not score_values:
            return 0.0
        
        mean_score = np.mean(score_values)
        std_score = np.std(score_values)
        
        # Higher confidence for consistent scores
        consistency = 1.0 - min(std_score, 1.0)
        
        # Higher confidence for higher mean scores
        confidence = (mean_score + consistency) / 2
        
        return min(confidence, 1.0)
    
    def _extract_ranking_factors(self, query: str, text: str, scores: Dict[str, float]) -> Dict[str, Any]:
        """Extract key factors that influenced the ranking."""
        factors = {
            'query_terms_found': [],
            'trading_terms_found': [],
            'quality_indicators_found': [],
            'text_length': len(text.split()),
            'score_breakdown': scores
        }
        
        query_words = set(query.lower().split())
        text_lower = text.lower()
        
        # Find query terms in text
        for word in query_words:
            if word in text_lower:
                factors['query_terms_found'].append(word)
        
        # Find trading terms
        for term in self.trading_high_value_terms:
            if term in text_lower:
                factors['trading_terms_found'].append(term)
        
        # Find quality indicators
        for indicator in self.quality_indicators:
            if indicator in text_lower:
                factors['quality_indicators_found'].append(indicator)
        
        return factors
    
    def _update_reranking_stats(self, rerank_time: float, results: List[RerankResult]) -> None:
        """Update reranking performance statistics."""
        total_reranks = self.reranking_stats['total_reranks']
        
        # Update average rerank time
        if total_reranks > 0:
            self.reranking_stats['avg_rerank_time'] = (
                (self.reranking_stats['avg_rerank_time'] * (total_reranks - 1) + rerank_time) 
                / total_reranks
            )
        
        # Update score distributions
        if results:
            scores = [r.final_score for r in results]
            self.reranking_stats['score_distributions'] = {
                'min': min(scores),
                'max': max(scores),
                'mean': np.mean(scores),
                'std': np.std(scores)
            }
    
    def get_reranking_stats(self) -> Dict[str, Any]:
        """Get reranking performance statistics."""
        return {
            'total_reranks': self.reranking_stats['total_reranks'],
            'avg_rerank_time': self.reranking_stats['avg_rerank_time'],
            'score_distributions': self.reranking_stats['score_distributions'],
            'scoring_weights': self.scoring_weights
        }
    
    def set_scoring_weights(self, weights: Dict[str, float]) -> None:
        """Update scoring weights for different methods."""
        self.scoring_weights.update(weights)
        logger.info(f"Updated scoring weights: {self.scoring_weights}")

# Global instance
advanced_reranker = AdvancedReranker()