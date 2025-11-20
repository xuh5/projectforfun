"""
Script to seed the database with initial data from the mock repository.
Run this script to populate the database with sample data.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the parent directory (project1/) to Python path so Python can find the 'backend' package
# Script is in: project1/backend/scripts/seed_db.py
# Backend package is at: project1/backend/
# We need project1/ in the path so Python can find 'backend' as a package
script_dir = Path(__file__).parent    # scripts/
backend_dir = script_dir.parent        # backend/
project_root = backend_dir.parent      # project1/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.database import init_db
from backend.database.config import SessionLocal
from backend.repositories import DatabaseGraphRepository, MockGraphRepository


def _seed_data_from_mock(db_repo: DatabaseGraphRepository) -> None:
    """Shared function to seed data from mock repository."""
    # Create mock repository to get sample data
    mock_repo = MockGraphRepository()

    # Get all nodes and relationships from mock
    nodes = list(mock_repo.list_nodes())
    relationships = list(mock_repo.list_relationships())

    print(f"Seeding {len(nodes)} nodes and {len(relationships)} relationships...")

    # Insert nodes
    for node in nodes:
        try:
            db_repo.create_node(node)
            print(f"  Created node: {node.id} - {node.label} (type: {node.type})")
        except Exception as e:
            print(f"  Skipped node {node.id}: {e}")

    # Insert relationships
    for relationship in relationships:
        try:
            db_repo.create_relationship(relationship)
            print(f"  Created relationship: {relationship.id}")
        except Exception as e:
            print(f"  Skipped relationship {relationship.id}: {e}")


def seed_database() -> None:
    """Seed the database with data from the mock repository."""
    # Initialize database
    init_db()

    # Create database session
    db = SessionLocal()

    try:
        # Create database repository
        db_repo = DatabaseGraphRepository(db)
        _seed_data_from_mock(db_repo)
        print("Database seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

