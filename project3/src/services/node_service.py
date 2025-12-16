"""Node validation and management service."""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NodeService:
    """Service for validating and managing nodes in project1."""
    
    def __init__(self, project1_client, openai_client):
        """
        Initialize node service.
        
        Args:
            project1_client: Project1 API client
            openai_client: OpenAI client for generating company info
        """
        self.project1_client = project1_client
        self.openai_client = openai_client
    
    def get_or_create_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get existing node or create a new one if it doesn't exist.
        
        Args:
            node_id: Node ID (e.g., NASDAQ ticker like 'AAPL')
            
        Returns:
            Node data
        """
        # Check if node already exists
        existing_node = self.project1_client.get_node(node_id)
        
        if existing_node:
            logger.info(f"Node {node_id} already exists")
            return self._normalize_node(existing_node)
        
        logger.info(f"Node {node_id} not found, will need to create")
        return None
    
    def generate_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Generate company information using AI.
        
        Args:
            ticker: Stock ticker (e.g., 'AAPL', 'MSFT')
            
        Returns:
            Generated company information
        """
        system_prompt = (
            "You are a financial data expert. Provide accurate company information "
            "based on stock tickers. Always return valid JSON format without any "
            "markdown code blocks or extra text."
        )
        
        prompt = f"""Generate company information for stock ticker: {ticker}

Provide accurate information and return a JSON object with this exact structure:
{{
  "id": "{ticker}",
  "type": "company",
  "label": "Full Company Name",
  "description": "Brief description of the company (2-3 sentences)",
  "sector": "Industry Sector"
}}

IMPORTANT: Return ONLY the JSON object, no markdown formatting, no explanations."""
        
        try:
            response = self.openai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more factual responses
            )
            
            # Ensure required fields
            company_info = {
                "id": response.get("id", ticker).upper(),
                "type": response.get("type", "company"),
                "label": response.get("label", ""),
                "description": response.get("description", ""),
                "sector": response.get("sector", ""),
                "metadata": response.get("metadata", {}),
            }
            
            logger.info(f"Generated info for {ticker}: {company_info['label']}")
            return company_info
            
        except Exception as e:
            logger.error(f"Failed to generate company info for {ticker}: {e}")
            raise ValueError(f"Could not generate company information for {ticker}")
    
    def create_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node in project1.
        
        Args:
            node_data: Node data to create
            
        Returns:
            Created node data
        """
        try:
            result = self.project1_client.create_node(node_data)
            logger.info(f"Created node: {node_data['id']}")
            return result
        except Exception as e:
            logger.error(f"Failed to create node {node_data.get('id')}: {e}")
            raise
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker format is valid.
        
        Args:
            ticker: Stock ticker
            
        Returns:
            True if valid format
        """
        if not ticker:
            return False
        
        # Basic validation: 1-5 uppercase letters
        ticker = ticker.strip().upper()
        return len(ticker) >= 1 and len(ticker) <= 5 and ticker.isalpha()
    
    def get_all_companies(self) -> list[Dict[str, Any]]:
        """
        Get all existing companies from project1.
        
        Returns:
            List of company nodes
        """
        try:
            companies = self.project1_client.get_existing_companies()
            logger.info(f"Retrieved {len(companies)} existing companies")
            return companies
        except Exception as e:
            logger.error(f"Failed to get existing companies: {e}")
            return []
    
    def _normalize_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize node data from project1 API response."""
        # Handle both direct node data and wrapped format
        if "data" in node_data:
            data = node_data["data"]
            node_id = node_data.get("id", data.get("id"))
        else:
            data = node_data
            node_id = data.get("id")
        
        return {
            "id": node_id,
            "type": data.get("type", "company"),
            "label": data.get("label", ""),
            "description": data.get("description", ""),
            "sector": data.get("sector"),
            "color": data.get("color"),
            "metadata": data.get("metadata", {}),
        }

