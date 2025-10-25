"""
System Prompt Manager for TradingAI Research Platform
Manages system prompts for different chat modes with user customization
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class SystemPromptManager:
    """Manages system prompts for different chat modes."""
    
    def __init__(self, storage_dir: str = "/workspace/system_prompts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Default system prompts
        self.default_prompts = {
            "rag_only": """You are an expert trading analyst specializing in Emini futures. You have access to a comprehensive knowledge base of trading documents, strategies, and market analysis.

Your role:
- Provide accurate, data-driven analysis based on the provided documents
- Focus on practical trading strategies and market insights
- Reference specific documents and sources when possible
- Maintain a professional, analytical tone

Guidelines:
- Use only information from the provided document context
- Cite specific sources and page numbers when available
- Provide actionable insights and recommendations
- If information is incomplete, clearly state limitations
- Focus on Emini futures trading (ES, NQ, YM, RTY)

Response format:
- Start with a clear answer to the user's question
- Provide supporting evidence from documents
- Include relevant examples and specifics
- End with actionable recommendations if applicable""",

            "web_search_only": """You are a knowledgeable research assistant with access to current web information. Answer the user's question directly using the provided web search results.

IMPORTANT: You MUST provide a helpful answer based on the search results. Do not refuse or say you cannot help.

Your role:
- Answer questions directly using the provided web search results
- Synthesize information from multiple sources
- Provide clear, accurate, and helpful responses
- Focus on being informative and useful

Guidelines:
- ALWAYS provide an answer based on the search results provided
- Use information from the web search results to answer the question
- Synthesize and summarize key information
- Include relevant details and context
- Be direct and helpful in your responses
- Never refuse to answer - always provide the best response possible based on available information

Response format:
- Start with a direct answer to the question
- Provide supporting information from search results
- Include relevant details and context
- Cite sources when appropriate
- Be comprehensive and helpful""",

            "obsidian_only": """You are a personal trading coach with access to the user's private knowledge base. You provide personalized advice based on their notes, strategies, and insights.

Your role:
- Provide personalized trading advice based on user's notes
- Reference their specific strategies and setups
- Build on their existing knowledge and experience
- Maintain continuity with their trading approach

Guidelines:
- Use only information from the provided Obsidian notes
- Reference specific strategies and setups from their notes
- Build on their existing knowledge
- Provide personalized recommendations
- Maintain consistency with their trading style

Response format:
- Start with personalized insights
- Reference their specific strategies
- Provide tailored recommendations
- Build on their existing knowledge
- Include relevant personal context""",

            "comprehensive_research": """You are a senior trading analyst with access to both historical knowledge and real-time market data. You provide comprehensive analysis combining document knowledge with current market information.

Your role:
- Combine historical knowledge with current market data
- Provide comprehensive analysis and recommendations
- Synthesize information from multiple sources
- Maintain awareness of both past and present market conditions

Guidelines:
- Use both document context and web search results
- Synthesize information from multiple sources
- Provide comprehensive analysis
- Balance historical knowledge with current events
- Focus on actionable trading insights

