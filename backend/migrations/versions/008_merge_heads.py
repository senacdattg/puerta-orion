"""Merge heads: eliminar id_mensualidad y merge anterior

Revision ID: 008_merge_heads
Revises: 007_eliminar_id_mensualidad, 7c633da1ff4d
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_merge_heads'
down_revision = ('007_eliminar_id_mensualidad', '7c633da1ff4d')
branch_labels = None
depends_on = None


def upgrade():
    """
    Merge de las dos ramas de migraciones:
    - 007_eliminar_id_mensualidad: Elimina id_mensualidad de deportista
    - 7c633da1ff4d: Merge anterior de otras migraciones
    
    Esta migración no hace cambios en la base de datos, solo fusiona las ramas.
    """
    pass


def downgrade():
    """
    Revertir el merge.
    """
    pass

