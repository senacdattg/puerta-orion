"""Agregar columnas hora_inicio y hora_fin a tabla eventos

Revision ID: add_evento_horas
Revises: f607fc09752c
Create Date: 2025-10-20 16:17:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_evento_horas'
down_revision = 'f607fc09752c'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columnas hora_inicio y hora_fin a la tabla puerta_orion_evento
    op.add_column('puerta_orion_evento', sa.Column('hora_inicio', sa.Time(), nullable=True))
    op.add_column('puerta_orion_evento', sa.Column('hora_fin', sa.Time(), nullable=True))


def downgrade():
    # Eliminar las columnas agregadas
    op.drop_column('puerta_orion_evento', 'hora_fin')
    op.drop_column('puerta_orion_evento', 'hora_inicio')
