#!/usr/bin/env python3
"""
Test different retrieval parameters with parallel processing
"""

import time
import requests
import json
import statistics
from typing import List, Dict, Any

def test_retrieval_parameters():
    """Test different retrieval parameters with parallel processing"""
    
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
    
    print("\n🧪 Testing Different Retrieval Parameters with Parallel Processing...")
    print("=" * 80)
    
    # Test query
    test_query = "What are the best trading strategies for futures markets?"
    
    # Test different parameter combinations
    parameter_tests = [
        {
            "name": "Ultra Fast (Minimal Recall)",
            "bm25_top_k": 5,
            "embedding_top_k": 5,
            "rerank_top_k": 2,
            "expected_speed": "fast",
            "expected_quality": "low"
        },
        {
            "name": "Fast (Low Recall)",
            "bm25_top_k": 10,
            "embedding_top_k": 10,
            "rerank_top_k": 3,
            "expected_speed": "fast",
            "expected_quality": "low"
        },
        {
            "name": "Balanced (Current Default)",
            "bm25_top_k": 30,
            "embedding_top_k": 30,
            "rerank_top_k": 8,
            "expected_speed": "medium",
            "expected_quality": "medium"
        },
        {
            "name": "Comprehensive (High Recall)",
            "bm25_top_k": 50,
            "embedding_top_k": 50,
            "rerank_top_k": 15,
            "expected_speed": "slow",
            "expected_quality": "high"
        },
        {
            "name": "Ultra Comprehensive (Max Recall)",
            "bm25_top_k": 100,
            "embedding_top_k": 100,
            "rerank_top_k": 25,
            "expected_speed": "slow",
            "expected_quality": "high"
        },
        {
            "name": "BM25 Heavy (Lexical Focus)",
            "bm25_top_k": 80,
            "embedding_top_k": 20,
            "rerank_top_k": 10,
            "expected_speed": "medium",
            "expected_quality": "medium"
        },
        {
            "name": "Embedding Heavy (Semantic Focus)",
            "bm25_top_k": 20,
            "embedding_top_k": 80,
            "rerank_top_k": 10,
            "expected_speed": "medium",
            "expected_quality": "medium"
        },
        {
            "name": "Rerank Heavy (Quality Focus)",
            "bm25_top_k": 40,
            "embedding_top_k": 40,
            "rerank_top_k": 20,
            "expected_speed": "slow",
            "expected_quality": "high"
        }
    ]
    
    results = []
    
    for i, test_config in enumerate(parameter_tests, 1):
        print(f"\n{i}. Testing {test_config['name']}:")
        print(f"   BM25: {test_config['bm25_top_k']}, Embedding: {test_config['embedding_top_k']}, Rerank: {test_config['rerank_top_k']}")
        
        # Test multiple times for consistency
        times = []
        response_lengths = []
        source_counts = []
        
        for run in range(3):  # 3 runs per test
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{base_url}/api/ask",
                    headers=headers,
                    json={
                        "query": test_query,
                        "mode": "qa",
                        "bm25_top_k": test_config["bm25_top_k"],
                        "embedding_top_k": test_config["embedding_top_k"],
                        "rerank_top_k": test_config["rerank_top_k"],
                        "temperature": 0.1,
                        "max_tokens": 2000
                    },
                    timeout=120  # Longer timeout for comprehensive tests
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
            time_std = statistics.stdev(times) if len(times) > 1 else 0
            
            print(f"      📈 Average: {avg_time:.2f}s ± {time_std:.2f}s, {avg_length:.0f} chars, {avg_sources:.1f} sources")
            
            # Performance assessment
            if avg_time < 5:
                speed_rating = "🚀 Very Fast"
            elif avg_time < 10:
                speed_rating = "⚡ Fast"
            elif avg_time < 20:
                speed_rating = "⚖️ Medium"
            elif avg_time < 30:
                speed_rating = "🐌 Slow"
            else:
                speed_rating = "🐢 Very Slow"
            
            if avg_sources > 15:
                quality_rating = "🎯 High Quality"
            elif avg_sources > 8:
                quality_rating = "✅ Good Quality"
            elif avg_sources > 3:
                quality_rating = "⚠️ Medium Quality"
            else:
                quality_rating = "❌ Low Quality"
            
            print(f"      📊 Assessment: {speed_rating}, {quality_rating}")
            
            results.append({
                "config": test_config,
                "avg_time": avg_time,
                "time_std": time_std,
                "avg_length": avg_length,
                "avg_sources": avg_sources,
                "times": times,
                "response_lengths": response_lengths,
                "source_counts": source_counts
            })
        else:
            print(f"      ❌ All runs failed")
            results.append({
                "config": test_config,
                "avg_time": 0,
                "time_std": 0,
                "avg_length": 0,
                "avg_sources": 0,
                "times": [],
                "response_lengths": [],
                "source_counts": []
            })
    
    # Analysis
    print("\n" + "=" * 80)
    print("📊 RETRIEVAL PARAMETERS ANALYSIS")
    print("=" * 80)
    
    successful_results = [r for r in results if r["avg_time"] > 0]
    
    if successful_results:
        print(f"📊 Performance Summary:")
        print(f"   ✅ Successful Configurations: {len(successful_results)}/{len(results)}")
        
        # Speed analysis
        times = [r["avg_time"] for r in successful_results]
        print(f"\n📊 Speed Analysis:")
        print(f"   🚀 Fastest: {min(times):.2f}s")
        print(f"   🐌 Slowest: {max(times):.2f}s")
        print(f"   📈 Average: {statistics.mean(times):.2f}s")
        print(f"   📊 Range: {max(times) - min(times):.2f}s")
        
        # Quality analysis
        sources = [r["avg_sources"] for r in successful_results]
        print(f"\n📊 Quality Analysis (Sources):")
        print(f"   📚 Most Sources: {max(sources):.1f}")
        print(f"   📚 Least Sources: {min(sources):.1f}")
        print(f"   📈 Average: {statistics.mean(sources):.1f}")
        
        # Response length analysis
        lengths = [r["avg_length"] for r in successful_results]
        print(f"\n📊 Response Length Analysis:")
        print(f"   📝 Longest: {max(lengths):.0f} chars")
        print(f"   📝 Shortest: {min(lengths):.0f} chars")
        print(f"   📈 Average: {statistics.mean(lengths):.0f} chars")
        
        # Performance by parameter type
        print(f"\n📊 Performance by Parameter Type:")
        
        # Speed vs Quality trade-off
        speed_quality_data = []
        for result in successful_results:
            speed_quality_data.append({
                "name": result["config"]["name"],
                "time": result["avg_time"],
                "sources": result["avg_sources"],
                "bm25": result["config"]["bm25_top_k"],
                "embedding": result["config"]["embedding_top_k"],
                "rerank": result["config"]["rerank_top_k"]
            })
        
        # Sort by time
        speed_quality_data.sort(key=lambda x: x["time"])
        
        print(f"   🏆 Speed Champions (Top 3):")
        for i, data in enumerate(speed_quality_data[:3], 1):
            print(f"      {i}. {data['name']}: {data['time']:.2f}s, {data['sources']:.1f} sources")
        
        # Sort by sources
        speed_quality_data.sort(key=lambda x: x["sources"], reverse=True)
        
        print(f"   🎯 Quality Champions (Top 3):")
        for i, data in enumerate(speed_quality_data[:3], 1):
            print(f"      {i}. {data['name']}: {data['sources']:.1f} sources, {data['time']:.2f}s")
        
        # Efficiency analysis (sources per second)
        print(f"\n📊 Efficiency Analysis (Sources per Second):")
        efficiency_data = []
        for result in successful_results:
            if result["avg_time"] > 0:
                efficiency = result["avg_sources"] / result["avg_time"]
                efficiency_data.append({
                    "name": result["config"]["name"],
                    "efficiency": efficiency,
                    "time": result["avg_time"],
                    "sources": result["avg_sources"]
                })
        
        efficiency_data.sort(key=lambda x: x["efficiency"], reverse=True)
        
        for i, data in enumerate(efficiency_data[:5], 1):
            print(f"      {i}. {data['name']}: {data['efficiency']:.2f} sources/sec")
        
        # Parameter impact analysis
        print(f"\n📊 Parameter Impact Analysis:")
        
        # BM25 impact
        bm25_impact = {}
        for result in successful_results:
            bm25_k = result["config"]["bm25_top_k"]
            if bm25_k not in bm25_impact:
                bm25_impact[bm25_k] = []
            bm25_impact[bm25_k].append(result["avg_time"])
        
        print(f"   🔍 BM25 Impact:")
        for bm25_k in sorted(bm25_impact.keys()):
            avg_time = statistics.mean(bm25_impact[bm25_k])
            print(f"      BM25={bm25_k}: {avg_time:.2f}s avg")
        
        # Embedding impact
        embedding_impact = {}
        for result in successful_results:
            embedding_k = result["config"]["embedding_top_k"]
            if embedding_k not in embedding_impact:
                embedding_impact[embedding_k] = []
            embedding_impact[embedding_k].append(result["avg_time"])
        
        print(f"   🧠 Embedding Impact:")
        for embedding_k in sorted(embedding_impact.keys()):
            avg_time = statistics.mean(embedding_impact[embedding_k])
            print(f"      Embedding={embedding_k}: {avg_time:.2f}s avg")
        
        # Rerank impact
        rerank_impact = {}
        for result in successful_results:
            rerank_k = result["config"]["rerank_top_k"]
            if rerank_k not in rerank_impact:
                rerank_impact[rerank_k] = []
            rerank_impact[rerank_k].append(result["avg_time"])
        
        print(f"   🎯 Rerank Impact:")
        for rerank_k in sorted(rerank_impact.keys()):
            avg_time = statistics.mean(rerank_impact[rerank_k])
            print(f"      Rerank={rerank_k}: {avg_time:.2f}s avg")
        
        # Recommendations
        print(f"\n📊 Recommendations:")
        
        # Best for speed
        fastest = min(successful_results, key=lambda x: x["avg_time"])
        print(f"   🚀 Best for Speed: {fastest['config']['name']} ({fastest['avg_time']:.2f}s)")
        
        # Best for quality
        best_quality = max(successful_results, key=lambda x: x["avg_sources"])
        print(f"   🎯 Best for Quality: {best_quality['config']['name']} ({best_quality['avg_sources']:.1f} sources)")
        
        # Best balance
        balance_scores = []
        for result in successful_results:
            # Normalize time (lower is better) and sources (higher is better)
            time_score = 1 / (result["avg_time"] / min(times))
            source_score = result["avg_sources"] / max(sources) if max(sources) > 0 else 0
            balance_score = (time_score + source_score) / 2
            balance_scores.append((result, balance_score))
        
        best_balance = max(balance_scores, key=lambda x: x[1])
        print(f"   ⚖️ Best Balance: {best_balance[0]['config']['name']} (score: {best_balance[1]:.3f})")
    
    return results

if __name__ == "__main__":
    test_retrieval_parameters()