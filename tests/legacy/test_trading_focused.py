#!/usr/bin/env python3
"""Focused test on trading-specific queries to validate context awareness."""
import requests
import time
import statistics

def test_trading_focused():
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
    
    print("\n🎯 TRADING-FOCUSED VALIDATION TEST")
    print("=" * 60)
    print("🔍 Testing context awareness and trading knowledge")
    print("=" * 60)
    
    # Trading-specific test queries
    test_queries = [
        {
            "query": "What is RSI in trading?",
            "expected": "Relative Strength Index",
            "description": "Trading RSI context"
        },
        {
            "query": "Explain MACD indicator",
            "expected": "Moving Average Convergence Divergence",
            "description": "Trading indicator"
        },
        {
            "query": "What is support and resistance in trading?",
            "expected": "price levels",
            "description": "Trading concepts"
        },
        {
            "query": "How does momentum trading work?",
            "expected": "momentum strategy",
            "description": "Trading strategy"
        },
        {
            "query": "What is a candlestick chart?",
            "expected": "candlestick",
            "description": "Trading chart type"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        description = test_case["description"]
        
        print(f"\n{i}. {description}: {query}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                
                # Check if answer contains expected content
                contains_expected = expected.lower() in answer.lower()
                
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer: {answer[:150]}...")
                print(f"   🎯 Contains '{expected}': {'✅ YES' if contains_expected else '❌ NO'}")
                
                results.append({
                    'query': query,
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'contains_expected': contains_expected,
                    'success': True
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📝 Error: {response.text[:100]}...")
                
                results.append({
                    'query': query,
                    'response_time': 0,
                    'answer_length': 0,
                    'contains_expected': False,
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'query': query,
                'response_time': 0,
                'answer_length': 0,
                'contains_expected': False,
                'success': False
            })
    
    # Analysis
    print(f"\n📊 ANALYSIS")
    print("=" * 60)
    
    successful_results = [r for r in results if r['success']]
    context_aware_results = [r for r in successful_results if r['contains_expected']]
    
    print(f"📈 Performance:")
    print(f"   Total queries: {len(results)}")
    print(f"   Successful: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
    print(f"   Context aware: {len(context_aware_results)} ({len(context_aware_results)/len(successful_results)*100:.1f}%)")
    
    if successful_results:
        response_times = [r['response_time'] for r in successful_results]
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
    
    # Context awareness assessment
    if len(context_aware_results) >= len(successful_results) * 0.8:
        print(f"\n✅ CONTEXT AWARENESS: EXCELLENT")
        print(f"   System correctly interprets trading context!")
    elif len(context_aware_results) >= len(successful_results) * 0.6:
        print(f"\n✅ CONTEXT AWARENESS: GOOD")
        print(f"   System mostly understands trading context!")
    else:
        print(f"\n⚠️  CONTEXT AWARENESS: NEEDS IMPROVEMENT")
        print(f"   System needs better trading context understanding!")
    
    return results

if __name__ == "__main__":
    results = test_trading_focused()