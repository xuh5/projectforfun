"""Client for interacting with project1 API."""

from typing import Any, Dict, List, Optional

import httpx


class Project1Client:
    """Client for project1 API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        """
        Initialize project1 client.
        
        Args:
            base_url: Base URL of project1 API (default: http://localhost:8000)
            token: Optional authentication token
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.client = httpx.Client(timeout=30.0)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def get_existing_companies(self) -> List[Dict[str, Any]]:
        """
        Get list of existing companies from project1.
        
        Returns:
            List of company nodes
        """
        try:
            response = self.client.get(
                f"{self.base_url}/api/nodes",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter to only company type nodes
            companies = []
            for node in data.get("nodes", []):
                node_data = node.get("data", {})
                if node_data.get("type") == "company":
                    companies.append({
                        "id": node.get("id"),
                        "label": node_data.get("label", ""),
                        "description": node_data.get("description", ""),
                        "sector": node_data.get("sector"),
                        "type": "company",
                    })
            
            return companies
        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch existing companies: {e}")
    
    def create_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a node in project1.
        
        Args:
            node_data: Node data including id, type, label, description, sector, color, metadata
            
        Returns:
            Created node data
        """
        try:
            response = self.client.post(
                f"{self.base_url}/api/nodes",
                json=node_data,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_detail = e.response.json().get("detail", str(e))
                raise ValueError(f"Failed to create node: {error_detail}")
            raise RuntimeError(f"Failed to create node: {e}")
    
    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        strength: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a relationship in project1.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Type of relationship
            strength: Optional relationship strength
            metadata: Optional relationship metadata
            
        Returns:
            Created relationship data
        """
        try:
            rel_data = {
                "source_id": source_id,
                "target_id": target_id,
                "type": relationship_type,
            }
            if strength is not None:
                rel_data["strength"] = strength
            if metadata:
                rel_data["metadata"] = metadata
            
            response = self.client.post(
                f"{self.base_url}/api/relationships",
                json=rel_data,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                error_detail = e.response.json().get("detail", str(e))
                raise ValueError(f"Failed to create relationship: {error_detail}")
            raise RuntimeError(f"Failed to create relationship: {e}")
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Node data if exists, None otherwise
        """
        try:
            response = self.client.get(
                f"{self.base_url}/api/nodes/{node_id}",
                headers=self._get_headers(),
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

