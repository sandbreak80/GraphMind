# 📊 RAG Monitoring Implementation Plan

## 🎯 **Goal: Track RAG Performance with Open-Source Tools**

Based on your analysis, we'll implement a focused monitoring system using the best open-source tools for our local Docker setup.

---

## 🛠️ **Recommended Tool Stack**

### **Primary Tools:**
1. **Langfuse** - LLM observability & tracing (self-hostable)
2. **DeepEval** - RAG evaluation metrics (open-source)
3. **Custom Dashboard** - Simple monitoring interface

### **Why This Stack:**
- ✅ **Self-hostable** - Runs in our Docker environment
- ✅ **Open-source** - No vendor lock-in
- ✅ **RAG-focused** - Built for our use case
- ✅ **Lightweight** - Won't overwhelm our system

---

## 📋 **What We'll Monitor**

### **Retrieval Metrics (The "R" in RAG)**
- **Top-K retrieval count** - How many docs retrieved
- **Precision/Recall** - Relevant vs irrelevant docs
- **Retrieval latency** - Time to fetch documents
- **Source quality** - Reliability of retrieved sources
- **Token cost** - Embedding and reranking costs

### **Generation Metrics (The "G" in RAG)**
- **Response latency** - Time to generate answer
- **Token usage** - Tokens consumed per query
- **Model performance** - Which models work best
- **Answer faithfulness** - Grounded in retrieved context
- **Hallucination detection** - Unsupported facts
- **Answer relevance** - Answers the user's question

### **End-to-End Monitoring**
- **Retrieval → Generation linking** - Where failures occur
- **Model versioning** - Track model changes
- **Cost vs Quality** - Trade-off analysis
- **Drift detection** - Performance degradation over time
- **User feedback loop** - Real user ratings

---

## 🚀 **Implementation Plan** (2-3 weeks)

### **Week 1: Langfuse Setup & Integration**

#### **1.1 Langfuse Docker Setup**
```yaml
# docker-compose.yml addition
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:langfuse@postgres:5432/langfuse
      - NEXTAUTH_SECRET=your-secret-key
      - NEXTAUTH_URL=http://localhost:3000
    depends_on:
      - postgres
    volumes:
      - langfuse_data:/app/data

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=langfuse
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  langfuse_data:
  postgres_data:
```

#### **1.2 Langfuse Integration**
```python
# app/langfuse_client.py
from langfuse import Langfuse
from langfuse.decorators import observe
import os

class LangfuseClient:
    def __init__(self):
        self.client = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            host=os.getenv("LANGFUSE_HOST", "http://localhost:3000")
        )
    
    @observe(name="rag_query")
    def track_rag_query(self, query: str, model: str, response: str, 
                       retrieval_results: List[Dict], response_time: float):
        """Track a complete RAG query"""
        
        # Track retrieval phase
        retrieval_trace = self.client.trace(
            name="retrieval",
            input={"query": query},
            output={"num_docs": len(retrieval_results)},
            metadata={
                "retrieval_method": "hybrid",
                "top_k": len(retrieval_results)
            }
        )
        
        # Track generation phase
        generation_trace = self.client.trace(
            name="generation",
            input={"query": query, "context": retrieval_results},
            output={"response": response},
            metadata={
                "model": model,
                "response_time": response_time,
                "tokens_used": len(response.split())
            }
        )
        
        return retrieval_trace, generation_trace
```

#### **1.3 Integration with Main App**
```python
# Modify app/main.py
from app.langfuse_client import LangfuseClient

# Global instance
langfuse_client = LangfuseClient()

@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    start_time = time.time()
    
    try:
        # ... existing retrieval code ...
        
        # Track with Langfuse
        langfuse_client.track_rag_query(
            query=request.query,
            model=request.model,
            response=answer,
            retrieval_results=doc_results,
            response_time=time.time() - start_time
        )
        
        return AskResponse(answer=answer, citations=citations)
        
    except Exception as e:
        # Track errors
        langfuse_client.client.trace(
            name="rag_error",
            input={"query": request.query},
            output={"error": str(e)},
            level="ERROR"
        )
        raise
```

