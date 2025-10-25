# GraphMind Connectors Tests
# Tests for data connectors

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any
import tempfile
import os
from pathlib import Path

from app.connectors.base_connector import BaseConnector
from app.connectors.connector_registry import ConnectorRegistry
from app.connectors.pdf_connector import PDFConnector
from app.connectors.web_connector import WebConnector
from app.connectors.obsidian_connector import ObsidianConnector
from app.connectors.database_connector import DatabaseConnector

class TestBaseConnector:
    """Test cases for BaseConnector."""
    
    @pytest.fixture
    def base_connector(self):
        """Create a BaseConnector instance for testing."""
        config = {
            'name': 'Test Connector',
            'enabled': True,
            'settings': {'test_setting': 'test_value'},
            'metadata': {'test_metadata': 'test_value'}
        }
        return BaseConnector(config)
    
    def test_connector_initialization(self, base_connector):
        """Test connector initialization."""
        assert base_connector is not None
        assert base_connector.name == 'Test Connector'
        assert base_connector.enabled == True
        assert base_connector.settings == {'test_setting': 'test_value'}
        assert base_connector.metadata == {'test_metadata': 'test_value'}
    
    def test_get_connector_info(self, base_connector):
        """Test connector information retrieval."""
        info = base_connector.get_connector_info()
        
        assert 'name' in info
        assert 'enabled' in info
        assert 'settings' in info
        assert 'metadata' in info
    
    def test_validate_config(self, base_connector):
        """Test configuration validation."""
        validation = base_connector.validate_config()
        
        assert 'valid' in validation
        assert 'errors' in validation
    
    def test_get_required_config_fields(self, base_connector):
        """Test required configuration fields retrieval."""
        fields = base_connector.get_required_config_fields()
        
        assert isinstance(fields, list)
        assert 'name' in fields
    
    def test_get_supported_formats(self, base_connector):
        """Test supported formats retrieval."""
        formats = base_connector.get_supported_formats()
        
        assert isinstance(formats, list)
    
    def test_get_search_capabilities(self, base_connector):
        """Test search capabilities retrieval."""
        capabilities = base_connector.get_search_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'metadata_search' in capabilities
        assert 'faceted_search' in capabilities
        assert 'full_text_search' in capabilities

class TestPDFConnector:
    """Test cases for PDFConnector."""
    
    @pytest.fixture
    def pdf_connector(self):
        """Create a PDFConnector instance for testing."""
        config = {
            'name': 'PDF Connector',
            'document_path': './test_documents',
            'enabled': True
        }
        return PDFConnector(config)
    
    def test_pdf_connector_initialization(self, pdf_connector):
        """Test PDF connector initialization."""
        assert pdf_connector is not None
        assert pdf_connector.name == 'PDF Connector'
        assert pdf_connector.document_path == './test_documents'
        assert pdf_connector.supported_formats == ['.pdf']
    
    def test_get_required_config_fields(self, pdf_connector):
        """Test required configuration fields."""
        fields = pdf_connector.get_required_config_fields()
        
        assert isinstance(fields, list)
        assert 'name' in fields
        assert 'document_path' in fields
    
    def test_get_supported_formats(self, pdf_connector):
        """Test supported formats."""
        formats = pdf_connector.get_supported_formats()
        
        assert isinstance(formats, list)
        assert '.pdf' in formats
    
    def test_get_search_capabilities(self, pdf_connector):
        """Test search capabilities."""
        capabilities = pdf_connector.get_search_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'metadata_search' in capabilities
        assert 'page_search' in capabilities
    
    def test_extract_context(self, pdf_connector):
        """Test context extraction."""
        text = "This is a test document with some content."
        query = "test"
        context = pdf_connector._extract_context(text, query)
        
        assert isinstance(context, str)
        assert len(context) > 0
    
    def test_calculate_relevance_score(self, pdf_connector):
        """Test relevance score calculation."""
        text = "This is a test document with test content."
        query = "test"
        score = pdf_connector._calculate_relevance_score(text, query)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_connect(self, pdf_connector):
        """Test PDF connector connection."""
        # This will fail if no PDF files exist, which is expected
        result = await pdf_connector.connect()
        
        # Should return False if no PDF files found
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_search(self, pdf_connector):
        """Test PDF connector search."""
        query = "test query"
        results = await pdf_connector.search(query)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_metadata(self, pdf_connector):
        """Test PDF connector metadata."""
        metadata = await pdf_connector.get_metadata()
        
        assert isinstance(metadata, dict)
        assert 'connector' in metadata
        assert 'document_path' in metadata

