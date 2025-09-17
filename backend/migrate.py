"""
Script para crear la base de datos y todas las tablas.
Ejecuta este script para inicializar la base de datos con los modelos ORM.
Cada tabla tiene su propio archivo de modelo siguiendo el principio SRP.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from flask import Flask
from dotenv import load_dotenv
from src.models import init_database, create_tables, db
from src.models import *  # Importar todos los modelos

def create_database():
    """
    Crea la base de datos y todas las tablas.
    """
    # Cargar variables de entorno
    load_dotenv()
    
    # Crear aplicación Flask
    app = Flask(__name__)
    
    # Configurar la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar la base de datos
    init_database(app)
    
    try:
        with app.app_context():
            print("🔄 Creando base de datos...")
            print("📋 Estructura modular: Cada tabla tiene su propio archivo de modelo")
            
            # Crear todas las tablas
            create_tables(app)
            
            print("✅ Base de datos creada exitosamente!")
            print("📋 Tablas creadas:")
            
            # Listar todas las tablas creadas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            for table in sorted(tables):
                print(f"   - {table}")
            
            print(f"\n📊 Total de tablas: {len(tables)}")
            print("\n🎯 Principios aplicados:")
            print("   ✓ SRP: Cada modelo en su propio archivo")
            print("   ✓ KISS: Estructura simple y clara")
            print("   ✓ DRY: Configuración centralizada")
            
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        return False
    
    return True

def drop_database():
    """
    Elimina todas las tablas de la base de datos.
    ⚠️ CUIDADO: Esto eliminará todos los datos!
    """
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    init_database(app)
    
    try:
        with app.app_context():
            print("⚠️  Eliminando todas las tablas...")
            db.drop_all()
            print("✅ Todas las tablas eliminadas!")
    except Exception as e:
        print(f"❌ Error al eliminar las tablas: {e}")
        return False
    
    return True

def reset_database():
    """
    Reinicia la base de datos (elimina y crea nuevamente).
    ⚠️ CUIDADO: Esto eliminará todos los datos!
    """
    print("🔄 Reiniciando base de datos...")
    if drop_database():
        return create_database()
    return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestionar la base de datos de Puerta Orion')
    parser.add_argument('action', choices=['create', 'drop', 'reset'], 
                       help='Acción a realizar: create (crear), drop (eliminar), reset (reiniciar)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        create_database()
    elif args.action == 'drop':
        confirm = input("⚠️  ¿Estás seguro de que quieres eliminar todas las tablas? (y/N): ")
        if confirm.lower() == 'y':
            drop_database()
        else:
            print("❌ Operación cancelada")
    elif args.action == 'reset':
        confirm = input("⚠️  ¿Estás seguro de que quieres reiniciar la base de datos? (y/N): ")
        if confirm.lower() == 'y':
            reset_database()
        else:
            print("Comando no reconocido. Usa: init, migrate, upgrade, revision.")

if __name__ == "__main__":
    main()
