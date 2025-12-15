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
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required. Set it in .env file or as environment variable."
        )
    
    return {
        "openai_api_key": api_key,
        "openai_model": model,
    }

