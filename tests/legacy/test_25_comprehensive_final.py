#!/usr/bin/env python3
"""Final comprehensive 25-prompt test with performance analysis."""
import requests
import time
import statistics
import json
import random
from datetime import datetime

def test_25_comprehensive_final():
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
    
    print("\n🚀 FINAL COMPREHENSIVE 25-PROMPT TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Testing: 25 diverse prompts across 4 modes")
    print("🧵 Mode: Single-threaded (GPU-optimized)")
    print("🎯 Focus: Performance delta and response quality")
    print("=" * 80)
    
    # 25 diverse test prompts covering different complexities
    test_prompts = [
        # Simple queries (6)
        {"query": "What is trading?", "complexity": "simple", "description": "Basic definition"},
        {"query": "What is RSI in trading?", "complexity": "simple", "description": "Trading indicator"},
        {"query": "What is momentum in trading?", "complexity": "simple", "description": "Trading concept"},
        {"query": "Define support and resistance", "complexity": "simple", "description": "Trading concepts"},
        {"query": "What is a candlestick chart?", "complexity": "simple", "description": "Chart type"},
        {"query": "Calculate 2 + 2", "complexity": "simple", "description": "Math test"},
        
        # Medium queries (8)
        {"query": "Explain RSI indicator and how it works in technical analysis", "complexity": "medium", "description": "Technical analysis"},
        {"query": "What is momentum trading and how does it work?", "complexity": "medium", "description": "Trading strategy"},
        {"query": "Compare MACD and RSI indicators", "complexity": "medium", "description": "Indicator comparison"},
        {"query": "How do you identify support and resistance levels?", "complexity": "medium", "description": "Technical method"},
        {"query": "What are the different types of trading orders?", "complexity": "medium", "description": "Trading mechanics"},
        {"query": "Explain risk management in trading", "complexity": "medium", "description": "Risk management"},
        {"query": "What is the difference between fundamental and technical analysis?", "complexity": "medium", "description": "Analysis comparison"},
        {"query": "How do you calculate position sizing?", "complexity": "medium", "description": "Position sizing"},
        
        # Complex queries (7)
        {"query": "Compare momentum and mean reversion strategies with technical analysis", "complexity": "complex", "description": "Strategy comparison"},
        {"query": "Analyze the relationship between volume and price movements", "complexity": "complex", "description": "Volume analysis"},
        {"query": "Explain how to build a trading system using multiple indicators", "complexity": "complex", "description": "System building"},
        {"query": "What are the advantages of different timeframes in trading?", "complexity": "complex", "description": "Timeframe analysis"},
        {"query": "How do you backtest a trading strategy effectively?", "complexity": "complex", "description": "Backtesting"},
        {"query": "Compare different risk management techniques for day trading", "complexity": "complex", "description": "Risk management comparison"},
        {"query": "Explain trading psychology and common behavioral biases", "complexity": "complex", "description": "Trading psychology"},
        
        # Research queries (4)
        {"query": "Provide comprehensive analysis of current market conditions with multiple trading strategies", "complexity": "research", "description": "Market analysis"},
        {"query": "Conduct in-depth study of algorithmic trading systems", "complexity": "research", "description": "Algorithmic trading"},
        {"query": "Analyze the evolution of trading strategies from traditional to quantitative approaches", "complexity": "research", "description": "Strategy evolution"},
        {"query": "Provide extensive research on market microstructure and trading performance", "complexity": "research", "description": "Market microstructure"}
    ]
    
    # Test modes
    test_modes = ["qa", "spec", "web", "research"]
    
    # Results storage
    results = []
    mode_results = {mode: [] for mode in test_modes}
    complexity_results = {"simple": [], "medium": [], "complex": [], "research": []}
    
    print(f"\n🧪 Testing {len(test_prompts)} prompts across {len(test_modes)} modes")
    print(f"📊 Total tests: {len(test_prompts) * len(test_modes)}")
    print("-" * 80)
    
    test_count = 0
    total_tests = len(test_prompts) * len(test_modes)
    
    for prompt_idx, prompt_data in enumerate(test_prompts, 1):
        query = prompt_data["query"]
        complexity = prompt_data["complexity"]
        description = prompt_data["description"]
        
        print(f"\n📝 Prompt {prompt_idx}/25: {description}")
        print(f"   Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"   Complexity: {complexity}")
        
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
                    timeout=120
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '')
                    citations = data.get('citations', [])
                    
                    print(f"      ✅ Success: {response_time:.2f}s")
                    print(f"      📝 Answer: {len(answer)} chars")
                    print(f"      📚 Citations: {len(citations)}")
                    
                    # Determine if cached
                    is_cached = response_time < 0.1
                    if is_cached:
                        print(f"      💾 CACHED")
                    
                    result = {
                        'prompt_id': prompt_idx,
                        'mode': mode,
                        'query': query,
                        'complexity': complexity,
                        'response_time': response_time,
                        'answer_length': len(answer),
                        'citations_count': len(citations),
                        'is_cached': is_cached,
                        'success': True,
                        'status_code': response.status_code,
                        'answer_preview': answer[:100] + "..." if len(answer) > 100 else answer
                    }
                    
                else:
                    print(f"      ❌ Failed: {response.status_code}")
                    print(f"      📝 Error: {response.text[:100]}...")
                    
                    result = {
                        'prompt_id': prompt_idx,
                        'mode': mode,
                        'query': query,
                        'complexity': complexity,
                        'response_time': response_time,
                        'answer_length': 0,
                        'citations_count': 0,
                        'is_cached': False,
                        'success': False,
                        'status_code': response.status_code,
                        'answer_preview': '',
                        'error': response.text[:100]
                    }
                
                # Store results
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
                
            except requests.exceptions.Timeout:
                result = {
                    'prompt_id': prompt_idx,
                    'mode': mode,
                    'query': query,
                    'complexity': complexity,
                    'response_time': 120.0,
                    'answer_length': 0,
                    'citations_count': 0,
                    'is_cached': False,
                    'success': False,
                    'status_code': 408,
                    'answer_preview': '',
                    'error': 'Timeout'
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
                
                print(f"      ⏰ Timeout after 120s")
                
            except Exception as e:
                result = {
                    'prompt_id': prompt_idx,
                    'mode': mode,
                    'query': query,
                    'complexity': complexity,
                    'response_time': 0,
                    'answer_length': 0,
                    'citations_count': 0,
                    'is_cached': False,
                    'success': False,
                    'status_code': 500,
                    'answer_preview': '',
                    'error': str(e)
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
                
                print(f"      ❌ Error: {e}")
            
            # Progress update
            progress = (test_count / total_tests) * 100
            print(f"      📊 Progress: {test_count}/{total_tests} ({progress:.1f}%)")
    
    # Analysis and reporting
    print(f"\n📊 COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
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
    
    # Performance delta analysis
    print(f"\n📈 PERFORMANCE DELTA ANALYSIS")
    print("-" * 80)
    
    # Compare with baseline (assuming original was ~34s average)
    baseline_avg = 34.0  # seconds
    if successful_results:
        current_avg = statistics.mean([r['response_time'] for r in successful_results])
        improvement = ((baseline_avg - current_avg) / baseline_avg) * 100
        
        print(f"   Baseline average: {baseline_avg:.1f}s")
        print(f"   Current average: {current_avg:.2f}s")
        print(f"   Performance improvement: {improvement:.1f}%")
        
        if improvement > 0:
            print(f"   🚀 System is {improvement:.1f}% faster than baseline!")
        else:
            print(f"   ⚠️  System is {abs(improvement):.1f}% slower than baseline")
    
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
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 80)
    
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
    
    if avg_response_time < 2.0:
        print("✅ Response Time: EXCELLENT")
    elif avg_response_time < 5.0:
        print("✅ Response Time: GOOD")
    else:
        print("⚠️  Response Time: NEEDS IMPROVEMENT")
    
    if cache_hit_rate >= 30:
        print("✅ Caching: EXCELLENT")
    elif cache_hit_rate >= 15:
        print("✅ Caching: GOOD")
    else:
        print("⚠️  Caching: NEEDS IMPROVEMENT")
    
    # Overall grade
    if success_rate >= 95 and avg_response_time < 2.0 and cache_hit_rate >= 30:
        print("\n🎉 OVERALL GRADE: A+ (EXCELLENT)")
        print("   System is performing exceptionally well!")
    elif success_rate >= 90 and avg_response_time < 5.0 and cache_hit_rate >= 15:
        print("\n✅ OVERALL GRADE: A (VERY GOOD)")
        print("   System is performing very well!")
    elif success_rate >= 80 and avg_response_time < 10.0:
        print("\n✅ OVERALL GRADE: B (GOOD)")
        print("   System is performing well with room for improvement!")
    else:
        print("\n⚠️  OVERALL GRADE: C (NEEDS IMPROVEMENT)")
        print("   System needs optimization!")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    results = test_25_comprehensive_final()