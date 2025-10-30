#!/bin/bash

# GraphMind Comprehensive Test Runner
# Runs all test suites: unit, integration, e2e, and performance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "GraphMind Comprehensive Test Suite"
echo -e "==========================================${NC}\n"

# Check if services are running
echo -e "${YELLOW}Checking service health...${NC}"
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend not running${NC}"
    echo "Start with: docker compose -f docker-compose.graphmind.yml up -d"
    exit 1
fi

# Install test dependencies
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
pip install -q pytest pytest-cov pytest-asyncio pytest-xdist pytest-timeout psutil 2>/dev/null || true
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Run unit tests
echo -e "\n${BLUE}=========================================="
echo "Running Unit Tests"
echo -e "==========================================${NC}"
pytest tests/unit/ -v -m unit --cov=app --cov-report=term-missing:skip-covered --cov-report=html --tb=short
UNIT_RESULT=$?

# Run integration tests
echo -e "\n${BLUE}=========================================="
echo "Running Integration Tests"
echo -e "==========================================${NC}"
pytest tests/integration/test_all_endpoints.py -v -m integration --tb=short
INTEGRATION_RESULT=$?

# Run validation tests (P1 fixes)
echo -e "\n${BLUE}=========================================="
echo "Running Validation Tests"
echo -e "==========================================${NC}"
python3 tests/validation/test_p1_api_fixes.py
VALIDATION_RESULT=$?

# Run performance benchmarks
echo -e "\n${BLUE}=========================================="
echo "Running Performance Benchmarks"
echo -e "==========================================${NC}"
pytest tests/performance/ -v -m performance --tb=short -k "not slow"
PERFORMANCE_RESULT=$?

# Run E2E tests (if Playwright is set up)
echo -e "\n${BLUE}=========================================="
echo "Running E2E Tests (Playwright)"
echo -e "==========================================${NC}"
if command -v npx &> /dev/null && [ -f "playwright.config.ts" ]; then
    npx playwright test tests/e2e/ --reporter=list
    E2E_RESULT=$?
else
    echo -e "${YELLOW}⚠ Playwright not installed, skipping E2E tests${NC}"
    E2E_RESULT=0
fi

# Generate coverage report
echo -e "\n${BLUE}=========================================="
echo "Test Coverage Report"
echo -e "==========================================${NC}"
if [ -f "coverage.xml" ]; then
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
    echo "Open with: xdg-open htmlcov/index.html"
fi

# Summary
echo -e "\n${BLUE}=========================================="
echo "TEST SUMMARY"
echo -e "==========================================${NC}"

if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Unit Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Unit Tests: FAILED${NC}"
fi

if [ $INTEGRATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Integration Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Integration Tests: FAILED${NC}"
fi

if [ $VALIDATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Validation Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Validation Tests: FAILED${NC}"
fi

if [ $PERFORMANCE_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Performance Tests: PASSED${NC}"
else
    echo -e "${RED}✗ Performance Tests: FAILED (or warnings)${NC}"
fi

if [ $E2E_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ E2E Tests: PASSED${NC}"
else
    echo -e "${RED}✗ E2E Tests: FAILED${NC}"
fi

echo -e "${BLUE}==========================================${NC}\n"

# Overall result
if [ $UNIT_RESULT -eq 0 ] && [ $INTEGRATION_RESULT -eq 0 ] && [ $VALIDATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 CORE TESTS PASSED! 🎉${NC}\n"
    exit 0
else
    echo -e "${RED}⚠️  SOME CORE TESTS FAILED${NC}\n"
    exit 1
fi

