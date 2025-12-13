"""Eliminar id_mensualidad de tabla deportista

Revision ID: 007_eliminar_id_mensualidad
Revises: 607d95db0456
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '007_eliminar_id_mensualidad'
down_revision = '607d95db0456'
branch_labels = None
depends_on = None


def _column_exists(bind, table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    inspector = Inspector.from_engine(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def _fk_exists(bind, table_name, constraint_name=None, column_name=None):
    """Verifica si una foreign key existe"""
    inspector = Inspector.from_engine(bind)
    for fk in inspector.get_foreign_keys(table_name):
        if constraint_name and fk.get('name') == constraint_name:
            return True
        if column_name and column_name in fk.get('constrained_columns', []):
            return True
    return False


def upgrade():
    """
    Eliminar el campo id_mensualidad de la tabla deportista.
    
    Las mensualidades ya están relacionadas con Persona, por lo que
    no es necesario mantener esta relación redundante en Deportista.
    """
    bind = op.get_bind()
    table_name = 'puerta_orion_deportista'
    
    # Verificar que la tabla existe
    inspector = Inspector.from_engine(bind)
    if table_name not in inspector.get_table_names():
        return  # Si la tabla no existe, no hacer nada
    
    # 1. Eliminar la foreign key si existe
    # Buscar la FK por nombre o por columna
    fk_name = None
    for fk in inspector.get_foreign_keys(table_name):
        if 'id_mensualidad' in fk.get('constrained_columns', []):
            fk_name = fk.get('name')
            break
    
    if fk_name:
        try:
            op.drop_constraint(fk_name, table_name, type_='foreignkey')
        except Exception as e:
            print(f"Advertencia: No se pudo eliminar la FK {fk_name}: {e}")
    
    # También intentar eliminar por nombre común
    for fk_name_common in ['fk_deportista_mensualidad', 'puerta_orion_deportista_ibfk_mensualidad']:
        try:
            op.drop_constraint(fk_name_common, table_name, type_='foreignkey')
        except Exception:
            pass  # Ignorar si no existe
    
    # 2. Eliminar la columna id_mensualidad si existe
    if _column_exists(bind, table_name, 'id_mensualidad'):
        try:
            with op.batch_alter_table(table_name, schema=None) as batch_op:
                batch_op.drop_column('id_mensualidad')
        except Exception as e:
            print(f"Advertencia: No se pudo eliminar la columna id_mensualidad: {e}")


def downgrade():
    """
    Revertir: Restaurar el campo id_mensualidad en la tabla deportista.
    """
    bind = op.get_bind()
    table_name = 'puerta_orion_deportista'
    
    inspector = Inspector.from_engine(bind)
    if table_name not in inspector.get_table_names():
        return
    
    # Restaurar la columna id_mensualidad
    if not _column_exists(bind, table_name, 'id_mensualidad'):
        with op.batch_alter_table(table_name, schema=None) as batch_op:
            batch_op.add_column(sa.Column('id_mensualidad', sa.Integer(), nullable=True))
    
    # Restaurar la foreign key
    if not _fk_exists(bind, table_name, column_name='id_mensualidad'):
        try:
            op.create_foreign_key(
                'fk_deportista_mensualidad',
                table_name,
                'puerta_orion_mensualidad',
                ['id_mensualidad'],
                ['id_mensualidad'],
                ondelete='SET NULL'
            )
        except Exception as e:
            print(f"Advertencia: No se pudo restaurar la FK: {e}")

