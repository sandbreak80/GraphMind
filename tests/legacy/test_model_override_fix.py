#!/usr/bin/env python3
"""Test that model override fix works correctly"""

import requests
import time
import json

def test_model_override_fix():
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
    
    print("\n🧪 TESTING MODEL OVERRIDE FIX")
    print("=" * 50)
    
    # Test 1: Without disable_model_override (should still override)
    print("\n📝 Test 1: Without disable_model_override")
    request_data = {
        "query": "Conduct a comprehensive analysis of algorithmic trading evolution (test_override_1)",
        "temperature": 0.1,
        "max_tokens": 1000,
        "model": "deepseek-r1:latest"
    }
    
    response = requests.post(f"{base_url}/ask", headers=headers, json=request_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response received: {len(data.get('answer', ''))} chars")
        print(f"   📊 Check logs for model override message")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    # Test 2: With disable_model_override=True (should use requested model)
    print("\n📝 Test 2: With disable_model_override=True")
    request_data = {
        "query": "Conduct a comprehensive analysis of algorithmic trading evolution (test_override_2)",
        "temperature": 0.1,
        "max_tokens": 1000,
        "model": "deepseek-r1:latest",
        "disable_model_override": True
    }
    
    response = requests.post(f"{base_url}/ask", headers=headers, json=request_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Response received: {len(data.get('answer', ''))} chars")
        print(f"   📊 Should use deepseek-r1:latest directly")
    else:
        print(f"   ❌ Error: {response.status_code}")
    
    print("\n🔍 Check the API logs to verify model selection behavior:")
    print("   docker logs emini-rag-dev --tail 20")

if __name__ == "__main__":
    test_model_override_fix()