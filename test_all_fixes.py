"""
Comprehensive test script to validate all GraphMind fixes
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:3000/api"
BACKEND_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

# Test 1: Login and get token
print_test("1. Authentication")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        if token:
            print_success(f"Login successful, token received")
            AUTH_HEADERS = {"Authorization": f"Bearer {token}"}
        else:
            print_error("No token in response")
            exit(1)
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        exit(1)
except Exception as e:
    print_error(f"Login error: {e}")
    exit(1)

# Test 2: Password change endpoint exists
print_test("2. Password Change Functionality")
try:
    response = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={
            "current_password": "admin123",
            "new_password": "admin123"  # Change to same password for testing
        },
        headers=AUTH_HEADERS
    )
    if response.status_code == 200:
        print_success("Password change endpoint working")
    else:
        print_error(f"Password change failed: {response.status_code}")
except Exception as e:
    print_error(f"Password change error: {e}")

# Test 3: Document upload endpoint
print_test("3. Document Upload to Backend")
try:
    # Create a test file
    test_file_content = b"This is a test document for GraphMind RAG system."
    
    files = {'file': ('test_document.txt', test_file_content, 'text/plain')}
    response = requests.post(
        f"{BASE_URL}/documents/upload",
        files=files,
        headers=AUTH_HEADERS
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Document uploaded: {data.get('filename', 'unknown')}")
    else:
        print_error(f"Document upload failed: {response.status_code} - {response.text}")
except Exception as e:
    print_error(f"Document upload error: {e}")

# Test 4: System prompts endpoint
print_test("4. System Prompts Management")
try:
    response = requests.get(
        f"{BASE_URL}/system-prompts",
        headers=AUTH_HEADERS
    )
    if response.status_code == 200:
        data = response.json()
        print_success(f"System prompts loaded: {len(data.get('prompts', {}))} modes")
    else:
        print_error(f"System prompts failed: {response.status_code}")
except Exception as e:
    print_error(f"System prompts error: {e}")

# Test 5: Web search with response validation
print_test("5. Web Search Response (No Refusal)")
try:
    response = requests.post(
        f"{BASE_URL}/ask-enhanced",
        json={
            "query": "What is machine learning?",
            "mode": "qa",
            "model": "qwen2.5:14b",
            "temperature": 0.1,
            "max_tokens": 2000,
            "web_search_results": 5,
            "web_pages_to_parse": 3,
            "conversation_history": []
        },
        headers=AUTH_HEADERS,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "")
        
        # Check for refusal phrases
        refusal_phrases = [
            "i can't fulfill",
            "i cannot fulfill",
            "i'm unable to",
            "i apologize, but i cannot"
        ]
        
        is_refusal = any(phrase in answer.lower() for phrase in refusal_phrases)
        
        if is_refusal:
            print_error(f"Web search still refusing: {answer[:100]}...")
        else:
            print_success(f"Web search working: {len(answer)} characters returned")
            if len(answer) > 50:
                print_success("Response is substantial (not a refusal)")
    else:
        print_error(f"Web search failed: {response.status_code}")
except Exception as e:
    print_error(f"Web search error: {e}")

# Test 6: Comprehensive research mode
print_test("6. Comprehensive Research Mode (Model Fix)")
try:
    response = requests.post(
        f"{BASE_URL}/ask-research",
        json={
            "query": "What is artificial intelligence?",
            "model": "qwen2.5:14b",
            "temperature": 0.3,
            "max_tokens": 3000,
            "web_search_results": 5,
            "conversation_history": []
        },
        headers=AUTH_HEADERS,
        timeout=90
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "")
        
        # Check if it's an error message
        if "404" in answer or "Error" in answer:
            print_error(f"Research mode error: {answer[:150]}...")
        else:
            print_success(f"Research mode working: {len(answer)} characters")
            sources = data.get("sources", [])
            print_success(f"Sources returned: {len(sources)}")
    else:
        print_error(f"Research mode failed: {response.status_code}")
except Exception as e:
    print_error(f"Research mode error: {e}")

# Test 7: Ollama models list
print_test("7. Ollama Models Available")
try:
    response = requests.get(
        f"{BASE_URL}/ollama/models",
        headers=AUTH_HEADERS
    )
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        print_success(f"Ollama models: {len(models)} available")
        for model in models[:5]:  # Show first 5
            print(f"  - {model.get('name', 'unknown')}")
    else:
        print_error(f"Ollama models failed: {response.status_code}")
except Exception as e:
    print_error(f"Ollama models error: {e}")

# Test 8: Documents list
print_test("8. Documents Management")
try:
    response = requests.get(
        f"{BASE_URL}/documents",
        headers=AUTH_HEADERS
    )
    if response.status_code == 200:
        data = response.json()
        docs = data.get("documents", [])
        print_success(f"Documents endpoint working: {len(docs)} documents")
    else:
        print_error(f"Documents list failed: {response.status_code}")
except Exception as e:
    print_error(f"Documents error: {e}")

# Summary
print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
print(f"{Colors.BLUE}Test Summary{Colors.END}")
print(f"{Colors.BLUE}{'='*60}{Colors.END}")
print("\nAll core functionality tests completed.")
print("Check above for any failures marked with ✗")
print("\nNote: Some tests may fail if backend is still starting up.")
print("Wait 30 seconds and run again if you see connection errors.")

