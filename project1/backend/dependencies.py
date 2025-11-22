from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db, init_db
from backend.repositories import DatabaseGraphRepository, GraphRepositoryProtocol
from backend.repositories.user_repository import UserRepository
from backend.services import GraphService, GraphServiceProtocol


def get_graph_repository(db: Session = Depends(get_db)) -> GraphRepositoryProtocol:
    """Get database repository instance."""
    return DatabaseGraphRepository(db)


def get_database_repository(db: Session = Depends(get_db)) -> DatabaseGraphRepository:
    """Get database repository instance (typed as DatabaseGraphRepository for CRUD operations)."""
    return DatabaseGraphRepository(db)


@lru_cache(maxsize=1)
def get_graph_service() -> GraphServiceProtocol:
    """Get graph service instance with mock repository (cached).
    
    Note: This is primarily for testing or development without a database.
    For production endpoints, use get_graph_service_from_db() instead.
    """
    from backend.repositories import MockGraphRepository

    return GraphService(MockGraphRepository())


def get_graph_service_from_db(db: Session = Depends(get_db)) -> GraphServiceProtocol:
    """Get graph service instance with database repository."""
    repository = DatabaseGraphRepository(db)
    return GraphService(repository)


# Optional: Authenticated versions of dependencies
# These can be used in endpoints that require authentication
def get_authenticated_graph_repository(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> DatabaseGraphRepository:
    """Get database repository instance with authentication."""
    # User information is available in the 'user' parameter
    # You can use it for row-level security or user-specific queries
    return DatabaseGraphRepository(db)


def get_authenticated_graph_service(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> GraphServiceProtocol:
    """Get graph service instance with database repository and authentication."""
    repository = DatabaseGraphRepository(db)
    return GraphService(repository)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db)


