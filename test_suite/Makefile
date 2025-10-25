# TradingAI Research Platform Test Suite Makefile

.PHONY: help status quick full stress clean install

# Default target
help:
	@echo "TradingAI Research Platform Test Suite"
	@echo "====================================="
	@echo ""
	@echo "Available targets:"
	@echo "  status    - Check system status"
	@echo "  quick     - Run quick test (10 prompts)"
	@echo "  full      - Run full test (25 prompts)"
	@echo "  stress    - Run stress test (3 consecutive full tests)"
	@echo "  clean     - Clean test results and logs"
	@echo "  install   - Install required dependencies"
	@echo ""
	@echo "Examples:"
	@echo "  make quick"
	@echo "  make full"
	@echo "  make stress"

# Check system status
status:
	@echo "🔍 Checking system status..."
	python3 run_tests.py --test-type status

# Run quick test
quick:
	@echo "🚀 Running quick test..."
	python3 run_tests.py --test-type quick

# Run full test
full:
	@echo "🚀 Running full test..."
	python3 run_tests.py --test-type full

# Run stress test
stress:
	@echo "🚀 Running stress test..."
	python3 run_tests.py --test-type stress

# Run CI tests
ci:
	@echo "🚀 Running CI test suite..."
	./run_ci_tests.sh

# Clean test artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf logs/*.log
	rm -rf results/*.json
	rm -rf results/*.md
	rm -rf __pycache__/
	@echo "✅ Cleaned"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install requests
	@echo "✅ Dependencies installed"

# Run all tests
all: status quick full
	@echo "✅ All tests completed"