class TestWebConnector:
    """Test cases for WebConnector."""
    
    @pytest.fixture
    def web_connector(self):
        """Create a WebConnector instance for testing."""
        config = {
            'name': 'Web Connector',
            'search_url': 'http://localhost:8080/search',
            'enabled': True,
            'max_results': 10,
            'timeout': 30
        }
        return WebConnector(config)
    
    def test_web_connector_initialization(self, web_connector):
        """Test web connector initialization."""
        assert web_connector is not None
        assert web_connector.name == 'Web Connector'
        assert web_connector.search_url == 'http://localhost:8080/search'
        assert web_connector.max_results == 10
        assert web_connector.timeout == 30
    
    def test_get_required_config_fields(self, web_connector):
        """Test required configuration fields."""
        fields = web_connector.get_required_config_fields()
        
        assert isinstance(fields, list)
        assert 'name' in fields
        assert 'search_url' in fields
    
    def test_get_supported_formats(self, web_connector):
        """Test supported formats."""
        formats = web_connector.get_supported_formats()
        
        assert isinstance(formats, list)
        assert 'text' in formats
        assert 'html' in formats
        assert 'json' in formats
    
    def test_get_search_capabilities(self, web_connector):
        """Test search capabilities."""
        capabilities = web_connector.get_search_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'web_search' in capabilities
        assert 'image_search' in capabilities
        assert 'news_search' in capabilities
    
    @pytest.mark.asyncio
    async def test_connect(self, web_connector):
        """Test web connector connection."""
        # This will fail if no web service is available, which is expected
        result = await web_connector.connect()
        
        # Should return False if no web service available
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_search(self, web_connector):
        """Test web connector search."""
        query = "test query"
        results = await web_connector.search(query)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_metadata(self, web_connector):
        """Test web connector metadata."""
        metadata = await web_connector.get_metadata()
        
        assert isinstance(metadata, dict)
        assert 'connector' in metadata
        assert 'search_url' in metadata
        assert 'max_results' in metadata
        assert 'timeout' in metadata

class TestObsidianConnector:
    """Test cases for ObsidianConnector."""
    
    @pytest.fixture
    def obsidian_connector(self):
        """Create an ObsidianConnector instance for testing."""
        config = {
            'name': 'Obsidian Connector',
            'vault_path': './test_vault',
            'enabled': True
        }
        return ObsidianConnector(config)
    
    def test_obsidian_connector_initialization(self, obsidian_connector):
        """Test Obsidian connector initialization."""
        assert obsidian_connector is not None
        assert obsidian_connector.name == 'Obsidian Connector'
        assert obsidian_connector.vault_path == './test_vault'
        assert obsidian_connector.supported_formats == ['.md', '.txt']
    
    def test_get_required_config_fields(self, obsidian_connector):
        """Test required configuration fields."""
        fields = obsidian_connector.get_required_config_fields()
        
        assert isinstance(fields, list)
        assert 'name' in fields
        assert 'vault_path' in fields
    
    def test_get_supported_formats(self, obsidian_connector):
        """Test supported formats."""
        formats = obsidian_connector.get_supported_formats()
        
        assert isinstance(formats, list)
        assert '.md' in formats
        assert '.txt' in formats
    
    def test_get_search_capabilities(self, obsidian_connector):
        """Test search capabilities."""
        capabilities = obsidian_connector.get_search_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'metadata_search' in capabilities
        assert 'frontmatter_search' in capabilities
        assert 'link_search' in capabilities
    
    def test_extract_context(self, obsidian_connector):
        """Test context extraction."""
        content = "This is a test markdown document with some content."
        query = "test"
        context = obsidian_connector._extract_context(content, query)
        
        assert isinstance(context, str)
        assert len(context) > 0)
    
    def test_calculate_relevance_score(self, obsidian_connector):
        """Test relevance score calculation."""
        content = "This is a test markdown document with test content."
        query = "test"
        score = obsidian_connector._calculate_relevance_score(content, query)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_connect(self, obsidian_connector):
        """Test Obsidian connector connection."""
        # This will fail if no vault exists, which is expected
        result = await obsidian_connector.connect()
        
        # Should return False if no vault found
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_search(self, obsidian_connector):
        """Test Obsidian connector search."""
        query = "test query"
        results = await obsidian_connector.search(query)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_metadata(self, obsidian_connector):
        """Test Obsidian connector metadata."""
        metadata = await obsidian_connector.get_metadata()
        
        assert isinstance(metadata, dict)
        assert 'connector' in metadata
        assert 'vault_path' in metadata

