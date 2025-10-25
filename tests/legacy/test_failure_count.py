#!/usr/bin/env python3
"""Simple test to count failures precisely."""
import requests
import time
import json
from datetime import datetime

def test_failure_count():
    base_url = "http://localhost:8002"
    
    # Get authentication token
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🚀 FAILURE COUNT TEST")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Testing: 25 prompts across 4 modes")
    print("🎯 Goal: Count every single failure")
    print("=" * 50)
    
    # Test prompts
    test_prompts = [
        {"query": f"What is a moving average in trading? (test_{int(time.time())}_1)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"Explain what a stop loss is (test_{int(time.time())}_2)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"What is the difference between a bull and bear market? (test_{int(time.time())}_3)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"Define volatility in financial markets (test_{int(time.time())}_4)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"What is a trading volume? (test_{int(time.time())}_5)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"Explain what a dividend is (test_{int(time.time())}_6)", "complexity": "simple", "model": "llama3.2:3b"},
        {"query": f"How do you calculate the Sharpe ratio for a trading strategy? (test_{int(time.time())}_7)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"What is the difference between fundamental and technical analysis? (test_{int(time.time())}_8)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"Explain how to use Bollinger Bands for trading decisions (test_{int(time.time())}_9)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"What are the key components of a trading plan? (test_{int(time.time())}_10)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"How do you calculate position sizing based on risk management? (test_{int(time.time())}_11)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"What is the difference between market orders and limit orders? (test_{int(time.time())}_12)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"Explain how to use the MACD indicator for trend analysis (test_{int(time.time())}_13)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"What are the advantages and disadvantages of day trading? (test_{int(time.time())}_14)", "complexity": "medium", "model": "llama3.1:latest"},
        {"query": f"Design a comprehensive backtesting framework for quantitative trading strategies (test_{int(time.time())}_15)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"Explain how to implement a pairs trading strategy using statistical arbitrage (test_{int(time.time())}_16)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"Analyze the impact of market microstructure on high-frequency trading strategies (test_{int(time.time())}_17)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"How do you build a multi-asset portfolio optimization model? (test_{int(time.time())}_18)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"Explain the implementation of machine learning models for algorithmic trading (test_{int(time.time())}_19)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"What are the key considerations for building a low-latency trading system? (test_{int(time.time())}_20)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"How do you implement risk management for a multi-strategy hedge fund? (test_{int(time.time())}_21)", "complexity": "complex", "model": "qwen2.5-coder:14b"},
        {"query": f"Conduct a comprehensive analysis of the evolution of algorithmic trading (test_{int(time.time())}_22)", "complexity": "research", "model": "deepseek-r1:latest"},
        {"query": f"Provide an in-depth study of market making strategies in cryptocurrency markets (test_{int(time.time())}_23)", "complexity": "research", "model": "deepseek-r1:latest"},
        {"query": f"Analyze the role of artificial intelligence in modern quantitative finance (test_{int(time.time())}_24)", "complexity": "research", "model": "deepseek-r1:latest"},
        {"query": f"Examine the impact of ESG factors on quantitative investment strategies (test_{int(time.time())}_25)", "complexity": "research", "model": "deepseek-r1:latest"}
    ]
    
    test_modes = ["qa", "spec", "web", "research"]
    
    # Counters
    total_tests = 0
    successful_tests = 0
    failed_tests = 0
    failures = []
    
    print(f"\n🧪 Testing {len(test_prompts)} prompts across {len(test_modes)} modes")
    print(f"📊 Total tests: {len(test_prompts) * len(test_modes)}")
    print("-" * 50)
    
    for prompt_idx, prompt_data in enumerate(test_prompts, 1):
        query = prompt_data["query"]
        complexity = prompt_data["complexity"]
        model = prompt_data["model"]
        
        print(f"\n📝 Prompt {prompt_idx}/25: {complexity.upper()} - {model}")
        
        for mode_idx, mode in enumerate(test_modes, 1):
            total_tests += 1
            
            # Prepare request
            request_data = {
                "query": query,
                "temperature": 0.1,
                "max_tokens": 1000,
                "model": model
            }
            
            if mode == "spec":
                request_data["top_k"] = 10
            elif mode == "web":
                request_data["web_enabled"] = True
            elif mode == "research":
                request_data["research_enabled"] = True
            
            print(f"   🔄 Mode {mode_idx}/4: {mode.upper()}", end=" ")
            
            try:
                response = requests.post(
                    f"{base_url}/ask",
                    headers=headers,
                    json=request_data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get('answer', '')
                    if answer and len(answer) > 100:
                        successful_tests += 1
                        print("✅")
                    else:
                        failed_tests += 1
                        failures.append(f"Prompt {prompt_idx}, Mode {mode}: Empty or too short answer")
                        print("❌ EMPTY")
                else:
                    failed_tests += 1
                    failures.append(f"Prompt {prompt_idx}, Mode {mode}: HTTP {response.status_code}")
                    print(f"❌ HTTP {response.status_code}")
                    
            except requests.exceptions.Timeout:
                failed_tests += 1
                failures.append(f"Prompt {prompt_idx}, Mode {mode}: Timeout")
                print("❌ TIMEOUT")
            except Exception as e:
                failed_tests += 1
                failures.append(f"Prompt {prompt_idx}, Mode {mode}: {str(e)}")
                print(f"❌ ERROR: {str(e)}")
    
    # Final results
    print(f"\n📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ FAILURES ({failed_tests}):")
        for i, failure in enumerate(failures, 1):
            print(f"   {i}. {failure}")
        print(f"\n🚨 TEST INVALIDATED: {failed_tests} failed responses")
    else:
        print(f"\n✅ TEST VALID: 0 failed responses")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    return failed_tests

if __name__ == "__main__":
    failures = test_failure_count()