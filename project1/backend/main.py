from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import math

app = FastAPI(title="Project For Fun API")

# CORS middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    status: str
    message: str


class NodeData(BaseModel):
    id: str
    label: str
    description: str = ""
    x: float = 0
    y: float = 0
    color: str = "#667eea"
    data: Dict[str, Any] = {}


class EdgeData(BaseModel):
    id: str
    source: str
    target: str


class GraphResponse(BaseModel):
    nodes: List[NodeData]
    edges: List[EdgeData]


# Sample data storage (in production, this would be a database)
sample_nodes = []
sample_edges = []


def generate_sample_graph():
    """Generate a sample graph with nodes in a circular pattern"""
    nodes = []
    edges = []
    node_count = 12
    radius = 300
    center_x = 400
    center_y = 300
    colors = ["#667eea", "#764ba2", "#f093fb"]

    for i in range(node_count):
        angle = (2 * math.pi * i) / node_count
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        nodes.append(NodeData(
            id=f"node-{i}",
            label=f"Node {i + 1}",
            description=f"This is node number {i + 1} in the graph network. It represents an important data point in the system.",
            x=x,
            y=y,
            color=colors[i % 3],
            data={
                "value": (i + 1) * 10,
                "category": ["A", "B", "C"][i % 3],
                "connections": 2 if i == 0 or i == node_count - 1 else 2,
            }
        ))

        # Create edges connecting to next node
        if i < node_count - 1:
            edges.append(EdgeData(
                id=f"edge-{i}-{i + 1}",
                source=f"node-{i}",
                target=f"node-{i + 1}"
            ))

    # Connect last node to first
    edges.append(EdgeData(
        id=f"edge-{node_count - 1}-0",
        source=f"node-{node_count - 1}",
        target="node-0"
    ))

    return nodes, edges


# Initialize sample data
sample_nodes, sample_edges = generate_sample_graph()


@app.get("/")
async def root():
    return {"message": "Welcome to Project For Fun API"}


@app.get("/api/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", message="Backend is running")


@app.get("/api/nodes", response_model=GraphResponse)
async def get_nodes():
    """Get all nodes and edges for the graph"""
    return GraphResponse(nodes=sample_nodes, edges=sample_edges)


@app.get("/api/nodes/{node_id}")
async def get_node(node_id: str):
    """Get detailed information about a specific node"""
    node = next((n for n in sample_nodes if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        "id": node.id,
        "data": {
            "label": node.label,
            "description": node.description,
            **node.data
        }
    }


@app.get("/api/hello")
async def hello():
    return {"message": "Hello from Python backend!"}

