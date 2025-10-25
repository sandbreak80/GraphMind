# TradingAI Research Platform Test Suite

Comprehensive testing framework for the TradingAI Research Platform API with support for multiple models and modes.

## Features

- **Multi-Model Testing**: Tests with 4 different Ollama models based on query complexity
- **Multi-Mode Testing**: Tests all API modes (QA, SPEC, WEB, RESEARCH)
- **Performance Metrics**: Detailed response time and success rate analysis
- **Flexible Configuration**: Support for different test types and configurations
- **Result Export**: JSON export of detailed test results
- **Automated Validation**: Automatic test validation with failure counting

## Test Models

| Complexity | Model | Description |
|------------|-------|-------------|
| Simple | `llama3.2:3b` | Small model for basic queries |
| Medium | `llama3.1:latest` | Medium model for intermediate queries |
| Complex | `qwen2.5-coder:14b` | Large model for complex queries |
| Research | `deepseek-r1:latest` | Thinking model for research queries |

## Test Modes

- **QA**: Standard question-answering mode
- **SPEC**: Specification extraction mode with top_k=10
- **WEB**: Web search enabled mode
- **RESEARCH**: Deep research mode

## Quick Start

### Prerequisites

1. Ensure the TradingAI Research Platform API is running on `http://localhost:8002`
2. Ensure Ollama is running with the required models
3. Install Python dependencies (requests)

### Running Tests

```bash
# Full comprehensive test (25 prompts, 4 modes, 4 models)
python3 run_tests.py --test-type full

# Quick test (10 prompts)
python3 run_tests.py --test-type quick

# Stress test (3 consecutive full tests)
python3 run_tests.py --test-type stress

# Model-specific test
python3 run_tests.py --test-type model --model llama3.2:3b

# Mode-specific test
python3 run_tests.py --test-type mode --mode qa

# Check system status
python3 run_tests.py --test-type status
```

### Using the Framework Directly

```python
from api_test_framework import APITestFramework

# Initialize framework
framework = APITestFramework()

# Run comprehensive test
results = framework.run_comprehensive_test()

# Print results
framework.print_results(results)

# Save results
framework.save_results(results, "my_test_results.json")
```

## Test Results

### Success Criteria

- **0 failed responses** = Test VALID
- **1+ failed responses** = Test INVALIDATED

### Metrics Tracked

- Total tests run
- Success/failure counts
- Response times (excluding cached)
- Cached response counts
- Performance by model
- Performance by mode
- Performance by complexity
- Error details for failures

### Output Files

Test results are automatically saved to JSON files in the `test_suite/` directory:

- `full_test_results_YYYYMMDD_HHMMSS.json`
- `quick_test_results.json`
- `model_test_MODELNAME_results.json`
- `mode_test_MODE_results.json`

## Configuration

### Customizing Test Prompts

Edit the `test_prompts` dictionary in `api_test_framework.py`:

```python
self.test_prompts = {
    "simple": [
        "Your simple prompts here",
        # ...
    ],
    "medium": [
        "Your medium prompts here",
        # ...
    ],
    # ...
}
```

### Customizing Models

Edit the `model_mapping` dictionary in `api_test_framework.py`:

```python
self.model_mapping = {
    "simple": "your-small-model",
    "medium": "your-medium-model",
    "complex": "your-large-model",
    "research": "your-thinking-model"
}
```

### Customizing API Settings

```python
framework = APITestFramework(
    base_url="http://your-api-url:port",
    username="your-username",
    password="your-password"
)
```

## Test Types

### 1. Full Test
- 25 prompts across 4 complexity levels
- 4 modes per prompt
- 4 different models
- Total: 100 tests
- Timeout: 60 seconds per request

### 2. Quick Test
- 10 prompts (reduced set)
- 4 modes per prompt
- 4 different models
- Total: 40 tests
- Timeout: 30 seconds per request

### 3. Stress Test
- 3 consecutive full tests
- Tests system stability under repeated load
- Total: 300 tests

### 4. Model-Specific Test
- Tests only one specific model
- All complexity levels and modes
- Useful for model comparison

### 5. Mode-Specific Test
- Tests only one specific mode
- All complexity levels and models
- Useful for mode validation

## Continuous Integration

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install requests
      - name: Start services
        run: |
          # Start your API and Ollama services
      - name: Run tests
        run: python3 test_suite/run_tests.py --test-type full
```

### Docker Integration

```dockerfile
FROM python:3.8-slim
COPY test_suite/ /app/test_suite/
WORKDIR /app
RUN pip install requests
CMD ["python3", "test_suite/run_tests.py", "--test-type", "full"]
```

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check if API is running on correct port
   - Verify username/password credentials

2. **Model Not Found**
   - Ensure Ollama is running
   - Check if required models are pulled: `docker exec ollama ollama list`

3. **Timeout Errors**
   - Increase timeout value
   - Check system resources (GPU memory, CPU)

4. **Empty Responses**
   - Check API logs for errors
   - Verify model is responding correctly

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Add new test cases to the appropriate complexity level
2. Update model mappings as needed
3. Add new test types in `run_tests.py`
4. Update documentation

## License

This test suite is part of the TradingAI Research Platform project.