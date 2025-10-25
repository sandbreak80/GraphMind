#!/usr/bin/env python3
"""Comprehensive Full Functionality Test Suite"""

import requests
import time
import json
from datetime import datetime
import asyncio
import concurrent.futures

class FullFunctionalityTester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.headers = None
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
            'test_details': []
        }
    
    def log_test(self, test_name, status, details="", duration=0):
        """Log test result"""
        self.test_results['total_tests'] += 1
        if status == 'PASS':
            self.test_results['passed'] += 1
        elif status == 'FAIL':
            self.test_results['failed'] += 1
        else:
            self.test_results['errors'] += 1
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
        status_icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({duration:.2f}s)")
        if details:
            print(f"   Details: {details}")
    
    def authenticate(self):
        """Test authentication"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "admin123"},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                self.log_test("Authentication", "PASS", "Successfully authenticated", time.time() - start_time)
                return True
            else:
                self.log_test("Authentication", "FAIL", f"HTTP {response.status_code}: {response.text}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Authentication", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_health_check(self):
        """Test health check endpoint"""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", "PASS", f"Service: {data.get('service', 'unknown')}", time.time() - start_time)
                return True
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Health Check", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_basic_ask_endpoint(self):
        """Test basic ask endpoint"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                json={
                    "query": "What is a moving average?",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("Basic Ask Endpoint", "PASS", f"Response length: {len(data.get('answer', ''))}", time.time() - start_time)
                return True
            else:
                self.log_test("Basic Ask Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Basic Ask Endpoint", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_query_analyzer(self):
        """Test query analyzer endpoint"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/analyze-query",
                headers=self.headers,
                data={"query": "How to implement a momentum trading strategy with risk management?"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                complexity = data.get('complexity', 'unknown')
                self.log_test("Query Analyzer", "PASS", f"Complexity: {complexity}", time.time() - start_time)
                return True
            else:
                self.log_test("Query Analyzer", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Query Analyzer", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_advanced_search(self):
        """Test advanced search endpoint"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/advanced-search",
                headers=self.headers,
                data={"query": "moving average strategy", "top_k": 5},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                results_count = data.get('count', 0)
                self.log_test("Advanced Search", "PASS", f"Found {results_count} results", time.time() - start_time)
                return True
            else:
                self.log_test("Advanced Search", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Advanced Search", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_query_expansion(self):
        """Test query expansion endpoint"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/expand-query",
                headers=self.headers,
                data={"query": "RSI trading strategy", "expansion_level": "medium"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                expanded_count = len(data.get('expanded_queries', []))
                self.log_test("Query Expansion", "PASS", f"Generated {expanded_count} expanded queries", time.time() - start_time)
                return True
            else:
                self.log_test("Query Expansion", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Query Expansion", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_reranking(self):
        """Test reranking endpoint"""
        start_time = time.time()
        try:
            # Sample results to rerank
            sample_results = [
                {"text": "Moving averages are technical indicators", "metadata": {"source": "test"}, "score": 0.8},
                {"text": "Risk management is important in trading", "metadata": {"source": "test"}, "score": 0.7},
                {"text": "Market analysis helps with decisions", "metadata": {"source": "test"}, "score": 0.6}
            ]
            
            response = requests.post(
                f"{self.base_url}/rerank-results",
                headers=self.headers,
                data={
                    "query": "trading strategy",
                    "results": json.dumps(sample_results),
                    "rerank_strategy": "comprehensive",
                    "top_k": 3
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                reranked_count = len(data.get('reranked_results', []))
                self.log_test("Reranking", "PASS", f"Reranked {reranked_count} results", time.time() - start_time)
                return True
            else:
                self.log_test("Reranking", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Reranking", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_context_compression(self):
        """Test context compression endpoint"""
        start_time = time.time()
        try:
            sample_text = """
            A comprehensive trading strategy implementation involves multiple critical steps that must be carefully executed to ensure success in the financial markets. The first step is to define clear entry and exit rules based on technical analysis, fundamental analysis, or a combination of both approaches. Risk management is the cornerstone of any successful trading strategy. This involves setting appropriate position sizes based on account size and risk tolerance, implementing stop-loss orders to limit potential losses, and diversifying across different assets and timeframes.
            """
            
            response = requests.post(
                f"{self.base_url}/compress-context",
                headers=self.headers,
                data={
                    "text": sample_text,
                    "target_ratio": 0.3,
                    "method": "hybrid",
                    "max_length": 1000
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                compression_ratio = data.get('compression_ratio', 0)
                self.log_test("Context Compression", "PASS", f"Compression ratio: {compression_ratio:.2f}", time.time() - start_time)
                return True
            else:
                self.log_test("Context Compression", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Context Compression", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_metadata_extraction(self):
        """Test metadata extraction endpoint"""
        start_time = time.time()
        try:
            sample_text = """
            This comprehensive guide covers the implementation of a sophisticated momentum trading strategy using RSI and MACD indicators. The strategy involves identifying strong trending markets and entering positions when momentum indicators confirm the trend direction. Risk management is critical, with stop losses set at 2% below entry and position sizing based on account volatility.
            """
            
            response = requests.post(
                f"{self.base_url}/extract-metadata",
                headers=self.headers,
                data={
                    "document_id": "test_doc_1",
                    "title": "Momentum Trading Strategy Guide",
                    "text": sample_text,
                    "source": "test_document"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                domain = data.get('trading_domain', 'unknown')
                complexity = data.get('complexity_level', 'unknown')
                self.log_test("Metadata Extraction", "PASS", f"Domain: {domain}, Complexity: {complexity}", time.time() - start_time)
                return True
            else:
                self.log_test("Metadata Extraction", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Metadata Extraction", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_document_ingestion(self):
        """Test document ingestion"""
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ingest",
                headers=self.headers,
                json={
                    "text": "This is a test document about trading strategies and risk management. It covers various aspects of algorithmic trading and portfolio optimization.",
                    "title": "Test Trading Document",
                    "source": "test_ingestion"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                doc_id = data.get('document_id', 'unknown')
                self.log_test("Document Ingestion", "PASS", f"Document ID: {doc_id}", time.time() - start_time)
                return True
            else:
                self.log_test("Document Ingestion", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Document Ingestion", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        start_time = time.time()
        try:
            # Test multiple concurrent requests
            queries = [
                "What is technical analysis?",
                "How to manage trading risk?",
                "Explain portfolio optimization",
                "What are moving averages?",
                "Describe momentum trading"
            ]
            
            def make_request(query):
                return requests.post(
                    f"{self.base_url}/ask",
                    headers=self.headers,
                    json={
                        "query": query,
                        "mode": "qa",
                        "model": "llama3.1:latest",
                        "disable_model_override": True
                    },
                    timeout=30
                )
            
            # Run concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, query) for query in queries]
                results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=60)]
            
            successful_requests = sum(1 for r in results if r.status_code == 200)
            total_time = time.time() - start_time
            
            if successful_requests >= 4:  # Allow 1 failure
                self.log_test("Performance Benchmarks", "PASS", f"{successful_requests}/5 requests successful in {total_time:.2f}s", time.time() - start_time)
                return True
            else:
                self.log_test("Performance Benchmarks", "FAIL", f"Only {successful_requests}/5 requests successful", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("Performance Benchmarks", "ERROR", str(e), time.time() - start_time)
            return False
    
    def run_all_tests(self):
        """Run all functionality tests"""
        print("🚀 STARTING COMPREHENSIVE FUNCTIONALITY TEST")
        print("=" * 60)
        
        self.test_results['start_time'] = datetime.now()
        
        # Core system tests
        if not self.authenticate():
            print("❌ Authentication failed - stopping tests")
            return False
        
        if not self.test_health_check():
            print("❌ Health check failed - stopping tests")
            return False
        
        # API endpoint tests
        self.test_basic_ask_endpoint()
        self.test_query_analyzer()
        self.test_advanced_search()
        self.test_query_expansion()
        self.test_reranking()
        self.test_context_compression()
        self.test_metadata_extraction()
        self.test_document_ingestion()
        
        # Performance tests
        self.test_performance_benchmarks()
        
        self.test_results['end_time'] = datetime.now()
        
        # Print summary
        self.print_summary()
        
        return self.test_results['failed'] == 0 and self.test_results['errors'] == 0
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        errors = self.test_results['errors']
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if self.test_results['start_time'] and self.test_results['end_time']:
            duration = (self.test_results['end_time'] - self.test_results['start_time']).total_seconds()
            print(f"Total Duration: {duration:.2f}s")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        for test in self.test_results['test_details']:
            status_icon = "✅" if test['status'] == 'PASS' else "❌" if test['status'] == 'FAIL' else "⚠️"
            print(f"{status_icon} {test['test_name']} ({test['status']}) - {test['duration']:.2f}s")
            if test['details']:
                print(f"   {test['details']}")
        
        print(f"\n⏰ Test completed at: {self.test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main test runner"""
    print("🔧 TradingAI Research Platform - Full Functionality Test")
    print("=" * 60)
    
    tester = FullFunctionalityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    exit(main())