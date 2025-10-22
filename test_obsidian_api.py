#!/usr/bin/env python3
"""Test script to verify Obsidian Local REST API is working."""

import requests
import json

def test_obsidian_api():
    """Test the Obsidian Local REST API."""
    
    base_url = "http://127.0.0.1:27124"
    
    print("🧪 Testing Obsidian Local REST API")
    print("=" * 50)
    
    # Test different common endpoints
    endpoints = [
        "/",
        "/health",
        "/api/health", 
        "/v1/health",
        "/notes",
        "/api/notes",
        "/v1/notes",
        "/search",
        "/api/search",
        "/v1/search"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing: {base_url}{endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print(f"   Content length: {len(content)}")
                print(f"   Content preview: {content[:200]}...")
                
                # Try to parse as JSON
                try:
                    json_data = response.json()
                    print(f"   JSON keys: {list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'}")
                except:
                    print("   Not valid JSON")
            else:
                print(f"   Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused")
        except requests.exceptions.Timeout:
            print("   ❌ Timeout")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Make sure Obsidian Local REST API plugin is installed and enabled")
    print("2. Check plugin settings - ensure API is enabled")
    print("3. Verify the port is set to 27124")
    print("4. Make sure the API is bound to 0.0.0.0 (not just 127.0.0.1)")
    print("5. Check if authentication is required")

if __name__ == "__main__":
    test_obsidian_api()