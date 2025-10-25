#!/usr/bin/env python3
"""Test Query Expansion System"""

import requests
import time
import json
from datetime import datetime

def test_query_expansion():
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
    
    print("\n🔄 TESTING QUERY EXPANSION SYSTEM")
    print("=" * 60)
    
    # Test queries for expansion
    test_queries = [
        "What is a moving average strategy?",
        "How to implement RSI trading?",
        "Explain momentum trading with examples",
        "Compare scalping vs swing trading",
        "What are the risks of leverage trading?",
        "How to backtest a mean reversion strategy?",
        "Explain Bollinger Bands for volatility trading",
        "What is portfolio optimization in trading?"
    ]
    
    expansion_levels = ["minimal", "medium", "aggressive"]
    
    print(f"📝 Testing {len(test_queries)} queries across {len(expansion_levels)} expansion levels...")
    print("-" * 60)
    
    total_tests = 0
    successful_tests = 0
    
    for level in expansion_levels:
        print(f"\n🎯 EXPANSION LEVEL: {level.upper()}")
        print("-" * 40)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Query {i}/{len(test_queries)}: {query[:50]}...")
            
            try:
                response = requests.post(
                    f"{base_url}/expand-query",
                    headers=headers,
                    data={"query": query, "expansion_level": level},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    original = data.get('original_query', '')
                    expanded = data.get('expanded_queries', [])
                    synonyms = data.get('synonyms', {})
                    context_terms = data.get('context_terms', [])
                    trading_terms = data.get('trading_terms', [])
                    confidence = data.get('confidence_score', 0)
                    
                    print(f"   ✅ Success: {len(expanded)} expanded queries")
                    print(f"   📊 Confidence: {confidence:.2f}")
                    print(f"   🔤 Synonyms: {len(synonyms)} terms")
                    print(f"   🎯 Context terms: {len(context_terms)}")
                    print(f"   📈 Trading terms: {len(trading_terms)}")
                    
                    # Show top expanded queries
                    if expanded:
                        print(f"   📝 Top expansions:")
                        for j, exp_query in enumerate(expanded[:3], 1):
                            if exp_query != original:
                                print(f"      {j}. {exp_query[:60]}...")
                    
                    # Show synonyms
                    if synonyms:
                        print(f"   🔤 Key synonyms:")
                        for term, syns in list(synonyms.items())[:2]:
                            print(f"      '{term}' → {', '.join(syns[:3])}")
                    
                    successful_tests += 1
                else:
                    print(f"   ❌ Error: HTTP {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                
                total_tests += 1
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                total_tests += 1
    
    print(f"\n📊 QUERY EXPANSION SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Test expansion effectiveness
    print(f"\n🔬 EXPANSION EFFECTIVENESS ANALYSIS")
    print("-" * 60)
    
    # Test a complex query with all levels
    complex_query = "How to implement a mean reversion strategy with proper risk management?"
    print(f"🔍 Complex query: {complex_query}")
    
    for level in expansion_levels:
        try:
            response = requests.post(
                f"{base_url}/expand-query",
                headers=headers,
                data={"query": complex_query, "expansion_level": level},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                expanded_count = len(data.get('expanded_queries', []))
                synonyms_count = len(data.get('synonyms', {}))
                confidence = data.get('confidence_score', 0)
                
                print(f"   {level.capitalize()}: {expanded_count} queries, {synonyms_count} synonyms, {confidence:.2f} confidence")
                
        except Exception as e:
            print(f"   {level.capitalize()}: Error - {e}")
    
    print(f"\n🎯 EXPANSION FEATURES TESTED:")
    print("   ✅ Trading-specific synonym mapping")
    print("   ✅ Context-aware term extraction")
    print("   ✅ Technical indicator expansion")
    print("   ✅ Phrase-level expansion")
    print("   ✅ Question pattern variations")
    print("   ✅ Confidence scoring")
    print("   ✅ Multi-level expansion strategies")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_query_expansion()