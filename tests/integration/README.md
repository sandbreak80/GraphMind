# Integration Tests - Real Ollama (No Mocks)

## Philosophy: NO MOCKS ALLOWED

These tests use **REAL services**:
- ✅ Real Ollama LLM at `http://ollama:11434` (Docker) or `http://localhost:11434` (host)
- ✅ Real backend at `http://graphmind-rag:8000` (Docker) or `http://localhost:8000` (host)
- ✅ Real frontend at `http://graphmind-frontend:3000` (Docker) or `http://localhost:3000` (host)
- ✅ Real authentication flow
- ✅ Real LLM responses

**Why?** Because mocking hides real bugs (like we just discovered).

## Running Tests

### From Host Machine
```bash
# Tests will use localhost ports
python3 -m pytest tests/integration/test_real_ollama_docker.py -v -s
```

### Inside Docker Container
```bash
# Tests will use Docker service names
docker exec graphmind-rag pytest /workspace/tests/integration/test_real_ollama_docker.py -v -s
```

## Test Structure

### 1. Frontend Integration Tests (✅ PASSING)
- `test_complete_user_flow_via_frontend()` - Full user flow: login → chat → response
- `test_multiple_chat_messages()` - Multiple messages in sequence
- `test_different_models()` - Test with different Ollama models

### 2. Prompt Uplift Tests
- `test_prompt_uplift_is_active()` - Verify prompt uplift metadata

### 3. Docker Health Checks
- `test_all_services_healthy()` - Verify all services reachable

## What These Tests Validate

✅ **Authentication**: Real login flow through frontend  
✅ **LLM Integration**: Real Ollama responses (no mocks)  
✅ **Frontend ↔ Backend**: Real API communication  
✅ **Prompt Uplift**: Feature actually working  
✅ **User Experience**: Complete end-to-end flow  

## Test Results

```
✅ test_complete_user_flow_via_frontend PASSED
   - Login successful
   - Chat message sent
   - Real LLM response: "The capital of France is Paris."
   - Prompt Uplift active
   - No errors!
```

## Key Lesson

**Never mock external services in integration tests!**

We had 91% unit test coverage with mocks, but **missed a critical auth bug** because:
1. Mocked LLM responses never tested real Ollama connectivity
2. Mocked auth never tested real token flow
3. Direct backend tests bypassed frontend proxy layer

The solution: **Test the real system, the way real users use it.**

## Coverage

These tests provide **real integration coverage** that unit tests cannot:
- Real network connectivity
- Real service-to-service communication
- Real authentication flows
- Real LLM responses
- Real error handling

This is **complementary** to unit tests, not a replacement.

