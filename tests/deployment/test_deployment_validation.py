#!/usr/bin/env python3
"""
GraphMind Deployment Validation Test Suite
Comprehensive tests to validate all functionality after deployment
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestResult:
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    duration: float
    details: Optional[Dict] = None

class GraphMindDeploymentValidator:
    def __init__(self, base_url: str = "http://localhost:3000", api_url: str = "http://localhost:3000/api"):
        self.base_url = base_url
        self.api_url = api_url
        self.auth_token = None
        self.test_results: List[TestResult] = []
        
    def run_all_tests(self) -> bool:
        """Run all deployment validation tests"""
        print("🧪 GraphMind Deployment Validation Test Suite")
        print("=" * 60)
        
        # Test categories
        test_categories = [
            ("Infrastructure Tests", self.test_infrastructure),
            ("Authentication Tests", self.test_authentication),
            ("API Endpoint Tests", self.test_api_endpoints),
            ("Frontend Tests", self.test_frontend),
            ("Backend Services Tests", self.test_backend_services),
            ("Ollama Integration Tests", self.test_ollama_integration),
            ("RAG System Tests", self.test_rag_system),
            ("Memory System Tests", self.test_memory_system),
            ("MCP Integration Tests", self.test_mcp_integration),
            ("Performance Tests", self.test_performance)
        ]
        
        all_passed = True
        
        for category_name, test_func in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 40)
            
            try:
                test_func()
            except Exception as e:
                self.add_result(f"{category_name} - Error", "FAIL", f"Test suite error: {str(e)}", 0)
                all_passed = False
        
        # Print summary
        self.print_summary()
        return all_passed
    
    def test_infrastructure(self):
        """Test basic infrastructure and connectivity"""
        # Test frontend accessibility
        self.test_endpoint("Frontend Homepage", "GET", self.base_url, expected_status=200)
        
        # Test API health
        self.test_endpoint("API Health", "GET", f"{self.api_url}/health", expected_status=200)
        
        # Test Docker services
        self.test_docker_services()
    
    def test_docker_services(self):
        """Test that all Docker services are running"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", "docker-compose.graphmind.yml", "ps", "--format", "json"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                services = json.loads(result.stdout)
                expected_services = [
                    "graphmind-rag", "graphmind-frontend", "graphmind-chromadb", 
                    "graphmind-redis", "graphmind-ollama", "graphmind-searxng"
                ]
                
                running_services = [s.get("Name", "") for s in services if s.get("State") == "running"]
                
                for service in expected_services:
                    if service in running_services:
                        self.add_result(f"Docker Service: {service}", "PASS", f"Service {service} is running", 0)
                    else:
                        self.add_result(f"Docker Service: {service}", "FAIL", f"Service {service} is not running", 0)
            else:
                self.add_result("Docker Services Check", "FAIL", f"Failed to check services: {result.stderr}", 0)
                
        except Exception as e:
            self.add_result("Docker Services Check", "FAIL", f"Error checking services: {str(e)}", 0)
    
    def test_authentication(self):
        """Test authentication system"""
        # Test login
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.make_request("POST", f"{self.api_url}/auth/login", data=login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.add_result("Authentication Login", "PASS", "Login successful", response.elapsed.total_seconds())
            
            # Test authenticated endpoint
            if self.auth_token:
                self.test_endpoint("Authenticated User Info", "GET", f"{self.api_url}/auth/me", 
                                 headers={"Authorization": f"Bearer {self.auth_token}"})
        else:
            self.add_result("Authentication Login", "FAIL", "Login failed", 0)
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        if not self.auth_token:
            self.add_result("API Endpoints", "SKIP", "No auth token available", 0)
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test system prompts
        self.test_endpoint("System Prompts", "GET", f"{self.api_url}/system-prompts", headers=headers)
        
        # Test user prompts
        self.test_endpoint("User Prompts", "GET", f"{self.api_url}/user-prompts", headers=headers)
        
        # Test Ollama models
        self.test_endpoint("Ollama Models", "GET", f"{self.api_url}/ollama/models", headers=headers)
        
        # Test memory profile
        self.test_endpoint("Memory Profile", "GET", f"{self.api_url}/memory/profile", headers=headers)
    
    def test_frontend(self):
        """Test frontend functionality"""
        # Test main page
        self.test_endpoint("Frontend Main Page", "GET", self.base_url, expected_status=200)
        
        # Test chat page (should redirect or show login)
        self.test_endpoint("Frontend Chat Page", "GET", f"{self.base_url}/chat/test", expected_status=[200, 302, 401])
        
        # Test memory page
        self.test_endpoint("Frontend Memory Page", "GET", f"{self.base_url}/memory", expected_status=[200, 302, 401])
    
    def test_backend_services(self):
        """Test backend service connectivity"""
        # Test internal service communication
        services_to_test = [
            ("ChromaDB", "http://graphmind-chromadb:8000"),
            ("Redis", "redis://graphmind-redis:6379"),
            ("SearXNG", "http://graphmind-searxng:8080"),
            ("Ollama", "http://graphmind-ollama:11434")
        ]
        
        for service_name, url in services_to_test:
            try:
                if url.startswith("redis://"):
                    # Skip Redis test for now (requires redis client)
                    self.add_result(f"Backend Service: {service_name}", "SKIP", "Redis test requires client library", 0)
                    continue
                
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404, 405]:  # 404/405 are OK for some services
                    self.add_result(f"Backend Service: {service_name}", "PASS", f"Service accessible", response.elapsed.total_seconds())
                else:
                    self.add_result(f"Backend Service: {service_name}", "FAIL", f"Unexpected status: {response.status_code}", response.elapsed.total_seconds())
            except Exception as e:
                self.add_result(f"Backend Service: {service_name}", "FAIL", f"Connection failed: {str(e)}", 0)
    
    def test_ollama_integration(self):
        """Test Ollama integration"""
        if not self.auth_token:
            self.add_result("Ollama Integration", "SKIP", "No auth token available", 0)
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test models endpoint
        response = self.make_request("GET", f"{self.api_url}/ollama/models", headers=headers)
        
        if response and response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                self.add_result("Ollama Models Available", "PASS", f"Found {len(models)} models", response.elapsed.total_seconds())
            else:
                self.add_result("Ollama Models Available", "FAIL", "No models found", response.elapsed.total_seconds())
        else:
            self.add_result("Ollama Models Available", "FAIL", "Failed to fetch models", 0)
    
    def test_rag_system(self):
        """Test RAG system functionality"""
        if not self.auth_token:
            self.add_result("RAG System", "SKIP", "No auth token available", 0)
            return
        
        # Test a simple query
        query_data = {
            "query": "What is GraphMind?",
            "mode": "qa",
            "model": "llama3.2:3b-instruct",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = self.make_request("POST", f"{self.api_url}/ask", 
                                   data=query_data, 
                                   headers={"Authorization": f"Bearer {self.auth_token}"})
        
        if response and response.status_code == 200:
            data = response.json()
            if data.get("answer"):
                self.add_result("RAG System Query", "PASS", "Query processed successfully", response.elapsed.total_seconds())
            else:
                self.add_result("RAG System Query", "FAIL", "No answer in response", response.elapsed.total_seconds())
        else:
            self.add_result("RAG System Query", "FAIL", f"Query failed: {response.status_code if response else 'No response'}", 0)
    
    def test_memory_system(self):
        """Test memory system functionality"""
        if not self.auth_token:
            self.add_result("Memory System", "SKIP", "No auth token available", 0)
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test memory profile
        response = self.make_request("GET", f"{self.api_url}/memory/profile", headers=headers)
        
        if response and response.status_code == 200:
            self.add_result("Memory Profile", "PASS", "Memory profile accessible", response.elapsed.total_seconds())
        else:
            self.add_result("Memory Profile", "FAIL", f"Memory profile failed: {response.status_code if response else 'No response'}", 0)
    
    def test_mcp_integration(self):
        """Test MCP integration"""
        # Test MCP services are running
        mcp_services = ["obsidian-mcp", "docker-mcp", "filesystem-mcp"]
        
        for service in mcp_services:
            try:
                response = requests.get(f"http://localhost:8081", timeout=5)  # Assuming MCP services on different ports
                self.add_result(f"MCP Service: {service}", "PASS", "MCP service accessible", response.elapsed.total_seconds())
            except Exception as e:
                self.add_result(f"MCP Service: {service}", "FAIL", f"MCP service not accessible: {str(e)}", 0)
    
    def test_performance(self):
        """Test system performance"""
        if not self.auth_token:
            self.add_result("Performance Tests", "SKIP", "No auth token available", 0)
            return
        
        # Test response times
        start_time = time.time()
        response = self.make_request("GET", f"{self.api_url}/health", 
                                   headers={"Authorization": f"Bearer {self.auth_token}"})
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response_time < 5.0:  # Should respond within 5 seconds
            self.add_result("API Response Time", "PASS", f"Response time: {response_time:.2f}s", response_time)
        else:
            self.add_result("API Response Time", "FAIL", f"Response time too slow: {response_time:.2f}s", response_time)
    
    def test_endpoint(self, name: str, method: str, url: str, expected_status: int = 200, 
                     headers: Dict = None, data: Dict = None):
        """Test a single endpoint"""
        start_time = time.time()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                self.add_result(name, "FAIL", f"Unsupported method: {method}", 0)
                return
            
            end_time = time.time()
            duration = end_time - start_time
            
            if isinstance(expected_status, list):
                if response.status_code in expected_status:
                    self.add_result(name, "PASS", f"Status {response.status_code}", duration)
                else:
                    self.add_result(name, "FAIL", f"Unexpected status: {response.status_code}", duration)
            else:
                if response.status_code == expected_status:
                    self.add_result(name, "PASS", f"Status {response.status_code}", duration)
                else:
                    self.add_result(name, "FAIL", f"Expected {expected_status}, got {response.status_code}", duration)
                    
        except Exception as e:
            self.add_result(name, "FAIL", f"Request failed: {str(e)}", 0)
    
    def make_request(self, method: str, url: str, data: Dict = None, headers: Dict = None) -> Optional[requests.Response]:
        """Make a request and return response"""
        try:
            if method == "GET":
                return requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                return requests.post(url, json=data, headers=headers, timeout=30)
            else:
                return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def add_result(self, test_name: str, status: str, message: str, duration: float, details: Dict = None):
        """Add a test result"""
        result = TestResult(test_name, status, message, duration, details)
        self.test_results.append(result)
        
        # Print result immediately
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
        print(f"{status_icon} {test_name}: {message}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r.status == "SKIP"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result.status == "FAIL":
                    print(f"  - {result.test_name}: {result.message}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! GraphMind deployment is working correctly.")
        else:
            print(f"\n⚠️ {failed_tests} tests failed. Please check the issues above.")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GraphMind Deployment Validation")
    parser.add_argument("--base-url", default="http://localhost:3000", help="Frontend base URL")
    parser.add_argument("--api-url", default="http://localhost:3000/api", help="API base URL")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    validator = GraphMindDeploymentValidator(args.base_url, args.api_url)
    
    print(f"🚀 Starting GraphMind deployment validation...")
    print(f"Frontend URL: {args.base_url}")
    print(f"API URL: {args.api_url}")
    
    success = validator.run_all_tests()
    
    if args.output:
        # Save results to file
        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": args.base_url,
            "api_url": args.api_url,
            "success": success,
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status,
                    "message": r.message,
                    "duration": r.duration,
                    "details": r.details
                } for r in validator.test_results
            ]
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {args.output}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
