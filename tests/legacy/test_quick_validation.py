#!/usr/bin/env python3
"""Quick validation test to check system functionality."""
import requests
import time

def test_quick_validation():
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
    
    print("\n🧪 Quick Validation Test")
    print("=" * 50)
    
    # Test a few simple queries
    test_queries = [
        "What is 2+2?",
        "What is trading?",
        "Explain RSI briefly"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 100
                },
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer: {answer[:100]}...")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📝 Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ Quick validation completed!")

if __name__ == "__main__":
    test_quick_validation()