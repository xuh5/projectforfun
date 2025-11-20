from __future__ import annotations

from typing import Iterable, Optional, Protocol, Sequence

from backend.domain import Node, NodeDetail, GraphSnapshot
from backend.repositories import GraphRepositoryProtocol


class GraphServiceProtocol(Protocol):
    """High-level operations available to the API layer."""

    def get_graph_snapshot(self) -> GraphSnapshot:
        ...

    def get_node_detail(self, node_id: str) -> Optional[NodeDetail]:
        ...

    def search_nodes(self, query: str, limit: int = 5) -> Sequence[Node]:
        ...


class GraphService(GraphServiceProtocol):
    """Default service that orchestrates repository access."""

    def __init__(self, repository: GraphRepositoryProtocol) -> None:
        self._repository = repository

    def get_graph_snapshot(self) -> GraphSnapshot:
        return self._repository.get_graph_snapshot()

    def get_node_detail(self, node_id: str) -> Optional[NodeDetail]:
        node = self._repository.get_node(node_id)
        if not node:
            return None
        return node.to_detail()

    def search_nodes(self, query: str, limit: int = 5) -> Sequence[Node]:
        normalized = query.strip().lower()
        if not normalized:
            return ()

        matches: list[Node] = []
        for node in self._repository.list_nodes():
            haystacks: Iterable[str] = (
                node.label,
                node.description,
                node.sector or "",
                node.type or "",
            )
            if any(normalized in value.lower() for value in haystacks if value):
                matches.append(node)
        matches.sort(key=lambda node: node.metadata.get("score", 0), reverse=True)
        return matches[:limit]


