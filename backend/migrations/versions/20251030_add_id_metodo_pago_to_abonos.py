"""add id_metodo_pago back to abonos mensualidad

Revision ID: abn_mens_add_metodo
Revises: abn_mens_drop_metodo
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


revision = 'abn_mens_add_metodo'
down_revision = 'abn_mens_drop_metodo'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('puerta_orion_abonos_mensualidad') as batch_op:
    batch_op.add_column(sa.Column('id_metodo_pago', sa.Integer(), nullable=True))
    batch_op.create_foreign_key(None, 'puerta_orion_metodo_pago', ['id_metodo_pago'], ['id_metodo_pago'])


def downgrade():
  with op.batch_alter_table('puerta_orion_abonos_mensualidad') as batch_op:
    try:
      batch_op.drop_constraint('puerta_orion_abonos_mensualidad_ibfk_1', type_='foreignkey')
    except Exception:
      pass
    try:
      batch_op.drop_column('id_metodo_pago')
    except Exception:
      pass


