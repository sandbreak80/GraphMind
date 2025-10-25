#!/usr/bin/env python3
"""Deep validation test to verify if results are actually valid or if there's an issue."""
import requests
import time
import json
import re

def test_validation_deep_dive():
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
    
    print("\n🔍 DEEP VALIDATION TEST - PROVING RESULT VALIDITY")
    print("=" * 70)
    print("🎯 Goal: Verify if 99% improvement is real or if results are invalid")
    print("=" * 70)
    
    # Test cases designed to expose potential issues
    test_cases = [
        {
            "query": "What is trading?",
            "expected_behavior": "Should return a real answer about trading",
            "test_type": "basic_validation"
        },
        {
            "query": "Explain RSI indicator in detail",
            "expected_behavior": "Should return detailed technical analysis content",
            "test_type": "content_validation"
        },
        {
            "query": "What is the capital of France?",
            "expected_behavior": "Should return Paris (tests if system is working)",
            "test_type": "knowledge_validation"
        },
        {
            "query": "Calculate 2 + 2",
            "expected_behavior": "Should return 4",
            "test_type": "math_validation"
        },
        {
            "query": "What is momentum trading and how does it work?",
            "expected_behavior": "Should return comprehensive trading strategy explanation",
            "test_type": "complex_validation"
        }
    ]
    
    print("\n🧪 Testing 5 validation cases...")
    print("-" * 50)
    
    validation_results = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['test_type'].upper()}: {case['query']}")
        print(f"   Expected: {case['expected_behavior']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": case["query"],
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                citations = data.get('citations', [])
                
                print(f"   ✅ Status: Success ({response_time:.2f}s)")
                print(f"   📝 Answer length: {len(answer)} characters")
                print(f"   📚 Citations: {len(citations)}")
                
                # Analyze answer quality
                answer_analysis = analyze_answer_quality(answer, case['query'], case['test_type'])
                
                result = {
                    'test_type': case['test_type'],
                    'query': case['query'],
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'citations_count': len(citations),
                    'answer_preview': answer[:200] + "..." if len(answer) > 200 else answer,
                    'quality_analysis': answer_analysis,
                    'success': True
                }
                
                print(f"   🔍 Quality Analysis:")
                for key, value in answer_analysis.items():
                    print(f"      {key}: {value}")
                
            else:
                print(f"   ❌ Status: Failed ({response.status_code})")
                print(f"   📝 Error: {response.text[:200]}...")
                
                result = {
                    'test_type': case['test_type'],
                    'query': case['query'],
                    'response_time': response_time,
                    'answer_length': 0,
                    'citations_count': 0,
                    'answer_preview': '',
                    'quality_analysis': {'error': response.text[:200]},
                    'success': False
                }
                
        except Exception as e:
            print(f"   ❌ Status: Exception - {e}")
            result = {
                'test_type': case['test_type'],
                'query': case['query'],
                'response_time': 0,
                'answer_length': 0,
                'citations_count': 0,
                'answer_preview': '',
                'quality_analysis': {'error': str(e)},
                'success': False
            }
        
        validation_results.append(result)
    
    # Analyze results for validity issues
    print(f"\n🔍 VALIDITY ANALYSIS")
    print("=" * 70)
    
    successful_tests = [r for r in validation_results if r['success']]
    failed_tests = [r for r in validation_results if not r['success']]
    
    print(f"📊 Basic Statistics:")
    print(f"   Successful tests: {len(successful_tests)}/{len(validation_results)}")
    print(f"   Failed tests: {len(failed_tests)}/{len(validation_results)}")
    
    if successful_tests:
        response_times = [r['response_time'] for r in successful_tests]
        print(f"   Average response time: {sum(response_times)/len(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
    
    # Check for suspicious patterns
    print(f"\n🚨 SUSPICIOUS PATTERN DETECTION:")
    
    # Check 1: Are all answers the same length?
    if successful_tests:
        answer_lengths = [r['answer_length'] for r in successful_tests]
        unique_lengths = set(answer_lengths)
        if len(unique_lengths) == 1:
            print("   ⚠️  WARNING: All answers have identical length - possible template response!")
        else:
            print("   ✅ Answer lengths vary - looks normal")
    
    # Check 2: Are response times suspiciously fast?
    if successful_tests:
        fast_responses = [r for r in successful_tests if r['response_time'] < 0.1]
        if len(fast_responses) == len(successful_tests):
            print("   ⚠️  WARNING: All responses < 0.1s - possible caching issue or template!")
        else:
            print("   ✅ Response times vary - looks normal")
    
    # Check 3: Are answers actually relevant?
    print(f"\n📝 CONTENT VALIDATION:")
    for result in successful_tests:
        print(f"\n   {result['test_type']}: {result['query']}")
        print(f"   Answer preview: {result['answer_preview']}")
        print(f"   Quality indicators:")
        for key, value in result['quality_analysis'].items():
            print(f"      {key}: {value}")
    
    # Check 4: Test with a completely new query to see if it's cached
    print(f"\n🔄 CACHE VALIDATION TEST:")
    print("   Testing with completely new query to check caching behavior...")
    
    new_query = "What is the weather like on Mars?"
    print(f"   New query: {new_query}")
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/ask",
            headers=headers,
            json={
                "query": new_query,
                "temperature": 0.1,
                "max_tokens": 1000
            },
            timeout=60
        )
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            print(f"   ✅ New query response: {response_time:.2f}s")
            print(f"   📝 Answer length: {len(answer)} characters")
            print(f"   📝 Answer preview: {answer[:200]}...")
            
            if response_time < 0.1:
                print("   ⚠️  WARNING: New query responded in < 0.1s - possible template response!")
            else:
                print("   ✅ New query took reasonable time - looks normal")
        else:
            print(f"   ❌ New query failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ New query exception: {e}")
    
    # Check 5: Test with a query that should definitely not be cached
    print(f"\n🔄 FRESH QUERY TEST:")
    import random
    random_query = f"What is the meaning of life? Random number: {random.randint(1000, 9999)}"
    print(f"   Random query: {random_query}")
    
    start_time = time.time()
    try:
        response = requests.post(
            f"{base_url}/ask",
            headers=headers,
            json={
                "query": random_query,
                "temperature": 0.1,
                "max_tokens": 1000
            },
            timeout=60
        )
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            print(f"   ✅ Random query response: {response_time:.2f}s")
            print(f"   📝 Answer length: {len(answer)} characters")
            print(f"   📝 Answer preview: {answer[:200]}...")
            
            if response_time < 0.1:
                print("   🚨 CRITICAL: Random query responded in < 0.1s - SYSTEM IS BROKEN!")
                print("   This suggests template responses or broken caching!")
            else:
                print("   ✅ Random query took reasonable time - system working normally")
        else:
            print(f"   ❌ Random query failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Random query exception: {e}")
    
    # Final verdict
    print(f"\n🎯 FINAL VERDICT")
    print("=" * 70)
    
    # Analyze all evidence
    evidence = {
        'all_same_length': len(set([r['answer_length'] for r in successful_tests])) == 1 if successful_tests else False,
        'all_very_fast': all(r['response_time'] < 0.1 for r in successful_tests) if successful_tests else False,
        'new_query_fast': False,  # Will be updated
        'random_query_fast': False,  # Will be updated
        'answers_relevant': True  # Will be analyzed
    }
    
    # Check if answers are actually relevant
    if successful_tests:
        relevant_count = 0
        for result in successful_tests:
            if result['quality_analysis'].get('relevance_score', 0) > 0.5:
                relevant_count += 1
        evidence['answers_relevant'] = relevant_count >= len(successful_tests) * 0.8
    
    print(f"🔍 Evidence Analysis:")
    print(f"   All answers same length: {'❌ YES (SUSPICIOUS)' if evidence['all_same_length'] else '✅ NO (NORMAL)'}")
    print(f"   All responses very fast: {'❌ YES (SUSPICIOUS)' if evidence['all_very_fast'] else '✅ NO (NORMAL)'}")
    print(f"   Answers seem relevant: {'✅ YES (NORMAL)' if evidence['answers_relevant'] else '❌ NO (SUSPICIOUS)'}")
    
    # Determine if 99% improvement is real or fake
    suspicious_indicators = sum([
        evidence['all_same_length'],
        evidence['all_very_fast'],
        not evidence['answers_relevant']
    ])
    
    if suspicious_indicators >= 2:
        print(f"\n🚨 VERDICT: 99% IMPROVEMENT IS LIKELY FAKE!")
        print(f"   Multiple suspicious indicators detected.")
        print(f"   System may be returning template responses or broken.")
        print(f"   Need to investigate further!")
    elif suspicious_indicators == 1:
        print(f"\n⚠️  VERDICT: 99% IMPROVEMENT IS SUSPICIOUS!")
        print(f"   Some suspicious indicators detected.")
        print(f"   Results may be partially invalid.")
        print(f"   Recommend further investigation!")
    else:
        print(f"\n✅ VERDICT: 99% IMPROVEMENT APPEARS REAL!")
        print(f"   No major suspicious indicators detected.")
        print(f"   Results appear to be valid.")
        print(f"   System is working as expected!")
    
    return validation_results

def analyze_answer_quality(answer, query, test_type):
    """Analyze the quality and relevance of an answer."""
    analysis = {}
    
    # Basic metrics
    analysis['length'] = len(answer)
    analysis['word_count'] = len(answer.split())
    
    # Check for common error patterns
    error_patterns = [
        r'sorry.*error',
        r'encountered.*error',
        r'please.*try.*again',
        r'not.*available',
        r'template.*response'
    ]
    
    has_errors = any(re.search(pattern, answer.lower()) for pattern in error_patterns)
    analysis['has_error_patterns'] = has_errors
    
    # Check for relevance based on test type
    relevance_score = 0
    
    if test_type == 'basic_validation':
        if any(word in answer.lower() for word in ['trading', 'buy', 'sell', 'market', 'investment']):
            relevance_score += 0.5
        if len(answer) > 50:
            relevance_score += 0.3
        if len(answer) > 200:
            relevance_score += 0.2
    
    elif test_type == 'content_validation':
        if any(word in answer.lower() for word in ['rsi', 'relative', 'strength', 'indicator', 'technical']):
            relevance_score += 0.5
        if len(answer) > 100:
            relevance_score += 0.3
        if len(answer) > 300:
            relevance_score += 0.2
    
    elif test_type == 'knowledge_validation':
        if 'paris' in answer.lower() or 'france' in answer.lower():
            relevance_score += 0.8
        if len(answer) > 20:
            relevance_score += 0.2
    
    elif test_type == 'math_validation':
        if '4' in answer or 'four' in answer.lower():
            relevance_score += 0.8
        if len(answer) > 10:
            relevance_score += 0.2
    
    elif test_type == 'complex_validation':
        if any(word in answer.lower() for word in ['momentum', 'strategy', 'trading', 'trend']):
            relevance_score += 0.4
        if len(answer) > 200:
            relevance_score += 0.3
        if len(answer) > 400:
            relevance_score += 0.3
    
    analysis['relevance_score'] = min(relevance_score, 1.0)
    
    # Check if answer seems like a template
    template_indicators = [
        len(answer) == 317,  # Suspiciously specific length
        answer.count(' ') < 10,  # Very few spaces
        answer.isupper(),  # All caps
        answer.islower() and len(answer) < 50  # All lowercase and short
    ]
    
    analysis['template_like'] = any(template_indicators)
    
    return analysis

if __name__ == "__main__":
    results = test_validation_deep_dive()