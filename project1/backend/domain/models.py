from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

# ⚠️ 重要：Node 字段定义应该与 node_schema.py 保持一致！
# 修改字段时，请同时更新 node_schema.py 和这里的定义
from .node_schema import NODE_FIELDS, COMPUTED_FIELDS

ScalarMap = Mapping[str, object]
MutableScalarMap = Dict[str, object]


@dataclass(frozen=True)
class Relationship:
    """A directional edge between two nodes."""

    id: str
    source_id: str
    target_id: str
    type: str  # e.g., "owns", "partners_with", "competes_with", etc.
    strength: Optional[float] = None
    created_datetime: Optional[datetime] = None


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
            edge: MutableScalarMap = {
                "id": relationship.id,
                "source": relationship.source_id,
                "target": relationship.target_id,
                "type": relationship.type,
            }
            if relationship.strength is not None:
                edge["strength"] = relationship.strength
            if relationship.created_datetime is not None:
                edge["created_datetime"] = relationship.created_datetime.isoformat()
            edges.append(edge)
        return edges


