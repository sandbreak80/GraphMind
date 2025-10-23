#!/bin/bash
# Automated QA Suite Runner for EminiPlayer
# Runs comprehensive tests and performance tests

set -e

# Configuration
BASE_URL="http://localhost:3001"
OUTPUT_DIR="test_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="${OUTPUT_DIR}/${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗${NC} $1"
}

# Create results directory
mkdir -p "$RESULTS_DIR"

log "Starting EminiPlayer QA Suite"
log "Results will be saved to: $RESULTS_DIR"

# Check if services are running
log "Checking if services are running..."

if ! curl -s "$BASE_URL/api/health" > /dev/null; then
    error "Services are not running. Please start the application first."
    exit 1
fi

success "Services are running"

# Wait for services to be fully ready
log "Waiting for services to be fully ready..."
sleep 10

# Run comprehensive test suite
log "Running comprehensive test suite..."
python3 tests/integration/test_comprehensive_suite_v2.py \
    --url "$BASE_URL" \
    --output "$RESULTS_DIR/comprehensive_tests.json" \
    --verbose

if [ $? -eq 0 ]; then
    success "Comprehensive tests passed"
else
    error "Comprehensive tests failed"
    COMPREHENSIVE_FAILED=1
fi

# Run performance test suite
log "Running performance test suite..."
python3 tests/performance/test_performance_suite.py \
    --url "$BASE_URL" \
    --output "$RESULTS_DIR/performance_tests.json" \
    --concurrent 5

if [ $? -eq 0 ]; then
    success "Performance tests passed"
else
    error "Performance tests failed"
    PERFORMANCE_FAILED=1
fi

# Run quick validation tests
log "Running quick validation tests..."
python3 tests/integration/test_quick_validation.py

if [ $? -eq 0 ]; then
    success "Quick validation tests passed"
else
    error "Quick validation tests failed"
    QUICK_FAILED=1
fi

# Generate summary report
log "Generating summary report..."

SUMMARY_FILE="$RESULTS_DIR/summary.md"
cat > "$SUMMARY_FILE" << EOF
# EminiPlayer QA Suite Results

**Timestamp:** $(date)
**Base URL:** $BASE_URL

## Test Results

### Comprehensive Tests
- **Status:** $([ -z "$COMPREHENSIVE_FAILED" ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Results:** comprehensive_tests.json

### Performance Tests
- **Status:** $([ -z "$PERFORMANCE_FAILED" ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Results:** performance_tests.json

### Quick Validation Tests
- **Status:** $([ -z "$QUICK_FAILED" ] && echo "✅ PASSED" || echo "❌ FAILED")

## Overall Status
$([ -z "$COMPREHENSIVE_FAILED$PERFORMANCE_FAILED$QUICK_FAILED" ] && echo "✅ ALL TESTS PASSED" || echo "❌ SOME TESTS FAILED")

## Files Generated
- comprehensive_tests.json
- performance_tests.json
- summary.md

EOF

# Display summary
echo ""
log "QA Suite Summary:"
echo "=================="
cat "$SUMMARY_FILE"

# Exit with appropriate code
if [ -z "$COMPREHENSIVE_FAILED$PERFORMANCE_FAILED$QUICK_FAILED" ]; then
    success "All tests passed!"
    exit 0
else
    error "Some tests failed. Check the results in $RESULTS_DIR"
    exit 1
fi