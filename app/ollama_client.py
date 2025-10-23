"""Ollama API client for local LLM interactions."""
import logging
import json
import requests
from typing import Optional, Dict, Any
from app.config import OLLAMA_BASE_URL

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama API."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, default_model: str = "llama3.1:8b"):
        """Initialize Ollama client."""
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        logger.info(f"Initialized Ollama client: {self.base_url} (model: {default_model})")
    
    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        top_k: Optional[int] = None,
        timeout: int = 180
    ) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: Input prompt
            model: Model to use (defaults to default_model)
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens to generate
            top_k: Top-K sampling for vocabulary diversity
            timeout: Request timeout in seconds
            
        Returns:
            Generated text response
        """
        model = model or self.default_model
        
        try:
            url = f"{self.base_url}/api/generate"
            options = {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "stop": ["Human:", "User:", "Question:", "Context:"]
            }
            
            # Add top_k if provided
            if top_k is not None:
                options["top_k"] = top_k
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": options
            }
            
            logger.debug(f"Calling Ollama API with model: {model}")
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generate: {e}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Ollama API.
        
        Args:
            prompt: Input prompt (should request JSON output)
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            timeout: Request timeout
            
        Returns:
            Parsed JSON response as dict
        """
        # Add JSON format instruction to prompt
        json_prompt = f"{prompt}\n\nOutput ONLY valid JSON, no other text."
        
        response_text = self.generate(
            prompt=json_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        # Try to extract JSON from response
        try:
            # Try direct parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in text (sometimes models add extra text)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            logger.warning(f"Failed to parse JSON response: {response_text[:200]}")
            # Return empty dict as fallback
            return {}
    
    def check_model_available(self, model: str) -> bool:
        """Check if a specific model is available."""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            models_data = response.json()
            available_models = [m['name'] for m in models_data.get('models', [])]
            
            return model in available_models
        except Exception as e:
            logger.warning(f"Could not check model availability: {e}")
            return False
    
    def list_models(self) -> list:
        """List all available models."""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            models_data = response.json()
            return [m['name'] for m in models_data.get('models', [])]
        except Exception as e:
            logger.error(f"Could not list models: {e}")
            return []
