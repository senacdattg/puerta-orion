"""Fusionar heads de migraciones

Revision ID: 9750ad435abf
Revises: b1a2c3d4e5f6, d89d5de320fd
Create Date: 2025-10-29 22:27:11.241309

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9750ad435abf'
down_revision = ('b1a2c3d4e5f6', 'd89d5de320fd')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
