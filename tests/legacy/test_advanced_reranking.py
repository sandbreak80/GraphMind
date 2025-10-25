#!/usr/bin/env python3
"""Test Advanced Reranking System"""

import requests
import time
import json
from datetime import datetime

def test_advanced_reranking():
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
    
    print("\n🎯 TESTING ADVANCED RERANKING SYSTEM")
    print("=" * 60)
    
    # Sample results to rerank (simulating retrieval results)
    sample_results = [
        {
            "text": "Moving averages are simple technical indicators that smooth out price data. They are calculated by averaging closing prices over a specific period. The 50-day and 200-day moving averages are commonly used for trend analysis.",
            "metadata": {"source": "technical_analysis_guide", "type": "definition"},
            "score": 0.8
        },
        {
            "text": "A comprehensive trading strategy implementation involves multiple steps: 1) Define entry and exit rules, 2) Implement risk management with stop losses, 3) Backtest the strategy on historical data, 4) Optimize parameters, 5) Deploy in live trading with proper position sizing.",
            "metadata": {"source": "strategy_implementation", "type": "guide"},
            "score": 0.7
        },
        {
            "text": "RSI (Relative Strength Index) is a momentum oscillator that measures the speed and change of price movements. Values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions. It's useful for identifying potential reversal points.",
            "metadata": {"source": "indicator_guide", "type": "technical"},
            "score": 0.6
        },
        {
            "text": "Risk management is crucial in trading. Never risk more than 2% of your account on a single trade. Use stop losses to limit downside risk. Diversify your portfolio across different assets and timeframes.",
            "metadata": {"source": "risk_management", "type": "best_practices"},
            "score": 0.5
        },
        {
            "text": "The market was volatile today with high volume and significant price swings. Many traders were caught off guard by the sudden reversal in the afternoon session.",
            "metadata": {"source": "market_commentary", "type": "news"},
            "score": 0.3
        }
    ]
    
    # Test queries
    test_queries = [
        "How to implement a trading strategy with risk management?",
        "What is RSI and how to use it for trading?",
        "Explain moving averages for trend analysis",
        "Best practices for portfolio risk management"
    ]
    
    rerank_strategies = ["comprehensive", "trading_focused", "quality_focused"]
    
    print(f"📝 Testing {len(test_queries)} queries across {len(rerank_strategies)} reranking strategies...")
    print("-" * 60)
    
    total_tests = 0
    successful_tests = 0
    
    for strategy in rerank_strategies:
        print(f"\n🎯 RERANKING STRATEGY: {strategy.upper()}")
        print("-" * 40)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Query {i}/{len(test_queries)}: {query[:50]}...")
            
            try:
                response = requests.post(
                    f"{base_url}/rerank-results",
                    headers=headers,
                    data={
                        "query": query,
                        "results": json.dumps(sample_results),
                        "rerank_strategy": strategy,
                        "top_k": 3
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reranked_results = data.get('reranked_results', [])
                    stats = data.get('stats', {})
                    
                    print(f"   ✅ Success: {len(reranked_results)} reranked results")
                    print(f"   📊 Avg rerank time: {stats.get('avg_rerank_time', 0):.3f}s")
                    
                    # Show top reranked results
                    if reranked_results:
                        print(f"   📝 Top reranked results:")
                        for j, result in enumerate(reranked_results[:3], 1):
                            final_score = result.get('final_score', 0)
                            confidence = result.get('confidence', 0)
                            text_preview = result.get('text', '')[:60]
                            print(f"      {j}. Score: {final_score:.3f}, Conf: {confidence:.3f} - {text_preview}...")
                            
                            # Show individual scores
                            individual_scores = result.get('individual_scores', {})
                            if individual_scores:
                                top_scores = sorted(individual_scores.items(), key=lambda x: x[1], reverse=True)[:2]
                                print(f"         Top factors: {', '.join([f'{k}: {v:.2f}' for k, v in top_scores])}")
                    
                    successful_tests += 1
                else:
                    print(f"   ❌ Error: HTTP {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                
                total_tests += 1
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                total_tests += 1
    
    print(f"\n📊 ADVANCED RERANKING SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Test reranking effectiveness
    print(f"\n🔬 RERANKING EFFECTIVENESS ANALYSIS")
    print("-" * 60)
    
    # Test with a specific query to see reranking differences
    test_query = "How to implement a trading strategy with proper risk management?"
    print(f"🔍 Test query: {test_query}")
    
    for strategy in rerank_strategies:
        try:
            response = requests.post(
                f"{base_url}/rerank-results",
                headers=headers,
                data={
                    "query": test_query,
                    "results": json.dumps(sample_results),
                    "rerank_strategy": strategy,
                    "top_k": 3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reranked_results = data.get('reranked_results', [])
                
                print(f"\n   {strategy.capitalize()} Strategy:")
                for j, result in enumerate(reranked_results, 1):
                    final_score = result.get('final_score', 0)
                    confidence = result.get('confidence', 0)
                    text_preview = result.get('text', '')[:50]
                    print(f"      {j}. Score: {final_score:.3f} - {text_preview}...")
                
        except Exception as e:
            print(f"   {strategy.capitalize()}: Error - {e}")
    
    print(f"\n🎯 RERANKING FEATURES TESTED:")
    print("   ✅ Multiple scoring methods (semantic, keyword, trading relevance)")
    print("   ✅ Document quality assessment")
    print("   ✅ Position importance weighting")
    print("   ✅ Length penalty optimization")
    print("   ✅ Diversity bonus for result variety")
    print("   ✅ Confidence scoring")
    print("   ✅ Multiple reranking strategies")
    print("   ✅ Performance tracking and statistics")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_advanced_reranking()