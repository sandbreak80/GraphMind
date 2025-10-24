#!/usr/bin/env python3
"""
Comprehensive RAG performance analysis and optimization recommendations
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any

def test_rag_performance():
    """Test RAG performance across different scenarios"""
    
    base_url = "http://localhost:3001"
    
    # Get auth token
    print("🔐 Authenticating...")
    try:
        auth_response = requests.post(f"{base_url}/api/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        if auth_response.status_code != 200:
            print(f"❌ Auth failed: {auth_response.status_code}")
            return
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return
    
    # Test queries with different complexity levels
    test_queries = [
        {
            "name": "Simple Query",
            "query": "What is trading?",
            "expected_complexity": "low"
        },
        {
            "name": "Medium Query", 
            "query": "What are the best trading strategies for futures markets?",
            "expected_complexity": "medium"
        },
        {
            "name": "Complex Query",
            "query": "Compare and contrast different technical analysis approaches for E-mini S&P 500 futures trading, including their advantages and disadvantages",
            "expected_complexity": "high"
        },
        {
            "name": "Research Query",
            "query": "Analyze the current market conditions and provide a comprehensive trading strategy recommendation based on technical indicators and market sentiment",
            "expected_complexity": "very_high"
        }
    ]
    
    # Test different retrieval settings
    retrieval_configs = [
        {
            "name": "Fast (Low Recall)",
            "bm25_top_k": 10,
            "embedding_top_k": 10,
            "rerank_top_k": 3
        },
        {
            "name": "Balanced (Current)",
            "bm25_top_k": 30,
            "embedding_top_k": 30,
            "rerank_top_k": 8
        },
        {
            "name": "Comprehensive (High Recall)",
            "bm25_top_k": 50,
            "embedding_top_k": 50,
            "rerank_top_k": 15
        }
    ]
    
    results = []
    
    print("\n🧪 Testing RAG Performance...")
    print("=" * 60)
    
    for config in retrieval_configs:
        print(f"\n📊 Testing {config['name']} Configuration:")
        print(f"   BM25: {config['bm25_top_k']}, Embedding: {config['embedding_top_k']}, Rerank: {config['rerank_top_k']}")
        
        config_results = []
        
        for test_case in test_queries:
            print(f"\n   🔍 {test_case['name']}: {test_case['query'][:50]}...")
            
            # Test multiple times for average
            times = []
            response_lengths = []
            source_counts = []
            
            for i in range(3):  # 3 runs per test
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{base_url}/api/ask-enhanced",
                        headers=headers,
                        json={
                            "query": test_case["query"],
                            "mode": "qa",
                            "bm25_top_k": config["bm25_top_k"],
                            "embedding_top_k": config["embedding_top_k"],
                            "rerank_top_k": config["rerank_top_k"],
                            "temperature": 0.1,
                            "max_tokens": 2000
                        },
                        timeout=60
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        times.append(response_time)
                        response_lengths.append(len(data.get('answer', '')))
                        source_counts.append(len(data.get('citations', [])))
                        
                        print(f"      Run {i+1}: {response_time:.2f}s, {len(data.get('answer', ''))} chars, {len(data.get('citations', []))} sources")
                    else:
                        print(f"      Run {i+1}: FAILED ({response.status_code})")
                        
                except Exception as e:
                    print(f"      Run {i+1}: ERROR - {e}")
            
            if times:
                avg_time = statistics.mean(times)
                avg_length = statistics.mean(response_lengths)
                avg_sources = statistics.mean(source_counts)
                
                config_results.append({
                    "test_case": test_case["name"],
                    "complexity": test_case["expected_complexity"],
                    "avg_time": avg_time,
                    "avg_length": avg_length,
                    "avg_sources": avg_sources,
                    "times": times
                })
                
                print(f"      📈 Average: {avg_time:.2f}s, {avg_length:.0f} chars, {avg_sources:.1f} sources")
        
        results.append({
            "config": config,
            "results": config_results
        })
    
    # Analyze results
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    for config_result in results:
        config = config_result["config"]
        results_data = config_result["results"]
        
        print(f"\n🔧 {config['name']} Configuration:")
        
        if results_data:
            avg_times = [r["avg_time"] for r in results_data]
            avg_lengths = [r["avg_length"] for r in results_data]
            avg_sources = [r["avg_sources"] for r in results_data]
            
            print(f"   ⏱️  Average Response Time: {statistics.mean(avg_times):.2f}s")
            print(f"   📝 Average Response Length: {statistics.mean(avg_lengths):.0f} characters")
            print(f"   📚 Average Sources: {statistics.mean(avg_sources):.1f}")
            print(f"   🚀 Fastest Query: {min(avg_times):.2f}s")
            print(f"   🐌 Slowest Query: {max(avg_times):.2f}s")
            
            # Performance by complexity
            complexity_performance = {}
            for result in results_data:
                complexity = result["complexity"]
                if complexity not in complexity_performance:
                    complexity_performance[complexity] = []
                complexity_performance[complexity].append(result["avg_time"])
            
            print(f"   📈 Performance by Complexity:")
            for complexity, times in complexity_performance.items():
                print(f"      {complexity}: {statistics.mean(times):.2f}s avg")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    
    # Find best performing config
    best_config = None
    best_avg_time = float('inf')
    
    for config_result in results:
        if config_result["results"]:
            avg_times = [r["avg_time"] for r in config_result["results"]]
            config_avg = statistics.mean(avg_times)
            if config_avg < best_avg_time:
                best_avg_time = config_avg
                best_config = config_result["config"]
    
    if best_config:
        print(f"🏆 Best Performing Configuration: {best_config['name']}")
        print(f"   Settings: BM25={best_config['bm25_top_k']}, Embedding={best_config['embedding_top_k']}, Rerank={best_config['rerank_top_k']}")
        print(f"   Average Time: {best_avg_time:.2f}s")
    
    print("\n🔧 Specific Optimization Opportunities:")
    print("   1. Consider implementing query caching for repeated queries")
    print("   2. Add parallel processing for BM25 and embedding searches")
    print("   3. Implement result prefetching for common query patterns")
    print("   4. Add query complexity detection to adjust retrieval parameters")
    print("   5. Consider implementing hybrid retrieval with different models")
    print("   6. Add response streaming for long queries")
    print("   7. Implement query result caching with TTL")
    print("   8. Add query preprocessing to optimize retrieval parameters")
    
    return results

if __name__ == "__main__":
    test_rag_performance()