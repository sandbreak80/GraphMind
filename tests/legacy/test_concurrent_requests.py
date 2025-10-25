#!/usr/bin/env python3
"""
Test concurrent requests to verify parallel processing works correctly
"""

import time
import requests
import json
import threading
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_concurrent_requests():
    """Test concurrent requests to verify parallel processing"""
    
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
    
    print("\n🧪 Testing Concurrent Requests with Parallel Processing...")
    print("=" * 70)
    
    # Test queries
    test_queries = [
        "What is trading?",
        "What are the best trading strategies?",
        "How do I use technical analysis?",
        "What is risk management?",
        "How do I backtest strategies?",
        "What are futures contracts?",
        "How do I read candlestick patterns?",
        "What is leverage in trading?",
        "How do I manage my trading psychology?",
        "What are the trading hours for futures?"
    ]
    
    def make_request(query: str, request_id: int) -> Dict[str, Any]:
        """Make a single request and return results"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/api/ask",
                headers=headers,
                json={
                    "query": query,
                    "mode": "qa",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "request_id": request_id,
                    "query": query,
                    "status": "success",
                    "response_time": response_time,
                    "answer_length": len(data.get('answer', '')),
                    "source_count": len(data.get('citations', [])),
                    "error": None
                }
            else:
                return {
                    "request_id": request_id,
                    "query": query,
                    "status": "error",
                    "response_time": response_time,
                    "answer_length": 0,
                    "source_count": 0,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return {
                "request_id": request_id,
                "query": query,
                "status": "error",
                "response_time": response_time,
                "answer_length": 0,
                "source_count": 0,
                "error": str(e)
            }
    
    # Test different concurrency levels
    concurrency_tests = [
        {"name": "Sequential (1 thread)", "threads": 1},
        {"name": "Low Concurrency (2 threads)", "threads": 2},
        {"name": "Medium Concurrency (5 threads)", "threads": 5},
        {"name": "High Concurrency (10 threads)", "threads": 10}
    ]
    
    all_results = []
    
    for test_config in concurrency_tests:
        print(f"\n📊 Testing {test_config['name']}:")
        print("-" * 50)
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=test_config['threads']) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(make_request, query, i): i 
                for i, query in enumerate(test_queries)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_request):
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    print(f"   ✅ Request {result['request_id']+1}: {result['response_time']:.2f}s, {result['answer_length']} chars")
                else:
                    print(f"   ❌ Request {result['request_id']+1}: {result['error']}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Sort results by request_id to maintain order
        results.sort(key=lambda x: x["request_id"])
        
        # Analyze results
        successful_results = [r for r in results if r["status"] == "success"]
        failed_results = [r for r in results if r["status"] == "error"]
        
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            answer_lengths = [r["answer_length"] for r in successful_results]
            source_counts = [r["source_count"] for r in successful_results]
            
            print(f"\n   📊 Results Summary:")
            print(f"      ✅ Successful: {len(successful_results)}/{len(results)}")
            print(f"      ❌ Failed: {len(failed_results)}/{len(results)}")
            print(f"      ⏱️  Total Time: {total_time:.2f}s")
            print(f"      📈 Average Response Time: {statistics.mean(response_times):.2f}s")
            print(f"      🚀 Fastest Response: {min(response_times):.2f}s")
            print(f"      🐌 Slowest Response: {max(response_times):.2f}s")
            print(f"      📝 Average Answer Length: {statistics.mean(answer_lengths):.0f} chars")
            print(f"      📚 Average Sources: {statistics.mean(source_counts):.1f}")
            
            # Calculate throughput
            throughput = len(successful_results) / total_time
            print(f"      🚀 Throughput: {throughput:.2f} requests/second")
            
            # Calculate efficiency (how much faster than sequential)
            if test_config['threads'] > 1:
                sequential_time = sum(response_times)
                parallel_efficiency = (sequential_time / total_time) / test_config['threads'] * 100
                print(f"      📊 Parallel Efficiency: {parallel_efficiency:.1f}%")
        
        if failed_results:
            print(f"\n   ❌ Failed Requests:")
            for result in failed_results:
                print(f"      - Request {result['request_id']+1}: {result['error']}")
        
        all_results.append({
            "config": test_config,
            "results": results,
            "total_time": total_time,
            "successful_count": len(successful_results),
            "failed_count": len(failed_results)
        })
    
    # Overall analysis
    print("\n" + "=" * 70)
    print("📊 CONCURRENT PROCESSING ANALYSIS")
    print("=" * 70)
    
    print(f"📊 Concurrency Performance Comparison:")
    for result in all_results:
        config = result["config"]
        successful = result["successful_count"]
        total = successful + result["failed_count"]
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"   {config['name']}:")
        print(f"      Success Rate: {success_rate:.1f}%")
        print(f"      Total Time: {result['total_time']:.2f}s")
        
        if successful > 0:
            # Calculate throughput
            throughput = successful / result['total_time']
            print(f"      Throughput: {throughput:.2f} requests/second")
    
    # Parallel processing effectiveness
    if len(all_results) >= 2:
        sequential_result = all_results[0]  # First result is sequential
        parallel_results = all_results[1:]  # Rest are parallel
        
        print(f"\n📊 Parallel Processing Effectiveness:")
        for result in parallel_results:
            config = result["config"]
            if result["successful_count"] > 0 and sequential_result["successful_count"] > 0:
                speedup = sequential_result["total_time"] / result["total_time"]
                efficiency = speedup / config["threads"] * 100
                
                print(f"   {config['name']}:")
                print(f"      Speedup: {speedup:.2f}x")
                print(f"      Efficiency: {efficiency:.1f}%")
                
                if efficiency > 80:
                    print(f"      ✅ EXCELLENT: Very efficient parallel processing")
                elif efficiency > 60:
                    print(f"      ✅ GOOD: Efficient parallel processing")
                elif efficiency > 40:
                    print(f"      ⚠️  MODERATE: Some parallel processing benefits")
                else:
                    print(f"      ⚠️  POOR: Limited parallel processing benefits")
    
    # Stability analysis
    print(f"\n📊 System Stability Analysis:")
    for result in all_results:
        config = result["config"]
        success_rate = (result["successful_count"] / (result["successful_count"] + result["failed_count"]) * 100) if (result["successful_count"] + result["failed_count"]) > 0 else 0
        
        if success_rate >= 95:
            print(f"   {config['name']}: ✅ EXCELLENT stability ({success_rate:.1f}%)")
        elif success_rate >= 90:
            print(f"   {config['name']}: ✅ GOOD stability ({success_rate:.1f}%)")
        elif success_rate >= 80:
            print(f"   {config['name']}: ⚠️  MODERATE stability ({success_rate:.1f}%)")
        else:
            print(f"   {config['name']}: ❌ POOR stability ({success_rate:.1f}%)")
    
    return all_results

if __name__ == "__main__":
    test_concurrent_requests()