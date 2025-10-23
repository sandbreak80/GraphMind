#!/usr/bin/env python3
"""Test Obsidian API connection and RAG integration."""

import requests
import json
import time

def test_obsidian_connection():
    """Test the complete Obsidian integration."""
    
    print("🧪 Testing Obsidian Integration")
    print("=" * 50)
    
    # Test 1: Host API connection
    print("\n1. Testing Obsidian API from host...")
    try:
        response = requests.get("http://127.0.0.1:27124/", timeout=5)
        print(f"   ✅ Host connection: {response.status_code}")
        print(f"   📄 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Host connection failed: {e}")
        return False
    
    # Test 2: Network API connection
    print("\n2. Testing Obsidian API from network...")
    try:
        response = requests.get("http://192.168.50.43:27124/", timeout=5)
        print(f"   ✅ Network connection: {response.status_code}")
        print(f"   📄 Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Network connection failed: {e}")
        print("   💡 Make sure 'Bind to localhost only' is OFF in plugin settings")
        return False
    
    # Test 3: RAG service connection
    print("\n3. Testing RAG service...")
    try:
        response = requests.get("http://localhost:8001/stats", timeout=5)
        if response.status_code == 200:
            print("   ✅ RAG service is running")
        else:
            print(f"   ❌ RAG service error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ RAG service connection failed: {e}")
        return False
    
    # Test 4: Obsidian RAG endpoint
    print("\n4. Testing Obsidian RAG endpoint...")
    try:
        response = requests.post(
            "http://localhost:8001/ask-obsidian",
            json={
                "query": "What trading strategies do I have in my notes?",
                "mode": "qa",
                "top_k": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Obsidian RAG endpoint working")
            print(f"   📊 Total sources: {data.get('total_sources', 0)}")
            print(f"   📝 Answer length: {len(data.get('answer', ''))}")
            print(f"   🔗 Citations: {len(data.get('citations', []))}")
            
            if data.get('total_sources', 0) > 0:
                print("   🎉 Obsidian integration is working!")
                return True
            else:
                print("   ⚠️  No sources found - check if you have trading notes")
                return True
        else:
            print(f"   ❌ RAG endpoint error: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ RAG endpoint failed: {e}")
        return False

def test_obsidian_endpoints():
    """Test specific Obsidian API endpoints."""
    
    print("\n5. Testing specific Obsidian endpoints...")
    
    endpoints = [
        "/",
        "/notes",
        "/search?query=test",
        "/health"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://192.168.50.43:27124{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except:
                    print(f"      Text length: {len(response.text)}")
        except Exception as e:
            print(f"   {endpoint}: Error - {e}")

if __name__ == "__main__":
    success = test_obsidian_connection()
    test_obsidian_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Obsidian integration is working!")
        print("\nYou can now use:")
        print("  curl -X POST http://localhost:8001/ask-obsidian \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{\"query\": \"Your question here\", \"mode\": \"qa\", \"top_k\": 5}'")
    else:
        print("❌ Obsidian integration needs configuration")
        print("\nPlease check:")
        print("  1. Obsidian Local REST API plugin is installed and enabled")
        print("  2. Plugin is configured with 'Bind to localhost only' OFF")
        print("  3. Port 27124 is not blocked by firewall")
        print("  4. RAG service is running")