"""Simplificar tabla personas según MER actualizado

Revision ID: 003_simplificar_personas
Revises: 002_actualizar_deportista
Create Date: 2025-09-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sys
import os

# Add migrations/helpers to path for helper imports
migrations_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
helpers_path = os.path.join(migrations_path, 'helpers')
if helpers_path not in sys.path:
    sys.path.insert(0, helpers_path)

from _helpers_table_modification import (
    drop_foreign_keys_for_columns,
    drop_columns_safe,
    drop_column_safe
)


# revision identifiers, used by Alembic.
revision = '003_simplificar_personas'
down_revision = '002_actualizar_deportista'
branch_labels = None
depends_on = None

TABLE_NAME = 'puerta_orion_personas'
COLUMNS_TO_DROP = ['id_mensualidad', 'id_ciudad', 'id_eps', 'id_institucion', 'id_tipo_sangre']


def _get_table_inspector():
    """Get SQLAlchemy inspector for database operations."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    return inspect(bind)


def _table_exists(inspector) -> bool:
    """Check if the personas table exists."""
    return TABLE_NAME in inspector.get_table_names()


def _get_existing_columns(inspector) -> set:
    """Get set of existing column names in the personas table."""
    columns = inspector.get_columns(TABLE_NAME)
    return {col['name'] for col in columns}


def _get_foreign_keys(inspector) -> list:
    """Get all foreign keys for the personas table."""
    return inspector.get_foreign_keys(TABLE_NAME)


def _alter_direccion_column(existing_columns: set) -> None:
    """Alter direccion column length if it exists."""
    if 'direccion' not in existing_columns:
        return
    
    try:
        op.alter_column(TABLE_NAME, 'direccion',
            existing_type=sa.String(length=150),
            type_=sa.String(length=50),
            existing_nullable=False)
    except Exception:
        pass  # Ignore if modification fails


def upgrade():
    """
    Simplificar la tabla personas según el MER actualizado.
    
    La tabla Persona ahora solo contiene información básica y personal.
    Los datos específicos de deportistas (EPS, ciudad, grupo sanguíneo, etc.)
    se manejan en la tabla Deportista.
    
    Cambios:
    - Eliminar FK: id_mensualidad
    - Eliminar FK: id_ciudad
    - Eliminar FK: id_eps
    - Eliminar FK: id_institucion
    - Eliminar FK: id_tipo_sangre
    - Eliminar campo: fecha_nacimiento
    - Actualizar longitud de direccion: VARCHAR(150) → VARCHAR(50)
    - Mantener: id_tipo_documento, id_sexo
    """
    inspector = _get_table_inspector()
    
    if not _table_exists(inspector):
        return
    
    existing_columns = _get_existing_columns(inspector)
    foreign_keys = _get_foreign_keys(inspector)
    columns_to_drop_set = set(COLUMNS_TO_DROP)
    
    drop_foreign_keys_for_columns(TABLE_NAME, foreign_keys, columns_to_drop_set)
    drop_columns_safe(TABLE_NAME, COLUMNS_TO_DROP, existing_columns)
    
    if 'fecha_nacimiento' in existing_columns:
        drop_column_safe(TABLE_NAME, 'fecha_nacimiento')
    
    _alter_direccion_column(existing_columns)


def downgrade():
    """
    Revertir los cambios: restaurar campos eliminados.
    """
    # Restaurar columnas
    op.add_column('puerta_orion_personas', 
        sa.Column('fecha_nacimiento', sa.Date(), nullable=True)
    )
    op.add_column('puerta_orion_personas', 
        sa.Column('id_tipo_sangre', sa.Integer(), nullable=True)
    )
    op.add_column('puerta_orion_personas', 
        sa.Column('id_institucion', sa.Integer(), nullable=True)
    )
    op.add_column('puerta_orion_personas', 
        sa.Column('id_eps', sa.Integer(), nullable=True)
    )
    op.add_column('puerta_orion_personas', 
        sa.Column('id_ciudad', sa.Integer(), nullable=True)
    )
    op.add_column('puerta_orion_personas', 
        sa.Column('id_mensualidad', sa.Integer(), nullable=True)
    )
    
    # Restaurar claves foráneas
    op.create_foreign_key(
        'puerta_orion_personas_ibfk_1',
        'puerta_orion_personas', 'puerta_orion_mensualidad',
        ['id_mensualidad'], ['id_mensualidad']
    )
    op.create_foreign_key(
        'puerta_orion_personas_ibfk_3',
        'puerta_orion_personas', 'puerta_orion_ciudad_residencia',
        ['id_ciudad'], ['id_ciudad']
    )
    op.create_foreign_key(
        'puerta_orion_personas_ibfk_5',
        'puerta_orion_personas', 'puerta_orion_eps',
        ['id_eps'], ['id_eps']
    )
    op.create_foreign_key(
        'puerta_orion_personas_ibfk_6',
        'puerta_orion_personas', 'puerta_orion_institucion_registro',
        ['id_institucion'], ['id_institucion']
    )
    op.create_foreign_key(
        'puerta_orion_personas_ibfk_7',
        'puerta_orion_personas', 'puerta_orion_grupo_sanguineo',
        ['id_tipo_sangre'], ['id_tipo_sangre']
    )
    
    # Restaurar longitud original del campo direccion
    op.alter_column('puerta_orion_personas', 'direccion',
        existing_type=sa.String(length=50),
        type_=sa.String(length=150),
        existing_nullable=False)

