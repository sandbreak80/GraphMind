#!/usr/bin/env python3
"""Debug advanced retrieval system"""

import requests
import time
import json
from datetime import datetime

def debug_advanced_retrieval():
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
    
    print("\n🔍 DEBUGGING ADVANCED RETRIEVAL")
    print("=" * 60)
    
    # Test a simple query
    query = "moving average"
    print(f"🔍 Testing query: '{query}'")
    
    try:
        response = requests.post(
            f"{base_url}/advanced-search",
            headers=headers,
            data={"query": query, "top_k": 5},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Also test regular search to compare
    print(f"\n🔍 Testing regular search for comparison...")
    
    try:
        response = requests.post(
            f"{base_url}/ask",
            headers=headers,
            json={
                "query": query,
                "mode": "qa",
                "model": "llama3.1:latest",
                "disable_model_override": True
            },
            timeout=30
        )
        
        print(f"📊 Regular search status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Regular search answer length: {len(data.get('answer', ''))}")
            print(f"📚 Regular search citations: {len(data.get('citations', []))}")
        
    except Exception as e:
        print(f"❌ Regular search exception: {e}")

if __name__ == "__main__":
    debug_advanced_retrieval()