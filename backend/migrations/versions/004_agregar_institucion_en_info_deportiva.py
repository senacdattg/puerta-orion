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
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    if 'informaciondeportiva' not in tables_map:
        return

    info_table = tables_map['informaciondeportiva']
    institucion_table = tables_map.get('puerta_orion_institucion_registro')

    # Agregar columna id_institucion_registro
    with op.batch_alter_table(info_table, schema=None) as batch_op:
        existing_columns = {col['name'] for col in inspector.get_columns(info_table)}
        if 'id_institucion_registro' not in existing_columns:
            batch_op.add_column(sa.Column('id_institucion_registro', sa.Integer(), nullable=True))

    if institucion_table:
        existing_fks = {fk.get('name') for fk in inspector.get_foreign_keys(info_table)}
        if 'fk_informacion_deportiva_institucion' not in existing_fks:
            op.create_foreign_key(
                'fk_informacion_deportiva_institucion',
                info_table, institucion_table,
                ['id_institucion_registro'], ['id_institucion']
            )

    existing_indexes = {idx['name'] for idx in inspector.get_indexes(info_table)}
    if 'ix_informacion_deportiva_institucion' not in existing_indexes:
        op.create_index(
            'ix_informacion_deportiva_institucion',
            info_table,
            ['id_institucion_registro'],
            unique=False
        )


def downgrade():
    """
    Revertir los cambios: eliminar campo id_institucion_registro.
    """
    # ORDEN CORRECTO EN MYSQL: FK primero, luego índice, luego columna
    
    # 1. Eliminar clave foránea primero
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    if 'informaciondeportiva' not in tables_map:
        return

    info_table = tables_map['informaciondeportiva']

    try:
        op.drop_constraint('fk_informacion_deportiva_institucion', info_table, type_='foreignkey')
    except Exception:
        pass

    try:
        op.drop_index('ix_informacion_deportiva_institucion', table_name=info_table)
    except Exception:
        pass

    try:
        with op.batch_alter_table(info_table, schema=None) as batch_op:
            batch_op.drop_column('id_institucion_registro')
    except Exception:
        pass


