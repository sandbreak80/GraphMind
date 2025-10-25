#!/bin/bash

# GraphMind Deployment Test Runner
# Comprehensive test suite for deployment validation

set -e  # Exit on any error

echo "🧪 GraphMind Deployment Test Suite"
echo "=================================="

# Configuration
BASE_URL="${FRONTEND_URL:-http://localhost:3000}"
API_URL="${API_URL:-http://localhost:3000/api}"
OUTPUT_DIR="${TEST_OUTPUT_DIR:-./test-results}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📋 Test Configuration:"
echo "  Frontend URL: $BASE_URL"
echo "  API URL: $API_URL"
echo "  Output Directory: $OUTPUT_DIR"
echo "  Timestamp: $TIMESTAMP"
echo ""

# Function to run test and capture output
run_test_suite() {
    local test_name="$1"
    local test_script="$2"
    local output_file="$OUTPUT_DIR/${test_name}_${TIMESTAMP}.json"
    
    echo "🔍 Running $test_name..."
    
    if [ -f "$test_script" ]; then
        if python3 "$test_script" --base-url "$BASE_URL" --api-url "$API_URL" --output "$output_file"; then
            echo "✅ $test_name completed successfully"
            return 0
        else
            echo "❌ $test_name failed"
            return 1
        fi
    else
        echo "⚠️ $test_name script not found: $test_script"
        return 1
    fi
}

# Function to run shell-based tests
run_shell_test() {
    local test_name="$1"
    local test_script="$2"
    local output_file="$OUTPUT_DIR/${test_name}_${TIMESTAMP}.log"
    
    echo "🔍 Running $test_name..."
    
    if [ -f "$test_script" ]; then
        if bash "$test_script" > "$output_file" 2>&1; then
            echo "✅ $test_name completed successfully"
            return 0
        else
            echo "❌ $test_name failed"
            return 1
        fi
    else
        echo "⚠️ $test_name script not found: $test_script"
        return 1
    fi
}

# Track test results
TOTAL_SUITES=0
PASSED_SUITES=0
FAILED_SUITES=0

# Test suites to run
echo "🚀 Starting test execution..."
echo ""

# 1. Quick validation test
TOTAL_SUITES=$((TOTAL_SUITES + 1))
if run_shell_test "quick_validation" "scripts/validate-deployment.sh"; then
    PASSED_SUITES=$((PASSED_SUITES + 1))
else
    FAILED_SUITES=$((FAILED_SUITES + 1))
fi

# 2. Comprehensive deployment validation
TOTAL_SUITES=$((TOTAL_SUITES + 1))
if run_test_suite "deployment_validation" "tests/deployment/test_deployment_validation.py"; then
    PASSED_SUITES=$((PASSED_SUITES + 1))
else
    FAILED_SUITES=$((FAILED_SUITES + 1))
fi

# 3. API integration tests (if they exist)
if [ -f "tests/integration/test_api_integration.py" ]; then
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    if run_test_suite "api_integration" "tests/integration/test_api_integration.py"; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
    fi
fi

# 4. Performance tests (if they exist)
if [ -f "tests/performance/test_performance_suite.py" ]; then
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    if run_test_suite "performance" "tests/performance/test_performance_suite.py"; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
    fi
fi

# 5. Security tests (if they exist)
if [ -f "tests/security/test_security_suite.py" ]; then
    TOTAL_SUITES=$((TOTAL_SUITES + 1))
    if run_test_suite "security" "tests/security/test_security_suite.py"; then
        PASSED_SUITES=$((PASSED_SUITES + 1))
    else
        FAILED_SUITES=$((FAILED_SUITES + 1))
    fi
fi

# Generate summary report
SUMMARY_FILE="$OUTPUT_DIR/test_summary_${TIMESTAMP}.json"
cat > "$SUMMARY_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "base_url": "$BASE_URL",
  "api_url": "$API_URL",
  "total_suites": $TOTAL_SUITES,
  "passed_suites": $PASSED_SUITES,
  "failed_suites": $FAILED_SUITES,
  "success_rate": $((PASSED_SUITES * 100 / TOTAL_SUITES)),
  "test_results": [
EOF

# Add individual test results
for result_file in "$OUTPUT_DIR"/*_${TIMESTAMP}.json; do
    if [ -f "$result_file" ]; then
        echo "    $(cat "$result_file")," >> "$SUMMARY_FILE"
    fi
done

# Remove trailing comma and close JSON
sed -i '$ s/,$//' "$SUMMARY_FILE"
cat >> "$SUMMARY_FILE" << EOF
  ]
}
EOF

# Print final summary
echo ""
echo "📊 TEST SUITE SUMMARY"
echo "====================="
echo "Total Test Suites: $TOTAL_SUITES"
echo "✅ Passed: $PASSED_SUITES"
echo "❌ Failed: $FAILED_SUITES"
echo "📈 Success Rate: $((PASSED_SUITES * 100 / TOTAL_SUITES))%"
echo ""
echo "📄 Results saved to: $OUTPUT_DIR"
echo "📋 Summary report: $SUMMARY_FILE"

# Generate HTML report
HTML_REPORT="$OUTPUT_DIR/test_report_${TIMESTAMP}.html"
cat > "$HTML_REPORT" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>GraphMind Deployment Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .failed { background: #ffe8e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .test-result { margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }
        .pass { border-left-color: #4caf50; }
        .fail { border-left-color: #f44336; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 GraphMind Deployment Test Report</h1>
        <p><strong>Timestamp:</strong> $TIMESTAMP</p>
        <p><strong>Frontend URL:</strong> $BASE_URL</p>
        <p><strong>API URL:</strong> $API_URL</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Total Test Suites:</strong> $TOTAL_SUITES</p>
        <p><strong>Passed:</strong> $PASSED_SUITES</p>
        <p><strong>Failed:</strong> $FAILED_SUITES</p>
        <p><strong>Success Rate:</strong> $((PASSED_SUITES * 100 / TOTAL_SUITES))%</p>
    </div>
EOF

if [ $FAILED_SUITES -gt 0 ]; then
    cat >> "$HTML_REPORT" << EOF
    <div class="failed">
        <h2>❌ Failed Tests</h2>
        <p>Some tests failed. Please check the detailed logs in the output directory.</p>
    </div>
EOF
else
    cat >> "$HTML_REPORT" << EOF
    <div class="summary">
        <h2>🎉 All Tests Passed!</h2>
        <p>GraphMind deployment is working correctly.</p>
    </div>
EOF
fi

cat >> "$HTML_REPORT" << EOF
    <div>
        <h2>📄 Test Results</h2>
        <p>Detailed test results are available in the following files:</p>
        <ul>
EOF

for result_file in "$OUTPUT_DIR"/*_${TIMESTAMP}.*; do
    if [ -f "$result_file" ]; then
        filename=$(basename "$result_file")
        cat >> "$HTML_REPORT" << EOF
            <li><a href="$filename">$filename</a></li>
EOF
    fi
done

cat >> "$HTML_REPORT" << EOF
        </ul>
    </div>
</body>
</html>
EOF

echo "📄 HTML Report: $HTML_REPORT"

# Exit with appropriate code
if [ $FAILED_SUITES -eq 0 ]; then
    echo ""
    echo "🎉 ALL TESTS PASSED! GraphMind deployment is working correctly."
    exit 0
else
    echo ""
    echo "⚠️ $FAILED_SUITES test suites failed. Please check the detailed logs."
    exit 1
fi