### **Week 2: DeepEval Integration**

#### **2.1 DeepEval Setup**
```python
# app/rag_evaluator.py
from deepeval import evaluate
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, ContextualPrecisionMetric
from deepeval.test_case import LLMTestCase

class RAGEvaluator:
    def __init__(self):
        self.faithfulness_metric = FaithfulnessMetric(threshold=0.7)
        self.answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
        self.contextual_precision_metric = ContextualPrecisionMetric(threshold=0.7)
    
    def evaluate_rag_response(self, query: str, context: str, answer: str) -> Dict:
        """Evaluate a single RAG response"""
        
        test_case = LLMTestCase(
            input=query,
            actual_output=answer,
            context=context
        )
        
        # Run evaluations
        faithfulness_result = self.faithfulness_metric.measure(test_case)
        relevancy_result = self.answer_relevancy_metric.measure(test_case)
        precision_result = self.contextual_precision_metric.measure(test_case)
        
        return {
            "faithfulness": faithfulness_result.score,
            "answer_relevancy": relevancy_result.score,
            "contextual_precision": precision_result.score,
            "overall_quality": (faithfulness_result.score + relevancy_result.score + precision_result.score) / 3
        }
    
    def batch_evaluate(self, test_cases: List[Dict]) -> Dict:
        """Evaluate multiple RAG responses"""
        results = []
        
        for case in test_cases:
            result = self.evaluate_rag_response(
                case["query"],
                case["context"],
                case["answer"]
            )
            results.append(result)
        
        # Calculate averages
        avg_metrics = {
            "avg_faithfulness": sum(r["faithfulness"] for r in results) / len(results),
            "avg_answer_relevancy": sum(r["answer_relevancy"] for r in results) / len(results),
            "avg_contextual_precision": sum(r["contextual_precision"] for r in results) / len(results),
            "avg_overall_quality": sum(r["overall_quality"] for r in results) / len(results),
            "total_evaluations": len(results)
        }
        
        return avg_metrics
```

#### **2.2 Evaluation Integration**
```python
# Add to app/main.py
from app.rag_evaluator import RAGEvaluator

# Global instance
rag_evaluator = RAGEvaluator()

@app.post("/evaluate/rag")
async def evaluate_rag_performance():
    """Run RAG evaluation on sample queries"""
    
    # Sample test cases (you can expand this)
    test_cases = [
        {
            "query": "What is momentum trading?",
            "context": "Momentum trading is a strategy that...",
            "answer": "Momentum trading is a strategy that..."
        },
        # Add more test cases
    ]
    
    results = rag_evaluator.batch_evaluate(test_cases)
    return results
```

### **Week 3: Dashboard & Monitoring**

#### **3.1 Monitoring API Endpoints**
```python
# Add to app/main.py
@app.get("/monitoring/langfuse")
async def get_langfuse_metrics():
    """Get Langfuse metrics"""
    # This would query Langfuse API for metrics
    return {"message": "Langfuse metrics endpoint"}

@app.get("/monitoring/deepeval")
async def get_deepeval_metrics():
    """Get DeepEval metrics"""
    # This would return evaluation results
    return {"message": "DeepEval metrics endpoint"}

@app.get("/monitoring/summary")
async def get_monitoring_summary():
    """Get comprehensive monitoring summary"""
    return {
        "langfuse_url": "http://localhost:3000",
        "deepeval_status": "active",
        "last_evaluation": "2024-12-01T10:00:00Z",
        "total_queries_tracked": 150,
        "average_response_time": 2.5,
        "average_quality_score": 0.85
    }
```

