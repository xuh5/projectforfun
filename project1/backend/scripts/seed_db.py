"""
Script to seed the database with initial data from the mock repository.
Run this script to populate the database with sample data.
"""

from __future__ import annotations

from backend.database import init_db
from backend.database.config import SessionLocal
from backend.repositories import DatabaseGraphRepository, MockGraphRepository


def seed_database() -> None:
    """Seed the database with data from the mock repository."""
    # Initialize database
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

        print("Database seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

