#!/usr/bin/env python3
"""Test script for dynamic retrieval parameter optimization."""
import requests
import time
import statistics

def test_dynamic_retrieval():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🎯 Testing Dynamic Retrieval Parameter Optimization")
    print("=" * 60)
    
    # Test queries designed to trigger different retrieval profiles
    test_cases = [
        {
            "query": "What is trading?",
            "expected_profile": "simple",
            "description": "Simple question - should use minimal retrieval"
        },
        {
            "query": "Explain RSI indicator and how it works",
            "expected_profile": "medium",
            "description": "Medium complexity - balanced retrieval"
        },
        {
            "query": "Compare momentum and mean reversion strategies with technical analysis",
            "expected_profile": "complex",
            "description": "Complex analysis - comprehensive retrieval"
        },
        {
            "query": "Provide a comprehensive, detailed, and thorough analysis of current market conditions with extensive research into multiple trading strategies",
            "expected_profile": "research",
            "description": "Research query - extensive retrieval"
        }
    ]
    
    response_times = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}")
        print(f"   Query: {case['query']}")
        print(f"   Expected profile: {case['expected_profile']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": case["query"],
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {response_time:.2f}s")
                print(f"   📝 Answer length: {len(data.get('answer', ''))}")
                print(f"   📚 Citations: {len(data.get('citations', []))}")
                
                # Analyze response time vs expected profile
                if case['expected_profile'] == 'simple' and response_time < 0.5:
                    print(f"   🚀 Fast response for simple query!")
                elif case['expected_profile'] == 'research' and response_time > 0.5:
                    print(f"   🔍 Thorough processing for research query!")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test retrieval optimization monitoring
    print(f"\n📊 Retrieval Optimization Monitoring:")
    try:
        response = requests.get(f"{base_url}/monitoring/retrieval")
        if response.status_code == 200:
            retrieval_data = response.json()
            print(f"   ✅ Retrieval profiles available:")
            for profile, details in retrieval_data['profiles'].items():
                print(f"      {profile}: {details['description']}")
                print(f"         Total docs: {details['total_docs_retrieved']}")
                print(f"         Final docs: {details['final_docs']}")
                print(f"         Efficiency: {details['efficiency_ratio']:.2f}")
        else:
            print(f"   ❌ Failed to get retrieval data: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting retrieval data: {e}")
    
    # Test performance comparison
    print(f"\n📈 Performance Analysis:")
    if response_times:
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        
        # Analyze performance by complexity
        simple_time = response_times[0]  # First query (simple)
        medium_time = response_times[1]  # Second query (medium)
        complex_time = response_times[2]  # Third query (complex)
        research_time = response_times[3]  # Fourth query (research)
        
        print(f"\n   Performance by complexity:")
        print(f"   Simple query: {simple_time:.2f}s")
        print(f"   Medium query: {medium_time:.2f}s")
        print(f"   Complex query: {complex_time:.2f}s")
        print(f"   Research query: {research_time:.2f}s")
        
        # Check if optimization is working (simple should be faster)
        if simple_time < medium_time < complex_time:
            print(f"   ✅ Optimization working: Simple queries are fastest!")
        else:
            print(f"   ⚠️  Optimization may need tuning")
    
    # Test with repeated queries to see caching + optimization
    print(f"\n🔄 Testing Caching + Optimization:")
    repeated_queries = [
        "What is trading?",
        "Explain RSI indicator",
        "What is trading?",  # Repeat
        "Explain RSI indicator"  # Repeat
    ]
    
    repeated_times = []
    for i, query in enumerate(repeated_queries, 1):
        print(f"\n   {i}. Testing: {query}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            repeated_times.append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Success: {response_time:.2f}s")
                print(f"      📝 Answer length: {len(data.get('answer', ''))}")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Analyze caching + optimization
    if len(repeated_times) >= 4:
        first_run = repeated_times[:2]
        second_run = repeated_times[2:]
        
        print(f"\n   📊 Caching + Optimization Analysis:")
        print(f"   First run average: {statistics.mean(first_run):.2f}s")
        print(f"   Second run average: {statistics.mean(second_run):.2f}s")
        
        if statistics.mean(second_run) < statistics.mean(first_run):
            improvement = ((statistics.mean(first_run) - statistics.mean(second_run)) / statistics.mean(first_run) * 100)
            print(f"   🚀 Combined improvement: {improvement:.1f}%")
        else:
            print(f"   ⚠️  Caching may not be working optimally")

if __name__ == "__main__":
    test_dynamic_retrieval()