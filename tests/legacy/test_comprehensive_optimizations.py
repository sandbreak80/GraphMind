#!/usr/bin/env python3
"""Comprehensive test suite for all optimizations."""
import requests
import time
import statistics
import json
from typing import List, Dict, Any

class OptimizationTester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
        self.test_results = {
            'model_selection': [],
            'caching': [],
            'monitoring': [],
            'performance': []
        }
    
    def authenticate(self) -> bool:
        """Get authentication token."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful!")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_model_selection(self):
        """Test smart model selection with different query complexities."""
        print("\n🧠 Testing Smart Model Selection")
        print("=" * 50)
        
        test_cases = [
            {
                "query": "What is trading?",
                "expected_complexity": "simple",
                "description": "Simple question"
            },
            {
                "query": "Explain the RSI indicator and how it works in technical analysis",
                "expected_complexity": "medium", 
                "description": "Medium complexity question"
            },
            {
                "query": "Analyze the current market conditions, compare different trading strategies including momentum, mean reversion, and breakout strategies, and provide a comprehensive recommendation with risk management",
                "expected_complexity": "complex",
                "description": "Complex analysis question"
            },
            {
                "query": "Provide a comprehensive, detailed, and thorough analysis of the current market conditions with extensive research into multiple trading strategies",
                "expected_complexity": "research",
                "description": "Research-level question"
            }
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{i}. {case['description']}")
            print(f"   Query: {case['query'][:60]}...")
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers=self.headers,
                    json={
                        "query": case["query"],
                        "temperature": 0.1,
                        "max_tokens": 1000
                    },
                    timeout=60
                )
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success: {response_time:.2f}s")
                    print(f"   📝 Answer length: {len(data.get('answer', ''))}")
                    
                    # Store result for analysis
                    self.test_results['model_selection'].append({
                        'query': case['query'],
                        'expected': case['expected_complexity'],
                        'response_time': response_time,
                        'answer_length': len(data.get('answer', ''))
                    })
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    def test_caching_performance(self):
        """Test query caching with repeated queries."""
        print("\n💾 Testing Query Caching")
        print("=" * 50)
        
        # Test queries with different complexities
        test_queries = [
            "What is momentum trading?",
            "Explain RSI indicator",
            "Compare different trading strategies",
            "What is momentum trading?",  # Repeat for cache test
            "Explain RSI indicator",     # Repeat for cache test
        ]
        
        response_times = []
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: {query}")
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers=self.headers,
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
                    
                    # Store result
                    self.test_results['caching'].append({
                        'query': query,
                        'response_time': response_time,
                        'is_repeat': i > 3
                    })
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Analyze caching performance
        if len(response_times) >= 5:
            first_run = response_times[:3]
            second_run = response_times[3:]
            
            print(f"\n📊 Caching Analysis:")
            print(f"   First run average: {statistics.mean(first_run):.2f}s")
            print(f"   Second run average: {statistics.mean(second_run):.2f}s")
            print(f"   Improvement: {((statistics.mean(first_run) - statistics.mean(second_run)) / statistics.mean(first_run) * 100):.1f}%")
    
    def test_monitoring_system(self):
        """Test monitoring endpoints and data collection."""
        print("\n📊 Testing Monitoring System")
        print("=" * 50)
        
        # Test performance metrics
        print("\n1. Performance Metrics:")
        try:
            response = requests.get(f"{self.base_url}/monitoring/performance")
            if response.status_code == 200:
                metrics = response.json()
                print(f"   ✅ Total queries: {metrics.get('total_queries', 0)}")
                print(f"   ✅ Avg response time: {metrics.get('avg_response_time', 0):.2f}s")
                print(f"   ✅ Error rate: {metrics.get('error_rate', 0):.2%}")
                print(f"   ✅ Model usage: {metrics.get('model_usage', {})}")
                
                self.test_results['monitoring'].append({
                    'endpoint': 'performance',
                    'status': 'success',
                    'data': metrics
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test cache metrics
        print("\n2. Cache Metrics:")
        try:
            response = requests.get(f"{self.base_url}/monitoring/cache")
            if response.status_code == 200:
                cache_metrics = response.json()
                print(f"   ✅ Cache hits: {cache_metrics.get('hits', 0)}")
                print(f"   ✅ Cache misses: {cache_metrics.get('misses', 0)}")
                print(f"   ✅ Hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
                print(f"   ✅ Cache size: {cache_metrics.get('cache_size', 0)}")
                
                self.test_results['monitoring'].append({
                    'endpoint': 'cache',
                    'status': 'success',
                    'data': cache_metrics
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test recent queries
        print("\n3. Recent Queries:")
        try:
            response = requests.get(f"{self.base_url}/monitoring/recent")
            if response.status_code == 200:
                recent_data = response.json()
                print(f"   ✅ Recent times: {recent_data.get('recent_times', [])}")
                
                self.test_results['monitoring'].append({
                    'endpoint': 'recent',
                    'status': 'success',
                    'data': recent_data
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def test_performance_under_load(self):
        """Test performance under concurrent load."""
        print("\n⚡ Testing Performance Under Load")
        print("=" * 50)
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(query, thread_id):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers=self.headers,
                    json={
                        "query": query,
                        "temperature": 0.1,
                        "max_tokens": 500
                    },
                    timeout=30
                )
                end_time = time.time()
                response_time = end_time - start_time
                
                results.put({
                    'thread_id': thread_id,
                    'success': response.status_code == 200,
                    'response_time': response_time,
                    'status_code': response.status_code
                })
            except Exception as e:
                results.put({
                    'thread_id': thread_id,
                    'success': False,
                    'response_time': 0,
                    'error': str(e)
                })
        
        # Create concurrent requests
        threads = []
        queries = [
            "What is trading?",
            "Explain RSI",
            "What is momentum?",
            "Explain MACD",
            "What is VWAP?"
        ]
        
        print(f"   🚀 Starting {len(queries)} concurrent requests...")
        start_time = time.time()
        
        for i, query in enumerate(queries):
            thread = threading.Thread(target=make_request, args=(query, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Collect results
        thread_results = []
        while not results.empty():
            thread_results.append(results.get())
        
        # Analyze results
        successful = [r for r in thread_results if r['success']]
        failed = [r for r in thread_results if not r['success']]
        
        if successful:
            response_times = [r['response_time'] for r in successful]
            print(f"   ✅ Successful requests: {len(successful)}/{len(queries)}")
            print(f"   ✅ Average response time: {statistics.mean(response_times):.2f}s")
            print(f"   ✅ Min response time: {min(response_times):.2f}s")
            print(f"   ✅ Max response time: {max(response_times):.2f}s")
            print(f"   ✅ Total time: {total_time:.2f}s")
            print(f"   ✅ Requests per second: {len(successful)/total_time:.2f}")
        else:
            print(f"   ❌ All requests failed")
        
        if failed:
            print(f"   ❌ Failed requests: {len(failed)}")
            for fail in failed:
                print(f"      Thread {fail['thread_id']}: {fail.get('error', 'Unknown error')}")
        
        self.test_results['performance'].append({
            'test_type': 'concurrent_load',
            'total_requests': len(queries),
            'successful': len(successful),
            'failed': len(failed),
            'total_time': total_time,
            'avg_response_time': statistics.mean(response_times) if successful else 0
        })
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n🔍 Testing Edge Cases")
        print("=" * 50)
        
        edge_cases = [
            {
                "query": "",
                "description": "Empty query"
            },
            {
                "query": "a" * 1000,
                "description": "Very long query"
            },
            {
                "query": "What is trading? " * 100,
                "description": "Repetitive query"
            },
            {
                "query": "🚀💰📈🎯",
                "description": "Emoji-only query"
            }
        ]
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n{i}. {case['description']}")
            print(f"   Query: {case['query'][:50]}...")
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/ask",
                    headers=self.headers,
                    json={
                        "query": case["query"],
                        "temperature": 0.1,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success: {response_time:.2f}s")
                    print(f"   📝 Answer length: {len(data.get('answer', ''))}")
                else:
                    print(f"   ⚠️  Expected behavior: {response.status_code}")
                    print(f"   📝 Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ⚠️  Expected behavior: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Model Selection Analysis
        if self.test_results['model_selection']:
            print("\n🧠 Model Selection Analysis:")
            for result in self.test_results['model_selection']:
                print(f"   Query: {result['query'][:50]}...")
                print(f"   Expected: {result['expected']}")
                print(f"   Response time: {result['response_time']:.2f}s")
                print(f"   Answer length: {result['answer_length']}")
                print()
        
        # Caching Analysis
        if self.test_results['caching']:
            print("\n💾 Caching Analysis:")
            first_run = [r for r in self.test_results['caching'] if not r['is_repeat']]
            second_run = [r for r in self.test_results['caching'] if r['is_repeat']]
            
            if first_run and second_run:
                first_avg = statistics.mean([r['response_time'] for r in first_run])
                second_avg = statistics.mean([r['response_time'] for r in second_run])
                improvement = ((first_avg - second_avg) / first_avg * 100) if first_avg > 0 else 0
                
                print(f"   First run average: {first_avg:.2f}s")
                print(f"   Second run average: {second_avg:.2f}s")
                print(f"   Performance improvement: {improvement:.1f}%")
        
        # Performance Analysis
        if self.test_results['performance']:
            print("\n⚡ Performance Analysis:")
            for result in self.test_results['performance']:
                print(f"   Test type: {result['test_type']}")
                print(f"   Successful requests: {result['successful']}/{result['total_requests']}")
                print(f"   Average response time: {result['avg_response_time']:.2f}s")
                print(f"   Total time: {result['total_time']:.2f}s")
                print()
        
        # Monitoring Analysis
        if self.test_results['monitoring']:
            print("\n📊 Monitoring Analysis:")
            for result in self.test_results['monitoring']:
                print(f"   Endpoint: {result['endpoint']}")
                print(f"   Status: {result['status']}")
                if result['status'] == 'success':
                    print(f"   Data: {result['data']}")
                print()
    
    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive Optimization Tests")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Run all test suites
        self.test_model_selection()
        self.test_caching_performance()
        self.test_monitoring_system()
        self.test_performance_under_load()
        self.test_edge_cases()
        
        # Generate final report
        self.generate_report()
        
        print("\n✅ All tests completed!")
        return True

if __name__ == "__main__":
    tester = OptimizationTester()
    tester.run_all_tests()