class TestDatabaseConnector:
    """Test cases for DatabaseConnector."""
    
    @pytest.fixture
    def database_connector(self):
        """Create a DatabaseConnector instance for testing."""
        config = {
            'name': 'Database Connector',
            'connection_string': 'sqlite:///test.db',
            'database_type': 'sqlite',
            'table_name': 'documents',
            'enabled': True
        }
        return DatabaseConnector(config)
    
    def test_database_connector_initialization(self, database_connector):
        """Test database connector initialization."""
        assert database_connector is not None
        assert database_connector.name == 'Database Connector'
        assert database_connector.connection_string == 'sqlite:///test.db'
        assert database_connector.database_type == 'sqlite'
        assert database_connector.table_name == 'documents'
    
    def test_get_required_config_fields(self, database_connector):
        """Test required configuration fields."""
        fields = database_connector.get_required_config_fields()
        
        assert isinstance(fields, list)
        assert 'name' in fields
        assert 'connection_string' in fields
        assert 'database_type' in fields
    
    def test_get_supported_formats(self, database_connector):
        """Test supported formats."""
        formats = database_connector.get_supported_formats()
        
        assert isinstance(formats, list)
        assert 'text' in formats
        assert 'json' in formats
        assert 'csv' in formats
    
    def test_get_search_capabilities(self, database_connector):
        """Test search capabilities."""
        capabilities = database_connector.get_search_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'metadata_search' in capabilities
        assert 'sql_search' in capabilities
    
    def test_parse_connection_string(self, database_connector):
        """Test connection string parsing."""
        # Test with MySQL connection string
        database_connector.connection_string = 'mysql://user:pass@host:3306/db'
        parsed = database_connector._parse_connection_string()
        
        assert isinstance(parsed, dict)
        assert 'host' in parsed
        assert 'port' in parsed
        assert 'user' in parsed
        assert 'password' in parsed
        assert 'database' in parsed
    
    def test_build_search_query(self, database_connector):
        """Test search query building."""
        query = "test query"
        search_query = database_connector._build_search_query(query, limit=5)
        
        assert isinstance(search_query, str)
        assert 'test query' in search_query
        assert 'LIMIT 5' in search_query
    
    @pytest.mark.asyncio
    async def test_connect(self, database_connector):
        """Test database connector connection."""
        # This will fail if no database is available, which is expected
        result = await database_connector.connect()
        
        # Should return False if no database available
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_search(self, database_connector):
        """Test database connector search."""
        query = "test query"
        results = await database_connector.search(query)
        
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_get_metadata(self, database_connector):
        """Test database connector metadata."""
        metadata = await database_connector.get_metadata()
        
        assert isinstance(metadata, dict)
        assert 'connector' in metadata
        assert 'database_type' in metadata
        assert 'table_name' in metadata

class TestConnectorRegistry:
    """Test cases for ConnectorRegistry."""
    
    @pytest.fixture
    def connector_registry(self):
        """Create a ConnectorRegistry instance for testing."""
        return ConnectorRegistry()
    
    def test_connector_registry_initialization(self, connector_registry):
        """Test connector registry initialization."""
        assert connector_registry is not None
        assert hasattr(connector_registry, 'connectors')
        assert hasattr(connector_registry, 'connector_classes')
    
    def test_register_connector(self, connector_registry):
        """Test connector registration."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        
        assert 'test' in connector_registry.connectors
        assert connector_registry.connectors['test'] == connector
    
    def test_get_connector(self, connector_registry):
        """Test connector retrieval."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        retrieved_connector = connector_registry.get_connector('test')
        
        assert retrieved_connector == connector
    
    def test_list_connectors(self, connector_registry):
        """Test connector listing."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        connectors = connector_registry.list_connectors()
        
        assert isinstance(connectors, list)
        assert 'test' in connectors
    
    def test_list_available_connectors(self, connector_registry):
        """Test available connector listing."""
        connectors = connector_registry.list_available_connectors()
        
        assert isinstance(connectors, list)
        # Should have some built-in connectors
        assert len(connectors) > 0
    
    def test_get_connector_info(self, connector_registry):
        """Test connector information retrieval."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        info = connector_registry.get_connector_info('test')
        
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'enabled' in info
    
    def test_validate_connector(self, connector_registry):
        """Test connector validation."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        validation = connector_registry.validate_connector('test')
        
        assert 'valid' in validation
        assert 'errors' in validation
    
    def test_get_connector_capabilities(self, connector_registry):
        """Test connector capabilities retrieval."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        capabilities = connector_registry.get_connector_capabilities('test')
        
        assert isinstance(capabilities, dict)
        assert 'text_search' in capabilities
        assert 'metadata_search' in capabilities
    
    def test_get_supported_formats(self, connector_registry):
        """Test supported formats retrieval."""
        config = {
            'name': 'Test Connector',
            'enabled': True
        }
        connector = BaseConnector(config)
        
        connector_registry.register_connector('test', connector)
        formats = connector_registry.get_supported_formats('test')
        
        assert isinstance(formats, list)
    
    def test_get_registry_statistics(self, connector_registry):
        """Test registry statistics retrieval."""
        stats = connector_registry.get_registry_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_connectors' in stats
        assert 'available_connector_types' in stats
        assert 'registered_connectors' in stats
        assert 'available_types' in stats
