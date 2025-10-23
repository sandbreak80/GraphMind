#!/usr/bin/env python3
"""Test network connectivity to Ollama."""
import sys
from pathlib import Path
import requests

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

def test_ollama_connection():
    """Test connection to Ollama from container."""
    
    urls_to_test = [
        "http://host.docker.internal:11434/api/tags",
        "http://localhost:11434/api/tags",
        "http://172.17.0.1:11434/api/tags"
    ]
    
    for url in urls_to_test:
        print(f"Testing: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                print(f"  Models: {models[:3]}...")
                print(f"  ✓ SUCCESS!")
                return url
            else:
                print(f"  ✗ Failed with status {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
        print()
    
    return None

if __name__ == "__main__":
    working_url = test_ollama_connection()
    if working_url:
        print(f"Working URL: {working_url}")
    else:
        print("No working URL found")