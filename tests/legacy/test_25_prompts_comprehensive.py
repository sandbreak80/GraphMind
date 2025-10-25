#!/usr/bin/env python3
"""Comprehensive test with 25 diverse prompts across different models and modes."""
import requests
import time
import statistics
import json
from datetime import datetime

def test_25_prompts():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🚀 COMPREHENSIVE 25-PROMPT TEST")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Testing: 25 diverse prompts across models and modes")
    print("🧵 Mode: Single-threaded (GPU-optimized)")
    print("=" * 70)
    
    # 25 diverse test prompts covering different complexities and use cases
    test_prompts = [
        # Simple queries (5) - should use llama3.2:3b + simple profile
        {
            "query": "What is trading?",
            "expected_complexity": "simple",
            "description": "Basic definition query"
        },
        {
            "query": "Explain RSI",
            "expected_complexity": "simple", 
            "description": "Simple technical indicator"
        },
        {
            "query": "What is momentum?",
            "expected_complexity": "simple",
            "description": "Basic concept query"
        },
        {
            "query": "Define support and resistance",
            "expected_complexity": "simple",
            "description": "Basic trading concepts"
        },
        {
            "query": "What is a candlestick?",
            "expected_complexity": "simple",
            "description": "Basic chart element"
        },
        
        # Medium queries (8) - should use llama3.1:latest + medium profile
        {
            "query": "Explain RSI indicator and how it works in technical analysis",
            "expected_complexity": "medium",
            "description": "Technical indicator explanation"
        },
        {
            "query": "What is momentum trading and how does it work?",
            "expected_complexity": "medium",
            "description": "Strategy explanation"
        },
        {
            "query": "Compare MACD and RSI indicators",
            "expected_complexity": "medium",
            "description": "Indicator comparison"
        },
        {
            "query": "How do you identify support and resistance levels?",
            "expected_complexity": "medium",
            "description": "Technical analysis method"
        },
        {
            "query": "What are the different types of trading orders?",
            "expected_complexity": "medium",
            "description": "Trading mechanics"
        },
        {
            "query": "Explain the concept of risk management in trading",
            "expected_complexity": "medium",
            "description": "Risk management basics"
        },
        {
            "query": "What is the difference between fundamental and technical analysis?",
            "expected_complexity": "medium",
            "description": "Analysis type comparison"
        },
        {
            "query": "How do you calculate position sizing in trading?",
            "expected_complexity": "medium",
            "description": "Position sizing methodology"
        },
        
        # Complex queries (7) - should use qwen2.5-coder:14b + complex profile
        {
            "query": "Compare momentum and mean reversion strategies with technical analysis",
            "expected_complexity": "complex",
            "description": "Strategy comparison with analysis"
        },
        {
            "query": "Analyze the relationship between volume and price movements in trading",
            "expected_complexity": "complex",
            "description": "Volume-price analysis"
        },
        {
            "query": "Explain how to build a trading system using multiple indicators",
            "expected_complexity": "complex",
            "description": "Trading system development"
        },
        {
            "query": "What are the advantages and disadvantages of different timeframes in trading?",
            "expected_complexity": "complex",
            "description": "Timeframe analysis"
        },
        {
            "query": "How do you backtest a trading strategy effectively?",
            "expected_complexity": "complex",
            "description": "Backtesting methodology"
        },
        {
            "query": "Compare different risk management techniques for day trading",
            "expected_complexity": "complex",
            "description": "Risk management comparison"
        },
        {
            "query": "Explain the psychology of trading and common behavioral biases",
            "expected_complexity": "complex",
            "description": "Trading psychology"
        },
        
        # Research queries (5) - should use gpt-oss:20b + research profile
        {
            "query": "Provide a comprehensive, detailed, and thorough analysis of current market conditions with extensive research into multiple trading strategies",
            "expected_complexity": "research",
            "description": "Comprehensive market analysis"
        },
        {
            "query": "Conduct an in-depth study of algorithmic trading systems and their implementation strategies",
            "expected_complexity": "research",
            "description": "Algorithmic trading research"
        },
        {
            "query": "Analyze the complete evolution of trading strategies from traditional to modern quantitative approaches",
            "expected_complexity": "research",
            "description": "Trading strategy evolution"
        },
        {
            "query": "Provide extensive research on market microstructure and its impact on trading performance",
            "expected_complexity": "research",
            "description": "Market microstructure research"
        },
        {
            "query": "Conduct a comprehensive analysis of different asset classes and their trading characteristics",
            "expected_complexity": "research",
            "description": "Multi-asset analysis"
        }
    ]
    
    # Test different modes
    test_modes = ["qa", "spec", "web", "research"]
    
    # Results storage
    results = []
    mode_results = {mode: [] for mode in test_modes}
    complexity_results = {"simple": [], "medium": [], "complex": [], "research": []}
    
    print(f"\n🧪 Testing {len(test_prompts)} prompts across {len(test_modes)} modes")
    print(f"📊 Total tests: {len(test_prompts) * len(test_modes)}")
    print("-" * 70)
    
    test_count = 0
    total_tests = len(test_prompts) * len(test_modes)
    
    for prompt_idx, prompt_data in enumerate(test_prompts, 1):
        query = prompt_data["query"]
        expected_complexity = prompt_data["expected_complexity"]
        description = prompt_data["description"]
        
        print(f"\n📝 Prompt {prompt_idx}/25: {description}")
        print(f"   Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"   Expected complexity: {expected_complexity}")
        
        for mode_idx, mode in enumerate(test_modes, 1):
            test_count += 1
            print(f"\n   🔄 Mode {mode_idx}/4: {mode.upper()}")
            
            start_time = time.time()
            try:
                # Prepare request based on mode
                request_data = {
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
                
                # Add mode-specific parameters
                if mode == "spec":
                    request_data["top_k"] = 10
                elif mode == "web":
                    request_data["web_enabled"] = True
                elif mode == "research":
                    request_data["research_enabled"] = True
                
                response = requests.post(
                    f"{base_url}/ask",
                    headers=headers,
                    json=request_data,
                    timeout=120  # Longer timeout for complex queries
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer_length = len(data.get('answer', ''))
                    citations_count = len(data.get('citations', []))
                    
                    # Determine if cached
                    is_cached = response_time < 0.1
                    
                    result = {
                        'prompt_id': prompt_idx,
                        'mode': mode,
                        'query': query,
                        'expected_complexity': expected_complexity,
                        'response_time': response_time,
                        'answer_length': answer_length,
                        'citations_count': citations_count,
                        'is_cached': is_cached,
                        'success': True,
                        'status_code': response.status_code
                    }
                    
                    print(f"      ✅ Success: {response_time:.2f}s")
                    print(f"      📝 Answer: {answer_length} chars")
                    print(f"      📚 Citations: {citations_count}")
                    if is_cached:
                        print(f"      💾 CACHED")
                    
                else:
                    result = {
                        'prompt_id': prompt_idx,
                        'mode': mode,
                        'query': query,
                        'expected_complexity': expected_complexity,
                        'response_time': response_time,
                        'answer_length': 0,
                        'citations_count': 0,
                        'is_cached': False,
                        'success': False,
                        'status_code': response.status_code,
                        'error': response.text[:100]
                    }
                    
                    print(f"      ❌ Failed: {response.status_code}")
                    print(f"      📝 Error: {response.text[:100]}...")
                
                # Store results
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[expected_complexity].append(result)
                
            except requests.exceptions.Timeout:
                result = {
                    'prompt_id': prompt_idx,
                    'mode': mode,
                    'query': query,
                    'expected_complexity': expected_complexity,
                    'response_time': 120.0,
                    'answer_length': 0,
                    'citations_count': 0,
                    'is_cached': False,
                    'success': False,
                    'status_code': 408,
                    'error': 'Timeout'
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[expected_complexity].append(result)
                
                print(f"      ⏰ Timeout after 120s")
                
            except Exception as e:
                result = {
                    'prompt_id': prompt_idx,
                    'mode': mode,
                    'query': query,
                    'expected_complexity': expected_complexity,
                    'response_time': 0,
                    'answer_length': 0,
                    'citations_count': 0,
                    'is_cached': False,
                    'success': False,
                    'status_code': 500,
                    'error': str(e)
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[expected_complexity].append(result)
                
                print(f"      ❌ Error: {e}")
            
            # Progress update
            progress = (test_count / total_tests) * 100
            print(f"      📊 Progress: {test_count}/{total_tests} ({progress:.1f}%)")
    
    # Analysis and reporting
    print(f"\n📊 COMPREHENSIVE ANALYSIS")
    print("=" * 70)
    
    # Overall statistics
    successful_results = [r for r in results if r['success']]
    failed_results = [r for r in results if not r['success']]
    
    print(f"\n📈 Overall Performance:")
    print(f"   Total tests: {len(results)}")
    print(f"   Successful: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
    print(f"   Failed: {len(failed_results)} ({len(failed_results)/len(results)*100:.1f}%)")
    
    if successful_results:
        response_times = [r['response_time'] for r in successful_results]
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        print(f"   Median response time: {statistics.median(response_times):.2f}s")
        print(f"   Standard deviation: {statistics.stdev(response_times):.2f}s")
    
    # Mode analysis
    print(f"\n🔄 Performance by Mode:")
    for mode, mode_data in mode_results.items():
        if mode_data:
            successful_mode = [r for r in mode_data if r['success']]
            if successful_mode:
                mode_times = [r['response_time'] for r in successful_mode]
                cached_count = sum(1 for r in successful_mode if r['is_cached'])
                print(f"   {mode.upper()}:")
                print(f"      Success rate: {len(successful_mode)}/{len(mode_data)} ({len(successful_mode)/len(mode_data)*100:.1f}%)")
                print(f"      Avg response time: {statistics.mean(mode_times):.2f}s")
                print(f"      Cached responses: {cached_count}/{len(successful_mode)} ({cached_count/len(successful_mode)*100:.1f}%)")
    
    # Complexity analysis
    print(f"\n🎯 Performance by Complexity:")
    for complexity, comp_data in complexity_results.items():
        if comp_data:
            successful_comp = [r for r in comp_data if r['success']]
            if successful_comp:
                comp_times = [r['response_time'] for r in successful_comp]
                cached_count = sum(1 for r in successful_comp if r['is_cached'])
                print(f"   {complexity.upper()}:")
                print(f"      Success rate: {len(successful_comp)}/{len(comp_data)} ({len(successful_comp)/len(comp_data)*100:.1f}%)")
                print(f"      Avg response time: {statistics.mean(comp_times):.2f}s")
                print(f"      Cached responses: {cached_count}/{len(successful_comp)} ({cached_count/len(successful_comp)*100:.1f}%)")
    
    # Caching analysis
    cached_results = [r for r in successful_results if r['is_cached']]
    non_cached_results = [r for r in successful_results if not r['is_cached']]
    
    print(f"\n💾 Caching Performance:")
    print(f"   Cached responses: {len(cached_results)} ({len(cached_results)/len(successful_results)*100:.1f}%)")
    print(f"   Non-cached responses: {len(non_cached_results)} ({len(non_cached_results)/len(successful_results)*100:.1f}%)")
    
    if cached_results and non_cached_results:
        cached_times = [r['response_time'] for r in cached_results]
        non_cached_times = [r['response_time'] for r in non_cached_results]
        print(f"   Cached avg time: {statistics.mean(cached_times):.2f}s")
        print(f"   Non-cached avg time: {statistics.mean(non_cached_times):.2f}s")
        improvement = ((statistics.mean(non_cached_times) - statistics.mean(cached_times)) / statistics.mean(non_cached_times)) * 100
        print(f"   Caching improvement: {improvement:.1f}%")
    
    # Error analysis
    if failed_results:
        print(f"\n❌ Error Analysis:")
        error_types = {}
        for result in failed_results:
            error_type = result.get('error', 'Unknown')[:50]
            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1
        
        for error_type, count in error_types.items():
            print(f"   {error_type}: {count} occurrences")
    
    # Get final monitoring data
    print(f"\n📊 Final System Monitoring:")
    try:
        # Performance metrics
        response = requests.get(f"{base_url}/monitoring/performance")
        if response.status_code == 200:
            perf_metrics = response.json()
            print(f"   Total queries processed: {perf_metrics.get('total_queries', 0)}")
            print(f"   System avg response time: {perf_metrics.get('avg_response_time', 0):.2f}s")
            print(f"   System error rate: {perf_metrics.get('error_rate', 0):.2%}")
            print(f"   Model usage: {perf_metrics.get('model_usage', {})}")
        
        # Cache metrics
        response = requests.get(f"{base_url}/monitoring/cache")
        if response.status_code == 200:
            cache_metrics = response.json()
            print(f"   Cache hit rate: {cache_metrics.get('hit_rate', 0):.2%}")
            print(f"   Cache size: {cache_metrics.get('cache_size', 0)}")
        
        # Retrieval metrics
        response = requests.get(f"{base_url}/monitoring/retrieval")
        if response.status_code == 200:
            retrieval_metrics = response.json()
            print(f"   Retrieval optimizer: {'✅ Active' if retrieval_metrics.get('optimizer_available') else '❌ Inactive'}")
            print(f"   Profiles configured: {len(retrieval_metrics.get('profiles', {}))}")
            
    except Exception as e:
        print(f"   ❌ Error getting monitoring data: {e}")
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 70)
    
    success_rate = len(successful_results) / len(results) * 100
    avg_response_time = statistics.mean([r['response_time'] for r in successful_results]) if successful_results else 0
    cache_hit_rate = len(cached_results) / len(successful_results) * 100 if successful_results else 0
    
    print(f"📊 Test Results Summary:")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Average Response Time: {avg_response_time:.2f}s")
    print(f"   Cache Hit Rate: {cache_hit_rate:.1f}%")
    print(f"   Total Tests: {len(results)}")
    
    # Performance grades
    if success_rate >= 95:
        print("✅ Success Rate: EXCELLENT")
    elif success_rate >= 90:
        print("✅ Success Rate: GOOD")
    else:
        print("⚠️  Success Rate: NEEDS IMPROVEMENT")
    
    if avg_response_time < 1.0:
        print("✅ Response Time: EXCELLENT")
    elif avg_response_time < 2.0:
        print("✅ Response Time: GOOD")
    else:
        print("⚠️  Response Time: NEEDS IMPROVEMENT")
    
    if cache_hit_rate >= 50:
        print("✅ Caching: EXCELLENT")
    elif cache_hit_rate >= 30:
        print("✅ Caching: GOOD")
    else:
        print("⚠️  Caching: NEEDS IMPROVEMENT")
    
    # Overall grade
    if success_rate >= 95 and avg_response_time < 1.0 and cache_hit_rate >= 50:
        print("\n🎉 OVERALL GRADE: A+ (EXCELLENT)")
        print("   System is performing exceptionally well!")
    elif success_rate >= 90 and avg_response_time < 2.0 and cache_hit_rate >= 30:
        print("\n✅ OVERALL GRADE: A (VERY GOOD)")
        print("   System is performing very well!")
    elif success_rate >= 80 and avg_response_time < 3.0:
        print("\n✅ OVERALL GRADE: B (GOOD)")
        print("   System is performing well with room for improvement!")
    else:
        print("\n⚠️  OVERALL GRADE: C (NEEDS IMPROVEMENT)")
        print("   System needs optimization!")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    results = test_25_prompts()