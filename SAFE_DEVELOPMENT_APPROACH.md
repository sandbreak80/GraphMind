# 🛡️ Safe Development Approach - Checkpoint & Parallel Development

## 🎯 **Goal: Make Changes Safely Without Breaking Production**

Yes, this is absolutely a best practice! We'll create a checkpoint and run our improvements in a separate development instance.

---

## 📋 **Step 1: Create System Checkpoint**

### **1.1 Git Checkpoint**
```bash
# Create a checkpoint branch
git checkout -b checkpoint-before-optimizations
git add .
git commit -m "Checkpoint: System before performance optimizations"
git push origin checkpoint-before-optimizations

# Create development branch
git checkout -b development-performance-optimizations
```

### **1.2 Docker State Checkpoint**
```bash
# Save current Docker images
docker save emini-rag:latest > checkpoint-emini-rag.tar
docker save config-frontend:latest > checkpoint-frontend.tar

# Save Docker volumes (if needed)
docker run --rm -v emini-rag_chroma_data:/data -v $(pwd):/backup alpine tar czf /backup/chroma-data-backup.tar.gz -C /data .
```

### **1.3 Configuration Backup**
```bash
# Backup current configurations
cp docker-compose.yml docker-compose.yml.checkpoint
cp -r app/ app-checkpoint/
cp -r frontend/ frontend-checkpoint/
```

---

## 🚀 **Step 2: Set Up Development Instance**

### **2.1 Development Docker Compose**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  # Development RAG service
  rag-service-dev:
    build: .
    container_name: emini-rag-dev
    ports:
      - "8002:8001"  # Different port
    volumes:
      - ./documents:/workspace/documents:ro
      - ./outputs:/workspace/outputs
      - ./app:/workspace/app  # Live code reload
    environment:
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    networks:
      - dev-network

  # Development frontend
  frontend-dev:
    build: ./frontend
    container_name: config-frontend-dev
    ports:
      - "3002:3000"  # Different port
    volumes:
      - ./frontend:/app  # Live code reload
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8002
    networks:
      - dev-network

  # Development ChromaDB
  chromadb-dev:
    image: chromadb/chroma:latest
    container_name: chromadb-dev
    ports:
      - "8003:8000"  # Different port
    volumes:
      - chromadb_dev_data:/chroma/chroma
    networks:
      - dev-network

  # Development Ollama
  ollama-dev:
    image: ollama/ollama:latest
    container_name: ollama-dev
    ports:
      - "11435:11434"  # Different port
    volumes:
      - ollama_dev_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  chromadb_dev_data:
  ollama_dev_data:
```

### **2.2 Development Environment Setup**
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f rag-service-dev
```

---

## 🔧 **Step 3: Implement Changes in Development**

### **3.1 Basic Monitoring Implementation**
```python
# app/monitoring.py
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
```

### **3.2 Query Caching Implementation**
```python
# app/caching.py
import hashlib
import json
import time
from functools import lru_cache
from typing import Optional, Dict, Any

class QueryCache:
    """Simple query caching with TTL."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _get_cache_key(self, query: str, model: str, **kwargs) -> str:
        """Generate cache key from query and parameters."""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Create hash of query + model + relevant parameters
        cache_data = {
            'query': normalized_query,
            'model': model,
            'temperature': kwargs.get('temperature', 0.1),
            'max_tokens': kwargs.get('max_tokens', 2000)
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get(self, query: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        cache_key = self._get_cache_key(query, model, **kwargs)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # Check TTL
            if time.time() - cached_data['timestamp'] < self.ttl_seconds:
                self.hits += 1
                return cached_data['response']
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        
        self.misses += 1
        return None
    
    def set(self, query: str, model: str, response: Dict[str, Any], **kwargs):
        """Cache response."""
        cache_key = self._get_cache_key(query, model, **kwargs)
        
        # Simple LRU: remove oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / max(1, total_requests)
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }

# Global instance
query_cache = QueryCache()
```

