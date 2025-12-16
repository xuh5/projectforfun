"""DeepSeek API client (Very cheap, Chinese API)."""

import json
import logging
import requests
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for DeepSeek API (超便宜的国内 API)."""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """
        Initialize DeepSeek client.
        
        Args:
            api_key: DeepSeek API key (from https://platform.deepseek.com/)
            model: Model name (deepseek-chat or deepseek-coder)
        
        Pricing (非常便宜):
            - Input: ¥0.001 / 1K tokens (约 $0.00014)
            - Output: ¥0.002 / 1K tokens (约 $0.00028)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.deepseek.com/v1"
        self.max_retries = 2
        
        logger.info(f"Initialized DeepSeek client with model: {model}")
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Any:
        """Generate JSON using DeepSeek API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"DeepSeek API call attempt {attempt + 1}/{self.max_retries} (model: {self.model})")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "response_format": {"type": "json_object"},  # Force JSON
                    },
                    timeout=30,
                )
                
                response.raise_for_status()
                data = response.json()
                
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                if not content:
                    raise ValueError("Empty response from DeepSeek")
                
                # Parse JSON
                content = content.strip()
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
                        messages[-1]["content"] = prompt + "\n\nIMPORTANT: Return ONLY valid JSON."
                        continue
                    raise ValueError(f"Failed to parse JSON: {e}")
                
            except requests.RequestException as e:
                logger.error(f"DeepSeek request failed: {e}")
                if attempt < self.max_retries - 1:
                    continue
                raise RuntimeError(f"DeepSeek API call failed: {e}")
        
        raise RuntimeError("Failed to generate data after retries")
    
    def generate_multiple(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        count: int = 1,
        temperature: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Generate multiple JSON objects."""
        if count == 1:
            result = self.generate_json(prompt, system_prompt, temperature)
            return [result] if isinstance(result, dict) else result
        
        array_prompt = prompt.replace("a single JSON object", f"{count} JSON objects in an array")
        result = self.generate_json(array_prompt, system_prompt, temperature)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return [result]
        else:
            raise ValueError(f"Unexpected response type: {type(result)}")

