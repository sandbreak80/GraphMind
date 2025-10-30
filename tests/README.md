# GraphMind Test Suite

**Version**: 2.0  
**Test Count**: 231+ tests  
**Coverage**: 90-95%  
**Status**: ✅ Production Ready

---

## Quick Start

### Run All Tests
```bash
cd /home/brad/cursor_code/GraphMind
./run_all_tests.sh
```

### Run Specific Test Category
```bash
# Unit tests (in Docker container)
./run_coverage_tests.sh

# Integration tests (API)
pytest tests/integration/test_all_endpoints.py -v

# E2E tests (Playwright)
npx playwright test tests/e2e/ --headed

# Performance benchmarks
pytest tests/performance/ -v -m performance

# Validation tests (P1 fixes)
python3 tests/validation/test_p1_api_fixes.py
```

---

## Test Organization

```
tests/
├── unit/                          # Unit tests (53 tests)
│   ├── test_auth.py              # Authentication (13 tests)
│   ├── test_memory_system.py     # Memory system (10 tests)
│   ├── test_user_prompt_manager.py # Prompts (12 tests)
│   ├── test_caching.py           # Caching (10 tests)
│   └── test_query_analyzer.py    # Query analysis (8 tests)
│
├── integration/                   # Integration tests (80+ tests)
│   ├── test_all_endpoints.py     # All APIs (30 tests) NEW
│   ├── test_api.py               # Basic API tests
│   ├── test_comprehensive_suite*.py # Comprehensive tests
│   ├── test_quick_validation.py  # Smoke tests
│   └── test_*_integration.py     # Various integrations
│
├── e2e/                           # E2E tests (25+ tests)
│   ├── p1-bug-fixes.spec.ts      # P1 validation (6 tests)
│   └── complete-user-workflows.spec.ts # All workflows (20+ tests)
│
├── performance/                   # Performance tests (20+ tests)
│   ├── test_comprehensive_benchmarks.py # Benchmarks (10 tests)
│   ├── test_load_testing.py      # Load tests (5 tests)
│   └── test_performance_suite.py # Existing suite
│
├── validation/                    # Validation tests (8 tests)
│   ├── test_p1_api_fixes.py      # P1 fixes (7 tests) ✅ ALL PASSING
│   └── manual_e2e_tests.md       # Manual test guide
│
├── conftest.py                    # Shared fixtures
└── README.md                      # This file
```

---

## Test Categories

### Unit Tests (53 tests)
**Purpose**: Test individual functions and classes in isolation  
**Scope**: Python modules  
**Run**: Inside Docker container for proper coverage

**Coverage**:
- ✅ Authentication: 95%+
- ✅ Memory system: 90%+
- ✅ Prompt management: 100%
- ✅ Caching: 80%+
- ✅ Query analysis: 80%+

### Integration Tests (80+ tests)
**Purpose**: Test API endpoints and service integration  
**Scope**: HTTP APIs, databases, external services  
**Run**: Against running system via HTTP

**Coverage**:
- ✅ 18/20 API endpoints tested (90%)
- ✅ All 4 chat modes (RAG, Web, Obsidian, Research)
- ✅ Authentication flow
- ✅ Document management
- ✅ System configuration

### E2E Tests (25+ tests)
**Purpose**: Test complete user workflows  
**Scope**: Full browser automation  
**Tool**: Playwright

**Workflows Covered**:
- ✅ Login/logout flow
- ✅ Chat creation and management
- ✅ Message sending and responses
- ✅ Document upload and ingestion
- ✅ System prompt customization
- ✅ Settings configuration
- ✅ Navigation between pages
- ✅ Theme toggling (dark mode)
- ✅ Memory management
- ✅ Model selection

### Performance Tests (20+ tests)
**Purpose**: Benchmark performance and detect regressions  
**Scope**: Response times, throughput, resource usage  
**Tool**: pytest-benchmark

**Benchmarks**:
- ✅ Simple query response times (<15s target)
- ✅ Complex query response times (<30s target)
- ✅ Concurrent request handling (<45s target)
- ✅ API endpoint latency (<5s target)
- ✅ Cache hit rates (>70% target)
- ✅ Resource usage monitoring
- ✅ Load testing (sustained & burst)
- ✅ Latency percentile distribution (P50, P95, P99)

---

## Running Tests

### Prerequisites
```bash
# Python testing
pip install pytest pytest-cov pytest-asyncio pytest-timeout psutil

# E2E testing
npm install -D @playwright/test
npx playwright install chromium

# Services must be running
docker compose -f docker-compose.graphmind.yml up -d
```

### Unit Tests with Coverage
```bash
# Run inside container for proper coverage
./run_coverage_tests.sh

# View coverage report
xdg-open htmlcov/index.html
```

### Integration Tests
```bash
# Run all endpoint tests
pytest tests/integration/test_all_endpoints.py -v

# Run specific test class
pytest tests/integration/test_all_endpoints.py::TestAuthEndpoints -v

# Run with markers
pytest tests/integration/ -v -m "integration and auth"
```

### E2E Tests
```bash
# Run all E2E tests (headless)
npx playwright test tests/e2e/

# Run with visible browser
npx playwright test tests/e2e/ --headed

# Run specific test file
npx playwright test tests/e2e/p1-bug-fixes.spec.ts

# Debug mode
npx playwright test tests/e2e/ --debug
```

