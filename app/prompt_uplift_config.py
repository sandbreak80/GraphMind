"""
Prompt Uplift Configuration.

Configuration management for prompt uplift feature.
"""
import os
from typing import Dict, Any
from pydantic import BaseModel


class PromptUpliftConfig(BaseModel):
    """Configuration for prompt uplift feature."""
    
    enabled: bool = True
    expansion_count: int = 3
    confidence_threshold: float = 0.75
    enable_hyde: bool = True
    skip_expansion_threshold: int = 3
    uplifter_model: str = "llama3.2:3b-instruct"
    expander_model: str = "llama3.2:3b-instruct"
    classifier_model: str = "llama3.2:3b-instruct"
    max_tokens_uplift: int = 200
    max_tokens_expansion: int = 100
    uplifter_temperature: float = 0.2
    expander_temperature: float = 0.3
    classifier_temperature: float = 0.1
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    latency_budget_ms: int = 600
    parallel_expansion: bool = True


def load_config() -> PromptUpliftConfig:
    """Load configuration from environment variables."""
    return PromptUpliftConfig(
        enabled=os.getenv("PROMPT_UPLIFT_ENABLED", "true").lower() == "true",
        expansion_count=int(os.getenv("PROMPT_EXPANSION_COUNT", "3")),
        confidence_threshold=float(os.getenv("PROMPT_CONFIDENCE_THRESHOLD", "0.75")),
        enable_hyde=os.getenv("PROMPT_ENABLE_HYDE", "true").lower() == "true",
        skip_expansion_threshold=int(os.getenv("PROMPT_SKIP_THRESHOLD", "3")),
        uplifter_model=os.getenv("PROMPT_UPLIFTER_MODEL", "llama3.2:3b-instruct"),
        expander_model=os.getenv("PROMPT_EXPANDER_MODEL", "llama3.2:3b-instruct"),
        classifier_model=os.getenv("PROMPT_CLASSIFIER_MODEL", "llama3.2:3b-instruct"),
        max_tokens_uplift=int(os.getenv("PROMPT_MAX_TOKENS_UPLIFT", "200")),
        max_tokens_expansion=int(os.getenv("PROMPT_MAX_TOKENS_EXPANSION", "100")),
        uplifter_temperature=float(os.getenv("PROMPT_UPLIFTER_TEMPERATURE", "0.2")),
        expander_temperature=float(os.getenv("PROMPT_EXPANDER_TEMPERATURE", "0.3")),
        classifier_temperature=float(os.getenv("PROMPT_CLASSIFIER_TEMPERATURE", "0.1")),
        cache_enabled=os.getenv("PROMPT_CACHE_ENABLED", "true").lower() == "true",
        cache_ttl_seconds=int(os.getenv("PROMPT_CACHE_TTL_SECONDS", "3600")),
        latency_budget_ms=int(os.getenv("PROMPT_LATENCY_BUDGET_MS", "600")),
        parallel_expansion=os.getenv("PROMPT_PARALLEL_EXPANSION", "true").lower() == "true"
    )


# Global config instance
prompt_uplift_config = load_config()


def get_config_dict() -> Dict[str, Any]:
    """Get configuration as dictionary for pipeline."""
    config = prompt_uplift_config
    return {
        "expansion_count": config.expansion_count,
        "confidence_threshold": config.confidence_threshold,
        "enable_hyde": config.enable_hyde,
        "skip_expansion_threshold": config.skip_expansion_threshold,
        "uplifter_model": config.uplifter_model,
        "expander_model": config.expander_model,
        "classifier_model": config.classifier_model,
        "max_tokens_uplift": config.max_tokens_uplift,
        "max_tokens_expansion": config.max_tokens_expansion,
        "cache_enabled": config.cache_enabled,
        "cache_ttl_seconds": config.cache_ttl_seconds,
        "latency_budget_ms": config.latency_budget_ms
    }
