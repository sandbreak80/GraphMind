"""
Real Integration Tests with Actual Ollama
NO MOCKS - Tests against real LLM service at http://0.0.0.0:11434/

This is what we SHOULD have done from the start!
"""

import pytest
import requests
import time
from typing import Dict, Any

OLLAMA_URL = "http://0.0.0.0:11434"
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class TestRealOllamaConnectivity:
    """Test actual Ollama connectivity - NO MOCKS"""
    
    def test_ollama_is_running(self):
        """Test that Ollama service is accessible"""
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert 'models' in data
        assert len(data['models']) > 0
        print(f"✓ Ollama has {len(data['models'])} models available")
    
    def test_ollama_can_generate_response(self):
        """Test that Ollama can actually generate text"""
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": "What is 2+2? Answer with just the number.",
                "stream": False
            },
            timeout=30
        )
        assert response.status_code == 200
        data = response.json()
        assert 'response' in data
        assert len(data['response']) > 0
        print(f"✓ Ollama response: {data['response'][:100]}")


class TestRealBackendOllamaIntegration:
    """Test backend can reach and use Ollama - NO MOCKS"""
    
    @pytest.fixture
    def auth_token(self):
        """Get real auth token from backend"""
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        return response.json()['access_token']
    
    def test_backend_can_reach_ollama(self):
        """Test that backend can connect to Ollama"""
        # This should be tested via backend health check or metrics endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200
        print("✓ Backend is healthy")
    
    def test_backend_ask_endpoint_with_real_llm(self, auth_token):
        """Test /ask endpoint with REAL Ollama (no mocks!)"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        data = {
            "query": "What is 2+2?",
            "mode": "qa",
            "model": "llama3.2:latest"
        }
        
        print(f"\nTesting /ask endpoint with real LLM...")
        print(f"Token: {auth_token[:50]}...")
        
        response = requests.post(
            f"{BACKEND_URL}/ask",
            headers=headers,
            json=data,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        # This is where we'll catch the auth issue!
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        result = response.json()
        assert 'answer' in result
        assert len(result['answer']) > 0
        assert 'Sorry, I encountered an error' not in result['answer']
        
        print(f"✓ Got real LLM response: {result['answer'][:200]}")


class TestRealFrontendFlow:
    """Test complete frontend flow with REAL LLM - NO MOCKS"""
    
    def test_frontend_login(self):
        """Test login via frontend API"""
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        print(f"✓ Frontend login successful")
        return data['access_token']
    
    def test_complete_chat_flow_with_real_llm(self):
        """Test complete chat flow: login → send message → get REAL LLM response"""
        # Step 1: Login
        login_response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()['access_token']
        print(f"✓ Step 1: Login successful")
        
        # Step 2: Send chat message
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        chat_data = {
            "query": "What is the capital of France? Answer in one sentence.",
            "mode": "qa",
            "model": "llama3.2:latest"
        }
        
        print(f"✓ Step 2: Sending chat request...")
        chat_response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json=chat_data,
            timeout=60
        )
        
        print(f"Status: {chat_response.status_code}")
        print(f"Response: {chat_response.text[:500]}")
        
        # This is the critical test that should catch auth issues!
        assert chat_response.status_code == 200, f"Chat failed: {chat_response.status_code} - {chat_response.text}"
        
        result = chat_response.json()
        assert 'answer' in result or 'response' in result, f"No answer in response: {result.keys()}"
        
        answer = result.get('answer') or result.get('response', '')
        assert len(answer) > 0, "Empty response from LLM"
        assert 'Sorry, I encountered an error' not in answer, "Got error message instead of response"
        assert 'Paris' in answer or 'paris' in answer.lower(), f"Expected Paris in answer, got: {answer}"
        
        print(f"✓ Step 3: Got real LLM response: {answer[:200]}")
        print(f"\n🎉 COMPLETE CHAT FLOW WITH REAL LLM: SUCCESS!")


class TestRealPerformance:
    """Test real performance with actual Ollama"""
    
    @pytest.fixture
    def auth_token(self):
        """Get real auth token"""
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        return response.json()['access_token']
    
    def test_llm_response_time(self, auth_token):
        """Test real LLM response time (no mocks!)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        data = {
            "query": "What is 2+2?",
            "mode": "qa",
            "model": "llama3.2:latest"
        }
        
        start = time.time()
        response = requests.post(
            f"{BACKEND_URL}/ask",
            headers=headers,
            json=data,
            timeout=60
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        print(f"✓ Real LLM response time: {elapsed:.2f}s")
        
        # Should be under 30 seconds for simple query
        assert elapsed < 30, f"Response too slow: {elapsed}s"


if __name__ == "__main__":
    """Run tests with real Ollama - NO MOCKS!"""
    print("\n" + "="*60)
    print("RUNNING REAL INTEGRATION TESTS WITH ACTUAL OLLAMA")
    print("NO MOCKS - Testing against real LLM service")
    print("="*60 + "\n")
    
    pytest.main([__file__, "-v", "-s", "--tb=short"])

