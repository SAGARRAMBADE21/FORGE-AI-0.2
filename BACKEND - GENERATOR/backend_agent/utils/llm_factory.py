"""
LLM Factory - Creates LLM instances based on provider configuration
Supports both OpenAI and Groq
"""

import os
from typing import Dict, Any, Optional
from langchain_core.language_models import BaseChatModel


def create_llm(llm_config: Dict[str, Any]) -> BaseChatModel:
    """
    Create LLM instance based on provider configuration.
    
    Supports:
    - Groq (default)
    - OpenAI
    
    Args:
        llm_config: Configuration dict with provider, model, temperature, etc.
        
    Returns:
        Configured LLM instance
    """
    provider = llm_config.get("provider", "groq").lower()
    temperature = llm_config.get("temperature", 0.1)
    
    # Get API keys from config or environment
    groq_api_key = llm_config.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    openai_api_key = llm_config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    
    if provider == "groq":
        try:
            from langchain_groq import ChatGroq
            
            model = llm_config.get("model", "llama-3.3-70b-versatile")
            
            if not groq_api_key:
                raise ValueError(
                    "Groq API key not found. Set GROQ_API_KEY environment variable or "
                    "add groq_api_key to config."
                )
            
            return ChatGroq(
                model=model,
                temperature=temperature,
                groq_api_key=groq_api_key
            )
        except ImportError:
            raise ImportError(
                "langchain-groq not installed. Install with: pip install langchain-groq"
            )
    
    elif provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
            
            model = llm_config.get("openai_model", "gpt-4o-mini")
            
            if not openai_api_key:
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable or "
                    "add openai_api_key to config."
                )
            
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                openai_api_key=openai_api_key
            )
        except ImportError:
            raise ImportError(
                "langchain-openai not installed. Install with: pip install langchain-openai"
            )
    
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. Supported providers: groq, openai"
        )


def get_available_models(provider: str) -> list:
    """Get list of available models for a provider."""
    
    if provider == "groq":
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
    elif provider == "openai":
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
    else:
        return []


def switch_provider(current_config: Dict[str, Any], new_provider: str) -> Dict[str, Any]:
    """
    Switch LLM provider and update model accordingly.
    
    Args:
        current_config: Current LLM configuration
        new_provider: New provider name ('groq' or 'openai')
        
    Returns:
        Updated configuration dict
    """
    config = current_config.copy()
    config["provider"] = new_provider
    
    if new_provider == "groq":
        config["model"] = config.get("model", "llama-3.3-70b-versatile")
    elif new_provider == "openai":
        config["model"] = config.get("openai_model", "gpt-4o-mini")
    
    return config
