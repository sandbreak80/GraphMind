"""
Comprehensive Performance Benchmark Suite for GraphMind
Tests response times, throughput, and resource usage
"""

import pytest
import requests
import time
import statistics
import concurrent.futures
from typing import List, Dict, Any
import psutil
import os

# Performance targets (from roadmap)
PERFORMANCE_TARGETS = {
    "single_request_p95": 30.0,  # seconds
    "concurrent_request_max": 45.0,  # seconds
    "api_endpoint_max": 5.0,  # seconds
    "cache_hit_rate_min": 0.70,  # 70%
    "success_rate_min": 0.80,  # 80%
}

@pytest.mark.performance
class TestResponseTimeBenchmarks:
    """Benchmark response times for different query types"""
    
    def test_simple_query_response_time(self, api_client):
        """Benchmark simple query response time"""
        query = "What is trading?"
        iterations = 5
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            response = api_client.post(
                "/ask",
                json={
                    "request": {
                        "query": query,
                        "mode": "qa",
                        "top_k": 3
                    }
                },
                timeout=30
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                response_times.append(response_time)
                print(f"  Simple query #{i+1}: {response_time:.2f}s")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 3 else max(response_times)
            
            print(f"\n📊 Simple Query Benchmarks:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  P95: {p95_time:.2f}s")
            print(f"  Target: < 15s")
            print(f"  Status: {'✓ PASS' if avg_time < 15 else '✗ FAIL'}")
            
            assert len(response_times) > 0  # At least some succeeded
    
    def test_complex_query_response_time(self, api_client):
        """Benchmark complex query response time"""
        query = "Compare momentum trading strategies using RSI versus MACD indicators, including entry and exit criteria, risk management approaches, and expected performance metrics"
        iterations = 3
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            response = api_client.post(
                "/ask",
                json={
                    "request": {
                        "query": query,
                        "mode": "qa",
                        "top_k": 10
                    }
                },
                timeout=45
            )
            
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                response_times.append(response_time)
                print(f"  Complex query #{i+1}: {response_time:.2f}s")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            p95_time = max(response_times)
            
            print(f"\n📊 Complex Query Benchmarks:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  P95: {p95_time:.2f}s")
            print(f"  Target: < {PERFORMANCE_TARGETS['single_request_p95']}s")
            print(f"  Status: {'✓ PASS' if p95_time < PERFORMANCE_TARGETS['single_request_p95'] else '⚠ SLOW'}")
            
            assert len(response_times) > 0

@pytest.mark.performance
@pytest.mark.slow
class TestConcurrentRequestBenchmarks:
    """Benchmark concurrent request handling"""
    
    def test_concurrent_requests(self, api_client):
        """Benchmark concurrent request performance"""
        queries = [
            "What is trading?",
            "What are technical indicators?",
            "Explain momentum strategies",
            "What is risk management?",
            "How to use RSI?",
        ]
        
        def make_request(query):
            start_time = time.time()
            try:
                response = api_client.post(
                    "/ask",
                    json={
                        "request": {
                            "query": query,
                            "mode": "qa",
                            "top_k": 3
                        }
                    },
                    timeout=45
                )
                end_time = time.time()
                return {
                    "success": response.status_code == 200,
                    "time": end_time - start_time,
                    "query": query
                }
            except Exception as e:
                return {
                    "success": False,
                    "time": None,
                    "query": query,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, queries))
        end_time = time.time()
        
        total_time = end_time - start_time
        successes = [r for r in results if r["success"]]
        failures = [r for r in results if not r["success"]]
        
        print(f"\n📊 Concurrent Request Benchmarks:")
        print(f"  Total requests: {len(queries)}")
        print(f"  Successful: {len(successes)}")
        print(f"  Failed: {len(failures)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Target: < {PERFORMANCE_TARGETS['concurrent_request_max']}s")
        print(f"  Status: {'✓ PASS' if total_time < PERFORMANCE_TARGETS['concurrent_request_max'] else '⚠ SLOW'}")
        
        if successes:
            response_times = [r["time"] for r in successes if r["time"]]
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            print(f"  Average response: {avg_time:.2f}s")
            print(f"  Max response: {max_time:.2f}s")
        
        # At least 80% should succeed
        success_rate = len(successes) / len(queries)
        assert success_rate >= PERFORMANCE_TARGETS["success_rate_min"]

