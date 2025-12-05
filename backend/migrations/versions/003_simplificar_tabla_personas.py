"""Simplificar tabla personas según MER actualizado

Revision ID: 003_simplificar_personas
Revises: 002_actualizar_deportista
Create Date: 2025-09-30 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_simplificar_personas'
down_revision = '002_actualizar_deportista'
branch_labels = None
depends_on = None


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
    
    from sqlalchemy import inspect
    
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Verificar que la tabla existe
    if 'puerta_orion_personas' not in inspector.get_table_names():
        return
    
    # Obtener todas las columnas existentes
    existing_columns = {col['name'] for col in inspector.get_columns('puerta_orion_personas')}
    
    # Obtener todas las FKs de la tabla personas
    fks = inspector.get_foreign_keys('puerta_orion_personas')
    
    # Eliminar las FKs de las columnas que queremos eliminar
    columnas_a_eliminar = ['id_mensualidad', 'id_ciudad', 'id_eps', 'id_institucion', 'id_tipo_sangre']
    
    for fk in fks:
        # Si la FK referencia a una de las columnas que queremos eliminar
        if fk['constrained_columns'] and fk['constrained_columns'][0] in columnas_a_eliminar:
            try:
                op.drop_constraint(fk['name'], 'puerta_orion_personas', type_='foreignkey')
            except Exception:
                pass  # Ignorar si la constraint no existe
    
    # Ahora eliminar las columnas solo si existen
    for columna in columnas_a_eliminar:
        if columna in existing_columns:
            try:
                op.drop_column('puerta_orion_personas', columna)
            except Exception:
                pass  # Ignorar si la columna no existe
    
    # Eliminar fecha_nacimiento (sin FK) solo si existe
    if 'fecha_nacimiento' in existing_columns:
        try:
            op.drop_column('puerta_orion_personas', 'fecha_nacimiento')
        except Exception:
            pass  # Ignorar si la columna no existe
    
    # Actualizar longitud del campo direccion solo si existe
    if 'direccion' in existing_columns:
        try:
            op.alter_column('puerta_orion_personas', 'direccion',
                existing_type=sa.String(length=150),
                type_=sa.String(length=50),
                existing_nullable=False)
        except Exception:
            pass  # Ignorar si no se puede modificar


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

