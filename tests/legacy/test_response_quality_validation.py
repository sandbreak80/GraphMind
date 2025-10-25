#!/usr/bin/env python3
"""Validate response quality using Ollama LLM to ensure responses are real and relevant."""
import requests
import time
import statistics
import json
import random
from datetime import datetime

def test_response_quality_validation():
    base_url = "http://localhost:8002"
    ollama_url = "http://localhost:11434"
    
    # Get authentication token
    print("🔐 Authenticating...")
    response = requests.post(
        f"{base_url}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful!")
    
    print("\n🔍 RESPONSE QUALITY VALIDATION TEST")
    print("=" * 80)
    print("🎯 Using Ollama LLM to validate response quality and relevance")
    print("=" * 80)
    
    # Test a diverse set of queries
    test_queries = [
        {
            "query": "What is RSI in trading?",
            "expected_keywords": ["Relative Strength Index", "momentum", "indicator", "trading"],
            "description": "Trading indicator query"
        },
        {
            "query": "Explain momentum trading strategy",
            "expected_keywords": ["momentum", "strategy", "trend", "trading"],
            "description": "Trading strategy query"
        },
        {
            "query": "What is 2 + 2?",
            "expected_keywords": ["4", "four"],
            "description": "Simple math query"
        },
        {
            "query": "Compare MACD and RSI indicators",
            "expected_keywords": ["MACD", "RSI", "indicator", "compare"],
            "description": "Comparison query"
        },
        {
            "query": "How do you identify support and resistance levels?",
            "expected_keywords": ["support", "resistance", "levels", "price"],
            "description": "Technical analysis query"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_queries, 1):
        query = test_case["query"]
        expected_keywords = test_case["expected_keywords"]
        description = test_case["description"]
        
        print(f"\n{i}. {description}: {query}")
        
        # Get response from our system
        start_time = time.time()
        try:
            response = requests.post(
                f"{base_url}/ask",
                headers=headers,
                json={
                    "query": query,
                    "temperature": 0.1,
                    "max_tokens": 1000
                },
                timeout=30
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                
                print(f"   ✅ System Response: {response_time:.2f}s")
                print(f"   📝 Answer length: {len(answer)} characters")
                print(f"   📝 Answer preview: {answer[:200]}...")
                
                # Validate with Ollama LLM
                print(f"   🔍 Validating with Ollama LLM...")
                validation_result = validate_response_with_ollama(answer, query, expected_keywords, ollama_url)
                
                # Check for expected keywords
                keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer.lower())
                keyword_score = keyword_matches / len(expected_keywords) * 100
                
                result = {
                    'query': query,
                    'response_time': response_time,
                    'answer_length': len(answer),
                    'answer_preview': answer[:200],
                    'keyword_score': keyword_score,
                    'keyword_matches': keyword_matches,
                    'expected_keywords': expected_keywords,
                    'ollama_validation': validation_result,
                    'success': True
                }
                
                print(f"   🎯 Keyword matches: {keyword_matches}/{len(expected_keywords)} ({keyword_score:.1f}%)")
                print(f"   🤖 Ollama validation: {validation_result['overall_score']}/10")
                print(f"   📊 Ollama summary: {validation_result['summary']}")
                
            else:
                print(f"   ❌ System failed: {response.status_code}")
                result = {
                    'query': query,
                    'response_time': 0,
                    'answer_length': 0,
                    'answer_preview': '',
                    'keyword_score': 0,
                    'keyword_matches': 0,
                    'expected_keywords': expected_keywords,
                    'ollama_validation': {'overall_score': 0, 'summary': 'System failed'},
                    'success': False
                }
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            result = {
                'query': query,
                'response_time': 0,
                'answer_length': 0,
                'answer_preview': '',
                'keyword_score': 0,
                'keyword_matches': 0,
                'expected_keywords': expected_keywords,
                'ollama_validation': {'overall_score': 0, 'summary': f'Error: {e}'},
                'success': False
            }
        
        results.append(result)
    
    # Analysis
    print(f"\n📊 QUALITY VALIDATION ANALYSIS")
    print("=" * 80)
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        # Keyword analysis
        keyword_scores = [r['keyword_score'] for r in successful_results]
        avg_keyword_score = statistics.mean(keyword_scores)
        
        # Ollama validation analysis
        ollama_scores = [r['ollama_validation']['overall_score'] for r in successful_results if 'ollama_validation' in r]
        avg_ollama_score = statistics.mean(ollama_scores) if ollama_scores else 0
        
        print(f"📈 Quality Metrics:")
        print(f"   Total queries tested: {len(results)}")
        print(f"   Successful responses: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
        print(f"   Average keyword score: {avg_keyword_score:.1f}%")
        print(f"   Average Ollama score: {avg_ollama_score:.1f}/10")
        
        # Response time analysis
        response_times = [r['response_time'] for r in successful_results]
        print(f"   Average response time: {statistics.mean(response_times):.2f}s")
        print(f"   Min response time: {min(response_times):.2f}s")
        print(f"   Max response time: {max(response_times):.2f}s")
        
        # Quality assessment
        print(f"\n🎯 Quality Assessment:")
        
        if avg_keyword_score >= 80 and avg_ollama_score >= 7:
            print("   ✅ RESPONSE QUALITY: EXCELLENT")
            print("   Responses are highly relevant and accurate!")
        elif avg_keyword_score >= 60 and avg_ollama_score >= 5:
            print("   ✅ RESPONSE QUALITY: GOOD")
            print("   Responses are mostly relevant and accurate!")
        else:
            print("   ⚠️  RESPONSE QUALITY: NEEDS IMPROVEMENT")
            print("   Responses may not be relevant or accurate!")
        
        # Detailed results
        print(f"\n📝 Detailed Results:")
        for i, result in enumerate(successful_results, 1):
            print(f"\n   {i}. Query: {result['query']}")
            print(f"      Keywords: {result['keyword_matches']}/{len(result['expected_keywords'])} matched")
            print(f"      Ollama score: {result['ollama_validation']['overall_score']}/10")
            print(f"      Response: {result['answer_preview']}...")
    
    else:
        print("   ❌ No successful responses to analyze!")
    
    return results

def validate_response_with_ollama(answer, original_query, expected_keywords, ollama_url):
    """Use Ollama to validate response quality."""
    try:
        # Create validation prompt
        validation_prompt = f"""You are a quality assurance validator for AI responses. Please evaluate the following response based on the original query and expected content.

Original Query: "{original_query}"
Expected Keywords: {expected_keywords}

Response to Evaluate:
"{answer}"

Please provide a score from 1-10 and brief explanation for each of these criteria:
1. Relevance (1-10): Does the response directly address the query?
2. Accuracy (1-10): Is the information factually correct?
3. Completeness (1-10): Does it fully answer the query?
4. Clarity (1-10): Is the response clear and well-structured?
5. Keyword Coverage (1-10): Does it contain the expected keywords/concepts?

Respond in JSON format:
{{
    "relevance_score": X,
    "accuracy_score": X,
    "completeness_score": X,
    "clarity_score": X,
    "keyword_score": X,
    "overall_score": X,
    "summary": "Brief explanation of the overall quality"
}}"""

        # Send to Ollama
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": "llama3.1:latest",
                "prompt": validation_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            validation_text = result.get('response', '')
            
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', validation_text, re.DOTALL)
                if json_match:
                    validation_data = json.loads(json_match.group())
                    return validation_data
                else:
                    # Fallback: basic scoring
                    return {
                        "relevance_score": 5,
                        "accuracy_score": 5,
                        "completeness_score": 5,
                        "clarity_score": 5,
                        "keyword_score": 5,
                        "overall_score": 5,
                        "summary": "Could not parse validation response"
                    }
            except json.JSONDecodeError:
                # Fallback: basic scoring
                return {
                    "relevance_score": 5,
                    "accuracy_score": 5,
                    "completeness_score": 5,
                    "clarity_score": 5,
                    "keyword_score": 5,
                    "overall_score": 5,
                    "summary": "Validation response parsing failed"
                }
        else:
            return {
                "relevance_score": 0,
                "accuracy_score": 0,
                "completeness_score": 0,
                "clarity_score": 0,
                "keyword_score": 0,
                "overall_score": 0,
                "summary": "Validation failed"
            }
            
    except Exception as e:
        return {
            "relevance_score": 0,
            "accuracy_score": 0,
            "completeness_score": 0,
            "clarity_score": 0,
            "keyword_score": 0,
            "overall_score": 0,
            "summary": f"Validation error: {str(e)}"
        }

if __name__ == "__main__":
    results = test_response_quality_validation()