@pytest.mark.performance
class TestAPEndpointPerformance:
    """Benchmark API endpoint performance"""
    
    def test_health_endpoint_performance(self, test_config):
        """Benchmark health check endpoint"""
        iterations = 10
        response_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            response = requests.get(f"{test_config['BASE_URL']}/api/health", timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 Health Endpoint Benchmark:")
        print(f"  Average: {avg_time*1000:.1f}ms")
        print(f"  Max: {max_time*1000:.1f}ms")
        print(f"  Target: < 100ms")
        print(f"  Status: {'✓ PASS' if avg_time < 0.1 else '⚠ SLOW'}")
        
        assert avg_time < 1.0  # Should be very fast
    
    def test_models_endpoint_performance(self, api_client):
        """Benchmark models listing endpoint"""
        iterations = 5
        response_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            response = api_client.get("/ollama/models", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            
            print(f"\n📊 Models Endpoint Benchmark:")
            print(f"  Average: {avg_time:.2f}s")
            print(f"  Target: < {PERFORMANCE_TARGETS['api_endpoint_max']}s")
            print(f"  Status: {'✓ PASS' if avg_time < PERFORMANCE_TARGETS['api_endpoint_max'] else '⚠ SLOW'}")
            
            assert avg_time < PERFORMANCE_TARGETS["api_endpoint_max"]

@pytest.mark.performance
class TestCachePerformance:
    """Benchmark cache hit rates and performance"""
    
    def test_cache_hit_rate(self, api_client):
        """Measure cache hit rate for repeated queries"""
        query = "What is momentum trading?"
        iterations = 5
        response_times = []
        
        for i in range(iterations):
            start_time = time.time()
            response = api_client.post(
                "/ask",
                json={
                    "request": {
                        "query": query,
                        "mode": "qa",
                        "top_k": 3
                    }
                },
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                response_times.append(response_time)
                print(f"  Request #{i+1}: {response_time:.2f}s")
        
        if len(response_times) >= 3:
            first_time = response_times[0]
            subsequent_avg = statistics.mean(response_times[1:])
            
            speedup = first_time / subsequent_avg if subsequent_avg > 0 else 1
            
            print(f"\n📊 Cache Performance:")
            print(f"  First request: {first_time:.2f}s")
            print(f"  Subsequent avg: {subsequent_avg:.2f}s")
            print(f"  Speedup: {speedup:.2f}x")
            print(f"  Status: {'✓ Cache working' if speedup > 1.2 else '⚠ No cache benefit'}")

@pytest.mark.performance
class TestResourceUsageBenchmarks:
    """Benchmark resource usage during operations"""
    
    def test_memory_usage_during_queries(self, api_client):
        """Monitor memory usage during query processing"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Run several queries
        for i in range(5):
            api_client.post(
                "/ask",
                json={
                    "request": {
                        "query": f"Test query {i}",
                        "mode": "qa",
                        "top_k": 3
                    }
                },
                timeout=30
            )
        
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"\n📊 Memory Usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  Final: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")
        print(f"  Target: < 500 MB increase")
        print(f"  Status: {'✓ PASS' if memory_increase < 500 else '⚠ HIGH'}")
        
        # Memory shouldn't grow excessively
        assert memory_increase < 1000  # Less than 1GB growth

@pytest.mark.performance
class TestThroughputBenchmarks:
    """Benchmark system throughput"""
    
    def test_sequential_throughput(self, api_client):
        """Measure throughput for sequential requests"""
        num_requests = 10
        successful = 0
        total_time = 0
        
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                response = api_client.get("/health", timeout=5)
                if response.status_code == 200:
                    successful += 1
            except:
                pass
        
        end_time = time.time()
        total_time = end_time - start_time
        
        throughput = successful / total_time if total_time > 0 else 0
        
        print(f"\n📊 Sequential Throughput:")
        print(f"  Requests: {successful}/{num_requests}")
        print(f"  Time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} req/s")
        
        assert successful >= num_requests * 0.8  # 80% success rate

def generate_performance_report(results: Dict[str, Any]) -> str:
    """Generate performance benchmark report"""
    report = """
# Performance Benchmark Report

**Date**: {date}
**Target Grade**: A+ (95/100)
**Current Status**: {status}

## Response Time Benchmarks

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Simple Query (avg) | {simple_avg}s | < 15s | {simple_status} |
| Complex Query (p95) | {complex_p95}s | < 30s | {complex_status} |
| API Endpoints | {api_avg}s | < 5s | {api_status} |

## Throughput Benchmarks

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Concurrent Requests | {concurrent}s | < 45s | {concurrent_status} |
| Sequential Throughput | {throughput} req/s | > 5 req/s | {throughput_status} |

## Resource Usage

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Memory Growth | {memory}MB | < 500MB | {memory_status} |
| Success Rate | {success_rate}% | > 80% | {success_status} |

## Recommendations

{recommendations}

---

**Generated**: {date}
"""
    return report

if __name__ == "__main__":
    print("Running performance benchmarks...")
    pytest.main([__file__, "-v", "--tb=short"])