Response format:
- Start with comprehensive market overview
- Combine historical and current information
- Provide detailed analysis and recommendations
- Include both document and web sources
- End with specific actionable insights"""
        }
        
        # Initialize with default prompts
        self._initialize_default_prompts()
    
    def _initialize_default_prompts(self):
        """Initialize default prompts if they don't exist."""
        for mode, prompt in self.default_prompts.items():
            prompt_file = self.storage_dir / f"{mode}.json"
            if not prompt_file.exists():
                self._save_prompt(mode, prompt, "default")
    
    def _save_prompt(self, mode: str, prompt: str, version: str = "latest") -> bool:
        """Save a system prompt to storage."""
        try:
            prompt_file = self.storage_dir / f"{mode}.json"
            
            # Load existing prompts or create new structure
            if prompt_file.exists():
                with open(prompt_file, 'r') as f:
                    prompts_data = json.load(f)
            else:
                prompts_data = {"versions": {}, "current": "latest"}
            
            # Create prompt data
            prompt_data = {
                "prompt": prompt,
                "version": version,
                "created_at": datetime.now().isoformat(),
                "hash": hashlib.md5(prompt.encode()).hexdigest()[:8]
            }
            
            # Save version
            prompts_data["versions"][version] = prompt_data
            prompts_data["current"] = version
            
            # Save to file
            with open(prompt_file, 'w') as f:
                json.dump(prompts_data, f, indent=2)
            
            logger.info(f"Saved system prompt for {mode} version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save system prompt for {mode}: {e}")
            return False
    
    def get_prompt(self, mode: str, version: str = "latest") -> Optional[str]:
        """Get system prompt for a mode."""
        try:
            prompt_file = self.storage_dir / f"{mode}.json"
            if not prompt_file.exists():
                return self.default_prompts.get(mode)
            
            with open(prompt_file, 'r') as f:
                prompts_data = json.load(f)
            
            # Get current version if not specified
            if version == "latest":
                version = prompts_data.get("current", "latest")
            
            # Get prompt from versions
            if version in prompts_data.get("versions", {}):
                return prompts_data["versions"][version]["prompt"]
            
            # Fallback to default
            return self.default_prompts.get(mode)
            
        except Exception as e:
            logger.error(f"Failed to get system prompt for {mode}: {e}")
            return self.default_prompts.get(mode)
    
    def update_prompt(self, mode: str, prompt: str, version: str = "latest") -> bool:
        """Update system prompt for a mode."""
        return self._save_prompt(mode, prompt, version)
    
    def list_prompts(self) -> Dict[str, List[str]]:
        """List all available prompts and versions."""
        try:
            result = {}
            for mode in self.default_prompts.keys():
                prompt_file = self.storage_dir / f"{mode}.json"
                if prompt_file.exists():
                    with open(prompt_file, 'r') as f:
                        prompts_data = json.load(f)
                    result[mode] = list(prompts_data.get("versions", {}).keys())
                else:
                    result[mode] = ["default"]
            return result
        except Exception as e:
            logger.error(f"Failed to list prompts: {e}")
            return {}
    
    def get_prompt_info(self, mode: str) -> Dict[str, Any]:
        """Get detailed information about a prompt."""
        try:
            prompt_file = self.storage_dir / f"{mode}.json"
            if not prompt_file.exists():
                return {
                    "mode": mode,
                    "current_version": "default",
                    "versions": ["default"],
                    "prompt": self.default_prompts.get(mode, ""),
                    "created_at": None,
                    "hash": None
                }
            
            with open(prompt_file, 'r') as f:
                prompts_data = json.load(f)
            
            current_version = prompts_data.get("current", "latest")
            versions = list(prompts_data.get("versions", {}).keys())
            
            current_prompt_data = prompts_data.get("versions", {}).get(current_version, {})
            
            return {
                "mode": mode,
                "current_version": current_version,
                "versions": versions,
                "prompt": current_prompt_data.get("prompt", ""),
                "created_at": current_prompt_data.get("created_at"),
                "hash": current_prompt_data.get("hash")
            }
            
        except Exception as e:
            logger.error(f"Failed to get prompt info for {mode}: {e}")
            return {
                "mode": mode,
                "current_version": "default",
                "versions": ["default"],
                "prompt": self.default_prompts.get(mode, ""),
                "created_at": None,
                "hash": None
            }
    
    def reset_to_default(self, mode: str) -> bool:
        """Reset prompt to default."""
        if mode in self.default_prompts:
            return self.update_prompt(mode, self.default_prompts[mode], "default")
        return False
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a system prompt."""
        issues = []
        warnings = []
        
        # Check length
        if len(prompt) < 50:
            issues.append("Prompt is too short (minimum 50 characters)")
        elif len(prompt) > 2000:
            warnings.append("Prompt is very long (over 2000 characters)")
        
        # Check for required sections
        required_sections = ["role", "guidelines", "format"]
        for section in required_sections:
            if section not in prompt.lower():
                warnings.append(f"Consider including '{section}' section")
        
        # Check for forbidden content
        forbidden_terms = ["harmful", "inappropriate", "illegal"]
        for term in forbidden_terms:
            if term in prompt.lower():
                issues.append(f"Contains potentially inappropriate term: {term}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "length": len(prompt),
            "word_count": len(prompt.split())
        }

# Global instance
system_prompt_manager = SystemPromptManager()