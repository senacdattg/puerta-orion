"""Agregar campo id_institucion_registro en InformacionDeportiva

Revision ID: 004_agregar_institucion
Revises: 003_simplificar_personas
Create Date: 2025-09-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_agregar_institucion'
down_revision = '003_simplificar_personas'
branch_labels = None
depends_on = None


def upgrade():
    """
    Agregar campo faltante id_institucion_registro en InformacionDeportiva.
    
    Según el MER, la tabla InformacionDeportiva debe tener una referencia
    a la institución de registro del deportista.
    """
    # Agregar columna id_institucion_registro
    op.add_column('InformacionDeportiva', 
        sa.Column('id_institucion_registro', sa.Integer(), nullable=True)
    )
    
    # Crear clave foránea
    op.create_foreign_key(
        'fk_informacion_deportiva_institucion',
        'InformacionDeportiva', 'puerta_orion_institucion_registro',
        ['id_institucion_registro'], ['id_institucion']
    )
    
    # Crear índice para mejorar el rendimiento
    op.create_index(
        'ix_informacion_deportiva_institucion',
        'InformacionDeportiva',
        ['id_institucion_registro'],
        unique=False
    )


def downgrade():
    """
    Revertir los cambios: eliminar campo id_institucion_registro.
    """
    # ORDEN CORRECTO EN MYSQL: FK primero, luego índice, luego columna
    
    # 1. Eliminar clave foránea primero
    try:
        op.drop_constraint('fk_informacion_deportiva_institucion', 'InformacionDeportiva', type_='foreignkey')
    except:
        pass
    
    # 2. Eliminar índice después
    try:
        op.drop_index('ix_informacion_deportiva_institucion', table_name='InformacionDeportiva')
    except:
        pass
    
    # 3. Eliminar columna al final
    try:
        op.drop_column('InformacionDeportiva', 'id_institucion_registro')
    except:
        pass


