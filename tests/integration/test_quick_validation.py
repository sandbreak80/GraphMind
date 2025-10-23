#!/usr/bin/env python3
"""
Quick Validation Test for EminiPlayer Data Source Fixes
======================================================

This script quickly validates that each chat mode uses only its intended data sources.
"""

import requests
import json
import sys

def test_data_sources():
    """Test that each mode uses only its intended data sources."""
    base_url = "http://localhost:3001"
    
    # Test query
    test_query = "What is trading?"
    test_data = {
        "request": {
            "query": test_query,
            "mode": "qa",
            "top_k": 5,
            "temperature": 0.1,
            "max_tokens": 1000,
            "conversation_history": []
        }
    }
    
    # Get auth token
    print("🔐 Authenticating...")
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        if login_response.status_code != 200:
            print(f"❌ Authentication failed: {login_response.status_code} - {login_response.text}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test each mode
    tests = [
        {
            "name": "RAG Only",
            "endpoint": "/api/ask",
            "expected_sources": ["pdf", "video_transcript", "llm_processed"],
            "forbidden_sources": ["Web Source", "Obsidian Note"]
        },
        {
            "name": "Web Search Only",
            "endpoint": "/api/ask-enhanced", 
            "expected_sources": ["Web Source"],
            "forbidden_sources": ["pdf", "video_transcript", "llm_processed", "Obsidian Note"]
        },
        {
            "name": "Obsidian Only",
            "endpoint": "/api/ask-obsidian",
            "expected_sources": ["Trading Strategy Framework", "trading strategy in your BattleCard"],
            "forbidden_sources": ["pdf", "video_transcript", "llm_processed", "Web Source"]
        },
        {
            "name": "Comprehensive Research",
            "endpoint": "/api/ask-research",
            "expected_sources": ["pdf", "video_transcript", "llm_processed", "Web Source"],
            "forbidden_sources": ["Obsidian Note"]
        }
    ]
    
    all_passed = True
    
    for test in tests:
        print(f"\n🧪 Testing {test['name']}...")
        
        try:
            response = requests.post(f"{base_url}{test['endpoint']}", 
                                   headers=headers, json=test_data, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ {test['name']} failed with status {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            citations = data.get("citations", [])
            
            if not citations:
                print(f"⚠️  {test['name']} returned no citations")
                continue
            
            # Extract source types
            sources = [citation.get("section", "unknown") for citation in citations]
            sources = list(set(sources))  # Remove duplicates
            
            print(f"   Sources found: {sources}")
            
            # Check for forbidden sources
            forbidden_found = [s for s in sources if any(fs in s for fs in test['forbidden_sources'])]
            if forbidden_found:
                print(f"❌ {test['name']} contains forbidden sources: {forbidden_found}")
                all_passed = False
            else:
                print(f"✅ {test['name']} - No forbidden sources found")
            
            # Check for expected sources (for modes that should have specific sources)
            if test['name'] in ["RAG Only", "Obsidian Only"]:
                expected_found = [s for s in sources if any(es in s for es in test['expected_sources'])]
                if not expected_found:
                    print(f"⚠️  {test['name']} - No expected sources found")
                else:
                    print(f"✅ {test['name']} - Expected sources found: {expected_found}")
            
        except Exception as e:
            print(f"❌ {test['name']} error: {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting EminiPlayer Data Source Validation...")
    
    if test_data_sources():
        print("\n🎉 All tests passed! Data source exclusivity is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed! Check the output above for details.")
        sys.exit(1)