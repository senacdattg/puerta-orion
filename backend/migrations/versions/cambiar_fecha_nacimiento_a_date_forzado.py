"""Forzar cambio de fecha_nacimiento a Date

Revision ID: force_fecha_nacimiento_date
Revises: fb54dee06167
Create Date: 2025-11-02 16:00:00.000000

Esta migración fuerza el cambio de fecha_nacimiento de SMALLINT a DATE
incluso si otras migraciones ya intentaron hacerlo.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'force_fecha_nacimiento_date'
down_revision = 'fb54dee06167'  # Después de add_password_reset
branch_labels = None
depends_on = None


def upgrade():
    """
    Forzar el cambio de fecha_nacimiento de SMALLINT a DATE.
    Esta migración se ejecuta después de todas las demás para asegurar el cambio.
    """
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Verificar si la tabla existe
    if 'puerta_orion_deportista' not in inspector.get_table_names():
        return
    
    existing_columns = [col['name'] for col in inspector.get_columns('puerta_orion_deportista')]
    
    if 'fecha_nacimiento' not in existing_columns:
        op.add_column('puerta_orion_deportista', 
                     sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
        return
    
    # Verificar el tipo actual de la columna
    fecha_col = [col for col in inspector.get_columns('puerta_orion_deportista') 
                 if col['name'] == 'fecha_nacimiento'][0]
    
    col_type_str = str(fecha_col['type']).upper()
    
    # Si ya es DATE, no hacer nada
    if 'DATE' in col_type_str:
        return
    
    # Verificar si existe columna temporal de intentos anteriores
    temp_cols = [col['name'] for col in inspector.get_columns('puerta_orion_deportista')]
    if 'fecha_nacimiento_temp' in temp_cols:
        op.drop_column('puerta_orion_deportista', 'fecha_nacimiento_temp')
    
    # Método seguro: columna temporal
    op.add_column('puerta_orion_deportista',
                 sa.Column('fecha_nacimiento_temp', sa.Date(), nullable=True))
    
    # Convertir años a fechas 01-01-YYYY
    op.execute("""
        UPDATE puerta_orion_deportista 
        SET fecha_nacimiento_temp = STR_TO_DATE(CONCAT(CAST(fecha_nacimiento AS UNSIGNED), '-01-01'), '%Y-%m-%d')
        WHERE fecha_nacimiento IS NOT NULL
        AND fecha_nacimiento BETWEEN 1900 AND 2100
    """)
    
    # Eliminar columna antigua
    op.drop_column('puerta_orion_deportista', 'fecha_nacimiento')
    
    # Renombrar columna temporal
    op.execute("""
        ALTER TABLE puerta_orion_deportista 
        CHANGE COLUMN fecha_nacimiento_temp fecha_nacimiento DATE NULL
    """)


def downgrade():
    """
    Revertir: volver de Date a SmallInteger (solo año).
    """
    # Crear columna temporal SMALLINT
    op.add_column('puerta_orion_deportista',
                 sa.Column('fecha_nacimiento_temp', sa.SmallInteger(), nullable=True))
    
    # Extraer años de fechas
    op.execute("""
        UPDATE puerta_orion_deportista 
        SET fecha_nacimiento_temp = YEAR(fecha_nacimiento)
        WHERE fecha_nacimiento IS NOT NULL
    """)
    
    # Eliminar columna DATE
    op.drop_column('puerta_orion_deportista', 'fecha_nacimiento')
    
    # Renombrar temporal
    op.execute("""
        ALTER TABLE puerta_orion_deportista 
        CHANGE COLUMN fecha_nacimiento_temp fecha_nacimiento SMALLINT NULL
    """)

