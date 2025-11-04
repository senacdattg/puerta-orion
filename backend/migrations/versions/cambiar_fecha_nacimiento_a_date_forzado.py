"""Forzar cambio de fecha_nacimiento a Date

Revision ID: force_fecha_nacimiento_date
Revises: fb54dee06167
Create Date: 2025-11-02 16:00:00.000000

Esta migración fuerza el cambio de fecha_nacimiento de SMALLINT a DATE
incluso si otras migraciones ya intentaron hacerlo.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'force_fecha_nacimiento_date'
down_revision = 'fb54dee06167'  # Después de add_password_reset
branch_labels = None
depends_on = None


def upgrade():
    """
    Forzar el cambio de fecha_nacimiento de SMALLINT a DATE.
    Esta migración se ejecuta después de todas las demás para asegurar el cambio.
    """
    bind = op.get_bind()
    inspector = inspect(bind)
    
    # Verificar si la tabla existe
    if 'puerta_orion_deportista' not in inspector.get_table_names():
        print("Tabla puerta_orion_deportista no existe, saltando migración")
        return
    
    existing_columns = [col['name'] for col in inspector.get_columns('puerta_orion_deportista')]
    
    if 'fecha_nacimiento' not in existing_columns:
        print("Columna fecha_nacimiento no existe, creándola como DATE")
        op.add_column('puerta_orion_deportista', 
                     sa.Column('fecha_nacimiento', sa.Date(), nullable=True))
        return
    
    # Verificar el tipo actual de la columna
    fecha_col = [col for col in inspector.get_columns('puerta_orion_deportista') 
                 if col['name'] == 'fecha_nacimiento'][0]
    
    col_type_str = str(fecha_col['type']).upper()
    
    # Si ya es DATE, no hacer nada
    if 'DATE' in col_type_str:
        print(f"[OK] fecha_nacimiento ya es de tipo DATE ({col_type_str}). No se requiere cambio.")
        return
    
    print(f"\n[!] DETECTADO: fecha_nacimiento es {col_type_str}, necesitamos cambiarlo a DATE")
    print("=== EJECUTANDO CONVERSIÓN FORZADA ===\n")
    
    # Verificar si existe columna temporal de intentos anteriores
    temp_cols = [col['name'] for col in inspector.get_columns('puerta_orion_deportista')]
    if 'fecha_nacimiento_temp' in temp_cols:
        print("[!] Limpiando columna temporal anterior...")
        try:
            op.drop_column('puerta_orion_deportista', 'fecha_nacimiento_temp')
            print("[OK] Columna temporal anterior eliminada")
        except Exception as e:
            print(f"[!] Error al eliminar columna temporal anterior: {e}")
    
    # Método seguro: columna temporal
    print("\n[PASO 1/4] Creando columna temporal fecha_nacimiento_temp (DATE)...")
    try:
        op.add_column('puerta_orion_deportista',
                     sa.Column('fecha_nacimiento_temp', sa.Date(), nullable=True))
        print("[OK] Columna temporal creada")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise Exception(f"No se pudo crear columna temporal: {e}")
    
    print("\n[PASO 2/4] Convirtiendo y copiando datos (anos SMALLINT -> fechas DATE)...")
    try:
        # Convertir años a fechas 01-01-YYYY
        op.execute("""
            UPDATE puerta_orion_deportista 
            SET fecha_nacimiento_temp = STR_TO_DATE(CONCAT(CAST(fecha_nacimiento AS UNSIGNED), '-01-01'), '%Y-%m-%d')
            WHERE fecha_nacimiento IS NOT NULL
            AND fecha_nacimiento BETWEEN 1900 AND 2100
        """)
        print("[OK] Datos convertidos y copiados exitosamente")
    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            op.drop_column('puerta_orion_deportista', 'fecha_nacimiento_temp')
        except:
            pass
        raise Exception(f"Error al convertir datos: {e}")
    
    print("\n[PASO 3/4] Eliminando columna antigua fecha_nacimiento (SMALLINT)...")
    try:
        op.drop_column('puerta_orion_deportista', 'fecha_nacimiento')
        print("[OK] Columna antigua eliminada")
    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            op.drop_column('puerta_orion_deportista', 'fecha_nacimiento_temp')
        except:
            pass
        raise Exception(f"Error al eliminar columna antigua: {e}")
    
    print("\n[PASO 4/4] Renombrando columna temporal a fecha_nacimiento...")
    try:
        op.execute("""
            ALTER TABLE puerta_orion_deportista 
            CHANGE COLUMN fecha_nacimiento_temp fecha_nacimiento DATE NULL
        """)
        print("[OK] Columna renombrada exitosamente")
    except Exception as e:
        print(f"[ERROR] {e}")
        raise Exception(f"Error al renombrar columna: {e}")
    
    print("\n" + "="*60)
    print("[OK][OK][OK] MIGRACION COMPLETADA EXITOSAMENTE [OK][OK][OK]")
    print("="*60)
    print("fecha_nacimiento ahora es de tipo DATE")
    
    # Verificación final
    try:
        inspector_final = inspect(op.get_bind())
        fecha_col_final = [col for col in inspector_final.get_columns('puerta_orion_deportista') 
                          if col['name'] == 'fecha_nacimiento'][0]
        col_type_final = str(fecha_col_final['type']).upper()
        print(f"\n[OK] VERIFICACION: Tipo de columna final: {col_type_final}")
        
        if 'DATE' in col_type_final:
            print("[OK][OK][OK] CONFIRMADO: fecha_nacimiento es ahora DATE [OK][OK][OK]")
        else:
            print(f"[!][!][!] ADVERTENCIA: El tipo sigue siendo {col_type_final}")
            print("Ejecuta manualmente: ALTER TABLE puerta_orion_deportista MODIFY fecha_nacimiento DATE NULL;")
    except Exception as e:
        print(f"[!] No se pudo verificar el tipo final: {e}")
        print("Verifica manualmente con: DESCRIBE puerta_orion_deportista;")


def downgrade():
    """
    Revertir: volver de Date a SmallInteger (solo año).
    """
    try:
        # Crear columna temporal SMALLINT
        op.add_column('puerta_orion_deportista',
                     sa.Column('fecha_nacimiento_temp', sa.SmallInteger(), nullable=True))
        
        # Extraer años de fechas
        op.execute("""
            UPDATE puerta_orion_deportista 
            SET fecha_nacimiento_temp = YEAR(fecha_nacimiento)
            WHERE fecha_nacimiento IS NOT NULL
        """)
        
        # Eliminar columna DATE
        op.drop_column('puerta_orion_deportista', 'fecha_nacimiento')
        
        # Renombrar temporal
        op.execute("""
            ALTER TABLE puerta_orion_deportista 
            CHANGE COLUMN fecha_nacimiento_temp fecha_nacimiento SMALLINT NULL
        """)
    except Exception as e:
        print(f"Error al revertir: {e}")

