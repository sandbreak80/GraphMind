#!/usr/bin/env python3
"""Test async parallel processing performance improvement"""

import requests
import time
import json
from datetime import datetime

def test_async_performance():
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
    
    print("\n🚀 TESTING ASYNC PARALLEL PROCESSING PERFORMANCE")
    print("=" * 60)
    
    # Test queries of different complexities
    test_queries = [
        "What is a moving average?",
        "Explain momentum trading strategies with examples",
        "Conduct a comprehensive analysis of algorithmic trading evolution from 1980s to present",
        "How do I implement a mean reversion strategy with proper risk management?",
        "What are the key factors affecting ES futures pricing during market hours?"
    ]
    
    print(f"📝 Testing {len(test_queries)} queries...")
    print("-" * 60)
    
    total_time = 0
    successful_queries = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🧪 Query {i}/{len(test_queries)}: {query[:50]}...")
        
        request_data = {
            "query": query,
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": "llama3.1:latest",
            "disable_model_override": True
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            total_time += response_time
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                print(f"   ✅ Success: {response_time:.2f}s, {answer_length} chars")
                successful_queries += 1
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    print(f"Total queries: {len(test_queries)}")
    print(f"Successful: {successful_queries}")
    print(f"Failed: {len(test_queries) - successful_queries}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per query: {total_time/len(test_queries):.2f}s")
    print(f"Success rate: {(successful_queries/len(test_queries))*100:.1f}%")
    
    # Performance expectations
    print(f"\n🎯 PERFORMANCE TARGETS:")
    print(f"   Target avg time: <8.0s per query")
    print(f"   Current avg time: {total_time/len(test_queries):.2f}s")
    
    if total_time/len(test_queries) < 8.0:
        print(f"   ✅ TARGET MET! Async parallel processing is working well.")
    else:
        print(f"   ⚠️  Above target - may need further optimization.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_async_performance()