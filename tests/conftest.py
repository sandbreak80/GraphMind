"""
Pytest configuration and fixtures for GraphMind test suite
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
import time

# Test configuration
TEST_CONFIG = {
    "BASE_URL": os.getenv("TEST_BASE_URL", "http://localhost:3000"),
    "BACKEND_URL": os.getenv("TEST_BACKEND_URL", "http://localhost:8000"),
    "TEST_USER": {
        "username": "admin",
        "password": "admin123"
    },
    "TIMEOUT": 30,
    "API_TIMEOUT": 10,
}

@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def test_user():
    """Test user credentials"""
    return TEST_CONFIG["TEST_USER"]

@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture(scope="function")
def clean_memory_dir():
    """Clean memory storage directory for tests"""
    memory_dir = Path(tempfile.mkdtemp())
    yield memory_dir
    shutil.rmtree(memory_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def auth_token(test_config, test_user):
    """Get authentication token for API tests"""
    import requests
    
    try:
        response = requests.post(
            f"{test_config['BASE_URL']}/api/auth/login",
            data=test_user,
            timeout=test_config["API_TIMEOUT"]
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return token
        
        # Try backend directly
        response = requests.post(
            f"{test_config['BACKEND_URL']}/auth/login",
            data=test_user,
            timeout=test_config["API_TIMEOUT"]
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            return token
        
        pytest.skip("Cannot authenticate - backend not available")
        
    except Exception as e:
        pytest.skip(f"Cannot authenticate: {e}")

@pytest.fixture
def api_headers(auth_token):
    """Get API request headers with authentication"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture
def api_client(test_config, api_headers):
    """Create an authenticated API client"""
    import requests
    
    class APIClient:
        def __init__(self, base_url, headers):
            self.base_url = base_url
            self.headers = headers
            self.session = requests.Session()
            self.session.headers.update(headers)
        
        def get(self, endpoint, **kwargs):
            return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
        
        def post(self, endpoint, **kwargs):
            return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
        
        def put(self, endpoint, **kwargs):
            return self.session.put(f"{self.base_url}{endpoint}", **kwargs)
        
        def delete(self, endpoint, **kwargs):
            return self.session.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    return APIClient(test_config["BASE_URL"] + "/api", api_headers)

@pytest.fixture
def sample_document():
    """Sample document for testing"""
    return {
        "content": "This is a test document about trading strategies. "
                  "It contains information about risk management, entry and exit criteria, "
                  "and technical indicators like RSI and MACD.",
        "metadata": {
            "filename": "test_document.pdf",
            "doc_type": "trading_strategy",
            "page": 1
        }
    }

@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "What are the best trading strategies for momentum trading?"

@pytest.fixture
def sample_chat_messages():
    """Sample chat messages for testing"""
    return [
        {"role": "user", "content": "What is momentum trading?"},
        {"role": "assistant", "content": "Momentum trading is a strategy..."},
        {"role": "user", "content": "What indicators should I use?"},
    ]

# Markers for test categories
def pytest_configure(config):
    """Register custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for API endpoints"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests for user workflows"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "auth: Authentication and authorization tests"
    )
    config.addinivalue_line(
        "markers", "rag: RAG system tests"
    )
    config.addinivalue_line(
        "markers", "web: Web search tests"
    )
    config.addinivalue_line(
        "markers", "obsidian: Obsidian integration tests"
    )

# Auto-use fixtures
@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset test state before each test"""
    yield
    # Cleanup after test
    pass

