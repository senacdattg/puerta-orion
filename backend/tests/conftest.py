"""
Configuración y fixtures esenciales para todos los tests.

Este archivo contiene las fixtures fundamentales que se ejecutan automáticamente
y las funciones auxiliares para configuración de base de datos.

Las fixtures específicas están organizadas en:
- fixtures/app_fixtures.py: Fixtures de aplicación Flask
- fixtures/data_fixtures.py: Fixtures de datos de prueba
- fixtures/model_fixtures.py: Fixtures de modelos de BD
- fixtures/mock_fixtures.py: Fixtures de mocks y stubs

Principios aplicados:
- DRY: Fixtures reutilizables
- AAA (Arrange-Act-Assert): Estructura clara en tests
- Isolation: Cada test es independiente
- Fast: Tests rápidos usando SQLite en memoria
"""

import os
import pytest
from typing import Generator

from flask import Flask
from flask.testing import FlaskClient

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# NO importar db ni create_app aquí - se importarán en los fixtures después de limpiar env
# Esto evita que se inicialicen con la configuración incorrecta de MySQL

# ============================================================================
# CONSTANTES PARA TESTS
# ============================================================================

# URI de base de datos SQLite en memoria para tests
SQLITE_MEMORY_URI = 'sqlite:///:memory:'

# Datos de prueba comunes
TEST_PRIMER_NOMBRE = 'Juan'
TEST_PRIMER_APELLIDO = 'Pérez'


# ============================================================================
# FIXTURES DE APLICACIÓN
# ============================================================================

@pytest.fixture(scope='function', autouse=True)
def clean_env_for_tests():
    """
    Fixture que limpia variables de entorno de MySQL antes de cada test.
    Se ejecuta automáticamente (autouse=True) para todos los tests.
    """
    # Guardar valores originales
    old_env = {}
    env_vars_to_clear = [
        'DATABASE_URL', 'DB_HOST', 'MYSQL_HOST', 'DB_PORT', 
        'DB_USERNAME', 'DB_USER', 'DB_PASSWORD', 'MYSQL_PASSWORD', 'DB_NAME'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            old_env[var] = os.environ[var]
            del os.environ[var]
    
    # Forzar entorno de testing
    os.environ['FLASK_ENV'] = 'testing'
    
    yield
    
    # Restaurar variables de entorno después del test
    for var, value in old_env.items():
        os.environ[var] = value


def _configurar_base_datos_testing(app: Flask) -> None:
    """Configura la URI de base de datos para testing y recrea engines si es necesario."""
    from src.models.base import db
    
    current_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if current_uri != SQLITE_MEMORY_URI:
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_MEMORY_URI
        app.config['SQLALCHEMY_BINDS'] = {}
        _limpiar_engines_cache(app, db)


def _limpiar_engines_cache(app: Flask, db) -> None:
    """Limpia el cache de engines de Flask-SQLAlchemy para forzar recreación."""
    with app.app_context():
        try:
            if hasattr(db, '_app_engines') and app in db._app_engines:
                engines_dict = db._app_engines[app]
                for bind_key, engine in engines_dict.items():
                    if engine:
                        engine.dispose()
                engines_dict.clear()
        except (AttributeError, KeyError, TypeError, ValueError):
            pass


def _asegurar_configuracion_base_datos(app: Flask) -> None:
    """Asegura que la configuración de base de datos esté presente."""
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', SQLITE_MEMORY_URI)
    app.config.setdefault('SQLALCHEMY_BINDS', {})


def _inicializar_base_datos(app: Flask, db) -> None:
    """Inicializa la base de datos creando las tablas."""
    try:
        _ = db.engine
    except Exception:
        _limpiar_engines_cache_alternativo(app, db)
    db.create_all()


def _limpiar_engines_cache_alternativo(app: Flask, db) -> None:
    """Intenta limpiar el cache de engines como alternativa."""
    try:
        if hasattr(db, '_app_engines') and app in db._app_engines:
            engines_dict = db._app_engines[app]
            engines_dict.clear()
    except (AttributeError, KeyError):
        pass


@pytest.fixture(scope='function')
def app() -> Generator[Flask, None, None]:
    """
    Crea una instancia de la aplicación Flask para testing.
    
    Usa TestingConfig que configura SQLite en memoria para tests rápidos.
    Cada test tiene su propia base de datos limpia.
    """
    # Importar create_app y db después de que clean_env_for_tests haya limpiado el entorno
    # Esto asegura que se inicialicen con la configuración correcta
    from app import create_app
    from src.models.base import db
    
    # CRÍTICO: Flask-SQLAlchemy 3.x crea engines en init_app() y no refleja cambios posteriores
    # Por lo tanto, TestingConfig DEBE tener la URI correcta desde el principio
    # Verificamos que la configuración esté correcta después de crear la app
    
    # Crear app con configuración de testing y sin scheduler
    app = create_app('testing', testing=True)
    app.config['TESTING'] = True
    # NOTA DE SEGURIDAD: Deshabilitar CSRF solo en entorno de testing
    # - Esta configuración es SOLO para el entorno de pruebas automatizadas
    # - En producción, CSRF está habilitado por defecto en Flask-WTF
    # - Es una práctica común deshabilitar CSRF en tests para simplificar las pruebas
    # - Los tests no están expuestos a ataques CSRF reales ya que se ejecutan en un entorno controlado
    app.config['WTF_CSRF_ENABLED'] = False  # nosonar: S4502 - Deshabilitar protección CSRF (seguro en entorno de testing)
    
    # Verificar y forzar la URI correcta
    _configurar_base_datos_testing(app)
    
    with app.app_context():
        _asegurar_configuracion_base_datos(app)
        _inicializar_base_datos(app, db)
        yield app
        # Limpiar sesiones y cerrar conexiones
        db.session.remove()
        db.session.close()
        db.drop_all()
        # Cerrar engines explícitamente para evitar ResourceWarning
        try:
            if hasattr(db, 'engine') and db.engine:
                db.engine.dispose()
            _limpiar_engines_cache(app, db)
        except Exception:
            pass


@pytest.fixture(scope='function')
def client(app: Flask) -> FlaskClient:
    """
    Crea un cliente de prueba para hacer requests HTTP.
    
    Returns:
        FlaskClient: Cliente de prueba configurado
    """
    return app.test_client()


# ============================================================================
# FIXTURES DE SESIÓN DE BASE DE DATOS
# ============================================================================

@pytest.fixture
def db_session(app: Flask):
    """Proporciona acceso a la sesión de base de datos."""
    from src.models.base import db
    with app.app_context():
        yield db.session
        # Asegurar que la sesión se cierra correctamente
        db.session.remove()
        db.session.close()


# ============================================================================
# IMPORTAR FIXTURES DE MÓDULOS ESPECÍFICOS
# ============================================================================

# Importar fixtures de módulos específicos para que estén disponibles
# automáticamente en todos los tests
from tests.fixtures import (
    # App fixtures
    auth_headers,
    # Data fixtures
    sample_persona_data,
    sample_deportista_data,
    sample_evento_data,
    sample_usuario_data,
    # Model fixtures
    tipo_documento,
    sexo,
    categoria,
    tipo_evento,
    persona,
    usuario,
    deportista,
    # Mock fixtures
    mock_get_current_user,
    mock_token_required,
    mock_logger,
)

