# GraphMind Domain Adapters Tests
# Tests for domain adapters

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from app.adapters.base_adapter import BaseDomainAdapter
from app.adapters.domain_registry import DomainRegistry
from app.adapters.finance_adapter import FinanceAdapter
from app.adapters.legal_adapter import LegalAdapter
from app.adapters.health_adapter import HealthAdapter

class TestBaseDomainAdapter:
    """Test cases for BaseDomainAdapter."""
    
    @pytest.fixture
    def base_adapter(self):
        """Create a BaseDomainAdapter instance for testing."""
        config = {
            'name': 'Test Domain',
            'description': 'Test domain adapter',
            'version': '1.0.0',
            'domain': 'test',
            'connectors': ['pdf_connector', 'web_connector'],
            'optional_connectors': ['database_connector']
        }
        return BaseDomainAdapter(config)
    
    def test_adapter_initialization(self, base_adapter):
        """Test adapter initialization."""
        assert base_adapter is not None
        assert base_adapter.name == 'Test Domain'
        assert base_adapter.domain == 'test'
        assert base_adapter.version == '1.0.0'
    
    def test_get_connectors(self, base_adapter):
        """Test connector retrieval."""
        connectors = base_adapter.get_connectors()
        assert isinstance(connectors, list)
        assert 'pdf_connector' in connectors
        assert 'web_connector' in connectors
    
    def test_get_optional_connectors(self, base_adapter):
        """Test optional connector retrieval."""
        optional_connectors = base_adapter.get_optional_connectors()
        assert isinstance(optional_connectors, list)
        assert 'database_connector' in optional_connectors
    
    def test_get_domain_info(self, base_adapter):
        """Test domain information retrieval."""
        info = base_adapter.get_domain_info()
        
        assert 'name' in info
        assert 'domain' in info
        assert 'description' in info
        assert 'version' in info
        assert 'connectors' in info
        assert 'optional_connectors' in info
    
    def test_get_settings(self, base_adapter):
        """Test settings retrieval."""
        settings = base_adapter.get_settings()
        assert isinstance(settings, dict)
    
    def test_validate_query(self, base_adapter):
        """Test query validation."""
        query = "test query"
        validation = base_adapter.validate_query(query)
        
        assert 'valid' in validation
        assert 'suggestions' in validation
        assert 'domain_terms' in validation
    
    def test_enhance_query(self, base_adapter):
        """Test query enhancement."""
        query = "test query"
        enhanced = base_adapter.enhance_query(query)
        
        assert isinstance(enhanced, str)
        assert len(enhanced) > 0
    
    def test_format_response(self, base_adapter):
        """Test response formatting."""
        response = "test response"
        sources = [{'text': 'source1', 'metadata': {'doc_id': '1'}}]
        
        formatted = base_adapter.format_response(response, sources)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_get_domain_filters(self, base_adapter):
        """Test domain filter retrieval."""
        filters = base_adapter.get_domain_filters()
        assert isinstance(filters, dict)
    
    def test_process_sources(self, base_adapter):
        """Test source processing."""
        sources = [
            {'text': 'source1', 'metadata': {'doc_id': '1'}},
            {'text': 'source2', 'metadata': {'doc_id': '2'}}
        ]
        
        processed = base_adapter.process_sources(sources)
        
        assert isinstance(processed, list)
        assert len(processed) == len(sources)
    
    def test_get_domain_metadata(self, base_adapter):
        """Test domain metadata retrieval."""
        metadata = base_adapter.get_domain_metadata()
        
        assert 'domain' in metadata
        assert 'adapter_version' in metadata
        assert 'connectors_used' in metadata

