#!/usr/bin/env python3
"""Focused test with 20 unique prompts and token refresh"""

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

def get_auth_token():
    """Get fresh auth token"""
    try:
        response = requests.post(
            "http://localhost:8002/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Auth failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def test_api():
    print("🚀 TESTING 20 UNIQUE PROMPTS - FOCUSED TEST")
    print("=" * 60)
    
    # Test each prompt with different endpoints and models
    test_id = 1
    passed = 0
    failed = 0
    
    # Test configurations: (endpoint, model, mode)
    test_configs = [
        ("/ask", "llama3.1:latest", "qa"),
        ("/ask", "llama3.1:8b", "qa"),
        ("/ask", "deepseek-r1:latest", "qa"),
        ("/ask-enhanced", "llama3.1:latest", "qa"),
        ("/ask-enhanced", "llama3.1:8b", "qa"),
        ("/ask-enhanced", "deepseek-r1:latest", "qa"),
        ("/ask-research", "llama3.1:latest", "qa"),
        ("/ask-research", "llama3.1:8b", "qa"),
        ("/ask-research", "deepseek-r1:latest", "qa"),
        ("/ask-obsidian", "llama3.1:latest", "qa"),
        ("/ask-obsidian", "llama3.1:8b", "qa"),
        ("/ask-obsidian", "deepseek-r1:latest", "qa"),
        ("/ask", "llama3.1:latest", "spec"),
        ("/ask", "llama3.1:8b", "spec"),
        ("/ask", "deepseek-r1:latest", "spec"),
        ("/ask-enhanced", "llama3.1:latest", "spec"),
        ("/ask-enhanced", "llama3.1:8b", "spec"),
        ("/ask-enhanced", "deepseek-r1:latest", "spec"),
        ("/ask-research", "llama3.1:latest", "spec"),
        ("/ask-research", "llama3.1:8b", "spec")
    ]
    
    print(f"Testing {len(prompts)} prompts × {len(test_configs)} configs = {len(prompts) * len(test_configs)} tests")
    print("\nTest | Prompt                    | Endpoint        | Model           | Mode | Duration | Status")
    print("-" * 90)
    
    for prompt in prompts:
        for endpoint, model, mode in test_configs:
            # Get fresh token for each test to avoid expiration
            token = get_auth_token()
            if not token:
                print(f"{test_id:4d} | {prompt[:25]:25s} | {endpoint:15s} | {model:15s} | {mode:4s} |    0.00s | ❌ AUTH FAIL")
                failed += 1
                test_id += 1
                continue
            
            headers = {"Authorization": f"Bearer {token}"}
            start_time = time.time()
            
            try:
                data = {
                    "query": prompt,
                    "mode": mode,
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
                    print(f"{test_id:4d} | {prompt[:25]:25s} | {endpoint:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | ✅ PASS ({answer_len} chars, {citations} cites)")
                    passed += 1
                else:
                    print(f"{test_id:4d} | {prompt[:25]:25s} | {endpoint:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | ❌ FAIL (HTTP {response.status_code})")
                    failed += 1
                    
            except requests.exceptions.Timeout:
                duration = time.time() - start_time
                print(f"{test_id:4d} | {prompt[:25]:25s} | {endpoint:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | ⏰ TIMEOUT")
                failed += 1
            except Exception as e:
                duration = time.time() - start_time
                print(f"{test_id:4d} | {prompt[:25]:25s} | {endpoint:15s} | {model:15s} | {mode:4s} | {duration:6.2f}s | 💥 ERROR: {e}")
                failed += 1
            
            test_id += 1
            time.sleep(0.5)  # Small delay
    
    # Results
    total = passed + failed
    print(f"\n" + "=" * 90)
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