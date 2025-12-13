"""create abonos mensualidad table

Revision ID: abn_mens_001
Revises: a1b2c3d4e6f7
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abn_mens_001'
down_revision = 'a1b2c3d4e6f7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'puerta_orion_abonos_mensualidad',
        sa.Column('id_abono', sa.Integer(), primary_key=True),
        sa.Column('id_mensualidad', sa.Integer(), sa.ForeignKey('puerta_orion_mensualidad.id_mensualidad'), nullable=False),
        sa.Column('monto', sa.Numeric(10, 2), nullable=False),
        sa.Column('fecha_abono', sa.Date(), nullable=False),
        sa.Column('id_metodo_pago', sa.Integer(), sa.ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_abono_mensualidad_mensualidad', 'puerta_orion_abonos_mensualidad', ['id_mensualidad'])


def downgrade():
    op.drop_index('ix_abono_mensualidad_mensualidad', table_name='puerta_orion_abonos_mensualidad')
    op.drop_table('puerta_orion_abonos_mensualidad')


