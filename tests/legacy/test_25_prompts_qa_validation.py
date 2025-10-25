#!/usr/bin/env python3
"""Comprehensive 25-prompt test with Ollama QA validation."""
import requests
import time
import statistics
import json
import random
from datetime import datetime

def test_25_prompts_qa_validation():
    base_url = "http://localhost:8002"
    ollama_url = "http://localhost:11434"
    
    # Get authentication token
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🚀 COMPREHENSIVE 25-PROMPT QA VALIDATION TEST")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Testing: 25 diverse prompts across 4 modes")
    print("🧵 Mode: Single-threaded (GPU-optimized)")
    print("🔍 QA: Ollama validation for response quality")
    print("=" * 80)
    
    # 25 diverse test prompts covering different complexities and use cases
    test_prompts = [
        # Simple queries (6) - should use llama3.2:3b + simple profile
        {
            "query": "What is trading?",
            "expected_complexity": "simple",
            "description": "Basic definition query",
            "validation_criteria": "Should explain trading concept clearly"
        },
        {
            "query": "Explain RSI",
            "expected_complexity": "simple", 
            "description": "Simple technical indicator",
            "validation_criteria": "Should define RSI and its basic purpose"
        },
        {
            "query": "What is momentum?",
            "expected_complexity": "simple",
            "description": "Basic concept query",
            "validation_criteria": "Should explain momentum in trading context"
        },
        {
            "query": "Define support and resistance",
            "expected_complexity": "simple",
            "description": "Basic trading concepts",
            "validation_criteria": "Should define both concepts clearly"
        },
        {
            "query": "What is a candlestick?",
            "expected_complexity": "simple",
            "description": "Basic chart element",
            "validation_criteria": "Should explain candlestick charting"
        },
        {
            "query": "Calculate 2 + 2",
            "expected_complexity": "simple",
            "description": "Basic math test",
            "validation_criteria": "Should return 4"
        },
        
        # Medium queries (8) - should use llama3.1:latest + medium profile
        {
            "query": "Explain RSI indicator and how it works in technical analysis",
            "expected_complexity": "medium",
            "description": "Technical indicator explanation",
            "validation_criteria": "Should explain RSI calculation and usage"
        },
        {
            "query": "What is momentum trading and how does it work?",
            "expected_complexity": "medium",
            "description": "Strategy explanation",
            "validation_criteria": "Should explain momentum trading strategy"
        },
        {
            "query": "Compare MACD and RSI indicators",
            "expected_complexity": "medium",
            "description": "Indicator comparison",
            "validation_criteria": "Should compare both indicators effectively"
        },
        {
            "query": "How do you identify support and resistance levels?",
            "expected_complexity": "medium",
            "description": "Technical analysis method",
            "validation_criteria": "Should explain identification methods"
        },
        {
            "query": "What are the different types of trading orders?",
            "expected_complexity": "medium",
            "description": "Trading mechanics",
            "validation_criteria": "Should list and explain order types"
        },
        {
            "query": "Explain the concept of risk management in trading",
            "expected_complexity": "medium",
            "description": "Risk management basics",
            "validation_criteria": "Should explain risk management principles"
        },
        {
            "query": "What is the difference between fundamental and technical analysis?",
            "expected_complexity": "medium",
            "description": "Analysis type comparison",
            "validation_criteria": "Should clearly distinguish both approaches"
        },
        {
            "query": "How do you calculate position sizing in trading?",
            "expected_complexity": "medium",
            "description": "Position sizing methodology",
            "validation_criteria": "Should explain position sizing calculations"
        },
        
        # Complex queries (7) - should use qwen2.5-coder:14b + complex profile
        {
            "query": "Compare momentum and mean reversion strategies with technical analysis",
            "expected_complexity": "complex",
            "description": "Strategy comparison with analysis",
            "validation_criteria": "Should compare both strategies comprehensively"
        },
        {
            "query": "Analyze the relationship between volume and price movements in trading",
            "expected_complexity": "complex",
            "description": "Volume-price analysis",
            "validation_criteria": "Should explain volume-price relationships"
        },
        {
            "query": "Explain how to build a trading system using multiple indicators",
            "expected_complexity": "complex",
            "description": "Trading system development",
            "validation_criteria": "Should explain system building methodology"
        },
        {
            "query": "What are the advantages and disadvantages of different timeframes in trading?",
            "expected_complexity": "complex",
            "description": "Timeframe analysis",
            "validation_criteria": "Should analyze timeframe trade-offs"
        },
        {
            "query": "How do you backtest a trading strategy effectively?",
            "expected_complexity": "complex",
            "description": "Backtesting methodology",
            "validation_criteria": "Should explain backtesting process"
        },
        {
            "query": "Compare different risk management techniques for day trading",
            "expected_complexity": "complex",
            "description": "Risk management comparison",
            "validation_criteria": "Should compare risk management approaches"
        },
        {
            "query": "Explain the psychology of trading and common behavioral biases",
            "expected_complexity": "complex",
            "description": "Trading psychology",
            "validation_criteria": "Should explain trading psychology and biases"
        },
        
        # Research queries (4) - should use gpt-oss:20b + research profile
        {
            "query": "Provide a comprehensive, detailed, and thorough analysis of current market conditions with extensive research into multiple trading strategies",
            "expected_complexity": "research",
            "description": "Comprehensive market analysis",
            "validation_criteria": "Should provide comprehensive market analysis"
        },
        {
            "query": "Conduct an in-depth study of algorithmic trading systems and their implementation strategies",
            "expected_complexity": "research",
            "description": "Algorithmic trading research",
            "validation_criteria": "Should explain algorithmic trading systems"
        },
        {
            "query": "Analyze the complete evolution of trading strategies from traditional to modern quantitative approaches",
            "expected_complexity": "research",
            "description": "Trading strategy evolution",
            "validation_criteria": "Should trace strategy evolution over time"
        },
        {
            "query": "Provide extensive research on market microstructure and its impact on trading performance",
            "expected_complexity": "research",
            "description": "Market microstructure research",
            "validation_criteria": "Should explain market microstructure concepts"
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
    print("-" * 80)
    
    test_count = 0
    total_tests = len(test_prompts) * len(test_modes)
    
    for prompt_idx, prompt_data in enumerate(test_prompts, 1):
        query = prompt_data["query"]
        expected_complexity = prompt_data["expected_complexity"]
        description = prompt_data["description"]
        validation_criteria = prompt_data["validation_criteria"]
        
        print(f"\n📝 Prompt {prompt_idx}/25: {description}")
        print(f"   Query: {query[:60]}{'...' if len(query) > 60 else ''}")
        print(f"   Expected complexity: {expected_complexity}")
        print(f"   Validation criteria: {validation_criteria}")
        
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
                    answer = data.get('answer', '')
                    citations = data.get('citations', [])
                    
                    print(f"      ✅ Success: {response_time:.2f}s")
                    print(f"      📝 Answer length: {len(answer)} characters")
                    print(f"      📚 Citations: {len(citations)}")
                    
                    # Determine if cached
                    is_cached = response_time < 0.1
                    if is_cached:
                        print(f"      💾 CACHED")
                    
                    # QA Validation with Ollama
                    print(f"      🔍 QA Validation...")
                    qa_result = validate_with_ollama_qa(answer, query, validation_criteria, ollama_url)
                    
                    result = {
                        'prompt_id': prompt_idx,
                        'mode': mode,
                        'query': query,
                        'expected_complexity': expected_complexity,
                        'response_time': response_time,
                        'answer_length': len(answer),
                        'citations_count': len(citations),
                        'is_cached': is_cached,
                        'success': True,
                        'status_code': response.status_code,
                        'qa_validation': qa_result,
                        'answer_preview': answer[:200] + "..." if len(answer) > 200 else answer
                    }
                    
                    print(f"      🎯 QA Score: {qa_result['overall_score']}/10")
                    print(f"      📊 QA Details: {qa_result['summary']}")
                    
                else:
                    print(f"      ❌ Failed: {response.status_code}")
                    print(f"      📝 Error: {response.text[:200]}...")
                    
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
                        'qa_validation': {'overall_score': 0, 'summary': 'Failed request'},
                        'answer_preview': '',
                        'error': response.text[:200]
                    }
                
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
                    'qa_validation': {'overall_score': 0, 'summary': 'Timeout'},
                    'answer_preview': '',
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
                    'qa_validation': {'overall_score': 0, 'summary': 'Exception'},
                    'answer_preview': '',
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
    
    # QA Validation Analysis
    print(f"\n🔍 QA Validation Analysis:")
    if successful_results:
        qa_scores = [r['qa_validation']['overall_score'] for r in successful_results if 'qa_validation' in r]
        if qa_scores:
            print(f"   Average QA score: {statistics.mean(qa_scores):.1f}/10")
            print(f"   Min QA score: {min(qa_scores)}/10")
            print(f"   Max QA score: {max(qa_scores)}/10")
            print(f"   High quality responses (>7/10): {sum(1 for s in qa_scores if s > 7)}/{len(qa_scores)}")
            print(f"   Low quality responses (<4/10): {sum(1 for s in qa_scores if s < 4)}/{len(qa_scores)}")
    
    # Mode analysis
    print(f"\n🔄 Performance by Mode:")
    for mode, mode_data in mode_results.items():
        if mode_data:
            successful_mode = [r for r in mode_data if r['success']]
            if successful_mode:
                mode_times = [r['response_time'] for r in successful_mode]
                cached_count = sum(1 for r in successful_mode if r['is_cached'])
                qa_scores = [r['qa_validation']['overall_score'] for r in successful_mode if 'qa_validation' in r]
                
                print(f"   {mode.upper()}:")
                print(f"      Success rate: {len(successful_mode)}/{len(mode_data)} ({len(successful_mode)/len(mode_data)*100:.1f}%)")
                print(f"      Avg response time: {statistics.mean(mode_times):.2f}s")
                print(f"      Cached responses: {cached_count}/{len(successful_mode)} ({cached_count/len(successful_mode)*100:.1f}%)")
                if qa_scores:
                    print(f"      Avg QA score: {statistics.mean(qa_scores):.1f}/10")
    
    # Complexity analysis
    print(f"\n🎯 Performance by Complexity:")
    for complexity, comp_data in complexity_results.items():
        if comp_data:
            successful_comp = [r for r in comp_data if r['success']]
            if successful_comp:
                comp_times = [r['response_time'] for r in successful_comp]
                cached_count = sum(1 for r in successful_comp if r['is_cached'])
                qa_scores = [r['qa_validation']['overall_score'] for r in successful_comp if 'qa_validation' in r]
                
                print(f"   {complexity.upper()}:")
                print(f"      Success rate: {len(successful_comp)}/{len(comp_data)} ({len(successful_comp)/len(comp_data)*100:.1f}%)")
                print(f"      Avg response time: {statistics.mean(comp_times):.2f}s")
                print(f"      Cached responses: {cached_count}/{len(successful_comp)} ({cached_count/len(successful_comp)*100:.1f}%)")
                if qa_scores:
                    print(f"      Avg QA score: {statistics.mean(qa_scores):.1f}/10")
    
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
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 80)
    
    success_rate = len(successful_results) / len(results) * 100
    avg_response_time = statistics.mean([r['response_time'] for r in successful_results]) if successful_results else 0
    cache_hit_rate = len([r for r in successful_results if r['is_cached']]) / len(successful_results) * 100 if successful_results else 0
    avg_qa_score = statistics.mean([r['qa_validation']['overall_score'] for r in successful_results if 'qa_validation' in r]) if successful_results else 0
    
    print(f"📊 Test Results Summary:")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Average Response Time: {avg_response_time:.2f}s")
    print(f"   Cache Hit Rate: {cache_hit_rate:.1f}%")
    print(f"   Average QA Score: {avg_qa_score:.1f}/10")
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
    
    if avg_qa_score >= 7.0:
        print("✅ Response Quality: EXCELLENT")
    elif avg_qa_score >= 5.0:
        print("✅ Response Quality: GOOD")
    else:
        print("⚠️  Response Quality: NEEDS IMPROVEMENT")
    
    if cache_hit_rate >= 30:
        print("✅ Caching: EXCELLENT")
    elif cache_hit_rate >= 15:
        print("✅ Caching: GOOD")
    else:
        print("⚠️  Caching: NEEDS IMPROVEMENT")
    
    # Overall grade
    if success_rate >= 95 and avg_response_time < 2.0 and avg_qa_score >= 7.0:
        print("\n🎉 OVERALL GRADE: A+ (EXCELLENT)")
        print("   System is performing exceptionally well!")
    elif success_rate >= 90 and avg_response_time < 5.0 and avg_qa_score >= 5.0:
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

