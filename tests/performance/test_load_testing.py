"""
Load testing suite for GraphMind
Tests system behavior under load
"""

import pytest
import requests
import time
import concurrent.futures
from typing import List, Dict
import statistics

@pytest.mark.performance
@pytest.mark.slow
class TestLoadScenarios:
    """Test system under various load scenarios"""
    
    def test_sustained_load(self, api_client):
        """Test sustained load over time"""
        duration = 60  # 60 seconds
        request_interval = 5  # Request every 5 seconds
        
        num_requests = duration // request_interval
        successful = 0
        failed = 0
        response_times = []
        
        print(f"\n🔄 Running sustained load test ({duration}s, {num_requests} requests)")
        
        start_time = time.time()
        
        for i in range(num_requests):
            req_start = time.time()
            
            try:
                response = api_client.post(
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
                
                req_end = time.time()
                req_time = req_end - req_start
                
                if response.status_code == 200:
                    successful += 1
                    response_times.append(req_time)
                else:
                    failed += 1
                
                print(f"  Request {i+1}/{num_requests}: {req_time:.2f}s - {'✓' if response.status_code == 200 else '✗'}")
                
            except Exception as e:
                failed += 1
                print(f"  Request {i+1}/{num_requests}: ✗ Error: {e}")
            
            # Wait for next interval
            elapsed = time.time() - start_time
            next_request_time = (i + 1) * request_interval
            sleep_time = max(0, next_request_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n📊 Sustained Load Results:")
        print(f"  Duration: {total_time:.2f}s")
        print(f"  Successful: {successful}/{num_requests}")
        print(f"  Failed: {failed}/{num_requests}")
        print(f"  Success Rate: {successful/num_requests*100:.1f}%")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"  Avg Response: {avg_time:.2f}s")
            print(f"  Median Response: {median_time:.2f}s")
            print(f"  Min Response: {min_time:.2f}s")
            print(f"  Max Response: {max_time:.2f}s")
        
        # Should maintain at least 80% success rate
        success_rate = successful / num_requests
        assert success_rate >= 0.80
    
    def test_burst_load(self, api_client):
        """Test burst of simultaneous requests"""
        num_concurrent = 10
        
        def make_request(index):
            start_time = time.time()
            try:
                response = api_client.get("/health", timeout=10)
                end_time = time.time()
                return {
                    "success": response.status_code == 200,
                    "time": end_time - start_time,
                    "index": index
                }
            except Exception as e:
                return {
                    "success": False,
                    "time": None,
                    "index": index,
                    "error": str(e)
                }
        
        print(f"\n🔄 Running burst load test ({num_concurrent} concurrent requests)")
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            results = list(executor.map(make_request, range(num_concurrent)))
        end_time = time.time()
        
        total_time = end_time - start_time
        successes = [r for r in results if r["success"]]
        
        print(f"\n📊 Burst Load Results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Successful: {len(successes)}/{num_concurrent}")
        print(f"  Success Rate: {len(successes)/num_concurrent*100:.1f}%")
        
        success_rate = len(successes) / num_concurrent
        assert success_rate >= 0.80

@pytest.mark.performance
class TestEndpointLatencyDistribution:
    """Test latency distribution for various endpoints"""
    
    def test_api_latency_percentiles(self, api_client):
        """Measure latency percentiles for API endpoints"""
        iterations = 20
        
        endpoints = {
            "health": {"method": "get", "path": "/health", "timeout": 5},
            "models": {"method": "get", "path": "/ollama/models", "timeout": 10},
            "prompts": {"method": "get", "path": "/user-prompts/rag_only", "timeout": 10},
        }
        
        results = {}
        
        for endpoint_name, config in endpoints.items():
            response_times = []
            
            for _ in range(iterations):
                start_time = time.time()
                
                try:
                    if config["method"] == "get":
                        response = api_client.get(config["path"], timeout=config["timeout"])
                    else:
                        response = api_client.post(config["path"], json={}, timeout=config["timeout"])
                    
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_times.append((end_time - start_time) * 1000)  # Convert to ms
                except:
                    pass
            
            if response_times:
                results[endpoint_name] = {
                    "p50": statistics.median(response_times),
                    "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 3 else max(response_times),
                    "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 10 else max(response_times),
                    "avg": statistics.mean(response_times),
                    "min": min(response_times),
                    "max": max(response_times),
                }
        
        print(f"\n📊 API Latency Percentiles:")
        for endpoint, metrics in results.items():
            print(f"\n  {endpoint.upper()}:")
            print(f"    P50: {metrics['p50']:.1f}ms")
            print(f"    P95: {metrics['p95']:.1f}ms")
            print(f"    P99: {metrics['p99']:.1f}ms")
            print(f"    Avg: {metrics['avg']:.1f}ms")
            print(f"    Range: {metrics['min']:.1f}ms - {metrics['max']:.1f}ms")
        
        # Health endpoint should be fast
        if "health" in results:
            assert results["health"]["p95"] < 500  # < 500ms

if __name__ == "__main__":
    print("Running load tests...")
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])

