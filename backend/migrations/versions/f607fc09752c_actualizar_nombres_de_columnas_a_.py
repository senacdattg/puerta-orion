"""Actualizar nombres de columnas a estandar

Revision ID: f607fc09752c
Revises: ce296712a0ca
Create Date: 2025-10-18 23:45:17.703042

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f607fc09752c'
down_revision = 'ce296712a0ca'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    personas_table = tables_map.get('puerta_orion_personas')
    if personas_table:
        with op.batch_alter_table(personas_table, schema=None) as batch_op:
            personas_columns = {col['name'] for col in inspector.get_columns(personas_table)}
            if 'documento' in personas_columns:
                batch_op.alter_column('documento',
                    existing_type=mysql.INTEGER(),
                    type_=sa.String(length=20),
                    existing_nullable=False)
            if 'correo_electronico' in personas_columns:
                batch_op.alter_column('correo_electronico',
                    existing_type=mysql.VARCHAR(length=50),
                    type_=sa.String(length=100),
                    existing_nullable=False)
            if 'direccion' in personas_columns:
                batch_op.alter_column('direccion',
                    existing_type=mysql.VARCHAR(length=50),
                    type_=sa.String(length=200),
                    existing_nullable=False)
            if 'telefono' in personas_columns:
                batch_op.alter_column('telefono',
                    existing_type=mysql.VARCHAR(length=15),
                    type_=sa.String(length=20),
                    existing_nullable=False)

    sexo_table = tables_map.get('puerta_orion_sexo')
    if sexo_table:
        sexo_columns = {col['name'] for col in inspector.get_columns(sexo_table)}
        with op.batch_alter_table(sexo_table, schema=None) as batch_op:
            if 'nombre' not in sexo_columns:
                batch_op.add_column(sa.Column('nombre', sa.String(length=150), nullable=False))
            if 'sexo' in sexo_columns:
                batch_op.drop_column('sexo')

    # ### end Alembic commands ###


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables_map = {t.lower(): t for t in inspector.get_table_names()}

    sexo_table = tables_map.get('puerta_orion_sexo')
    if sexo_table:
        sexo_columns = {col['name'] for col in inspector.get_columns(sexo_table)}
        with op.batch_alter_table(sexo_table, schema=None) as batch_op:
            if 'sexo' not in sexo_columns:
                batch_op.add_column(sa.Column('sexo', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
            if 'nombre' in sexo_columns:
                batch_op.drop_column('nombre')

    personas_table = tables_map.get('puerta_orion_personas')
    if personas_table:
        personas_columns = {col['name'] for col in inspector.get_columns(personas_table)}
        with op.batch_alter_table(personas_table, schema=None) as batch_op:
            if 'telefono' in personas_columns:
                batch_op.alter_column('telefono',
                    existing_type=sa.String(length=20),
                    type_=mysql.VARCHAR(length=15),
                    existing_nullable=False)
            if 'direccion' in personas_columns:
                batch_op.alter_column('direccion',
                    existing_type=sa.String(length=200),
                    type_=mysql.VARCHAR(length=50),
                    existing_nullable=False)
            if 'correo_electronico' in personas_columns:
                batch_op.alter_column('correo_electronico',
                    existing_type=sa.String(length=100),
                    type_=mysql.VARCHAR(length=50),
                    existing_nullable=False)
            if 'documento' in personas_columns:
                batch_op.alter_column('documento',
                    existing_type=sa.String(length=20),
                    type_=mysql.INTEGER(),
                    existing_nullable=False)

    # ### end Alembic commands ###
