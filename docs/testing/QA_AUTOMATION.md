# QA Automation Documentation

## Overview

This document outlines the comprehensive QA automation strategy for the EminiPlayer application, including automated testing, continuous integration, and quality assurance processes.

## Current Testing Infrastructure

### Existing Test Files
- `tests/integration/test_comprehensive_suite.py` - Full test suite
- `tests/integration/test_quick_validation.py` - Quick validation
- `tests/integration/test_api.py` - API endpoint tests
- `tests/integration/test_obsidian_*.py` - Obsidian integration tests
- `tests/integration/test_*.py` - Various component tests

### Test Categories
1. **Unit Tests** - Individual component testing
2. **Integration Tests** - API and service integration
3. **End-to-End Tests** - Full user workflow testing
4. **Performance Tests** - Response time and load testing
5. **Security Tests** - Authentication and data protection

## QA Automation Strategy

### 1. Automated Test Execution
**Trigger**: Every code change, pull request, and deployment
**Scope**: Full test suite execution
**Reporting**: Automated test result reporting

### 2. Continuous Integration
**Platform**: GitHub Actions
**Workflow**: Automated build, test, and deployment
**Quality Gates**: Tests must pass before merge/deployment

### 3. Test Coverage
**Target**: >80% code coverage
**Monitoring**: Continuous coverage tracking
**Reporting**: Coverage reports for each change

## Implementation Plan

### Phase 1: Test Infrastructure Setup
1. **GitHub Actions Workflow**
   - Automated test execution
   - Build and deployment
   - Test result reporting

2. **Test Environment**
   - Docker-based test environment
   - Isolated test database
   - Mock external services

3. **Test Data Management**
   - Test data fixtures
   - Data cleanup procedures
   - Test data isolation

### Phase 2: Test Suite Enhancement
1. **Expand Test Coverage**
   - Add missing test cases
   - Improve test quality
   - Add edge case testing

2. **Performance Testing**
   - Response time testing
   - Load testing
   - Stress testing

3. **Security Testing**
   - Authentication testing
   - Authorization testing
   - Data protection testing

### Phase 3: Advanced QA Features
1. **Test Analytics**
   - Test performance metrics
   - Failure analysis
   - Trend monitoring

2. **Quality Gates**
   - Automated quality checks
   - Performance benchmarks
   - Security scans

3. **Reporting and Notifications**
   - Test result notifications
   - Quality dashboards
   - Alert systems

## Test Suite Structure

### 1. Unit Tests (`tests/unit/`)
```
tests/unit/
├── test_auth.py
├── test_memory_system.py
├── test_retrieval.py
├── test_web_search.py
├── test_obsidian_client.py
└── test_models.py
```

### 2. Integration Tests (`tests/integration/`)
```
tests/integration/
├── test_api_endpoints.py
├── test_chat_modes.py
├── test_data_sources.py
├── test_memory_integration.py
├── test_model_switching.py
└── test_export_functionality.py
```

### 3. End-to-End Tests (`tests/e2e/`)
```
tests/e2e/
├── test_user_workflows.py
├── test_chat_scenarios.py
├── test_memory_management.py
├── test_export_workflows.py
└── test_performance_scenarios.py
```

### 4. Performance Tests (`tests/performance/`)
```
tests/performance/
├── test_response_times.py
├── test_load_testing.py
├── test_memory_usage.py
└── test_concurrent_users.py
```

## GitHub Actions Workflow

### 1. Main Workflow (`.github/workflows/main.yml`)
```yaml
name: EminiPlayer QA Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10]
        node-version: [18]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        cd frontend && npm install
    
    - name: Start services
      run: |
        docker-compose up -d
        sleep 30  # Wait for services to start
    
    - name: Run unit tests
      run: |
        python -m pytest tests/unit/ -v --cov=app --cov-report=xml
    
    - name: Run integration tests
      run: |
        python -m pytest tests/integration/ -v
    
    - name: Run e2e tests
      run: |
        python -m pytest tests/e2e/ -v
    
    - name: Run performance tests
      run: |
        python -m pytest tests/performance/ -v
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: test-results/
```

### 2. Security Workflow (`.github/workflows/security.yml`)
```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r app/
    
    - name: Run dependency scan
      run: |
        pip install pip-audit
        pip-audit
```

## Test Configuration

### 1. Pytest Configuration (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
    auth: Authentication tests
    memory: Memory system tests
    chat: Chat system tests
```

### 2. Test Environment Configuration
```python
# tests/conftest.py
import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///test.db",
        "MEMORY_STORAGE_DIR": tempfile.mkdtemp(),
        "OLLAMA_URL": "http://localhost:11434",
        "SEARXNG_URL": "http://localhost:8888"
    }

@pytest.fixture(scope="function")
def clean_memory():
    """Clean memory storage before each test"""
    memory_dir = Path(tempfile.mkdtemp())
    yield memory_dir
    # Cleanup after test
    import shutil
    shutil.rmtree(memory_dir, ignore_errors=True)
```

## Test Categories and Examples

### 1. Unit Tests
```python
# tests/unit/test_memory_system.py
import pytest
from app.memory_system import UserMemory

