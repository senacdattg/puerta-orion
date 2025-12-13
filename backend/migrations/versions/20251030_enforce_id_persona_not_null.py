"""Enforce id_persona NOT NULL en mensualidad

Revision ID: f6e5d4c3b2a1
Revises: 9750ad435abf
Create Date: 2025-10-30 00:10:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'f6e5d4c3b2a1'
down_revision = '9750ad435abf'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Verificar que no existan registros con id_persona NULL
    result = bind.execute(text("""
        SELECT COUNT(*) AS cnt
        FROM puerta_orion_mensualidad
        WHERE id_persona IS NULL
    """))
    null_count = result.scalar() or 0

    if null_count > 0:
        raise RuntimeError(
            f"No se puede poner NOT NULL id_persona: hay {null_count} registros con id_persona NULL en puerta_orion_mensualidad. "
            "Realiza el backfill antes de aplicar esta migración."
        )

    # Alterar columna a NOT NULL
    with op.batch_alter_table('puerta_orion_mensualidad') as batch_op:
        batch_op.alter_column(
            'id_persona',
            existing_type=sa.Integer(),
            nullable=False
        )


def downgrade():
    # Revertir a NULLABLE
    with op.batch_alter_table('puerta_orion_mensualidad') as batch_op:
        batch_op.alter_column(
            'id_persona',
            existing_type=sa.Integer(),
            nullable=True
        )
