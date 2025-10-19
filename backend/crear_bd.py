#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear la base de datos y tablas desde cero
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from src.models.base import db
from src.models import *

def crear_base_datos():
    """Crear todas las tablas de la base de datos"""
    print("Creando base de datos...")
    
    # Crear contexto de aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Base de datos creada exitosamente!")
            
            # Verificar que las tablas se crearon
            print("\n📊 Tablas creadas:")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            for table in sorted(tables):
                print(f"  - {table}")
                
        except Exception as e:
            print(f"❌ Error al crear base de datos: {str(e)}")
            raise

if __name__ == '__main__':
    crear_base_datos()
