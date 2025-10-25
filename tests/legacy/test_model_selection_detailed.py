#!/usr/bin/env python3
"""Detailed test for model selection logic."""
import requests
import time
import json

def test_model_selection():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧠 Detailed Model Selection Test")
    print("=" * 50)
    
    # Test cases designed to trigger different model selections
    test_cases = [
        {
            "query": "Hi",
            "expected": "simple",
            "description": "Very simple greeting"
        },
        {
            "query": "What is trading?",
            "expected": "simple", 
            "description": "Basic question"
        },
        {
            "query": "Explain RSI indicator",
            "expected": "medium",
            "description": "Technical question"
        },
        {
            "query": "Compare momentum and mean reversion strategies",
            "expected": "complex",
            "description": "Strategy comparison"
        },
        {
            "query": "Analyze the current market conditions and provide comprehensive trading recommendations",
            "expected": "complex",
            "description": "Analysis request"
        },
        {
            "query": "Provide a comprehensive, detailed, and thorough analysis of market conditions with extensive research",
            "expected": "research",
            "description": "Research request"
        },
        {
            "query": "What is momentum trading? What is RSI? What is MACD? What is VWAP? What is Bollinger Bands?",
            "expected": "research",
            "description": "Multiple questions"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Query: {case['query']}")
        print(f"   Expected: {case['expected']}")
        
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
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer length: {len(data.get('answer', ''))}")
                
                # The model selection happens internally, but we can see the response time
                # which gives us hints about which model was used
                if response_time < 0.1:
                    print(f"   🤖 Likely model: Simple (cached or very fast)")
                elif response_time < 0.5:
                    print(f"   🤖 Likely model: Medium/Complex")
                else:
                    print(f"   🤖 Likely model: Research/Complex")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test monitoring to see model usage
    print(f"\n📊 Model Usage Summary:")
    try:
        response = requests.get(f"{base_url}/monitoring/performance")
        if response.status_code == 200:
            metrics = response.json()
            model_usage = metrics.get('model_usage', {})
            print(f"   Model distribution: {model_usage}")
            
            # Analyze model selection patterns
            total_queries = sum(model_usage.values())
            if total_queries > 0:
                print(f"\n   Model Selection Analysis:")
                for model, count in model_usage.items():
                    percentage = (count / total_queries) * 100
                    print(f"   {model}: {count} queries ({percentage:.1f}%)")
        else:
            print(f"   ❌ Failed to get model usage: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting model usage: {e}")

if __name__ == "__main__":
    test_model_selection()