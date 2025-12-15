"""add_metadata_to_relationships

Revision ID: c3f8a9d2e1b4
Revises: 8a9518267406
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f8a9d2e1b4'
down_revision: Union[str, None] = '8a9518267406'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add metadata_json column to relationships table
    op.add_column('relationships', sa.Column('metadata_json', sa.Text(), nullable=False, server_default='{}'))


def downgrade() -> None:
    # Remove metadata_json column from relationships table
    op.drop_column('relationships', 'metadata_json')

