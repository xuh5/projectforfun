from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database import get_db, init_db
from backend.repositories import DatabaseGraphRepository, GraphRepositoryProtocol
from backend.services import GraphService, GraphServiceProtocol


def get_graph_repository(db: Session = Depends(get_db)) -> GraphRepositoryProtocol:
    """Get database repository instance."""
    return DatabaseGraphRepository(db)


def get_database_repository(db: Session = Depends(get_db)) -> DatabaseGraphRepository:
    """Get database repository instance (typed as DatabaseGraphRepository for CRUD operations)."""
    return DatabaseGraphRepository(db)


@lru_cache(maxsize=1)
def get_graph_service() -> GraphServiceProtocol:
    """Get graph service instance (cached)."""
    # Note: This creates a service with a mock repository for initialization
    # In practice, services should be created per request with the database session
    from backend.repositories import MockGraphRepository

    return GraphService(MockGraphRepository())


def get_graph_service_from_db(db: Session = Depends(get_db)) -> GraphServiceProtocol:
    """Get graph service instance with database repository."""
    repository = DatabaseGraphRepository(db)
    return GraphService(repository)


