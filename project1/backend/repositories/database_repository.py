from __future__ import annotations

import json
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from backend.database.models import CompanyModel, RelationshipModel
from backend.domain import Company, GraphSnapshot, Relationship
from backend.repositories.base import GraphRepositoryProtocol


class DatabaseGraphRepository(GraphRepositoryProtocol):
    """Repository implementation using SQLAlchemy database."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_graph_snapshot(self) -> GraphSnapshot:
        """Get complete graph snapshot."""
        companies = self.list_companies()
        relationships = self.list_relationships()
        return GraphSnapshot(companies=companies, relationships=relationships)

    def list_companies(self) -> Iterable[Company]:
        """List all companies."""
        models = self._db.query(CompanyModel).all()
        return [self._model_to_company(model) for model in models]

    def list_relationships(self) -> Iterable[Relationship]:
        """List all relationships."""
        models = self._db.query(RelationshipModel).all()
        return [self._model_to_relationship(model) for model in models]

    def get_company(self, company_id: str) -> Optional[Company]:
        """Get a company by ID."""
        model = self._db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        if not model:
            return None
        return self._model_to_company(model)

    def create_company(self, company: Company) -> Company:
        """Create a new company."""
        model = self._company_to_model(company)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_company(model)

    def update_company(self, company_id: str, **updates) -> Optional[Company]:
        """Update an existing company."""
        model = self._db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
        if not model:
            return None

        if "label" in updates:
            model.label = updates["label"]
        if "description" in updates:
            model.description = updates["description"]
        if "sector" in updates:
            model.sector = updates["sector"]
        if "color" in updates:
            model.color = updates["color"]
        if "metadata" in updates:
            model.metadata_json = json.dumps(updates["metadata"])

        self._db.commit()
        self._db.refresh(model)
        return self._model_to_company(model)

    def delete_company(self, company_id: str) -> bool:
        """Delete a company and its relationships."""
        model = self._db.query(CompanyModel).filter(CompanyModel.id == company_id).first()
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
        if "strength" in updates:
            model.strength = updates["strength"]

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

    def _model_to_company(self, model: CompanyModel) -> Company:
        """Convert database model to domain Company."""
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}
        # Position is not stored in database - it's generated dynamically during graph layout
        return Company(
            id=model.id,
            label=model.label,
            description=model.description,
            sector=model.sector,
            color=model.color,
            metadata=metadata,
            position=None,  # Position is calculated dynamically, not stored
        )

    def _company_to_model(self, company: Company) -> CompanyModel:
        """Convert domain Company to database model."""
        # Position is not stored - it's generated dynamically during graph layout
        return CompanyModel(
            id=company.id,
            label=company.label,
            description=company.description,
            sector=company.sector,
            color=company.color,
            metadata_json=json.dumps(company.metadata),
        )

    def _model_to_relationship(self, model: RelationshipModel) -> Relationship:
        """Convert database model to domain Relationship."""
        return Relationship(
            id=model.id,
            source_id=model.source_id,
            target_id=model.target_id,
            strength=model.strength,
        )

    def _relationship_to_model(self, relationship: Relationship) -> RelationshipModel:
        """Convert domain Relationship to database model."""
        return RelationshipModel(
            id=relationship.id,
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            strength=relationship.strength,
        )

