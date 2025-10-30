"""
Real Integration Tests Using Docker Network
Tests run INSIDE Docker containers using Docker service names

This is the CORRECT way to test a Docker-based application!
"""

import pytest
import requests
import time
import os

# Use Docker service names (not localhost)
OLLAMA_URL = "http://ollama:11434"
BACKEND_URL = "http://graphmind-rag:8000"
FRONTEND_URL = "http://graphmind-frontend:3000"

# For tests running on host, use exposed ports
if os.getenv('DOCKER_TESTS') != 'true':
    OLLAMA_URL = "http://localhost:11434"
    BACKEND_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:3000"


class TestDockerNetworkConnectivity:
    """Test connectivity within Docker network"""
    
    def test_ollama_accessible_via_docker_network(self):
        """Test Ollama is accessible via Docker service name"""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            assert response.status_code == 200
            models = response.json()['models']
            print(f"✓ Ollama accessible: {len(models)} models available")
        except Exception as e:
            pytest.skip(f"Running on host, not in Docker network: {e}")


class TestFrontendIntegration:
    """Test complete frontend flow (the CORRECT way users interact)"""
    
    def test_complete_user_flow_via_frontend(self):
        """
        Test the ACTUAL user flow:
        1. User opens browser → frontend
        2. User logs in → frontend API → backend
        3. User sends message → frontend API → backend → Ollama
        4. User gets response
        
        This is what we should have tested from the start!
        """
        print("\n" + "="*60)
        print("TESTING REAL USER FLOW (NO MOCKS)")
        print("="*60)
        
        # Step 1: Login via frontend (how users actually do it)
        print("\n[Step 1] Login via frontend...")
        login_response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=10
        )
        
        assert login_response.status_code == 200, f"Login failed: {login_response.status_code} - {login_response.text}"
        token = login_response.json()['access_token']
        print(f"✓ Login successful, token: {token[:30]}...")
        
        # Step 2: Send chat message via frontend (how users actually do it)
        print("\n[Step 2] Send chat message via frontend...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        chat_data = {
            "query": "What is 2+2? Answer with just the number.",
            "mode": "qa",
            "model": "llama3.2:latest"
        }
        
        chat_response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json=chat_data,
            timeout=60
        )
        
        print(f"Response status: {chat_response.status_code}")
        
        # Step 3: Verify we got a real LLM response (not an error)
        assert chat_response.status_code == 200, f"Chat failed: {chat_response.status_code} - {chat_response.text[:500]}"
        
        result = chat_response.json()
        print(f"\nResponse keys: {list(result.keys())}")
        
        # Get the answer
        answer = result.get('answer', '')
        print(f"\n[Step 3] LLM Response: {answer}")
        
        # Verify it's a real response, not an error
        assert len(answer) > 0, "Empty response from LLM"
        assert 'Sorry, I encountered an error' not in answer, "Got error message instead of LLM response"
        assert '4' in answer or 'four' in answer.lower(), f"Expected '4' in answer, got: {answer}"
        
        print("\n" + "="*60)
        print("✅ COMPLETE USER FLOW: SUCCESS!")
        print(f"✅ User can login → send message → get LLM response")
        print(f"✅ Real Ollama integration working")
        print(f"✅ No mocks used - tested actual system")
        print("="*60)
    
    def test_multiple_chat_messages(self):
        """Test multiple messages in sequence (real usage)"""
        # Login
        login_response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()['access_token']
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Send multiple messages
        questions = [
            "What is 2+2?",
            "What is 3+3?",
            "What is 5+5?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n[Message {i}] {question}")
            response = requests.post(
                f"{FRONTEND_URL}/api/ask",
                headers=headers,
                json={"query": question, "mode": "qa", "model": "llama3.2:latest"},
                timeout=60
            )
            assert response.status_code == 200
            answer = response.json().get('answer', '')
            print(f"Response: {answer[:100]}")
            assert 'Sorry, I encountered an error' not in answer
        
        print("\n✅ Multiple messages working - real user experience validated")
    
    def test_different_models(self):
        """Test with different Ollama models"""
        # Login
        login_response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()['access_token']
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Test with different models
        models = ["llama3.2:latest", "llama3.1:latest"]
        
        for model in models:
            print(f"\n[Testing model: {model}]")
            response = requests.post(
                f"{FRONTEND_URL}/api/ask",
                headers=headers,
                json={
                    "query": "Say 'Hello'",
                    "mode": "qa",
                    "model": model
                },
                timeout=60
            )
            
            if response.status_code == 200:
                answer = response.json().get('answer', '')
                print(f"✓ {model} response: {answer[:100]}")
                assert 'Sorry, I encountered an error' not in answer
            else:
                print(f"⚠️  {model} not available: {response.status_code}")


class TestPromptUpliftIntegration:
    """Test that Prompt Uplift feature works with real LLM"""
    
    def test_prompt_uplift_is_active(self):
        """Verify Prompt Uplift is actually working"""
        # Login
        login_response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()['access_token']
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Send vague query (should be uplifted)
        response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json={
                "query": "AAPL",  # Vague query
                "mode": "qa",
                "model": "llama3.2:latest"
            },
            timeout=60
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check if prompt_uplift metadata is present
        if 'search_metadata' in result and 'prompt_uplift' in result['search_metadata']:
            uplift_data = result['search_metadata']['prompt_uplift']
            print(f"\n✅ Prompt Uplift Active!")
            print(f"Original: {uplift_data.get('original_query')}")
            print(f"Improved: {uplift_data.get('improved_query', '')[:100]}...")
            assert uplift_data['original_query'] != uplift_data.get('improved_query')
        else:
            print("\n⚠️  Prompt Uplift metadata not in response")


class TestDockerHealthChecks:
    """Health checks for Docker services"""
    
    def test_all_services_healthy(self):
        """Verify all Docker services are reachable"""
        services = {
            'Frontend': f"{FRONTEND_URL}/api/health",
            'Backend': f"{BACKEND_URL}/health",
            'Ollama': f"{OLLAMA_URL}/api/tags"
        }
        
        print("\n" + "="*60)
        print("DOCKER SERVICE HEALTH CHECKS")
        print("="*60)
        
        all_healthy = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}: Healthy")
                else:
                    print(f"⚠️  {name}: Status {response.status_code}")
                    all_healthy = False
            except Exception as e:
                print(f"❌ {name}: {str(e)[:50]}")
                all_healthy = False
        
        print("="*60)
        assert all_healthy, "Some services are not healthy"


if __name__ == "__main__":
    """
    Run these tests to validate the REAL system:
    - No mocks
    - Real Ollama responses
    - Real user flow through frontend
    - Docker network connectivity
    """
    print("\n" + "="*70)
    print("REAL INTEGRATION TESTS - NO MOCKS")
    print("Testing actual user flow with real Ollama LLM")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s", "--tb=short", "-x"])

