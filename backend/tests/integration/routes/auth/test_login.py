"""
Tests para el endpoint de login.

Endpoint: POST /api/auth/login
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestLogin:
    """Tests para el endpoint POST /api/auth/login"""
    
    def test_login_success(self, client):
        """Test: Login exitoso."""
        # Arrange
        from tests.helpers.test_config import TEST_USERNAME, TEST_PASSWORD
        
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
        from tests.helpers.test_config import TEST_USERNAME, TEST_PASSWORD_INCORRECTA
        
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

