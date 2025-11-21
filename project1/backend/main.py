from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.schemas import (
    NodeCreateRequest,
    NodeDetailResponse,
    NodeUpdateRequest,
    GraphResponse,
    HealthCheckResponse,
    MessageResponse,
    RelationshipCreateRequest,
    RelationshipUpdateRequest,
    SearchHit,
    SearchResponse,
)
from backend.database import init_db
from backend.dependencies import (
    get_database_repository,
    get_graph_repository,
    get_graph_service_from_db,
    # Optional: Import authenticated dependencies when needed
    # get_authenticated_graph_repository,
    # get_authenticated_graph_service,
)
from backend.domain import Node, Relationship
from backend.repositories import DatabaseGraphRepository, GraphRepositoryProtocol
from backend.services import GraphServiceProtocol
# Optional: Import auth dependency when protecting endpoints
# from backend.auth import get_current_user

app = FastAPI(title="Project For Fun API")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"],  # Include Authorization header for JWT tokens
)


@app.get("/")
async def root():
    return {"message": "Welcome to Project For Fun API"}


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(status="ok", message="Backend is running")


@app.get("/api/nodes", response_model=GraphResponse)
async def get_nodes(service: GraphServiceProtocol = Depends(get_graph_service_from_db)):
    """Get all nodes and edges for the graph."""
    snapshot = service.get_graph_snapshot()
    return GraphResponse(nodes=snapshot.to_node_payload(), edges=snapshot.to_edge_payload())


@app.get("/api/nodes/{node_id}", response_model=NodeDetailResponse)
async def get_node(node_id: str, service: GraphServiceProtocol = Depends(get_graph_service_from_db)):
    """Get detailed information about a specific node."""
    detail = service.get_node_detail(node_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Node not found")

    return NodeDetailResponse(id=detail.id, data=dict(detail.data))


@app.get("/api/search", response_model=SearchResponse)
async def search_nodes(
    query: str = Query("", min_length=1, description="Search term matching node label/description"),
    limit: int = Query(5, ge=1, le=20),
    service: GraphServiceProtocol = Depends(get_graph_service_from_db),
):
    """Search for nodes matching a query string."""
    matches = service.search_nodes(query, limit=limit)
    hits = [
        SearchHit(
            id=node.id,
            label=node.label,
            type=node.type,
            sector=node.sector,
            score=node.metadata.get("score") if isinstance(node.metadata, dict) else None,
        )
        for node in matches
    ]
    return SearchResponse(query=query, results=hits)


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from Python backend!"}


# CRUD endpoints for Nodes
@app.post("/api/nodes", response_model=NodeDetailResponse, status_code=201)
async def create_node(
    node_data: NodeCreateRequest,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Create a new node."""
    # Position is not stored - it's generated dynamically during graph layout
    node = Node(
        id=node_data.id,
        type=node_data.type,
        label=node_data.label,
        description=node_data.description,
        sector=node_data.sector,
        color=node_data.color,
        metadata=node_data.metadata,
        position=None,  # Position calculated dynamically, not stored
    )

    created = repository.create_node(node)
    return NodeDetailResponse(id=created.id, data=dict(created.to_detail().data))


@app.put("/api/nodes/{node_id}", response_model=NodeDetailResponse)
async def update_node(
    node_id: str,
    node_data: NodeUpdateRequest,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Update an existing node."""
    updates: dict = {}
    if node_data.type is not None:
        updates["type"] = node_data.type
    if node_data.label is not None:
        updates["label"] = node_data.label
    if node_data.description is not None:
        updates["description"] = node_data.description
    if node_data.sector is not None:
        updates["sector"] = node_data.sector
    if node_data.color is not None:
        updates["color"] = node_data.color
    if node_data.metadata is not None:
        updates["metadata"] = node_data.metadata
    # Position is not stored - it's generated dynamically during graph layout

    updated = repository.update_node(node_id, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Node not found")

    return NodeDetailResponse(id=updated.id, data=dict(updated.to_detail().data))


@app.delete("/api/nodes/{node_id}", response_model=MessageResponse)
async def delete_node(
    node_id: str,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Delete a node."""
    deleted = repository.delete_node(node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Node not found")

    return MessageResponse(message=f"Node {node_id} deleted successfully")


# CRUD endpoints for Relationships
@app.post("/api/relationships", response_model=dict, status_code=201)
async def create_relationship(
    relationship_data: RelationshipCreateRequest,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Create a new relationship. ID is auto-generated based on source_id, target_id, and type."""
    from datetime import datetime, timezone
    
    # Generate unique ID based on properties: source_id + target_id + type
    # Format: {source_id}_{target_id}_{type}
    relationship_id = f"{relationship_data.source_id}_{relationship_data.target_id}_{relationship_data.type}"
    
    # Check if relationship already exists
    existing = repository.get_relationship(relationship_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Relationship already exists with ID: {relationship_id}")
    
    # Verify source and target nodes exist
    source_node = repository.get_node(relationship_data.source_id)
    if not source_node:
        raise HTTPException(status_code=404, detail=f"Source node not found: {relationship_data.source_id}")
    
    target_node = repository.get_node(relationship_data.target_id)
    if not target_node:
        raise HTTPException(status_code=404, detail=f"Target node not found: {relationship_data.target_id}")
    
    relationship = Relationship(
        id=relationship_id,
        source_id=relationship_data.source_id,
        target_id=relationship_data.target_id,
        type=relationship_data.type,
        strength=relationship_data.strength,
        created_datetime=datetime.now(timezone.utc),
    )

    created = repository.create_relationship(relationship)
    result = {
        "id": created.id,
        "source_id": created.source_id,
        "target_id": created.target_id,
        "type": created.type,
        "strength": created.strength,
    }
    if created.created_datetime:
        result["created_datetime"] = created.created_datetime.isoformat()
    return result


@app.put("/api/relationships/{relationship_id}", response_model=dict)
async def update_relationship(
    relationship_id: str,
    relationship_data: RelationshipUpdateRequest,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Update an existing relationship."""
    updates: dict = {}
    if relationship_data.source_id is not None:
        updates["source_id"] = relationship_data.source_id
    if relationship_data.target_id is not None:
        updates["target_id"] = relationship_data.target_id
    if relationship_data.type is not None:
        updates["type"] = relationship_data.type
    if relationship_data.strength is not None:
        updates["strength"] = relationship_data.strength
    if relationship_data.created_datetime is not None:
        from datetime import datetime
        updates["created_datetime"] = datetime.fromisoformat(relationship_data.created_datetime.replace('Z', '+00:00'))

    updated = repository.update_relationship(relationship_id, **updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Relationship not found")

    result = {
        "id": updated.id,
        "source_id": updated.source_id,
        "target_id": updated.target_id,
        "type": updated.type,
        "strength": updated.strength,
    }
    if updated.created_datetime:
        result["created_datetime"] = updated.created_datetime.isoformat()
    return result


@app.delete("/api/relationships/{relationship_id}", response_model=MessageResponse)
async def delete_relationship(
    relationship_id: str,
    repository: DatabaseGraphRepository = Depends(get_database_repository),
):
    """Delete a relationship."""
    deleted = repository.delete_relationship(relationship_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return MessageResponse(message=f"Relationship {relationship_id} deleted successfully")

