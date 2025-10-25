#!/usr/bin/env python3
"""
Test different query types and complexities with parallel processing
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any

def test_query_variety():
    """Test different query types and complexities"""
    
    base_url = "http://localhost:3001"
    
    # Get auth token
    print("🔐 Authenticating...")
    try:
        auth_response = requests.post(f"{base_url}/api/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        if auth_response.status_code != 200:
            print(f"❌ Auth failed: {auth_response.status_code}")
            return
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return
    
    # Test different query types
    test_queries = [
        {
            "category": "Simple Questions",
            "queries": [
                "What is trading?",
                "Define futures",
                "What is a stop loss?",
                "Explain leverage"
            ]
        },
        {
            "category": "Technical Analysis",
            "queries": [
                "What are the best technical indicators for day trading?",
                "How do I use RSI for entry and exit signals?",
                "What is the difference between support and resistance?",
                "How do I read candlestick patterns?"
            ]
        },
        {
            "category": "Strategy Questions",
            "queries": [
                "What are the most profitable trading strategies for E-mini S&P 500?",
                "How do I implement a mean reversion strategy?",
                "What is the best risk management approach for futures trading?",
                "How do I backtest a trading strategy?"
            ]
        },
        {
            "category": "Complex Analysis",
            "queries": [
                "Compare and contrast different approaches to algorithmic trading in futures markets",
                "Analyze the relationship between market volatility and trading performance across different timeframes",
                "What are the key factors that influence the effectiveness of technical analysis in different market conditions?",
                "How do macroeconomic indicators affect futures trading strategies and what are the best practices for incorporating them?"
            ]
        },
        {
            "category": "Market-Specific",
            "queries": [
                "What are the trading hours for E-mini S&P 500 futures?",
                "How do I trade crude oil futures?",
                "What is the margin requirement for gold futures?",
                "How do I hedge with currency futures?"
            ]
        }
    ]
    
    print("\n🧪 Testing Query Variety with Parallel Processing...")
    print("=" * 70)
    
    results = []
    
    for category in test_queries:
        print(f"\n📊 Testing {category['category']}:")
        print("-" * 50)
        
        category_results = []
        
        for i, query in enumerate(category['queries'], 1):
            print(f"\n   {i}. {query[:60]}{'...' if len(query) > 60 else ''}")
            
            # Test 2 times for consistency
            times = []
            response_lengths = []
            source_counts = []
            
            for run in range(2):
                start_time = time.time()
                
                try:
                    response = requests.post(
                        f"{base_url}/api/ask",
                        headers=headers,
                        json={
                            "query": query,
                            "mode": "qa",
                            "temperature": 0.1,
                            "max_tokens": 2000
                        },
                        timeout=60
                    )
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        times.append(response_time)
                        response_lengths.append(len(data.get('answer', '')))
                        source_counts.append(len(data.get('citations', [])))
                        
                        print(f"      Run {run+1}: {response_time:.2f}s, {len(data.get('answer', ''))} chars, {len(data.get('citations', []))} sources")
                    else:
                        print(f"      Run {run+1}: FAILED ({response.status_code}) - {response.text[:100]}")
                        
                except Exception as e:
                    print(f"      Run {run+1}: ERROR - {e}")
            
            if times:
                avg_time = statistics.mean(times)
                avg_length = statistics.mean(response_lengths)
                avg_sources = statistics.mean(source_counts)
                
                category_results.append({
                    "query": query,
                    "avg_time": avg_time,
                    "avg_length": avg_length,
                    "avg_sources": avg_sources,
                    "times": times
                })
                
                print(f"      📈 Average: {avg_time:.2f}s, {avg_length:.0f} chars, {avg_sources:.1f} sources")
        
        if category_results:
            avg_times = [r["avg_time"] for r in category_results]
            avg_lengths = [r["avg_length"] for r in category_results]
            avg_sources = [r["avg_sources"] for r in category_results]
            
            print(f"\n   📊 Category Summary:")
            print(f"      ⏱️  Average Response Time: {statistics.mean(avg_times):.2f}s")
            print(f"      📝 Average Response Length: {statistics.mean(avg_lengths):.0f} characters")
            print(f"      📚 Average Sources: {statistics.mean(avg_sources):.1f}")
            print(f"      🚀 Fastest: {min(avg_times):.2f}s")
            print(f"      🐌 Slowest: {max(avg_times):.2f}s")
            
            results.append({
                "category": category["category"],
                "results": category_results,
                "summary": {
                    "avg_time": statistics.mean(avg_times),
                    "avg_length": statistics.mean(avg_lengths),
                    "avg_sources": statistics.mean(avg_sources),
                    "min_time": min(avg_times),
                    "max_time": max(avg_times)
                }
            })
    
    # Overall analysis
    print("\n" + "=" * 70)
    print("📊 OVERALL QUERY VARIETY ANALYSIS")
    print("=" * 70)
    
    all_times = []
    all_lengths = []
    all_sources = []
    
    for category_result in results:
        all_times.extend([r["avg_time"] for r in category_result["results"]])
        all_lengths.extend([r["avg_length"] for r in category_result["results"]])
        all_sources.extend([r["avg_sources"] for r in category_result["results"]])
    
    if all_times:
        print(f"📊 Overall Performance:")
        print(f"   ⏱️  Average Response Time: {statistics.mean(all_times):.2f}s")
        print(f"   📝 Average Response Length: {statistics.mean(all_lengths):.0f} characters")
        print(f"   📚 Average Sources: {statistics.mean(all_sources):.1f}")
        print(f"   🚀 Fastest Query: {min(all_times):.2f}s")
        print(f"   🐌 Slowest Query: {max(all_times):.2f}s")
        print(f"   📈 Time Range: {max(all_times) - min(all_times):.2f}s")
        
        # Performance by category
        print(f"\n📊 Performance by Category:")
        for category_result in results:
            summary = category_result["summary"]
            print(f"   {category_result['category']}: {summary['avg_time']:.2f}s avg ({summary['min_time']:.2f}s - {summary['max_time']:.2f}s)")
        
        # Consistency analysis
        print(f"\n📊 Consistency Analysis:")
        time_std = statistics.stdev(all_times) if len(all_times) > 1 else 0
        print(f"   📈 Time Standard Deviation: {time_std:.2f}s")
        print(f"   📊 Coefficient of Variation: {(time_std/statistics.mean(all_times)*100):.1f}%")
        
        if time_std < 5:
            print("   ✅ EXCELLENT: Very consistent performance across query types")
        elif time_std < 10:
            print("   ✅ GOOD: Consistent performance across query types")
        elif time_std < 15:
            print("   ⚠️  MODERATE: Some variation in performance across query types")
        else:
            print("   ⚠️  HIGH VARIATION: Significant performance differences across query types")
    
    return results

if __name__ == "__main__":
    test_query_variety()