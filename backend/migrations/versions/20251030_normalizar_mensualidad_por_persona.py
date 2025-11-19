"""Normalizar mensualidad por persona (robusta)

Revision ID: b1a2c3d4e5f6
Revises: ce296712a0ca
Create Date: 2025-10-30 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = 'ce296712a0ca'
branch_labels = None
depends_on = None


def _column_exists(bind, table_name, column_name):
    inspector = Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _fk_exists(bind, table_name, constraint_name=None, column_name=None):
    inspector = Inspector.from_engine(bind)
    for fk in inspector.get_foreign_keys(table_name):
        if constraint_name and fk.get('name') == constraint_name:
            return True
        if column_name and column_name in fk.get('constrained_columns', []):
            return True
    return False


def upgrade():
    bind = op.get_bind()
    table_name = 'puerta_orion_mensualidad'

    # 1) Agregar columna id_persona (si no existe). Nullable inicialmente para no romper datos
    if not _column_exists(bind, table_name, 'id_persona'):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.add_column(sa.Column('id_persona', sa.Integer(), nullable=True))

    # 2) Crear FK a puerta_orion_personas.id_persona si no existe
    if not _fk_exists(bind, table_name, constraint_name='fk_mensualidad_persona', column_name='id_persona'):
        op.create_foreign_key(
            constraint_name='fk_mensualidad_persona',
            source_table=table_name,
            referent_table='puerta_orion_personas',
            local_cols=['id_persona'],
            remote_cols=['id_persona'],
            ondelete='RESTRICT'
        )

    # 3) Ajustar estado default False (0 en MySQL) y not null; fecha_pago nullable True
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column('estado',
                              existing_type=sa.Boolean(),
                              nullable=False,
                              server_default=sa.text('0'))
        batch_op.alter_column('fecha_pago',
                              existing_type=sa.Date(),
                              nullable=True)

    # 4) Eliminar FK y columna id_categoria si existen
    # Detectar FK por columna
    if _column_exists(bind, table_name, 'id_categoria'):
        # Intentar dropear FKs que referencian id_categoria
        inspector = Inspector.from_engine(bind)
        for fk in inspector.get_foreign_keys(table_name):
            if 'id_categoria' in fk.get('constrained_columns', []):
                op.drop_constraint(fk.get('name'), table_name, type_='foreignkey')
        # Dropear columna
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column('id_categoria')

    # Nota: Mantener id_persona como nullable por ahora. Se puede hacer otra migración para NOT NULL tras backfill.


def downgrade():
    bind = op.get_bind()
    table_name = 'puerta_orion_mensualidad'

    # 1) Restaurar columna id_categoria (nullable)
    if not _column_exists(bind, table_name, 'id_categoria'):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.add_column(sa.Column('id_categoria', sa.Integer(), nullable=True))

    # 2) Restaurar FK de categoría si no existe
    if not _fk_exists(bind, table_name, constraint_name='fk_mensualidad_categoria', column_name='id_categoria'):
        op.create_foreign_key(
            constraint_name='fk_mensualidad_categoria',
            source_table=table_name,
            referent_table='puerta_orion_categoria',
            local_cols=['id_categoria'],
            remote_cols=['id_categoria'],
            ondelete='RESTRICT'
        )

    # 3) Revertir cambios en estado y fecha_pago
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column('estado',
                              existing_type=sa.Boolean(),
                              nullable=False,
                              server_default=sa.text('1'))
        batch_op.alter_column('fecha_pago',
                              existing_type=sa.Date(),
                              nullable=False)

    # 4) Eliminar FK y columna id_persona
    op.drop_constraint('fk_mensualidad_persona', table_name, type_='foreignkey')

    if _column_exists(bind, table_name, 'id_persona'):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_column('id_persona')
