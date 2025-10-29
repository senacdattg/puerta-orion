"""eliminar_id_sesion_de_tabla_calendario

Revision ID: d5d9653abbda
Revises: c0e120125790
Create Date: 2025-10-28 17:46:21.510096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5d9653abbda'
down_revision = 'c0e120125790'
branch_labels = None
depends_on = None


def upgrade():
    # Primero eliminar la foreign key constraint
    op.drop_constraint('puerta_orion_calendario_ibfk_2', 'puerta_orion_calendario', type_='foreignkey')
    
    # Luego eliminar la columna id_sesion
    op.drop_column('puerta_orion_calendario', 'id_sesion')


def downgrade():
    # Restaurar columna id_sesion
    op.add_column('puerta_orion_calendario', sa.Column('id_sesion', sa.Integer(), nullable=False))
    
    # Restaurar foreign key constraint
    op.create_foreign_key('puerta_orion_calendario_ibfk_2', 'puerta_orion_calendario', 'puerta_orion_sesiones', ['id_sesion'], ['id_sesion'])
