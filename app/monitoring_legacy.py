"""Simple performance monitoring for RAG system."""
import time
import logging
from typing import Dict, List, Any
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class SimpleMonitor:
    """Simple performance monitoring for RAG system."""
    
    def __init__(self, max_history: int = 1000):
        self.metrics = {
            'response_times': deque(maxlen=max_history),
            'model_usage': defaultdict(int),
            'query_types': defaultdict(int),
            'error_count': 0,
            'total_queries': 0
        }
        self.start_time = time.time()
    
    def track_query(self, query: str, model: str, response_time: float, 
                   query_type: str = "unknown", success: bool = True):
        """Track a single query performance."""
        self.metrics['response_times'].append(response_time)
        self.metrics['model_usage'][model] += 1
        self.metrics['query_types'][query_type] += 1
        self.metrics['total_queries'] += 1
        
        if not success:
            self.metrics['error_count'] += 1
        
        logger.info(f"Query tracked: {model} - {response_time:.2f}s - {query_type}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics['response_times']:
            return {"message": "No data yet"}
        
        response_times = list(self.metrics['response_times'])
        avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "total_queries": self.metrics['total_queries'],
            "avg_response_time": avg_response_time,
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "error_rate": self.metrics['error_count'] / max(1, self.metrics['total_queries']),
            "model_usage": dict(self.metrics['model_usage']),
            "query_types": dict(self.metrics['query_types']),
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_recent_queries(self, count: int = 10) -> List[float]:
        """Get recent response times."""
        return list(self.metrics['response_times'])[-count:]

# Global instance
monitor = SimpleMonitor()