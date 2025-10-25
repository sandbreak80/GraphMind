#!/usr/bin/env python3
"""Test with 25 TRULY NEW prompts that haven't been cached."""
import requests
import time
import statistics
import json
import random
from datetime import datetime

def test_25_truly_new_prompts():
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
    
    print("\n🚀 TRULY NEW 25 PROMPTS - NO CACHING TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Testing: 25 COMPLETELY NEW prompts across 4 modes")
    print("🧵 Mode: Single-threaded (GPU-optimized)")
    print("⏱️  Patience: Will wait for ALL responses to complete")
    print("🆕 Using unique timestamps to avoid caching")
    print("=" * 80)
    
    # 25 TRULY NEW test prompts with unique identifiers
    timestamp = int(time.time())
    test_prompts = [
        # Simple queries (6) - with unique identifiers
        {"query": f"What is a moving average in trading? (test_{timestamp}_1)", "complexity": "simple", "description": "Basic technical indicator"},
        {"query": f"Explain what a stop loss is (test_{timestamp}_2)", "complexity": "simple", "description": "Basic risk management"},
        {"query": f"What is the difference between a bull and bear market? (test_{timestamp}_3)", "complexity": "simple", "description": "Market terminology"},
        {"query": f"Define volatility in financial markets (test_{timestamp}_4)", "complexity": "simple", "description": "Market concept"},
        {"query": f"What is a trading volume? (test_{timestamp}_5)", "complexity": "simple", "description": "Basic trading metric"},
        {"query": f"Explain what a dividend is (test_{timestamp}_6)", "complexity": "simple", "description": "Basic financial concept"},
        
        # Medium queries (8) - with unique identifiers
        {"query": f"How do you calculate the Sharpe ratio for a trading strategy? (test_{timestamp}_7)", "complexity": "medium", "description": "Risk-adjusted return calculation"},
        {"query": f"What is the difference between fundamental and technical analysis in stock trading? (test_{timestamp}_8)", "complexity": "medium", "description": "Analysis methodology comparison"},
        {"query": f"Explain how to use Bollinger Bands for trading decisions (test_{timestamp}_9)", "complexity": "medium", "description": "Technical indicator usage"},
        {"query": f"What are the key components of a trading plan? (test_{timestamp}_10)", "complexity": "medium", "description": "Trading strategy development"},
        {"query": f"How do you calculate position sizing based on risk management? (test_{timestamp}_11)", "complexity": "medium", "description": "Risk management calculation"},
        {"query": f"What is the difference between market orders and limit orders? (test_{timestamp}_12)", "complexity": "medium", "description": "Order type comparison"},
        {"query": f"Explain how to use the MACD indicator for trend analysis (test_{timestamp}_13)", "complexity": "medium", "description": "Technical analysis method"},
        {"query": f"What are the advantages and disadvantages of day trading? (test_{timestamp}_14)", "complexity": "medium", "description": "Trading strategy evaluation"},
        
        # Complex queries (7) - with unique identifiers
        {"query": f"Design a comprehensive backtesting framework for quantitative trading strategies including walk-forward analysis and Monte Carlo simulation (test_{timestamp}_15)", "complexity": "complex", "description": "Advanced backtesting methodology"},
        {"query": f"Explain how to implement a pairs trading strategy using statistical arbitrage and cointegration analysis (test_{timestamp}_16)", "complexity": "complex", "description": "Statistical arbitrage strategy"},
        {"query": f"Analyze the impact of market microstructure on high-frequency trading strategies and execution algorithms (test_{timestamp}_17)", "complexity": "complex", "description": "Market microstructure analysis"},
        {"query": f"How do you build a multi-asset portfolio optimization model using modern portfolio theory and factor models? (test_{timestamp}_18)", "complexity": "complex", "description": "Portfolio optimization"},
        {"query": f"Explain the implementation of machine learning models for algorithmic trading including feature engineering and model validation (test_{timestamp}_19)", "complexity": "complex", "description": "ML for trading"},
        {"query": f"What are the key considerations for building a low-latency trading system with microsecond execution times? (test_{timestamp}_20)", "complexity": "complex", "description": "Low-latency system design"},
        {"query": f"How do you implement risk management for a multi-strategy hedge fund including VaR, stress testing, and scenario analysis? (test_{timestamp}_21)", "complexity": "complex", "description": "Advanced risk management"},
        
        # Research queries (4) - with unique identifiers
        {"query": f"Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_{timestamp}_22)", "complexity": "research", "description": "Historical analysis of algo trading"},
        {"query": f"Provide an in-depth study of market making strategies in cryptocurrency markets including liquidity provision, risk management, and regulatory considerations (test_{timestamp}_23)", "complexity": "research", "description": "Crypto market making research"},
        {"query": f"Analyze the role of artificial intelligence and machine learning in modern quantitative finance including deep learning applications, natural language processing, and alternative data sources (test_{timestamp}_24)", "complexity": "research", "description": "AI in quantitative finance"},
        {"query": f"Examine the impact of ESG (Environmental, Social, Governance) factors on quantitative investment strategies and portfolio construction in institutional asset management (test_{timestamp}_25)", "complexity": "research", "description": "ESG in quantitative investing"}
    ]
    
    # Test ALL modes
    test_modes = ["qa", "spec", "web", "research"]
    
    # Results storage
    results = []
    mode_results = {mode: [] for mode in test_modes}
    complexity_results = {"simple": [], "medium": [], "complex": [], "research": []}
    
    print(f"\n🧪 Testing {len(test_prompts)} TRULY NEW prompts across {len(test_modes)} modes")
    print(f"📊 Total tests: {len(test_prompts) * len(test_modes)}")
    print(f"⏱️  Estimated time: {len(test_prompts) * len(test_modes) * 10} seconds (10s per query)")
    print("-" * 80)
    
    test_count = 0
    total_tests = len(test_prompts) * len(test_modes)
    start_time = time.time()
    
    for prompt_idx, prompt_data in enumerate(test_prompts, 1):
        query = prompt_data["query"]
        complexity = prompt_data["complexity"]
        description = prompt_data["description"]
        
        print(f"\n📝 Prompt {prompt_idx}/25: {description}")
        print(f"   Query: {query[:80]}{'...' if len(query) > 80 else ''}")
        print(f"   Complexity: {complexity}")
        
        for mode_idx, mode in enumerate(test_modes, 1):
            test_count += 1
            print(f"\n   🔄 Mode {mode_idx}/4: {mode.upper()}")
            
            # Prepare request based on mode
            request_data = {
                "query": query,
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            # Add mode-specific parameters
            if mode == "spec":
                request_data["top_k"] = 15
            elif mode == "web":
                request_data["web_enabled"] = True
            elif mode == "research":
                request_data["research_enabled"] = True
            
            print(f"      ⏳ Sending request... (will wait for completion)")
            
            query_start_time = time.time()
            try:
                # Use a longer timeout and wait for completion
                response = requests.post(
                    f"{base_url}/ask",
                    headers=headers,
                    json=request_data,
                    timeout=120  # 2 minute timeout per query
                )
                
                query_end_time = time.time()
                response_time = query_end_time - query_start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '')
                    citations = data.get('citations', [])
                    
                    print(f"      ✅ Success: {response_time:.2f}s")
                    print(f"      📝 Answer: {len(answer)} characters")
                    print(f"      📚 Citations: {len(citations)}")
                    print(f"      📝 Preview: {answer[:150]}...")
                    
                    # Determine if cached
                    is_cached = response_time < 0.5
                    if is_cached:
                        print(f"      💾 CACHED")
                    else:
                        print(f"      🆕 NEW QUERY")
                    
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
                        'answer_preview': answer[:200] + "..." if len(answer) > 200 else answer
                    }
                    
                else:
                    print(f"      ❌ Failed: {response.status_code}")
                    print(f"      📝 Error: {response.text[:200]}...")
                    
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
                        'error': response.text[:200]
                    }
                
                # Store results
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
                
            except requests.exceptions.Timeout:
                query_end_time = time.time()
                response_time = query_end_time - query_start_time
                
                print(f"      ⏰ Timeout after {response_time:.2f}s")
                
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
                    'status_code': 408,
                    'answer_preview': '',
                    'error': 'Timeout'
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
                
            except Exception as e:
                query_end_time = time.time()
                response_time = query_end_time - query_start_time
                
                print(f"      ❌ Error: {e}")
                
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
                    'status_code': 500,
                    'answer_preview': '',
                    'error': str(e)
                }
                results.append(result)
                mode_results[mode].append(result)
                complexity_results[complexity].append(result)
            
            # Progress update
            progress = (test_count / total_tests) * 100
            elapsed_time = time.time() - start_time
            estimated_remaining = (elapsed_time / test_count) * (total_tests - test_count)
            
            print(f"      📊 Progress: {test_count}/{total_tests} ({progress:.1f}%)")
            print(f"      ⏱️  Elapsed: {elapsed_time/60:.1f}m, Est. remaining: {estimated_remaining/60:.1f}m")
    
    # Final analysis
    total_time = time.time() - start_time
    
    print(f"\n📊 COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    print(f"⏰ Total test time: {total_time/60:.1f} minutes")
    
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
    print(f"   Total Time: {total_time/60:.1f} minutes")
    
    # Performance grades
    if success_rate >= 95:
        print("✅ Success Rate: EXCELLENT")
    elif success_rate >= 90:
        print("✅ Success Rate: GOOD")
    else:
        print("⚠️  Success Rate: NEEDS IMPROVEMENT")
    
    if avg_response_time < 5.0:
        print("✅ Response Time: EXCELLENT")
    elif avg_response_time < 15.0:
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
    if success_rate >= 95 and avg_response_time < 5.0 and cache_hit_rate >= 30:
        print("\n🎉 OVERALL GRADE: A+ (EXCELLENT)")
        print("   System is performing exceptionally well!")
    elif success_rate >= 90 and avg_response_time < 15.0 and cache_hit_rate >= 15:
        print("\n✅ OVERALL GRADE: A (VERY GOOD)")
        print("   System is performing very well!")
    elif success_rate >= 80 and avg_response_time < 30.0:
        print("\n✅ OVERALL GRADE: B (GOOD)")
        print("   System is performing well with room for improvement!")
    else:
        print("\n⚠️  OVERALL GRADE: C (NEEDS IMPROVEMENT)")
        print("   System needs optimization!")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    results = test_25_truly_new_prompts()