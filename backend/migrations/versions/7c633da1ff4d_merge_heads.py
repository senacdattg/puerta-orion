"""merge_heads

Revision ID: 7c633da1ff4d
Revises: 607d95db0456, force_fecha_nacimiento_date
Create Date: 2025-11-03 19:22:00.551859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c633da1ff4d'
down_revision = ('607d95db0456', 'force_fecha_nacimiento_date')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
