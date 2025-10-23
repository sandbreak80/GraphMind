#!/usr/bin/env python3
"""
Performance Test Suite for EminiPlayer
Tests response times, load handling, and performance metrics
"""

import requests
import json
import time
import statistics
import concurrent.futures
from dataclasses import dataclass
from typing import List, Dict, Any
import argparse
import sys

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    threshold: float
    passed: bool

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.auth_token = None
        self.metrics = []
        
    def authenticate(self) -> bool:
        """Authenticate with the system."""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data="username=admin&password=admin123",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                return True
            return False
        except:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def measure_response_time(self, endpoint: str, payload: Dict[str, Any], timeout: int = 30) -> float:
        """Measure response time for an endpoint."""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers(),
                json=payload,
                timeout=timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                return end_time - start_time
            else:
                return -1  # Error
        except:
            return -1  # Error
    
    def test_single_request_performance(self) -> List[PerformanceMetric]:
        """Test performance of single requests."""
        metrics = []
        
        # Test different modes
        test_cases = [
            ("/api/ask", {"request": {"query": "What is trading?", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}),
            ("/api/ask-enhanced", {"request": {"query": "What is the current market trend?", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}),
            ("/api/ask-obsidian", {"request": {"query": "What are my trading strategies?", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}),
            ("/api/ask-research", {"request": {"query": "What are the latest trading strategies?", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}),
        ]
        
        for endpoint, payload in test_cases:
            response_time = self.measure_response_time(endpoint, payload)
            if response_time > 0:
                mode_name = endpoint.split("/")[-1].replace("ask-", "").replace("-", " ").title()
                threshold = 30.0  # 30 seconds threshold
                passed = response_time < threshold
                
                metrics.append(PerformanceMetric(
                    name=f"{mode_name} Response Time",
                    value=response_time,
                    unit="seconds",
                    threshold=threshold,
                    passed=passed
                ))
        
        return metrics
    
    def test_concurrent_requests(self, num_requests: int = 5) -> List[PerformanceMetric]:
        """Test performance under concurrent load."""
        metrics = []
        
        def make_request():
            return self.measure_response_time(
                "/api/ask",
                {"request": {"query": "What is trading?", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}
            )
        
        # Run concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=60)]
        end_time = time.time()
        
        # Filter out errors
        valid_results = [r for r in results if r > 0]
        
        if valid_results:
            avg_response_time = statistics.mean(valid_results)
            max_response_time = max(valid_results)
            min_response_time = min(valid_results)
            total_time = end_time - start_time
            
            metrics.extend([
                PerformanceMetric(
                    name="Concurrent Requests Average Response Time",
                    value=avg_response_time,
                    unit="seconds",
                    threshold=30.0,
                    passed=avg_response_time < 30.0
                ),
                PerformanceMetric(
                    name="Concurrent Requests Max Response Time",
                    value=max_response_time,
                    unit="seconds",
                    threshold=45.0,
                    passed=max_response_time < 45.0
                ),
                PerformanceMetric(
                    name="Concurrent Requests Min Response Time",
                    value=min_response_time,
                    unit="seconds",
                    threshold=5.0,
                    passed=min_response_time < 5.0
                ),
                PerformanceMetric(
                    name="Concurrent Requests Total Time",
                    value=total_time,
                    unit="seconds",
                    threshold=60.0,
                    passed=total_time < 60.0
                ),
                PerformanceMetric(
                    name="Concurrent Requests Success Rate",
                    value=len(valid_results) / num_requests * 100,
                    unit="percent",
                    threshold=80.0,
                    passed=len(valid_results) / num_requests >= 0.8
                )
            ])
        
        return metrics
    
    def test_memory_usage(self) -> List[PerformanceMetric]:
        """Test memory usage patterns."""
        metrics = []
        
        # Make multiple requests to test memory stability
        response_times = []
        for i in range(10):
            response_time = self.measure_response_time(
                "/api/ask",
                {"request": {"query": f"Test query {i}", "mode": "qa", "top_k": 3, "model": "llama3.2:3b"}}
            )
            if response_time > 0:
                response_times.append(response_time)
        
        if response_times:
            # Check for memory leaks (response times should not increase significantly)
            first_half = response_times[:5]
            second_half = response_times[5:]
            
            if first_half and second_half:
                avg_first = statistics.mean(first_half)
                avg_second = statistics.mean(second_half)
                performance_degradation = ((avg_second - avg_first) / avg_first) * 100
                
                metrics.append(PerformanceMetric(
                    name="Memory Stability (Response Time Degradation)",
                    value=performance_degradation,
                    unit="percent",
                    threshold=50.0,  # Should not degrade more than 50%
                    passed=performance_degradation < 50.0
                ))
        
        return metrics
    
    def test_api_endpoint_performance(self) -> List[PerformanceMetric]:
        """Test performance of various API endpoints."""
        metrics = []
        
        # Test different endpoints
        endpoints = [
            ("/api/health", "GET", None),
            ("/api/ollama/models", "GET", None),
            ("/api/auth/me", "GET", None),
            ("/api/system-prompts", "GET", None),
        ]
        
        for endpoint, method, payload in endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", headers=self.get_headers(), timeout=10)
                else:
                    response = requests.post(f"{self.base_url}{endpoint}", headers=self.get_headers(), json=payload, timeout=10)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    endpoint_name = endpoint.split("/")[-1].replace("-", " ").title()
                    threshold = 5.0  # 5 seconds for API endpoints
                    passed = response_time < threshold
                    
                    metrics.append(PerformanceMetric(
                        name=f"{endpoint_name} Response Time",
                        value=response_time,
                        unit="seconds",
                        threshold=threshold,
                        passed=passed
                    ))
            except:
                pass
        
        return metrics
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        print("Starting performance test suite...")
        
        # Authenticate
        if not self.authenticate():
            print("Authentication failed. Exiting.")
            return {"error": "Authentication failed"}
        
        all_metrics = []
        
        # Run different performance tests
        print("Testing single request performance...")
        all_metrics.extend(self.test_single_request_performance())
        
        print("Testing concurrent requests...")
        all_metrics.extend(self.test_concurrent_requests())
        
        print("Testing memory usage...")
        all_metrics.extend(self.test_memory_usage())
        
        print("Testing API endpoint performance...")
        all_metrics.extend(self.test_api_endpoint_performance())
        
        # Calculate summary
        total_tests = len(all_metrics)
        passed_tests = sum(1 for m in all_metrics if m.passed)
        failed_tests = total_tests - passed_tests
        
        # Group metrics by category
        categories = {}
        for metric in all_metrics:
            category = metric.name.split(" ")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(metric)
        
        results = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "metrics": all_metrics,
            "categories": categories
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("Performance Test Summary:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print("=" * 60)
        
        # Print detailed results
        for category, metrics in categories.items():
            print(f"\n{category}:")
            for metric in metrics:
                status = "✓" if metric.passed else "✗"
                print(f"  {status} {metric.name}: {metric.value:.2f} {metric.unit} (threshold: {metric.threshold} {metric.unit})")
        
        return results

def main():
    parser = argparse.ArgumentParser(description="EminiPlayer Performance Test Suite")
    parser.add_argument("--url", default="http://localhost:3001", help="Base URL for the API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument("--concurrent", type=int, default=5, help="Number of concurrent requests")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(args.url)
    results = tester.run_performance_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Performance test results saved to {args.output}")
    
    # Exit with error code if any tests failed
    if results.get("failed", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()