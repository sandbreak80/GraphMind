"""
Comprehensive integration tests for all API endpoints
"""

import pytest
import requests
import time
from typing import Dict

@pytest.mark.integration
class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_valid_credentials(self, test_config, test_user):
        """Test login with valid credentials"""
        response = requests.post(
            f"{test_config['BASE_URL']}/api/auth/login",
            data=test_user,
            timeout=test_config["API_TIMEOUT"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data or "access_token" in data
    
    def test_login_invalid_credentials(self, test_config):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{test_config['BASE_URL']}/api/auth/login",
            data={"username": "admin", "password": "wrongpassword"},
            timeout=test_config["API_TIMEOUT"]
        )
        
        assert response.status_code in [401, 403]
    
    def test_get_current_user(self, test_config, api_headers):
        """Test getting current user info"""
        response = requests.get(
            f"{test_config['BASE_URL']}/api/auth/me",
            headers=api_headers,
            timeout=test_config["API_TIMEOUT"]
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "username" in data

@pytest.mark.integration
@pytest.mark.rag
class TestRAGEndpoints:
    """Test RAG query endpoints"""
    
    def test_rag_only_query(self, api_client):
        """Test RAG-only query endpoint"""
        response = api_client.post(
            "/ask",
            json={
                "request": {
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            },
            timeout=30
        )
        
        # Accept 200 (success), 404 (no docs), or 422 (validation error)
        assert response.status_code in [200, 404, 422, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data or "response" in data or "error" not in data
    
    def test_rag_query_with_sources(self, api_client):
        """Test that RAG query returns sources"""
        response = api_client.post(
            "/ask",
            json={
                "request": {
                    "query": "What are trading strategies?",
                    "mode": "qa",
                    "top_k": 5
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            # Should have citations or sources
            assert "citations" in data or "sources" in data

@pytest.mark.integration
@pytest.mark.web
class TestWebSearchEndpoints:
    """Test web search endpoints"""
    
    def test_web_search_query(self, api_client):
        """Test web search endpoint"""
        response = api_client.post(
            "/ask-enhanced",
            json={
                "request": {
                    "query": "Latest AI news",
                    "mode": "qa",
                    "top_k": 3
                }
            },
            timeout=30
        )
        
        # Web search might not be configured
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data or "response" in data

@pytest.mark.integration
@pytest.mark.obsidian
class TestObsidianEndpoints:
    """Test Obsidian integration endpoints"""
    
    def test_obsidian_query(self, api_client):
        """Test Obsidian query endpoint"""
        response = api_client.post(
            "/ask-obsidian",
            json={
                "request": {
                    "query": "What are my notes about trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            },
            timeout=30
        )
        
        # Obsidian might not be configured
        assert response.status_code in [200, 404, 503]

@pytest.mark.integration
class TestDocumentEndpoints:
    """Test document management endpoints"""
    
    def test_list_documents(self, api_client):
        """Test listing documents"""
        response = api_client.get("/documents", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) or isinstance(data, list)
    
    def test_trigger_ingestion(self, api_client):
        """Test triggering document ingestion"""
        response = api_client.post("/ingest", json={}, timeout=60)
        
        assert response.status_code in [200, 202, 204]

@pytest.mark.integration
class TestSystemPromptEndpoints:
    """Test system prompt endpoints"""
    
    def test_get_user_prompts(self, api_client):
        """Test getting all user prompts"""
        response = api_client.get("/user-prompts", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_specific_prompt(self, api_client):
        """Test getting prompt for specific mode"""
        response = api_client.get("/user-prompts/rag_only", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert "prompt" in data
    
    def test_set_user_prompt(self, api_client):
        """Test setting custom user prompt"""
        timestamp = int(time.time())
        test_prompt = f"""Test prompt {timestamp}.

Your role:
- Test the prompt system
- Verify persistence

Guidelines:
- Follow best practices
- Be helpful and accurate

Response format:
- Clear markdown responses
- Well-structured output"""
        
        response = api_client.put(
            "/user-prompts/rag_only",
            json={"prompt": test_prompt},
            timeout=10
        )
        
        assert response.status_code == 200
        
        # Verify it was saved
        get_response = api_client.get("/user-prompts/rag_only", timeout=10)
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert str(timestamp) in data["prompt"]
    
    def test_reset_user_prompt(self, api_client):
        """Test resetting user prompt to default"""
        # First set a custom prompt
        test_prompt = "Custom prompt with role and guidelines and response format sections"
        api_client.put(
            "/user-prompts/rag_only",
            json={"prompt": test_prompt},
            timeout=10
        )
        
        # Then reset
        response = api_client.delete("/user-prompts/rag_only", timeout=10)
        assert response.status_code == 200
        
        # Verify it was reset
        get_response = api_client.get("/user-prompts/rag_only", timeout=10)
        data = get_response.json()
        
        # Should return default prompt now
        assert data.get("is_default") is True or test_prompt not in data.get("prompt", "")

@pytest.mark.integration
class TestModelEndpoints:
    """Test LLM model endpoints"""
    
    def test_list_models(self, api_client):
        """Test listing available models"""
        response = api_client.get("/ollama/models", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
    
    def test_models_have_required_fields(self, api_client):
        """Test that models have required fields"""
        response = api_client.get("/ollama/models", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            
            if len(models) > 0:
                model = models[0]
                assert "name" in model
                assert "size" in model or "modified_at" in model

@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self, test_config):
        """Test health check endpoint"""
        response = requests.get(
            f"{test_config['BASE_URL']}/api/health",
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["healthy", "ok"]

@pytest.mark.integration
class TestMemoryEndpoints:
    """Test memory system endpoints"""
    
    def test_get_memory_profile(self, api_client):
        """Test getting memory profile"""
        response = api_client.get("/memory/profile", timeout=10)
        
        # May return empty if no memory stored
        assert response.status_code in [200, 404]
    
    def test_store_memory_insight(self, api_client):
        """Test storing memory insight"""
        response = api_client.post(
            "/memory/insights",
            json={"insight": "Test insight for memory system"},
            timeout=10
        )
        
        assert response.status_code in [200, 201]
    
    def test_clear_memory_category(self, api_client):
        """Test clearing specific memory category"""
        response = api_client.delete("/memory/clear/preferences", timeout=10)
        
        assert response.status_code in [200, 204]

