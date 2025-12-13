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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    if 'puerta_orion_evento' not in tables_map:
        return

    evento_table = tables_map['puerta_orion_evento']
    existing_columns = {col['name'] for col in inspector.get_columns(evento_table)}

    if 'hora_inicio' not in existing_columns:
        op.add_column(evento_table, sa.Column('hora_inicio', sa.Time(), nullable=True))
    if 'hora_fin' not in existing_columns:
        op.add_column(evento_table, sa.Column('hora_fin', sa.Time(), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    if 'puerta_orion_evento' not in tables_map:
        return

    evento_table = tables_map['puerta_orion_evento']
    existing_columns = {col['name'] for col in inspector.get_columns(evento_table)}

    if 'hora_fin' in existing_columns:
        op.drop_column(evento_table, 'hora_fin')
    if 'hora_inicio' in existing_columns:
        op.drop_column(evento_table, 'hora_inicio')
