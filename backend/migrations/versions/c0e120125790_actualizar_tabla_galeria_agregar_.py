"""actualizar_tabla_galeria_agregar_foreign_keys

Revision ID: c0e120125790
Revises: a3493d8526e9
Create Date: 2025-10-28 17:36:59.188746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0e120125790'
down_revision = 'a3493d8526e9'
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar columna activo
    op.drop_column('puerta_orion_galeria', 'activo')
    
    # Agregar foreign keys
    op.add_column('puerta_orion_galeria', sa.Column('id_tipo_evento', sa.Integer(), nullable=True))
    op.add_column('puerta_orion_galeria', sa.Column('id_categoria', sa.Integer(), nullable=True))
    
    # Crear foreign key constraints
    op.create_foreign_key('fk_galeria_tipo_evento', 'puerta_orion_galeria', 'puerta_orion_tipo_evento', ['id_tipo_evento'], ['id_tipo_evento'])
    op.create_foreign_key('fk_galeria_categoria', 'puerta_orion_galeria', 'puerta_orion_categoria', ['id_categoria'], ['id_categoria'])


def downgrade():
    # Eliminar foreign key constraints
    op.drop_constraint('fk_galeria_categoria', 'puerta_orion_galeria', type_='foreignkey')
    op.drop_constraint('fk_galeria_tipo_evento', 'puerta_orion_galeria', type_='foreignkey')
    
    # Eliminar columnas foreign key
    op.drop_column('puerta_orion_galeria', 'id_categoria')
    op.drop_column('puerta_orion_galeria', 'id_tipo_evento')
    
    # Restaurar columna activo
    op.add_column('puerta_orion_galeria', sa.Column('activo', sa.Boolean(), nullable=False, default=True))
