#!/usr/bin/env python3
"""Test script for monitoring endpoints only."""
import requests
import time

def test_monitoring():
    base_url = "http://localhost:8002"
    
    print("🧪 Testing Monitoring Endpoints in Development Instance")
    print("=" * 60)
    
    # Test performance metrics
    print("\n📊 Performance Metrics:")
    try:
        perf_response = requests.get(f"{base_url}/monitoring/performance")
        if perf_response.status_code == 200:
            metrics = perf_response.json()
            print(f"   ✅ Success: {metrics}")
        else:
            print(f"   ❌ Failed: {perf_response.status_code}")
            print(f"   Response: {perf_response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test cache metrics
    print(f"\n💾 Cache Metrics:")
    try:
        cache_response = requests.get(f"{base_url}/monitoring/cache")
        if cache_response.status_code == 200:
            cache_metrics = cache_response.json()
            print(f"   ✅ Success: {cache_metrics}")
        else:
            print(f"   ❌ Failed: {cache_response.status_code}")
            print(f"   Response: {cache_response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test recent queries
    print(f"\n📈 Recent Queries:")
    try:
        recent_response = requests.get(f"{base_url}/monitoring/recent")
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            print(f"   ✅ Success: {recent_data}")
        else:
            print(f"   ❌ Failed: {recent_response.status_code}")
            print(f"   Response: {recent_response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_monitoring()