### **3.3 Smart Model Selection**
```python
# app/model_selector.py
import re
from typing import Dict, List, Any

class ModelSelector:
    """Smart model selection based on query characteristics."""
    
    def __init__(self):
        self.models = {
            'simple': 'llama3.2:3b',      # Fastest
            'medium': 'llama3.1:latest',   # Balanced
            'complex': 'qwen2.5-coder:14b', # More capable
            'research': 'gpt-oss:20b'      # Most capable
        }
        
        # Query complexity indicators
        self.complex_indicators = [
            'analyze', 'compare', 'explain', 'evaluate', 'research',
            'strategy', 'technical', 'fundamental', 'backtest',
            'correlation', 'regression', 'optimization'
        ]
        
        self.research_indicators = [
            'comprehensive', 'detailed', 'thorough', 'in-depth',
            'extensive', 'complete', 'full analysis'
        ]
    
    def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine complexity."""
        query_lower = query.lower()
        words = query.split()
        
        # Basic metrics
        word_count = len(words)
        char_count = len(query)
        
        # Complexity indicators
        complex_count = sum(1 for indicator in self.complex_indicators 
                           if indicator in query_lower)
        research_count = sum(1 for indicator in self.research_indicators 
                            if indicator in query_lower)
        
        # Question complexity
        question_marks = query.count('?')
        has_multiple_questions = question_marks > 1
        
        # Technical terms (trading-specific)
        technical_terms = [
            'rsi', 'macd', 'bollinger', 'vwap', 'support', 'resistance',
            'momentum', 'volatility', 'trend', 'breakout', 'reversal'
        ]
        technical_count = sum(1 for term in technical_terms 
                             if term in query_lower)
        
        return {
            'word_count': word_count,
            'char_count': char_count,
            'complex_indicators': complex_count,
            'research_indicators': research_count,
            'technical_terms': technical_count,
            'has_multiple_questions': has_multiple_questions,
            'question_marks': question_marks
        }
    
    def select_model(self, query: str) -> str:
        """Select best model for query."""
        analysis = self.analyze_query_complexity(query)
        
        # Research queries (highest complexity)
        if (analysis['research_indicators'] > 0 or 
            analysis['word_count'] > 30 or 
            analysis['has_multiple_questions']):
            return self.models['research']
        
        # Complex queries
        elif (analysis['complex_indicators'] > 1 or 
              analysis['word_count'] > 15 or 
              analysis['technical_terms'] > 2):
            return self.models['complex']
        
        # Medium queries
        elif (analysis['word_count'] > 5 or 
              analysis['complex_indicators'] > 0 or 
              analysis['technical_terms'] > 0):
            return self.models['medium']
        
        # Simple queries
        else:
            return self.models['simple']
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        model_info = {
            'llama3.2:3b': {
                'name': 'Llama 3.2 3B',
                'speed': 'Fastest',
                'capability': 'Basic',
                'use_case': 'Simple questions'
            },
            'llama3.1:latest': {
                'name': 'Llama 3.1 Latest',
                'speed': 'Fast',
                'capability': 'Balanced',
                'use_case': 'General questions'
            },
            'qwen2.5-coder:14b': {
                'name': 'Qwen 2.5 Coder 14B',
                'speed': 'Medium',
                'capability': 'High',
                'use_case': 'Complex analysis'
            },
            'gpt-oss:20b': {
                'name': 'GPT-OSS 20B',
                'speed': 'Slowest',
                'capability': 'Highest',
                'use_case': 'Research & analysis'
            }
        }
        return model_info.get(model, {'name': 'Unknown', 'speed': 'Unknown'})

# Global instance
model_selector = ModelSelector()
```

---

## 🔧 **Step 4: Integration with Main App**

