from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Literal, Mapping, Optional, Tuple

# ⚠️ 重要：Node 字段定义应该与 node_schema.py 保持一致！
# 修改字段时，请同时更新 node_schema.py 和这里的定义
from .node_schema import NODE_FIELDS, COMPUTED_FIELDS

ScalarMap = Mapping[str, object]
MutableScalarMap = Dict[str, object]


@dataclass(frozen=True)
class Relationship:
    """
    A directional edge between two nodes with weight-based visibility.
    
    Metadata can contain:
    - "alpha": float - Weight parameter alpha
    - "beta": float - Weight parameter beta
    - "threshold": float - Visibility threshold (edge is visible if current_weight >= threshold)
    - "decay": float - Decay rate (0-1), how much weight decreases over time
    - "decay_rate": float - Alternative decay rate parameter
    - "initial_weight": float - Initial weight value
    - "current_weight": float - Current computed weight (can be manually set or computed)
    - "visible": bool - Manual visibility override (optional)
    """

    id: str
    source_id: str
    target_id: str
    type: str  # e.g., "owns", "partners_with", "competes_with", etc.
    strength: Optional[float] = None
    created_datetime: Optional[datetime] = None
    metadata: ScalarMap = field(default_factory=dict)
    
    def compute_weight(self) -> float:
        """
        Compute current weight from metadata or strength.
        
        Simple calculation: uses current_weight from metadata if available,
        otherwise falls back to initial_weight or strength.
        
        Returns:
            Computed weight value
        """
        # If current_weight is explicitly set in metadata, use it
        if "current_weight" in self.metadata:
            return float(self.metadata.get("current_weight", 0.0))
        
        # Otherwise use initial_weight or strength as base
        initial = self.metadata.get("initial_weight")
        if initial is None:
            initial = self.strength if self.strength is not None else 1.0
        
        # Apply alpha and beta if provided (simple multiplication)
        alpha = self.metadata.get("alpha", 1.0)
        beta = self.metadata.get("beta", 1.0)
        
        weight = float(initial) * float(alpha) * float(beta)
        
        return weight
    
    def apply_decay(self) -> float:
        """
        Calculate what the weight would be after applying decay.
        
        This function does NOT modify the relationship - it's just a calculation.
        You can use this to preview what the weight would be after decay,
        then manually update metadata["current_weight"] if needed.
        
        Returns:
            Calculated weight after decay (but doesn't save it)
        """
        # Get current weight (before decay)
        current = self.compute_weight()
        
        # Get decay parameters from metadata
        decay = self.metadata.get("decay", 0.0)
        decay_rate = self.metadata.get("decay_rate", 0.0)
        
        # Use decay if provided, otherwise decay_rate
        effective_decay = decay if decay != 0.0 else decay_rate
        
        # Simple decay formula: new_weight = current * (1 - decay)
        # TODO: You can change this formula later when you decide on the decay logic
        decayed_weight = current * (1 - effective_decay)
        
        return decayed_weight
    
    def is_visible(self, computed_weight: Optional[float] = None) -> bool:
        """
        Determine if edge should be visible based on threshold.
        
        Args:
            computed_weight: Pre-computed weight (optional, will compute if not provided)
            
        Returns:
            True if edge should be visible, False otherwise
        """
        # Check for manual visibility override
        if "visible" in self.metadata:
            manual_visible = self.metadata.get("visible")
            if isinstance(manual_visible, bool):
                return manual_visible
        
        # Get threshold (default: 0.0, meaning all edges visible by default)
        threshold = self.metadata.get("threshold", 0.0)
        
        # Get current weight
        if computed_weight is not None:
            weight = computed_weight
        else:
            # Compute weight if not provided
            weight = self.compute_weight()
        
        return weight >= threshold


@dataclass(frozen=True)
class Node:
    """
    Core node entity used across the domain. Can represent companies or other entity types.
    
    ⚠️ 字段定义来源：backend/domain/node_schema.py
    添加新字段时，请先在 node_schema.py 中定义，然后在这里添加。
    """

    id: str
    type: str  # e.g., "company", "person", "project", etc.
    label: str
    description: str
    sector: Optional[str] = None
    color: Optional[str] = None
    metadata: ScalarMap = field(default_factory=dict)
    position: Optional[Tuple[float, float, float]] = None

    def to_detail(self) -> "NodeDetail":
        """Materialize the frontend-facing detail payload."""
        payload: MutableScalarMap = dict(self.metadata)
        # 从 schema 定义中获取需要包含在 detail 中的字段
        for field_def in NODE_FIELDS:
            if field_def.in_frontend:
                value = getattr(self, field_def.name, None)
                if value is not None:
                    payload.setdefault(field_def.name, value)
        # 确保 type 总是包含
        payload.setdefault("type", self.type)
        return NodeDetail(id=self.id, data=payload)


@dataclass(frozen=True)
class NodeDetail:
    """Detailed representation consumed by the frontend."""

    id: str
    data: ScalarMap


@dataclass(frozen=True)
class GraphSnapshot:
    """Immutable snapshot of the relationship graph."""

    nodes: Iterable[Node]
    relationships: Iterable[Relationship]

    def to_node_payload(self) -> List[Mapping[str, object]]:
        nodes: List[MutableScalarMap] = []
        for node in self.nodes:
            node_payload: MutableScalarMap = {
                "id": node.id,
                "data": {
                    "label": node.label,
                    "description": node.description,
                    "type": node.type,
                    **node.metadata,
                },
            }
            if node.color:
                node_payload.setdefault("color", node.color)
            if node.position:
                x, y, z = node.position
                node_payload["position"] = {"x": x, "y": y, "z": z}
            nodes.append(node_payload)
        return nodes

    def to_edge_payload(self) -> List[Mapping[str, object]]:
        edges: List[MutableScalarMap] = []
        for relationship in self.relationships:
            # Compute current weight
            current_weight = relationship.compute_weight()
            
            # Check visibility
            visible = relationship.is_visible(computed_weight=current_weight)
            
            edge: MutableScalarMap = {
                "id": relationship.id,
                "source": relationship.source_id,
                "target": relationship.target_id,
                "type": relationship.type,
                "current_weight": current_weight,
                "visible": visible,
            }
            
            # Add optional fields
            if relationship.strength is not None:
                edge["strength"] = relationship.strength
            if relationship.created_datetime is not None:
                edge["created_datetime"] = relationship.created_datetime.isoformat()
            
            # Add metadata if present
            if relationship.metadata:
                edge["metadata"] = dict(relationship.metadata)
            
            edges.append(edge)
        return edges


@dataclass(frozen=True)
class User:
    """User entity in the domain layer."""

    id: str  # Supabase user ID
    email: str
    balance: float = 1000.0
    role: str = "user"  # "user" or "admin"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class NodeRequest:
    """Node creation request entity that requires approval."""

    id: int
    requestor_id: str
    status: Literal["pending", "approved", "rejected"]
    node_id: str
    node_type: str
    label: str
    description: str
    sector: Optional[str] = None
    color: Optional[str] = None
    metadata: ScalarMap = field(default_factory=dict)
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "requestor_id": self.requestor_id,
            "status": self.status,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "description": self.description,
            "sector": self.sector,
            "color": self.color,
            "metadata": dict(self.metadata),
            "approver_id": self.approver_id,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


