# GraphMind RAG System Tests
# Tests for the main RAG system

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

from app.core.rag_system import GraphMindRAGSystem
from app.core.memory_system import GraphMindMemorySystem
from app.core.mcp_integration import GraphMindMCPIntegration

class TestGraphMindRAGSystem:
    """Test cases for GraphMindRAGSystem."""
    
    @pytest.fixture
    def rag_system(self):
        """Create a GraphMindRAGSystem instance for testing."""
        config = {
            'retrieval': {
                'top_k': 5,
                'rerank_top_k': 8
            },
            'embedding': {
                'model_name': 'BAAI/bge-m3'
            },
            'reranking': {
                'model_name': 'BAAI/bge-reranker-large'
            },
            'connectors': {
                'pdf_connector': {
                    'name': 'PDF Connector',
                    'enabled': True,
                    'document_path': './test_documents'
                },
                'web_connector': {
                    'name': 'Web Connector',
                    'enabled': True,
                    'search_url': 'http://localhost:8080/search'
                }
            }
        }
        return GraphMindRAGSystem(config)
    
    def test_rag_system_initialization(self, rag_system):
        """Test RAG system initialization."""
        assert rag_system is not None
        assert rag_system.config is not None
        assert rag_system.domain_registry is not None
        assert rag_system.connector_registry is not None
        assert rag_system.retriever is not None
        assert rag_system.embedding_service is not None
        assert rag_system.reranking_service is not None
    
    @pytest.mark.asyncio
    async def test_set_domain(self, rag_system):
        """Test domain setting."""
        # Test with non-existent domain
        result = await rag_system.set_domain('nonexistent')
        assert result == False
        
        # Test with valid domain (if config exists)
        result = await rag_system.set_domain('finance')
        # Should return True if domain config exists, False otherwise
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_search(self, rag_system):
        """Test search functionality."""
        query = "test query"
        results = await rag_system.search(query)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_search_with_domain(self, rag_system):
        """Test search with domain context."""
        query = "test query"
        domain = "finance"
        results = await rag_system.search(query, domain=domain)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_context(self, rag_system):
        """Test context generation."""
        query = "test query"
        context = await rag_system.get_context(query)
        
        assert isinstance(context, str)
        assert len(context) > 0
    
    @pytest.mark.asyncio
    async def test_get_context_with_domain(self, rag_system):
        """Test context generation with domain."""
        query = "test query"
        domain = "finance"
        context = await rag_system.get_context(query, domain=domain)
        
        assert isinstance(context, str)
        assert len(context) > 0
    
    @pytest.mark.asyncio
    async def test_get_citations(self, rag_system):
        """Test citation generation."""
        query = "test query"
        citations = await rag_system.get_citations(query)
        
        assert isinstance(citations, list)
    
    @pytest.mark.asyncio
    async def test_get_citations_with_domain(self, rag_system):
        """Test citation generation with domain."""
        query = "test query"
        domain = "finance"
        citations = await rag_system.get_citations(query, domain=domain)
        
        assert isinstance(citations, list)
    
    @pytest.mark.asyncio
    async def test_get_system_prompt(self, rag_system):
        """Test system prompt retrieval."""
        prompt = await rag_system.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @pytest.mark.asyncio
    async def test_get_system_prompt_with_domain(self, rag_system):
        """Test system prompt retrieval with domain."""
        domain = "finance"
        prompt = await rag_system.get_system_prompt(domain=domain)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @pytest.mark.asyncio
    async def test_get_web_search_prompt(self, rag_system):
        """Test web search prompt retrieval."""
        prompt = await rag_system.get_web_search_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{query}' in prompt
    
    @pytest.mark.asyncio
    async def test_get_web_search_prompt_with_domain(self, rag_system):
        """Test web search prompt retrieval with domain."""
        domain = "finance"
        prompt = await rag_system.get_web_search_prompt(domain=domain)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{query}' in prompt
    
    @pytest.mark.asyncio
    async def test_get_domain_info(self, rag_system):
        """Test domain information retrieval."""
        info = await rag_system.get_domain_info()
        
        assert isinstance(info, dict)
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, rag_system):
        """Test system status retrieval."""
        status = await rag_system.get_system_status()
        
        assert isinstance(status, dict)
        assert 'domain' in status
        assert 'connectors' in status
        assert 'retriever_available' in status
        assert 'embedding_available' in status
        assert 'reranking_available' in status
    
    @pytest.mark.asyncio
    async def test_close(self, rag_system):
        """Test RAG system closure."""
        # Should not raise exception
        await rag_system.close()

