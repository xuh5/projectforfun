from __future__ import annotations

import json
from typing import Any, Dict, Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CompanyModel(Base):
    """SQLAlchemy model for Company entity."""

    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    sector = Column(String, nullable=True, index=True)
    color = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")

    # Relationships
    source_relationships = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.source_id",
        back_populates="source_company",
        cascade="all, delete-orphan",
    )
    target_relationships = relationship(
        "RelationshipModel",
        foreign_keys="RelationshipModel.target_id",
        back_populates="target_company",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        metadata = json.loads(self.metadata_json) if self.metadata_json else {}
        return {
            "id": self.id,
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
    source_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    target_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    strength = Column(Float, nullable=True)

    # Relationships
    source_company = relationship("CompanyModel", foreign_keys=[source_id], back_populates="source_relationships")
    target_company = relationship("CompanyModel", foreign_keys=[target_id], back_populates="target_relationships")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result: Dict[str, Any] = {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength,
        }
        return result

