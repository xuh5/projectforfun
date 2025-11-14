from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

from backend.domain import Company, GraphSnapshot, Relationship
from backend.repositories.base import GraphRepositoryProtocol


@dataclass(frozen=True)
class _GraphCache:
    companies: Sequence[Company]
    relationships: Sequence[Relationship]
    company_index: Dict[str, Company]


class MockGraphRepository(GraphRepositoryProtocol):
    """Deterministic repository seeded with pseudo-random sample data."""

    def __init__(self, seed: int = 42, company_count: int = 18) -> None:
        self._seed = seed
        self._company_count = company_count
        self._cache: Optional[_GraphCache] = None

    def _ensure_cache(self) -> _GraphCache:
        if self._cache is None:
            self._cache = self._generate_cache()
        return self._cache

    def _generate_cache(self) -> _GraphCache:
        rng = random.Random(self._seed)
        companies: List[Company] = []
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
        for index in range(self._company_count):
            color = palette[index % len(palette)]
            sector = sectors[index % len(sectors)]
            company_id = f"node-{index + 1}"
            angle = (2 * math.pi * index) / max(self._company_count, 1)
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            z = rng.uniform(-radius / 2, radius / 2)

            metadata = {
                "sector": sector,
                "category": categories[index % len(categories)],
                "marketCap": round(rng.uniform(100, 900), 2),
                "score": round(rng.uniform(0.1, 1.0), 3),
            }
            company = Company(
                id=company_id,
                label=f"Company {index + 1}",
                description=f"Company {index + 1} operates in the {sector} space.",
                sector=sector,
                color=color,
                metadata=metadata,
                position=(x, y, z),
            )
            companies.append(company)

        for index in range(self._company_count):
            source = companies[index]
            primary_target = companies[(index + 1) % self._company_count]
            secondary_target = companies[(index + self._company_count // 3) % self._company_count]
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

        company_index = {company.id: company for company in companies}
        return _GraphCache(
            companies=tuple(companies),
            relationships=tuple(relationships),
            company_index=company_index,
        )

    def get_graph_snapshot(self) -> GraphSnapshot:
        cache = self._ensure_cache()
        return GraphSnapshot(companies=cache.companies, relationships=cache.relationships)

    def list_companies(self) -> Iterable[Company]:
        return self._ensure_cache().companies

    def list_relationships(self) -> Iterable[Relationship]:
        return self._ensure_cache().relationships

    def get_company(self, company_id: str) -> Optional[Company]:
        return self._ensure_cache().company_index.get(company_id)

