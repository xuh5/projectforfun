from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "message" in payload


def test_nodes_endpoint_returns_graph():
    response = client.get("/api/nodes")
    assert response.status_code == 200
    payload = response.json()

    assert "nodes" in payload and isinstance(payload["nodes"], list)
    assert "edges" in payload and isinstance(payload["edges"], list)
    assert len(payload["nodes"]) > 0
    assert len(payload["edges"]) > 0

    first_node = payload["nodes"][0]
    assert "id" in first_node
    assert "data" in first_node and isinstance(first_node["data"], dict)


def test_node_detail_matches_graph_payload():
    graph = client.get("/api/nodes").json()
    node_id = graph["nodes"][0]["id"]

    response = client.get(f"/api/nodes/{node_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["id"] == node_id
    assert payload["data"]["label"]


def test_search_endpoint_filters_results():
    response = client.get("/api/search", params={"query": "Company 1"})
    assert response.status_code == 200
    payload = response.json()

    assert payload["query"] == "Company 1"
    assert isinstance(payload["results"], list)
    assert any(hit["id"] == "node-1" for hit in payload["results"])


