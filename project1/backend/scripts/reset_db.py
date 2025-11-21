"""
Script to reset the database by dropping all tables and re-seeding.
This will delete all existing data and create fresh sample data.
Works with both SQLite (fallback) and Supabase PostgreSQL.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the parent directory (project1/) to Python path so Python can find the 'backend' package
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.database import init_db
from backend.database.config import DATABASE_URL, SessionLocal, engine
from backend.database.models import Base
from backend.repositories import DatabaseGraphRepository
from backend.scripts.seed_db import _seed_data_from_mock


def reset_database() -> None:
    """Reset the database by dropping all tables and re-seeding."""
    print(f"Resetting database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    
    # Drop all tables
    if "sqlite" in DATABASE_URL:
        # For SQLite, delete the file
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        if db_path.exists():
            print(f"Deleting SQLite database file: {db_path}")
            db_path.unlink()
            print("Database file deleted successfully!")
        else:
            print("Database file does not exist.")
    else:
        # For PostgreSQL (Supabase), drop all tables
        print("Dropping all tables from PostgreSQL database...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully!")
    
    # Initialize database (creates new tables)
    print("\nInitializing new database...")
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create database repository
        db_repo = DatabaseGraphRepository(db)
        _seed_data_from_mock(db_repo)
        print("\nDatabase reset and seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()

