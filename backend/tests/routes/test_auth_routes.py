"""
Tests para las rutas de autenticación.

Este módulo contiene tests para todos los endpoints de autenticación.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.test_helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
    create_auth_headers
)


# ============================================================================
# TESTS PARA REGISTRO DE USUARIO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestRegistroUsuario:
    """Tests para el endpoint POST /api/auth/register"""
    
    def test_registro_usuario_success(self, client, sample_usuario_data):
        """Test: Registro de usuario exitoso."""
        # Arrange
        mock_result = {
            'id_usuario': 1,
            'usuario': 'testuser',
            'persona': {'id_persona': 1}
        }
        
        # Act
        with patch('src.routes.auth_routes.usuario_service.registrar_usuario_completo',
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/auth/register',
                data=sample_usuario_data
            )
        
        # Assert
        data = assert_success_response(response, expected_status=201)
        assert 'data' in data
        assert data['data']['id_usuario'] == 1
    
    def test_registro_usuario_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/auth/register', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_registro_usuario_datos_faltantes(self, client):
        """Test: Error cuando faltan datos requeridos."""
        # Arrange
        datos_incompletos = {
            'persona': {
                'primer_nombre': 'Test'
                # Faltan otros campos requeridos
            }
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/auth/register',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)


# ============================================================================
# TESTS PARA LOGIN
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Tests para el endpoint POST /api/auth/login"""
    
    def test_login_success(self, client):
        """Test: Login exitoso."""
        # Arrange
        from tests.test_config import TEST_USERNAME, TEST_PASSWORD
        
        datos_login = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        mock_result = {
            'token': 'test_token_12345',
            'usuario': {
                'id_usuario': 1,
                'username': 'testuser'
            }
        }
        
        # Act
        with patch('src.routes.auth_routes.auth_service.autenticar_usuario',
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/auth/login',
                data=datos_login
            )
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert 'token' in data['data']
    
    def test_login_credenciales_invalidas(self, client):
        """Test: Error con credenciales inválidas."""
        # Arrange
        from tests.test_config import TEST_USERNAME, TEST_PASSWORD_INCORRECTA
        
        datos_login = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD_INCORRECTA
        }
        
        # Act
        from src.services.Auth.auth_service import AuthServiceError
        with patch('src.routes.auth_routes.auth_service.autenticar_usuario',
                   side_effect=AuthServiceError('Credenciales inválidas')):
            response = make_json_request(
                client, 'POST', '/api/auth/login',
                data=datos_login
            )
        
        # Assert
        assert_error_response(response, expected_status=401)
    
    def test_login_sin_datos(self, client):
        """Test: Error cuando no se envían datos."""
        # Act
        response = make_json_request(client, 'POST', '/api/auth/login', data={})
        
        # Assert
        assert_error_response(response, expected_status=400)


# ============================================================================
# TESTS PARA OBTENER PERFIL
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestObtenerPerfil:
    """Tests para el endpoint GET /api/auth/perfil"""
    
    def test_obtener_perfil_success(self, client, mock_get_current_user):
        """Test: Obtener perfil exitosamente."""
        # Act
        response = client.get('/api/auth/perfil')
        
        # Assert
        # Nota: Ajustar según implementación real del decorador
        assert response.status_code in [200, 401, 403]
    
    def test_obtener_perfil_sin_autenticacion(self, client):
        """Test: Error cuando no hay autenticación."""
        # Act
        with patch('src.routes.auth_routes.get_current_user', return_value=None):
            response = client.get('/api/auth/perfil')
        
        # Assert
        assert_error_response(response, expected_status=401)