### **4.1 Update Main App**
```python
# Add to app/main.py
from app.monitoring import monitor
from app.caching import query_cache
from app.model_selector import model_selector

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    start_time = time.time()
    
    try:
        # Smart model selection
        selected_model = model_selector.select_model(request.query)
        if request.model != selected_model:
            logger.info(f"Model auto-selected: {selected_model} (requested: {request.model})")
        
        # Check cache first
        cached_response = query_cache.get(
            query=request.query,
            model=selected_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if cached_response:
            logger.info("Cache hit - returning cached response")
            response_time = time.time() - start_time
            monitor.track_query(
                query=request.query,
                model=selected_model,
                response_time=response_time,
                query_type="cached",
                success=True
            )
            return AskResponse(**cached_response)
        
        # Process query normally
        # ... existing code ...
        
        # Cache the response
        response_data = {
            "answer": answer,
            "citations": [{"text": r['text'], "source": r['metadata'].get('file_name', 'Unknown')} 
                         for r in doc_results]
        }
        query_cache.set(
            query=request.query,
            model=selected_model,
            response=response_data,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Track performance
        response_time = time.time() - start_time
        monitor.track_query(
            query=request.query,
            model=selected_model,
            response_time=response_time,
            query_type="normal",
            success=True
        )
        
        return AskResponse(answer=answer, citations=citations)
        
    except Exception as e:
        response_time = time.time() - start_time
        monitor.track_query(
            query=request.query,
            model=request.model,
            response_time=response_time,
            query_type="error",
            success=False
        )
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New monitoring endpoints
@app.get("/monitoring/performance")
async def get_performance_metrics():
    """Get current performance metrics."""
    return monitor.get_summary()

@app.get("/monitoring/cache")
async def get_cache_metrics():
    """Get cache statistics."""
    return query_cache.get_stats()

@app.get("/monitoring/recent")
async def get_recent_queries(count: int = 10):
    """Get recent query response times."""
    return {"recent_times": monitor.get_recent_queries(count)}
```

---

## 🧪 **Step 5: Testing in Development**

### **5.1 Test Script**
```python
# test_optimizations.py
import requests
import time
import statistics

def test_optimizations():
    base_url = "http://localhost:8002"  # Development instance
    
    test_queries = [
        "What is momentum trading?",
        "Explain RSI indicator",
        "Compare different trading strategies",
        "Analyze the current market conditions and provide a comprehensive trading strategy recommendation",
        "What is momentum trading?",  # Repeat for cache test
    ]
    
    print("🧪 Testing Optimizations in Development Instance")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/ask",
            json={
                "query": query,
                "temperature": 0.1,
                "max_tokens": 1000
            }
        )
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {end_time - start_time:.2f}s")
            print(f"   📝 Answer length: {len(data.get('answer', ''))}")
            print(f"   📚 Citations: {len(data.get('citations', []))}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    
    # Test monitoring endpoints
    print(f"\n📊 Performance Metrics:")
    perf_response = requests.get(f"{base_url}/api/monitoring/performance")
    if perf_response.status_code == 200:
        metrics = perf_response.json()
        print(f"   Total queries: {metrics.get('total_queries', 0)}")
        print(f"   Avg response time: {metrics.get('avg_response_time', 0):.2f}s")
        print(f"   Error rate: {metrics.get('error_rate', 0):.2%}")
    
    print(f"\n💾 Cache Metrics:")
    cache_response = requests.get(f"{base_url}/api/monitoring/cache")
    if cache_response.status_code == 200:
        cache_metrics = cache_response.json()
        print(f"   Cache hits: {cache_metrics.get('hits', 0)}")
        print(f"   Cache misses: {cache_metrics.get('misses', 0)}")
        print(f"   Hit rate: {cache_metrics.get('hit_rate', 0):.2%}")

if __name__ == "__main__":
    test_optimizations()
```

---

## 🚀 **Step 6: Deployment Strategy**

### **6.1 Gradual Rollout**
1. **Test in development** - Validate all improvements
2. **Deploy to production** - Replace current system
3. **Monitor closely** - Watch for any issues
4. **Rollback plan** - Quick revert if needed

### **6.2 Rollback Plan**
```bash
# If issues occur, quick rollback
git checkout checkpoint-before-optimizations
docker-compose down
docker-compose up -d

# Or restore from checkpoint images
docker load < checkpoint-emini-rag.tar
docker load < checkpoint-frontend.tar
```

---

## 📊 **Expected Results**

### **Performance Improvements:**
- **Simple queries**: 34s → 8-12s (70% improvement)
- **Medium queries**: 34s → 15-20s (50% improvement)
- **Repeated queries**: 34s → 2-3s (90% improvement)

### **New Capabilities:**
- **Real-time monitoring** of performance
- **Smart model selection** based on query complexity
- **Query caching** for instant repeated responses
- **Full observability** into system behavior

This approach ensures we can make improvements safely while keeping our production system running!