from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from backend.domain import Node, GraphSnapshot, Relationship
from backend.repositories.base import GraphRepositoryProtocol


@dataclass(frozen=True)
class _GraphCache:
    nodes: Sequence[Node]
    relationships: Sequence[Relationship]
    node_index: Dict[str, Node]


class MockGraphRepository(GraphRepositoryProtocol):
    """Deterministic repository seeded with pseudo-random sample data."""

    def __init__(self, seed: int = 42, node_count: int = 18) -> None:
        self._seed = seed
        self._node_count = node_count
        self._cache: Optional[_GraphCache] = None

    def _ensure_cache(self) -> _GraphCache:
        if self._cache is None:
            self._cache = self._generate_cache()
        return self._cache

    def _generate_cache(self) -> _GraphCache:
        rng = random.Random(self._seed)
        nodes: List[Node] = []
        relationships: List[Relationship] = []

        palette = [
            "#667eea",
            "#764ba2",
            "#f093fb",
            "#4f46e5",
            "#22d3ee",
            "#f472b6",
            "#10b981",
            "#f97316",
        ]
        sectors = ["AI", "Automotive", "Consumer", "Enterprise", "Cloud", "Semiconductors"]
        categories = ["Tier 1", "Tier 2", "Tier 3"]

        radius = 12.0
        for index in range(self._node_count):
            color = palette[index % len(palette)]
            sector = sectors[index % len(sectors)]
            node_id = f"node-{index + 1}"
            angle = (2 * math.pi * index) / max(self._node_count, 1)
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            z = rng.uniform(-radius / 2, radius / 2)

            metadata = {
                "sector": sector,
                "category": categories[index % len(categories)],
                "marketCap": round(rng.uniform(100, 900), 2),
                "score": round(rng.uniform(0.1, 1.0), 3),
            }
            node = Node(
                id=node_id,
                type="company",  # Default type for mock data
                label=f"Company {index + 1}",
                description=f"Company {index + 1} operates in the {sector} space.",
                sector=sector,
                color=color,
                metadata=metadata,
                position=(x, y, z),
            )
            nodes.append(node)

        for index in range(self._node_count):
            source = nodes[index]
            primary_target = nodes[(index + 1) % self._node_count]
            secondary_target = nodes[(index + self._node_count // 3) % self._node_count]
            relationships.append(
                Relationship(
                    id=f"edge-{source.id}-{primary_target.id}",
                    source_id=source.id,
                    target_id=primary_target.id,
                    strength=0.35,
                )
            )
            if primary_target.id != secondary_target.id:
                relationships.append(
                    Relationship(
                        id=f"edge-{source.id}-{secondary_target.id}",
                        source_id=source.id,
                        target_id=secondary_target.id,
                        strength=0.15,
                    )
                )

        node_index = {node.id: node for node in nodes}
        return _GraphCache(
            nodes=tuple(nodes),
            relationships=tuple(relationships),
            node_index=node_index,
        )

    def get_graph_snapshot(self) -> GraphSnapshot:
        cache = self._ensure_cache()
        return GraphSnapshot(nodes=cache.nodes, relationships=cache.relationships)

    def list_nodes(self) -> Iterable[Node]:
        return self._ensure_cache().nodes

    def list_relationships(self) -> Iterable[Relationship]:
        return self._ensure_cache().relationships

    def get_node(self, node_id: str) -> Optional[Node]:
        return self._ensure_cache().node_index.get(node_id)

