#!/usr/bin/env python3
"""Comprehensive API Test - 20 Unique Prompts Across All Endpoints and Models"""

import requests
import time
import json
import random
from datetime import datetime
import threading
import queue

class ComprehensiveAPITester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.headers = None
        self.results = []
        self.failed_tests = []
        self.start_time = time.time()
        
        # Test prompts with varying complexity
        self.test_prompts = [
            # Simple queries
            "What is a moving average?",
            "Explain RSI indicator",
            "What is stop loss?",
            "Define portfolio diversification",
            "What is market volatility?",
            
            # Medium complexity
            "How to implement a momentum trading strategy using RSI and MACD?",
            "What are the key risk management principles for algorithmic trading?",
            "Explain the differences between trend following and mean reversion strategies",
            "How do you calculate position sizing in portfolio management?",
            "What are the advantages of using multiple timeframes in technical analysis?",
            
            # High complexity
            "Design a comprehensive quantitative trading system that combines machine learning with traditional technical indicators, including backtesting methodology and risk management framework",
            "Explain the mathematical foundations of options pricing models and their application in volatility trading strategies",
            "Analyze the impact of market microstructure on high-frequency trading algorithms and propose optimization techniques",
            "Develop a multi-asset portfolio optimization strategy using modern portfolio theory with transaction costs and liquidity constraints",
            "Create a systematic approach to regime detection in financial markets using statistical methods and machine learning",
            
            # Very high complexity
            "Implement a sophisticated market-making algorithm that dynamically adjusts bid-ask spreads based on order flow, volatility, and inventory risk while maintaining profitability across different market conditions",
            "Design a comprehensive risk management system for a multi-strategy hedge fund that includes real-time monitoring, stress testing, and automated position adjustments",
            "Develop an advanced sentiment analysis framework for trading that combines news sentiment, social media data, and market microstructure indicators",
            "Create a systematic approach to factor investing that identifies, validates, and implements alpha-generating factors while managing factor exposure and decay",
            "Build a complete algorithmic trading infrastructure including order management, execution algorithms, market data processing, and compliance monitoring"
        ]
        
        # Models to test
        self.models = [
            "llama3.1:latest",
            "llama3.1:8b",
            "llama3.1:70b",
            "deepseek-r1:latest"
        ]
        
        # API endpoints to test
        self.endpoints = [
            ("/ask", "Basic Ask"),
            ("/ask-enhanced", "Enhanced Ask"),
            ("/ask-research", "Research Ask"),
            ("/ask-obsidian", "Obsidian Ask")
        ]
        
        # Modes to test
        self.modes = ["qa", "spec", "research"]
    
    def authenticate(self):
        """Authenticate and get token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": "admin", "password": "admin123"},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_endpoint(self, endpoint, endpoint_name, prompt, model, mode, test_id):
        """Test a specific endpoint with given parameters"""
        start_time = time.time()
        try:
            # Prepare request data
            data = {
                "query": prompt,
                "mode": mode,
                "model": model,
                "disable_model_override": True
            }
            
            # Add top_k for enhanced endpoints
            if "enhanced" in endpoint or "research" in endpoint:
                data["top_k"] = 5
            
            # Make request
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                timeout=120  # 2 minute timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                answer_length = len(result_data.get('answer', ''))
                citations = len(result_data.get('citations', []))
                
                result = {
                    "test_id": test_id,
                    "endpoint": endpoint_name,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "model": model,
                    "mode": mode,
                    "status": "PASS",
                    "duration": duration,
                    "answer_length": answer_length,
                    "citations": citations,
                    "http_status": response.status_code
                }
                
                print(f"✅ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:8s} | {duration:6.2f}s | {answer_length:3d} chars | {citations:2d} citations")
                return result
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                result = {
                    "test_id": test_id,
                    "endpoint": endpoint_name,
                    "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                    "model": model,
                    "mode": mode,
                    "status": "FAIL",
                    "duration": duration,
                    "error": error_msg,
                    "http_status": response.status_code
                }
                
                print(f"❌ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:8s} | {duration:6.2f}s | FAILED: {error_msg}")
                return result
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            result = {
                "test_id": test_id,
                "endpoint": endpoint_name,
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "model": model,
                "mode": mode,
                "status": "TIMEOUT",
                "duration": duration,
                "error": "Request timeout after 120 seconds",
                "http_status": 0
            }
            print(f"⏰ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:8s} | {duration:6.2f}s | TIMEOUT")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            result = {
                "test_id": test_id,
                "endpoint": endpoint_name,
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "model": model,
                "mode": mode,
                "status": "ERROR",
                "duration": duration,
                "error": str(e),
                "http_status": 0
            }
            print(f"💥 Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:8s} | {duration:6.2f}s | ERROR: {e}")
            return result
    
    def test_advanced_endpoints(self):
        """Test advanced RAG endpoints"""
        print("\n🔍 TESTING ADVANCED RAG ENDPOINTS")
        print("-" * 80)
        
        advanced_tests = [
            ("/analyze-query", "Query Analyzer", "How to implement a complex momentum trading strategy with risk management?"),
            ("/advanced-search", "Advanced Search", "momentum trading strategy"),
            ("/expand-query", "Query Expansion", "RSI trading strategy"),
            ("/extract-metadata", "Metadata Extraction", "This is a comprehensive guide to algorithmic trading strategies and risk management."),
            ("/compress-context", "Context Compression", "A comprehensive trading strategy implementation involves multiple critical steps that must be carefully executed to ensure success in the financial markets. The first step is to define clear entry and exit rules based on technical analysis, fundamental analysis, or a combination of both approaches. Risk management is the cornerstone of any successful trading strategy. This involves setting appropriate position sizes based on account size and risk tolerance, implementing stop-loss orders to limit potential losses, and diversifying across different assets and timeframes."),
            ("/ingest", "Document Ingestion", "This is a test document about algorithmic trading strategies and risk management. It covers various aspects of quantitative finance and portfolio optimization.")
        ]
        
        test_id = 21
        for endpoint, name, data in advanced_tests:
            start_time = time.time()
            try:
                if endpoint == "/analyze-query":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        data={"query": data},
                        timeout=30
                    )
                elif endpoint == "/advanced-search":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        data={"query": data, "top_k": 5},
                        timeout=30
                    )
                elif endpoint == "/expand-query":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        data={"query": data, "expansion_level": "medium"},
                        timeout=30
                    )
                elif endpoint == "/extract-metadata":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        data={
                            "document_id": f"test_doc_{test_id}",
                            "title": "Test Document",
                            "text": data,
                            "source": "test"
                        },
                        timeout=30
                    )
                elif endpoint == "/compress-context":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        data={
                            "text": data,
                            "target_ratio": 0.3,
                            "method": "hybrid",
                            "max_length": 1000
                        },
                        timeout=30
                    )
                elif endpoint == "/ingest":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        headers=self.headers,
                        json={
                            "text": data,
                            "title": f"Test Document {test_id}",
                            "source": "test_ingestion"
                        },
                        timeout=30
                    )
                
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result_data = response.json()
                    print(f"✅ Test {test_id:2d}: {name:20s} | {duration:6.2f}s | SUCCESS")
                    self.results.append({
                        "test_id": test_id,
                        "endpoint": name,
                        "status": "PASS",
                        "duration": duration,
                        "http_status": response.status_code
                    })
                else:
                    print(f"❌ Test {test_id:2d}: {name:20s} | {duration:6.2f}s | FAILED: HTTP {response.status_code}")
                    self.failed_tests.append({
                        "test_id": test_id,
                        "endpoint": name,
                        "status": "FAIL",
                        "duration": duration,
                        "error": f"HTTP {response.status_code}: {response.text[:100]}",
                        "http_status": response.status_code
                    })
                    
            except Exception as e:
                duration = time.time() - start_time
                print(f"💥 Test {test_id:2d}: {name:20s} | {duration:6.2f}s | ERROR: {e}")
                self.failed_tests.append({
                    "test_id": test_id,
                    "endpoint": name,
                    "status": "ERROR",
                    "duration": duration,
                    "error": str(e),
                    "http_status": 0
                })
            
            test_id += 1
    
    def run_comprehensive_test(self):
        """Run comprehensive test with 20 unique prompts"""
        print("🚀 COMPREHENSIVE API TEST - 20 UNIQUE PROMPTS")
        print("=" * 80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - stopping tests")
            return False
        
        print(f"\n📋 Test Plan:")
        print(f"   • Prompts: {len(self.test_prompts)} unique prompts")
        print(f"   • Models: {len(self.models)} models")
        print(f"   • Endpoints: {len(self.endpoints)} endpoints")
        print(f"   • Modes: {len(self.modes)} modes")
        print(f"   • Total Tests: {len(self.test_prompts) * len(self.endpoints) * len(self.models) * len(self.modes)}")
        
        print(f"\n🔍 TESTING CORE API ENDPOINTS")
        print("-" * 80)
        print("Test ID | Endpoint        | Model           | Mode     | Duration | Chars | Citations")
        print("-" * 80)
        
        test_id = 1
        total_tests = 0
        
        # Test each prompt with each endpoint, model, and mode combination
        for prompt in self.test_prompts:
            for endpoint, endpoint_name in self.endpoints:
                for model in self.models:
                    for mode in self.modes:
                        total_tests += 1
                        result = self.test_endpoint(endpoint, endpoint_name, prompt, model, mode, test_id)
                        self.results.append(result)
                        
                        if result["status"] != "PASS":
                            self.failed_tests.append(result)
                        
                        test_id += 1
                        
                        # Small delay to avoid overwhelming the system
                        time.sleep(0.5)
        
        # Test advanced endpoints
        self.test_advanced_endpoints()
        
        # Calculate final statistics
        total_duration = time.time() - self.start_time
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len(self.failed_tests)
        total_tests = len(self.results)
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Average Duration: {total_duration/total_tests:.2f} seconds per test")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            print("-" * 80)
            for test in self.failed_tests:
                print(f"Test {test['test_id']:2d}: {test['endpoint']:20s} | {test['status']:8s} | {test.get('error', 'Unknown error')}")
        
        # Performance analysis
        durations = [r["duration"] for r in self.results if "duration" in r]
        if durations:
            print(f"\n📈 PERFORMANCE ANALYSIS:")
            print(f"   • Fastest Response: {min(durations):.2f}s")
            print(f"   • Slowest Response: {max(durations):.2f}s")
            print(f"   • Average Response: {sum(durations)/len(durations):.2f}s")
        
        # Model performance analysis
        model_stats = {}
        for result in self.results:
            if "model" in result:
                model = result["model"]
                if model not in model_stats:
                    model_stats[model] = {"total": 0, "passed": 0, "avg_duration": 0}
                model_stats[model]["total"] += 1
                if result["status"] == "PASS":
                    model_stats[model]["passed"] += 1
                model_stats[model]["avg_duration"] += result.get("duration", 0)
        
        print(f"\n🤖 MODEL PERFORMANCE:")
        for model, stats in model_stats.items():
            if stats["total"] > 0:
                success_rate = (stats["passed"] / stats["total"]) * 100
                avg_duration = stats["avg_duration"] / stats["total"]
                print(f"   • {model:15s}: {stats['passed']:2d}/{stats['total']:2d} ({success_rate:5.1f}%) | {avg_duration:.2f}s avg")
        
        # Endpoint performance analysis
        endpoint_stats = {}
        for result in self.results:
            if "endpoint" in result:
                endpoint = result["endpoint"]
                if endpoint not in endpoint_stats:
                    endpoint_stats[endpoint] = {"total": 0, "passed": 0, "avg_duration": 0}
                endpoint_stats[endpoint]["total"] += 1
                if result["status"] == "PASS":
                    endpoint_stats[endpoint]["passed"] += 1
                endpoint_stats[endpoint]["avg_duration"] += result.get("duration", 0)
        
        print(f"\n🔗 ENDPOINT PERFORMANCE:")
        for endpoint, stats in endpoint_stats.items():
            if stats["total"] > 0:
                success_rate = (stats["passed"] / stats["total"]) * 100
                avg_duration = stats["avg_duration"] / stats["total"]
                print(f"   • {endpoint:20s}: {stats['passed']:2d}/{stats['total']:2d} ({success_rate:5.1f}%) | {avg_duration:.2f}s avg")
        
        # Final result
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! System is fully operational.")
            print(f"✅ BUILD SUCCESS - Ready for commit and deployment")
            return True
        else:
            print(f"\n❌ {failed_tests} TESTS FAILED! Build fails.")
            print(f"❌ BUILD FAILURE - Fix issues before committing")
            return False

def main():
    """Main test runner"""
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())