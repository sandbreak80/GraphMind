# GraphMind Domain Registry
# Registry for managing domain adapters

import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
import yaml
import importlib
import os

from .base_adapter import BaseDomainAdapter

logger = logging.getLogger(__name__)

class DomainRegistry:
    """
    Registry for managing domain adapters in GraphMind.
    
    This class handles registration, discovery, and management of
    domain-specific adapters for the GraphMind RAG framework.
    """
    
    def __init__(self, config_dir: str = "config/domains"):
        """Initialize the domain registry."""
        self.config_dir = Path(config_dir)
        self.adapters: Dict[str, BaseDomainAdapter] = {}
        self.domain_configs: Dict[str, Dict[str, Any]] = {}
        self._load_domain_configs()
    
    def _load_domain_configs(self):
        """Load domain configurations from YAML files."""
        try:
            if not self.config_dir.exists():
                logger.warning(f"Domain config directory not found: {self.config_dir}")
                return
            
            for config_file in self.config_dir.glob("*.yaml"):
                domain_name = config_file.stem
                try:
                    with open(config_file, 'r') as f:
                        config = yaml.safe_load(f)
                        self.domain_configs[domain_name] = config
                        logger.info(f"Loaded domain config: {domain_name}")
                except Exception as e:
                    logger.error(f"Failed to load domain config {config_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to load domain configurations: {e}")
    
    def register_adapter(self, domain: str, adapter: BaseDomainAdapter):
        """
        Register a domain adapter.
        
        Args:
            domain: Domain name
            adapter: Domain adapter instance
        """
        self.adapters[domain] = adapter
        logger.info(f"Registered domain adapter: {domain}")
    
    def get_adapter(self, domain: str) -> Optional[BaseDomainAdapter]:
        """
        Get a domain adapter by name.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain adapter instance or None
        """
        return self.adapters.get(domain)
    
    def list_domains(self) -> List[str]:
        """
        List all registered domains.
        
        Returns:
            List of domain names
        """
        return list(self.adapters.keys())
    
    def get_domain_config(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain configuration or None
        """
        return self.domain_configs.get(domain)
    
    def create_adapter(self, domain: str) -> Optional[BaseDomainAdapter]:
        """
        Create a domain adapter from configuration.
        
        Args:
            domain: Domain name
            
        Returns:
            Domain adapter instance or None
        """
        try:
            config = self.get_domain_config(domain)
            if not config:
                logger.error(f"No configuration found for domain: {domain}")
                return None
            
            # Import and create adapter
            adapter_class = self._get_adapter_class(domain)
            if not adapter_class:
                logger.error(f"No adapter class found for domain: {domain}")
                return None
            
            adapter = adapter_class(config)
            self.register_adapter(domain, adapter)
            return adapter
            
        except Exception as e:
            logger.error(f"Failed to create adapter for domain {domain}: {e}")
            return None
    
    def _get_adapter_class(self, domain: str) -> Optional[Type[BaseDomainAdapter]]:
        """
        Get the adapter class for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Adapter class or None
        """
        try:
            # Map domain names to adapter classes
            adapter_mapping = {
                'finance': 'FinanceAdapter',
                'legal': 'LegalAdapter',
                'health': 'HealthAdapter',
                'academic': 'AcademicAdapter'
            }
            
            class_name = adapter_mapping.get(domain)
            if not class_name:
                logger.error(f"No adapter mapping for domain: {domain}")
                return None
            
            # Import the adapter module
            module_name = f"app.adapters.{domain}_adapter"
            module = importlib.import_module(module_name)
            
            # Get the adapter class
            adapter_class = getattr(module, class_name)
            return adapter_class
            
        except Exception as e:
            logger.error(f"Failed to get adapter class for domain {domain}: {e}")
            return None
    
    def get_available_domains(self) -> List[Dict[str, Any]]:
        """
        Get list of available domains with their information.
        
        Returns:
            List of domain information dictionaries
        """
        domains = []
        for domain, config in self.domain_configs.items():
            domains.append({
                'name': domain,
                'title': config.get('name', domain.title()),
                'description': config.get('description', ''),
                'version': config.get('version', '1.0.0'),
                'connectors': config.get('connectors', []),
                'metadata': config.get('metadata', {})
            })
        return domains
    
    def validate_domain(self, domain: str) -> Dict[str, Any]:
        """
        Validate a domain configuration.
        
        Args:
            domain: Domain name
            
        Returns:
            Validation result
        """
        config = self.get_domain_config(domain)
        if not config:
            return {
                'valid': False,
                'errors': [f"No configuration found for domain: {domain}"]
            }
        
        errors = []
        
        # Check required fields
        required_fields = ['name', 'description', 'prompts', 'connectors']
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check prompts
        if 'prompts' in config:
            prompts = config['prompts']
            required_prompts = ['system', 'web_search']
            for prompt in required_prompts:
                if prompt not in prompts:
                    errors.append(f"Missing required prompt: {prompt}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def reload_domain_configs(self):
        """Reload domain configurations from files."""
        self.domain_configs.clear()
        self._load_domain_configs()
        logger.info("Domain configurations reloaded")
    
    def get_domain_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about registered domains.
        
        Returns:
            Domain statistics
        """
        return {
            'total_domains': len(self.adapters),
            'available_configs': len(self.domain_configs),
            'domains': list(self.adapters.keys()),
            'configs': list(self.domain_configs.keys())
        }
