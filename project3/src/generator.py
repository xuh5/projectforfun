"""Node data generator using LLM."""

import logging
from typing import Any, Dict, Optional
from .models import NodeData

logger = logging.getLogger(__name__)


class NodeGenerator:
    """Generates node data using LLM in a single API call."""
    
    def __init__(self, llm_client: Any):
        """
        Initialize node generator.
        
        Args:
            llm_client: LLM client instance (OpenAI/Ollama/DeepSeek)
                       Must have generate_json(prompt, system_prompt, temperature) method
        """
        self.llm_client = llm_client
    
    def generate(
        self,
        symbol: str,
        company_name: str,
        sector_info: Optional[str] = None
    ) -> NodeData:
        """
        Generate complete node data using a single LLM call.
        
        Generates all fields in one request:
        - description: 2-3 sentence company description
        - sector: Main sector/industry classification (TODO function)
        - sectors: Array of related sector tags (for metadata)
        
        Args:
            symbol: Stock ticker symbol (e.g., "NVDA")
            company_name: Full company name (e.g., "NVIDIA Corporation")
            sector_info: Optional existing sector information from yfinance
            
        Returns:
            NodeData instance with all generated fields
            
        Raises:
            ValueError: If LLM response is invalid or missing required fields
            RuntimeError: If LLM API call fails
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(symbol, company_name, sector_info)
        
        try:
            logger.info(f"Generating node data for {symbol} ({company_name})")
            
            # Call LLM to generate all fields at once
            response = self.llm_client.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5,  # Lower temperature for more consistent output
            )
            
            # Validate response structure
            self._validate_response(response)
            
            # Create NodeData instance
            node_data = NodeData(
                id=symbol.upper(),
                label=company_name,
                description=response["description"],
                sector=response.get("sector"),  # TODO function will enhance this
                type="company",
                color=None,  # Let frontend handle coloring
                metadata={
                    "sectors": response.get("sectors", [])
                }
            )
            
            logger.info(f"Successfully generated data for {symbol}")
            logger.debug(f"Generated sectors: {node_data.metadata.get('sectors')}")
            
            return node_data
            
        except KeyError as e:
            logger.error(f"Missing required field in LLM response: {e}")
            raise ValueError(f"Invalid LLM response: missing field {e}")
        except Exception as e:
            logger.error(f"Failed to generate node data for {symbol}: {e}")
            raise
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt for LLM.
        
        Returns:
            System prompt string
        """
        return (
            "You are a financial data expert with deep knowledge of technology companies, "
            "AI/ML industries, and semiconductor sectors. Your task is to generate accurate, "
            "informative descriptions and sector classifications for public companies. "
            "Always return valid JSON format without any markdown code blocks or extra text."
        )
    
    def _build_user_prompt(
        self,
        symbol: str,
        company_name: str,
        sector_info: Optional[str] = None
    ) -> str:
        """
        Build user prompt for LLM.
        
        Args:
            symbol: Stock ticker symbol
            company_name: Full company name
            sector_info: Optional existing sector information
            
        Returns:
            User prompt string
        """
        sector_context = ""
        if sector_info:
            sector_context = f"\nExisting sector classification: {sector_info}"
        
        prompt = f"""Generate information for this company:

Stock Symbol: {symbol}
Company Name: {company_name}{sector_context}

Generate a JSON object with the following fields:

1. "description": A concise 2-3 sentence description of the company. Include:
   - What the company does (products/services)
   - Their position in the industry
   - Any notable AI/technology focus if applicable

2. "sector": The PRIMARY industry sector this company belongs to. Choose ONE of:
   - "Technology"
   - "Communication Services"  
   - "Consumer Cyclical"
   - "Industrials"
   - "Healthcare"
   - Or another appropriate broad sector

3. "sectors": An array of related industry tags and categories. Include multiple relevant tags such as:
   - Specific industries (e.g., "Semiconductor", "Software", "Cloud Computing")
   - Technology areas (e.g., "AI", "Machine Learning", "GPU", "Chip Design")
   - Business categories (e.g., "Enterprise Software", "Consumer Electronics")
   - Include 3-6 relevant tags

Example format:
{{
  "description": "NVIDIA Corporation is a leading technology company specializing in graphics processing units (GPUs) and AI computing platforms. The company dominates the AI chip market with its data center GPUs powering large language models and machine learning workloads. NVIDIA's products are essential for AI training and inference across cloud providers and enterprises.",
  "sector": "Technology",
  "sectors": ["Semiconductor", "AI", "GPU", "Data Center", "Machine Learning", "Chip Design"]
}}

IMPORTANT: Return ONLY the JSON object, no markdown formatting, no code blocks, no explanations."""
        
        return prompt
    
    def _validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate LLM response structure.
        
        Args:
            response: LLM response dictionary
            
        Raises:
            ValueError: If response is missing required fields
        """
        required_fields = ["description", "sector", "sectors"]
        
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate field types
        if not isinstance(response["description"], str):
            raise ValueError("'description' must be a string")
        
        if not isinstance(response["sector"], str):
            raise ValueError("'sector' must be a string")
        
        if not isinstance(response["sectors"], list):
            raise ValueError("'sectors' must be a list")
        
        # Validate description is not empty
        if not response["description"].strip():
            raise ValueError("'description' cannot be empty")
        
        logger.debug("Response validation passed")

