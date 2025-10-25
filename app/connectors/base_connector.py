# GraphMind Base Connector
# Base class for data source connectors

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    """
    Base class for all data connectors in GraphMind.
    
    This class provides the interface that all connectors must implement
    to integrate with the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the connector."""
        self.config = config
        self.name = config.get('name', 'unknown')
        self.enabled = config.get('enabled', True)
        self.connection = None
        self._initialize_connector()
    
    def _initialize_connector(self):
        """Initialize connector-specific settings."""
        self.settings = self.config.get('settings', {})
        self.metadata = self.config.get('metadata', {})
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Test connection to data source.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search the data source.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """
        Get connector metadata.
        
        Returns:
            Connector metadata dictionary
        """
        pass
    
    def get_connector_info(self) -> Dict[str, Any]:
        """
        Get information about this connector.
        
        Returns:
            Connector information dictionary
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'settings': self.settings,
            'metadata': self.metadata
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate connector configuration.
        
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        # Check required configuration
        required_fields = self.get_required_config_fields()
        for field in required_fields:
            if field not in self.config:
                errors.append(f"Missing required configuration field: {field}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_required_config_fields(self) -> List[str]:
        """
        Get list of required configuration fields.
        
        Returns:
            List of required field names
        """
        return ['name']
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the connector.
        
        Returns:
            Health check result
        """
        try:
            is_connected = await self.connect()
            return {
                'healthy': is_connected,
                'status': 'connected' if is_connected else 'disconnected',
                'connector': self.name
            }
        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            return {
                'healthy': False,
                'status': 'error',
                'connector': self.name,
                'error': str(e)
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get connector statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'connector': self.name,
            'enabled': self.enabled,
            'connected': await self.connect() if self.connection else False
        }
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported data formats.
        
        Returns:
            List of supported format names
        """
        return []
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """
        Get search capabilities of this connector.
        
        Returns:
            Capabilities dictionary
        """
        return {
            'text_search': True,
            'metadata_search': False,
            'faceted_search': False,
            'full_text_search': True
        }
    
    async def close(self):
        """Close the connector and clean up resources."""
        if self.connection:
            try:
                await self.connection.close()
                self.connection = None
                logger.info(f"Connector {self.name} closed successfully")
            except Exception as e:
                logger.error(f"Error closing connector {self.name}: {e}")
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.connection:
            try:
                import asyncio
                asyncio.create_task(self.close())
            except Exception:
                pass
