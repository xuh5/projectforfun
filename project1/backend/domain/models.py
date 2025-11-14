from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Tuple

ScalarMap = Mapping[str, object]
MutableScalarMap = Dict[str, object]


@dataclass(frozen=True)
class Relationship:
    """A directional edge between two companies."""

    id: str
    source_id: str
    target_id: str
    strength: Optional[float] = None


@dataclass(frozen=True)
class Company:
    """Core company entity used across the domain."""

    id: str
    label: str
    description: str
    sector: Optional[str] = None
    color: Optional[str] = None
    metadata: ScalarMap = field(default_factory=dict)
    position: Optional[Tuple[float, float, float]] = None

    def to_detail(self) -> "CompanyDetail":
        """Materialize the frontend-facing detail payload."""
        payload: MutableScalarMap = dict(self.metadata)
        payload.setdefault("label", self.label)
        payload.setdefault("description", self.description)
        if self.sector:
            payload.setdefault("sector", self.sector)
        if self.color:
            payload.setdefault("color", self.color)
        return CompanyDetail(id=self.id, data=payload)


@dataclass(frozen=True)
class CompanyDetail:
    """Detailed representation consumed by the frontend."""

    id: str
    data: ScalarMap


@dataclass(frozen=True)
class GraphSnapshot:
    """Immutable snapshot of the relationship graph."""

    companies: Iterable[Company]
    relationships: Iterable[Relationship]

    def to_node_payload(self) -> List[Mapping[str, object]]:
        nodes: List[MutableScalarMap] = []
        for company in self.companies:
            node_payload: MutableScalarMap = {
                "id": company.id,
                "data": {
                    "label": company.label,
                    "description": company.description,
                    **company.metadata,
                },
            }
            if company.color:
                node_payload.setdefault("color", company.color)
            if company.position:
                x, y, z = company.position
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
            }
            if relationship.strength is not None:
                edge["strength"] = relationship.strength
            edges.append(edge)
        return edges


