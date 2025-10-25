#!/usr/bin/env python3
"""
Comprehensive GraphMind Functionality Test
Tests all major features and modes after deployment
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost"
API_TIMEOUT = 60
USERNAME = "admin"
PASSWORD = "admin123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(test_name: str):
    print(f"\n{Colors.BLUE}Testing: {test_name}{Colors.END}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

class GraphMindTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.results = {"passed": 0, "failed": 0, "warnings": 0}
    
    def login(self) -> bool:
        """Test login and get auth token"""
        print_test("Authentication")
        try:
            response = self.session.post(
                f"{BASE_URL}/api/auth/login",
                data={"username": USERNAME, "password": PASSWORD},  # Use form data, not JSON
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print_success(f"Login successful (token: {self.auth_token[:20]}...)")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Login failed: HTTP {response.status_code} - {response.text}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Login error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        print_test("Health Check")
        try:
            response = self.session.get(f"{BASE_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Health check passed: {response.json()}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Health check failed: HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Health check error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_models(self) -> bool:
        """Test model listing"""
        print_test("Ollama Models")
        try:
            response = self.session.get(f"{BASE_URL}/api/ollama/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                if models:
                    print_success(f"Found {len(models)} models:")
                    for model in models[:5]:
                        size_gb = model.get("size", 0) / 1024 / 1024 / 1024
                        print(f"  - {model.get('name')} ({size_gb:.1f}GB)")
                    self.results["passed"] += 1
                    return True
                else:
                    print_warning("No models found")
                    self.results["warnings"] += 1
                    return False
            else:
                print_error(f"Models endpoint failed: HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Models error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_mode(self, mode_name: str, endpoint: str, query: str) -> bool:
        """Test a specific chat mode"""
        print_test(f"{mode_name} Mode")
        try:
            request_data = {
                "query": query,
                "mode": "qa",
                "temperature": 0.1,
                "max_tokens": 500,
                "top_k_sampling": 40,
                "bm25_top_k": 30,
                "embedding_top_k": 30,
                "rerank_top_k": 8,
                "web_search_results": 6,
                "web_pages_to_parse": 4
            }
            
            print(f"  Sending query: '{query}'")
            start_time = time.time()
            
            response = self.session.post(
                f"{BASE_URL}/api/{endpoint}",
                json=request_data,
                timeout=API_TIMEOUT
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                citations = data.get("citations", [])
                total_sources = data.get("total_sources", 0)
                
                print_success(f"Response received ({elapsed:.1f}s)")
                print(f"  Answer length: {len(answer)} chars")
                print(f"  Sources: {total_sources}")
                print(f"  Citations: {len(citations)}")
                
                if answer:
                    print(f"  First 150 chars: {answer[:150]}...")
                    self.results["passed"] += 1
                    return True
                else:
                    print_warning("Empty answer received")
                    self.results["warnings"] += 1
                    return False
            else:
                print_error(f"{mode_name} failed: HTTP {response.status_code} - {response.text[:200]}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"{mode_name} error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_all_modes(self):
        """Test all 4 operating modes"""
        modes = [
            ("RAG Only", "ask", "What is this system?"),
            ("Web Search", "ask-enhanced", "What is the current weather?"),
            ("Obsidian", "ask-obsidian", "What notes do I have?"),
            ("Comprehensive Research", "ask-research", "Explain machine learning")
        ]
        
        for mode_name, endpoint, query in modes:
            self.test_mode(mode_name, endpoint, query)
            time.sleep(1)  # Brief pause between tests
    
    def test_documents(self) -> bool:
        """Test document listing"""
        print_test("Document Management")
        try:
            response = self.session.get(f"{BASE_URL}/api/documents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                docs = data.get("documents", [])
                if docs:
                    print_success(f"Found {len(docs)} documents")
                    for doc in docs[:5]:
                        print(f"  - {doc.get('filename')} ({doc.get('chunks')} chunks)")
                    self.results["passed"] += 1
                else:
                    print_warning("No documents found - ChromaDB is empty")
                    self.results["warnings"] += 1
                return True
            else:
                print_error(f"Documents endpoint failed: HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Documents error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_system_prompts(self) -> bool:
        """Test system prompts management"""
        print_test("System Prompts")
        try:
            response = self.session.get(f"{BASE_URL}/api/system-prompts", timeout=10)
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", {})
                print_success(f"Found {len(prompts)} prompt modes:")
                for mode in prompts.keys():
                    print(f"  - {mode}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"System prompts failed: HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"System prompts error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_memory(self) -> bool:
        """Test memory system"""
        print_test("Memory System")
        try:
            response = self.session.get(f"{BASE_URL}/api/memory/profile", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print_success("Memory profile loaded")
                print(f"  Keys: {list(data.keys())[:5]}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Memory system failed: HTTP {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Memory error: {e}")
            self.results["failed"] += 1
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"GraphMind Comprehensive Test Suite")
        print(f"{'='*60}{Colors.END}\n")
        
        if not self.login():
            print_error("Cannot continue without authentication")
            return False
        
        # Core tests
        self.test_health()
        self.test_models()
        self.test_documents()
        self.test_system_prompts()
        self.test_memory()
        
        # Mode tests
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"Testing All 4 Operating Modes")
        print(f"{'='*60}{Colors.END}")
        self.test_all_modes()
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"Test Summary")
        print(f"{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.results['warnings']}{Colors.END}")
        
        if self.results['failed'] == 0:
            print(f"\n{Colors.GREEN}All tests passed!{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}Some tests failed. Please review the errors above.{Colors.END}")
            return False

def main():
    tester = GraphMindTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

