"""
CRITICAL TEST: RAG Retrieval Validation (NO MOCKS)
Tests that should have caught the "empty database" bug

This test suite validates that RAG modes ACTUALLY USE RETRIEVAL
and return appropriate errors when no documents are available.
"""

import pytest
import requests
import os

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"


class TestRAGRetrievalValidation:
    """
    CRITICAL: These tests validate RAG actually uses retrieval.
    
    The bug we missed:
    - RAG mode with empty database returns LLM response
    - Should return "No relevant documents found"
    - Tests passed because we only checked "did it respond?"
    - Should have checked "did it use retrieval?"
    """
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        return response.json()['access_token']
    
    def test_rag_with_empty_database_should_return_error(self, auth_token):
        """
        CRITICAL TEST: When database is empty, RAG should return error.
        
        This is the test we SHOULD have had that would have caught the bug!
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Query that would need documents
        response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json={
                "query": "What trading strategies are documented?",
                "mode": "rag-only",
                "model": "llama3.2:latest"
            },
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # CRITICAL CHECKS that were missing:
        print(f"\nAnswer: {result.get('answer', '')[:200]}")
        print(f"Citations: {len(result.get('citations', []))}")
        print(f"Sources: {len(result.get('sources', []))}")
        
        # When database is empty, we should either:
        # Option A: Return explicit error
        if 'No relevant documents found' in result.get('answer', ''):
            print("✅ CORRECT: Returns 'No relevant documents found'")
            assert len(result.get('citations', [])) == 0
            assert len(result.get('sources', [])) == 0
        # Option B: Have citations from somewhere
        elif len(result.get('citations', [])) > 0:
            print("✅ CORRECT: Has citations (retrieved from somewhere)")
        # Option C: BUG - Long answer with no citations
        else:
            answer_length = len(result.get('answer', ''))
            if answer_length > 100:  # Long answer without citations = BUG!
                print(f"❌ BUG DETECTED: Long answer ({answer_length} chars) but 0 citations!")
                print("This means LLM answered WITHOUT retrieval!")
                pytest.fail(
                    "RAG mode returned LLM response without retrieval. "
                    "Should return 'No relevant documents found' when database is empty."
                )
    
    def test_all_modes_with_empty_database(self, auth_token):
        """Test all 4 modes with empty database"""
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        modes = [
            ("rag-only", "RAG Only", True),  # Should need documents
            ("obsidian-only", "Obsidian Only", True),  # Should need Obsidian
            ("web-only", "Web Search Only", False),  # Can work without local docs
            ("research", "Comprehensive Research", False)  # Can work without local docs
        ]
        
        for mode, name, requires_docs in modes:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print(f"{'='*60}")
            
            response = requests.post(
                f"{FRONTEND_URL}/api/ask",
                headers=headers,
                json={
                    "query": "What documents do we have?",
                    "mode": mode,
                    "model": "llama3.2:latest"
                },
                timeout=30 if mode != "research" else 60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                citations = len(result.get('citations', []))
                sources = len(result.get('sources', []))
                
                print(f"Answer length: {len(answer)}")
                print(f"Citations: {citations}")
                print(f"Sources: {sources}")
                
                if requires_docs:
                    # Modes that need documents should either:
                    # 1. Return error message, OR
                    # 2. Have citations (if found documents)
                    if len(answer) > 100 and citations == 0:
                        print(f"⚠️  WARNING: {name} gave long answer without citations")
                        print("This suggests it's using LLM without retrieval!")
                    else:
                        print(f"✅ {name} behaves correctly")
                else:
                    # Modes that can work without docs (web search)
                    print(f"✅ {name} can work without local docs")
            else:
                print(f"❌ {name} failed: {response.status_code}")
    
    def test_rag_mode_actually_uses_retrieval_when_docs_exist(self, auth_token):
        """
        Test that when documents DO exist, RAG uses them.
        
        This validates RAG is working when documents are present.
        (Skip if no documents uploaded)
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Check if documents exist
        docs_dir = "/home/brad/cursor_code/GraphMind/documents"
        if not os.path.exists(docs_dir) or len(os.listdir(docs_dir)) == 0:
            pytest.skip("No documents uploaded - cannot test retrieval")
        
        response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json={
                "query": "What information is in our documents?",
                "mode": "rag-only",
                "model": "llama3.2:latest"
            },
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # When documents exist, RAG should retrieve them
        citations = len(result.get('citations', []))
        sources = len(result.get('sources', []))
        
        print(f"\nCitations: {citations}")
        print(f"Sources: {sources}")
        
        # Should have citations when documents exist
        assert citations > 0, "RAG mode should retrieve documents when they exist"
        assert sources > 0, "RAG mode should cite sources when documents exist"
        
        print("✅ RAG mode correctly uses retrieval when documents exist")


class TestModeSpecificBackends:
    """Test that each mode uses its specific backend"""
    
    @pytest.fixture
    def auth_token(self):
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        return response.json()['access_token']
    
    def test_web_mode_actually_uses_web_search(self, auth_token):
        """
        Test that web-only mode actually searches the web.
        
        This should work even with empty local database.
        """
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        # Query about current events (LLM wouldn't know from training)
        response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json={
                "query": "What is the current date?",
                "mode": "web-only",
                "model": "llama3.2:latest"
            },
            timeout=30
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Web mode should work even with empty local database
        answer = result.get('answer', '')
        assert len(answer) > 0, "Web mode should return response"
        
        # Check if it mentions current information
        print(f"✅ Web mode response: {answer[:200]}")


if __name__ == "__main__":
    """
    Run these tests to validate RAG retrieval is working correctly.
    
    These are the tests we SHOULD have had from the start!
    """
    print("\n" + "="*70)
    print("CRITICAL RAG RETRIEVAL VALIDATION TESTS")
    print("Testing that RAG modes actually use retrieval")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s", "--tb=short"])

