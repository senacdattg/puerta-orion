"""Agregar tabla diagnostico_deportista y actualizar relaciones

Revision ID: 001_diagnostico_deportista
Revises: bf34fa9e9087
Create Date: 2025-09-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_diagnostico_deportista'
down_revision = 'bf34fa9e9087'
branch_labels = None
depends_on = None


def upgrade():
    """
    Crear la tabla diagnostico_deportista que relaciona deportistas con diagnósticos médicos.
    
    Esta tabla es diferente a diagnostico_persona, ya que está enfocada específicamente
    en los deportistas del sistema, permitiendo un seguimiento más detallado de su
    condición médica durante su carrera deportiva.
    """
    # Crear tabla diagnostico_deportista
    op.create_table('diagnostico_deportista',
        sa.Column('id_diagnostico_deportista', sa.Integer(), nullable=False),
        sa.Column('diagnostico', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('id_deportista', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['diagnostico'], ['diagnostico.id_diagnostico'], ),
        sa.ForeignKeyConstraint(['id_deportista'], ['puerta_orion_deportista.id_deportista'], ),
        sa.PrimaryKeyConstraint('id_diagnostico_deportista')
    )
    
    # Crear índices para mejorar el rendimiento de las consultas
    op.create_index(
        'ix_diagnostico_deportista_id_deportista',
        'diagnostico_deportista',
        ['id_deportista'],
        unique=False
    )
    op.create_index(
        'ix_diagnostico_deportista_diagnostico',
        'diagnostico_deportista',
        ['diagnostico'],
        unique=False
    )


def downgrade():
    """
    Revertir los cambios: eliminar tabla diagnostico_deportista.
    """
    # Eliminar índices
    op.drop_index('ix_diagnostico_deportista_diagnostico', table_name='diagnostico_deportista')
    op.drop_index('ix_diagnostico_deportista_id_deportista', table_name='diagnostico_deportista')
    
    # Eliminar tabla
    op.drop_table('diagnostico_deportista')

