#!/usr/bin/env python3
"""Comprehensive QA Test - All APIs and Functionality"""

import requests
import time
import json
import random
from datetime import datetime

class ComprehensiveQA:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.headers = None
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'categories': {}
        }
    
    def log_test(self, category, test_name, status, details="", duration=0):
        """Log test result"""
        self.results['total_tests'] += 1
        if status == 'PASS':
            self.results['passed'] += 1
        elif status == 'FAIL':
            self.results['failed'] += 1
        else:
            self.results['errors'] += 1
        
        if category not in self.results['categories']:
            self.results['categories'][category] = {'passed': 0, 'failed': 0, 'errors': 0}
        
        if status == 'PASS':
            self.results['categories'][category]['passed'] += 1
        elif status == 'FAIL':
            self.results['categories'][category]['failed'] += 1
        else:
            self.results['categories'][category]['errors'] += 1
        
        status_icon = "✅" if status == 'PASS' else "❌" if status == 'FAIL' else "⚠️"
        print(f"{status_icon} [{category}] {test_name}: {status} ({duration:.2f}s)")
        if details:
            print(f"   {details}")
    
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
                self.log_test("AUTH", "Authentication", "PASS", "Successfully authenticated", time.time() - start_time)
                return True
            else:
                self.log_test("AUTH", "Authentication", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
                return False
        except Exception as e:
            self.log_test("AUTH", "Authentication", "ERROR", str(e), time.time() - start_time)
            return False
    
    def test_core_endpoints(self):
        """Test core RAG endpoints"""
        print("\n🔍 TESTING CORE RAG ENDPOINTS")
        print("-" * 50)
        
        # Test basic ask endpoint
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                json={
                    "query": "What is a moving average in trading?",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("CORE", "Basic Ask", "PASS", f"Answer: {len(data.get('answer', ''))} chars", time.time() - start_time)
            else:
                self.log_test("CORE", "Basic Ask", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("CORE", "Basic Ask", "ERROR", str(e), time.time() - start_time)
        
        # Test enhanced ask endpoint
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask-enhanced",
                headers=self.headers,
                json={
                    "query": "How to implement a momentum trading strategy?",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                citations = len(data.get('citations', []))
                self.log_test("CORE", "Enhanced Ask", "PASS", f"Answer: {len(data.get('answer', ''))} chars, Citations: {citations}", time.time() - start_time)
            else:
                self.log_test("CORE", "Enhanced Ask", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("CORE", "Enhanced Ask", "ERROR", str(e), time.time() - start_time)
        
        # Test research ask endpoint
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask-research",
                headers=self.headers,
                json={
                    "query": "What are the latest trends in algorithmic trading?",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                citations = len(data.get('citations', []))
                self.log_test("CORE", "Research Ask", "PASS", f"Answer: {len(data.get('answer', ''))} chars, Citations: {citations}", time.time() - start_time)
            else:
                self.log_test("CORE", "Research Ask", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("CORE", "Research Ask", "ERROR", str(e), time.time() - start_time)
        
        # Test spec extraction
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                json={
                    "query": "Create a trading strategy for mean reversion",
                    "mode": "spec",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("CORE", "Spec Extraction", "PASS", f"Answer: {len(data.get('answer', ''))} chars", time.time() - start_time)
            else:
                self.log_test("CORE", "Spec Extraction", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("CORE", "Spec Extraction", "ERROR", str(e), time.time() - start_time)
    
    def test_advanced_features(self):
        """Test advanced RAG features"""
        print("\n🔍 TESTING ADVANCED RAG FEATURES")
        print("-" * 50)
        
        # Test query analyzer
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/analyze-query",
                headers=self.headers,
                data={"query": "How to implement a complex momentum trading strategy with risk management?"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                complexity = data.get('complexity', 'unknown')
                self.log_test("ADVANCED", "Query Analyzer", "PASS", f"Complexity: {complexity}", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Query Analyzer", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Query Analyzer", "ERROR", str(e), time.time() - start_time)
        
        # Test advanced search
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/advanced-search",
                headers=self.headers,
                data={"query": "momentum trading strategy", "top_k": 5},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                results_count = data.get('count', 0)
                self.log_test("ADVANCED", "Advanced Search", "PASS", f"Found {results_count} results", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Advanced Search", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Advanced Search", "ERROR", str(e), time.time() - start_time)
        
        # Test query expansion
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/expand-query",
                headers=self.headers,
                data={"query": "RSI trading strategy", "expansion_level": "medium"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                expanded_count = len(data.get('expanded_queries', []))
                confidence = data.get('confidence_score', 0)
                self.log_test("ADVANCED", "Query Expansion", "PASS", f"Generated {expanded_count} queries, Confidence: {confidence:.2f}", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Query Expansion", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Query Expansion", "ERROR", str(e), time.time() - start_time)
        
        # Test reranking
        start_time = time.time()
        try:
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
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                reranked_count = len(data.get('reranked_results', []))
                self.log_test("ADVANCED", "Reranking", "PASS", f"Reranked {reranked_count} results", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Reranking", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Reranking", "ERROR", str(e), time.time() - start_time)
        
        # Test context compression
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
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                compression_ratio = data.get('compression_ratio', 0)
                quality_score = data.get('quality_score', 0)
                self.log_test("ADVANCED", "Context Compression", "PASS", f"Ratio: {compression_ratio:.2f}, Quality: {quality_score:.2f}", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Context Compression", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Context Compression", "ERROR", str(e), time.time() - start_time)
        
        # Test metadata extraction
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
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                domain = data.get('trading_domain', 'unknown')
                complexity = data.get('complexity_level', 'unknown')
                concepts = len(data.get('key_concepts', []))
                self.log_test("ADVANCED", "Metadata Extraction", "PASS", f"Domain: {domain}, Complexity: {complexity}, Concepts: {concepts}", time.time() - start_time)
            else:
                self.log_test("ADVANCED", "Metadata Extraction", "FAIL", f"HTTP {response.status_code}", time.time() - start_time)
        except Exception as e:
            self.log_test("ADVANCED", "Metadata Extraction", "ERROR", str(e), time.time() - start_time)
    
    def test_document_operations(self):
        """Test document ingestion and management"""
        print("\n🔍 TESTING DOCUMENT OPERATIONS")
        print("-" * 50)
        
        # Test document ingestion
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ingest",
                headers=self.headers,
                json={
                    "text": "This is a test document about algorithmic trading strategies and risk management. It covers various aspects of quantitative finance and portfolio optimization.",
                    "title": "Test Trading Document",
                    "source": "test_ingestion"
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                doc_id = data.get('document_id', 'unknown')
                self.log_test("DOCS", "Document Ingestion", "PASS", f"Document ID: {doc_id}", time.time() - start_time)
            else:
                self.log_test("DOCS", "Document Ingestion", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("DOCS", "Document Ingestion", "ERROR", str(e), time.time() - start_time)
        
        # Test document filtering
        start_time = time.time()
        try:
            sample_documents = [
                {
                    "id": "doc_1",
                    "title": "Sample Document 1",
                    "text": "This is a sample document about trading strategies",
                    "metadata": {
                        "trading_domain": "technical_analysis",
                        "complexity_level": "intermediate"
                    }
                },
                {
                    "id": "doc_2", 
                    "title": "Sample Document 2",
                    "text": "This is a sample document about portfolio management",
                    "metadata": {
                        "trading_domain": "portfolio_management",
                        "complexity_level": "expert"
                    }
                }
            ]
            
            response = requests.post(
                f"{self.base_url}/filter-documents",
                headers=self.headers,
                data={
                    "documents": json.dumps(sample_documents),
                    "filters": json.dumps({
                        "trading_domain": "technical_analysis",
                        "complexity_level": "intermediate"
                    })
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                filtered_count = len(data.get('filtered_documents', []))
                self.log_test("DOCS", "Document Filtering", "PASS", f"Filtered {filtered_count} documents", time.time() - start_time)
            else:
                self.log_test("DOCS", "Document Filtering", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("DOCS", "Document Filtering", "ERROR", str(e), time.time() - start_time)
    
    def test_problematic_endpoints(self):
        """Test endpoints that were previously failing"""
        print("\n🔍 TESTING PROBLEMATIC ENDPOINTS")
        print("-" * 50)
        
        # Test Obsidian endpoint (was failing with asyncio.run error)
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask-obsidian",
                headers=self.headers,
                json={
                    "query": "test query about trading strategies",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("PROBLEMATIC", "Obsidian Integration", "PASS", f"Answer: {len(data.get('answer', ''))} chars", time.time() - start_time)
            else:
                self.log_test("PROBLEMATIC", "Obsidian Integration", "FAIL", f"HTTP {response.status_code}: {response.text[:100]}", time.time() - start_time)
        except Exception as e:
            self.log_test("PROBLEMATIC", "Obsidian Integration", "ERROR", str(e), time.time() - start_time)
    
    def test_performance(self):
        """Test system performance"""
        print("\n🔍 TESTING PERFORMANCE")
        print("-" * 50)
        
        # Test response times
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                json={
                    "query": "What is technical analysis?",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("PERF", "Response Time", "PASS", f"Response time: {duration:.2f}s", duration)
            else:
                self.log_test("PERF", "Response Time", "FAIL", f"HTTP {response.status_code}", duration)
        except Exception as e:
            self.log_test("PERF", "Response Time", "ERROR", str(e), time.time() - start_time)
    
    def run_comprehensive_qa(self):
        """Run comprehensive QA tests"""
        print("🚀 COMPREHENSIVE QA TESTING")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - stopping tests")
            return False
        
        # Run all test categories
        self.test_core_endpoints()
        self.test_advanced_features()
        self.test_document_operations()
        self.test_problematic_endpoints()
        self.test_performance()
        
        # Print comprehensive summary
        self.print_summary()
        
        return self.results['failed'] == 0 and self.results['errors'] == 0
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QA SUMMARY")
        print("=" * 80)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        errors = self.results['errors']
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        print("-" * 50)
        for category, stats in self.results['categories'].items():
            total_cat = stats['passed'] + stats['failed'] + stats['errors']
            success_rate = (stats['passed'] / total_cat) * 100 if total_cat > 0 else 0
            print(f"{category}: {stats['passed']}/{total_cat} ({success_rate:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! System is fully operational.")
        else:
            print(f"\n⚠️  {failed + errors} TESTS FAILED! Please review and fix issues.")

def main():
    """Main QA runner"""
    print("🔧 TradingAI Research Platform - Comprehensive QA")
    print("=" * 60)
    
    qa = ComprehensiveQA()
    success = qa.run_comprehensive_qa()
    
    if success:
        print("\n🎉 QA COMPLETE! All systems operational.")
        return 0
    else:
        print("\n❌ QA FAILED! Please review results and fix issues.")
        return 1

if __name__ == "__main__":
    exit(main())