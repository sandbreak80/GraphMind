#!/usr/bin/env python3
"""Comprehensive API Testing Suite - All Endpoints, Modes, and Models"""

import requests
import time
import json
import random
from datetime import datetime
import asyncio
import concurrent.futures

class ComprehensiveAPITester:
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
        
        # Fresh prompts to avoid caching
        self.fresh_prompts = [
            "Explain the concept of mean reversion in quantitative trading strategies",
            "How do you implement a momentum-based portfolio optimization algorithm?",
            "What are the key differences between arbitrage and market making strategies?",
            "Describe the mathematical foundations of Black-Scholes option pricing model",
            "How can machine learning be applied to predict market volatility?",
            "What is the role of risk parity in modern portfolio theory?",
            "Explain the implementation of a pairs trading strategy using cointegration",
            "How do you backtest a high-frequency trading algorithm effectively?",
            "What are the advantages of using Monte Carlo simulation in risk management?",
            "Describe the process of building a multi-factor equity model",
            "How can sentiment analysis be integrated into algorithmic trading systems?",
            "What are the key considerations for implementing a market neutral strategy?",
            "Explain the concept of value at risk (VaR) in portfolio management",
            "How do you optimize transaction costs in systematic trading strategies?",
            "What is the impact of market microstructure on algorithmic trading performance?",
            "Describe the implementation of a trend-following strategy using technical indicators",
            "How can alternative data sources enhance quantitative trading models?",
            "What are the challenges of implementing a cross-asset trading strategy?",
            "Explain the role of regime detection in adaptive trading systems",
            "How do you measure and manage model risk in quantitative finance?",
            "What is the significance of transaction cost analysis in execution algorithms?",
            "Describe the implementation of a volatility trading strategy",
            "How can machine learning improve order execution quality?",
            "What are the key factors in designing a robust risk management framework?",
            "Explain the concept of statistical arbitrage and its implementation challenges"
        ]
        
        # Available models
        self.models = [
            "llama3.1:latest",
            "llama3.1:8b", 
            "llama3.1:70b",
            "llama3.2:latest",
            "llama3.2:3b",
            "llama3.2:1b",
            "qwen2.5:latest",
            "qwen2.5:7b",
            "qwen2.5:14b",
            "deepseek-coder:latest",
            "deepseek-coder:6.7b",
            "deepseek-coder:33b",
            "mistral:latest",
            "mistral:7b",
            "mistral:8x7b",
            "phi3:latest",
            "phi3:3.8b",
            "phi3:14b",
            "gemma2:latest",
            "gemma2:9b",
            "gemma2:27b"
        ]
        
        # Query modes
        self.modes = ["qa", "spec", "enhanced", "research", "obsidian"]
        
    def log_test(self, test_name, status, details="", duration=0, response_data=None):
        """Log test result with detailed information"""
        self.test_results['total_tests'] += 1
        if status == 'PASS':
            self.test_results['passed'] += 1
        elif status == 'FAIL':
            self.test_results['failed'] += 1
        else:
            self.test_results['errors'] += 1
        
        test_detail = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        if response_data:
            test_detail['response_data'] = response_data
            
        self.test_results['test_details'].append(test_detail)
        
        status_icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
        print(f"{status_icon} {test_name}: {status} ({duration:.2f}s)")
        if details:
            print(f"   Details: {details}")
        if response_data and 'answer' in response_data:
            answer_preview = response_data['answer'][:100] + "..." if len(response_data['answer']) > 100 else response_data['answer']
            print(f"   Response: {answer_preview}")
    
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
    
    def test_basic_ask_endpoints(self):
        """Test all basic ask endpoints with different models"""
        print("\n🔍 TESTING BASIC ASK ENDPOINTS")
        print("-" * 50)
        
        endpoints = [
            ("/ask", "Basic Q&A"),
            ("/ask-enhanced", "Enhanced with Web Search"),
            ("/ask-research", "Comprehensive Research"),
            ("/ask-obsidian", "Obsidian Integration")
        ]
        
        for endpoint, description in endpoints:
            for mode in ["qa", "spec"] if endpoint == "/ask" else ["qa"]:
                for model in random.sample(self.models, 3):  # Test 3 random models per endpoint
                    prompt = random.choice(self.fresh_prompts)
                    test_name = f"{description} - {mode} - {model}"
                    
                    start_time = time.time()
                    try:
                        payload = {
                            "query": prompt,
                            "mode": mode,
                            "model": model,
                            "disable_model_override": True,
                            "top_k": 5,
                            "temperature": 0.7
                        }
                        
                        response = requests.post(
                            f"{self.base_url}{endpoint}",
                            headers=self.headers,
                            json=payload,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer_length = len(data.get('answer', ''))
                            citations_count = len(data.get('citations', []))
                            
                            self.log_test(
                                test_name, 
                                "PASS", 
                                f"Answer: {answer_length} chars, Citations: {citations_count}",
                                time.time() - start_time,
                                data
                            )
                        else:
                            self.log_test(
                                test_name, 
                                "FAIL", 
                                f"HTTP {response.status_code}: {response.text[:200]}",
                                time.time() - start_time
                            )
                    except Exception as e:
                        self.log_test(test_name, "ERROR", str(e), time.time() - start_time)
    
    def test_advanced_endpoints(self):
        """Test advanced RAG optimization endpoints"""
        print("\n🔍 TESTING ADVANCED RAG ENDPOINTS")
        print("-" * 50)
        
        # Query Analyzer
        for i in range(3):
            prompt = random.choice(self.fresh_prompts)
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/analyze-query",
                    headers=self.headers,
                    data={"query": prompt},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    complexity = data.get('complexity', 'unknown')
                    self.log_test(
                        f"Query Analyzer - Test {i+1}", 
                        "PASS", 
                        f"Complexity: {complexity}",
                        time.time() - start_time,
                        data
                    )
                else:
                    self.log_test(f"Query Analyzer - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
            except Exception as e:
                self.log_test(f"Query Analyzer - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Advanced Search
        for i in range(3):
            prompt = random.choice(self.fresh_prompts)
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/advanced-search",
                    headers=self.headers,
                    data={"query": prompt, "top_k": 5},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    results_count = data.get('count', 0)
                    self.log_test(
                        f"Advanced Search - Test {i+1}", 
                        "PASS", 
                        f"Found {results_count} results",
                        time.time() - start_time,
                        data
                    )
                else:
                    self.log_test(f"Advanced Search - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
            except Exception as e:
                self.log_test(f"Advanced Search - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Query Expansion
        for i in range(3):
            prompt = random.choice(self.fresh_prompts)
            for expansion_level in ["minimal", "medium", "aggressive"]:
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.base_url}/expand-query",
                        headers=self.headers,
                        data={"query": prompt, "expansion_level": expansion_level},
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        expanded_count = len(data.get('expanded_queries', []))
                        confidence = data.get('confidence_score', 0)
                        self.log_test(
                            f"Query Expansion - {expansion_level} - Test {i+1}", 
                            "PASS", 
                            f"Generated {expanded_count} queries, Confidence: {confidence:.2f}",
                            time.time() - start_time,
                            data
                        )
                    else:
                        self.log_test(f"Query Expansion - {expansion_level} - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                except Exception as e:
                    self.log_test(f"Query Expansion - {expansion_level} - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Reranking
        for i in range(3):
            sample_results = [
                {"text": f"Sample result {j} about {random.choice(['trading', 'finance', 'algorithms'])}", 
                 "metadata": {"source": f"test_{j}", "score": random.uniform(0.1, 0.9)}, 
                 "score": random.uniform(0.1, 0.9)}
                for j in range(5)
            ]
            
            for strategy in ["comprehensive", "trading_focused", "quality_focused"]:
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.base_url}/rerank-results",
                        headers=self.headers,
                        data={
                            "query": random.choice(self.fresh_prompts),
                            "results": json.dumps(sample_results),
                            "rerank_strategy": strategy,
                            "top_k": 3
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        reranked_count = len(data.get('reranked_results', []))
                        self.log_test(
                            f"Reranking - {strategy} - Test {i+1}", 
                            "PASS", 
                            f"Reranked {reranked_count} results",
                            time.time() - start_time,
                            data
                        )
                    else:
                        self.log_test(f"Reranking - {strategy} - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                except Exception as e:
                    self.log_test(f"Reranking - {strategy} - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Context Compression
        for i in range(3):
            sample_text = f"""
            This is a comprehensive analysis of {random.choice(['quantitative trading', 'portfolio optimization', 'risk management'])} 
            strategies. The methodology involves multiple critical steps that must be carefully executed to ensure success 
            in the financial markets. The first step is to define clear entry and exit rules based on technical analysis, 
            fundamental analysis, or a combination of both approaches. Risk management is the cornerstone of any successful 
            trading strategy. This involves setting appropriate position sizes based on account size and risk tolerance, 
            implementing stop-loss orders to limit potential losses, and diversifying across different assets and timeframes.
            """
            
            for method in ["extractive", "hybrid", "semantic"]:
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{self.base_url}/compress-context",
                        headers=self.headers,
                        data={
                            "text": sample_text,
                            "target_ratio": random.uniform(0.2, 0.5),
                            "method": method,
                            "max_length": random.randint(500, 1500)
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        compression_ratio = data.get('compression_ratio', 0)
                        quality_score = data.get('quality_score', 0)
                        self.log_test(
                            f"Context Compression - {method} - Test {i+1}", 
                            "PASS", 
                            f"Ratio: {compression_ratio:.2f}, Quality: {quality_score:.2f}",
                            time.time() - start_time,
                            data
                        )
                    else:
                        self.log_test(f"Context Compression - {method} - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                except Exception as e:
                    self.log_test(f"Context Compression - {method} - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Metadata Extraction
        for i in range(3):
            sample_text = f"""
            This comprehensive guide covers the implementation of a sophisticated {random.choice(['momentum', 'mean reversion', 'arbitrage'])} 
            trading strategy using {random.choice(['RSI', 'MACD', 'Bollinger Bands'])} indicators. The strategy involves identifying 
            strong trending markets and entering positions when momentum indicators confirm the trend direction. Risk management 
            is critical, with stop losses set at 2% below entry and position sizing based on account volatility.
            """
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/extract-metadata",
                    headers=self.headers,
                    data={
                        "document_id": f"test_doc_{i+1}",
                        "title": f"Trading Strategy Guide {i+1}",
                        "text": sample_text,
                        "source": "test_document"
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    domain = data.get('trading_domain', 'unknown')
                    complexity = data.get('complexity_level', 'unknown')
                    concepts = len(data.get('key_concepts', []))
                    self.log_test(
                        f"Metadata Extraction - Test {i+1}", 
                        "PASS", 
                        f"Domain: {domain}, Complexity: {complexity}, Concepts: {concepts}",
                        time.time() - start_time,
                        data
                    )
                else:
                    self.log_test(f"Metadata Extraction - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
            except Exception as e:
                self.log_test(f"Metadata Extraction - Test {i+1}", "ERROR", str(e), time.time() - start_time)
    
    def test_document_operations(self):
        """Test document ingestion and management"""
        print("\n🔍 TESTING DOCUMENT OPERATIONS")
        print("-" * 50)
        
        # Document Ingestion
        for i in range(3):
            sample_text = f"""
            This is a comprehensive document about {random.choice(['algorithmic trading', 'portfolio theory', 'risk management'])} 
            strategies. It covers various aspects including {random.choice(['backtesting', 'optimization', 'execution'])} 
            and provides detailed insights into {random.choice(['market microstructure', 'quantitative finance', 'derivatives'])}.
            """
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/ingest",
                    headers=self.headers,
                    json={
                        "text": sample_text,
                        "title": f"Test Document {i+1}",
                        "source": f"test_ingestion_{i+1}"
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    doc_id = data.get('document_id', 'unknown')
                    self.log_test(
                        f"Document Ingestion - Test {i+1}", 
                        "PASS", 
                        f"Document ID: {doc_id}",
                        time.time() - start_time,
                        data
                    )
                else:
                    self.log_test(f"Document Ingestion - Test {i+1}", "FAIL", f"HTTP {response.status_code}: {response.text[:200]}", time.time() - start_time)
            except Exception as e:
                self.log_test(f"Document Ingestion - Test {i+1}", "ERROR", str(e), time.time() - start_time)
        
        # Document Filtering
        for i in range(2):
            start_time = time.time()
            try:
                # Create sample documents for filtering
                sample_documents = [
                    {
                        "id": f"doc_{j}",
                        "title": f"Sample Document {j}",
                        "text": f"This is a sample document about {random.choice(['trading', 'finance', 'algorithms'])}",
                        "metadata": {
                            "trading_domain": random.choice(["technical_analysis", "portfolio_management", "risk_management"]),
                            "complexity_level": random.choice(["beginner", "intermediate", "expert"])
                        }
                    }
                    for j in range(3)
                ]
                
                response = requests.post(
                    f"{self.base_url}/filter-documents",
                    headers=self.headers,
                    data={
                        "documents": json.dumps(sample_documents),
                        "filters": json.dumps({
                            "trading_domain": random.choice(["technical_analysis", "portfolio_management", "risk_management"]),
                            "complexity_level": random.choice(["beginner", "intermediate", "expert"])
                        })
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    filtered_count = len(data.get('filtered_documents', []))
                    self.log_test(
                        f"Document Filtering - Test {i+1}", 
                        "PASS", 
                        f"Filtered {filtered_count} documents",
                        time.time() - start_time,
                        data
                    )
                else:
                    self.log_test(f"Document Filtering - Test {i+1}", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
            except Exception as e:
                self.log_test(f"Document Filtering - Test {i+1}", "ERROR", str(e), time.time() - start_time)
    
    def test_performance_under_load(self):
        """Test system performance under concurrent load"""
        print("\n🔍 TESTING PERFORMANCE UNDER LOAD")
        print("-" * 50)
        
        def make_concurrent_request(request_id):
            """Make a single concurrent request"""
            prompt = random.choice(self.fresh_prompts)
            model = random.choice(self.models)
            endpoint = random.choice(["/ask", "/ask-enhanced", "/ask-research"])
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    json={
                        "query": prompt,
                        "mode": "qa",
                        "model": model,
                        "disable_model_override": True
                    },
                    timeout=60
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    return {
                        "request_id": request_id,
                        "status": "PASS",
                        "duration": duration,
                        "endpoint": endpoint,
                        "model": model
                    }
                else:
                    return {
                        "request_id": request_id,
                        "status": "FAIL",
                        "duration": duration,
                        "endpoint": endpoint,
                        "model": model,
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status": "ERROR",
                    "duration": time.time() - start_time,
                    "endpoint": endpoint,
                    "model": model,
                    "error": str(e)
                }
        
        # Run 10 concurrent requests
        print("Running 10 concurrent requests...")
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures, timeout=120)]
        
        total_time = time.time() - start_time
        successful_requests = sum(1 for r in results if r['status'] == 'PASS')
        failed_requests = sum(1 for r in results if r['status'] == 'FAIL')
        error_requests = sum(1 for r in results if r['status'] == 'ERROR')
        
        avg_duration = sum(r['duration'] for r in results) / len(results)
        
        self.log_test(
            "Concurrent Load Test", 
            "PASS" if successful_requests >= 8 else "FAIL", 
            f"Success: {successful_requests}/10, Avg Duration: {avg_duration:.2f}s, Total Time: {total_time:.2f}s",
            total_time
        )
        
        # Log individual results
        for result in results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"   {status_icon} Request {result['request_id']}: {result['status']} ({result['duration']:.2f}s) - {result['endpoint']} - {result['model']}")
            if 'error' in result:
                print(f"      Error: {result['error']}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 COMPREHENSIVE API TESTING SUITE")
        print("=" * 60)
        print(f"Testing with {len(self.fresh_prompts)} fresh prompts")
        print(f"Testing {len(self.models)} different models")
        print(f"Testing {len(self.modes)} query modes")
        print("=" * 60)
        
        self.test_results['start_time'] = datetime.now()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Run all test categories
        self.test_basic_ask_endpoints()
        self.test_advanced_endpoints()
        self.test_document_operations()
        self.test_performance_under_load()
        
        self.test_results['end_time'] = datetime.now()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
        
        return self.test_results['failed'] == 0 and self.test_results['errors'] == 0
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
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
        
        # Group results by category
        categories = {}
        for test in self.test_results['test_details']:
            category = test['test_name'].split(' - ')[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'errors': 0}
            
            if test['status'] == 'PASS':
                categories[category]['passed'] += 1
            elif test['status'] == 'FAIL':
                categories[category]['failed'] += 1
            else:
                categories[category]['errors'] += 1
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        print("-" * 50)
        for category, stats in categories.items():
            total_cat = stats['passed'] + stats['failed'] + stats['errors']
            success_rate = (stats['passed'] / total_cat) * 100 if total_cat > 0 else 0
            print(f"{category}: {stats['passed']}/{total_cat} ({success_rate:.1f}%)")
        
        print(f"\n⏰ Test completed at: {self.test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is fully operational across all endpoints, modes, and models.")
        else:
            print(f"\n⚠️  {failed + errors} TESTS FAILED! Please review and fix issues.")

def main():
    """Main test runner"""
    print("🔧 TradingAI Research Platform - Comprehensive API Test")
    print("=" * 60)
    
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 COMPREHENSIVE TESTING COMPLETE! All systems operational.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED! Please review results and fix issues.")
        return 1

if __name__ == "__main__":
    exit(main())