"""
Tests unitarios para database.py.

Cubre las funciones de inicialización y gestión de la base de datos.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from src.database.database import db, init_database, create_tables, drop_tables


@pytest.mark.unit
class TestDatabaseInit:
    """Tests para init_database."""
    
    def test_init_database_calls_init_app(self):
        """Test: init_database llama a db.init_app."""
        app = Flask(__name__)
        
        with patch.object(db, 'init_app') as mock_init_app:
            result = init_database(app)
            
            mock_init_app.assert_called_once_with(app)
            assert result == db
    
    def test_init_database_returns_db_instance(self):
        """Test: init_database retorna la instancia de db."""
        app = Flask(__name__)
        
        with patch.object(db, 'init_app'):
            result = init_database(app)
            
            assert result == db


@pytest.mark.unit
class TestCreateTables:
    """Tests para create_tables."""
    
    def test_create_tables_calls_db_create_all(self):
        """Test: create_tables llama a db.create_all dentro del contexto."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with patch.object(db, 'create_all') as mock_create_all:
            create_tables(app)
            
            mock_create_all.assert_called_once()
    
    def test_create_tables_with_app_context(self):
        """Test: create_tables se ejecuta dentro del contexto de la app."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Verificar que no hay error al crear tablas
        with patch.object(db, 'create_all'):
            create_tables(app)


@pytest.mark.unit
class TestDropTables:
    """Tests para drop_tables."""
    
    def test_drop_tables_calls_db_drop_all(self):
        """Test: drop_tables llama a db.drop_all dentro del contexto."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with patch.object(db, 'drop_all') as mock_drop_all:
            drop_tables(app)
            
            mock_drop_all.assert_called_once()
    
    def test_drop_tables_with_app_context(self):
        """Test: drop_tables se ejecuta dentro del contexto de la app."""
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Verificar que no hay error al eliminar tablas
        with patch.object(db, 'drop_all'):
            drop_tables(app)


@pytest.mark.unit
class TestDatabaseInstance:
    """Tests para la instancia de db."""
    
    def test_db_is_sqlalchemy_instance(self):
        """Test: db es una instancia de SQLAlchemy."""
        from flask_sqlalchemy import SQLAlchemy
        assert isinstance(db, SQLAlchemy)

