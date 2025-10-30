"""Monitoring module for GraphMind RAG system."""
from .prompt_uplift_metrics import prompt_uplift_metrics

# Re-export monitor from legacy monitoring for backwards compatibility
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from monitoring_legacy import monitor

__all__ = ['prompt_uplift_metrics', 'monitor']