def validate_with_ollama_qa(answer, original_query, validation_criteria, ollama_url):
    """Use Ollama to validate response quality."""
    try:
        # Create QA prompt
        qa_prompt = f"""You are a quality assurance validator for AI responses. Please evaluate the following response based on the original query and validation criteria.

Original Query: "{original_query}"
Validation Criteria: "{validation_criteria}"

Response to Evaluate:
"{answer}"

Please provide a score from 1-10 and brief explanation for each of these criteria:
1. Relevance (1-10): Does the response directly address the query?
2. Accuracy (1-10): Is the information factually correct?
3. Completeness (1-10): Does it fully answer the query?
4. Clarity (1-10): Is the response clear and well-structured?
5. Depth (1-10): Does it provide appropriate detail for the query complexity?

Respond in JSON format:
{{
    "relevance_score": X,
    "accuracy_score": X,
    "completeness_score": X,
    "clarity_score": X,
    "depth_score": X,
    "overall_score": X,
    "summary": "Brief explanation of the overall quality"
}}"""

        # Send to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama3.1:latest",
                "prompt": qa_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            qa_text = result.get('response', '')
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', qa_text, re.DOTALL)
                if json_match:
                    qa_data = json.loads(json_match.group())
                    return qa_data
                else:
                    # Fallback: basic scoring
                    return {
                        "relevance_score": 5,
                        "accuracy_score": 5,
                        "completeness_score": 5,
                        "clarity_score": 5,
                        "depth_score": 5,
                        "overall_score": 5,
                        "summary": "Could not parse QA response"
                    }
            except json.JSONDecodeError:
                # Fallback: basic scoring
                return {
                    "relevance_score": 5,
                    "accuracy_score": 5,
                    "completeness_score": 5,
                    "clarity_score": 5,
                    "depth_score": 5,
                    "overall_score": 5,
                    "summary": "QA response parsing failed"
                }
        else:
            return {
                "relevance_score": 0,
                "accuracy_score": 0,
                "completeness_score": 0,
                "clarity_score": 0,
                "depth_score": 0,
                "overall_score": 0,
                "summary": "QA validation failed"
            }
            
    except Exception as e:
        return {
            "relevance_score": 0,
            "accuracy_score": 0,
            "completeness_score": 0,
            "clarity_score": 0,
            "depth_score": 0,
            "overall_score": 0,
            "summary": f"QA error: {str(e)}"
        }

if __name__ == "__main__":
    results = test_25_prompts_qa_validation()