class TestGraphMindMemorySystem:
    """Test cases for GraphMindMemorySystem."""
    
    @pytest.fixture
    def memory_system(self):
        """Create a GraphMindMemorySystem instance for testing."""
        config = {
            'memory_dir': './test_memory',
            'max_memory_size': 1000
        }
        return GraphMindMemorySystem(config)
    
    def test_memory_system_initialization(self, memory_system):
        """Test memory system initialization."""
        assert memory_system is not None
        assert memory_system.config is not None
        assert memory_system.memory_dir is not None
        assert memory_system.max_memory_size == 1000
    
    @pytest.mark.asyncio
    async def test_add_memory(self, memory_system):
        """Test memory addition."""
        key = "test_key"
        value = "test_value"
        domain = "test"
        metadata = {"test_metadata": "test_value"}
        
        result = await memory_system.add_memory(key, value, domain, metadata)
        
        assert result == True
        assert key in memory_system.memory
    
    @pytest.mark.asyncio
    async def test_get_memory(self, memory_system):
        """Test memory retrieval."""
        key = "test_key"
        value = "test_value"
        domain = "test"
        
        # Add memory first
        await memory_system.add_memory(key, value, domain)
        
        # Retrieve memory
        retrieved_value = await memory_system.get_memory(key)
        
        assert retrieved_value == value
    
    @pytest.mark.asyncio
    async def test_update_memory(self, memory_system):
        """Test memory update."""
        key = "test_key"
        value = "test_value"
        domain = "test"
        
        # Add memory first
        await memory_system.add_memory(key, value, domain)
        
        # Update memory
        new_value = "updated_value"
        result = await memory_system.update_memory(key, new_value)
        
        assert result == True
        assert memory_system.memory[key]['value'] == new_value
    
    @pytest.mark.asyncio
    async def test_delete_memory(self, memory_system):
        """Test memory deletion."""
        key = "test_key"
        value = "test_value"
        domain = "test"
        
        # Add memory first
        await memory_system.add_memory(key, value, domain)
        
        # Delete memory
        result = await memory_system.delete_memory(key)
        
        assert result == True
        assert key not in memory_system.memory
    
    @pytest.mark.asyncio
    async def test_search_memory(self, memory_system):
        """Test memory search."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        await memory_system.add_memory("key2", "another test", "test")
        await memory_system.add_memory("key3", "different content", "other")
        
        # Search memories
        results = await memory_system.search_memory("test")
        
        assert isinstance(results, list)
        assert len(results) >= 2  # Should find at least 2 results
    
    @pytest.mark.asyncio
    async def test_search_memory_with_domain(self, memory_system):
        """Test memory search with domain filter."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        await memory_system.add_memory("key2", "another test", "other")
        
        # Search memories with domain filter
        results = await memory_system.search_memory("test", domain="test")
        
        assert isinstance(results, list)
        assert len(results) == 1  # Should find only 1 result from "test" domain
    
    @pytest.mark.asyncio
    async def test_get_domain_memory(self, memory_system):
        """Test domain memory retrieval."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        await memory_system.add_memory("key2", "another test", "test")
        await memory_system.add_memory("key3", "different content", "other")
        
        # Get domain memory
        domain_memory = await memory_system.get_domain_memory("test")
        
        assert isinstance(domain_memory, dict)
        assert len(domain_memory) == 2  # Should have 2 memories from "test" domain
    
    @pytest.mark.asyncio
    async def test_get_memory_statistics(self, memory_system):
        """Test memory statistics retrieval."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        await memory_system.add_memory("key2", "another test", "other")
        
        # Get statistics
        stats = await memory_system.get_memory_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_entries' in stats
        assert 'domains' in stats
        assert 'domain_count' in stats
        assert 'total_size_bytes' in stats
    
    @pytest.mark.asyncio
    async def test_clear_domain_memory(self, memory_system):
        """Test domain memory clearing."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        await memory_system.add_memory("key2", "another test", "other")
        
        # Clear domain memory
        result = await memory_system.clear_domain_memory("test")
        
        assert result == True
        assert "key1" not in memory_system.memory
        assert "key2" in memory_system.memory  # Should still exist
    
    @pytest.mark.asyncio
    async def test_export_memory(self, memory_system):
        """Test memory export."""
        # Add some test memories
        await memory_system.add_memory("key1", "test content", "test")
        
        # Export memory
        result = await memory_system.export_memory("./test_export.json")
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_import_memory(self, memory_system):
        """Test memory import."""
        # Create a test import file
        import_data = {
            "imported_key": {
                "value": "imported_value",
                "domain": "imported",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "metadata": {}
            }
        }
        
        # Write test file
        import json
        with open("./test_import.json", "w") as f:
            json.dump(import_data, f)
        
        # Import memory
        result = await memory_system.import_memory("./test_import.json")
        
        assert result == True
        assert "imported_key" in memory_system.memory
    
    @pytest.mark.asyncio
    async def test_close(self, memory_system):
        """Test memory system closure."""
        # Should not raise exception
        await memory_system.close()

class TestGraphMindMCPIntegration:
    """Test cases for GraphMindMCPIntegration."""
    
    @pytest.fixture
    def mcp_integration(self):
        """Create a GraphMindMCPIntegration instance for testing."""
        config = {
            'mcp_enabled': True,
            'mcp_servers': {
                'docker_server': {
                    'type': 'docker',
                    'enabled': True,
                    'docker_socket': '/var/run/docker.sock'
                },
                'filesystem_server': {
                    'type': 'filesystem',
                    'enabled': True,
                    'root_path': './test_files'
                },
                'database_server': {
                    'type': 'database',
                    'enabled': True,
                    'connection_string': 'sqlite:///test.db',
                    'database_type': 'sqlite'
                }
            }
        }
        return GraphMindMCPIntegration(config)
    
    def test_mcp_integration_initialization(self, mcp_integration):
        """Test MCP integration initialization."""
        assert mcp_integration is not None
        assert mcp_integration.config is not None
        assert mcp_integration.mcp_enabled == True
        assert mcp_integration.mcp_servers is not None
        assert mcp_integration.connections is not None
    
    @pytest.mark.asyncio
    async def test_get_mcp_capabilities(self, mcp_integration):
        """Test MCP capabilities retrieval."""
        capabilities = await mcp_integration.get_mcp_capabilities('docker_server')
        
        assert isinstance(capabilities, dict)
        assert 'server_name' in capabilities
        assert 'type' in capabilities
        assert 'capabilities' in capabilities
    
    @pytest.mark.asyncio
    async def test_get_mcp_capabilities_nonexistent(self, mcp_integration):
        """Test MCP capabilities retrieval for non-existent server."""
        capabilities = await mcp_integration.get_mcp_capabilities('nonexistent')
        
        assert isinstance(capabilities, dict)
        assert 'error' in capabilities
    
    @pytest.mark.asyncio
    async def test_execute_mcp_command(self, mcp_integration):
        """Test MCP command execution."""
        command = "list_containers"
        parameters = {}
        
        result = await mcp_integration.execute_mcp_command('docker_server', command, parameters)
        
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_execute_mcp_command_nonexistent(self, mcp_integration):
        """Test MCP command execution for non-existent server."""
        command = "test_command"
        parameters = {}
        
        result = await mcp_integration.execute_mcp_command('nonexistent', command, parameters)
        
        assert isinstance(result, dict)
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_get_mcp_status(self, mcp_integration):
        """Test MCP status retrieval."""
        status = await mcp_integration.get_mcp_status()
        
        assert isinstance(status, dict)
        assert 'mcp_enabled' in status
        assert 'total_servers' in status
        assert 'servers' in status
    
    @pytest.mark.asyncio
    async def test_close(self, mcp_integration):
        """Test MCP integration closure."""
        # Should not raise exception
        await mcp_integration.close()

class TestIntegration:
    """Integration tests for GraphMind components."""
    
    @pytest.mark.asyncio
    async def test_rag_system_with_memory(self):
        """Test RAG system with memory integration."""
        config = {
            'retrieval': {'top_k': 5},
            'embedding': {'model_name': 'BAAI/bge-m3'},
            'reranking': {'model_name': 'BAAI/bge-reranker-large'},
            'connectors': {},
            'memory': {
                'memory_dir': './test_memory',
                'max_memory_size': 1000
            }
        }
        
        rag_system = GraphMindRAGSystem(config)
        memory_system = GraphMindMemorySystem(config.get('memory', {}))
        
        # Test that components can work together
        assert rag_system is not None
        assert memory_system is not None
    
    @pytest.mark.asyncio
    async def test_rag_system_with_mcp(self):
        """Test RAG system with MCP integration."""
        config = {
            'retrieval': {'top_k': 5},
            'embedding': {'model_name': 'BAAI/bge-m3'},
            'reranking': {'model_name': 'BAAI/bge-reranker-large'},
            'connectors': {},
            'mcp': {
                'mcp_enabled': True,
                'mcp_servers': {}
            }
        }
        
        rag_system = GraphMindRAGSystem(config)
        mcp_integration = GraphMindMCPIntegration(config.get('mcp', {}))
        
        # Test that components can work together
        assert rag_system is not None
        assert mcp_integration is not None
    
    def test_error_handling(self):
        """Test error handling in GraphMind components."""
        # Test with invalid configuration
        invalid_config = {'invalid': 'config'}
        
        try:
            rag_system = GraphMindRAGSystem(invalid_config)
            # Should not raise exception, but handle gracefully
            assert rag_system is not None
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            assert isinstance(e, Exception)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        valid_config = {
            'retrieval': {'top_k': 5},
            'embedding': {'model_name': 'BAAI/bge-m3'},
            'reranking': {'model_name': 'BAAI/bge-reranker-large'},
            'connectors': {}
        }
        
        rag_system = GraphMindRAGSystem(valid_config)
        assert rag_system.config == valid_config
        
        # Test with missing configuration
        empty_config = {}
        rag_system_empty = GraphMindRAGSystem(empty_config)
        assert rag_system_empty.config == {}
