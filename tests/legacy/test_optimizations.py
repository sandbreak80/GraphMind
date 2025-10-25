#!/usr/bin/env python3
"""Test script for performance optimizations in development instance."""
import requests
import time
import statistics
import json

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
    
    response_times = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer length: {len(data.get('answer', ''))}")
                print(f"   📚 Citations: {len(data.get('citations', []))}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 60s")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test monitoring endpoints
    print(f"\n📊 Performance Metrics:")
    try:
        perf_response = requests.get(f"{base_url}/api/monitoring/performance")
        if perf_response.status_code == 200:
            metrics = perf_response.json()
            print(f"   Total queries: {metrics.get('total_queries', 0)}")
            print(f"   Avg response time: {metrics.get('avg_response_time', 0):.2f}s")
            print(f"   Error rate: {metrics.get('error_rate', 0):.2%}")
            print(f"   Model usage: {metrics.get('model_usage', {})}")
        else:
            print(f"   ❌ Failed to get performance metrics: {perf_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting performance metrics: {e}")
    
    print(f"\n💾 Cache Metrics:")
    try:
        cache_response = requests.get(f"{base_url}/api/monitoring/cache")
        if cache_response.status_code == 200:
            cache_metrics = cache_response.json()
            print(f"   Cache hits: {cache_metrics.get('hits', 0)}")
            print(f"   Cache misses: {cache_metrics.get('misses', 0)}")
            print(f"   Hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
        else:
            print(f"   ❌ Failed to get cache metrics: {cache_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting cache metrics: {e}")
    
    # Summary
    if response_times:
        print(f"\n📈 Summary:")
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        print(f"   Total queries tested: {len(response_times)}")

if __name__ == "__main__":
    test_optimizations()