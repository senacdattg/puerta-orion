"""
Script para ejecutar solo los seeders del sistema de permisos y super admin.

Ejecuta en orden:
1. Permisos
2. Roles
3. Super Administrador

Uso:
    python ejecutar_superadmin.py
"""

import sys
import os

# Agregar el directorio raíz al path para las importaciones
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from src.models.base import db

# Importar seeders
from src.seeders import seed_permisos, seed_roles, seed_superadmin


def main():
    """Ejecuta los seeders del sistema de permisos y super admin."""
    print("=" * 70)
    print("👑 CONFIGURACIÓN DEL SUPER ADMINISTRADOR")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            print("📦 PASO 1: Insertando permisos del sistema...")
            print("-" * 70)
            seed_permisos.run()
            print()
            
            print("📦 PASO 2: Configurando roles...")
            print("-" * 70)
            seed_roles.run()
            print()
            
            print("📦 PASO 3: Creando Super Administrador...")
            print("-" * 70)
            seed_superadmin.run()
            print()
            
            print("=" * 70)
            print("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 70)
            print()
            print("🔑 CREDENCIALES DE ACCESO:")
            print("   Usuario: superadmin")
            print("   Contraseña: SuperAdmin2024!")
            print()
            print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
            print()
            
        except Exception as e:
            print("=" * 70)
            print("❌ ERROR EN LA CONFIGURACIÓN")
            print("=" * 70)
            print(f"Error: {str(e)}")
            print()
            db.session.rollback()
            raise


if __name__ == '__main__':
    main()

