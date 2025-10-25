"""Context compression and summarization for long documents."""

import logging
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import aiohttp
from collections import Counter
import math

logger = logging.getLogger(__name__)

@dataclass
class CompressedContext:
    """Represents compressed context with summary and key points."""
    original_text: str
    compressed_text: str
    summary: str
    key_points: List[str]
    compression_ratio: float
    quality_score: float
    compression_method: str
    metadata: Dict[str, Any]

class ContextCompressor:
    """Advanced context compression and summarization system."""
    
    def __init__(self):
        # Compression strategies
        self.compression_strategies = {
            'extractive': self._extractive_compression,
            'abstractive': self._abstractive_compression,
            'hybrid': self._hybrid_compression,
            'semantic': self._semantic_compression
        }
        
        # Key phrase patterns for trading content
        self.trading_key_patterns = [
            r'\b(?:strategy|method|approach|technique|system)\b',
            r'\b(?:implementation|execution|deployment)\b',
            r'\b(?:risk management|position sizing|stop loss)\b',
            r'\b(?:backtesting|validation|optimization)\b',
            r'\b(?:entry signal|exit signal|trigger)\b',
            r'\b(?:performance|returns|profit|loss)\b',
            r'\b(?:volatility|liquidity|volume)\b',
            r'\b(?:support|resistance|trend|momentum)\b'
        ]
        
        # Important sentence starters
        self.important_starters = [
            'The key', 'Important', 'Critical', 'Essential', 'Note that',
            'Remember', 'Always', 'Never', 'Best practice', 'Common mistake',
            'Step 1', 'Step 2', 'First', 'Second', 'Finally', 'In conclusion'
        ]
        
        # Quality indicators for sentence importance
        self.quality_indicators = {
            'formulas': r'[=+\-*/()0-9]+',
            'code_blocks': r'```[\s\S]*?```',
            'numbered_lists': r'^\d+\.',
            'bullet_points': r'^[-*•]',
            'definitions': r'\b(?:is|are|means|refers to|defined as)\b',
            'examples': r'\b(?:example|for instance|such as|like)\b',
            'steps': r'\b(?:step|process|procedure|method)\b'
        }
        
        # Performance tracking
        self.compression_stats = {
            'total_compressions': 0,
            'avg_compression_ratio': 0.0,
            'avg_quality_score': 0.0,
            'method_usage': {},
            'avg_compression_time': 0.0
        }
    
    async def compress_context(self, text: str, target_ratio: float = 0.3, 
                             method: str = 'hybrid', max_length: int = 1000) -> CompressedContext:
        """Compress context using specified method and target ratio."""
        start_time = time.time()
        self.compression_stats['total_compressions'] += 1
        
        if not text or len(text.strip()) < 100:
            return CompressedContext(
                original_text=text,
                compressed_text=text,
                summary="",
                key_points=[],
                compression_ratio=1.0,
                quality_score=1.0,
                compression_method=method,
                metadata={}
            )
        
        # Choose compression method
        if method in self.compression_strategies:
            compressed_result = await self.compression_strategies[method](text, target_ratio, max_length)
        else:
            compressed_result = await self._hybrid_compression(text, target_ratio, max_length)
        
        # Calculate metrics
        compression_ratio = len(compressed_result['compressed_text']) / len(text) if text else 1.0
        quality_score = self._calculate_quality_score(text, compressed_result['compressed_text'])
        
        # Update stats
        compression_time = time.time() - start_time
        self._update_compression_stats(compression_time, compression_ratio, quality_score, method)
        
        return CompressedContext(
            original_text=text,
            compressed_text=compressed_result['compressed_text'],
            summary=compressed_result['summary'],
            key_points=compressed_result['key_points'],
            compression_ratio=compression_ratio,
            quality_score=quality_score,
            compression_method=method,
            metadata=compressed_result['metadata']
        )
    
    async def _extractive_compression(self, text: str, target_ratio: float, 
                                    max_length: int) -> Dict[str, Any]:
        """Extractive compression by selecting most important sentences."""
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return {
                'compressed_text': text,
                'summary': '',
                'key_points': [],
                'metadata': {'method': 'extractive', 'sentences_selected': 0}
            }
        
        # Score sentences for importance
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence_importance(sentence, i, len(sentences))
            scored_sentences.append((sentence, score, i))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate number of sentences to keep
        target_sentences = max(1, int(len(sentences) * target_ratio))
        target_sentences = min(target_sentences, max_length // 50)  # Rough estimate
        
        selected_sentences = scored_sentences[:target_sentences]
        selected_sentences.sort(key=lambda x: x[2])  # Sort by original order
        
        compressed_text = ' '.join([s[0] for s in selected_sentences])
        key_points = [s[0] for s in selected_sentences if s[1] > 0.7]
        
        return {
            'compressed_text': compressed_text,
            'summary': self._create_summary(selected_sentences),
            'key_points': key_points,
            'metadata': {
                'method': 'extractive',
                'sentences_selected': len(selected_sentences),
                'total_sentences': len(sentences),
                'avg_sentence_score': sum(s[1] for s in selected_sentences) / len(selected_sentences)
            }
        }
    
    async def _abstractive_compression(self, text: str, target_ratio: float, 
                                     max_length: int) -> Dict[str, Any]:
        """Abstractive compression using summarization techniques."""
        # For now, use extractive as fallback
        # In production, this would use a summarization model
        return await self._extractive_compression(text, target_ratio, max_length)
    
    async def _hybrid_compression(self, text: str, target_ratio: float, 
                                max_length: int) -> Dict[str, Any]:
        """Hybrid compression combining extractive and abstractive methods."""
        # First, do extractive compression
        extractive_result = await self._extractive_compression(text, target_ratio * 1.2, max_length)
        
        # Then apply additional compression techniques
        compressed_text = self._apply_additional_compression(extractive_result['compressed_text'])
        
        # Extract key points
        key_points = self._extract_key_points(compressed_text)
        
        return {
            'compressed_text': compressed_text,
            'summary': extractive_result['summary'],
            'key_points': key_points,
            'metadata': {
                'method': 'hybrid',
                'base_method': 'extractive',
                'additional_compression': True,
                'key_points_count': len(key_points)
            }
        }
    
    async def _semantic_compression(self, text: str, target_ratio: float, 
                                  max_length: int) -> Dict[str, Any]:
        """Semantic compression focusing on meaning preservation."""
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return {
                'compressed_text': text,
                'summary': '',
                'key_points': [],
                'metadata': {'method': 'semantic', 'sentences_selected': 0}
            }
        
        # Group sentences by semantic similarity
        semantic_groups = self._group_sentences_semantically(sentences)
        
        # Select representative sentences from each group
        selected_sentences = []
        for group in semantic_groups:
            if group:
                # Select the most important sentence from each group
                best_sentence = max(group, key=lambda s: self._score_sentence_importance(s, 0, 1))
                selected_sentences.append(best_sentence)
        
        compressed_text = ' '.join(selected_sentences)
        key_points = [s for s in selected_sentences if self._score_sentence_importance(s, 0, 1) > 0.6]
        
        return {
            'compressed_text': compressed_text,
            'summary': self._create_summary([(s, 0.5, i) for i, s in enumerate(selected_sentences)]),
            'key_points': key_points,
            'metadata': {
                'method': 'semantic',
                'semantic_groups': len(semantic_groups),
                'sentences_selected': len(selected_sentences),
                'compression_ratio': len(compressed_text) / len(text)
            }
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be enhanced with NLP libraries)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _score_sentence_importance(self, sentence: str, position: int, total_sentences: int) -> float:
        """Score sentence importance based on multiple factors."""
        score = 0.0
        sentence_lower = sentence.lower()
        
        # Position score (beginning and end are often important)
        if position < total_sentences * 0.1 or position > total_sentences * 0.9:
            score += 0.2
        
        # Length score (very short or very long sentences are often important)
        word_count = len(sentence.split())
        if 10 <= word_count <= 30:
            score += 0.1
        elif word_count > 50:
            score += 0.15
        
        # Trading-specific patterns
        for pattern in self.trading_key_patterns:
            if re.search(pattern, sentence_lower):
                score += 0.3
        
        # Important sentence starters
        for starter in self.important_starters:
            if sentence_lower.startswith(starter.lower()):
                score += 0.2
        
        # Quality indicators
        for indicator, pattern in self.quality_indicators.items():
            if re.search(pattern, sentence):
                score += 0.1
        
        # Keyword density (trading terms)
        trading_terms = ['strategy', 'trading', 'risk', 'portfolio', 'market', 'price', 'signal']
        term_count = sum(1 for term in trading_terms if term in sentence_lower)
        score += term_count * 0.05
        
        # Question sentences are often important
        if sentence.strip().endswith('?'):
            score += 0.15
        
        return min(score, 1.0)
    
    def _create_summary(self, selected_sentences: List[Tuple[str, float, int]]) -> str:
        """Create a summary from selected sentences."""
        if not selected_sentences:
            return ""
        
        # Take the top 3 most important sentences
        top_sentences = sorted(selected_sentences, key=lambda x: x[1], reverse=True)[:3]
        summary_sentences = [s[0] for s in top_sentences]
        
        return ' '.join(summary_sentences)
    
    def _apply_additional_compression(self, text: str) -> str:
        """Apply additional compression techniques."""
        # Remove redundant phrases
        redundant_phrases = [
            r'\b(?:it is important to note that|it should be noted that)\b',
            r'\b(?:in other words|that is to say|in other terms)\b',
            r'\b(?:as mentioned earlier|as stated before|as previously mentioned)\b',
            r'\b(?:for example,|for instance,|such as,)\b'
        ]
        
        compressed = text
        for pattern in redundant_phrases:
            compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        compressed = re.sub(r'\s+', ' ', compressed).strip()
        
        return compressed
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from compressed text."""
        sentences = self._split_into_sentences(text)
        key_points = []
        
        for sentence in sentences:
            if self._score_sentence_importance(sentence, 0, 1) > 0.6:
                key_points.append(sentence)
        
        return key_points[:5]  # Limit to top 5 key points
    
    def _group_sentences_semantically(self, sentences: List[str]) -> List[List[str]]:
        """Group sentences by semantic similarity (simplified approach)."""
        if len(sentences) <= 1:
            return [sentences]
        
        # Simple grouping based on shared keywords
        groups = []
        used_indices = set()
        
        for i, sentence in enumerate(sentences):
            if i in used_indices:
                continue
            
            group = [sentence]
            used_indices.add(i)
            
            # Find similar sentences
            sentence_words = set(sentence.lower().split())
            for j, other_sentence in enumerate(sentences[i+1:], i+1):
                if j in used_indices:
                    continue
                
                other_words = set(other_sentence.lower().split())
                similarity = len(sentence_words.intersection(other_words)) / len(sentence_words.union(other_words))
                
                if similarity > 0.3:  # Similarity threshold
                    group.append(other_sentence)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _calculate_quality_score(self, original_text: str, compressed_text: str) -> float:
        """Calculate quality score for compressed text."""
        if not original_text or not compressed_text:
            return 0.0
        
        # Length ratio (closer to target is better)
        length_ratio = len(compressed_text) / len(original_text)
        length_score = 1.0 - abs(length_ratio - 0.3)  # Target 30% compression
        
        # Information preservation (keyword overlap)
        original_words = set(original_text.lower().split())
        compressed_words = set(compressed_text.lower().split())
        overlap = len(original_words.intersection(compressed_words)) / len(original_words)
        
        # Trading term preservation
        trading_terms = ['strategy', 'trading', 'risk', 'portfolio', 'market', 'price', 'signal']
        original_trading_terms = sum(1 for term in trading_terms if term in original_text.lower())
        compressed_trading_terms = sum(1 for term in trading_terms if term in compressed_text.lower())
        
        if original_trading_terms > 0:
            trading_preservation = compressed_trading_terms / original_trading_terms
        else:
            trading_preservation = 1.0
        
        # Combine scores
        quality_score = (length_score * 0.3 + overlap * 0.4 + trading_preservation * 0.3)
        
        return min(quality_score, 1.0)
    
    def _update_compression_stats(self, compression_time: float, compression_ratio: float, 
                                quality_score: float, method: str) -> None:
        """Update compression statistics."""
        total_compressions = self.compression_stats['total_compressions']
        
        # Update averages
        if total_compressions > 0:
            self.compression_stats['avg_compression_ratio'] = (
                (self.compression_stats['avg_compression_ratio'] * (total_compressions - 1) + compression_ratio) 
                / total_compressions
            )
            self.compression_stats['avg_quality_score'] = (
                (self.compression_stats['avg_quality_score'] * (total_compressions - 1) + quality_score) 
                / total_compressions
            )
            self.compression_stats['avg_compression_time'] = (
                (self.compression_stats['avg_compression_time'] * (total_compressions - 1) + compression_time) 
                / total_compressions
            )
        
        # Update method usage
        if method not in self.compression_stats['method_usage']:
            self.compression_stats['method_usage'][method] = 0
        self.compression_stats['method_usage'][method] += 1
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression performance statistics."""
        return {
            'total_compressions': self.compression_stats['total_compressions'],
            'avg_compression_ratio': self.compression_stats['avg_compression_ratio'],
            'avg_quality_score': self.compression_stats['avg_quality_score'],
            'avg_compression_time': self.compression_stats['avg_compression_time'],
            'method_usage': self.compression_stats['method_usage']
        }

# Global instance
context_compressor = ContextCompressor()