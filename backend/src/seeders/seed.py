"""
Script principal para ejecutar todos los seeders del sistema.

Este script ejecuta todos los seeders en el orden correcto,
respetando las dependencias entre tablas.

Uso:
    python -m src.seeders.seed
    o desde el directorio raíz:
    python backend/src/seeders/seed.py
"""

import sys
import os

# Agregar el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app import create_app
from backend.src.models.base import db

# Importar todos los seeders
from backend.src.seeders import (
    seed_tipo_documento,
    seed_sexo,
    seed_grupo_sanguineo,
    seed_categoria,
    seed_deporte,
    seed_tipo_evento,
    seed_metodo_pago,
    seed_parentesco,
    seed_tipo_enfermedad,
    seed_diagnostico
)


def run_all_seeders():
    """
    Ejecuta todos los seeders del sistema en orden lógico.
    
    Orden de ejecución:
    1. Catálogos básicos independientes
    2. Tablas dependientes
    """
    print("=" * 70)
    print("🌱 INICIANDO SEEDERS DEL SISTEMA PUERTA_ORION")
    print("=" * 70)
    print()
    
    # Crear contexto de aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # PASO 1: Catálogos básicos (sin dependencias)
            print("📦 PASO 1: Insertando catálogos básicos...")
            print("-" * 70)
            seed_tipo_documento.run()
            seed_sexo.run()
            seed_grupo_sanguineo.run()
            seed_categoria.run()
            seed_deporte.run()
            seed_tipo_evento.run()
            seed_metodo_pago.run()
            seed_parentesco.run()
            
            # PASO 2: Tablas con dependencias
            print("📦 PASO 2: Insertando tablas con dependencias...")
            print("-" * 70)
            seed_tipo_enfermedad.run()
            seed_diagnostico.run()  # Depende de TipoEnfermedad
            
            print("=" * 70)
            print("✅ TODOS LOS SEEDERS SE EJECUTARON EXITOSAMENTE")
            print("=" * 70)
            print()
            print("📊 Resumen:")
            print("  - 10 seeders ejecutados")
            print("  - Base de datos poblada con datos iniciales")
            print("  - Sistema listo para usar")
            print()
            
        except Exception as e:
            print("=" * 70)
            print("❌ ERROR AL EJECUTAR SEEDERS")
            print("=" * 70)
            print(f"Error: {str(e)}")
            print()
            db.session.rollback()
            raise


if __name__ == '__main__':
    run_all_seeders()


