# GraphMind Adapters Module
# Domain-specific adapters for the GraphMind RAG framework

from .base_adapter import BaseDomainAdapter
from .domain_registry import DomainRegistry
from .finance_adapter import FinanceAdapter
from .legal_adapter import LegalAdapter
from .health_adapter import HealthAdapter

__all__ = [
    'BaseDomainAdapter',
    'DomainRegistry',
    'FinanceAdapter',
    'LegalAdapter', 
    'HealthAdapter'
]
