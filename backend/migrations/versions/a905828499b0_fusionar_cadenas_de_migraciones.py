"""Fusionar cadenas de migraciones

Revision ID: a905828499b0
Revises: a30aaee567e3
Create Date: 2025-10-15 16:12:49.080185

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a905828499b0'
down_revision = 'a30aaee567e3'
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