class TestFinanceAdapter:
    """Test cases for FinanceAdapter."""
    
    @pytest.fixture
    def finance_adapter(self):
        """Create a FinanceAdapter instance for testing."""
        config = {
            'name': 'Finance Research',
            'description': 'Financial analysis and trading research assistant',
            'version': '1.0.0',
            'domain': 'finance',
            'connectors': ['pdf_connector', 'web_connector', 'obsidian_connector'],
            'optional_connectors': ['database_connector', 'api_connector']
        }
        return FinanceAdapter(config)
    
    def test_finance_adapter_initialization(self, finance_adapter):
        """Test finance adapter initialization."""
        assert finance_adapter is not None
        assert finance_adapter.domain == 'finance'
        assert finance_adapter.name == 'Finance Research'
    
    def test_get_system_prompt(self, finance_adapter):
        """Test finance system prompt."""
        prompt = finance_adapter.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'financial' in prompt.lower()
        assert 'trading' in prompt.lower()
    
    def test_get_web_search_prompt(self, finance_adapter):
        """Test finance web search prompt."""
        prompt = finance_adapter.get_web_search_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{query}' in prompt
        assert 'financial' in prompt.lower()
    
    def test_get_connectors(self, finance_adapter):
        """Test finance connector retrieval."""
        connectors = finance_adapter.get_connectors()
        
        assert isinstance(connectors, list)
        assert 'pdf_connector' in connectors
        assert 'web_connector' in connectors
        assert 'obsidian_connector' in connectors
    
    def test_get_optional_connectors(self, finance_adapter):
        """Test finance optional connector retrieval."""
        optional_connectors = finance_adapter.get_optional_connectors()
        
        assert isinstance(optional_connectors, list)
        assert 'database_connector' in optional_connectors
        assert 'api_connector' in optional_connectors
    
    def test_validate_query(self, finance_adapter):
        """Test finance query validation."""
        query = "trading strategies"
        validation = finance_adapter.validate_query(query)
        
        assert 'valid' in validation
        assert 'has_finance_terms' in validation
        assert validation['has_finance_terms'] == True
    
    def test_enhance_query(self, finance_adapter):
        """Test finance query enhancement."""
        query = "trading strategies"
        enhanced = finance_adapter.enhance_query(query)
        
        assert isinstance(enhanced, str)
        assert len(enhanced) > len(query)
        assert 'trading' in enhanced.lower()
    
    def test_format_response(self, finance_adapter):
        """Test finance response formatting."""
        response = "Buy this stock"
        sources = [{'text': 'source1', 'metadata': {'doc_id': '1'}}]
        
        formatted = finance_adapter.format_response(response, sources)
        
        assert isinstance(formatted, str)
        assert len(formatted) > len(response)
        assert 'disclaimer' in formatted.lower()
    
    def test_get_domain_filters(self, finance_adapter):
        """Test finance domain filters."""
        filters = finance_adapter.get_domain_filters()
        
        assert isinstance(filters, dict)
        assert 'doc_types' in filters
        assert 'categories' in filters
        assert 'priority_sources' in filters
    
    def test_process_sources(self, finance_adapter):
        """Test finance source processing."""
        sources = [
            {'text': 'trading guide', 'metadata': {'doc_type': 'trading_guide'}},
            {'text': 'market analysis', 'metadata': {'doc_type': 'market_analysis'}}
        ]
        
        processed = finance_adapter.process_sources(sources)
        
        assert isinstance(processed, list)
        assert len(processed) == len(sources)
        
        # Check that finance-specific metadata was added
        for source in processed:
            assert 'finance_category' in source['metadata']

class TestLegalAdapter:
    """Test cases for LegalAdapter."""
    
    @pytest.fixture
    def legal_adapter(self):
        """Create a LegalAdapter instance for testing."""
        config = {
            'name': 'Legal Research',
            'description': 'Legal research and case law analysis assistant',
            'version': '1.0.0',
            'domain': 'legal',
            'connectors': ['pdf_connector', 'web_connector', 'database_connector'],
            'optional_connectors': ['api_connector', 'obsidian_connector']
        }
        return LegalAdapter(config)
    
    def test_legal_adapter_initialization(self, legal_adapter):
        """Test legal adapter initialization."""
        assert legal_adapter is not None
        assert legal_adapter.domain == 'legal'
        assert legal_adapter.name == 'Legal Research'
    
    def test_get_system_prompt(self, legal_adapter):
        """Test legal system prompt."""
        prompt = legal_adapter.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'legal' in prompt.lower()
        assert 'case law' in prompt.lower()
    
    def test_get_web_search_prompt(self, legal_adapter):
        """Test legal web search prompt."""
        prompt = legal_adapter.get_web_search_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{query}' in prompt
        assert 'legal' in prompt.lower()
    
    def test_validate_query(self, legal_adapter):
        """Test legal query validation."""
        query = "case law analysis"
        validation = legal_adapter.validate_query(query)
        
        assert 'valid' in validation
        assert 'has_legal_terms' in validation
        assert validation['has_legal_terms'] == True
    
    def test_enhance_query(self, legal_adapter):
        """Test legal query enhancement."""
        query = "case law analysis"
        enhanced = legal_adapter.enhance_query(query)
        
        assert isinstance(enhanced, str)
        assert len(enhanced) > len(query)
        assert 'case law' in enhanced.lower()
    
    def test_format_response(self, legal_adapter):
        """Test legal response formatting."""
        response = "Legal advice"
        sources = [{'text': 'source1', 'metadata': {'doc_id': '1'}}]
        
        formatted = legal_adapter.format_response(response, sources)
        
        assert isinstance(formatted, str)
        assert len(formatted) > len(response)
        assert 'disclaimer' in formatted.lower()
    
    def test_process_sources(self, legal_adapter):
        """Test legal source processing."""
        sources = [
            {'text': 'case law', 'metadata': {'doc_type': 'case_law'}},
            {'text': 'statute', 'metadata': {'doc_type': 'statute'}}
        ]
        
        processed = legal_adapter.process_sources(sources)
        
        assert isinstance(processed, list)
        assert len(processed) == len(sources)
        
        # Check that legal-specific metadata was added
        for source in processed:
            assert 'legal_category' in source['metadata']

