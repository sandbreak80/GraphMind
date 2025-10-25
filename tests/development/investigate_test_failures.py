#!/usr/bin/env python3
"""Investigate what caused the original test failures"""

import requests
import time
import json
from datetime import datetime

def investigate_test_failures():
    base_url = "http://localhost:8002"
    
    # Authenticate
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🔍 INVESTIGATING ORIGINAL TEST FAILURES")
    print("=" * 60)
    
    # Let's test the exact same queries that failed, with the exact same parameters
    # but using the original timestamp format from the test
    original_timestamp = 1761281352  # From the original test
    
    failing_cases = [
        {
            "prompt_id": 22,
            "mode": "web",
            "query": f"Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_{original_timestamp}_22)",
            "model": "deepseek-r1:latest"
        },
        {
            "prompt_id": 22,
            "mode": "research", 
            "query": f"Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_{original_timestamp}_22)",
            "model": "deepseek-r1:latest"
        },
        {
            "prompt_id": 23,
            "mode": "research",
            "query": f"Provide an in-depth study of market making strategies in cryptocurrency markets including liquidity provision, risk management, and regulatory considerations (test_{original_timestamp}_23)",
            "model": "deepseek-r1:latest"
        }
    ]
    
    print("🧪 Testing with ORIGINAL query strings from failed test...")
    print("-" * 60)
    
    for i, case in enumerate(failing_cases, 1):
        print(f"\n🔍 Testing Original Failure {i}/3")
        print(f"Mode: {case['mode']}")
        print(f"Query: {case['query'][:80]}...")
        
        # Prepare request data exactly as in the original test
        request_data = {
            "query": case["query"],
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": case["model"]
        }
        
        if case["mode"] == "web":
            request_data["web_enabled"] = True
        elif case["mode"] == "research":
            request_data["research_enabled"] = True
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                cached = data.get('cached', False)
                
                print(f"   📊 Status: HTTP 200")
                print(f"   ⏱️  Time: {response_time:.2f}s")
                print(f"   📄 Answer length: {len(answer)} chars")
                print(f"   💾 Cached: {cached}")
                
                if len(answer) <= 100:
                    print(f"   ❌ STILL FAILING: Answer too short!")
                    print(f"   📝 Answer content: '{answer}'")
                else:
                    print(f"   ✅ NOW SUCCESS: Answer length acceptable")
                    print(f"   📝 Preview: {answer[:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🔍 HYPOTHESIS TESTING")
    print("=" * 60)
    
    # Test hypothesis: Was it a race condition or resource contention?
    print("\n🧪 Testing concurrent requests to simulate test conditions...")
    
    import threading
    import queue
    
    def make_request(request_data, result_queue, thread_id):
        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                result_queue.put({
                    'thread_id': thread_id,
                    'success': True,
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'cached': data.get('cached', False)
                })
            else:
                result_queue.put({
                    'thread_id': thread_id,
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'response_time': response_time
                })
        except Exception as e:
            result_queue.put({
                'thread_id': thread_id,
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time
            })
    
    # Test concurrent deepseek requests
    print("🚀 Sending 5 concurrent deepseek requests...")
    
    result_queue = queue.Queue()
    threads = []
    
    for i in range(5):
        request_data = {
            "query": f"Test concurrent deepseek request {i} - comprehensive analysis of algorithmic trading evolution (test_concurrent_{i})",
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": "deepseek-r1:latest",
            "research_enabled": True
        }
        
        thread = threading.Thread(target=make_request, args=(request_data, result_queue, i))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Collect results
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    print(f"\n📊 Concurrent Test Results ({len(results)} requests):")
    for result in results:
        if result['success']:
            status = "✅" if result['answer_length'] > 100 else "❌"
            print(f"   Thread {result['thread_id']}: {status} {result['answer_length']} chars, {result['response_time']:.2f}s, cached={result['cached']}")
        else:
            print(f"   Thread {result['thread_id']}: ❌ {result['error']}, {result['response_time']:.2f}s")
    
    # Check for any failures
    failures = [r for r in results if not r['success'] or r.get('answer_length', 0) <= 100]
    if failures:
        print(f"\n❌ Found {len(failures)} failures in concurrent test!")
    else:
        print(f"\n✅ All concurrent requests succeeded!")

if __name__ == "__main__":
    investigate_test_failures()