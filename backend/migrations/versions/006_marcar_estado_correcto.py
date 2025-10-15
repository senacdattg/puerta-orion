"""Marcar estado correcto de migraciones

Revision ID: 006_marcar_estado_correcto
Revises: 005_eliminar_diagnostico_persona
Create Date: 2025-10-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_marcar_estado_correcto'
down_revision = '005_eliminar_diagnostico_persona'
branch_labels = None
depends_on = None


def upgrade():
    """
    Esta migración solo marca el estado correcto sin hacer cambios en la base de datos.
    Los cambios en las relaciones se manejan a nivel de modelo SQLAlchemy.
    """
    pass


def downgrade():
    """
    Revertir el estado.
    """
    pass
