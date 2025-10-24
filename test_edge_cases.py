#!/usr/bin/env python3
"""
Test edge cases and error handling with parallel processing
"""

import time
import requests
import json
from typing import List, Dict, Any

def test_edge_cases():
    """Test edge cases and error handling"""
    
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
    
    print("\n🧪 Testing Edge Cases and Error Handling...")
    print("=" * 60)
    
    # Test cases
    edge_cases = [
        {
            "name": "Empty Query",
            "query": "",
            "expected_status": 422
        },
        {
            "name": "Very Long Query",
            "query": "What is trading? " * 100,  # Very long query
            "expected_status": 200
        },
        {
            "name": "Special Characters",
            "query": "What is trading? @#$%^&*()_+{}|:<>?[]\\;'\",./",
            "expected_status": 200
        },
        {
            "name": "Unicode Characters",
            "query": "What is trading? 中文测试 🚀💰📈",
            "expected_status": 200
        },
        {
            "name": "SQL Injection Attempt",
            "query": "What is trading?'; DROP TABLE users; --",
            "expected_status": 200
        },
        {
            "name": "Extreme Parameters",
            "query": "What is trading?",
            "params": {
                "bm25_top_k": 1000,
                "embedding_top_k": 1000,
                "rerank_top_k": 1000,
                "temperature": 2.0,
                "max_tokens": 50000
            },
            "expected_status": 200
        },
        {
            "name": "Invalid Parameters",
            "query": "What is trading?",
            "params": {
                "bm25_top_k": -1,
                "embedding_top_k": -1,
                "rerank_top_k": -1,
                "temperature": -1.0,
                "max_tokens": -1
            },
            "expected_status": 200  # Should handle gracefully
        },
        {
            "name": "Very Short Query",
            "query": "?",
            "expected_status": 200
        },
        {
            "name": "Numbers Only",
            "query": "123456789",
            "expected_status": 200
        },
        {
            "name": "Mixed Languages",
            "query": "What is trading? ¿Qué es el trading? トレーディングとは何ですか？",
            "expected_status": 200
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}:")
        print(f"   Query: {test_case['query'][:50]}{'...' if len(test_case['query']) > 50 else ''}")
        
        start_time = time.time()
        
        try:
            # Prepare request data
            request_data = {
                "query": test_case["query"],
                "mode": "qa",
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            # Add custom parameters if provided
            if "params" in test_case:
                request_data.update(test_case["params"])
            
            response = requests.post(
                f"{base_url}/api/ask",
                headers=headers,
                json=request_data,
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Check if response matches expected status
            expected_status = test_case.get("expected_status", 200)
            status_match = response.status_code == expected_status
            
            if response.status_code == 200:
                data = response.json()
                answer_length = len(data.get('answer', ''))
                source_count = len(data.get('citations', []))
                
                print(f"   ✅ Status: {response.status_code} (Expected: {expected_status})")
                print(f"   ⏱️  Time: {response_time:.2f}s")
                print(f"   📝 Answer Length: {answer_length} chars")
                print(f"   📚 Sources: {source_count}")
                
                # Check for error messages in response
                if "error" in data or "Sorry, I encountered an error" in data.get('answer', ''):
                    print(f"   ⚠️  Warning: Error message in response")
                
                results.append({
                    "test_case": test_case["name"],
                    "status": response.status_code,
                    "expected_status": expected_status,
                    "status_match": status_match,
                    "response_time": response_time,
                    "answer_length": answer_length,
                    "source_count": source_count,
                    "success": status_match and response.status_code == 200
                })
                
            else:
                print(f"   ❌ Status: {response.status_code} (Expected: {expected_status})")
                print(f"   ⏱️  Time: {response_time:.2f}s")
                print(f"   📝 Response: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
                
                results.append({
                    "test_case": test_case["name"],
                    "status": response.status_code,
                    "expected_status": expected_status,
                    "status_match": status_match,
                    "response_time": response_time,
                    "answer_length": 0,
                    "source_count": 0,
                    "success": False
                })
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 60s")
            results.append({
                "test_case": test_case["name"],
                "status": "timeout",
                "expected_status": test_case.get("expected_status", 200),
                "status_match": False,
                "response_time": 60.0,
                "answer_length": 0,
                "source_count": 0,
                "success": False
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                "test_case": test_case["name"],
                "status": "error",
                "expected_status": test_case.get("expected_status", 200),
                "status_match": False,
                "response_time": 0,
                "answer_length": 0,
                "source_count": 0,
                "success": False
            })
    
    # Analysis
    print("\n" + "=" * 60)
    print("📊 EDGE CASE ANALYSIS")
    print("=" * 60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"📊 Test Results:")
    print(f"   ✅ Successful: {len(successful_tests)}/{len(results)}")
    print(f"   ❌ Failed: {len(failed_tests)}/{len(results)}")
    print(f"   📈 Success Rate: {len(successful_tests)/len(results)*100:.1f}%")
    
    if successful_tests:
        avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
        avg_length = sum(r["answer_length"] for r in successful_tests) / len(successful_tests)
        avg_sources = sum(r["source_count"] for r in successful_tests) / len(successful_tests)
        
        print(f"\n📊 Performance of Successful Tests:")
        print(f"   ⏱️  Average Response Time: {avg_time:.2f}s")
        print(f"   📝 Average Answer Length: {avg_length:.0f} chars")
        print(f"   📚 Average Sources: {avg_sources:.1f}")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   - {test['test_case']}: {test['status']} (Expected: {test['expected_status']})")
    
    # Robustness assessment
    print(f"\n📊 Robustness Assessment:")
    if len(successful_tests) >= len(results) * 0.8:
        print("   ✅ EXCELLENT: System handles edge cases very well")
    elif len(successful_tests) >= len(results) * 0.6:
        print("   ✅ GOOD: System handles most edge cases well")
    elif len(successful_tests) >= len(results) * 0.4:
        print("   ⚠️  MODERATE: System handles some edge cases but needs improvement")
    else:
        print("   ❌ POOR: System struggles with edge cases")
    
    return results

if __name__ == "__main__":
    test_edge_cases()