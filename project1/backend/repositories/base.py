from __future__ import annotations

from typing import Iterable, Optional, Protocol

from backend.domain import Company, GraphSnapshot, Relationship


class GraphRepositoryProtocol(Protocol):
    """Repository contract for loading graph data."""

    def get_graph_snapshot(self) -> GraphSnapshot:
        ...

    def list_companies(self) -> Iterable[Company]:
        ...

    def list_relationships(self) -> Iterable[Relationship]:
        ...

    def get_company(self, company_id: str) -> Optional[Company]:
        ...


