"""Agregar columna rol_activo_id a puerta_orion_usuario

Revision ID: f2d1e3a4b5c6
Revises: b1a2c3d4e5f6
Create Date: 2025-11-09 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision = 'f2d1e3a4b5c6'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None


def _column_exists(inspector: reflection.Inspector, table_name: str, column_name: str) -> bool:
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _fk_exists(inspector: reflection.Inspector, table_name: str, constraint_name: str) -> bool:
    for fk in inspector.get_foreign_keys(table_name):
        if fk.get('name') == constraint_name:
            return True
    return False


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_name = 'puerta_orion_usuario'
    column_name = 'rol_activo_id'
    fk_name = 'fk_usuario_rol_activo'

    if not _column_exists(inspector, table_name, column_name):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.add_column(sa.Column(column_name, sa.Integer(), nullable=True))

    inspector = sa.inspect(bind)

    if not _fk_exists(inspector, table_name, fk_name):
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.create_foreign_key(
                fk_name,
                referent_table='puerta_orion_roles',
                local_cols=[column_name],
                remote_cols=['id_rol'],
                ondelete='SET NULL'
            )


def downgrade():
    table_name = 'puerta_orion_usuario'
    column_name = 'rol_activo_id'
    fk_name = 'fk_usuario_rol_activo'

    with op.batch_alter_table(table_name) as batch_op:
        batch_op.drop_constraint(fk_name, type_='foreignkey')
        batch_op.drop_column(column_name)

