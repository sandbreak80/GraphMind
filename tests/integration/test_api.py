#!/usr/bin/env python3
"""Test Ollama API directly."""
import requests
import json

def test_api():
    """Test Ollama API directly."""
    
    url = "http://host.docker.internal:11434/api/generate"
    payload = {
        "model": "llama3.1:latest",
        "prompt": "Hello",
        "stream": False
    }
    
    print(f"Testing: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('response', 'No response')}")
            print("✓ SUCCESS!")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()