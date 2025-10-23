#!/usr/bin/env python3
"""Test configuration and Ollama connection."""
import sys
from pathlib import Path
import os

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from config import OLLAMA_BASE_URL, VIDEO_ENRICHMENT_MODEL, PDF_ENRICHMENT_MODEL, CHUNK_ENRICHMENT_MODEL
from ollama_client import OllamaClient

def test_config():
    """Test configuration and Ollama connection."""
    
    print("Configuration:")
    print(f"  OLLAMA_BASE_URL: {OLLAMA_BASE_URL}")
    print(f"  VIDEO_ENRICHMENT_MODEL: {VIDEO_ENRICHMENT_MODEL}")
    print(f"  PDF_ENRICHMENT_MODEL: {PDF_ENRICHMENT_MODEL}")
    print(f"  CHUNK_ENRICHMENT_MODEL: {CHUNK_ENRICHMENT_MODEL}")
    print()
    
    # Test Ollama client
    client = OllamaClient()
    
    # Test simple generation
    print("Testing simple generation...")
    try:
        response = client.generate("Hello, how are you?", max_tokens=10)
        print(f"  Response: {response}")
        print("  ✓ SUCCESS!")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test JSON generation
    print("\nTesting JSON generation...")
    try:
        response = client.generate_json("Return a JSON object with a 'test' field set to 'success'", max_tokens=50)
        print(f"  Response: {response}")
        print("  ✓ SUCCESS!")
    except Exception as e:
        print(f"  ✗ Error: {e}")

if __name__ == "__main__":
    test_config()