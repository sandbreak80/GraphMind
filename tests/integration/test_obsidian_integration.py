#!/usr/bin/env python3
"""Test script for Obsidian MCP integration."""

import requests
import json
import time

def test_obsidian_integration():
    """Test the Obsidian MCP integration."""
    
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Obsidian MCP Integration")
    print("=" * 50)
    
    # Test 1: Check if the service is running
    print("\n1. Testing service availability...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Service is running")
            stats = response.json()
            print(f"   Documents in database: {stats.get('total_documents', 0)}")
        else:
            print("❌ Service not responding")
            return False
    except Exception as e:
        print(f"❌ Service not available: {e}")
        return False
    
    # Test 2: Test Obsidian endpoint
    print("\n2. Testing Obsidian endpoint...")
    test_queries = [
        "What trading strategies do I have in my notes?",
        "Show me my recent trading notes",
        "What are my thoughts on ES futures trading?",
        "Find notes about risk management"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {query}")
        try:
            response = requests.post(
                f"{base_url}/ask-obsidian",
                json={
                    "query": query,
                    "mode": "qa",
                    "top_k": 5
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response received")
                print(f"   📊 Total sources: {data.get('total_sources', 0)}")
                print(f"   📝 Answer length: {len(data.get('answer', ''))} characters")
                print(f"   🔗 Citations: {len(data.get('citations', []))}")
                
                # Show first 200 characters of answer
                answer = data.get('answer', '')
                if answer:
                    print(f"   💬 Answer preview: {answer[:200]}...")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    # Test 3: Compare with standard search
    print("\n3. Comparing with standard search...")
    query = "What are the 3 fade setups?"
    
    try:
        # Standard search
        standard_response = requests.post(
            f"{base_url}/ask",
            json={"query": query, "mode": "qa", "top_k": 5},
            timeout=30
        )
        
        # Obsidian search
        obsidian_response = requests.post(
            f"{base_url}/ask-obsidian",
            json={"query": query, "mode": "qa", "top_k": 5},
            timeout=30
        )
        
        if standard_response.status_code == 200 and obsidian_response.status_code == 200:
            standard_data = standard_response.json()
            obsidian_data = obsidian_response.json()
            
            print(f"   📊 Standard sources: {len(standard_data.get('citations', []))}")
            print(f"   📊 Obsidian sources: {obsidian_data.get('total_sources', 0)}")
            print(f"   📝 Standard answer length: {len(standard_data.get('answer', ''))}")
            print(f"   📝 Obsidian answer length: {len(obsidian_data.get('answer', ''))}")
            
            if obsidian_data.get('total_sources', 0) > len(standard_data.get('citations', [])):
                print("   ✅ Obsidian integration is providing additional sources!")
            else:
                print("   ℹ️  Obsidian integration may not be active or no personal notes found")
        
    except Exception as e:
        print(f"   ❌ Comparison test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Obsidian integration test completed!")
    print("\nTo use the integration:")
    print("1. Make sure Obsidian is running with Local REST API plugin")
    print("2. Set OBSIDIAN_VAULT_PATH environment variable")
    print("3. Use /ask-obsidian endpoint for personal knowledge search")

if __name__ == "__main__":
    test_obsidian_integration()