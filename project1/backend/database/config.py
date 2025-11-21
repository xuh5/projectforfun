from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Database URL - defaults to SQLite in project directory
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent / 'data' / 'graph.db'}",
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from backend.database.models import Base

    # Create data directory if it doesn't exist
    if "sqlite" in DATABASE_URL:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Migrate existing tables if needed (for SQLite)
    if "sqlite" in DATABASE_URL:
        _migrate_sqlite_schema()


def _migrate_sqlite_schema() -> None:
    """Add missing columns to existing SQLite tables for backward compatibility."""
    from sqlalchemy import inspect, text
    
    inspector = inspect(engine)
    
    # Define migrations for each table
    # Format: (table_name, [(column_name, sql_type, default_update_sql, ...), ...])
    migrations = {
        "relationships": [
            # (column_name, sql_type, optional_default_update_sql)
            ("type", "VARCHAR", "UPDATE relationships SET type = 'works_with' WHERE type IS NULL"),
            ("created_datetime", "DATETIME", None),
            # Add new fields here! Example:
            # ("decay", "FLOAT", None),
            # ("weight", "FLOAT", None),
        ],
    }
    
    for table_name, columns in migrations.items():
        if table_name not in inspector.get_table_names():
            continue
        
        # Get existing columns
        existing_columns = [col["name"] for col in inspector.get_columns(table_name)]
        
        with engine.connect() as conn:
            for column_name, sql_type, default_update_sql in columns:
                if column_name not in existing_columns:
                    try:
                        # Add the column
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}"))
                        
                        # Update existing rows with default value if provided
                        if default_update_sql:
                            conn.execute(text(default_update_sql))
                        
                        conn.commit()
                    except Exception as e:
                        # Column might already exist or other error - ignore
                        conn.rollback()
                        pass

