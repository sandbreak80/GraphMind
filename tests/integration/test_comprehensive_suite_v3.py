#!/usr/bin/env python3
"""
Comprehensive Test Suite v3.0 - TradingAI Research Platform
Tests all functionality including new URL routing and memory features.
"""

import asyncio
import json
import time
import requests
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.api_url = "http://localhost:8001"
        self.auth_token = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance": {},
            "features": {}
        }
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ {test_name}: PASSED {details}")
        else:
            self.test_results["failed"] += 1
            error_msg = f"❌ {test_name}: FAILED {details}"
            logger.error(error_msg)
            self.test_results["errors"].append(error_msg)
    
    def authenticate(self) -> bool:
        """Test authentication"""
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                data={"username": "admin", "password": "admin123"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_test("Authentication", True, f"Token: {self.auth_token[:20]}...")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_health_checks(self) -> bool:
        """Test all health endpoints"""
        health_endpoints = [
            f"{self.api_url}/health",
            f"{self.base_url}/api/health"
        ]
        
        all_healthy = True
        for endpoint in health_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Health Check {endpoint}", True)
                else:
                    self.log_test(f"Health Check {endpoint}", False, f"Status: {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_test(f"Health Check {endpoint}", False, f"Error: {str(e)}")
                all_healthy = False
        
        return all_healthy
    
    def test_ollama_models(self) -> bool:
        """Test Ollama model availability"""
        try:
            response = requests.get(f"{self.api_url}/ollama/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                self.log_test("Ollama Models", True, f"Found {len(models)} models")
                return len(models) > 0
            else:
                self.log_test("Ollama Models", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Ollama Models", False, f"Error: {str(e)}")
            return False
    
    def test_rag_functionality(self) -> bool:
        """Test RAG mode functionality"""
        if not self.auth_token:
            self.log_test("RAG Functionality", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "query": "What trading strategies work best?",
                "mode": "qa",
                "model": "qwen2.5-coder:14b"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/ask",
                json=payload,
                headers=headers,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_sources = "sources" in data and len(data["sources"]) > 0
                
                self.test_results["performance"]["rag_response_time"] = response_time
                self.test_results["features"]["rag_sources"] = len(data.get("sources", []))
                
                if has_answer and has_sources:
                    self.log_test("RAG Functionality", True, f"Response time: {response_time:.2f}s, Sources: {len(data.get('sources', []))}")
                    return True
                else:
                    self.log_test("RAG Functionality", False, f"Missing answer or sources")
                    return False
            else:
                self.log_test("RAG Functionality", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("RAG Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_web_search(self) -> bool:
        """Test web search functionality"""
        if not self.auth_token:
            self.log_test("Web Search", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "query": "What is the current market trend?",
                "mode": "web",
                "model": "qwen2.5-coder:14b"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/ask-enhanced",
                json=payload,
                headers=headers,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_answer = "answer" in data and len(data["answer"]) > 0
                
                self.test_results["performance"]["web_response_time"] = response_time
                
                if has_answer:
                    self.log_test("Web Search", True, f"Response time: {response_time:.2f}s")
                    return True
                else:
                    self.log_test("Web Search", False, "No answer returned")
                    return False
            else:
                self.log_test("Web Search", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Web Search", False, f"Error: {str(e)}")
            return False
    
    def test_obsidian_integration(self) -> bool:
        """Test Obsidian MCP integration"""
        if not self.auth_token:
            self.log_test("Obsidian Integration", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "query": "What are my trading notes?",
                "mode": "obsidian",
                "model": "qwen2.5-coder:14b"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/ask-obsidian",
                json=payload,
                headers=headers,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_answer = "answer" in data and len(data["answer"]) > 0
                
                self.test_results["performance"]["obsidian_response_time"] = response_time
                
                if has_answer:
                    self.log_test("Obsidian Integration", True, f"Response time: {response_time:.2f}s")
                    return True
                else:
                    self.log_test("Obsidian Integration", False, "No answer returned")
                    return False
            else:
                self.log_test("Obsidian Integration", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Obsidian Integration", False, f"Error: {str(e)}")
            return False
    
    def test_research_mode(self) -> bool:
        """Test comprehensive research mode"""
        if not self.auth_token:
            self.log_test("Research Mode", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "query": "What are the best trading strategies for 2024?",
                "mode": "research",
                "model": "qwen2.5-coder:14b"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/ask-research",
                json=payload,
                headers=headers,
                timeout=90
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                has_answer = "answer" in data and len(data["answer"]) > 0
                has_sources = "sources" in data and len(data["sources"]) > 0
                
                self.test_results["performance"]["research_response_time"] = response_time
                self.test_results["features"]["research_sources"] = len(data.get("sources", []))
                
                if has_answer and has_sources:
                    self.log_test("Research Mode", True, f"Response time: {response_time:.2f}s, Sources: {len(data.get('sources', []))}")
                    return True
                else:
                    self.log_test("Research Mode", False, "Missing answer or sources")
                    return False
            else:
                self.log_test("Research Mode", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Research Mode", False, f"Error: {str(e)}")
            return False
    
    def test_memory_system(self) -> bool:
        """Test user memory system"""
        if not self.auth_token:
            self.log_test("Memory System", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test memory profile
            response = requests.get(
                f"{self.api_url}/memory/profile/admin",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Memory Profile", True, f"Profile data: {len(data)} fields")
            else:
                self.log_test("Memory Profile", False, f"Status: {response.status_code}")
                return False
            
            # Test memory insights
            response = requests.get(
                f"{self.api_url}/memory/insights/admin?category=general",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get("insights", [])
                self.log_test("Memory Insights", True, f"Found {len(insights)} insights")
                return True
            else:
                self.log_test("Memory Insights", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Memory System", False, f"Error: {str(e)}")
            return False
    
    def test_system_prompts(self) -> bool:
        """Test system prompt management"""
        if not self.auth_token:
            self.log_test("System Prompts", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test getting system prompts
            response = requests.get(
                f"{self.api_url}/system-prompts",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                prompts = data.get("prompts", {})
                self.log_test("System Prompts", True, f"Found {len(prompts)} prompt modes")
                return len(prompts) > 0
            else:
                self.log_test("System Prompts", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Prompts", False, f"Error: {str(e)}")
            return False
    
    def test_redis_caching(self) -> bool:
        """Test Redis caching functionality"""
        if not self.auth_token:
            self.log_test("Redis Caching", False, "No auth token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {
                "query": "Test caching query",
                "mode": "qa",
                "model": "qwen2.5-coder:14b"
            }
            
            # First request (should cache)
            start_time = time.time()
            response1 = requests.post(
                f"{self.api_url}/ask",
                json=payload,
                headers=headers,
                timeout=60
            )
            first_time = time.time() - start_time
            
            # Second request (should be faster if cached)
            start_time = time.time()
            response2 = requests.post(
                f"{self.api_url}/ask",
                json=payload,
                headers=headers,
                timeout=60
            )
            second_time = time.time() - start_time
            
            if response1.status_code == 200 and response2.status_code == 200:
                speedup = first_time / second_time if second_time > 0 else 1
                self.log_test("Redis Caching", True, f"Speedup: {speedup:.2f}x")
                return speedup > 1.1  # At least 10% faster
            else:
                self.log_test("Redis Caching", False, "Request failed")
                return False
                
        except Exception as e:
            self.log_test("Redis Caching", False, f"Error: {str(e)}")
            return False
    
    def test_frontend_routing(self) -> bool:
        """Test frontend URL routing"""
        try:
            # Test main page
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code != 200:
                self.log_test("Frontend Main Page", False, f"Status: {response.status_code}")
                return False
            
            # Test memory page
            response = requests.get(f"{self.base_url}/memory", timeout=10)
            if response.status_code != 200:
                self.log_test("Frontend Memory Page", False, f"Status: {response.status_code}")
                return False
            
            self.log_test("Frontend Routing", True, "All routes accessible")
            return True
            
        except Exception as e:
            self.log_test("Frontend Routing", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Test Suite v3.0")
        logger.info("=" * 60)
        
        # Core functionality tests
        self.test_health_checks()
        self.authenticate()
        
        if self.auth_token:
            # RAG and search tests
            self.test_ollama_models()
            self.test_rag_functionality()
            self.test_web_search()
            self.test_obsidian_integration()
            self.test_research_mode()
            
            # Advanced features
            self.test_memory_system()
            self.test_system_prompts()
            self.test_redis_caching()
        
        # Frontend tests
        self.test_frontend_routing()
        
        # Calculate success rate
        success_rate = (self.test_results["passed"] / self.test_results["total_tests"]) * 100
        
        logger.info("=" * 60)
        logger.info(f"📊 Test Results Summary:")
        logger.info(f"   Total Tests: {self.test_results['total_tests']}")
        logger.info(f"   Passed: {self.test_results['passed']}")
        logger.info(f"   Failed: {self.test_results['failed']}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            logger.info(f"   Errors: {len(self.test_results['errors'])}")
            for error in self.test_results["errors"]:
                logger.error(f"   {error}")
        
        # Performance summary
        if self.test_results["performance"]:
            logger.info(f"   Performance Metrics:")
            for metric, value in self.test_results["performance"].items():
                logger.info(f"     {metric}: {value:.2f}s")
        
        # Feature summary
        if self.test_results["features"]:
            logger.info(f"   Feature Metrics:")
            for feature, value in self.test_results["features"].items():
                logger.info(f"     {feature}: {value}")
        
        return self.test_results

def main():
    """Run comprehensive test suite"""
    test_suite = ComprehensiveTestSuite()
    results = test_suite.run_comprehensive_tests()
    
    # Save results to file
    with open("COMPREHENSIVE_TEST_RESULTS_V3.md", "w") as f:
        f.write("# Comprehensive Test Results v3.0\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Tests**: {results['total_tests']}\n")
        f.write(f"**Passed**: {results['passed']}\n")
        f.write(f"**Failed**: {results['failed']}\n")
        f.write(f"**Success Rate**: {(results['passed']/results['total_tests']*100):.1f}%\n\n")
        
        if results["performance"]:
            f.write("## Performance Metrics\n\n")
            for metric, value in results["performance"].items():
                f.write(f"- **{metric}**: {value:.2f}s\n")
        
        if results["features"]:
            f.write("\n## Feature Metrics\n\n")
            for feature, value in results["features"].items():
                f.write(f"- **{feature}**: {value}\n")
        
        if results["errors"]:
            f.write("\n## Errors\n\n")
            for error in results["errors"]:
                f.write(f"- {error}\n")
    
    logger.info("📄 Results saved to COMPREHENSIVE_TEST_RESULTS_V3.md")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
