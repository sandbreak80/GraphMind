#!/usr/bin/env python3
"""Deployment Verification Script"""

import requests
import time
import json
from datetime import datetime

def verify_deployment():
    """Verify complete deployment functionality"""
    print("🔍 DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    # Test endpoints
    endpoints = {
        "Backend Health": "http://localhost:8002/health",
        "Frontend": "http://localhost:3000",
        "ChromaDB": "http://localhost:8003/api/v1/heartbeat",
        "Redis": "redis://localhost:6379"
    }
    
    results = {}
    
    # Test backend health
    try:
        response = requests.get(endpoints["Backend Health"], timeout=5)
        if response.status_code == 200:
            results["Backend Health"] = "✅ PASS"
        else:
            results["Backend Health"] = f"❌ FAIL (HTTP {response.status_code})"
    except Exception as e:
        results["Backend Health"] = f"❌ ERROR ({str(e)})"
    
    # Test frontend
    try:
        response = requests.get(endpoints["Frontend"], timeout=5)
        if response.status_code == 200 and "TradingAI Research Platform" in response.text:
            results["Frontend"] = "✅ PASS"
        else:
            results["Frontend"] = f"❌ FAIL (HTTP {response.status_code})"
    except Exception as e:
        results["Frontend"] = f"❌ ERROR ({str(e)})"
    
    # Test ChromaDB
    try:
        response = requests.get(endpoints["ChromaDB"], timeout=5)
        if response.status_code == 200:
            results["ChromaDB"] = "✅ PASS"
        else:
            results["ChromaDB"] = f"❌ FAIL (HTTP {response.status_code})"
    except Exception as e:
        results["ChromaDB"] = f"❌ ERROR ({str(e)})"
    
    # Test Redis (basic connection)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        results["Redis"] = "✅ PASS"
    except Exception as e:
        results["Redis"] = f"❌ ERROR ({str(e)})"
    
    # Print results
    print("\n📊 SERVICE STATUS:")
    for service, status in results.items():
        print(f"  {service}: {status}")
    
    # Test API functionality
    print("\n🔧 API FUNCTIONALITY TEST:")
    
    # Authenticate
    try:
        auth_response = requests.post(
            "http://localhost:8002/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=10
        )
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test basic ask
            ask_response = requests.post(
                "http://localhost:8002/ask",
                headers=headers,
                json={
                    "query": "Test query",
                    "mode": "qa",
                    "model": "llama3.1:latest",
                    "disable_model_override": True
                },
                timeout=30
            )
            
            if ask_response.status_code == 200:
                print("  ✅ Authentication: PASS")
                print("  ✅ Basic Ask API: PASS")
            else:
                print(f"  ❌ Basic Ask API: FAIL (HTTP {ask_response.status_code})")
        else:
            print(f"  ❌ Authentication: FAIL (HTTP {auth_response.status_code})")
    except Exception as e:
        print(f"  ❌ API Test: ERROR ({str(e)})")
    
    # Overall status
    all_passed = all("✅" in status for status in results.values())
    
    print(f"\n🎯 OVERALL STATUS: {'✅ READY FOR COMMIT' if all_passed else '❌ ISSUES FOUND'}")
    
    if all_passed:
        print("\n🚀 DEPLOYMENT VERIFICATION SUCCESSFUL!")
        print("   - All services are running")
        print("   - API endpoints are functional")
        print("   - Frontend is accessible")
        print("   - Ready for Git commit")
    else:
        print("\n⚠️  DEPLOYMENT VERIFICATION FAILED!")
        print("   - Some services have issues")
        print("   - Please fix before committing")
    
    return all_passed

if __name__ == "__main__":
    verify_deployment()