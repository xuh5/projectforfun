from __future__ import annotations

from typing import Optional, Tuple

from backend.domain import Node, NodeRequest
from backend.repositories import DatabaseGraphRepository


def approve_node_request(
    node_request: NodeRequest,
    user: Optional[dict],
    repository: DatabaseGraphRepository,
) -> Tuple[str, Optional[str], Optional[Node]]:
    """
    Automatically approve or reject a node request based on business rules.
    
    Rules:
    - If user is authenticated AND node_type == 'company' → approved
    - Otherwise → rejected
    
    Returns:
        Tuple of (status, rejection_reason, created_node)
        - status: 'approved' or 'rejected'
        - rejection_reason: None if approved, reason string if rejected
        - created_node: Node instance if approved, None if rejected
    """
    # Check if node_id already exists
    existing_node = repository.get_node(node_request.node_id)
    if existing_node:
        return (
            "rejected",
            f"Node with ID '{node_request.node_id}' already exists",
            None,
        )

    # Auto-approval rule: authenticated user AND type == 'company'
    if user is not None and node_request.node_type == "company":
        # Create the actual node
        node = Node(
            id=node_request.node_id,
            type=node_request.node_type,
            label=node_request.label,
            description=node_request.description,
            sector=node_request.sector,
            color=node_request.color,
            metadata=node_request.metadata,
            position=None,  # Position calculated dynamically, not stored
        )
        created_node = repository.create_node(node)
        return ("approved", None, created_node)
    
    # Reject all other cases
    if user is None:
        reason = "User must be authenticated to create nodes"
    elif node_request.node_type != "company":
        reason = f"Only 'company' type nodes are allowed. Requested type: '{node_request.node_type}'"
    else:
        reason = "Request does not meet approval criteria"
    
    return ("rejected", reason, None)

