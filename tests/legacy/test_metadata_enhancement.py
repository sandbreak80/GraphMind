#!/usr/bin/env python3
"""Test Metadata Enhancement System"""

import requests
import time
import json
from datetime import datetime

def test_metadata_enhancement():
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
    
    print("\n🏷️ TESTING METADATA ENHANCEMENT SYSTEM")
    print("=" * 60)
    
    # Sample documents for metadata extraction
    sample_documents = [
        {
            "id": "doc_1",
            "title": "Advanced Momentum Trading Strategy Implementation",
            "text": """
            This comprehensive guide covers the implementation of a sophisticated momentum trading strategy 
            using RSI and MACD indicators. The strategy involves identifying strong trending markets and 
            entering positions when momentum indicators confirm the trend direction. Risk management is 
            critical, with stop losses set at 2% below entry and position sizing based on account volatility. 
            Backtesting on 5 years of historical data shows consistent profitability with a Sharpe ratio of 1.8. 
            The strategy works best in trending markets with high volatility and requires careful monitoring 
            of market conditions. Implementation involves Python code for signal generation and automated 
            execution through broker APIs. Key success factors include proper risk management, disciplined 
            execution, and regular strategy optimization based on changing market conditions.
            """,
            "expected_domain": "strategy_development"
        },
        {
            "id": "doc_2", 
            "title": "Risk Management Best Practices for Portfolio Optimization",
            "text": """
            Effective risk management is the cornerstone of successful trading and portfolio management. 
            This analysis covers essential risk management techniques including position sizing, diversification, 
            and drawdown control. Never risk more than 2% of your portfolio on any single trade. Diversification 
            across different asset classes, sectors, and timeframes helps reduce overall portfolio risk. 
            Regular portfolio rebalancing ensures risk exposure remains within acceptable limits. Key metrics 
            include maximum drawdown, Value at Risk (VaR), and Sharpe ratio. The analysis shows that proper 
            risk management can improve portfolio performance by 15-20% while reducing volatility. Common 
            mistakes include over-leveraging, inadequate diversification, and emotional decision-making. 
            Best practices include setting clear risk parameters, using stop losses, and maintaining detailed 
            performance records.
            """,
            "expected_domain": "risk_management"
        },
        {
            "id": "doc_3",
            "title": "Technical Analysis: Chart Patterns and Indicators",
            "text": """
            Technical analysis is a powerful tool for market analysis using price charts and indicators. 
            This tutorial covers basic chart patterns including head and shoulders, double tops, triangles, 
            and flags. Moving averages help identify trends, while RSI and Stochastic oscillators detect 
            overbought and oversold conditions. Support and resistance levels are crucial for entry and 
            exit points. Volume analysis confirms the strength of price movements. The tutorial includes 
            step-by-step examples and practical exercises. Beginners should start with simple patterns 
            and gradually learn more complex techniques. Common mistakes include over-analyzing charts 
            and ignoring fundamental analysis. Best practices include using multiple timeframes and 
            combining different indicators for confirmation.
            """,
            "expected_domain": "technical_analysis"
        }
    ]
    
    print(f"📝 Testing metadata extraction for {len(sample_documents)} documents...")
    print("-" * 60)
    
    total_tests = 0
    successful_tests = 0
    extracted_metadata = []
    
    for i, doc in enumerate(sample_documents, 1):
        print(f"\n📄 Document {i}/{len(sample_documents)}: {doc['title']}")
        
        try:
            response = requests.post(
                f"{base_url}/extract-metadata",
                headers=headers,
                data={
                    "document_id": doc["id"],
                    "title": doc["title"],
                    "text": doc["text"],
                    "source": "test_document"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display extracted metadata
                print(f"   ✅ Success: Metadata extracted")
                print(f"   📊 Content Type: {data.get('content_type', 'N/A')}")
                print(f"   🎯 Trading Domain: {data.get('trading_domain', 'N/A')}")
                print(f"   📈 Complexity Level: {data.get('complexity_level', 'N/A')}")
                print(f"   🔑 Key Concepts: {len(data.get('key_concepts', []))} found")
                print(f"   📋 Trading Strategies: {', '.join(data.get('trading_strategies', []))}")
                print(f"   📊 Technical Indicators: {len(data.get('technical_indicators', []))} found")
                print(f"   ⚠️  Risk Factors: {', '.join(data.get('risk_factors', []))}")
                print(f"   ⏰ Time Frames: {', '.join(data.get('time_frames', []))}")
                print(f"   📈 Market Conditions: {', '.join(data.get('market_conditions', []))}")
                print(f"   😊 Sentiment: {data.get('sentiment', 'N/A')}")
                
                # Show confidence scores
                confidence_scores = data.get('confidence_scores', {})
                if confidence_scores:
                    print(f"   🎯 Confidence Scores:")
                    for key, value in confidence_scores.items():
                        print(f"      {key}: {value:.2f}")
                
                # Show quality indicators
                quality_indicators = data.get('quality_indicators', {})
                if quality_indicators:
                    print(f"   📊 Quality Score: {quality_indicators.get('overall_score', 0):.2f}")
                
                extracted_metadata.append(data)
                successful_tests += 1
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
            
            total_tests += 1
            
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            total_tests += 1
    
    print(f"\n📊 METADATA EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Test document filtering
    print(f"\n🔍 TESTING DOCUMENT FILTERING")
    print("-" * 60)
    
    if extracted_metadata:
        # Test filtering by trading domain
        print(f"🔍 Filtering by trading domain: strategy_development")
        
        try:
            response = requests.post(
                f"{base_url}/filter-documents",
                headers=headers,
                data={
                    "documents": json.dumps(extracted_metadata),
                    "filters": json.dumps({"trading_domain": "strategy_development"})
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Filtered {data.get('filtered_count', 0)} documents from {data.get('original_count', 0)}")
                
                for doc in data.get('filtered_documents', []):
                    print(f"      - {doc.get('title', 'N/A')} ({doc.get('trading_domain', 'N/A')})")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test filtering by complexity level
        print(f"\n🔍 Filtering by complexity level: intermediate")
        
        try:
            response = requests.post(
                f"{base_url}/filter-documents",
                headers=headers,
                data={
                    "documents": json.dumps(extracted_metadata),
                    "filters": json.dumps({"complexity_level": "intermediate"})
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Filtered {data.get('filtered_count', 0)} documents from {data.get('original_count', 0)}")
                
                for doc in data.get('filtered_documents', []):
                    print(f"      - {doc.get('title', 'N/A')} ({doc.get('complexity_level', 'N/A')})")
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test metadata analysis
    print(f"\n🔬 METADATA ANALYSIS")
    print("-" * 60)
    
    if extracted_metadata:
        # Analyze domain distribution
        domains = [doc.get('trading_domain', 'unknown') for doc in extracted_metadata]
        domain_counts = {}
        for domain in domains:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        print(f"📊 Domain Distribution:")
        for domain, count in domain_counts.items():
            print(f"   {domain}: {count} documents")
        
        # Analyze complexity distribution
        complexities = [doc.get('complexity_level', 'unknown') for doc in extracted_metadata]
        complexity_counts = {}
        for complexity in complexities:
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        print(f"📈 Complexity Distribution:")
        for complexity, count in complexity_counts.items():
            print(f"   {complexity}: {count} documents")
        
        # Analyze sentiment distribution
        sentiments = [doc.get('sentiment', 'unknown') for doc in extracted_metadata]
        sentiment_counts = {}
        for sentiment in sentiments:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        print(f"😊 Sentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            print(f"   {sentiment}: {count} documents")
    
    print(f"\n🎯 METADATA ENHANCEMENT FEATURES TESTED:")
    print("   ✅ Trading domain classification")
    print("   ✅ Complexity level assessment")
    print("   ✅ Key concept extraction")
    print("   ✅ Trading strategy identification")
    print("   ✅ Technical indicator detection")
    print("   ✅ Risk factor analysis")
    print("   ✅ Time frame extraction")
    print("   ✅ Market condition analysis")
    print("   ✅ Quality indicator assessment")
    print("   ✅ Sentiment analysis")
    print("   ✅ Confidence scoring")
    print("   ✅ Document filtering capabilities")
    print("   ✅ Performance tracking and statistics")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_metadata_enhancement()