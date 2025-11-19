"""Merge heads 008 y f2d1

Revision ID: 2066cb478250
Revises: 008_merge_heads, f2d1e3a4b5c6
Create Date: 2025-11-09 17:46:45.496017

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '2066cb478250'
down_revision = ('008_merge_heads', 'f2d1e3a4b5c6')
branch_labels = None
depends_on = None


def upgrade():
    # Empty migration: This is a merge migration that combines two migration branches.
    # No actual schema changes are needed, only the revision chain is updated.
    pass


def downgrade():
    # Empty migration: This is a merge migration that combines two migration branches.
    # No actual schema changes are needed, only the revision chain is updated.
    pass
