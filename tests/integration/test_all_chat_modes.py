"""
Test ALL Chat Modes with Real Services (NO MOCKS)
This test should have caught the "No relevant documents found" issue!
"""

import pytest
import requests
import time

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"


class TestAllChatModes:
    """Test all 4 chat modes - this is what we SHOULD have tested!"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{FRONTEND_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        return response.json()['access_token']
    
    def test_rag_only_mode(self, auth_token):
        """Test RAG Only mode"""
        print("\n[TEST: RAG ONLY]")
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        data = {
            "query": "What is GraphMind?",
            "mode": "rag_only",
            "model": "llama3.2:latest"
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/api/ask",
            headers=headers,
            json=data,
            timeout=60
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = result.get('answer', '')
        
        print(f"Answer: {answer[:200]}")
        
        # CRITICAL CHECK: Should not return "No relevant documents found"
        assert 'No relevant documents found' not in answer, \
            "RAG mode returned 'No relevant documents found' - document ingestion issue!"
        
        assert len(answer) > 0, "Empty answer from RAG mode"
        print("✓ RAG Only mode: WORKING")
    
    def test_obsidian_only_mode(self, auth_token):
        """Test Obsidian Only mode"""
        print("\n[TEST: OBSIDIAN ONLY]")
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        data = {
            "query": "What is GraphMind?",
            "mode": "obsidian_only",
            "model": "llama3.2:latest"
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/api/ask-obsidian",
            headers=headers,
            json=data,
            timeout=60
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = result.get('answer', result.get('response', ''))
        
        print(f"Answer: {answer[:200]}")
        
        # CRITICAL CHECK
        if 'No relevant documents found' in answer:
            pytest.fail(
                "Obsidian mode returned 'No relevant documents found'!\n"
                "Possible causes:\n"
                "1. Obsidian vault not configured\n"
                "2. No notes in Obsidian vault\n"
                "3. Obsidian MCP server not running\n"
                "4. Obsidian API not accessible"
            )
        
        print("✓ Obsidian Only mode: WORKING")
    
    def test_web_search_only_mode(self, auth_token):
        """Test Web Search Only mode"""
        print("\n[TEST: WEB SEARCH ONLY]")
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        data = {
            "query": "What is Python programming language?",  # Something that should be findable on web
            "mode": "web_search_only",
            "model": "llama3.2:latest"
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/api/ask-enhanced",
            headers=headers,
            json=data,
            timeout=60
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = result.get('answer', result.get('response', ''))
        
        print(f"Answer: {answer[:200]}")
        
        # CRITICAL CHECK
        if 'No relevant documents found' in answer:
            pytest.fail(
                "Web Search mode returned 'No relevant documents found'!\n"
                "Possible causes:\n"
                "1. SearXNG not running\n"
                "2. SearXNG not accessible from backend\n"
                "3. Web search provider not configured\n"
                "4. Network/firewall blocking web requests"
            )
        
        assert 'Python' in answer or 'python' in answer.lower(), \
            "Web search should find information about Python"
        
        print("✓ Web Search Only mode: WORKING")
    
    def test_comprehensive_research_mode(self, auth_token):
        """Test Comprehensive Research mode (combines all sources)"""
        print("\n[TEST: COMPREHENSIVE RESEARCH]")
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        data = {
            "query": "What is artificial intelligence?",
            "mode": "comprehensive_research",
            "model": "llama3.2:latest"
        }
        
        response = requests.post(
            f"{FRONTEND_URL}/api/ask-research",
            headers=headers,
            json=data,
            timeout=60
        )
        
        assert response.status_code == 200
        result = response.json()
        answer = result.get('answer', result.get('response', ''))
        
        print(f"Answer: {answer[:200]}")
        
        # CRITICAL CHECK
        if 'No relevant documents found' in answer:
            pytest.fail(
                "Comprehensive Research mode returned 'No relevant documents found'!\n"
                "Possible causes:\n"
                "1. All data sources empty/not configured\n"
                "2. RAG documents not ingested\n"
                "3. Web search not working\n"
                "4. Obsidian vault empty"
            )
        
        print("✓ Comprehensive Research mode: WORKING")


class TestDataSourceAvailability:
    """Test that all data sources are properly configured"""
    
    def test_rag_documents_exist(self):
        """Test that RAG has documents ingested"""
        print("\n[TEST: RAG Documents]")
        
        try:
            response = requests.get(f"{BACKEND_URL}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                total_docs = stats.get('total_documents', 0)
                print(f"Total documents: {total_docs}")
                
                if total_docs == 0:
                    pytest.fail(
                        "No documents ingested in RAG!\n"
                        "Please ingest documents:\n"
                        "1. Upload PDFs via UI\n"
                        "2. Or run: curl -X POST http://localhost:8000/ingest"
                    )
                
                print(f"✓ RAG has {total_docs} documents")
            else:
                pytest.skip("Stats endpoint not available")
        except Exception as e:
            pytest.skip(f"Cannot check RAG stats: {e}")
    
    def test_web_search_available(self):
        """Test that SearXNG web search is available"""
        print("\n[TEST: Web Search Service]")
        
        try:
            # Try to access SearXNG
            response = requests.get("http://localhost:8080", timeout=5)
            print(f"SearXNG status: {response.status_code}")
            
            if response.status_code != 200:
                pytest.fail(
                    "SearXNG not accessible!\n"
                    "Check if graphmind-searxng container is running:\n"
                    "docker ps | grep searxng"
                )
            
            print("✓ SearXNG is accessible")
        except Exception as e:
            pytest.fail(f"SearXNG not reachable: {e}")
    
    def test_obsidian_configured(self):
        """Test that Obsidian vault is configured"""
        print("\n[TEST: Obsidian Configuration]")
        
        # Check if obsidian vault exists
        import os
        vault_path = "/home/brad/cursor_code/GraphMind/obsidian_vault"
        
        if not os.path.exists(vault_path):
            pytest.fail(
                f"Obsidian vault not found at {vault_path}!\n"
                "Create vault or configure OBSIDIAN_VAULT_PATH"
            )
        
        # Check if vault has any notes
        notes = [f for f in os.listdir(vault_path) if f.endswith('.md')]
        if len(notes) == 0:
            pytest.fail(
                f"Obsidian vault is empty (no .md files)!\n"
                "Add some notes to {vault_path}"
            )
        
        print(f"✓ Obsidian vault has {len(notes)} notes")


if __name__ == "__main__":
    """
    This is the test suite we SHOULD have run to catch the issue!
    
    Run with:
        python3 -m pytest tests/integration/test_all_chat_modes.py -v -s
    """
    print("\n" + "="*70)
    print("TESTING ALL CHAT MODES (NO MOCKS)")
    print("This test catches 'No relevant documents found' errors!")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s", "--tb=short"])

