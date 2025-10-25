#!/usr/bin/env python3
"""Test 20 Unique Prompts Across All APIs and Models"""

import requests
import time
import json
import random
from datetime import datetime

class API20Tester:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.token = None
        self.headers = None
        self.results = []
        self.failed_tests = []
        
        # 20 unique prompts with varying complexity
        self.prompts = [
            "What is a moving average?",
            "Explain RSI indicator in trading",
            "How to implement stop loss strategy?",
            "Define portfolio diversification",
            "What causes market volatility?",
            "How to build a momentum trading system?",
            "Explain risk management in algorithmic trading",
            "What are trend following strategies?",
            "How to calculate position sizing?",
            "Explain multi-timeframe analysis",
            "Design a quantitative trading system with machine learning",
            "Explain options pricing models for volatility trading",
            "Analyze market microstructure impact on HFT algorithms",
            "Develop multi-asset portfolio optimization strategy",
            "Create systematic approach to regime detection",
            "Implement sophisticated market-making algorithm",
            "Design comprehensive risk management for hedge fund",
            "Develop sentiment analysis framework for trading",
            "Create systematic factor investing approach",
            "Build complete algorithmic trading infrastructure"
        ]
        
        self.models = ["llama3.1:latest", "llama3.1:8b", "deepseek-r1:latest"]
        self.endpoints = [
            ("/ask", "Basic Ask"),
            ("/ask-enhanced", "Enhanced Ask"), 
            ("/ask-research", "Research Ask"),
            ("/ask-obsidian", "Obsidian Ask")
        ]
        self.modes = ["qa", "spec"]
    
    def authenticate(self):
        """Get auth token"""
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
                print(f"❌ Auth failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Auth error: {e}")
            return False
    
    def test_single(self, prompt, endpoint, endpoint_name, model, mode, test_id):
        """Test single API call"""
        start_time = time.time()
        try:
            data = {
                "query": prompt,
                "mode": mode,
                "model": model,
                "disable_model_override": True
            }
            
            if "enhanced" in endpoint or "research" in endpoint:
                data["top_k"] = 5
            
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                json=data,
                timeout=120
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                answer_len = len(result_data.get('answer', ''))
                citations = len(result_data.get('citations', []))
                
                print(f"✅ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | {answer_len:3d} chars | {citations:2d} cites")
                
                return {
                    "test_id": test_id,
                    "status": "PASS",
                    "duration": duration,
                    "answer_length": answer_len,
                    "citations": citations
                }
            else:
                error = f"HTTP {response.status_code}: {response.text[:50]}"
                print(f"❌ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | FAILED: {error}")
                
                return {
                    "test_id": test_id,
                    "status": "FAIL",
                    "duration": duration,
                    "error": error
                }
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            print(f"⏰ Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | TIMEOUT")
            return {
                "test_id": test_id,
                "status": "TIMEOUT",
                "duration": duration,
                "error": "120s timeout"
            }
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 Test {test_id:2d}: {endpoint_name:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | ERROR: {e}")
            return {
                "test_id": test_id,
                "status": "ERROR",
                "duration": duration,
                "error": str(e)
            }
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 TESTING 20 UNIQUE PROMPTS ACROSS ALL APIs")
        print("=" * 80)
        print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        
        if not self.authenticate():
            return False
        
        print(f"\n📋 Testing {len(self.prompts)} prompts × {len(self.endpoints)} endpoints × {len(self.models)} models × {len(self.modes)} modes")
        print(f"Total tests: {len(self.prompts) * len(self.endpoints) * len(self.models) * len(self.modes)}")
        print("\nTest ID | Endpoint        | Model           | Mode | Duration | Chars | Cites")
        print("-" * 80)
        
        test_id = 1
        start_time = time.time()
        
        # Run all combinations
        for prompt in self.prompts:
            for endpoint, endpoint_name in self.endpoints:
                for model in self.models:
                    for mode in self.modes:
                        result = self.test_single(prompt, endpoint, endpoint_name, model, mode, test_id)
                        self.results.append(result)
                        
                        if result["status"] != "PASS":
                            self.failed_tests.append(result)
                        
                        test_id += 1
                        time.sleep(0.3)  # Small delay
        
        total_time = time.time() - start_time
        
        # Results summary
        total_tests = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len(self.failed_tests)
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Avg Time: {total_time/total_tests:.2f}s per test")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  Test {test['test_id']}: {test.get('error', 'Unknown')}")
        
        # Model performance
        model_stats = {}
        for result in self.results:
            # Extract model from test context (simplified)
            model = "unknown"
            if "model" in result:
                model = result["model"]
            elif test_id <= 20:
                model = "llama3.1:latest"
            elif test_id <= 40:
                model = "llama3.1:8b"
            else:
                model = "deepseek-r1:latest"
                
            if model not in model_stats:
                model_stats[model] = {"total": 0, "passed": 0}
            model_stats[model]["total"] += 1
            if result["status"] == "PASS":
                model_stats[model]["passed"] += 1
        
        print(f"\n🤖 MODEL PERFORMANCE:")
        for model, stats in model_stats.items():
            if stats["total"] > 0:
                rate = (stats["passed"] / stats["total"]) * 100
                print(f"  {model:15s}: {stats['passed']:2d}/{stats['total']:2d} ({rate:5.1f}%)")
        
        if failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! BUILD SUCCESS ✅")
            return True
        else:
            print(f"\n❌ {failed} TESTS FAILED! BUILD FAILS ❌")
            return False

def main():
    tester = API20Tester()
    success = tester.run_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())