from __future__ import annotations

import json
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from backend.database.models import NodeModel, NodeRequestModel, RelationshipModel
from backend.domain import Node, NodeRequest, GraphSnapshot, Relationship
from backend.repositories.base import GraphRepositoryProtocol

# ⚠️ 重要：字段映射应该与 node_schema.py 保持一致！
# 修改字段时，请确保这里的映射与 schema 定义一致
from backend.domain.node_schema import NODE_FIELDS


class DatabaseGraphRepository(GraphRepositoryProtocol):
    """Repository implementation using SQLAlchemy database."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_graph_snapshot(self) -> GraphSnapshot:
        """Get complete graph snapshot."""
        nodes = self.list_nodes()
        relationships = self.list_relationships()
        return GraphSnapshot(nodes=nodes, relationships=relationships)

    def list_nodes(self) -> Iterable[Node]:
        """List all nodes."""
        models = self._db.query(NodeModel).all()
        return [self._model_to_node(model) for model in models]

    def list_relationships(self) -> Iterable[Relationship]:
        """List all relationships."""
        models = self._db.query(RelationshipModel).all()
        return [self._model_to_relationship(model) for model in models]

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID."""
        model = self._db.query(NodeModel).filter(NodeModel.id == node_id).first()
        if not model:
            return None
        return self._model_to_node(model)

    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get a relationship by ID."""
        model = self._db.query(RelationshipModel).filter(RelationshipModel.id == relationship_id).first()
        if not model:
            return None
        return self._model_to_relationship(model)

    def create_node(self, node: Node) -> Node:
        """Create a new node."""
        model = self._node_to_model(node)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_node(model)

    def update_node(self, node_id: str, **updates) -> Optional[Node]:
        """
        Update an existing node.
        
        ⚠️ 字段更新应该与 node_schema.py 中的 NODE_FIELDS 保持一致！
        添加新字段时，请确保在这里添加对应的更新逻辑。
        """
        model = self._db.query(NodeModel).filter(NodeModel.id == node_id).first()
        if not model:
            return None

        # 动态更新字段，基于 node_schema 定义
        for field_name, value in updates.items():
            if field_name == "metadata":
                model.metadata_json = json.dumps(value)
            elif hasattr(model, field_name):
                setattr(model, field_name, value)

        self._db.commit()
        self._db.refresh(model)
        return self._model_to_node(model)

    def delete_node(self, node_id: str) -> bool:
        """Delete a node and its relationships."""
        model = self._db.query(NodeModel).filter(NodeModel.id == node_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    def create_relationship(self, relationship: Relationship) -> Relationship:
        """Create a new relationship."""
        model = self._relationship_to_model(relationship)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_relationship(model)

    def update_relationship(self, relationship_id: str, **updates) -> Optional[Relationship]:
        """Update an existing relationship."""
        model = self._db.query(RelationshipModel).filter(RelationshipModel.id == relationship_id).first()
        if not model:
            return None

        if "source_id" in updates:
            model.source_id = updates["source_id"]
        if "target_id" in updates:
            model.target_id = updates["target_id"]
        if "type" in updates:
            model.type = updates["type"]
        if "strength" in updates:
            model.strength = updates["strength"]
        if "created_datetime" in updates:
            model.created_datetime = updates["created_datetime"]

        self._db.commit()
        self._db.refresh(model)
        return self._model_to_relationship(model)

    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        model = self._db.query(RelationshipModel).filter(RelationshipModel.id == relationship_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    def _model_to_node(self, model: NodeModel) -> Node:
        """
        Convert database model to domain Node.
        
        ⚠️ 字段映射应该与 node_schema.py 中的 NODE_FIELDS 保持一致！
        添加新字段时，请确保在这里添加对应的映射。
        """
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}
        # Position is not stored in database - it's generated dynamically during graph layout
        
        # 动态构建字段字典，基于 node_schema 定义
        node_data = {
            "id": model.id,
            "metadata": metadata,
            "position": None,  # Position is calculated dynamically, not stored
        }
        
        # 从 schema 中获取所有字段并映射
        for field_def in NODE_FIELDS:
            if field_def.name != "id":  # id 已经处理
                value = getattr(model, field_def.name, None)
                if field_def.name == "type" and value is None:
                    value = "company"  # Default for backward compatibility
                node_data[field_def.name] = value
        
        return Node(**node_data)

    def _node_to_model(self, node: Node) -> NodeModel:
        """
        Convert domain Node to database model.
        
        ⚠️ 字段映射应该与 node_schema.py 中的 NODE_FIELDS 保持一致！
        添加新字段时，请确保在这里添加对应的映射。
        """
        # Position is not stored - it's generated dynamically during graph layout
        
        # 动态构建模型字段，基于 node_schema 定义
        model_data = {
            "id": node.id,
            "metadata_json": json.dumps(node.metadata),
        }
        
        # 从 schema 中获取所有字段并映射（排除 id 和 metadata）
        for field_def in NODE_FIELDS:
            if field_def.name != "id":  # id 已经处理
                value = getattr(node, field_def.name, None)
                model_data[field_def.name] = value
        
        return NodeModel(**model_data)

    def _model_to_relationship(self, model: RelationshipModel) -> Relationship:
        """Convert database model to domain Relationship."""
        # Handle backward compatibility: if type is missing (old data), default to 'works_with'
        relationship_type = getattr(model, 'type', None) or 'works_with'
        return Relationship(
            id=model.id,
            source_id=model.source_id,
            target_id=model.target_id,
            type=relationship_type,
            strength=model.strength,
            created_datetime=getattr(model, 'created_datetime', None),
        )

    def _relationship_to_model(self, relationship: Relationship) -> RelationshipModel:
        """Convert domain Relationship to database model."""
        return RelationshipModel(
            id=relationship.id,
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            type=relationship.type,
            strength=relationship.strength,
            created_datetime=relationship.created_datetime,
        )

    # NodeRequest CRUD methods
    def create_node_request(self, node_request: NodeRequest) -> NodeRequest:
        """Create a new node request."""
        model = self._node_request_to_model(node_request)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_node_request(model)

    def get_node_request(self, request_id: int) -> Optional[NodeRequest]:
        """Get a node request by ID."""
        model = self._db.query(NodeRequestModel).filter(NodeRequestModel.id == request_id).first()
        if not model:
            return None
        return self._model_to_node_request(model)

    def update_node_request_status(
        self,
        request_id: int,
        status: str,
        approver_id: Optional[str] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[NodeRequest]:
        """Update node request status."""
        model = self._db.query(NodeRequestModel).filter(NodeRequestModel.id == request_id).first()
        if not model:
            return None

        model.status = status
        if approver_id:
            model.approver_id = approver_id
        if rejection_reason:
            model.rejection_reason = rejection_reason
        if status == "approved":
            from datetime import datetime, timezone
            model.approved_at = datetime.now(timezone.utc)

        self._db.commit()
        self._db.refresh(model)
        return self._model_to_node_request(model)

    def _model_to_node_request(self, model: NodeRequestModel) -> NodeRequest:
        """Convert database model to domain NodeRequest."""
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}
        return NodeRequest(
            id=model.id,
            requestor_id=model.requestor_id,
            status=model.status,  # type: ignore
            node_id=model.node_id,
            node_type=model.node_type,
            label=model.label,
            description=model.description,
            sector=model.sector,
            color=model.color,
            metadata=metadata,
            approver_id=model.approver_id,
            approved_at=model.approved_at,
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _node_request_to_model(self, node_request: NodeRequest) -> NodeRequestModel:
        """Convert domain NodeRequest to database model."""
        return NodeRequestModel(
            id=node_request.id if node_request.id > 0 else None,  # Let DB auto-generate if 0
            requestor_id=node_request.requestor_id,
            status=node_request.status,
            node_id=node_request.node_id,
            node_type=node_request.node_type,
            label=node_request.label,
            description=node_request.description,
            sector=node_request.sector,
            color=node_request.color,
            metadata_json=json.dumps(node_request.metadata),
            approver_id=node_request.approver_id,
            approved_at=node_request.approved_at,
            rejection_reason=node_request.rejection_reason,
            created_at=node_request.created_at,
            updated_at=node_request.updated_at,
        )

