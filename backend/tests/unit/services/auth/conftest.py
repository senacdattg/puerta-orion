"""
Fixtures específicas para tests de servicios de autenticación.

Proporciona contexto de aplicación Flask y mocks necesarios.
"""

import pytest
from unittest.mock import MagicMock, Mock
from flask import Flask


@pytest.fixture
def app_context():
    """Proporciona un contexto de aplicación Flask para los tests."""
    from app import create_app
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    
    with app.app_context():
        yield app


@pytest.fixture
def mock_usuario():
    """Create a mock usuario without spec to avoid Flask-SQLAlchemy issues."""
    usuario = MagicMock()
    usuario.id_usuario = 1
    usuario.usuario = 'testuser'
    usuario.password = 'hashed_password'
    usuario.id_persona = 1
    usuario.estado = True
    usuario.roles = []
    usuario.rol_activo = None
    return usuario


@pytest.fixture
def mock_persona():
    """Create a mock persona without spec to avoid Flask-SQLAlchemy issues."""
    persona = MagicMock()
    persona.id_persona = 1
    persona.nombre_completo = 'Test User'
    persona.correo_electronico = 'test@example.com'
    persona.documento = '12345678'
    return persona


@pytest.fixture
def mock_request_context(app_context):
    """Proporciona un contexto de solicitud Flask."""
    with app_context.test_request_context(
        headers={'X-Forwarded-For': '192.168.1.1', 'User-Agent': 'Mozilla/5.0'}
    ):
        yield

