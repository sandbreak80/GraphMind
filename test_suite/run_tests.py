#!/usr/bin/env python3
"""
Test Runner for TradingAI Research Platform
Provides different test configurations and automation options
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
import subprocess
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api_test_framework import APITestFramework

def run_quick_test():
    """Run a quick test with fewer prompts"""
    print("🚀 Running Quick Test (10 prompts)")
    print("=" * 50)
    
    framework = APITestFramework()
    
    # Override with fewer prompts for quick testing
    framework.test_prompts = {
        "simple": [
            "What is a moving average in trading?",
            "Explain what a stop loss is"
        ],
        "medium": [
            "How do you calculate the Sharpe ratio for a trading strategy?",
            "What is the difference between fundamental and technical analysis?"
        ],
        "complex": [
            "Design a comprehensive backtesting framework for quantitative trading strategies"
        ],
        "research": [
            "Conduct a comprehensive analysis of the evolution of algorithmic trading"
        ]
    }
    
    try:
        results = framework.run_comprehensive_test(timeout=30)
        framework.print_results(results)
        framework.save_results(results, "quick_test_results.json")
        return 0 if results.failed_tests == 0 else 1
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        return 1

def run_full_test():
    """Run the full comprehensive test"""
    print("🚀 Running Full Comprehensive Test (25 prompts)")
    print("=" * 50)
    
    framework = APITestFramework()
    
    try:
        results = framework.run_comprehensive_test(timeout=60)
        framework.print_results(results)
        framework.save_results(results, "full_test_results.json")
        return 0 if results.failed_tests == 0 else 1
    except Exception as e:
        print(f"❌ Full test failed: {str(e)}")
        return 1

def run_stress_test():
    """Run stress test with concurrent requests"""
    print("🚀 Running Stress Test (Concurrent Requests)")
    print("=" * 50)
    
    # This would require implementing concurrent testing
    # For now, just run multiple full tests in sequence
    framework = APITestFramework()
    
    try:
        print("Running 3 consecutive full tests...")
        all_results = []
        
        for i in range(3):
            print(f"\n--- Test Run {i+1}/3 ---")
            results = framework.run_comprehensive_test(timeout=60)
            all_results.append(results)
            
            if results.failed_tests > 0:
                print(f"❌ Test run {i+1} had {results.failed_tests} failures")
                break
            else:
                print(f"✅ Test run {i+1} passed")
        
        # Analyze combined results
        total_tests = sum(r.total_tests for r in all_results)
        total_failures = sum(r.failed_tests for r in all_results)
        total_success = sum(r.successful_tests for r in all_results)
        
        print(f"\n📊 STRESS TEST SUMMARY:")
        print(f"Total test runs: {len(all_results)}")
        print(f"Total tests: {total_tests}")
        print(f"Total successes: {total_success}")
        print(f"Total failures: {total_failures}")
        print(f"Overall success rate: {(total_success/total_tests)*100:.1f}%")
        
        if total_failures == 0:
            print("✅ STRESS TEST PASSED: All test runs successful")
            return 0
        else:
            print(f"❌ STRESS TEST FAILED: {total_failures} total failures")
            return 1
            
    except Exception as e:
        print(f"❌ Stress test failed: {str(e)}")
        return 1

def run_model_specific_test(model_name: str):
    """Run test with a specific model only"""
    print(f"🚀 Running Model-Specific Test: {model_name}")
    print("=" * 50)
    
    framework = APITestFramework()
    
    # Override model mapping to use only the specified model
    framework.model_mapping = {
        "simple": model_name,
        "medium": model_name,
        "complex": model_name,
        "research": model_name
    }
    
    try:
        results = framework.run_comprehensive_test(timeout=60)
        framework.print_results(results)
        framework.save_results(results, f"model_test_{model_name.replace(':', '_')}_results.json")
        return 0 if results.failed_tests == 0 else 1
    except Exception as e:
        print(f"❌ Model-specific test failed: {str(e)}")
        return 1

def run_mode_specific_test(mode: str):
    """Run test with a specific mode only"""
    print(f"🚀 Running Mode-Specific Test: {mode.upper()}")
    print("=" * 50)
    
    framework = APITestFramework()
    
    # Override test modes to use only the specified mode
    framework.test_modes = [mode]
    
    try:
        results = framework.run_comprehensive_test(timeout=60)
        framework.print_results(results)
        framework.save_results(results, f"mode_test_{mode}_results.json")
        return 0 if results.failed_tests == 0 else 1
    except Exception as e:
        print(f"❌ Mode-specific test failed: {str(e)}")
        return 1

def check_system_status():
    """Check if the system is ready for testing"""
    print("🔍 Checking System Status")
    print("=" * 30)
    
    framework = APITestFramework()
    
    # Test authentication
    if not framework.authenticate():
        print("❌ Authentication failed - check if API is running")
        return False
    
    # Test a simple query
    try:
        result = framework.run_single_test(
            prompt="What is a moving average?",
            complexity="simple",
            mode="qa",
            prompt_id=1,
            timeout=10
        )
        
        if result.success:
            print("✅ System is ready for testing")
            return True
        else:
            print(f"❌ System test failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ System check failed: {str(e)}")
        return False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="TradingAI Research Platform Test Suite")
    parser.add_argument("--test-type", choices=["quick", "full", "stress", "model", "mode", "status"], 
                       default="full", help="Type of test to run")
    parser.add_argument("--model", help="Model name for model-specific test")
    parser.add_argument("--mode", choices=["qa", "spec", "web", "research"], 
                       help="Mode for mode-specific test")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    print("🧪 TradingAI Research Platform Test Suite")
    print("=" * 50)
    print(f"Test type: {args.test_type}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check system status first
    if not check_system_status():
        print("❌ System not ready for testing")
        return 1
    
    print()
    
    # Run the appropriate test
    if args.test_type == "quick":
        return run_quick_test()
    elif args.test_type == "full":
        return run_full_test()
    elif args.test_type == "stress":
        return run_stress_test()
    elif args.test_type == "model":
        if not args.model:
            print("❌ --model argument required for model-specific test")
            return 1
        return run_model_specific_test(args.model)
    elif args.test_type == "mode":
        if not args.mode:
            print("❌ --mode argument required for mode-specific test")
            return 1
        return run_mode_specific_test(args.mode)
    elif args.test_type == "status":
        print("✅ System status check completed")
        return 0

if __name__ == "__main__":
    exit(main())