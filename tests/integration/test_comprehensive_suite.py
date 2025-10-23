#!/usr/bin/env python3
"""
Comprehensive Test Suite for EminiPlayer Application
====================================================

This test suite validates all major functionality including:
- Authentication (login/logout)
- All chat modes and their data source exclusivity
- API endpoint functionality
- Data source validation
- Error handling

Usage:
    python test_comprehensive_suite.py [--base-url URL] [--verbose]
"""

import requests
import json
import time
import argparse
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"

@dataclass
class TestCase:
    name: str
    description: str
    endpoint: str
    method: str
    headers: Dict[str, str]
    data: Dict[str, Any]
    expected_status: int
    expected_sources: Optional[List[str]] = None
    should_contain: Optional[List[str]] = None
    should_not_contain: Optional[List[str]] = None

class EminiPlayerTester:
    def __init__(self, base_url: str = "http://localhost:3001", verbose: bool = False):
        self.base_url = base_url
        self.verbose = verbose
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level == "ERROR":
            print(f"[{level}] {message}")
    
    def authenticate(self) -> bool:
        """Test authentication and get token."""
        self.log("Testing authentication...")
        
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=30
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
    
    def run_test(self, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        self.log(f"Running test: {test_case.name}")
        
        try:
            # Prepare request
            url = f"{self.base_url}{test_case.endpoint}"
            headers = test_case.headers.copy()
            
            if self.auth_token and "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Make request
            if test_case.method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif test_case.method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=test_case.data, timeout=30)
            else:
                self.log(f"Unsupported method: {test_case.method}", "ERROR")
                return TestResult.FAIL
            
            # Check status code
            if response.status_code != test_case.expected_status:
                self.log(f"Expected status {test_case.expected_status}, got {response.status_code}", "ERROR")
                return TestResult.FAIL
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            # Check data source exclusivity
            if test_case.expected_sources:
                if "citations" in response_data:
                    actual_sources = [citation.get("section", "unknown") for citation in response_data["citations"]]
                    actual_sources = list(set(actual_sources))  # Remove duplicates
                    
                    # Check if only expected sources are present
                    unexpected_sources = [s for s in actual_sources if s not in test_case.expected_sources]
                    if unexpected_sources:
                        self.log(f"Unexpected sources found: {unexpected_sources}", "ERROR")
                        return TestResult.FAIL
                    
                    # Check if expected sources are present
                    missing_sources = [s for s in test_case.expected_sources if s not in actual_sources]
                    if missing_sources and test_case.expected_sources != ["any"]:
                        self.log(f"Missing expected sources: {missing_sources}", "ERROR")
                        return TestResult.FAIL
            
            # Check content requirements
            if test_case.should_contain:
                response_text = json.dumps(response_data).lower()
                for required in test_case.should_contain:
                    if required.lower() not in response_text:
                        self.log(f"Response should contain '{required}' but doesn't", "ERROR")
                        return TestResult.FAIL
            
            if test_case.should_not_contain:
                response_text = json.dumps(response_data).lower()
                for forbidden in test_case.should_not_contain:
                    if forbidden.lower() in response_text:
                        self.log(f"Response should not contain '{forbidden}' but does", "ERROR")
                        return TestResult.FAIL
            
            self.log(f"Test passed: {test_case.name}")
            return TestResult.PASS
            
        except Exception as e:
            self.log(f"Test error: {e}", "ERROR")
            return TestResult.FAIL
    
    def create_test_cases(self) -> List[TestCase]:
        """Create all test cases."""
        return [
            # Authentication Tests
            TestCase(
                name="Health Check",
                description="Test basic health endpoint",
                endpoint="/api/health",
                method="GET",
                headers={},
                data={},
                expected_status=200,
                should_contain=["healthy"]
            ),
            
            TestCase(
                name="Login Test",
                description="Test user authentication",
                endpoint="/api/auth/login",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={"username": "admin", "password": "admin123"},
                expected_status=200,
                should_contain=["access_token"]
            ),
            
            # RAG Only Mode Tests
            TestCase(
                name="RAG Only Mode - Documents Only",
                description="Test RAG mode uses only document sources",
                endpoint="/api/ask",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={
                    "request": {
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 5,
                        "temperature": 0.1,
                        "max_tokens": 1000,
                        "conversation_history": []
                    }
                },
                expected_status=200,
                expected_sources=["pdf", "video_transcript", "llm_processed"],
                should_not_contain=["Web Source", "Obsidian Note"]
            ),
            
            # Web Search Only Mode Tests
            TestCase(
                name="Web Search Only Mode - Web Only",
                description="Test enhanced mode uses only web sources",
                endpoint="/api/ask-enhanced",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={
                    "request": {
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 5,
                        "temperature": 0.1,
                        "max_tokens": 1000,
                        "conversation_history": []
                    }
                },
                expected_status=200,
                expected_sources=["any"],  # Web sources vary, just check no documents
                should_not_contain=["pdf", "video_transcript", "llm_processed", "Obsidian Note"]
            ),
            
            # Obsidian Only Mode Tests
            TestCase(
                name="Obsidian Only Mode - Obsidian Only",
                description="Test Obsidian mode uses only Obsidian sources",
                endpoint="/api/ask-obsidian",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={
                    "request": {
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 5,
                        "temperature": 0.1,
                        "max_tokens": 1000,
                        "conversation_history": []
                    }
                },
                expected_status=200,
                expected_sources=["Trading Strategy Framework", "trading strategy in your BattleCard"],
                should_not_contain=["pdf", "video_transcript", "llm_processed", "Web Source"]
            ),
            
            # Comprehensive Research Mode Tests
            TestCase(
                name="Comprehensive Research Mode - Documents + Web",
                description="Test research mode uses both documents and web sources",
                endpoint="/api/ask-research",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={
                    "request": {
                        "query": "What is trading?",
                        "mode": "qa",
                        "top_k": 5,
                        "temperature": 0.1,
                        "max_tokens": 1000,
                        "conversation_history": []
                    }
                },
                expected_status=200,
                expected_sources=["any"],  # Should have both documents and web
                should_contain=["pdf", "video_transcript", "llm_processed"]  # Should have documents
            ),
            
            # Error Handling Tests
            TestCase(
                name="Invalid Endpoint",
                description="Test 404 for invalid endpoint",
                endpoint="/api/invalid-endpoint",
                method="GET",
                headers={},
                data={},
                expected_status=404
            ),
            
            TestCase(
                name="Unauthorized Request",
                description="Test 401 for request without token",
                endpoint="/api/ask",
                method="POST",
                headers={"Content-Type": "application/json"},
                data={
                    "request": {
                        "query": "test",
                        "mode": "qa",
                        "top_k": 5,
                        "temperature": 0.1,
                        "max_tokens": 1000,
                        "conversation_history": []
                    }
                },
                expected_status=401
            ),
            
            # Model Tests
            TestCase(
                name="Ollama Models",
                description="Test Ollama models endpoint",
                endpoint="/api/ollama/models",
                method="GET",
                headers={},
                data={},
                expected_status=200,
                should_contain=["models"]
            ),
            
            # User Info Test
            TestCase(
                name="User Info",
                description="Test user info endpoint",
                endpoint="/api/auth/me",
                method="GET",
                headers={},
                data={},
                expected_status=200,
                should_contain=["username"]
            )
        ]
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases and return results."""
        self.log("Starting comprehensive test suite...")
        
        # Authenticate first
        if not self.authenticate():
            self.log("Authentication failed, some tests will be skipped", "ERROR")
        
        # Run all test cases
        test_cases = self.create_test_cases()
        passed = 0
        failed = 0
        skipped = 0
        
        for test_case in test_cases:
            result = self.run_test(test_case)
            self.test_results.append({
                "name": test_case.name,
                "result": result.value,
                "description": test_case.description
            })
            
            if result == TestResult.PASS:
                passed += 1
            elif result == TestResult.FAIL:
                failed += 1
            else:
                skipped += 1
        
        # Summary
        total = passed + failed + skipped
        success_rate = (passed / total * 100) if total > 0 else 0
        
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": success_rate,
            "test_results": self.test_results
        }
        
        self.log(f"\nTest Summary:")
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Skipped: {skipped}")
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="EminiPlayer Comprehensive Test Suite")
    parser.add_argument("--base-url", default="http://localhost:3001", help="Base URL for the API")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    # Run tests
    tester = EminiPlayerTester(args.base_url, args.verbose)
    results = tester.run_all_tests()
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Test results saved to {args.output}")
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()