"""OpenAI API client wrapper for generating synthetic data."""

import json
import time
from typing import Any, Dict, List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion


class OpenAIClient:
    """Wrapper around OpenAI Python SDK for generating synthetic JSON data."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name to use (default: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Any:
        """
        Generate JSON data using OpenAI API.
        
        Args:
            prompt: User prompt describing what to generate
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (0.0 to 2.0)
            
        Returns:
            Parsed JSON data (dict or list)
            
        Raises:
            ValueError: If response is not valid JSON
            RuntimeError: If API call fails after retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"} if self.model.startswith("gpt-4") else None,
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from OpenAI API")
                
                # Try to parse JSON
                # Sometimes GPT wraps JSON in markdown code blocks
                content = content.strip()
                if content.startswith("```"):
                    # Remove markdown code blocks
                    lines = content.split("\n")
                    content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
                    # Remove language identifier if present
                    if content.startswith("json"):
                        content = "\n".join(content.split("\n")[1:])
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    if attempt < self.max_retries - 1:
                        # Retry with a more explicit prompt
                        retry_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown, no code blocks, no text before or after the JSON."
                        messages[-1]["content"] = retry_prompt
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {content[:200]}")
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenAI API call failed after {self.max_retries} attempts: {e}")
        
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
            system_prompt: System prompt (optional)
            count: Number of objects to generate
            temperature: Sampling temperature
            
        Returns:
            List of generated JSON objects
        """
        if count == 1:
            result = self.generate_json(prompt, system_prompt, temperature)
            return [result] if isinstance(result, dict) else result
        
        # For multiple items, request an array
        array_prompt = prompt.replace("a single JSON object", f"{count} JSON objects in an array")
        result = self.generate_json(array_prompt, system_prompt, temperature)
        
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            return [result]
        else:
            raise ValueError(f"Unexpected response type: {type(result)}")

