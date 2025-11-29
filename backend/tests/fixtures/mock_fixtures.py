"""
Fixtures para mocks y stubs.

Este módulo contiene fixtures que mockean dependencias externas
y servicios para aislar los tests.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.conftest import TEST_PRIMER_NOMBRE, TEST_PRIMER_APELLIDO


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
    # Mock usuario válido para get_current_user
    mock_usuario_data = {
        'id_usuario': 1,
        'username': 'testuser',
        'usuario': 'testuser',
        'persona': {
            'id_persona': 1,
            'nombre_completo': 'Test User',
            'documento': 12345678
        },
        'roles': [
            {'nombre_rol': 'SuperAdmin', 'id_rol': 1},
            {'nombre_rol': 'Administrador', 'id_rol': 2},
            {'nombre_rol': 'Deportista', 'id_rol': 3},
            {'nombre_rol': 'Acudiente', 'id_rol': 4},
            {'nombre_rol': 'usuario', 'id_rol': 5}
        ],
        'rol_activo': {'nombre_rol': 'SuperAdmin', 'id_rol': 1},
        'permisos': []
    }
    
    # Mock de SesionAuth
    mock_sesion = MagicMock()
    mock_sesion.activa = True
    mock_sesion.id_usuario = 1
    
    # Mock de Persona
    mock_persona = MagicMock()
    mock_persona.id_persona = 1
    mock_persona.primer_nombre = 'Test'
    mock_persona.primer_apellido = 'User'
    
    # Mock de Usuario
    mock_usuario = MagicMock()
    mock_usuario.id_usuario = 1
    mock_usuario.usuario = 'testuser'
    mock_usuario.persona = mock_persona
    mock_usuario.roles = [
        MagicMock(nombre_rol='SuperAdmin', id_rol=1),
        MagicMock(nombre_rol='Administrador', id_rol=2),
        MagicMock(nombre_rol='Deportista', id_rol=3),
        MagicMock(nombre_rol='Acudiente', id_rol=4),
        MagicMock(nombre_rol='usuario', id_rol=5)
    ]
    mock_usuario.rol_activo = MagicMock(nombre_rol='SuperAdmin', id_rol=1)
    
    # Mock del payload del token
    mock_payload = {
        'usuario_id': 1,
        'username': 'testuser',
        'exp': 9999999999,
        'iat': 1000000000
    }
    
    # Mockear _inyectar_datos_usuario para configurar g con valores serializables
    def mock_inyectar_datos_usuario(self, usuario, sesion, payload):
        """Mock que configura g con valores serializables, evitando MagicMock."""
        from flask import g
        g.current_user = mock_usuario_data
        g.current_session = {
            'id_sesion': 1,
            'fecha_inicio': '2024-01-01T00:00:00',
            'fecha_expiracion': '2024-12-31T23:59:59',
            'ip_origen': '127.0.0.1'
        }
        g.token_payload = mock_payload
        # No establecer g.current_user_obj para evitar MagicMock
    
    # Hacer patch de get_current_user y métodos de validación
    with patch('src.middleware.auth_decorator.get_current_user', return_value=mock_usuario_data):
        with patch('src.middleware.auth_decorator.TokenRequired._extraer_token', return_value='mock_token'):
            with patch('src.middleware.auth_decorator.TokenRequired._validar_token_jwt', return_value=mock_payload):
                with patch('src.middleware.auth_decorator.TokenRequired._verificar_sesion_activa', return_value=mock_sesion):
                    with patch('src.middleware.auth_decorator.TokenRequired._obtener_usuario_completo', return_value=mock_usuario):
                        with patch('src.middleware.auth_decorator.TokenRequired._verificar_roles', return_value=True):
                            with patch('src.middleware.auth_decorator.TokenRequired._verificar_permisos', return_value=True):
                                with patch('src.middleware.auth_decorator.TokenRequired._verificar_rol_activo', return_value=True):
                                    with patch('src.middleware.auth_decorator.TokenRequired._inyectar_datos_usuario', mock_inyectar_datos_usuario):
                                        with patch('src.middleware.auth_decorator.asegurar_rol_activo_valido', return_value=mock_usuario.rol_activo):
                                            with patch('src.middleware.auth_decorator.obtener_paneles_autorizados', return_value=[]):
                                                with patch('src.middleware.auth_decorator.get_user_permissions', return_value=[]):
                                                    yield


@pytest.fixture
def mock_logger():
    """Mock para el logger para evitar logs en tests."""
    with patch('src.utils.logger.obtener_registrador') as mock:
        logger = MagicMock()
        mock.return_value = logger
        yield logger

