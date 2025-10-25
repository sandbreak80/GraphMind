#!/usr/bin/env python3
"""Stress test for the optimized system."""
import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

def stress_test():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("⚡ Stress Test for Optimized System")
    print("=" * 50)
    
    # Test queries of varying complexity
    test_queries = [
        "What is trading?",
        "Explain RSI indicator",
        "What is momentum trading?",
        "Compare different strategies",
        "Analyze market conditions",
        "What is MACD?",
        "Explain VWAP",
        "What is Bollinger Bands?",
        "Compare momentum and mean reversion",
        "Analyze current market trends"
    ]
    
    # Results storage
    results = []
    errors = []
    
    def make_request(query, request_id):
        """Make a single request and return results."""
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'request_id': request_id,
                'query': query,
                'success': response.status_code == 200,
                'response_time': response_time,
                'status_code': response.status_code,
                'answer_length': len(response.json().get('answer', '')) if response.status_code == 200 else 0
            }
        except Exception as e:
            return {
                'request_id': request_id,
                'query': query,
                'success': False,
                'response_time': 0,
                'error': str(e)
            }
    
    # Test 1: Sequential requests (baseline)
    print("\n1. Sequential Requests (Baseline)")
    print("-" * 30)
    
    start_time = time.time()
    for i, query in enumerate(test_queries):
        result = make_request(query, i)
        results.append(result)
        if result['success']:
            print(f"   Request {i+1}: {result['response_time']:.2f}s")
        else:
            print(f"   Request {i+1}: FAILED - {result.get('error', 'Unknown error')}")
    sequential_time = time.time() - start_time
    
    # Test 2: Concurrent requests (5 threads)
    print(f"\n2. Concurrent Requests (5 threads)")
    print("-" * 30)
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, query, i) for i, query in enumerate(test_queries)]
        concurrent_results = []
        
        for future in as_completed(futures):
            result = future.result()
            concurrent_results.append(result)
            if result['success']:
                print(f"   Request {result['request_id']+1}: {result['response_time']:.2f}s")
            else:
                print(f"   Request {result['request_id']+1}: FAILED - {result.get('error', 'Unknown error')}")
    
    concurrent_time = time.time() - start_time
    
    # Test 3: High load (10 threads)
    print(f"\n3. High Load Test (10 threads)")
    print("-" * 30)
    
    # Create more queries for high load
    high_load_queries = test_queries * 2  # 20 queries total
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, query, i) for i, query in enumerate(high_load_queries)]
        high_load_results = []
        
        for future in as_completed(futures):
            result = future.result()
            high_load_results.append(result)
            if result['success']:
                print(f"   Request {result['request_id']+1}: {result['response_time']:.2f}s")
            else:
                print(f"   Request {result['request_id']+1}: FAILED - {result.get('error', 'Unknown error')}")
    
    high_load_time = time.time() - start_time
    
    # Analysis
    print(f"\n📊 STRESS TEST ANALYSIS")
    print("=" * 50)
    
    # Sequential analysis
    sequential_successful = [r for r in results if r['success']]
    if sequential_successful:
        sequential_times = [r['response_time'] for r in sequential_successful]
        print(f"\nSequential Requests:")
        print(f"   Successful: {len(sequential_successful)}/{len(test_queries)}")
        print(f"   Total time: {sequential_time:.2f}s")
        print(f"   Average response time: {statistics.mean(sequential_times):.2f}s")
        print(f"   Requests per second: {len(sequential_successful)/sequential_time:.2f}")
    
    # Concurrent analysis
    concurrent_successful = [r for r in concurrent_results if r['success']]
    if concurrent_successful:
        concurrent_times = [r['response_time'] for r in concurrent_successful]
        print(f"\nConcurrent Requests (5 threads):")
        print(f"   Successful: {len(concurrent_successful)}/{len(test_queries)}")
        print(f"   Total time: {concurrent_time:.2f}s")
        print(f"   Average response time: {statistics.mean(concurrent_times):.2f}s")
        print(f"   Requests per second: {len(concurrent_successful)/concurrent_time:.2f}")
    
    # High load analysis
    high_load_successful = [r for r in high_load_results if r['success']]
    if high_load_successful:
        high_load_times = [r['response_time'] for r in high_load_successful]
        print(f"\nHigh Load (10 threads, 20 queries):")
        print(f"   Successful: {len(high_load_successful)}/{len(high_load_queries)}")
        print(f"   Total time: {high_load_time:.2f}s")
        print(f"   Average response time: {statistics.mean(high_load_times):.2f}s")
        print(f"   Requests per second: {len(high_load_successful)/high_load_time:.2f}")
    
    # Performance comparison
    if sequential_successful and concurrent_successful:
        speedup = (len(concurrent_successful)/concurrent_time) / (len(sequential_successful)/sequential_time)
        print(f"\n🚀 Performance Improvement:")
        print(f"   Concurrent vs Sequential speedup: {speedup:.2f}x")
    
    # Check monitoring after stress test
    print(f"\n📊 Post-Stress Monitoring:")
    try:
        response = requests.get(f"{base_url}/monitoring/performance")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   Total queries processed: {metrics.get('total_queries', 0)}")
            print(f"   Average response time: {metrics.get('avg_response_time', 0):.2f}s")
            print(f"   Error rate: {metrics.get('error_rate', 0):.2%}")
            print(f"   Model usage: {metrics.get('model_usage', {})}")
        
        response = requests.get(f"{base_url}/monitoring/cache")
        if response.status_code == 200:
            cache_metrics = response.json()
            print(f"   Cache hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
            print(f"   Cache size: {cache_metrics.get('cache_size', 0)}")
    except Exception as e:
        print(f"   Error getting monitoring data: {e}")

if __name__ == "__main__":
    stress_test()