"""
Prometheus metrics for Prompt Uplift Pipeline.

Tracks latency, confidence, expansion counts, and violations.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import prometheus_client, fall back to simple metrics if not available
try:
    from prometheus_client import Histogram, Counter, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("prometheus_client not available, using simple metrics")


class PromptUpliftMetrics:
    """Metrics for prompt uplift pipeline."""
    
    def __init__(self):
        """Initialize metrics."""
        if PROMETHEUS_AVAILABLE:
            # Latency metrics
            self.prompt_uplift_latency = Histogram(
                'rag_prompt_uplift_latency_seconds',
                'Prompt uplift pipeline latency by stage',
                ['stage']  # classify, uplift, expand, total
            )
            
            # Quality metrics
            self.prompt_uplift_confidence = Histogram(
                'rag_prompt_uplift_confidence',
                'Uplift confidence score distribution'
            )
            
            # Usage metrics
            self.prompt_expansion_count = Histogram(
                'rag_prompt_expansion_count',
                'Number of expansions generated per query'
            )
            
            self.query_improvement_score = Histogram(
                'rag_query_improvement_score',
                'Quality score of uplift (0.0-1.0)'
            )
            
            # Violation tracking
            self.fact_injection_violations = Counter(
                'rag_fact_injection_violations_total',
                'Count of detected fact injection violations'
            )
            
            # Cache metrics
            self.uplift_cache_hits = Counter(
                'rag_uplift_cache_hits_total',
                'Cache hits for uplift pipeline'
            )
            
            self.uplift_cache_misses = Counter(
                'rag_uplift_cache_misses_total',
                'Cache misses for uplift pipeline'
            )
            
            # Fallback metrics
            self.uplift_fallback_original = Counter(
                'rag_uplift_fallback_original_total',
                'Count of fallbacks to original query (low confidence)'
            )
            
            self.uplift_skip_expansion = Counter(
                'rag_uplift_skip_expansion_total',
                'Count of skipped expansions (good baseline)'
            )
            
            # Classification metrics
            self.classification_by_type = Counter(
                'rag_classification_by_type_total',
                'Query classifications by task type',
                ['task_type']
            )
        else:
            # Simple metrics fallback
            self._simple_metrics = {
                'latency': {'classify': [], 'uplift': [], 'expand': [], 'total': []},
                'confidence': [],
                'expansion_count': [],
                'cache_hits': 0,
                'cache_misses': 0,
                'fallbacks': 0,
                'violations': 0
            }
    
    def record_latency(self, stage: str, latency_seconds: float):
        """Record latency for a specific stage."""
        if PROMETHEUS_AVAILABLE:
            self.prompt_uplift_latency.labels(stage=stage).observe(latency_seconds)
        else:
            if stage in self._simple_metrics['latency']:
                self._simple_metrics['latency'][stage].append(latency_seconds)
                # Keep only last 1000
                if len(self._simple_metrics['latency'][stage]) > 1000:
                    self._simple_metrics['latency'][stage] = self._simple_metrics['latency'][stage][-1000:]
    
    def record_confidence(self, confidence: float):
        """Record uplift confidence score."""
        if PROMETHEUS_AVAILABLE:
            self.prompt_uplift_confidence.observe(confidence)
        else:
            self._simple_metrics['confidence'].append(confidence)
            if len(self._simple_metrics['confidence']) > 1000:
                self._simple_metrics['confidence'] = self._simple_metrics['confidence'][-1000:]
    
    def record_expansion_count(self, count: int):
        """Record number of expansions generated."""
        if PROMETHEUS_AVAILABLE:
            self.prompt_expansion_count.observe(count)
        else:
            self._simple_metrics['expansion_count'].append(count)
            if len(self._simple_metrics['expansion_count']) > 1000:
                self._simple_metrics['expansion_count'] = self._simple_metrics['expansion_count'][-1000:]
    
    def record_improvement_score(self, score: float):
        """Record query improvement score."""
        if PROMETHEUS_AVAILABLE:
            self.query_improvement_score.observe(score)
        else:
            # Store in confidence for now
            pass
    
    def record_fact_injection_violation(self):
        """Record fact injection violation."""
        if PROMETHEUS_AVAILABLE:
            self.fact_injection_violations.inc()
        else:
            self._simple_metrics['violations'] += 1
    
    def record_cache_hit(self):
        """Record cache hit."""
        if PROMETHEUS_AVAILABLE:
            self.uplift_cache_hits.inc()
        else:
            self._simple_metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        if PROMETHEUS_AVAILABLE:
            self.uplift_cache_misses.inc()
        else:
            self._simple_metrics['cache_misses'] += 1
    
    def record_fallback(self):
        """Record fallback to original query."""
        if PROMETHEUS_AVAILABLE:
            self.uplift_fallback_original.inc()
        else:
            self._simple_metrics['fallbacks'] += 1
    
    def record_skip_expansion(self):
        """Record skipped expansion."""
        if PROMETHEUS_AVAILABLE:
            self.uplift_skip_expansion.inc()
        else:
            pass
    
    def record_classification(self, task_type: str):
        """Record classification by task type."""
        if PROMETHEUS_AVAILABLE:
            self.classification_by_type.labels(task_type=task_type).inc()
        else:
            pass
    
    def get_stats(self) -> dict:
        """Get current metrics statistics."""
        if PROMETHEUS_AVAILABLE:
            # Prometheus metrics are exposed via /metrics endpoint
            return {"prometheus": "enabled"}
        else:
            # Calculate simple statistics
            stats = {}
            
            for stage, latencies in self._simple_metrics['latency'].items():
                if latencies:
                    stats[f'{stage}_latency'] = {
                        'avg': sum(latencies) / len(latencies),
                        'min': min(latencies),
                        'max': max(latencies),
                        'count': len(latencies)
                    }
            
            if self._simple_metrics['confidence']:
                stats['confidence'] = {
                    'avg': sum(self._simple_metrics['confidence']) / len(self._simple_metrics['confidence']),
                    'min': min(self._simple_metrics['confidence']),
                    'max': max(self._simple_metrics['confidence'])
                }
            
            stats['cache'] = {
                'hits': self._simple_metrics['cache_hits'],
                'misses': self._simple_metrics['cache_misses'],
                'hit_rate': self._simple_metrics['cache_hits'] / max(1, self._simple_metrics['cache_hits'] + self._simple_metrics['cache_misses'])
            }
            
            stats['fallbacks'] = self._simple_metrics['fallbacks']
            stats['violations'] = self._simple_metrics['violations']
            
            return stats


# Global metrics instance
prompt_uplift_metrics = PromptUpliftMetrics()
