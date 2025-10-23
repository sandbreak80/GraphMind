#!/usr/bin/env python3
"""
Test script for intelligent query generation
"""

import requests
import json
from typing import Dict, Any

def test_query_generation():
    """Test the intelligent query generation endpoint."""
    
    # Test cases with different types of trading questions
    test_cases = [
        "What's the current market sentiment for ES futures?",
        "How is the NASDAQ performing today?",
        "What are the key support and resistance levels for NQ?",
        "Show me recent economic indicators that might affect futures trading",
        "What's the correlation between ES and VIX today?",
        "I want to understand mean reversion strategies for E-mini futures"
    ]
    
    base_url = "http://localhost:8001"
    
    print("🧠 Testing Intelligent Query Generation")
    print("=" * 50)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {query}")
        print("-" * 40)
        
        try:
            # Call the query generation endpoint
            response = requests.post(
                f"{base_url}/generate-search-queries",
                json={
                    "request": {
                        "query": query,
                        "mode": "qa",
                        "top_k": 5
                    }
                },
                headers={"Authorization": "Bearer test-token"}  # Use test token
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generated {data['total_queries']} search queries:")
                
                for j, gen_query in enumerate(data['generated_queries'], 1):
                    print(f"  {j}. Query: {gen_query['query']}")
                    print(f"     Intent: {gen_query['intent']}")
                    print(f"     Type: {gen_query['search_type']}")
                    print(f"     Priority: {gen_query['priority']}")
                    print(f"     Entities: {gen_query['entities']}")
                    print(f"     Context: {gen_query['context']}")
                    print()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Query Generation Test Complete!")

def test_enhanced_search():
    """Test the enhanced search with intelligent queries."""
    
    test_query = "What are the current market conditions for ES futures and what should I watch for?"
    
    base_url = "http://localhost:8001"
    
    print("\n🔍 Testing Enhanced Search with Intelligent Queries")
    print("=" * 60)
    print(f"Query: {test_query}")
    print("-" * 60)
    
    try:
        # Call the enhanced search endpoint
        response = requests.post(
            f"{base_url}/ask-enhanced",
            json={
                "request": {
                    "query": test_query,
                    "mode": "qa",
                    "top_k": 5
                }
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced search successful!")
            print(f"Answer: {data['answer'][:200]}...")
            print(f"Total sources: {data['total_sources']}")
            print(f"Web enabled: {data['web_enabled']}")
            
            if data.get('search_metadata'):
                metadata = data['search_metadata']
                print(f"\n📊 Search Metadata:")
                print(f"  Generated queries: {metadata.get('generated_queries', [])}")
                print(f"  Entities found: {metadata.get('entities_found', [])}")
                print(f"  Total queries: {metadata.get('total_queries', 0)}")
                print(f"  Successful queries: {metadata.get('successful_queries', 0)}")
            
            print(f"\n📚 Citations ({len(data['citations'])}):")
            for i, citation in enumerate(data['citations'][:3], 1):  # Show first 3
                print(f"  {i}. {citation['text'][:100]}...")
                print(f"     Source: {citation['doc_id']} | Score: {citation['score']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Starting Intelligent Search Tests")
    
    # Test query generation
    test_query_generation()
    
    # Test enhanced search
    test_enhanced_search()
    
    print("\n✨ All tests completed!")
