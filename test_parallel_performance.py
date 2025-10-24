#!/usr/bin/env python3
"""
Test parallel processing performance improvements
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any

def test_parallel_performance():
    """Test parallel processing performance improvements"""
    
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
    
    # Test queries
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
            "query": "Compare and contrast different technical analysis approaches for E-mini S&P 500 futures trading",
            "expected_complexity": "high"
        }
    ]
    
    # Test configurations
    test_configs = [
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
        }
    ]
    
    print("\n🧪 Testing Parallel Processing Performance...")
    print("=" * 60)
    
    results = []
    
    for config in test_configs:
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
                        f"{base_url}/api/ask",
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
                        print(f"      Run {i+1}: FAILED ({response.status_code}) - {response.text}")
                        
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
    print("📊 PARALLEL PROCESSING PERFORMANCE ANALYSIS")
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
    
    # Compare with baseline (from previous test)
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 60)
    
    # Previous baseline (from rag_performance_analysis.py)
    baseline_times = {
        "Fast (Low Recall)": 34.46,
        "Balanced (Current)": 36.29
    }
    
    for config_result in results:
        config = config_result["config"]
        results_data = config_result["results"]
        
        if results_data and config["name"] in baseline_times:
            current_avg = statistics.mean([r["avg_time"] for r in results_data])
            baseline_avg = baseline_times[config["name"]]
            improvement = ((baseline_avg - current_avg) / baseline_avg) * 100
            
            print(f"\n🔧 {config['name']}:")
            print(f"   📊 Baseline: {baseline_avg:.2f}s")
            print(f"   📊 Current:  {current_avg:.2f}s")
            print(f"   📈 Improvement: {improvement:.1f}% faster")
            
            if improvement > 0:
                print(f"   ✅ SUCCESS: {improvement:.1f}% performance improvement!")
            else:
                print(f"   ⚠️  No improvement detected")
    
    print("\n" + "=" * 60)
    print("🎯 PARALLEL PROCESSING IMPACT SUMMARY")
    print("=" * 60)
    
    # Calculate overall improvement
    all_current_times = []
    all_baseline_times = []
    
    for config_result in results:
        config = config_result["config"]
        results_data = config_result["results"]
        
        if results_data and config["name"] in baseline_times:
            all_current_times.extend([r["avg_time"] for r in results_data])
            all_baseline_times.extend([baseline_times[config["name"]]] * len(results_data))
    
    if all_current_times and all_baseline_times:
        overall_improvement = ((statistics.mean(all_baseline_times) - statistics.mean(all_current_times)) / statistics.mean(all_baseline_times)) * 100
        
        print(f"📊 Overall Performance Improvement: {overall_improvement:.1f}%")
        print(f"📊 Average Response Time: {statistics.mean(all_baseline_times):.2f}s → {statistics.mean(all_current_times):.2f}s")
        
        if overall_improvement > 10:
            print("🎉 EXCELLENT: Significant performance improvement achieved!")
        elif overall_improvement > 5:
            print("✅ GOOD: Noticeable performance improvement achieved!")
        elif overall_improvement > 0:
            print("👍 MODEST: Some performance improvement achieved!")
        else:
            print("⚠️  No significant improvement detected. May need further optimization.")
    
    return results

if __name__ == "__main__":
    test_parallel_performance()