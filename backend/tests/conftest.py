"""
Configuración y fixtures compartidas para todos los tests.

Este archivo contiene fixtures de pytest que se pueden usar en todos los tests,
siguiendo el principio DRY y las mejores prácticas de testing.

Principios aplicados:
- DRY: Fixtures reutilizables
- AAA (Arrange-Act-Assert): Estructura clara en tests
- Isolation: Cada test es independiente
- Fast: Tests rápidos usando SQLite en memoria
"""

import os
import pytest
from datetime import date, datetime
from typing import Dict, Any, Optional, Generator
from unittest.mock import Mock, patch, MagicMock

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
    
    # Crear app con configuración de testing
    app = create_app('testing')
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
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app: Flask) -> FlaskClient:
    """
    Crea un cliente de prueba para hacer requests HTTP.
    
    Returns:
        FlaskClient: Cliente de prueba configurado
    """
    return app.test_client()


@pytest.fixture(scope='function')
def auth_headers(client: FlaskClient) -> Dict[str, str]:
    """
    Crea headers de autenticación con un token válido.
    
    Returns:
        Dict con headers de Authorization
    """
    # Crear usuario de prueba y obtener token
    # Esto se puede mejorar creando un usuario real en la BD de test
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test_token_12345'
    }


# ============================================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================================

@pytest.fixture
def sample_persona_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear una persona."""
    return {
        'primer_nombre': TEST_PRIMER_NOMBRE,
        'segundo_nombre': 'Carlos',
        'primer_apellido': TEST_PRIMER_APELLIDO,
        'segundo_apellido': 'García',
        'documento': 12345678,
        'correo_electronico': 'juan.perez@example.com',
        'telefono': '3001234567',
        'direccion': 'Calle 123 #45-67',
        'id_tipo_documento': 1,
        'id_sexo': 1,
        'fecha_nacimiento': date(2000, 1, 15)
    }


@pytest.fixture
def sample_deportista_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un deportista."""
    return {
        'datos_deportista': {
            'id_persona': 1,
            'id_categoria': 1,
            'peso': 65.5,
            'altura': 1.75,
            'fecha_nacimiento': 2000,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        },
        'informacion_deportiva': {
            'practica_otro_deporte': False,
            'participa_escuela': True,
            'recomendacion_medica': False,
            'id_escuela': 1,
            'id_deporte': 1,
            'id_institucion_registro': 1
        },
        'tipo_enfermedad': 1,
        'diagnostico': [1, 2]
    }


