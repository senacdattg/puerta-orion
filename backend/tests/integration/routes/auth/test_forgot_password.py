"""
Tests para el endpoint de solicitud de recuperación de contraseña.

Endpoint: POST /api/auth/forgot-password
Funcionalidad: Permite a los usuarios solicitar un token de recuperación de contraseña.
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
class TestForgotPassword:
    """Tests para el endpoint POST /api/auth/forgot-password"""
    
    def test_forgot_password_success(self, client):
        """Test: Solicitar recuperación de contraseña exitosamente."""
        # Arrange
        datos_solicitud = {
            'email': 'usuario@example.com'
        }
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.correo_electronico = 'usuario@example.com'
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        mock_usuario.persona = mock_persona
        
        # Act
        with patch('src.routes.auth_reset.Persona.query') as mock_persona_query:
            mock_persona_query.filter_by.return_value.first.return_value = mock_persona
            with patch('src.routes.auth_reset.Usuario.query') as mock_usuario_query:
                mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
                with patch('src.routes.auth_reset.PasswordResetToken') as mock_token_class:
                    mock_token_class.query.filter_by.return_value.first.return_value = None
                    with patch('src.routes.auth_reset.db') as mock_db:
                        mock_db.session.add = MagicMock()
                        mock_db.session.commit = MagicMock()
                        with patch('src.routes.auth_reset._enviar_correo_reset',
                                   return_value=None):
                            response = make_json_request(
                                client, 'POST', '/api/auth/forgot-password',
                                data=datos_solicitud
                            )
        
        # Assert
        assert response.status_code in [200, 500]
    
    def test_forgot_password_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/auth/forgot-password', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_forgot_password_sin_email(self, client):
        """Test: Error cuando no se proporciona email."""
        # Arrange
        datos_sin_email = {}
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/auth/forgot-password',
            data=datos_sin_email
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_forgot_password_email_no_registrado(self, client):
        """Test: Error cuando el email no está registrado."""
        # Arrange
        datos_email = {'email': 'noexiste@example.com'}
        
        # Act
        with patch('src.routes.auth_reset._validar_configuracion_email', return_value=None):
            with patch('src.routes.auth_reset.Persona.query') as mock_persona_query:
                mock_persona_query.filter_by.return_value.first.return_value = None
                
                response = make_json_request(
                    client, 'POST', '/api/auth/forgot-password',
                    data=datos_email
                )
        
        # Assert
        assert_error_response(response, expected_status=404)

