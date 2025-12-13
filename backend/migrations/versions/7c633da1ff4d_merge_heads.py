"""merge_heads

Revision ID: 7c633da1ff4d
Revises: 607d95db0456, force_fecha_nacimiento_date
Create Date: 2025-11-03 19:22:00.551859

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7c633da1ff4d'
down_revision = ('607d95db0456', 'force_fecha_nacimiento_date')
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
