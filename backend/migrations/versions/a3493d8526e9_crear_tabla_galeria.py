"""crear_tabla_galeria

Revision ID: a3493d8526e9
Revises: 5567620a36ee
Create Date: 2025-10-28 17:26:33.433455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3493d8526e9'
down_revision = '5567620a36ee'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla puerta_orion_galeria
    op.create_table('puerta_orion_galeria',
        sa.Column('id_galeria', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=250), nullable=False),
        sa.Column('url_imagen', sa.String(length=500), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fecha_subida', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_galeria')
    )


def downgrade():
    # Eliminar tabla puerta_orion_galeria
    op.drop_table('puerta_orion_galeria')
