"""
Script to reset the database by deleting the database file and re-seeding.
This will delete all existing data and create fresh sample data.
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
from backend.database.config import DATABASE_URL, SessionLocal
from backend.repositories import DatabaseGraphRepository, MockGraphRepository


def reset_database() -> None:
    """Reset the database by deleting the file and re-seeding."""
    # Get database file path
    if "sqlite" in DATABASE_URL:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        
        # Delete database file if it exists
        if db_path.exists():
            print(f"Deleting database file: {db_path}")
            db_path.unlink()
            print("Database file deleted successfully!")
        else:
            print("Database file does not exist. Creating new database.")
    else:
        print(f"Warning: Non-SQLite database detected ({DATABASE_URL})")
        print("This script only works with SQLite databases.")
        print("Please manually reset your database or use database-specific commands.")
        return
    
    # Initialize database (creates new tables)
    print("\nInitializing new database...")
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create database repository
        db_repo = DatabaseGraphRepository(db)
        
        # Create mock repository to get sample data
        mock_repo = MockGraphRepository()
        
        # Get all companies and relationships from mock
        companies = list(mock_repo.list_companies())
        relationships = list(mock_repo.list_relationships())
        
        print(f"Seeding {len(companies)} companies and {len(relationships)} relationships...")
        
        # Insert companies
        for company in companies:
            try:
                db_repo.create_company(company)
                print(f"  Created company: {company.id} - {company.label}")
            except Exception as e:
                print(f"  Skipped company {company.id}: {e}")
        
        # Insert relationships
        for relationship in relationships:
            try:
                db_repo.create_relationship(relationship)
                print(f"  Created relationship: {relationship.id}")
            except Exception as e:
                print(f"  Skipped relationship {relationship.id}: {e}")
        
        print("\nDatabase reset and seeded successfully!")
        
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()

