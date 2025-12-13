"""drop id_metodo_pago from abonos mensualidad

Revision ID: abn_mens_drop_metodo
Revises: abn_mens_001
Create Date: 2025-10-30
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = 'abn_mens_drop_metodo'
down_revision = 'abn_mens_001'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    # Buscar nombres reales de las FKs sobre la columna id_metodo_pago (MySQL suele nombrarlas *_ibfk_#)
    fk_rows = bind.execute(text("""
        SELECT CONSTRAINT_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'puerta_orion_abonos_mensualidad'
          AND COLUMN_NAME = 'id_metodo_pago'
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """)).fetchall()

    for (constraint_name,) in fk_rows:
        try:
            bind.execute(text(f"ALTER TABLE puerta_orion_abonos_mensualidad DROP FOREIGN KEY `{constraint_name}`"))
        except Exception:
            pass

    # Eliminar la columna si existe
    try:
        bind.execute(text("""
            ALTER TABLE puerta_orion_abonos_mensualidad
            DROP COLUMN id_metodo_pago
        """))
    except Exception:
        pass


def downgrade():
    with op.batch_alter_table('puerta_orion_abonos_mensualidad') as batch_op:
        batch_op.add_column(sa.Column('id_metodo_pago', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'puerta_orion_metodo_pago', ['id_metodo_pago'], ['id_metodo_pago'])


