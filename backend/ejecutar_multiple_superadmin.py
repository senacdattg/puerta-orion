#!/usr/bin/env python3
"""
Script para ejecutar el seeder de múltiples super administradores.

Este script crea varios usuarios SuperAdmin con todos los permisos del sistema.

Uso:
    python ejecutar_multiple_superadmin.py
"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app
from backend.src.seeders.seed_multiple_superadmin import run

def main():
    """Función principal para ejecutar el seeder."""
    print("🚀 Iniciando creación de múltiples Super Administradores...")
    print("=" * 60)
    
    try:
        # Crear aplicación Flask
        app = create_app()
        
        # Ejecutar dentro del contexto de la aplicación
        with app.app_context():
            run()
        
        print("=" * 60)
        print("✅ Proceso completado exitosamente")
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error durante la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
