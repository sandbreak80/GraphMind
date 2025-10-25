#!/usr/bin/env python3
"""Test regular retrieval to see if documents exist"""

import requests
import time
import json
from datetime import datetime

def test_regular_retrieval():
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
    
    print("\n🔍 TESTING REGULAR RETRIEVAL")
    print("=" * 60)
    
    # Test a simple query
    query = "moving average"
    print(f"🔍 Testing query: '{query}'")
    
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
        
        print(f"📊 Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            citations = data.get('citations', [])
            
            print(f"📄 Answer length: {len(answer)}")
            print(f"📚 Citations: {len(citations)}")
            print(f"📝 Answer preview: {answer[:200]}...")
            
            if citations:
                print(f"📚 Citation details:")
                for i, citation in enumerate(citations[:3], 1):
                    print(f"   {i}. {citation.get('title', 'No title')} (score: {citation.get('score', 0):.3f})")
        else:
            print(f"❌ Error: {response.text}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_regular_retrieval()