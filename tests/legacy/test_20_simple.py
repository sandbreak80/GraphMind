#!/usr/bin/env python3
"""Simple test with 20 unique prompts"""

import requests
import time
import json

# 20 unique prompts with varying complexity
prompts = [
    "What is a moving average?",
    "Explain RSI indicator in trading",
    "How to implement stop loss strategy?",
    "Define portfolio diversification",
    "What causes market volatility?",
    "How to build a momentum trading system?",
    "Explain risk management in algorithmic trading",
    "What are trend following strategies?",
    "How to calculate position sizing?",
    "Explain multi-timeframe analysis",
    "Design a quantitative trading system with machine learning",
    "Explain options pricing models for volatility trading",
    "Analyze market microstructure impact on HFT algorithms",
    "Develop multi-asset portfolio optimization strategy",
    "Create systematic approach to regime detection",
    "Implement sophisticated market-making algorithm",
    "Design comprehensive risk management for hedge fund",
    "Develop sentiment analysis framework for trading",
    "Create systematic factor investing approach",
    "Build complete algorithmic trading infrastructure"
]

models = ["llama3.1:latest", "llama3.1:8b", "deepseek-r1:latest"]
endpoints = ["/ask", "/ask-enhanced", "/ask-research", "/ask-obsidian"]

def test_api():
    print("🚀 TESTING 20 UNIQUE PROMPTS")
    print("=" * 60)
    
    # Get auth token
    try:
        auth_response = requests.post(
            "http://localhost:8002/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=10
        )
        if auth_response.status_code != 200:
            print(f"❌ Auth failed: {auth_response.status_code}")
            return False
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return False
    
    # Test each prompt with each endpoint and model
    test_id = 1
    passed = 0
    failed = 0
    
    print(f"\nTesting {len(prompts)} prompts × {len(endpoints)} endpoints × {len(models)} models = {len(prompts) * len(endpoints) * len(models)} tests")
    print("\nTest | Endpoint        | Model           | Duration | Status")
    print("-" * 60)
    
    for prompt in prompts:
        for endpoint in endpoints:
            for model in models:
                start_time = time.time()
                try:
                    data = {
                        "query": prompt,
                        "mode": "qa",
                        "model": model,
                        "disable_model_override": True
                    }
                    
                    if "enhanced" in endpoint or "research" in endpoint:
                        data["top_k"] = 5
                    
                    response = requests.post(
                        f"http://localhost:8002{endpoint}",
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                    
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer_len = len(result.get('answer', ''))
                        citations = len(result.get('citations', []))
                        print(f"{test_id:4d} | {endpoint:15s} | {model:15s} | {duration:6.2f}s | ✅ PASS ({answer_len} chars, {citations} cites)")
                        passed += 1
                    else:
                        print(f"{test_id:4d} | {endpoint:15s} | {model:15s} | {duration:6.2f}s | ❌ FAIL (HTTP {response.status_code})")
                        failed += 1
                        
                except requests.exceptions.Timeout:
                    duration = time.time() - start_time
                    print(f"{test_id:4d} | {endpoint:15s} | {model:15s} | {duration:6.2f}s | ⏰ TIMEOUT")
                    failed += 1
                except Exception as e:
                    duration = time.time() - start_time
                    print(f"{test_id:4d} | {endpoint:15s} | {model:15s} | {duration:6.2f}s | 💥 ERROR: {e}")
                    failed += 1
                
                test_id += 1
                time.sleep(0.5)  # Small delay
    
    # Results
    total = passed + failed
    print(f"\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! BUILD SUCCESS ✅")
        return True
    else:
        print(f"❌ {failed} TESTS FAILED! BUILD FAILS ❌")
        return False

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)