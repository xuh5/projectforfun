from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# ⚠️ 重要：字段定义应该与 node_schema.py 保持一致！
# 修改字段时，请同时更新 node_schema.py 和这里的定义
from backend.domain.node_schema import NODE_FIELDS

Base = declarative_base()


class NodeModel(Base):
    """
    SQLAlchemy model for Node entity.
    
    ⚠️ 字段定义来源：backend/domain/node_schema.py
    添加新字段时，请先在 node_schema.py 中定义，然后在这里添加对应的 Column。
    """

    __tablename__ = "nodes"

    # 字段定义应该与 node_schema.py 中的 NODE_FIELDS 保持一致
    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True, default="company")  # e.g., "company", "person", "project"
    label = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    sector = Column(String, nullable=True, index=True)
    color = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")

    # Relationships
    source_relationships = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.source_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    target_relationships = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.target_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        metadata = json.loads(self.metadata_json) if self.metadata_json else {}
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "description": self.description,
            "sector": self.sector,
            "color": self.color,
            "metadata": metadata,
        }


class RelationshipModel(Base):
    """SQLAlchemy model for Relationship entity."""

    __tablename__ = "relationships"

    id = Column(String, primary_key=True, index=True)
    source_id = Column(String, ForeignKey("nodes.id"), nullable=False, index=True)
    target_id = Column(String, ForeignKey("nodes.id"), nullable=False, index=True)
    type = Column(String, nullable=True, index=True, default='works_with')  # e.g., "owns", "partners_with", "competes_with"
    strength = Column(Float, nullable=True)
    created_datetime = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))

    # Relationships
    source_node = relationship("NodeModel", foreign_keys=[source_id], back_populates="source_relationships")
    target_node = relationship("NodeModel", foreign_keys=[target_id], back_populates="target_relationships")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result: Dict[str, Any] = {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "strength": self.strength,
        }
        if self.created_datetime:
            result["created_datetime"] = self.created_datetime.isoformat()
        return result

