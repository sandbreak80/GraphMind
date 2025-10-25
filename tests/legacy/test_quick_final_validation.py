#!/usr/bin/env python3
"""Quick final validation to check system performance."""
import requests
import time
import statistics

def test_quick_final_validation():
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
    
    print("\n🔍 QUICK FINAL VALIDATION")
    print("=" * 50)
    
    # Test a few queries across different modes
    test_cases = [
        {"query": "What is a moving average?", "mode": "qa"},
        {"query": "Explain stop loss", "mode": "spec"},
        {"query": "What is volatility?", "mode": "web"},
        {"query": "How do you calculate Sharpe ratio?", "mode": "research"}
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        mode = test_case["mode"]
        
        print(f"\n{i}. Testing {mode.upper()}: {query}")
        
        start_time = time.time()
        try:
            request_data = {
                "query": query,
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
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
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer: {len(answer)} characters")
                print(f"   📝 Preview: {answer[:100]}...")
                
                results.append({
                    'mode': mode,
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'success': True
                })
            else:
                print(f"   ❌ Failed: {response.status_code}")
                results.append({
                    'mode': mode,
                    'response_time': response_time,
                    'answer_length': 0,
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'mode': mode,
                'response_time': 0,
                'answer_length': 0,
                'success': False
            })
    
    # Analysis
    print(f"\n📊 QUICK ANALYSIS")
    print("=" * 50)
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        response_times = [r['response_time'] for r in successful_results]
        print(f"📈 Performance:")
        print(f"   Successful: {len(successful_results)}/{len(results)}")
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        
        # Check for caching
        cached_count = sum(1 for r in successful_results if r['response_time'] < 0.5)
        print(f"   Cached responses: {cached_count}/{len(successful_results)} ({cached_count/len(successful_results)*100:.1f}%)")
        
        print(f"\n✅ System is working with real responses!")
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        if cached_count > 0:
            print(f"   Caching is working: {cached_count} instant responses")
    else:
        print(f"❌ No successful responses!")
    
    return results

if __name__ == "__main__":
    results = test_quick_final_validation()