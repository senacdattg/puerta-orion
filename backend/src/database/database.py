"""
Configuración de la base de datos usando SQLAlchemy.
Maneja la conexión y configuración de la base de datos de manera centralizada.
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# Inicializar SQLAlchemy
db = SQLAlchemy()

def init_database(app: Flask):
    """
    Inicializa la base de datos con la aplicación Flask.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://"
        f"{os.environ.get('DB_USER', 'root')}:"
        f"{os.environ.get('DB_PASSWORD', '')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}/"
        f"{os.environ.get('DB_NAME', 'puerta_orion')}"
    )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Inicializar la base de datos con la app
    db.init_app(app)
    
    return db

def create_tables(app: Flask):
    """
    Crea todas las tablas en la base de datos.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    with app.app_context():
        db.create_all()

def drop_tables(app: Flask):
    """
    Elimina todas las tablas de la base de datos.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    with app.app_context():
        db.drop_all()



