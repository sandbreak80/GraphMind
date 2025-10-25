#!/usr/bin/env python3
"""Test Fixed Endpoints - Obsidian and Document Filtering"""

import requests
import time
import json
import random

def test_fixed_endpoints():
    """Test the endpoints that were failing"""
    base_url = "http://localhost:8002"
    
    # Authenticate
    print("🔐 Authenticating...")
    auth_response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"},
        timeout=10
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return False
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Test Obsidian Integration (was failing with asyncio.run error)
    print("\n🔍 Testing Obsidian Integration...")
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask-obsidian",
                headers=headers,
                json={
                    "query": f"Test query {i+1} about trading strategies",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Obsidian Test {i+1}: PASS ({duration:.2f}s) - Answer: {len(data.get('answer', ''))} chars")
            else:
                print(f"❌ Obsidian Test {i+1}: FAIL ({duration:.2f}s) - HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Obsidian Test {i+1}: ERROR ({duration:.2f}s) - {str(e)}")
    
    # Test Document Filtering (was failing with HTTP 422)
    print("\n🔍 Testing Document Filtering...")
    for i in range(3):
        start_time = time.time()
        try:
            # Create sample documents for filtering
            sample_documents = [
                {
                    "id": f"doc_{j}",
                    "title": f"Sample Document {j}",
                    "text": f"This is a sample document about {random.choice(['trading', 'finance', 'algorithms'])}",
                    "metadata": {
                        "trading_domain": random.choice(["technical_analysis", "portfolio_management", "risk_management"]),
                        "complexity_level": random.choice(["beginner", "intermediate", "expert"])
                    }
                }
                for j in range(3)
            ]
            
            response = requests.post(
                f"{base_url}/filter-documents",
                headers=headers,
                data={
                    "documents": json.dumps(sample_documents),
                    "filters": json.dumps({
                        "trading_domain": random.choice(["technical_analysis", "portfolio_management", "risk_management"]),
                        "complexity_level": random.choice(["beginner", "intermediate", "expert"])
                    })
                },
                timeout=30
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                filtered_count = len(data.get('filtered_documents', []))
                print(f"✅ Document Filtering Test {i+1}: PASS ({duration:.2f}s) - Filtered {filtered_count} documents")
            else:
                print(f"❌ Document Filtering Test {i+1}: FAIL ({duration:.2f}s) - HTTP {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"❌ Document Filtering Test {i+1}: ERROR ({duration:.2f}s) - {str(e)}")
    
    print("\n🎯 Fixed Endpoints Test Complete!")

if __name__ == "__main__":
    test_fixed_endpoints()