"""Data models for node generation."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class NodeData:
    """
    Data model representing a node compatible with project1's NodeCreateRequest schema.
    
    Attributes:
        id: NASDAQ symbol (e.g., "AAPL")
        label: Company name (e.g., "Apple Inc.")
        description: AI-generated description (2-3 sentences)
        sector: Main sector/industry classification
        type: Node type (default: "company")
        color: Display color (optional, hex format)
        metadata: Additional data including multiple sector tags
    """
    id: str
    label: str
    description: str
    sector: Optional[str] = None
    type: str = "company"
    color: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format compatible with project1 NodeCreateRequest.
        
        Returns:
            Dictionary with all required and optional fields for node creation.
        """
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "description": self.description,
            "sector": self.sector,
            "color": self.color,
            "metadata": self.metadata if self.metadata else {},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeData":
        """
        Create NodeData instance from dictionary.
        
        Args:
            data: Dictionary containing node data
            
        Returns:
            NodeData instance
        """
        return cls(
            id=data["id"],
            label=data["label"],
            description=data["description"],
            sector=data.get("sector"),
            type=data.get("type", "company"),
            color=data.get("color"),
            metadata=data.get("metadata", {}),
        )

