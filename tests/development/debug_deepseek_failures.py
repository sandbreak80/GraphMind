#!/usr/bin/env python3
"""Debug script to investigate deepseek-r1:latest failures in detail"""

import requests
import time
import json
from datetime import datetime

def debug_deepseek_failures():
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
    
    print("\n🔍 DEBUGGING DEEPSEEK-R1 FAILURES")
    print("=" * 60)
    
    # The 3 failing cases from the test results:
    failing_cases = [
        {
            "prompt_id": 22,
            "mode": "web", 
            "query": "Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_debug_22_web)",
            "model": "deepseek-r1:latest"
        },
        {
            "prompt_id": 22,
            "mode": "research",
            "query": "Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_debug_22_research)",
            "model": "deepseek-r1:latest"
        },
        {
            "prompt_id": 23,
            "mode": "research",
            "query": "Provide an in-depth study of market making strategies in cryptocurrency markets including liquidity provision, risk management, and regulatory considerations (test_debug_23_research)",
            "model": "deepseek-r1:latest"
        }
    ]
    
    for i, case in enumerate(failing_cases, 1):
        print(f"\n🧪 DEBUGGING FAILURE {i}/3")
        print(f"Prompt ID: {case['prompt_id']}")
        print(f"Mode: {case['mode']}")
        print(f"Model: {case['model']}")
        print(f"Query: {case['query'][:100]}...")
        print("-" * 60)
        
        # Prepare request data
        request_data = {
            "query": case["query"],
            "temperature": 0.1,
            "max_tokens": 1000,
            "model": case["model"]
        }
        
        # Add mode-specific parameters
        if case["mode"] == "spec":
            request_data["top_k"] = 10
        elif case["mode"] == "web":
            request_data["web_enabled"] = True
        elif case["mode"] == "research":
            request_data["research_enabled"] = True
        
        print(f"📤 Request data: {json.dumps(request_data, indent=2)}")
        
        # Make the request with detailed logging
        start_time = time.time()
        
        try:
            print(f"⏳ Sending request... (timeout: 60s)")
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            response_time = time.time() - start_time
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📝 Response keys: {list(data.keys())}")
                
                answer = data.get('answer', '')
                citations = data.get('citations', [])
                cached = data.get('cached', False)
                
                print(f"📄 Answer length: {len(answer)} characters")
                print(f"📚 Citations count: {len(citations)}")
                print(f"💾 Cached: {cached}")
                
                if answer:
                    print(f"📝 Answer preview (first 200 chars):")
                    print(f"   {answer[:200]}...")
                    
                    if len(answer) <= 100:
                        print("❌ FAILURE: Answer too short!")
                    else:
                        print("✅ SUCCESS: Answer length acceptable")
                else:
                    print("❌ FAILURE: Empty answer!")
                
                # Check for any error messages in the response
                if 'error' in data:
                    print(f"❌ Error in response: {data['error']}")
                if 'message' in data:
                    print(f"📢 Message: {data['message']}")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response text: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: Request timed out after 60 seconds")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
        
        print("\n" + "=" * 60)
    
    print("\n🔍 ADDITIONAL DEBUGGING: Testing same queries with different models")
    print("=" * 60)
    
    # Test the same failing queries with other models to see if it's model-specific
    test_queries = [
        "Conduct a comprehensive analysis of the evolution of algorithmic trading from the 1980s to present day, including regulatory changes, technological advances, and market impact (test_comparison_22)",
        "Provide an in-depth study of market making strategies in cryptocurrency markets including liquidity provision, risk management, and regulatory considerations (test_comparison_23)"
    ]
    
    models_to_test = ["llama3.1:latest", "qwen2.5-coder:14b", "deepseek-r1:latest"]
    
    for query in test_queries:
        print(f"\n🧪 Testing query: {query[:80]}...")
        print("-" * 40)
        
        for model in models_to_test:
            print(f"\n🤖 Testing with {model}:")
            
            request_data = {
                "query": query,
                "temperature": 0.1,
                "max_tokens": 1000,
                "model": model,
                "research_enabled": True
            }
            
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
                    print(f"   ✅ Success: {len(answer)} chars, {response_time:.2f}s")
                    if len(answer) <= 100:
                        print(f"   ⚠️  Short answer: {answer[:100]}")
                else:
                    print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_deepseek_failures()