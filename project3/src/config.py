"""Configuration management for the synthetic data generator."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


def load_config() -> dict:
    """Load configuration from environment variables."""
    # Load .env file from project root
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    # LLM Provider (openai, ollama, deepseek)
    llm_provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    
    config = {
        "llm_provider": llm_provider,
        "project1_api_url": os.getenv("PROJECT1_API_URL", "http://localhost:8000"),
        "project1_api_token": os.getenv("PROJECT1_API_TOKEN"),
    }
    
    # Provider-specific configuration
    if llm_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        config["openai_api_key"] = api_key
        config["openai_model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    
    elif llm_provider == "ollama":
        config["ollama_base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        config["ollama_model"] = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
    
    elif llm_provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is required when using DeepSeek provider")
        config["deepseek_api_key"] = api_key
        config["deepseek_model"] = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
    
    else:
        raise ValueError(f"Unknown LLM provider: {llm_provider}. Use: openai, ollama, or deepseek")
    
    return config

