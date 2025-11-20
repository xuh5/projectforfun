from __future__ import annotations

from typing import Any, Dict, List, Sequence

from pydantic import BaseModel, Field

# ⚠️ 重要：字段定义应该与 node_schema.py 保持一致！
# 修改字段时，请同时更新 node_schema.py 和这里的定义
from backend.domain.node_schema import NODE_FIELDS


class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="ok")
    message: str = Field(..., example="Backend is running")


class GraphNodePayload(BaseModel):
    id: str
    position: Dict[str, float] | None = None
    color: str | None = None
    data: Dict[str, Any] = Field(default_factory=dict)  # data.type should indicate node type (e.g., "company")


class GraphEdgePayload(BaseModel):
    id: str
    source: str
    target: str
    strength: float | None = None


class GraphResponse(BaseModel):
    nodes: List[GraphNodePayload]
    edges: List[GraphEdgePayload]


class NodeDetailResponse(BaseModel):
    id: str
    data: Dict[str, Any]


class SearchHit(BaseModel):
    id: str
    label: str
    type: str | None = None
    sector: str | None = None
    score: float | None = None


class SearchResponse(BaseModel):
    query: str
    results: Sequence[SearchHit]


# CRUD Schemas
# ⚠️ 字段定义来源：backend/domain/node_schema.py
# 添加新字段时，请先在 node_schema.py 中定义，然后在这里添加
class NodeCreateRequest(BaseModel):
    """
    Request schema for creating a node.
    Fields should match node_schema.py definitions.
    """
    id: str
    type: str = "company"  # e.g., "company", "person", "project", etc.
    label: str
    description: str
    sector: str | None = None
    color: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Note: position is not stored - it's generated dynamically during graph layout


class NodeUpdateRequest(BaseModel):
    """
    Request schema for updating a node.
    Fields should match node_schema.py definitions.
    """
    type: str | None = None
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


