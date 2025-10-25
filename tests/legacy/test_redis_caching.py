#!/usr/bin/env python3
"""Test Redis caching system performance"""

import requests
import time
import json
from datetime import datetime

def test_redis_caching():
    base_url = "http://localhost:8002"
    
    # Authenticate
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🚀 TESTING REDIS CACHING SYSTEM")
    print("=" * 60)
    
    # Test queries - same queries to test cache hits
    test_queries = [
        "What is a moving average in trading?",
        "Explain momentum trading strategies",
        "How do I implement a mean reversion strategy?",
        "What are the key factors affecting ES futures pricing?",
        "What is a moving average in trading?",  # Repeat for cache hit
        "Explain momentum trading strategies",   # Repeat for cache hit
    ]
    
    print(f"📝 Testing {len(test_queries)} queries (including repeats for cache testing)...")
    print("-" * 60)
    
    # First run - no cache hits expected
    print("\n🔥 FIRST RUN (No cache hits expected)")
    print("-" * 40)
    
    first_run_times = []
    for i, query in enumerate(test_queries[:4], 1):
        print(f"\n🧪 Query {i}/4: {query[:40]}...")
        
        request_data = {
            "query": query,
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": "llama3.1:latest",
            "disable_model_override": True
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            first_run_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                print(f"   ✅ Success: {response_time:.2f}s, {answer_length} chars")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Second run - cache hits expected for repeated queries
    print(f"\n⚡ SECOND RUN (Cache hits expected for repeated queries)")
    print("-" * 40)
    
    second_run_times = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Query {i}/{len(test_queries)}: {query[:40]}...")
        
        request_data = {
            "query": query,
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": "llama3.1:latest",
            "disable_model_override": True
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            second_run_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                cached = data.get('cached', False)
                cache_status = "💾 CACHED" if cached else "🔄 FRESH"
                print(f"   ✅ Success: {response_time:.2f}s, {answer_length} chars {cache_status}")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Check cache statistics
    print(f"\n📊 CACHE STATISTICS")
    print("-" * 40)
    
    try:
        cache_response = requests.get(f"{base_url}/monitoring/cache", headers=headers)
        if cache_response.status_code == 200:
            cache_stats = cache_response.json()
            print(f"Cache hits: {cache_stats.get('hits', 0)}")
            print(f"Cache misses: {cache_stats.get('misses', 0)}")
            print(f"Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
            print(f"Cached queries: {cache_stats.get('cached_queries', 0)}")
            print(f"Redis connected: {cache_stats.get('redis_connected', False)}")
        else:
            print(f"❌ Failed to get cache stats: {cache_response.status_code}")
    except Exception as e:
        print(f"❌ Error getting cache stats: {e}")
    
    # Performance analysis
    print(f"\n📈 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    first_avg = sum(first_run_times) / len(first_run_times) if first_run_times else 0
    second_avg = sum(second_run_times) / len(second_run_times) if second_run_times else 0
    
    print(f"First run average: {first_avg:.2f}s")
    print(f"Second run average: {second_avg:.2f}s")
    
    if first_avg > 0 and second_avg > 0:
        improvement = ((first_avg - second_avg) / first_avg) * 100
        print(f"Performance improvement: {improvement:.1f}%")
        
        if improvement > 50:
            print("✅ EXCELLENT: Redis caching is working very well!")
        elif improvement > 20:
            print("✅ GOOD: Redis caching is providing significant improvement!")
        elif improvement > 0:
            print("⚠️  MODERATE: Some caching benefit detected")
        else:
            print("❌ ISSUE: No caching benefit detected - check Redis connection")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_redis_caching()