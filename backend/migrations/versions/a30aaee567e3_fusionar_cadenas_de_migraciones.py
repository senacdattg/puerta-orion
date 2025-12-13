"""Fusionar cadenas de migraciones

Revision ID: a30aaee567e3
Revises: 172b75592622, 32930ce69edb
Create Date: 2025-10-15 16:11:39.471370

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a30aaee567e3'
down_revision = '172b75592622'
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
