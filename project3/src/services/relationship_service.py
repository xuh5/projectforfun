"""Relationship generation and management service."""

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


class RelationshipService:
    """Service for generating and managing relationships."""
    
    def __init__(self, project1_client, openai_client, node_service):
        """
        Initialize relationship service.
        
        Args:
            project1_client: Project1 API client
            openai_client: OpenAI client
            node_service: Node service for validation
        """
        self.project1_client = project1_client
        self.openai_client = openai_client
        self.node_service = node_service
    
    def generate_relationships(
        self,
        source_company: Dict[str, Any],
        count: int = 5,
        existing_companies: List[Dict[str, Any]] = None,
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate relationship suggestions for a company.
        
        Args:
            source_company: Source company information
            count: Number of relationships to generate
            existing_companies: Optional list of existing companies to avoid duplicates
            include_metadata: Whether to include metadata fields
            
        Returns:
            List of relationship suggestions
        """
        if existing_companies is None:
            existing_companies = self.node_service.get_all_companies()
        
        prompt = self._build_relationship_prompt(
            source_company, existing_companies, count, include_metadata
        )
        
        system_prompt = (
            "You are a business relationship analyst with deep knowledge of corporate "
            "structures, partnerships, and industry relationships. Generate realistic "
            "and accurate business relationships based on company information. "
            "Always return valid JSON without any markdown formatting or explanatory text."
        )
        
        try:
            response = self.openai_client.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
            )
            
            # Parse and normalize response
            relationships_raw = self._parse_response(response)
            
            # Normalize relationships
            relationships = []
            for rel in relationships_raw[:count]:
                try:
                    normalized = self._normalize_relationship(rel)
                    relationships.append(normalized)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Skipping invalid relationship: {e}")
                    continue
            
            logger.info(f"Generated {len(relationships)} relationships for {source_company['id']}")
            return relationships
            
        except Exception as e:
            logger.error(f"Failed to generate relationships: {e}")
            raise ValueError(f"Failed to generate relationships: {e}")
    
    def create_relationship(
        self,
        source_id: str,
        target_company: Dict[str, Any],
        relationship: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a relationship, ensuring target node exists.
        
        Args:
            source_id: Source node ID
            target_company: Target company information
            relationship: Relationship data (type, strength, metadata)
            
        Returns:
            Result with status and details
        """
        target_id = target_company.get("id")
        
        try:
            # Check if target node exists
            existing_node = self.project1_client.get_node(target_id)
            
            # Create target node if it doesn't exist
            if not existing_node:
                node_data = {
                    "id": target_id,
                    "type": target_company.get("type", "company"),
                    "label": target_company.get("label", ""),
                    "description": target_company.get("description", ""),
                    "sector": target_company.get("sector"),
                    "color": target_company.get("color"),
                    "metadata": target_company.get("metadata", {}),
                }
                self.project1_client.create_node(node_data)
                action = "created_node_and_relationship"
                logger.info(f"Created new node: {target_id}")
            else:
                action = "created_relationship"
                logger.info(f"Node {target_id} already exists")
            
            # Create relationship
            self.project1_client.create_relationship(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship.get("type", "works_with"),
                strength=relationship.get("strength"),
                metadata=relationship.get("metadata", {}),
            )
            
            logger.info(f"Created relationship: {source_id} -> {target_id}")
            
            return {
                "status": "success",
                "action": action,
                "target_company": target_company.get("label", target_id),
            }
            
        except Exception as e:
            logger.error(f"Failed to create relationship {source_id} -> {target_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "target_company": target_company.get("label", "unknown"),
            }
    
    def _build_relationship_prompt(
        self,
        source_company: Dict[str, Any],
        existing_companies: List[Dict[str, Any]],
        count: int,
        include_metadata: bool = True,
    ) -> str:
        """Build prompt for relationship generation."""
        source_info = f"""
Source Company Information:
- ID: {source_company.get('id', 'N/A')}
- Name: {source_company.get('label', source_company.get('name', 'N/A'))}
- Description: {source_company.get('description', 'N/A')}
- Sector: {source_company.get('sector', 'N/A')}
"""
        
        existing_info = ""
        if existing_companies:
            existing_names = []
            for c in existing_companies[:20]:
                name = c.get('label', c.get('name', c.get('id', '')))
                if name:
                    existing_names.append(name)
            if existing_names:
                existing_info = f"\nExisting companies in the graph (avoid duplicates): {', '.join(existing_names)}\n"
        
        metadata_req = """MUST include:
     * alpha: float (0.0-1.0, influence weight)
     * beta: float (0.0-1.0, reciprocal influence)
     * decay: float (0.0-1.0, decay rate over time)
     * threshold: float (0.0-1.0, activation threshold)
     * weight: float (0.0-1.0, overall importance)""" if include_metadata else "Optional, can be empty object {}"
        
        metadata_example = '"alpha": 0.7, "beta": 0.6, "decay": 0.1, "threshold": 0.5, "weight": 0.8' if include_metadata else ''
        
        prompt = f"""You are a business relationship analyst. Generate realistic business relationships for a company.

{source_info}
{existing_info}

Generate {count} business relationships for this company. For each relationship:

1. **Target Company**: Generate complete company information:
   - id: Stock ticker or short code
   - type: "company"
   - label: Full company name
   - description: Brief description (2-3 sentences)
   - sector: Industry sector
   - color: Hex color (e.g., "#FF5733")
   - metadata: Empty object {{}}

2. **Relationship**: The relationship between source and target:
   - type: Relationship type (owns, partners_with, competes_with, supplies_to, etc.)
   - strength: Relationship strength (float 0.0-1.0)
   - metadata: {metadata_req}

CRITICAL: Return EXACTLY {count} relationships in a JSON array.

Example:
[
  {{
    "target_company": {{
      "id": "MSFT",
      "type": "company",
      "label": "Microsoft Corporation",
      "description": "Technology company...",
      "sector": "Technology",
      "color": "#00A4EF",
      "metadata": {{}}
    }},
    "relationship": {{
      "type": "partners_with",
      "strength": 0.85,
      "metadata": {{{metadata_example}}}
    }}
  }}
]

Return ONLY a valid JSON array with EXACTLY {count} items. NO markdown, NO explanations."""
        
        return prompt
    
    def _parse_response(self, response: Any) -> List[Dict[str, Any]]:
        """Parse OpenAI response to extract relationships."""
        if isinstance(response, dict):
            if "relationships" in response:
                return response["relationships"]
            elif "target_company" in response and "relationship" in response:
                return [response]
            else:
                return [response]
        elif isinstance(response, list):
            return response
        else:
            raise ValueError(f"Unexpected response type: {type(response)}")
    
    def _normalize_relationship(self, rel: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate a relationship object."""
        if "target_company" not in rel:
            raise ValueError("Missing 'target_company' field")
        if "relationship" not in rel:
            raise ValueError("Missing 'relationship' field")
        
        target = rel["target_company"]
        relationship = rel["relationship"]
        
        return {
            "target_company": {
                "id": target.get("id", "").upper() if target.get("id") else "",
                "type": target.get("type", "company"),
                "label": target.get("label", target.get("name", "")),
                "description": target.get("description", ""),
                "sector": target.get("sector"),
                "color": target.get("color"),
                "metadata": target.get("metadata", {}),
            },
            "relationship": {
                "type": relationship.get("type", "works_with"),
                "strength": relationship.get("strength"),
                "metadata": relationship.get("metadata", {}),
            },
        }

