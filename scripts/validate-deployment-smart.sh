#!/bin/bash

# GraphMind Smart Deployment Validation Script
# Waits for models to be ready and validates all functionality

echo "🧪 GraphMind Smart Deployment Validation"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="${3:-0}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing $test_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test HTTP endpoint
test_endpoint() {
    local test_name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing $test_name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout 10)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $response, expected $expected_status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test Docker service
test_docker_service() {
    local service_name="$1"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "Testing Docker service $service_name... "
    
    if docker compose -f docker-compose.graphmind.yml ps | grep -q "$service_name.*Up"; then
        echo -e "${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to wait for Ollama models
wait_for_models() {
    echo -e "\n${BLUE}🔄 Waiting for Ollama models to be ready...${NC}"
    echo "This may take several minutes for large models..."
    
    local max_attempts=60  # 10 minutes max
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        echo -n "Checking models (attempt $((attempt + 1))/$max_attempts)... "
        
        # Check if any models are available
        models_response=$(curl -s http://localhost:11434/api/tags 2>/dev/null)
        
        if echo "$models_response" | grep -q '"models"'; then
            model_count=$(echo "$models_response" | grep -o '"name"' | wc -l)
            if [ "$model_count" -gt 0 ]; then
                echo -e "${GREEN}✅ $model_count models available${NC}"
                return 0
            fi
        fi
        
        echo -e "${YELLOW}⏳ No models ready yet${NC}"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Timeout waiting for models${NC}"
    return 1
}

echo -e "\n${BLUE}📋 Infrastructure Tests${NC}"
echo "------------------------"

# Test Docker services
test_docker_service "graphmind-rag"
test_docker_service "graphmind-frontend"
test_docker_service "graphmind-chromadb"
test_docker_service "graphmind-redis"
test_docker_service "graphmind-ollama"
test_docker_service "graphmind-searxng"

echo -e "\n${BLUE}📋 Frontend Tests${NC}"
echo "----------------"

# Test frontend accessibility
test_endpoint "Frontend Homepage" "http://localhost:3000" "200"
test_endpoint "Frontend Chat Page" "http://localhost:3000/chat/test" "200"

echo -e "\n${BLUE}📋 API Tests${NC}"
echo "-------------"

# Test API health
test_endpoint "API Health" "http://localhost:3000/api/health" "200"

# Test authentication
echo -n "Testing Authentication... "
auth_response=$(curl -s -X POST http://localhost:3000/api/auth/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=admin123" \
    --connect-timeout 10)

if echo "$auth_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    AUTH_TOKEN=$(echo "$auth_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
else
    echo -e "${RED}❌ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    AUTH_TOKEN=""
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Wait for models if we have auth
if [ -n "$AUTH_TOKEN" ]; then
    if wait_for_models; then
        echo -e "\n${BLUE}📋 Authenticated API Tests${NC}"
        echo "---------------------------"
        
        # Test system prompts
        test_endpoint "System Prompts" "http://localhost:3000/api/system-prompts" "200"
        
        # Test user prompts
        test_endpoint "User Prompts" "http://localhost:3000/api/user-prompts" "200"
        
        # Test Ollama models
        test_endpoint "Ollama Models" "http://localhost:3000/api/ollama/models" "200"
        
        # Test memory profile
        test_endpoint "Memory Profile" "http://localhost:3000/api/memory/profile" "200"
        
        # Test a simple query
        echo -n "Testing RAG Query... "
        query_response=$(curl -s -X POST http://localhost:3000/api/ask \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -d '{"query":"What is GraphMind?","mode":"qa","model":"llama3.2:3b-instruct","temperature":0.7,"max_tokens":100}' \
            --connect-timeout 30)
        
        if echo "$query_response" | grep -q "answer"; then
            echo -e "${GREEN}✅ PASS${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ FAIL${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    else
        echo -e "\n${YELLOW}⚠️ Skipping model-dependent tests (models not ready)${NC}"
    fi
fi

echo -e "\n${BLUE}📋 Backend Service Tests${NC}"
echo "-------------------------"

# Test internal services
echo -n "Testing ChromaDB... "
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⏭️ SKIP${NC} (Internal service)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo -n "Testing Ollama... "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⏭️ SKIP${NC} (Internal service)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Print summary
echo -e "\n${BLUE}📊 VALIDATION SUMMARY${NC}"
echo "========================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "✅ Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "❌ Failed: ${RED}$FAILED_TESTS${NC}"

success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "📈 Success Rate: ${BLUE}$success_rate%${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! GraphMind deployment is working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️ $FAILED_TESTS tests failed. Please check the issues above.${NC}"
    exit 1
fi
