#!/usr/bin/env python3
"""Test adding documents to advanced retrieval system"""

import requests
import time
import json
from datetime import datetime

def test_add_documents():
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
    
    print("\n📚 ADDING TEST DOCUMENTS TO ADVANCED RETRIEVAL")
    print("=" * 60)
    
    # Test documents
    test_documents = [
        {
            "id": "doc_1",
            "title": "Moving Average Trading Strategy",
            "text": "A moving average is a technical indicator that smooths out price data by creating a constantly updated average price. The most common types are Simple Moving Average (SMA) and Exponential Moving Average (EMA). SMA is calculated by adding up closing prices over a period and dividing by the number of periods. EMA gives more weight to recent prices. Moving averages are used to identify trends and generate trading signals. When price crosses above the moving average, it's a bullish signal. When price crosses below, it's bearish. The 50-day and 200-day moving averages are commonly used for trend analysis."
        },
        {
            "id": "doc_2", 
            "title": "Momentum Trading Strategies",
            "text": "Momentum trading is a strategy that aims to capitalize on the continuation of existing price trends. Key momentum indicators include RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), and Stochastic Oscillator. RSI measures the speed and change of price movements on a scale of 0-100. Values above 70 indicate overbought conditions, while values below 30 indicate oversold conditions. MACD uses two moving averages to identify trend changes. Momentum strategies work best in trending markets and require strict risk management. Common momentum strategies include breakout trading, trend following, and mean reversion."
        },
        {
            "id": "doc_3",
            "title": "Mean Reversion Strategy Implementation",
            "text": "Mean reversion is a trading strategy based on the theory that prices tend to return to their average over time. This strategy involves identifying when an asset's price has deviated significantly from its historical average and betting that it will revert. Key components include: 1) Statistical measures like Z-scores and Bollinger Bands to identify deviations, 2) Entry signals when price reaches extreme levels, 3) Exit signals when price returns to mean, 4) Risk management with stop-losses and position sizing. Mean reversion works best in ranging markets and requires careful backtesting. Common mean reversion strategies include pairs trading, statistical arbitrage, and contrarian trading."
        }
    ]
    
    print(f"📝 Adding {len(test_documents)} test documents...")
    
    for i, doc in enumerate(test_documents, 1):
        print(f"\n📄 Document {i}/{len(test_documents)}: {doc['title']}")
        
        try:
            # Use the regular ingest endpoint to add documents
            response = requests.post(
                f"{base_url}/ingest",
                headers=headers,
                json={
                    "text": doc["text"],
                    "title": doc["title"],
                    "source": "test_document"
                }
            )
            
            if response.status_code == 200:
                print(f"   ✅ Successfully added")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n🔍 TESTING ADVANCED RETRIEVAL WITH NEW DOCUMENTS")
    print("-" * 60)
    
    # Test queries
    test_queries = [
        "What is a moving average?",
        "Explain momentum trading strategies",
        "How do I implement mean reversion?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        
        try:
            response = requests.post(
                f"{base_url}/advanced-search",
                headers=headers,
                data={"query": query, "top_k": 3},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results_count = data.get('count', 0)
                print(f"   ✅ Success: {results_count} results")
                
                if data.get('results'):
                    for j, result in enumerate(data['results'][:2], 1):
                        preview = result.get('text', '')[:100]
                        score = result.get('score', 0)
                        print(f"   📄 Result {j}: {preview}... (score: {score:.3f})")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_add_documents()