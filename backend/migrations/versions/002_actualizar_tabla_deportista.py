"""Actualizar tabla deportista con campos del MER

Revision ID: 002_actualizar_deportista
Revises: 001_diagnostico_deportista
Create Date: 2025-09-30 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_actualizar_deportista'
down_revision = '001_diagnostico_deportista'
branch_labels = None
depends_on = None


def upgrade():
    """
    Agregar campos faltantes a la tabla deportista según el MER.
    
    Campos a agregar:
    - id_tipo_sanguineo: FK al grupo sanguíneo del deportista
    - id_diagnosco_deportista: FK al diagnóstico principal del deportista
    - id_ciudad_recidencia: FK a la ciudad de residencia
    - id_mensualidad: FK a la mensualidad
    - id_informacion_deportiva: FK a información deportiva adicional
    - id_eps: FK a la EPS
    - fecha_nacimiento: Fecha de nacimiento (tinyint)
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {col['name'] for col in inspector.get_columns('puerta_orion_deportista')}
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    def add_column_if_missing(column: sa.Column):
        if column.name not in existing_columns:
            op.add_column('puerta_orion_deportista', column)
            existing_columns.add(column.name)

    # Agregar columnas nuevas a la tabla deportista
    add_column_if_missing(sa.Column('id_tipo_sanguineo', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('id_diagnosco_deportista', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('id_ciudad_recidencia', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('id_mensualidad', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('id_informacion_deportiva', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('id_eps', sa.Integer(), nullable=True))
    add_column_if_missing(sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
    
    # Crear claves foráneas
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('puerta_orion_deportista') if fk.get('name')}

    if 'fk_deportista_tipo_sanguineo' not in existing_fks and 'id_tipo_sanguineo' in existing_columns and 'puerta_orion_grupo_sanguineo' in tables_map:
        op.create_foreign_key(
            'fk_deportista_tipo_sanguineo',
            'puerta_orion_deportista', tables_map['puerta_orion_grupo_sanguineo'],
            ['id_tipo_sanguineo'], ['id_tipo_sangre']
        )
    if 'fk_deportista_diagnostico' not in existing_fks and 'id_diagnosco_deportista' in existing_columns and 'diagnostico' in tables_map:
        op.create_foreign_key(
            'fk_deportista_diagnostico',
            'puerta_orion_deportista', tables_map['diagnostico'],
            ['id_diagnosco_deportista'], ['id_diagnostico']
        )
    if 'fk_deportista_ciudad' not in existing_fks and 'id_ciudad_recidencia' in existing_columns and 'puerta_orion_ciudad_residencia' in tables_map:
        op.create_foreign_key(
            'fk_deportista_ciudad',
            'puerta_orion_deportista', tables_map['puerta_orion_ciudad_residencia'],
            ['id_ciudad_recidencia'], ['id_ciudad']
        )
    if 'fk_deportista_mensualidad' not in existing_fks and 'id_mensualidad' in existing_columns and 'puerta_orion_mensualidad' in tables_map:
        op.create_foreign_key(
            'fk_deportista_mensualidad',
            'puerta_orion_deportista', tables_map['puerta_orion_mensualidad'],
            ['id_mensualidad'], ['id_mensualidad']
        )
    if 'informaciondeportiva' in tables_map and 'fk_deportista_informacion_deportiva' not in existing_fks and 'id_informacion_deportiva' in existing_columns:
        ref_table = tables_map['informaciondeportiva']
        op.create_foreign_key(
            'fk_deportista_informacion_deportiva',
            'puerta_orion_deportista', ref_table,
            ['id_informacion_deportiva'], ['id_informacion_deportiva']
        )
    if 'fk_deportista_eps' not in existing_fks and 'id_eps' in existing_columns and 'puerta_orion_eps' in tables_map:
        op.create_foreign_key(
            'fk_deportista_eps',
            'puerta_orion_deportista', tables_map['puerta_orion_eps'],
            ['id_eps'], ['id_eps']
        )
    
    # Crear índices para mejorar el rendimiento
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('puerta_orion_deportista')}
    if 'ix_deportista_tipo_sanguineo' not in existing_indexes and 'id_tipo_sanguineo' in existing_columns:
        op.create_index('ix_deportista_tipo_sanguineo', 'puerta_orion_deportista', ['id_tipo_sanguineo'], unique=False)
    if 'ix_deportista_ciudad' not in existing_indexes and 'id_ciudad_recidencia' in existing_columns:
        op.create_index('ix_deportista_ciudad', 'puerta_orion_deportista', ['id_ciudad_recidencia'], unique=False)
    if 'ix_deportista_eps' not in existing_indexes and 'id_eps' in existing_columns:
        op.create_index('ix_deportista_eps', 'puerta_orion_deportista', ['id_eps'], unique=False)
    
    # Eliminar campo estado_deportivo si existe (no está en el MER)
    if 'estado_deportivo' in existing_columns:
        try:
            op.drop_column('puerta_orion_deportista', 'estado_deportivo')
        except Exception:
            pass  # Si no existe, no hace nada


def downgrade():
    """
    Revertir los cambios: eliminar campos agregados.
    """
    # Eliminar índices
    op.drop_index('ix_deportista_eps', table_name='puerta_orion_deportista')
    op.drop_index('ix_deportista_ciudad', table_name='puerta_orion_deportista')
    op.drop_index('ix_deportista_tipo_sanguineo', table_name='puerta_orion_deportista')
    
    # Eliminar claves foráneas
    op.drop_constraint('fk_deportista_eps', 'puerta_orion_deportista', type_='foreignkey')
    op.drop_constraint('fk_deportista_informacion_deportiva', 'puerta_orion_deportista', type_='foreignkey')
    op.drop_constraint('fk_deportista_mensualidad', 'puerta_orion_deportista', type_='foreignkey')
    op.drop_constraint('fk_deportista_ciudad', 'puerta_orion_deportista', type_='foreignkey')
    op.drop_constraint('fk_deportista_diagnostico', 'puerta_orion_deportista', type_='foreignkey')
    op.drop_constraint('fk_deportista_tipo_sanguineo', 'puerta_orion_deportista', type_='foreignkey')
    
    # Eliminar columnas
    op.drop_column('puerta_orion_deportista', 'fecha_nacimiento')
    op.drop_column('puerta_orion_deportista', 'id_eps')
    op.drop_column('puerta_orion_deportista', 'id_informacion_deportiva')
    op.drop_column('puerta_orion_deportista', 'id_mensualidad')
    op.drop_column('puerta_orion_deportista', 'id_ciudad_recidencia')
    op.drop_column('puerta_orion_deportista', 'id_diagnosco_deportista')
    op.drop_column('puerta_orion_deportista', 'id_tipo_sanguineo')
    
    # Restaurar campo estado_deportivo
    op.add_column('puerta_orion_deportista', 
        sa.Column('estado_deportivo', sa.Integer(), nullable=False, server_default='1')
    )






