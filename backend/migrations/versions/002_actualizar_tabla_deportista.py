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


def _add_columns_to_deportista(existing_columns: set) -> None:
    """Add missing columns to deportista table."""
    columns_to_add = [
        ('id_tipo_sanguineo', sa.Integer()),
        ('id_diagnosco_deportista', sa.Integer()),
        ('id_ciudad_recidencia', sa.Integer()),
        ('id_mensualidad', sa.Integer()),
        ('id_informacion_deportiva', sa.Integer()),
        ('id_eps', sa.Integer()),
        ('fecha_nacimiento', sa.Date())
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            op.add_column('puerta_orion_deportista', sa.Column(col_name, col_type, nullable=True))
            existing_columns.add(col_name)


def _create_foreign_keys(inspector, existing_columns: set, tables_map: dict) -> None:
    """Create foreign keys for deportista table."""
    existing_fks = {fk['name'] for fk in inspector.get_foreign_keys('puerta_orion_deportista') if fk.get('name')}
    
    fk_definitions = [
        {
            'name': 'fk_deportista_tipo_sanguineo',
            'column': 'id_tipo_sanguineo',
            'ref_table': 'puerta_orion_grupo_sanguineo',
            'ref_column': 'id_tipo_sangre'
        },
        {
            'name': 'fk_deportista_diagnostico',
            'column': 'id_diagnosco_deportista',
            'ref_table': 'diagnostico',
            'ref_column': 'id_diagnostico'
        },
        {
            'name': 'fk_deportista_ciudad',
            'column': 'id_ciudad_recidencia',
            'ref_table': 'puerta_orion_ciudad_residencia',
            'ref_column': 'id_ciudad'
        },
        {
            'name': 'fk_deportista_mensualidad',
            'column': 'id_mensualidad',
            'ref_table': 'puerta_orion_mensualidad',
            'ref_column': 'id_mensualidad'
        },
        {
            'name': 'fk_deportista_eps',
            'column': 'id_eps',
            'ref_table': 'puerta_orion_eps',
            'ref_column': 'id_eps'
        }
    ]
    
    for fk_def in fk_definitions:
        should_create = (
            fk_def['name'] not in existing_fks and
            fk_def['column'] in existing_columns and
            fk_def['ref_table'] in tables_map
        )
        if should_create:
            op.create_foreign_key(
                fk_def['name'],
                'puerta_orion_deportista',
                tables_map[fk_def['ref_table']],
                [fk_def['column']],
                [fk_def['ref_column']]
            )
    
    # Special case for informacion_deportiva
    if ('informaciondeportiva' in tables_map and
            'fk_deportista_informacion_deportiva' not in existing_fks and
            'id_informacion_deportiva' in existing_columns):
        op.create_foreign_key(
            'fk_deportista_informacion_deportiva',
            'puerta_orion_deportista',
            tables_map['informaciondeportiva'],
            ['id_informacion_deportiva'],
            ['id_informacion_deportiva']
        )


def _create_indexes(inspector, existing_columns: set) -> None:
    """Create indexes for deportista table."""
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('puerta_orion_deportista')}
    
    indexes_to_create = [
        ('ix_deportista_tipo_sanguineo', 'id_tipo_sanguineo'),
        ('ix_deportista_ciudad', 'id_ciudad_recidencia'),
        ('ix_deportista_eps', 'id_eps')
    ]
    
    for index_name, column_name in indexes_to_create:
        if index_name not in existing_indexes and column_name in existing_columns:
            op.create_index(index_name, 'puerta_orion_deportista', [column_name], unique=False)


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

    _add_columns_to_deportista(existing_columns)
    _create_foreign_keys(inspector, existing_columns, tables_map)
    _create_indexes(inspector, existing_columns)
    
    # Eliminar campo estado_deportivo si existe (no está en el MER)
    if 'estado_deportivo' in existing_columns:
        op.drop_column('puerta_orion_deportista', 'estado_deportivo')


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






