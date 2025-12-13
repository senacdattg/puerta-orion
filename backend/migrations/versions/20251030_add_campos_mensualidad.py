"""Agregar campos a mensualidad: saldo_pendiente, fecha_vencimiento, activo

Revision ID: a1b2c3d4e6f7
Revises: f6e5d4c3b2a1
Create Date: 2025-10-30 00:20:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e6f7'
down_revision = 'f6e5d4c3b2a1'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    table = 'puerta_orion_mensualidad'
    inspector = Inspector.from_engine(bind)
    existing_cols = {c['name'] for c in inspector.get_columns(table)}

    with op.batch_alter_table(table) as batch_op:
        if 'saldo_pendiente' not in existing_cols:
            batch_op.add_column(sa.Column('saldo_pendiente', sa.Numeric(10, 2), nullable=False, server_default=sa.text('0')))
        if 'fecha_vencimiento' not in existing_cols:
            batch_op.add_column(sa.Column('fecha_vencimiento', sa.Date(), nullable=True))
        if 'activo' not in existing_cols:
            batch_op.add_column(sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('1')))

    # Quitar defaults de servidor si no deseas que permanezcan explícitos
    with op.batch_alter_table(table) as batch_op:
        batch_op.alter_column('saldo_pendiente', server_default=None, existing_type=sa.Numeric(10, 2))
        batch_op.alter_column('activo', server_default=None, existing_type=sa.Boolean())


def downgrade():
    table = 'puerta_orion_mensualidad'
    with op.batch_alter_table(table) as batch_op:
        try:
            batch_op.drop_column('saldo_pendiente')
        except Exception:
            pass
        try:
            batch_op.drop_column('fecha_vencimiento')
        except Exception:
            pass
        try:
            batch_op.drop_column('activo')
        except Exception:
            pass
