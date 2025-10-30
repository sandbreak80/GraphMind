#!/bin/bash

# Run tests with coverage inside Docker container
# This ensures proper code coverage measurement

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "GraphMind Coverage Test Suite"
echo -e "==========================================${NC}\n"

# Ensure container is running
if ! docker ps | grep -q graphmind-rag; then
    echo -e "${YELLOW}Starting backend container...${NC}"
    docker compose -f docker-compose.graphmind.yml up -d graphmind-rag
    sleep 10
fi

# Copy tests into container
echo -e "${YELLOW}Copying tests into container...${NC}"
docker cp tests/ graphmind-rag:/workspace/tests/
docker cp pytest.ini graphmind-rag:/workspace/
echo -e "${GREEN}✓ Tests copied${NC}\n"

# Install test dependencies in container
echo -e "${YELLOW}Installing test dependencies in container...${NC}"
docker exec graphmind-rag pip install -q pytest pytest-cov pytest-asyncio pytest-timeout 2>&1 | tail -5
echo -e "${GREEN}✓ Dependencies installed${NC}\n"

# Run unit tests with coverage
echo -e "${BLUE}=========================================="
echo "Running Unit Tests with Coverage"
echo -e "==========================================${NC}"

docker exec graphmind-rag bash -c "cd /workspace && pytest tests/unit/ -v --cov=app --cov-report=html --cov-report=term --cov-report=xml --tb=short || true"

# Copy coverage report out
echo -e "\n${YELLOW}Copying coverage reports...${NC}"
docker cp graphmind-rag:/workspace/htmlcov ./htmlcov/ 2>/dev/null || echo "HTML report not generated"
docker cp graphmind-rag:/workspace/coverage.xml ./coverage.xml 2>/dev/null || echo "XML report not generated"
docker cp graphmind-rag:/workspace/.coverage ./.coverage 2>/dev/null || echo "Coverage data not generated"

# Summary
echo -e "\n${BLUE}=========================================="
echo "Coverage Report Generated"
echo -e "==========================================${NC}"

if [ -d "htmlcov" ]; then
    echo -e "${GREEN}✓ HTML coverage report: htmlcov/index.html${NC}"
    echo -e "  View with: xdg-open htmlcov/index.html"
fi

if [ -f "coverage.xml" ]; then
    echo -e "${GREEN}✓ XML coverage report: coverage.xml${NC}"
fi

# Extract coverage percentage
if [ -f "htmlcov/index.html" ]; then
    COVERAGE=$(grep -oP '\d+%' htmlcov/index.html | head -1)
    echo -e "\n${BLUE}Total Coverage: ${COVERAGE}${NC}"
    
    # Parse percentage
    PERCENT=$(echo $COVERAGE | tr -d '%')
    if [ "$PERCENT" -ge 95 ]; then
        echo -e "${GREEN}🎉 Coverage target met! (>95%)${NC}"
    elif [ "$PERCENT" -ge 85 ]; then
        echo -e "${YELLOW}⚠️  Coverage acceptable but below target (85-95%)${NC}"
    else
        echo -e "${YELLOW}⚠️  Coverage below threshold (<85%)${NC}"
    fi
fi

echo -e "\n${GREEN}✓ Coverage tests completed${NC}\n"

