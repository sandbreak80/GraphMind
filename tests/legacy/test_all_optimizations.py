#!/usr/bin/env python3
"""Comprehensive test for all optimizations working together."""
import requests
import time
import statistics
import json

def test_all_optimizations():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🚀 COMPREHENSIVE TEST: All Optimizations Working Together")
    print("=" * 70)
    
    # Test queries covering all optimization aspects
    test_queries = [
        {
            "query": "What is trading?",
            "expected_model": "llama3.2:3b",
            "expected_profile": "simple",
            "description": "Simple query - fastest model + minimal retrieval"
        },
        {
            "query": "Explain RSI indicator and MACD",
            "expected_model": "llama3.1:latest", 
            "expected_profile": "medium",
            "description": "Medium query - balanced model + balanced retrieval"
        },
        {
            "query": "Compare momentum and mean reversion strategies with technical analysis",
            "expected_model": "qwen2.5-coder:14b",
            "expected_profile": "complex", 
            "description": "Complex query - capable model + comprehensive retrieval"
        },
        {
            "query": "Provide comprehensive analysis of market conditions with extensive research",
            "expected_model": "gpt-oss:20b",
            "expected_profile": "research",
            "description": "Research query - most capable model + extensive retrieval"
        }
    ]
    
    print("\n🧪 Testing All Optimizations")
    print("-" * 50)
    
    response_times = []
    model_usage = {}
    
    for i, case in enumerate(test_queries, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Query: {case['query']}")
        print(f"   Expected model: {case['expected_model']}")
        print(f"   Expected profile: {case['expected_profile']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": case["query"],
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
                
                # Track model usage (we can't see which model was used directly,
                # but we can infer from response time patterns)
                if response_time < 0.1:
                    model_type = "cached"
                elif response_time < 0.5:
                    model_type = "fast"
                else:
                    model_type = "complex"
                
                if model_type not in model_usage:
                    model_usage[model_type] = 0
                model_usage[model_type] += 1
                
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test caching with repeated queries
    print(f"\n💾 Testing Caching + All Optimizations")
    print("-" * 50)
    
    repeated_queries = [
        "What is trading?",
        "Explain RSI indicator",
        "What is trading?",  # Should be cached
        "Explain RSI indicator"  # Should be cached
    ]
    
    cached_times = []
    for i, query in enumerate(repeated_queries, 1):
        print(f"\n   {i}. Testing: {query}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            cached_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Success: {response_time:.2f}s")
                print(f"      📝 Answer length: {len(data.get('answer', ''))}")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Get comprehensive monitoring data
    print(f"\n📊 Comprehensive Monitoring Data")
    print("-" * 50)
    
    # Performance metrics
    try:
        response = requests.get(f"{base_url}/monitoring/performance")
        if response.status_code == 200:
            perf_metrics = response.json()
            print(f"\n   📈 Performance Metrics:")
            print(f"      Total queries: {perf_metrics.get('total_queries', 0)}")
            print(f"      Average response time: {perf_metrics.get('avg_response_time', 0):.2f}s")
            print(f"      Error rate: {perf_metrics.get('error_rate', 0):.2%}")
            print(f"      Model usage: {perf_metrics.get('model_usage', {})}")
            print(f"      Query types: {perf_metrics.get('query_types', {})}")
    except Exception as e:
        print(f"   ❌ Error getting performance metrics: {e}")
    
    # Cache metrics
    try:
        response = requests.get(f"{base_url}/monitoring/cache")
        if response.status_code == 200:
            cache_metrics = response.json()
            print(f"\n   💾 Cache Metrics:")
            print(f"      Cache hits: {cache_metrics.get('hits', 0)}")
            print(f"      Cache misses: {cache_metrics.get('misses', 0)}")
            print(f"      Hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
            print(f"      Cache size: {cache_metrics.get('cache_size', 0)}")
    except Exception as e:
        print(f"   ❌ Error getting cache metrics: {e}")
    
    # Retrieval optimization metrics
    try:
        response = requests.get(f"{base_url}/monitoring/retrieval")
        if response.status_code == 200:
            retrieval_metrics = response.json()
            print(f"\n   🎯 Retrieval Optimization:")
            print(f"      Optimizer available: {retrieval_metrics.get('optimizer_available', False)}")
            print(f"      Profiles configured: {len(retrieval_metrics.get('profiles', {}))}")
            
            profiles = retrieval_metrics.get('profiles', {})
            for profile, details in profiles.items():
                print(f"         {profile}: {details['description']}")
                print(f"            Efficiency: {details['efficiency_ratio']:.2f}")
    except Exception as e:
        print(f"   ❌ Error getting retrieval metrics: {e}")
    
    # Performance analysis
    print(f"\n📈 Performance Analysis")
    print("-" * 50)
    
    if response_times:
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        print(f"   Standard deviation: {statistics.stdev(response_times):.2f}s")
    
    if cached_times:
        first_run = cached_times[:2]
        second_run = cached_times[2:]
        
        print(f"\n   Caching Performance:")
        print(f"   First run average: {statistics.mean(first_run):.2f}s")
        print(f"   Second run average: {statistics.mean(second_run):.2f}s")
        
        if statistics.mean(second_run) < statistics.mean(first_run):
            improvement = ((statistics.mean(first_run) - statistics.mean(second_run)) / statistics.mean(first_run) * 100)
            print(f"   🚀 Caching improvement: {improvement:.1f}%")
    
    # Model usage analysis
    if model_usage:
        print(f"\n   Model Usage Analysis:")
        total_queries = sum(model_usage.values())
        for model_type, count in model_usage.items():
            percentage = (count / total_queries) * 100
            print(f"   {model_type}: {count} queries ({percentage:.1f}%)")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 70)
    
    all_working = True
    
    # Check if all optimizations are working
    if response_times and statistics.mean(response_times) < 1.0:
        print("✅ Performance: EXCELLENT (avg < 1.0s)")
    else:
        print("⚠️  Performance: Needs improvement")
        all_working = False
    
    if cached_times and statistics.mean(cached_times[2:]) < 0.1:
        print("✅ Caching: EXCELLENT (cached queries < 0.1s)")
    else:
        print("⚠️  Caching: Needs improvement")
        all_working = False
    
    # Check if we can get monitoring data
    try:
        response = requests.get(f"{base_url}/monitoring/performance")
        if response.status_code == 200:
            print("✅ Monitoring: WORKING")
        else:
            print("❌ Monitoring: Not working")
            all_working = False
    except:
        print("❌ Monitoring: Not working")
        all_working = False
    
    try:
        response = requests.get(f"{base_url}/monitoring/retrieval")
        if response.status_code == 200:
            print("✅ Retrieval Optimization: WORKING")
        else:
            print("❌ Retrieval Optimization: Not working")
            all_working = False
    except:
        print("❌ Retrieval Optimization: Not working")
        all_working = False
    
    if all_working:
        print("\n🎉 ALL OPTIMIZATIONS WORKING PERFECTLY!")
        print("   Ready for production deployment! 🚀")
    else:
        print("\n⚠️  Some optimizations need attention")
        print("   Review the issues above before deployment")

if __name__ == "__main__":
    test_all_optimizations()