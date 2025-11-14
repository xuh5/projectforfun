from __future__ import annotations

from typing import Any, Dict, List, Sequence

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok")
    message: str = Field(..., example="Backend is running")


class GraphNodePayload(BaseModel):
    id: str
    position: Dict[str, float] | None = None
    color: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)


class GraphEdgePayload(BaseModel):
    id: str
    source: str
    target: str
    strength: float | None = None


class GraphResponse(BaseModel):
    nodes: List[GraphNodePayload]
    edges: List[GraphEdgePayload]


class CompanyDetailResponse(BaseModel):
    id: str
    data: Dict[str, Any]


class SearchHit(BaseModel):
    id: str
    label: str
    sector: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    results: Sequence[SearchHit]


# CRUD Schemas
class CompanyCreateRequest(BaseModel):
    id: str
    label: str
    description: str
    sector: str | None = None
    color: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Note: position is not stored - it's generated dynamically during graph layout


class CompanyUpdateRequest(BaseModel):
    label: str | None = None
    description: str | None = None
    sector: str | None = None
    color: str | None = None
    metadata: Dict[str, Any] | None = None
    # Note: position is not stored - it's generated dynamically during graph layout


class RelationshipCreateRequest(BaseModel):
    id: str
    source_id: str
    target_id: str
    strength: float | None = None


class RelationshipUpdateRequest(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    strength: float | None = None


class MessageResponse(BaseModel):
    message: str


