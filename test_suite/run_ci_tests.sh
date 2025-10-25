#!/bin/bash
# Continuous Integration Test Script for TradingAI Research Platform

set -e  # Exit on any error

echo "🧪 TradingAI Research Platform CI Tests"
echo "========================================"
echo "Started at: $(date)"
echo

# Configuration
API_URL="http://localhost:8002"
TIMEOUT=300  # 5 minutes for full test
LOG_DIR="test_suite/logs"
RESULTS_DIR="test_suite/results"

# Create directories
mkdir -p "$LOG_DIR"
mkdir -p "$RESULTS_DIR"

# Function to check if API is ready
check_api_ready() {
    echo "🔍 Checking API readiness..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
            echo "✅ API is ready"
            return 0
        fi
        
        echo "⏳ Attempt $attempt/$max_attempts - API not ready, waiting..."
        sleep 10
        ((attempt++))
    done
    
    echo "❌ API not ready after $max_attempts attempts"
    return 1
}

# Function to check Ollama models
check_ollama_models() {
    echo "🔍 Checking Ollama models..."
    
    local required_models=("llama3.2:3b" "llama3.1:latest" "qwen2.5-coder:14b" "deepseek-r1:latest")
    
    for model in "${required_models[@]}"; do
        if docker exec ollama ollama list | grep -q "$model"; then
            echo "✅ Model $model is available"
        else
            echo "❌ Model $model is missing"
            echo "Pulling model $model..."
            docker exec ollama ollama pull "$model"
        fi
    done
}

# Function to run test with timeout and logging
run_test() {
    local test_type="$1"
    local log_file="$LOG_DIR/${test_type}_$(date +%Y%m%d_%H%M%S).log"
    local result_file="$RESULTS_DIR/${test_type}_$(date +%Y%m%d_%H%M%S).json"
    
    echo "🚀 Running $test_type test..."
    echo "Log file: $log_file"
    echo "Result file: $result_file"
    
    if timeout $TIMEOUT python3 test_suite/run_tests.py --test-type "$test_type" --output "$result_file" > "$log_file" 2>&1; then
        echo "✅ $test_type test passed"
        return 0
    else
        local exit_code=$?
        echo "❌ $test_type test failed (exit code: $exit_code)"
        echo "Last 20 lines of log:"
        tail -20 "$log_file"
        return $exit_code
    fi
}

# Function to generate test report
generate_report() {
    local report_file="$RESULTS_DIR/test_report_$(date +%Y%m%d_%H%M%S).md"
    
    echo "📊 Generating test report..."
    
    cat > "$report_file" << EOF
# Test Report - $(date)

## Test Summary
- **Date**: $(date)
- **API URL**: $API_URL
- **Test Duration**: $(($(date +%s) - START_TIME)) seconds

## Test Results

EOF

    # Add results for each test type
    for result_file in "$RESULTS_DIR"/*.json; do
        if [ -f "$result_file" ]; then
            local test_name=$(basename "$result_file" .json)
            echo "### $test_name" >> "$report_file"
            
            # Extract key metrics from JSON
            if command -v jq > /dev/null; then
                echo "**Summary:**" >> "$report_file"
                jq -r '.summary | "  - Total Tests: \(.total_tests)\n  - Successful: \(.successful_tests)\n  - Failed: \(.failed_tests)\n  - Success Rate: \(.success_rate)%\n  - Avg Response Time: \(.average_response_time)s"' "$result_file" >> "$report_file"
            else
                echo "  - Results available in: $result_file" >> "$report_file"
            fi
            echo "" >> "$report_file"
        fi
    done
    
    echo "📄 Test report generated: $report_file"
}

# Main execution
START_TIME=$(date +%s)

echo "🔧 Pre-test setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
fi

# Check if Ollama container is running
if ! docker ps | grep -q ollama; then
    echo "❌ Ollama container is not running"
    exit 1
fi

# Check API readiness
if ! check_api_ready; then
    echo "❌ API is not ready, aborting tests"
    exit 1
fi

# Check Ollama models
check_ollama_models

echo
echo "🧪 Starting test suite..."

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Run different test types
test_types=("status" "quick" "full")

for test_type in "${test_types[@]}"; do
    echo
    echo "--- Running $test_type test ---"
    
    if run_test "$test_type"; then
        ((PASSED_TESTS++))
    else
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
done

# Generate final report
echo
echo "📊 Test Suite Summary"
echo "===================="
echo "Total test types: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo "Success rate: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"

# Generate detailed report
generate_report

# Final result
if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ $FAILED_TESTS test type(s) failed"
    exit 1
fi