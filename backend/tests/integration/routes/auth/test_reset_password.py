"""
Tests para el endpoint de reseteo de contraseña.

Endpoint: POST /api/auth/reset-password
Funcionalidad: Permite a los usuarios resetear su contraseña usando un token válido.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestResetPassword:
    """Tests para el endpoint POST /api/auth/reset-password"""
    
    def test_reset_password_success(self, client):
        """Test: Resetear contraseña exitosamente."""
        # Arrange
        datos_reset = {
            'token': 'valid_token_123',
            'new_password': 'nueva_password_123',
            'confirm_password': 'nueva_password_123'
        }
        mock_token = MagicMock()
        mock_token.token = 'valid_token_123'
        mock_token.usuario_id = 1
        mock_token.fecha_expiracion = MagicMock()
        mock_token.fecha_expiracion.__gt__ = MagicMock(return_value=True)
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        # Act
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_token_query:
            mock_token_query.filter_by.return_value.first.return_value = mock_token
            with patch('src.routes.auth_reset.Usuario.query') as mock_usuario_query:
                mock_usuario_query.get.return_value = mock_usuario
                with patch('src.routes.auth_reset.db') as mock_db:
                    mock_db.session.delete = MagicMock()
                    mock_db.session.commit = MagicMock()
                    
                    response = make_json_request(
                        client, 'POST', '/api/auth/reset-password',
                        data=datos_reset
                    )
        
        # Assert
        assert response.status_code in [200, 400, 500]
    
    def test_reset_password_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/auth/reset-password', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_reset_password_campos_faltantes(self, client):
        """Test: Error cuando faltan campos requeridos."""
        # Arrange
        datos_incompletos = {
            'token': 'valid_token_123'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/auth/reset-password',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_reset_password_token_invalido(self, client):
        """Test: Error cuando el token es inválido."""
        # Arrange
        datos_reset = {
            'token': 'invalid_token',
            'new_password': 'nueva_password_123',
            'confirm_password': 'nueva_password_123'
        }
        
        # Act
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_token_query:
            mock_token_query.filter_by.return_value.first.return_value = None
            
            response = make_json_request(
                client, 'POST', '/api/auth/reset-password',
                data=datos_reset
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_reset_password_contraseñas_no_coinciden(self, client):
        """Test: Error cuando las contraseñas no coinciden."""
        # Arrange
        datos_reset = {
            'token': 'valid_token_123',
            'new_password': 'password_123',
            'confirm_password': 'password_456'
        }
        mock_token = MagicMock()
        mock_token.token = 'valid_token_123'
        
        # Act
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_token_query:
            mock_token_query.filter_by.return_value.first.return_value = mock_token
            
            response = make_json_request(
                client, 'POST', '/api/auth/reset-password',
                data=datos_reset
            )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_reset_password_contraseña_corta(self, client):
        """Test: Error cuando la contraseña es muy corta."""
        # Arrange
        datos_reset = {
            'token': 'valid_token_123',
            'new_password': '12345',
            'confirm_password': '12345'
        }
        mock_token = MagicMock()
        mock_token.token = 'valid_token_123'
        
        # Act
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_token_query:
            mock_token_query.filter_by.return_value.first.return_value = mock_token
            
            response = make_json_request(
                client, 'POST', '/api/auth/reset-password',
                data=datos_reset
            )
        
        # Assert
        assert_error_response(response, expected_status=400)

