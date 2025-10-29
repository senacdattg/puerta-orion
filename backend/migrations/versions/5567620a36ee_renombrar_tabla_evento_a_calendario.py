"""renombrar_tabla_evento_a_calendario

Revision ID: 5567620a36ee
Revises: add_evento_horas
Create Date: 2025-10-28 17:26:21.631090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5567620a36ee'
down_revision = 'add_evento_horas'
branch_labels = None
depends_on = None


def upgrade():
    # Renombrar la tabla puerta_orion_evento a puerta_orion_calendario
    op.rename_table('puerta_orion_evento', 'puerta_orion_calendario')


def downgrade():
    # Revertir el cambio: renombrar puerta_orion_calendario a puerta_orion_evento
    op.rename_table('puerta_orion_calendario', 'puerta_orion_evento')