class TestHealthAdapter:
    """Test cases for HealthAdapter."""
    
    @pytest.fixture
    def health_adapter(self):
        """Create a HealthAdapter instance for testing."""
        config = {
            'name': 'Health Research',
            'description': 'Medical and health research assistant',
            'version': '1.0.0',
            'domain': 'health',
            'connectors': ['pdf_connector', 'web_connector', 'database_connector'],
            'optional_connectors': ['api_connector', 'obsidian_connector']
        }
        return HealthAdapter(config)
    
    def test_health_adapter_initialization(self, health_adapter):
        """Test health adapter initialization."""
        assert health_adapter is not None
        assert health_adapter.domain == 'health'
        assert health_adapter.name == 'Health Research'
    
    def test_get_system_prompt(self, health_adapter):
        """Test health system prompt."""
        prompt = health_adapter.get_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'medical' in prompt.lower()
        assert 'health' in prompt.lower()
    
    def test_get_web_search_prompt(self, health_adapter):
        """Test health web search prompt."""
        prompt = health_adapter.get_web_search_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert '{query}' in prompt
        assert 'medical' in prompt.lower()
    
    def test_validate_query(self, health_adapter):
        """Test health query validation."""
        query = "medical treatment"
        validation = health_adapter.validate_query(query)
        
        assert 'valid' in validation
        assert 'has_health_terms' in validation
        assert validation['has_health_terms'] == True
    
    def test_enhance_query(self, health_adapter):
        """Test health query enhancement."""
        query = "medical treatment"
        enhanced = health_adapter.enhance_query(query)
        
        assert isinstance(enhanced, str)
        assert len(enhanced) > len(query)
        assert 'medical' in enhanced.lower()
    
    def test_format_response(self, health_adapter):
        """Test health response formatting."""
        response = "Medical advice"
        sources = [{'text': 'source1', 'metadata': {'doc_id': '1'}}]
        
        formatted = health_adapter.format_response(response, sources)
        
        assert isinstance(formatted, str)
        assert len(formatted) > len(response)
        assert 'disclaimer' in formatted.lower()
    
    def test_process_sources(self, health_adapter):
        """Test health source processing."""
        sources = [
            {'text': 'clinical study', 'metadata': {'doc_type': 'clinical_study'}},
            {'text': 'treatment guide', 'metadata': {'doc_type': 'treatment_guide'}}
        ]
        
        processed = health_adapter.process_sources(sources)
        
        assert isinstance(processed, list)
        assert len(processed) == len(sources)
        
        # Check that health-specific metadata was added
        for source in processed:
            assert 'health_category' in source['metadata']

class TestDomainRegistry:
    """Test cases for DomainRegistry."""
    
    @pytest.fixture
    def domain_registry(self):
        """Create a DomainRegistry instance for testing."""
        return DomainRegistry()
    
    def test_domain_registry_initialization(self, domain_registry):
        """Test domain registry initialization."""
        assert domain_registry is not None
        assert hasattr(domain_registry, 'adapters')
        assert hasattr(domain_registry, 'domain_configs')
    
    def test_register_adapter(self, domain_registry):
        """Test adapter registration."""
        config = {
            'name': 'Test Domain',
            'description': 'Test domain adapter',
            'version': '1.0.0',
            'domain': 'test'
        }
        adapter = BaseDomainAdapter(config)
        
        domain_registry.register_adapter('test', adapter)
        
        assert 'test' in domain_registry.adapters
        assert domain_registry.adapters['test'] == adapter
    
    def test_get_adapter(self, domain_registry):
        """Test adapter retrieval."""
        config = {
            'name': 'Test Domain',
            'description': 'Test domain adapter',
            'version': '1.0.0',
            'domain': 'test'
        }
        adapter = BaseDomainAdapter(config)
        
        domain_registry.register_adapter('test', adapter)
        retrieved_adapter = domain_registry.get_adapter('test')
        
        assert retrieved_adapter == adapter
    
    def test_list_domains(self, domain_registry):
        """Test domain listing."""
        config = {
            'name': 'Test Domain',
            'description': 'Test domain adapter',
            'version': '1.0.0',
            'domain': 'test'
        }
        adapter = BaseDomainAdapter(config)
        
        domain_registry.register_adapter('test', adapter)
        domains = domain_registry.list_domains()
        
        assert isinstance(domains, list)
        assert 'test' in domains
    
    def test_get_available_domains(self, domain_registry):
        """Test available domain retrieval."""
        domains = domain_registry.get_available_domains()
        
        assert isinstance(domains, list)
        # Should have some default domains if config files exist
    
    def test_validate_domain(self, domain_registry):
        """Test domain validation."""
        # Test with non-existent domain
        validation = domain_registry.validate_domain('nonexistent')
        
        assert 'valid' in validation
        assert validation['valid'] == False
        assert 'errors' in validation
    
    def test_get_domain_statistics(self, domain_registry):
        """Test domain statistics retrieval."""
        stats = domain_registry.get_domain_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_domains' in stats
        assert 'available_configs' in stats
        assert 'domains' in stats
        assert 'configs' in stats
