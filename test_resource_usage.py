#!/usr/bin/env python3
"""
Test memory usage and resource utilization with parallel processing
"""

import time
import requests
import json
import psutil
import os
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

def get_system_resources():
    """Get current system resource usage"""
    process = psutil.Process(os.getpid())
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        "process_memory_mb": process.memory_info().rss / (1024**2),
        "process_cpu_percent": process.cpu_percent(),
        "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
    }

def test_resource_usage():
    """Test memory usage and resource utilization"""
    
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
    
    print("\n🧪 Testing Resource Usage with Parallel Processing...")
    print("=" * 70)
    
    # Baseline measurement
    print("📊 Measuring Baseline Resources...")
    baseline_resources = get_system_resources()
    print(f"   CPU Usage: {baseline_resources['cpu_percent']:.1f}%")
    print(f"   Memory Usage: {baseline_resources['memory_percent']:.1f}%")
    print(f"   Available Memory: {baseline_resources['memory_available_gb']:.1f} GB")
    print(f"   Process Memory: {baseline_resources['process_memory_mb']:.1f} MB")
    
    # Test queries of different complexities
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
    
    def make_request_with_monitoring(query_info: Dict[str, Any], request_id: int) -> Dict[str, Any]:
        """Make a request while monitoring resources"""
        start_time = time.time()
        start_resources = get_system_resources()
        
        try:
            response = requests.post(
                f"{base_url}/api/ask",
                headers=headers,
                json={
                    "query": query_info["query"],
                    "mode": "qa",
                    "temperature": 0.1,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            end_time = time.time()
            end_resources = get_system_resources()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "request_id": request_id,
                    "query_name": query_info["name"],
                    "complexity": query_info["expected_complexity"],
                    "status": "success",
                    "response_time": response_time,
                    "answer_length": len(data.get('answer', '')),
                    "source_count": len(data.get('citations', [])),
                    "start_resources": start_resources,
                    "end_resources": end_resources,
                    "peak_cpu": max(start_resources['cpu_percent'], end_resources['cpu_percent']),
                    "peak_memory": max(start_resources['memory_percent'], end_resources['memory_percent']),
                    "memory_delta": end_resources['memory_percent'] - start_resources['memory_percent'],
                    "error": None
                }
            else:
                return {
                    "request_id": request_id,
                    "query_name": query_info["name"],
                    "complexity": query_info["expected_complexity"],
                    "status": "error",
                    "response_time": response_time,
                    "answer_length": 0,
                    "source_count": 0,
                    "start_resources": start_resources,
                    "end_resources": end_resources,
                    "peak_cpu": max(start_resources['cpu_percent'], end_resources['cpu_percent']),
                    "peak_memory": max(start_resources['memory_percent'], end_resources['memory_percent']),
                    "memory_delta": end_resources['memory_percent'] - start_resources['memory_percent'],
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            end_time = time.time()
            end_resources = get_system_resources()
            response_time = end_time - start_time
            
            return {
                "request_id": request_id,
                "query_name": query_info["name"],
                "complexity": query_info["expected_complexity"],
                "status": "error",
                "response_time": response_time,
                "answer_length": 0,
                "source_count": 0,
                "start_resources": start_resources,
                "end_resources": end_resources,
                "peak_cpu": max(start_resources['cpu_percent'], end_resources['cpu_percent']),
                "peak_memory": max(start_resources['memory_percent'], end_resources['memory_percent']),
                "memory_delta": end_resources['memory_percent'] - start_resources['memory_percent'],
                "error": str(e)
            }
    
    # Test different concurrency levels
    concurrency_tests = [
        {"name": "Sequential", "threads": 1, "iterations": 3},
        {"name": "Low Concurrency", "threads": 2, "iterations": 3},
        {"name": "Medium Concurrency", "threads": 3, "iterations": 3}
    ]
    
    all_results = []
    
    for test_config in concurrency_tests:
        print(f"\n📊 Testing {test_config['name']} ({test_config['threads']} threads):")
        print("-" * 50)
        
        # Prepare test queries (repeat for multiple iterations)
        test_queries_repeated = []
        for i in range(test_config['iterations']):
            for query_info in test_queries:
                test_queries_repeated.append({
                    **query_info,
                    "iteration": i + 1
                })
        
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=test_config['threads']) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(make_request_with_monitoring, query_info, i): i 
                for i, query_info in enumerate(test_queries_repeated)
            }
            
            # Collect results as they complete
            for future in future_to_request:
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    print(f"   ✅ {result['query_name']} (Iter {result.get('iteration', 1)}): {result['response_time']:.2f}s, CPU: {result['peak_cpu']:.1f}%, Mem: {result['peak_memory']:.1f}%")
                else:
                    print(f"   ❌ {result['query_name']} (Iter {result.get('iteration', 1)}): {result['error']}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_results = [r for r in results if r["status"] == "success"]
        failed_results = [r for r in results if r["status"] == "error"]
        
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            peak_cpus = [r["peak_cpu"] for r in successful_results]
            peak_memories = [r["peak_memory"] for r in successful_results]
            memory_deltas = [r["memory_delta"] for r in successful_results]
            
            print(f"\n   📊 Resource Usage Summary:")
            print(f"      ✅ Successful: {len(successful_results)}/{len(results)}")
            print(f"      ❌ Failed: {len(failed_results)}/{len(results)}")
            print(f"      ⏱️  Total Time: {total_time:.2f}s")
            print(f"      📈 Average Response Time: {sum(response_times)/len(response_times):.2f}s")
            print(f"      🔥 Peak CPU Usage: {max(peak_cpus):.1f}%")
            print(f"      💾 Peak Memory Usage: {max(peak_memories):.1f}%")
            print(f"      📊 Average CPU Usage: {sum(peak_cpus)/len(peak_cpus):.1f}%")
            print(f"      📊 Average Memory Usage: {sum(peak_memories)/len(peak_memories):.1f}%")
            print(f"      📈 Memory Delta: {sum(memory_deltas)/len(memory_deltas):.2f}%")
            
            # Resource efficiency
            cpu_efficiency = (sum(peak_cpus) / len(peak_cpus)) / test_config['threads'] * 100
            print(f"      🎯 CPU Efficiency: {cpu_efficiency:.1f}% per thread")
        
        if failed_results:
            print(f"\n   ❌ Failed Requests:")
            for result in failed_results:
                print(f"      - {result['query_name']}: {result['error']}")
        
        all_results.append({
            "config": test_config,
            "results": results,
            "total_time": total_time,
            "successful_count": len(successful_results),
            "failed_count": len(failed_results)
        })
    
    # Final resource measurement
    print(f"\n📊 Final Resource Measurement...")
    final_resources = get_system_resources()
    print(f"   CPU Usage: {final_resources['cpu_percent']:.1f}%")
    print(f"   Memory Usage: {final_resources['memory_percent']:.1f}%")
    print(f"   Available Memory: {final_resources['memory_available_gb']:.1f} GB")
    print(f"   Process Memory: {final_resources['process_memory_mb']:.1f} MB")
    
    # Overall analysis
    print("\n" + "=" * 70)
    print("📊 RESOURCE USAGE ANALYSIS")
    print("=" * 70)
    
    print(f"📊 Resource Usage Comparison:")
    print(f"   Baseline CPU: {baseline_resources['cpu_percent']:.1f}%")
    print(f"   Final CPU: {final_resources['cpu_percent']:.1f}%")
    print(f"   CPU Change: {final_resources['cpu_percent'] - baseline_resources['cpu_percent']:+.1f}%")
    print(f"   Baseline Memory: {baseline_resources['memory_percent']:.1f}%")
    print(f"   Final Memory: {final_resources['memory_percent']:.1f}%")
    print(f"   Memory Change: {final_resources['memory_percent'] - baseline_resources['memory_percent']:+.1f}%")
    
    # Performance by concurrency level
    print(f"\n📊 Performance by Concurrency Level:")
    for result in all_results:
        config = result["config"]
        successful = result["successful_count"]
        total = successful + result["failed_count"]
        success_rate = (successful / total * 100) if total > 0 else 0
        
        if successful > 0:
            successful_results = [r for r in result["results"] if r["status"] == "success"]
            avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
            avg_cpu = sum(r["peak_cpu"] for r in successful_results) / len(successful_results)
            avg_memory = sum(r["peak_memory"] for r in successful_results) / len(successful_results)
            
            print(f"   {config['name']} ({config['threads']} threads):")
            print(f"      Success Rate: {success_rate:.1f}%")
            print(f"      Avg Response Time: {avg_response_time:.2f}s")
            print(f"      Avg CPU Usage: {avg_cpu:.1f}%")
            print(f"      Avg Memory Usage: {avg_memory:.1f}%")
            print(f"      Total Time: {result['total_time']:.2f}s")
    
    # Resource efficiency analysis
    print(f"\n📊 Resource Efficiency Analysis:")
    for result in all_results:
        config = result["config"]
        successful_results = [r for r in result["results"] if r["status"] == "success"]
        
        if successful_results and config['threads'] > 1:
            avg_cpu = sum(r["peak_cpu"] for r in successful_results) / len(successful_results)
            cpu_efficiency = avg_cpu / config['threads'] * 100
            
            print(f"   {config['name']}:")
            print(f"      CPU Efficiency: {cpu_efficiency:.1f}% per thread")
            
            if cpu_efficiency > 80:
                print(f"      ✅ EXCELLENT: Very efficient CPU utilization")
            elif cpu_efficiency > 60:
                print(f"      ✅ GOOD: Good CPU utilization")
            elif cpu_efficiency > 40:
                print(f"      ⚠️  MODERATE: Moderate CPU utilization")
            else:
                print(f"      ⚠️  POOR: Low CPU utilization")
    
    # Memory stability analysis
    print(f"\n📊 Memory Stability Analysis:")
    memory_changes = []
    for result in all_results:
        successful_results = [r for r in result["results"] if r["status"] == "success"]
        for r in successful_results:
            memory_changes.append(r["memory_delta"])
    
    if memory_changes:
        avg_memory_change = sum(memory_changes) / len(memory_changes)
        max_memory_change = max(memory_changes)
        min_memory_change = min(memory_changes)
        
        print(f"   Average Memory Change per Request: {avg_memory_change:+.2f}%")
        print(f"   Max Memory Change: {max_memory_change:+.2f}%")
        print(f"   Min Memory Change: {min_memory_change:+.2f}%")
        
        if abs(avg_memory_change) < 1:
            print(f"   ✅ EXCELLENT: Very stable memory usage")
        elif abs(avg_memory_change) < 2:
            print(f"   ✅ GOOD: Stable memory usage")
        elif abs(avg_memory_change) < 5:
            print(f"   ⚠️  MODERATE: Some memory variation")
        else:
            print(f"   ⚠️  POOR: High memory variation")
    
    return all_results

if __name__ == "__main__":
    test_resource_usage()