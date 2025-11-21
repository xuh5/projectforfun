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
    """
    Default service that orchestrates repository access.
    
    ⚠️ NOTE: Currently filters to 'company' type nodes only.
    This is a temporary restriction to support single-type graphs.
    Future enhancements may support multiple types (overlapped or separate graphs).
    """

    def __init__(self, repository: GraphRepositoryProtocol) -> None:
        self._repository = repository

    def get_graph_snapshot(self) -> GraphSnapshot:
        """
        Get graph snapshot, currently filtered to only include 'company' type nodes.
        
        TODO: In the future, this may accept a type parameter or support multiple types.
        """
        snapshot = self._repository.get_graph_snapshot()
        # Filter to only company nodes for the current graph
        company_nodes = [node for node in snapshot.nodes if node.type == "company"]
        company_node_ids = {node.id for node in company_nodes}
        # Filter relationships to only include edges between company nodes
        company_relationships = [
            rel for rel in snapshot.relationships
            if rel.source_id in company_node_ids and rel.target_id in company_node_ids
        ]
        return GraphSnapshot(nodes=company_nodes, relationships=company_relationships)

    def get_node_detail(self, node_id: str) -> Optional[NodeDetail]:
        node = self._repository.get_node(node_id)
        if not node:
            return None
        return node.to_detail()

    def search_nodes(self, query: str, limit: int = 5) -> Sequence[Node]:
        """
        Search nodes, currently filtered to only search 'company' type nodes.
        
        TODO: In the future, this may accept a type parameter or search across all types.
        """
        normalized = query.strip().lower()
        if not normalized:
            return ()

        matches: list[Node] = []
        # Only search company nodes for the current graph
        for node in self._repository.list_nodes():
            # Filter to company type only
            if node.type != "company":
                continue
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


