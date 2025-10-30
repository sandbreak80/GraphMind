#!/bin/bash

# P1 Bug Fixes Validation Test Runner
# This script runs both API and E2E tests to validate the fixes

set -e

echo "=========================================="
echo "P1 Bug Fixes - Validation Test Suite"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo "Checking if services are running..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${RED}✗ Frontend not running on port 3000${NC}"
    echo "Please start the frontend: cd frontend && npm run dev"
    exit 1
fi
echo -e "${GREEN}✓ Frontend is running${NC}"

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}⚠ Backend not responding on port 8000${NC}"
    echo "Trying to connect via Docker..."
fi
echo ""

# Run API validation tests
echo "=========================================="
echo "Running API Validation Tests (Python)"
echo "=========================================="
python3 tests/validation/test_p1_api_fixes.py
API_TEST_RESULT=$?
echo ""

# Install Playwright if needed
if ! command -v npx playwright &> /dev/null; then
    echo "Installing Playwright..."
    npm install -D @playwright/test
    npx playwright install chromium
fi

# Run E2E tests
echo "=========================================="
echo "Running E2E Tests (Playwright)"
echo "=========================================="
npx playwright test tests/e2e/p1-bug-fixes.spec.ts --reporter=list
E2E_TEST_RESULT=$?
echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
if [ $API_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ API Tests: PASSED${NC}"
else
    echo -e "${RED}✗ API Tests: FAILED${NC}"
fi

if [ $E2E_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ E2E Tests: PASSED${NC}"
else
    echo -e "${RED}✗ E2E Tests: FAILED${NC}"
fi
echo "=========================================="

if [ $API_TEST_RESULT -eq 0 ] && [ $E2E_TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! 🎉${NC}"
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi

