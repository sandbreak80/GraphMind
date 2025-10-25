# GraphMind Database Connector
# Database connector for GraphMind

import logging
from typing import Dict, List, Any, Optional
import asyncio
import json

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class DatabaseConnector(BaseConnector):
    """
    Database connector for GraphMind.
    
    This connector handles database access and retrieval
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the database connector."""
        super().__init__(config)
        self.name = "Database Connector"
        self.connection_string = config.get('connection_string', '')
        self.database_type = config.get('database_type', 'sqlite')
        self.table_name = config.get('table_name', 'documents')
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection."""
        try:
            if self.database_type == 'sqlite':
                import sqlite3
                self.db_module = sqlite3
            elif self.database_type == 'postgresql':
                import psycopg2
                self.db_module = psycopg2
            elif self.database_type == 'mysql':
                import mysql.connector
                self.db_module = mysql.connector
            else:
                logger.error(f"Unsupported database type: {self.database_type}")
                self.db_module = None
                
        except ImportError as e:
            logger.error(f"Database module not available: {e}")
            self.db_module = None
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields for database connector."""
        return ['name', 'connection_string', 'database_type']
    
    async def connect(self) -> bool:
        """Test connection to database."""
        try:
            if not self.db_module:
                logger.error("Database module not available")
                return False
            
            # Test database connection
            if self.database_type == 'sqlite':
                self.connection = self.db_module.connect(self.connection_string)
            elif self.database_type == 'postgresql':
                self.connection = self.db_module.connect(self.connection_string)
            elif self.database_type == 'mysql':
                self.connection = self.db_module.connect(**self._parse_connection_string())
            
            # Test query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            logger.info(f"Database connector connected to {self.database_type}")
            return True
            
        except Exception as e:
            logger.error(f"Database connector connection failed: {e}")
            return False
    
    def _parse_connection_string(self) -> Dict[str, Any]:
        """Parse connection string for MySQL."""
        # Simple parsing for MySQL connection string
        # Format: mysql://user:password@host:port/database
        if self.connection_string.startswith('mysql://'):
            parts = self.connection_string[8:].split('/')
            if len(parts) >= 2:
                auth_part = parts[0]
                database = parts[1]
                
                if '@' in auth_part:
                    user_pass, host_port = auth_part.split('@')
                    if ':' in user_pass:
                        user, password = user_pass.split(':')
                    else:
                        user, password = user_pass, ''
                    
                    if ':' in host_port:
                        host, port = host_port.split(':')
                        port = int(port)
                    else:
                        host, port = host_port, 3306
                    
                    return {
                        'host': host,
                        'port': port,
                        'user': user,
                        'password': password,
                        'database': database
                    }
        
        return {}
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search database."""
        try:
            if not self.connection:
                await self.connect()
            
            if not self.connection:
                return []
            
            # Build search query
            search_query = self._build_search_query(query, **kwargs)
            
            # Execute search
            cursor = self.connection.cursor()
            cursor.execute(search_query)
            rows = cursor.fetchall()
            cursor.close()
            
            # Format results
            results = []
            for row in rows:
                result = {
                    'text': row[1],  # Assuming text is in second column
                    'metadata': {
                        'doc_id': str(row[0]),  # Assuming id is first column
                        'doc_type': 'database_record',
                        'source': 'database_connector',
                        'database_type': self.database_type,
                        'table_name': self.table_name
                    },
                    'score': row[2] if len(row) > 2 else 0.5  # Assuming score is third column
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Database search failed: {e}")
            return []
    
    def _build_search_query(self, query: str, **kwargs) -> str:
        """Build database search query."""
        if self.database_type == 'sqlite':
            return f"""
                SELECT id, content, score 
                FROM {self.table_name} 
                WHERE content LIKE '%{query}%' 
                ORDER BY score DESC 
                LIMIT {kwargs.get('limit', 10)}
            """
        elif self.database_type == 'postgresql':
            return f"""
                SELECT id, content, score 
                FROM {self.table_name} 
                WHERE content ILIKE '%{query}%' 
                ORDER BY score DESC 
                LIMIT {kwargs.get('limit', 10)}
            """
        elif self.database_type == 'mysql':
            return f"""
                SELECT id, content, score 
                FROM {self.table_name} 
                WHERE content LIKE '%{query}%' 
                ORDER BY score DESC 
                LIMIT {kwargs.get('limit', 10)}
            """
        else:
            return f"SELECT * FROM {self.table_name} LIMIT 10"
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get database connector metadata."""
        try:
            if not self.connection:
                await self.connect()
            
            if not self.connection:
                return {
                    'connector': self.name,
                    'error': 'Not connected to database'
                }
            
            # Get table information
            cursor = self.connection.cursor()
            
            if self.database_type == 'sqlite':
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cursor.fetchone()[0]
            elif self.database_type == 'postgresql':
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cursor.fetchone()[0]
            elif self.database_type == 'mysql':
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                count = cursor.fetchone()[0]
            else:
                count = 0
            
            cursor.close()
            
            return {
                'connector': self.name,
                'database_type': self.database_type,
                'table_name': self.table_name,
                'total_records': count,
                'connection_string': self.connection_string[:20] + "..." if len(self.connection_string) > 20 else self.connection_string
            }
            
        except Exception as e:
            logger.error(f"Failed to get database metadata: {e}")
            return {
                'connector': self.name,
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported formats (database records are text-based)."""
        return ['text', 'json', 'csv']
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get search capabilities."""
        return {
            'text_search': True,
            'metadata_search': True,
            'faceted_search': True,
            'full_text_search': True,
            'sql_search': True
        }
    
    async def close(self):
        """Close the database connector."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                logger.info("Database connector closed")
            except Exception as e:
                logger.error(f"Error closing database connector: {e}")
        else:
            logger.info("Database connector already closed")