#### **3.2 Simple Monitoring Dashboard**
```typescript
// frontend/components/MonitoringDashboard.tsx
export default function MonitoringDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [langfuseUrl] = useState("http://localhost:3000");

  useEffect(() => {
    fetch('/api/monitoring/summary')
      .then(res => res.json())
      .then(setMetrics);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">RAG Performance Monitoring</h1>
      
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Total Queries</h3>
          <p className="text-3xl font-bold text-blue-600">
            {metrics?.total_queries_tracked || 0}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Avg Response Time</h3>
          <p className="text-3xl font-bold text-green-600">
            {metrics?.average_response_time?.toFixed(2)}s
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Quality Score</h3>
          <p className="text-3xl font-bold text-purple-600">
            {(metrics?.average_quality_score * 100)?.toFixed(1)}%
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Last Evaluation</h3>
          <p className="text-sm text-gray-600">
            {metrics?.last_evaluation ? new Date(metrics.last_evaluation).toLocaleDateString() : 'N/A'}
          </p>
        </div>
      </div>

      {/* External Tools */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Langfuse Tracing</h3>
          <p className="text-gray-600 mb-4">
            View detailed traces of your RAG queries, including retrieval and generation phases.
          </p>
          <a 
            href={langfuseUrl} 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Open Langfuse Dashboard
          </a>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">RAG Evaluation</h3>
          <p className="text-gray-600 mb-4">
            Run DeepEval tests to measure faithfulness, relevancy, and precision.
          </p>
          <button 
            onClick={() => fetch('/api/evaluate/rag')}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Run Evaluation
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 📊 **Key Metrics Dashboard**

### **Retrieval Metrics**
- **Top-K Count**: Average documents retrieved per query
- **Retrieval Latency**: Time to fetch documents
- **Precision/Recall**: Relevant vs irrelevant documents
- **Source Quality**: Reliability of retrieved sources

### **Generation Metrics**
- **Response Latency**: Time to generate answer
- **Token Usage**: Tokens consumed per query
- **Model Performance**: Which models work best
- **Answer Quality**: Faithfulness, relevancy, precision

### **End-to-End Metrics**
- **Overall Performance**: Combined retrieval + generation
- **Error Rate**: Failed queries percentage
- **Cost Analysis**: Token usage vs quality trade-offs
- **Trend Analysis**: Performance over time

---

## 🎯 **Usage Workflow**

### **Before Adding Features:**
1. **Capture Baseline**: Run evaluation on current system
2. **Set Alerts**: Configure thresholds for key metrics
3. **Document Current Performance**: Save baseline metrics

### **After Adding Features:**
1. **Run New Queries**: Collect performance data
2. **Compare Metrics**: Before vs after analysis
3. **Measure Impact**: Quantify improvements
4. **Optimize**: Adjust based on monitoring data

### **Ongoing Monitoring:**
1. **Check Dashboard**: Daily performance review
2. **Monitor Trends**: Weekly performance analysis
3. **Run Evaluations**: Regular quality assessments
4. **Optimize Continuously**: Based on monitoring insights

---

## 🚀 **Implementation Benefits**

### **Immediate Value:**
- **Performance Visibility**: See exactly how your RAG system performs
- **Quality Assurance**: Ensure answers are faithful and relevant
- **Cost Optimization**: Track token usage and optimize costs
- **Debugging**: Quickly identify where problems occur

### **Long-term Value:**
- **Feature Impact**: Measure the impact of new features
- **Performance Trends**: Track improvements over time
- **User Experience**: Ensure consistent quality
- **System Optimization**: Data-driven improvements

---

## 💡 **Why This Approach Works**

1. **Focused**: Only monitors what matters for RAG systems
2. **Open-source**: No vendor lock-in, full control
3. **Local**: Runs in our Docker environment
4. **Actionable**: Metrics directly inform development decisions
5. **Scalable**: Easy to add more monitoring as needed

This gives us professional-grade RAG monitoring without the complexity of enterprise tools, perfectly suited for our local development and feature development workflow!