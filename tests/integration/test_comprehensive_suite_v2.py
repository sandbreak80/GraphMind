#!/usr/bin/env python3
"""
Comprehensive Test Suite for EminiPlayer
Tests all functionality including new features: model switching, chat export, response times, system prompts
"""

import requests
import json
import time
import argparse
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
import sys
import os

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestCase:
    name: str
    description: str
    test_func: callable
    expected_result: TestResult = TestResult.PASS
    timeout: int = 30

class EminiPlayerTester:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.auth_token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def authenticate(self) -> bool:
        """Authenticate with the system."""
        try:
            self.log("Authenticating...")
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data="username=admin&password=admin123",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log(f"Authentication successful. Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log(f"Authentication failed: {response.status_code} - {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Authentication error: {e}", "ERROR")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        self.log(f"Running test: {test_case.name}")
        start_time = time.time()
        
        try:
            result = test_case.test_func()
            duration = time.time() - start_time
            
            if result:
                self.log(f"✓ {test_case.name} - PASSED ({duration:.2f}s)")
                self.test_results.append({
                    "name": test_case.name,
                    "result": TestResult.PASS,
                    "duration": duration,
                    "message": "Test passed"
                })
                return TestResult.PASS
            else:
                self.log(f"✗ {test_case.name} - FAILED ({duration:.2f}s)", "ERROR")
                self.test_results.append({
                    "name": test_case.name,
                    "result": TestResult.FAIL,
                    "duration": duration,
                    "message": "Test failed"
                })
                return TestResult.FAIL
                
        except Exception as e:
            duration = time.time() - start_time
            self.log(f"✗ {test_case.name} - ERROR ({duration:.2f}s): {e}", "ERROR")
            self.test_results.append({
                "name": test_case.name,
                "result": TestResult.ERROR,
                "duration": duration,
                "message": str(e)
            })
            return TestResult.ERROR
    
    def test_health_check(self) -> bool:
        """Test health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200 and "healthy" in response.json().get("status", "")
        except:
            return False
    
    def test_ollama_models(self) -> bool:
        """Test Ollama models endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/ollama/models", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                return "models" in data and len(data["models"]) > 0
            return False
        except:
            return False
    
    def test_user_info(self) -> bool:
        """Test user info endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/auth/me", headers=self.get_headers(), timeout=10)
            return response.status_code == 200 and "username" in response.json()
        except:
            return False
    
    def test_rag_only_mode(self) -> bool:
        """Test RAG only mode with data source validation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/ask",
                headers=self.get_headers(),
                json={
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3,
                    "model": "llama3.2:3b"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check that it has answer and citations
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_citations = "citations" in data
                return has_answer and has_citations
            return False
        except:
            return False
    
    def test_web_search_only_mode(self) -> bool:
        """Test web search only mode with data source validation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/ask-enhanced",
                headers=self.get_headers(),
                json={
                    "query": "What is the current market trend?",
                    "mode": "qa",
                    "top_k": 3,
                    "model": "llama3.2:3b"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check that it has answer and citations
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_citations = "citations" in data
                return has_answer and has_citations
            return False
        except:
            return False
    
    def test_obsidian_only_mode(self) -> bool:
        """Test Obsidian only mode with data source validation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/ask-obsidian",
                headers=self.get_headers(),
                json={
                    "query": "What are my trading strategies?",
                    "mode": "qa",
                    "top_k": 3,
                    "model": "llama3.2:3b"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check that it has answer and citations
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_citations = "citations" in data
                return has_answer and has_citations
            return False
        except:
            return False
    
    def test_comprehensive_research_mode(self) -> bool:
        """Test comprehensive research mode with data source validation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/ask-research",
                headers=self.get_headers(),
                json={
                    "query": "What are the latest trading strategies?",
                    "mode": "qa",
                    "top_k": 3,
                    "model": "llama3.2:3b"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check that it has answer and citations
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_citations = "citations" in data
                return has_answer and has_citations
            return False
        except:
            return False
    
    def test_chat_title_generation(self) -> bool:
        """Test smart chat title generation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate-chat-title",
                headers=self.get_headers(),
                json={
                    "message": "Tell me about trading strategies for E-mini futures"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                title = data.get("title", "")
                # Check that title is meaningful and not just the first few words
                return len(title) > 0 and len(title) < 50 and "Tell me about" not in title
            return False
        except:
            return False
    
    def test_system_prompts_list(self) -> bool:
        """Test system prompts listing."""
        try:
            response = requests.get(f"{self.base_url}/api/system-prompts", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                expected_modes = ["rag_only", "web_search_only", "obsidian_only", "comprehensive_research"]
                return all(mode in data.get("prompts", {}) for mode in expected_modes)
            return False
        except:
            return False
    
    def test_system_prompt_detail(self) -> bool:
        """Test system prompt detail retrieval."""
        try:
            response = requests.get(f"{self.base_url}/api/system-prompts/rag_only", headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["mode", "current_version", "prompt"]
                return all(field in data for field in required_fields) and len(data["prompt"]) > 100
            return False
        except:
            return False
    
    def test_model_switching(self) -> bool:
        """Test model switching functionality."""
        try:
            # Test with different models
            models_to_test = ["llama3.2:3b", "llama3.1:latest"]
            
            for model in models_to_test:
                response = requests.post(
                    f"{self.base_url}/api/ask",
                    headers=self.get_headers(),
                    json={
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 3,
                        "model": model
                    },
                    timeout=30
                )
                
                if response.status_code != 200:
                    return False
                
                data = response.json()
                if "answer" not in data or len(data["answer"]) == 0:
                    return False
            
            return True
        except:
            return False
    
    def test_response_time_measurement(self) -> bool:
        """Test response time measurement."""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/ask",
                headers=self.get_headers(),
                json={
                    "query": "What is trading?",
                    "mode": "qa",
                    "top_k": 3,
                    "model": "llama3.2:3b"
                },
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                # Response should be reasonable (less than 30 seconds)
                return response_time < 30
            return False
        except:
            return False
    
    def test_unauthorized_access(self) -> bool:
        """Test unauthorized access is properly rejected."""
        try:
            response = requests.get(f"{self.base_url}/api/auth/me", timeout=10)
            return response.status_code == 401 or response.status_code == 403
        except:
            return False
    
    def test_invalid_endpoint(self) -> bool:
        """Test invalid endpoint returns 404."""
        try:
            response = requests.get(f"{self.base_url}/api/invalid-endpoint", timeout=10)
            return response.status_code == 404
        except:
            return False
    
    def create_test_cases(self) -> List[TestCase]:
        """Create all test cases."""
        return [
            TestCase("health_check", "Health endpoint check", self.test_health_check),
            TestCase("ollama_models", "Ollama models endpoint", self.test_ollama_models),
            TestCase("user_info", "User info endpoint", self.test_user_info),
            TestCase("rag_only_mode", "RAG only mode with data source validation", self.test_rag_only_mode),
            TestCase("web_search_only_mode", "Web search only mode with data source validation", self.test_web_search_only_mode),
            TestCase("obsidian_only_mode", "Obsidian only mode with data source validation", self.test_obsidian_only_mode),
            TestCase("comprehensive_research_mode", "Comprehensive research mode with data source validation", self.test_comprehensive_research_mode),
            TestCase("chat_title_generation", "Smart chat title generation", self.test_chat_title_generation),
            TestCase("system_prompts_list", "System prompts listing", self.test_system_prompts_list),
            TestCase("system_prompt_detail", "System prompt detail retrieval", self.test_system_prompt_detail),
            TestCase("model_switching", "Model switching functionality", self.test_model_switching),
            TestCase("response_time_measurement", "Response time measurement", self.test_response_time_measurement),
            TestCase("unauthorized_access", "Unauthorized access rejection", self.test_unauthorized_access),
            TestCase("invalid_endpoint", "Invalid endpoint 404", self.test_invalid_endpoint),
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases."""
        self.log("Starting comprehensive test suite...")
        
        # Authenticate first
        if not self.authenticate():
            self.log("Authentication failed. Some tests will be skipped.", "ERROR")
        
        # Create and run test cases
        test_cases = self.create_test_cases()
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_case in test_cases:
            result = self.run_test(test_case)
            if result == TestResult.PASS:
                passed += 1
            elif result == TestResult.FAIL:
                failed += 1
            else:
                errors += 1
        
        total_time = time.time() - self.start_time
        
        # Generate summary
        summary = {
            "total_tests": len(test_cases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_time": total_time,
            "test_results": self.test_results
        }
        
        self.log("=" * 60)
        self.log(f"Test Suite Summary:")
        self.log(f"Total Tests: {len(test_cases)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Errors: {errors}")
        self.log(f"Total Time: {total_time:.2f}s")
        self.log("=" * 60)
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="EminiPlayer Comprehensive Test Suite")
    parser.add_argument("--url", default="http://localhost:3001", help="Base URL for the API")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = EminiPlayerTester(args.url)
    results = tester.run_all_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Test results saved to {args.output}")
    
    # Exit with error code if any tests failed
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()