@pytest.fixture
def sample_evento_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un evento."""
    return {
        'nombre': 'Torneo de Fútbol',
        'fecha_evento': '2024-12-31',
        'hora_inicio': '10:00',
        'hora_fin': '12:00',
        'lugar': 'Cancha Principal',
        'descripcion': 'Torneo anual de fútbol',
        'id_categoria': 1,
        'id_tipo_evento': 1
    }


@pytest.fixture
def sample_usuario_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un usuario."""
    from tests.test_config import TEST_PASSWORD, TEST_USERNAME, TEST_EMAIL
    
    return {
        'persona': {
            'primer_nombre': 'Test',
            'primer_apellido': 'User',
            'documento': 99999999,
            'correo_electronico': TEST_EMAIL,
            'telefono': '3009999999',
            'id_tipo_documento': 1,
            'id_sexo': 1
        },
        'usuario': {
            'usuario': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
    }


# ============================================================================
# FIXTURES DE MODELOS (OBJETOS DE BD)
# ============================================================================

@pytest.fixture
def tipo_documento(db_session):
    """Crea un tipo de documento de prueba."""
    try:
        from src.models.catalogos.tipo_documento import TipoDocumento
        tipo = TipoDocumento(
            nombre_documento='Cédula de Ciudadanía',
            codigo='CC'
        )
        db_session.add(tipo)
        db_session.commit()
        return tipo
    except Exception:
        # Si el modelo no existe, retornar un mock
        return MagicMock(id_tipo_documento=1, nombre_documento='Cédula de Ciudadanía')


@pytest.fixture
def sexo(db_session):
    """Crea un sexo de prueba."""
    try:
        from src.models.categorias.sexo import Sexo
        sexo_obj = Sexo(nombre='Masculino', codigo='M')
        db_session.add(sexo_obj)
        db_session.commit()
        return sexo_obj
    except Exception:
        return MagicMock(id_sexo=1, nombre='Masculino')


@pytest.fixture
def categoria(db_session):
    """Crea una categoría de prueba."""
    try:
        from src.models.categorias.categoria import Categoria
        categoria_obj = Categoria(
            nombre_categoria='Sub-15',
            codigo_categoria=101,
            edad_minima=13,
            edad_maxima=15
        )
        db_session.add(categoria_obj)
        db_session.commit()
        return categoria_obj
    except Exception:
        return MagicMock(id_categoria=1, nombre_categoria='Sub-15')


@pytest.fixture
def tipo_evento(db_session):
    """Crea un tipo de evento de prueba."""
    try:
        from src.models.eventos.tipo_evento import TipoEvento
        tipo = TipoEvento(
            nombre='Torneo',
            descripcion='Evento tipo torneo'
        )
        db_session.add(tipo)
        db_session.commit()
        return tipo
    except Exception:
        return MagicMock(id_tipo_evento=1, nombre='Torneo')


@pytest.fixture
def persona(db_session, tipo_documento, sexo):
    """Crea una persona de prueba."""
    try:
        from src.models.personas.persona import Persona
        persona_obj = Persona(
            primer_nombre=TEST_PRIMER_NOMBRE,
            primer_apellido=TEST_PRIMER_APELLIDO,
            documento=12345678,
            correo_electronico='juan@example.com',
            telefono='3001234567',
            id_tipo_documento=getattr(tipo_documento, 'id_tipo_documento', 1),
            id_sexo=getattr(sexo, 'id_sexo', 1),
            fecha_nacimiento=date(2000, 1, 15)
        )
        db_session.add(persona_obj)
        db_session.commit()
        return persona_obj
    except Exception:
        return MagicMock(id_persona=1, primer_nombre=TEST_PRIMER_NOMBRE, primer_apellido=TEST_PRIMER_APELLIDO)


@pytest.fixture
def usuario(db_session, persona):
    """Crea un usuario de prueba."""
    try:
        from src.models.usuarios.usuario import Usuario
        from passlib.hash import bcrypt
        from tests.test_config import TEST_USERNAME, TEST_PASSWORD
        
        usuario_obj = Usuario(
            usuario=TEST_USERNAME,
            password=bcrypt.hash(TEST_PASSWORD),
            id_persona=getattr(persona, 'id_persona', 1),
            estado=True
        )
        db_session.add(usuario_obj)
        db_session.commit()
        return usuario_obj
    except Exception:
        from tests.test_config import TEST_USERNAME
        return MagicMock(id_usuario=1, usuario=TEST_USERNAME)


@pytest.fixture
def deportista(db_session, persona, categoria):
    """Crea un deportista de prueba."""
    try:
        from src.models.deportistas.deportista import Deportista
        deportista_obj = Deportista(
            id_persona=getattr(persona, 'id_persona', 1),
            id_categoria=getattr(categoria, 'id_categoria', 1),
            peso=65.5,
            altura=1.75,
            fecha_nacimiento=date(2000, 1, 15)
        )
        db_session.add(deportista_obj)
        db_session.commit()
        return deportista_obj
    except Exception:
        return MagicMock(id_deportista=1, id_persona=1, id_categoria=1)


# ============================================================================
# FIXTURES DE SESIÓN Y MOCKS
# ============================================================================

@pytest.fixture
def db_session(app: Flask):
    """Proporciona acceso a la sesión de base de datos."""
    # db ya está importado en el fixture app, pero lo importamos aquí por seguridad
    from src.models.base import db
    with app.app_context():
        yield db.session


@pytest.fixture
def mock_get_current_user():
    """Mock para get_current_user que retorna un usuario de prueba."""
    user_data = {
        'id_usuario': 1,
        'username': 'testuser',
        'persona': {
            'id_persona': 1,
            'nombre_completo': f'{TEST_PRIMER_NOMBRE} {TEST_PRIMER_APELLIDO}',
            'documento': 12345678
        },
        'roles': [{'nombre_rol': 'Deportista'}],
        'rol_activo': {'nombre_rol': 'Deportista'}
    }
    
    with patch('src.middleware.auth_decorator.get_current_user', return_value=user_data):
        yield user_data


@pytest.fixture
def mock_token_required():
    """Mock para el decorador token_required que siempre permite acceso."""
    def passthrough_decorator(*args, **kwargs):
        """Decorador que no hace nada, solo pasa la función."""
        def decorator(f):
            return f
        return decorator
    
    # Mockear el decorador en todos los lugares donde se usa
    # Nota: catalogos_routes no usa token_required, así que no lo parcheamos
    with patch('src.routes.deportistas_routes.token_required', side_effect=passthrough_decorator):
        with patch('src.routes.eventos_routes.token_required', side_effect=passthrough_decorator):
            with patch('src.routes.auth_routes.token_required', side_effect=passthrough_decorator):
                # catalogos_routes no usa token_required, así que no intentamos parchearlo
                yield


@pytest.fixture
def mock_logger():
    """Mock para el logger para evitar logs en tests."""
    with patch('src.utils.logger.obtener_registrador') as mock:
        logger = MagicMock()
        mock.return_value = logger
        yield logger


# ============================================================================
# HELPERS Y UTILIDADES
# ============================================================================

def assert_json_response(response, expected_status: int = 200, has_success: bool = True):
    """
    Helper para validar respuestas JSON.
    
    Args:
        response: Respuesta del cliente de Flask
        expected_status: Código de estado HTTP esperado
        has_success: Si la respuesta debe tener success=True
    """
    assert response.status_code == expected_status
    assert response.is_json
    
    data = response.get_json()
    assert 'success' in data
    
    if has_success:
        assert data['success'] is True
    else:
        assert data['success'] is False
    
    return data


def create_auth_token(user_id: int, username: str) -> str:
    """
    Crea un token JWT de prueba.
    
    Args:
        user_id: ID del usuario
        username: Nombre de usuario
    
    Returns:
        Token JWT como string
    """
    import jwt
    from datetime import datetime, timedelta, timezone
    
    payload = {
        'usuario_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc)
    }
    
    # Usar una clave secreta de prueba
    secret = os.getenv('JWT_SECRET_KEY', 'test_secret_key')
    return jwt.encode(payload, secret, algorithm='HS256')

