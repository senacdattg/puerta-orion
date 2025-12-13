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
    
    NOTA: Esta función está deshabilitada porque la configuración
    de la base de datos ahora se maneja en config.py para mayor
    flexibilidad y consistencia.
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    # La configuración de la base de datos ahora se maneja en config.py
    # Solo inicializamos la base de datos con la app
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



