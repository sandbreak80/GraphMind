# GraphMind Connector Registry
# Registry for managing data connectors

import logging
from typing import Dict, List, Any, Optional, Type
import importlib
import os

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class ConnectorRegistry:
    """
    Registry for managing data connectors in GraphMind.
    
    This class handles registration, discovery, and management of
    data source connectors for the GraphMind RAG framework.
    """
    
    def __init__(self):
        """Initialize the connector registry."""
        self.connectors: Dict[str, BaseConnector] = {}
        self.connector_classes: Dict[str, Type[BaseConnector]] = {}
        self._register_builtin_connectors()
    
    def _register_builtin_connectors(self):
        """Register built-in connectors."""
        builtin_connectors = {
            'pdf_connector': 'PDFConnector',
            'web_connector': 'WebConnector',
            'obsidian_connector': 'ObsidianConnector',
            'database_connector': 'DatabaseConnector'
        }
        
        for connector_name, class_name in builtin_connectors.items():
            try:
                # Import connector module
                module_name = f"app.connectors.{connector_name}"
                module = importlib.import_module(module_name)
                
                # Get connector class
                connector_class = getattr(module, class_name)
                self.connector_classes[connector_name] = connector_class
                
                logger.info(f"Registered built-in connector: {connector_name}")
                
            except Exception as e:
                logger.error(f"Failed to register connector {connector_name}: {e}")
    
    def register_connector(self, name: str, connector: BaseConnector):
        """
        Register a connector instance.
        
        Args:
            name: Connector name
            connector: Connector instance
        """
        self.connectors[name] = connector
        logger.info(f"Registered connector: {name}")
    
    def create_connector(self, name: str, config: Dict[str, Any]) -> Optional[BaseConnector]:
        """
        Create a connector from configuration.
        
        Args:
            name: Connector name
            config: Connector configuration
            
        Returns:
            Connector instance or None
        """
        try:
            connector_class = self.connector_classes.get(name)
            if not connector_class:
                logger.error(f"No connector class found for: {name}")
                return None
            
            connector = connector_class(config)
            self.register_connector(name, connector)
            return connector
            
        except Exception as e:
            logger.error(f"Failed to create connector {name}: {e}")
            return None
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """
        Get a connector by name.
        
        Args:
            name: Connector name
            
        Returns:
            Connector instance or None
        """
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """
        List all registered connectors.
        
        Returns:
            List of connector names
        """
        return list(self.connectors.keys())
    
    def list_available_connectors(self) -> List[str]:
        """
        List all available connector types.
        
        Returns:
            List of available connector names
        """
        return list(self.connector_classes.keys())
    
    def get_connector_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a connector.
        
        Args:
            name: Connector name
            
        Returns:
            Connector information or None
        """
        connector = self.get_connector(name)
        if connector:
            return connector.get_connector_info()
        return None
    
    def validate_connector(self, name: str) -> Dict[str, Any]:
        """
        Validate a connector configuration.
        
        Args:
            name: Connector name
            
        Returns:
            Validation result
        """
        connector = self.get_connector(name)
        if not connector:
            return {
                'valid': False,
                'errors': [f"Connector not found: {name}"]
            }
        
        return connector.validate_config()
    
    async def health_check_all(self) -> Dict[str, Any]:
        """
        Perform health check on all connectors.
        
        Returns:
            Health check results
        """
        results = {}
        
        for name, connector in self.connectors.items():
            try:
                health_result = await connector.health_check()
                results[name] = health_result
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = {
                    'healthy': False,
                    'status': 'error',
                    'error': str(e)
                }
        
        return results
    
    async def get_all_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for all connectors.
        
        Returns:
            Statistics for all connectors
        """
        statistics = {}
        
        for name, connector in self.connectors.items():
            try:
                stats = await connector.get_statistics()
                statistics[name] = stats
            except Exception as e:
                logger.error(f"Failed to get statistics for {name}: {e}")
                statistics[name] = {
                    'error': str(e)
                }
        
        return statistics
    
    def get_connector_capabilities(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get capabilities of a connector.
        
        Args:
            name: Connector name
            
        Returns:
            Connector capabilities or None
        """
        connector = self.get_connector(name)
        if connector:
            return connector.get_search_capabilities()
        return None
    
    def get_supported_formats(self, name: str) -> List[str]:
        """
        Get supported formats for a connector.
        
        Args:
            name: Connector name
            
        Returns:
            List of supported formats
        """
        connector = self.get_connector(name)
        if connector:
            return connector.get_supported_formats()
        return []
    
    async def search_all_connectors(
        self, 
        query: str, 
        connector_names: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple connectors.
        
        Args:
            query: Search query
            connector_names: List of connector names to search
            **kwargs: Additional search parameters
            
        Returns:
            Search results from all connectors
        """
        if connector_names is None:
            connector_names = self.list_connectors()
        
        results = {}
        
        for name in connector_names:
            connector = self.get_connector(name)
            if connector and connector.enabled:
                try:
                    search_results = await connector.search(query, **kwargs)
                    results[name] = search_results
                except Exception as e:
                    logger.error(f"Search failed for connector {name}: {e}")
                    results[name] = []
            else:
                results[name] = []
        
        return results
    
    async def close_all_connectors(self):
        """Close all connectors and clean up resources."""
        for name, connector in self.connectors.items():
            try:
                await connector.close()
                logger.info(f"Closed connector: {name}")
            except Exception as e:
                logger.error(f"Error closing connector {name}: {e}")
        
        self.connectors.clear()
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the connector registry.
        
        Returns:
            Registry statistics
        """
        return {
            'total_connectors': len(self.connectors),
            'available_connector_types': len(self.connector_classes),
            'registered_connectors': list(self.connectors.keys()),
            'available_types': list(self.connector_classes.keys())
        }
