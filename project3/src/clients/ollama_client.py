"""Ollama API client for local LLM inference (FREE!)."""

import json
import logging
import requests
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for Ollama local LLM server."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model: Model name (default: llama3.2)
                   Available models: llama3.2, mistral, phi3, qwen2.5, etc.
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_retries = 2
        
        logger.info(f"Initialized Ollama client with model: {model}")
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Any:
        """
        Generate JSON data using Ollama.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON data
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Ollama API call attempt {attempt + 1}/{self.max_retries} (model: {self.model})")
                
                # Ollama chat API
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "format": "json",  # Force JSON output
                        "options": {
                            "temperature": temperature,
                        }
                    },
                    timeout=120,  # Ollama can be slow on first run
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data.get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty response from Ollama")
                
                # Parse JSON
                content = content.strip()
                
                # Remove markdown if present
                if content.startswith("```"):
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                    if content.startswith("json"):
                        content = "\n".join(content.split("\n")[1:])
                
                try:
                    parsed_json = json.loads(content)
                    logger.info(f"Successfully parsed JSON on attempt {attempt + 1}")
                    return parsed_json
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse failed on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        # Retry with more explicit prompt
                        messages[-1]["content"] = prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown, no explanations."
                        continue
                    raise ValueError(f"Failed to parse JSON: {e}\nResponse: {content[:200]}")
                
            except requests.RequestException as e:
                logger.error(f"Ollama request failed: {e}")
                if "Connection refused" in str(e):
                    raise RuntimeError(
                        "Cannot connect to Ollama. Make sure Ollama is running:\n"
                        "  1. Install: https://ollama.com/download\n"
                        f"  2. Pull model: ollama pull {self.model}\n"
                        "  3. Ollama should auto-start, or run: ollama serve"
                    )
                if attempt < self.max_retries - 1:
                    continue
                raise RuntimeError(f"Ollama API call failed: {e}")
        
        raise RuntimeError("Failed to generate data after retries")
    
    def generate_multiple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        count: int = 1,
        temperature: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple JSON objects.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            count: Number of objects
            temperature: Temperature
            
        Returns:
            List of JSON objects
        """
        if count == 1:
            result = self.generate_json(prompt, system_prompt, temperature)
            return [result] if isinstance(result, dict) else result
        
        # Request array
        array_prompt = prompt.replace("a single JSON object", f"{count} JSON objects in an array")
        result = self.generate_json(array_prompt, system_prompt, temperature)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return [result]
        else:
            raise ValueError(f"Unexpected response type: {type(result)}")

