from __future__ import annotations

from typing import Iterable, Optional, Protocol

from backend.domain import Node, GraphSnapshot, Relationship


class GraphRepositoryProtocol(Protocol):
    """Repository contract for loading graph data."""

    def get_graph_snapshot(self) -> GraphSnapshot:
        ...

    def list_nodes(self) -> Iterable[Node]:
        ...

    def list_relationships(self) -> Iterable[Relationship]:
        ...

    def get_node(self, node_id: str) -> Optional[Node]:
        ...


