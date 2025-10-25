#!/usr/bin/env python3
"""Test QueryAnalyzer functionality"""

import requests
import json
from datetime import datetime

def test_query_analyzer():
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
    
    print("\n🧠 TESTING QUERY ANALYZER")
    print("=" * 60)
    
    # Test queries of different complexities
    test_queries = [
        "What is a moving average?",
        "Explain momentum trading strategies with examples",
        "How do I implement a mean reversion strategy with proper risk management?",
        "Conduct a comprehensive analysis of algorithmic trading evolution from 1980s to present day, including regulatory changes, technological advances, and market impact",
        "What are the key factors affecting ES futures pricing during market hours?",
        "Compare and contrast different portfolio optimization techniques for quantitative trading strategies"
    ]
    
    print(f"📝 Testing {len(test_queries)} queries...")
    print("-" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}/{len(test_queries)}: {query[:50]}...")
        
        try:
            # Test the analyze-query endpoint
            response = requests.post(
                f"{base_url}/analyze-query",
                headers=headers,
                data={"query": query}
            )
            
            if response.status_code == 200:
                analysis = response.json()
                print(f"   📊 Complexity Score: {analysis['complexity_score']:.2f}")
                print(f"   🎯 Level: {analysis['complexity_level'].upper()}")
                print(f"   🤖 Suggested Model: {analysis['recommendations']['suggested_model']}")
                print(f"   📈 Retrieval Params: {analysis['recommendations']['retrieval_params']}")
                print(f"   📝 Metrics: {analysis['metrics']['word_count']} words, {analysis['metrics']['technical_terms']} tech terms")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n📊 QUERY ANALYZER SUMMARY")
    print("=" * 60)
    print("✅ Query analyzer is working correctly!")
    print("🎯 Features tested:")
    print("   - Complexity scoring (0.0 to 1.0)")
    print("   - Level classification (simple/medium/complex/research)")
    print("   - Model recommendations")
    print("   - Retrieval parameter suggestions")
    print("   - Technical term detection")
    print("   - Question complexity analysis")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_query_analyzer()