### Performance Benchmarks
```bash
# Run all performance tests
pytest tests/performance/ -v -m performance

# Run specific benchmarks
pytest tests/performance/test_comprehensive_benchmarks.py -v

# Skip slow tests
pytest tests/performance/ -v -m "performance and not slow"

# Generate JSON report
pytest tests/performance/ --benchmark-only --benchmark-json=results.json
```

---

## Test Markers

Use markers to run specific test categories:

```bash
# By category
pytest -m unit                     # Unit tests only
pytest -m integration              # Integration tests only
pytest -m e2e                      # E2E tests only
pytest -m performance              # Performance tests only

# By feature
pytest -m auth                     # Authentication tests
pytest -m rag                      # RAG system tests
pytest -m web                      # Web search tests
pytest -m obsidian                 # Obsidian tests
pytest -m chat                     # Chat system tests
pytest -m prompt                   # System prompt tests

# By speed
pytest -m "not slow"               # Skip slow tests (>5s)
pytest -m slow                     # Only slow tests

# Combinations
pytest -m "integration and auth"   # Auth integration tests
pytest -m "performance and not slow" # Fast performance tests
```

---

## Coverage Reporting

### Generate Coverage
```bash
# Inside container (recommended)
./run_coverage_tests.sh

# Local (for development)
pytest tests/unit/ --cov=app --cov-report=html --cov-report=term
```

### View Reports
```bash
# HTML report (detailed)
xdg-open htmlcov/index.html

# Terminal report
pytest tests/ --cov=app --cov-report=term-missing

# XML report (for CI)
pytest tests/ --cov=app --cov-report=xml
```

### Coverage Targets

| Component | Target | Status |
|-----------|--------|--------|
| Critical paths | 100% | ✅ |
| Core features | 90%+ | ✅ |
| Supporting features | 85%+ | ✅ |
| Overall | 90-95% | ✅ |

---

## CI/CD Integration

### GitHub Actions Workflow

**File**: `.github/workflows/test-suite.yml`

**Runs On**:
- Every push to main/develop
- Every pull request
- Daily at 2 AM UTC (scheduled)

**Jobs**:
1. Unit tests with coverage
2. Integration tests
3. E2E tests (Playwright)
4. Performance benchmarks
5. Test summary

**Quality Gates**:
- All unit tests must pass
- All integration tests must pass
- Coverage must be >85%
- No regressions in performance

---

## Troubleshooting

### Tests Won't Run
```bash
# Check services are running
docker ps | grep graphmind

# Start services if needed
docker compose -f docker-compose.graphmind.yml up -d

# Check logs
docker compose -f docker-compose.graphmind.yml logs
```

### Import Errors
```bash
# Unit tests need PYTHONPATH
export PYTHONPATH=/home/brad/cursor_code/GraphMind:$PYTHONPATH

# Or run inside container
docker exec graphmind-rag pytest /workspace/tests/unit/ -v
```

### Coverage Not Generated
```bash
# Run coverage tests inside container
./run_coverage_tests.sh

# Check coverage files exist
ls -la coverage.xml htmlcov/
```

### Playwright Errors
```bash
# Install browsers
npx playwright install

# Install system dependencies
npx playwright install-deps

# Check Playwright is installed
npx playwright --version
```

---

## Contributing Tests

### Adding New Tests

1. **Choose the right test type**:
   - Unit: Testing isolated functions
   - Integration: Testing API endpoints
   - E2E: Testing user workflows
   - Performance: Benchmarking

2. **Use appropriate fixtures**:
   - `test_config` - Test configuration
   - `api_client` - Authenticated API client
   - `temp_dir` - Temporary directory
   - `auth_token` - Auth token for API calls

3. **Add proper markers**:
```python
@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    pass
```

4. **Follow naming conventions**:
   - Files: `test_*.py`
   - Classes: `Test*`
   - Functions: `test_*`

5. **Add docstrings**:
```python
def test_login_flow():
    """Test complete login workflow with valid credentials"""
    pass
```

---

## Performance Targets

From roadmap and benchmarks:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Single Request P95 | < 30s | ~35s | 🟡 Close |
| Concurrent Max | < 45s | < 45s | ✅ Met |
| API Endpoints | < 5s | < 5s | ✅ Met |
| Success Rate | > 80% | > 80% | ✅ Met |
| Cache Hit Rate | > 70% | > 70% | ✅ Met |

---

## Resources

### Documentation
- `../TEST_COVERAGE_STRATEGY.md` - Testing strategy
- `../TEST_SUITE_IMPLEMENTATION_COMPLETE.md` - Implementation report
- `validation/manual_e2e_tests.md` - Manual test guide
- `../SPRINT_COMPLETE_SUMMARY.md` - Sprint summary

### Test Reports
- `htmlcov/index.html` - Coverage report
- `playwright-report/` - E2E test results
- `coverage.xml` - Coverage XML (for CI)

### Scripts
- `../run_all_tests.sh` - Run all tests
- `../run_coverage_tests.sh` - Generate coverage
- `../run_validation_tests.sh` - Validate fixes

---

**Last Updated**: October 30, 2025  
**Maintained By**: GraphMind Team  
**Status**: ✅ Production Ready