class TestUserMemory:
    def test_store_preference(self, clean_memory):
        memory = UserMemory(storage_dir=str(clean_memory))
        result = memory.store_preference("user123", "model", "qwen2.5-coder:14b")
        assert result is True
        
        value = memory.get_preference("user123", "model")
        assert value == "qwen2.5-coder:14b"
    
    def test_get_nonexistent_preference(self, clean_memory):
        memory = UserMemory(storage_dir=str(clean_memory))
        value = memory.get_preference("user123", "nonexistent", "default")
        assert value == "default"
```

### 2. Integration Tests
```python
# tests/integration/test_chat_modes.py
import pytest
import requests

class TestChatModes:
    def test_rag_only_mode(self, auth_token):
        response = requests.post(
            "http://localhost:3001/api/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "request": {
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "citations" in data
        assert all(c["section"] in ["pdf", "video_transcript", "llm_processed"] 
                  for c in data["citations"])
    
    def test_web_search_only_mode(self, auth_token):
        response = requests.post(
            "http://localhost:3001/api/ask-enhanced",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "request": {
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "citations" in data
        assert not any(c["section"] in ["pdf", "video_transcript", "llm_processed"] 
                      for c in data["citations"])
```

### 3. End-to-End Tests
```python
# tests/e2e/test_user_workflows.py
import pytest
import requests
import time

class TestUserWorkflows:
    def test_complete_chat_workflow(self, auth_token):
        # Create new chat
        chat_response = requests.post(
            "http://localhost:3001/api/chats",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Test Chat"}
        )
        assert chat_response.status_code == 201
        chat_id = chat_response.json()["id"]
        
        # Send message
        message_response = requests.post(
            f"http://localhost:3001/api/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "content": "What is trading?",
                "role": "user"
            }
        )
        assert message_response.status_code == 201
        
        # Get response
        response = requests.post(
            "http://localhost:3001/api/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "request": {
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            }
        )
        assert response.status_code == 200
        
        # Export chat
        export_response = requests.post(
            f"http://localhost:3001/api/chats/{chat_id}/export",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert export_response.status_code == 200
        assert "markdown" in export_response.json()
```

### 4. Performance Tests
```python
# tests/performance/test_response_times.py
import pytest
import requests
import time
import statistics

class TestResponseTimes:
    def test_rag_mode_response_time(self, auth_token):
        """Test RAG mode response time is under 30 seconds"""
        start_time = time.time()
        response = requests.post(
            "http://localhost:3001/api/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "request": {
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3
                }
            }
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 30.0
    
    def test_average_response_times(self, auth_token):
        """Test average response times across multiple requests"""
        response_times = []
        
        for _ in range(5):
            start_time = time.time()
            response = requests.post(
                "http://localhost:3001/api/ask",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={
                    "request": {
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 3
                    }
                }
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        assert len(response_times) == 5
        avg_time = statistics.mean(response_times)
        assert avg_time < 25.0  # Average should be under 25 seconds
```

## Cursor Rules for QA Automation

### 1. Cursor Rules File (`.cursorrules`)
```
# EminiPlayer QA Automation Rules

## Test Requirements
- All new features must include unit tests
- All API changes must include integration tests
- All user workflows must include e2e tests
- Test coverage must be >80%
- All tests must pass before merge

## Test Execution
- Run tests automatically on every change
- Run full test suite on pull requests
- Run performance tests on main branch
- Run security scans on all changes

## Test Quality
- Tests must be deterministic and reliable
- Tests must clean up after themselves
- Tests must not depend on external services
- Tests must be fast and efficient

## Test Documentation
- All test files must have docstrings
- Complex test logic must be commented
- Test data must be clearly documented
- Test failures must be actionable

## Automated Actions
- On code change: Run unit tests
- On pull request: Run full test suite
- On merge to main: Run performance tests
- On deployment: Run security scans
- On test failure: Block merge/deployment
```

### 2. Pre-commit Hooks (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [tests/unit/, -v]
      
      - id: flake8
        name: flake8
        entry: flake8
        language: system
        files: \.py$
        args: [app/, tests/]
      
      - id: black
        name: black
        entry: black
        language: system
        files: \.py$
        args: [--check, app/, tests/]
```

## Monitoring and Reporting

### 1. Test Metrics Dashboard
- Test execution time
- Test pass/fail rates
- Code coverage trends
- Performance benchmarks
- Security scan results

### 2. Automated Notifications
- Test failure alerts
- Coverage drop notifications
- Performance regression alerts
- Security vulnerability alerts

### 3. Quality Gates
- Minimum test coverage: 80%
- Maximum response time: 30 seconds
- Zero security vulnerabilities
- All tests must pass

## Maintenance and Updates

### 1. Regular Updates
- Update test dependencies monthly
- Review and update test cases quarterly
- Performance benchmark updates
- Security scan updates

### 2. Test Maintenance
- Remove obsolete tests
- Update test data
- Optimize slow tests
- Improve test reliability

### 3. Documentation Updates
- Update test documentation
- Maintain test guides
- Update QA procedures
- Document new test patterns

## Future Enhancements

### Short-term (1-2 months)
- Complete test infrastructure setup
- Implement all test categories
- Set up automated reporting
- Add performance monitoring

### Medium-term (3-6 months)
- Advanced test analytics
- AI-powered test generation
- Advanced performance testing
- Security automation

### Long-term (6+ months)
- Predictive testing
- Advanced quality gates
- Automated test optimization
- Full CI/CD integration