"""Eliminar tabla diagnostico_persona - No existe en el MER

Revision ID: 005_eliminar_diagnostico_persona
Revises: 004_agregar_institucion
Create Date: 2025-09-30 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_eliminar_diagnostico_persona'
down_revision = '004_agregar_institucion'
branch_labels = None
depends_on = None


def upgrade():
    """
    Eliminar la tabla diagnostico_persona.
    
    Según el MER, solo existe diagnostico_deportista, NO diagnostico_persona.
    Esta tabla fue creada por error en migraciones anteriores.
    """
    # Verificar si la tabla existe antes de intentar eliminarla
    try:
        op.drop_table('diagnostico_persona')
    except:
        # Si la tabla no existe, no hacer nada
        pass


def downgrade():
    """
    Restaurar la tabla diagnostico_persona (solo si se necesita revertir).
    """
    op.create_table('diagnostico_persona',
        sa.Column('id_diagnostico_persona', sa.Integer(), nullable=False),
        sa.Column('diagnostico', sa.Integer(), nullable=False),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('id_persona', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['diagnostico'], ['diagnostico.id_diagnostico'], ),
        sa.ForeignKeyConstraint(['id_persona'], ['puerta_orion_personas.id_persona'], ),
        sa.PrimaryKeyConstraint('id_diagnostico_persona')
    )






