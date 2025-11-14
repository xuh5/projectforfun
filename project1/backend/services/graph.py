from __future__ import annotations

from typing import Iterable, Optional, Protocol, Sequence

from backend.domain import Company, CompanyDetail, GraphSnapshot
from backend.repositories import GraphRepositoryProtocol


class GraphServiceProtocol(Protocol):
    """High-level operations available to the API layer."""

    def get_graph_snapshot(self) -> GraphSnapshot:
        ...

    def get_company_detail(self, company_id: str) -> Optional[CompanyDetail]:
        ...

    def search_companies(self, query: str, limit: int = 5) -> Sequence[Company]:
        ...


class GraphService(GraphServiceProtocol):
    """Default service that orchestrates repository access."""

    def __init__(self, repository: GraphRepositoryProtocol) -> None:
        self._repository = repository

    def get_graph_snapshot(self) -> GraphSnapshot:
        return self._repository.get_graph_snapshot()

    def get_company_detail(self, company_id: str) -> Optional[CompanyDetail]:
        company = self._repository.get_company(company_id)
        if not company:
            return None
        return company.to_detail()

    def search_companies(self, query: str, limit: int = 5) -> Sequence[Company]:
        normalized = query.strip().lower()
        if not normalized:
            return ()

        matches: list[Company] = []
        for company in self._repository.list_companies():
            haystacks: Iterable[str] = (
                company.label,
                company.description,
                company.sector or "",
            )
            if any(normalized in value.lower() for value in haystacks if value):
                matches.append(company)
        matches.sort(key=lambda company: company.metadata.get("score", 0), reverse=True)
        return matches[:limit]


