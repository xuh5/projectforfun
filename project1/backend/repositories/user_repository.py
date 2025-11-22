from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.database.models import UserModel
from backend.domain import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository implementation for User entity using SQLAlchemy database."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return None
        return self._model_to_user(model)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        model = self._db.query(UserModel).filter(UserModel.email == email).first()
        if not model:
            return None
        return self._model_to_user(model)

    def create_user(self, user: User) -> User:
        """Create a new user."""
        try:
            model = self._user_to_model(user)
            self._db.add(model)
            self._db.commit()
            self._db.refresh(model)
            return self._model_to_user(model)
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}", exc_info=True)
            self._db.rollback()
            raise

    def get_or_create_user(self, user_id: str, email: str) -> User:
        """
        Get an existing user or create a new one if it doesn't exist.
        
        This is used for first-time login to automatically create user records.
        New users are created with balance=1000.0 and role="user".
        """
        # Try to get existing user
        existing = self.get_user(user_id)
        if existing:
            return existing

        # Create new user with default values
        now = datetime.now(timezone.utc)
        new_user = User(
            id=user_id,
            email=email,
            balance=1000.0,
            role="user",
            created_at=now,
            updated_at=now,
        )
        return self.create_user(new_user)

    def _model_to_user(self, model: UserModel) -> User:
        """Convert database model to domain User."""
        return User(
            id=model.id,
            email=model.email,
            balance=model.balance,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _user_to_model(self, user: User) -> UserModel:
        """Convert domain User to database model."""
        return UserModel(
            id=user.id,
            email=user.email,
            balance=user.balance,
            role=user.role,
            created_at=user.created_at or datetime.now(timezone.utc),
            updated_at=user.updated_at or datetime.now(timezone.utc),
        )

