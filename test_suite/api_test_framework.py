#!/usr/bin/env python3
"""
Comprehensive API Test Framework for TradingAI Research Platform
Tests all modes (QA, SPEC, WEB, RESEARCH) with 4 different Ollama models
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Individual test result"""
    prompt_id: int
    mode: str
    model: str
    complexity: str
    success: bool
    response_time: float
    answer_length: int
    citations: int
    error_message: Optional[str] = None
    cached: bool = False

@dataclass
class TestSuiteResults:
    """Complete test suite results"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    success_rate: float
    average_response_time: float
    results: List[TestResult]
    model_performance: Dict[str, Dict]
    mode_performance: Dict[str, Dict]
    complexity_performance: Dict[str, Dict]
    start_time: datetime
    end_time: datetime
    duration_seconds: float

class APITestFramework:
    """Main test framework class"""
    
    def __init__(self, base_url: str = "http://localhost:8002", 
                 username: str = "admin", password: str = "admin123"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.headers = None
        
        # Model mapping based on complexity
        self.model_mapping = {
            "simple": "llama3.2:3b",      # Small model
            "medium": "llama3.1:latest",  # Medium model  
            "complex": "qwen2.5-coder:14b", # Large model
            "research": "deepseek-r1:latest" # Thinking model
        }
        
        # Test modes
        self.test_modes = ["qa", "spec", "web", "research"]
        
        # Test prompts by complexity
        self.test_prompts = {
            "simple": [
                "What is a moving average in trading?",
                "Explain what a stop loss is",
                "What is the difference between a bull and bear market?",
                "Define volatility in financial markets",
                "What is a trading volume?",
                "Explain what a dividend is"
            ],
            "medium": [
                "How do you calculate the Sharpe ratio for a trading strategy?",
                "What is the difference between fundamental and technical analysis in stock trading?",
                "Explain how to use Bollinger Bands for trading decisions",
                "What are the key components of a trading plan?",
                "How do you calculate position sizing based on risk management?",
                "What is the difference between market orders and limit orders?",
                "Explain how to use the MACD indicator for trend analysis",
                "What are the advantages and disadvantages of day trading?"
            ],
            "complex": [
                "Design a comprehensive backtesting framework for quantitative trading strategies including walk-forward analysis and Monte Carlo simulation",
                "Explain how to implement a pairs trading strategy using statistical arbitrage and cointegration analysis",
                "Analyze the impact of market microstructure on high-frequency trading strategies and execution algorithms",
                "How do you build a multi-asset portfolio optimization model using modern portfolio theory and factor models?",
                "Explain the implementation of machine learning models for algorithmic trading including feature engineering and model validation",
                "What are the key considerations for building a low-latency trading system with microsecond execution times?",
                "How do you implement risk management for a multi-strategy hedge fund including VaR, stress testing, and scenario analysis?"
            ],
            "research": [
                "Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact",
                "Provide an in-depth study of market making strategies in cryptocurrency markets including liquidity provision, risk management, and regulatory considerations",
                "Analyze the role of artificial intelligence and machine learning in modern quantitative finance including deep learning applications, natural language processing, and alternative data sources",
                "Examine the impact of ESG (Environmental, Social, Governance) factors on quantitative investment strategies and portfolio construction in institutional asset management"
            ]
        }
    
    def authenticate(self) -> bool:
        """Authenticate with the API"""
        try:
            logger.info("🔐 Authenticating...")
            response = requests.post(
                f"{self.base_url}/auth/login",
                data={"username": self.username, "password": self.password},
                timeout=10
            )
            
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                logger.info("✅ Authentication successful!")
                return True
            else:
                logger.error(f"❌ Authentication failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False
    
    def run_single_test(self, prompt: str, complexity: str, mode: str, 
                       prompt_id: int, timeout: int = 60) -> TestResult:
        """Run a single test"""
        model = self.model_mapping[complexity]
        
        # Prepare request data
        request_data = {
            "query": f"{prompt} (test_{int(time.time())}_{prompt_id})",
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": model,
            "disable_model_override": True  # Ensure we use the requested model
        }
        
        # Add mode-specific parameters
        if mode == "spec":
            request_data["top_k"] = 10
        elif mode == "web":
            request_data["web_enabled"] = True
        elif mode == "research":
            request_data["research_enabled"] = True
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                json=request_data,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                citations = len(data.get('citations', []))
                cached = data.get('cached', False)
                
                if answer and len(answer) > 100:
                    return TestResult(
                        prompt_id=prompt_id,
                        mode=mode,
                        model=model,
                        complexity=complexity,
                        success=True,
                        response_time=response_time,
                        answer_length=len(answer),
                        citations=citations,
                        cached=cached
                    )
                else:
                    return TestResult(
                        prompt_id=prompt_id,
                        mode=mode,
                        model=model,
                        complexity=complexity,
                        success=False,
                        response_time=response_time,
                        answer_length=len(answer),
                        citations=citations,
                        error_message="Empty or too short answer",
                        cached=cached
                    )
            else:
                return TestResult(
                    prompt_id=prompt_id,
                    mode=mode,
                    model=model,
                    complexity=complexity,
                    success=False,
                    response_time=response_time,
                    answer_length=0,
                    citations=0,
                    error_message=f"HTTP {response.status_code}",
                    cached=False
                )
                
        except requests.exceptions.Timeout:
            return TestResult(
                prompt_id=prompt_id,
                mode=mode,
                model=model,
                complexity=complexity,
                success=False,
                response_time=timeout,
                answer_length=0,
                citations=0,
                error_message="Timeout",
                cached=False
            )
        except Exception as e:
            return TestResult(
                prompt_id=prompt_id,
                mode=mode,
                model=model,
                complexity=complexity,
                success=False,
                response_time=time.time() - start_time,
                answer_length=0,
                citations=0,
                error_message=str(e),
                cached=False
            )
    
    def run_comprehensive_test(self, timeout: int = 60) -> TestSuiteResults:
        """Run comprehensive test suite"""
        if not self.authenticate():
            raise Exception("Authentication failed")
        
        logger.info("🚀 Starting comprehensive API test suite")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        results = []
        
        # Generate all test combinations
        prompt_id = 1
        for complexity, prompts in self.test_prompts.items():
            for prompt in prompts:
                for mode in self.test_modes:
                    logger.info(f"🧪 Testing: {complexity.upper()} - {mode.upper()} - Prompt {prompt_id}")
                    
                    result = self.run_single_test(
                        prompt=prompt,
                        complexity=complexity,
                        mode=mode,
                        prompt_id=prompt_id,
                        timeout=timeout
                    )
                    
                    results.append(result)
                    
                    status = "✅" if result.success else "❌"
                    cached = " (CACHED)" if result.cached else ""
                    logger.info(f"   {status} {result.response_time:.2f}s{cached}")
                
                prompt_id += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Calculate statistics
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = len(results) - successful_tests
        success_rate = (successful_tests / len(results)) * 100
        
        # Calculate average response time (excluding cached)
        non_cached_times = [r.response_time for r in results if not r.cached]
        avg_response_time = statistics.mean(non_cached_times) if non_cached_times else 0
        
        # Performance by model
        model_performance = {}
        for model in self.model_mapping.values():
            model_results = [r for r in results if r.model == model]
            if model_results:
                model_performance[model] = {
                    "total": len(model_results),
                    "successful": sum(1 for r in model_results if r.success),
                    "failed": sum(1 for r in model_results if r.success == False),
                    "avg_response_time": statistics.mean([r.response_time for r in model_results if not r.cached]),
                    "cached_count": sum(1 for r in model_results if r.cached)
                }
        
        # Performance by mode
        mode_performance = {}
        for mode in self.test_modes:
            mode_results = [r for r in results if r.mode == mode]
            if mode_results:
                mode_performance[mode] = {
                    "total": len(mode_results),
                    "successful": sum(1 for r in mode_results if r.success),
                    "failed": sum(1 for r in mode_results if r.success == False),
                    "avg_response_time": statistics.mean([r.response_time for r in mode_results if not r.cached]),
                    "cached_count": sum(1 for r in mode_results if r.cached)
                }
        
        # Performance by complexity
        complexity_performance = {}
        for complexity in self.test_prompts.keys():
            complexity_results = [r for r in results if r.complexity == complexity]
            if complexity_results:
                complexity_performance[complexity] = {
                    "total": len(complexity_results),
                    "successful": sum(1 for r in complexity_results if r.success),
                    "failed": sum(1 for r in complexity_results if r.success == False),
                    "avg_response_time": statistics.mean([r.response_time for r in complexity_results if not r.cached]),
                    "cached_count": sum(1 for r in complexity_results if r.cached)
                }
        
        return TestSuiteResults(
            total_tests=len(results),
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            average_response_time=avg_response_time,
            results=results,
            model_performance=model_performance,
            mode_performance=mode_performance,
            complexity_performance=complexity_performance,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration
        )
    
    def print_results(self, results: TestSuiteResults):
        """Print formatted test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE API TEST RESULTS")
        print("=" * 80)
        print(f"⏰ Started: {results.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Completed: {results.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {results.duration_seconds:.1f} seconds")
        print(f"📊 Total tests: {results.total_tests}")
        print(f"✅ Successful: {results.successful_tests}")
        print(f"❌ Failed: {results.failed_tests}")
        print(f"📈 Success rate: {results.success_rate:.1f}%")
        print(f"⚡ Avg response time: {results.average_response_time:.2f}s")
        
        # Model performance
        print(f"\n🤖 MODEL PERFORMANCE:")
        print("-" * 40)
        for model, perf in results.model_performance.items():
            success_rate = (perf['successful'] / perf['total']) * 100
            print(f"{model}:")
            print(f"  Total: {perf['total']}, Success: {perf['successful']}, Failed: {perf['failed']}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg response time: {perf['avg_response_time']:.2f}s")
            print(f"  Cached responses: {perf['cached_count']}")
            print()
        
        # Mode performance
        print(f"🔄 MODE PERFORMANCE:")
        print("-" * 40)
        for mode, perf in results.mode_performance.items():
            success_rate = (perf['successful'] / perf['total']) * 100
            print(f"{mode.upper()}:")
            print(f"  Total: {perf['total']}, Success: {perf['successful']}, Failed: {perf['failed']}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg response time: {perf['avg_response_time']:.2f}s")
            print(f"  Cached responses: {perf['cached_count']}")
            print()
        
        # Complexity performance
        print(f"📊 COMPLEXITY PERFORMANCE:")
        print("-" * 40)
        for complexity, perf in results.complexity_performance.items():
            success_rate = (perf['successful'] / perf['total']) * 100
            print(f"{complexity.upper()}:")
            print(f"  Total: {perf['total']}, Success: {perf['successful']}, Failed: {perf['failed']}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Avg response time: {perf['avg_response_time']:.2f}s")
            print(f"  Cached responses: {perf['cached_count']}")
            print()
        
        # Failures
        if results.failed_tests > 0:
            print(f"❌ FAILURES ({results.failed_tests}):")
            print("-" * 40)
            for i, result in enumerate([r for r in results.results if not r.success], 1):
                print(f"{i}. Prompt {result.prompt_id}, {result.mode.upper()}, {result.model}: {result.error_message}")
        
        print("=" * 80)
        
        # Test validity
        if results.failed_tests == 0:
            print("✅ TEST VALID: 0 failed responses")
        else:
            print(f"🚨 TEST INVALIDATED: {results.failed_tests} failed responses")
    
    def save_results(self, results: TestSuiteResults, filename: str = None):
        """Save results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        # Convert results to serializable format
        results_dict = {
            "summary": {
                "total_tests": results.total_tests,
                "successful_tests": results.successful_tests,
                "failed_tests": results.failed_tests,
                "success_rate": results.success_rate,
                "average_response_time": results.average_response_time,
                "start_time": results.start_time.isoformat(),
                "end_time": results.end_time.isoformat(),
                "duration_seconds": results.duration_seconds
            },
            "model_performance": results.model_performance,
            "mode_performance": results.mode_performance,
            "complexity_performance": results.complexity_performance,
            "detailed_results": [
                {
                    "prompt_id": r.prompt_id,
                    "mode": r.mode,
                    "model": r.model,
                    "complexity": r.complexity,
                    "success": r.success,
                    "response_time": r.response_time,
                    "answer_length": r.answer_length,
                    "citations": r.citations,
                    "error_message": r.error_message,
                    "cached": r.cached
                }
                for r in results.results
            ]
        }
        
        # Ensure test_suite directory exists
        Path("test_suite").mkdir(exist_ok=True)
        
        filepath = Path("test_suite") / filename
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        logger.info(f"📁 Results saved to: {filepath}")

def main():
    """Main function to run the test suite"""
    framework = APITestFramework()
    
    try:
        results = framework.run_comprehensive_test(timeout=60)
        framework.print_results(results)
        framework.save_results(results)
        
        # Return exit code based on test validity
        return 0 if results.failed_tests == 0 else 1
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())