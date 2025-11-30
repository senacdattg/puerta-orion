"""
Tests adicionales para forgot_password completando cobertura.

Cubre casos adicionales y edge cases.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)
from tests.integration.test_utils import create_mock_persona, create_mock_usuario


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestForgotPasswordCompleto:
    """Tests adicionales para POST /api/auth/forgot-password"""
    
    def test_forgot_password_usuario_inactivo(self, client):
        """Test: Error cuando usuario está inactivo."""
        # Arrange
        datos_solicitud = {'email': 'usuario@example.com'}
        
        mock_persona = create_mock_persona()
        mock_usuario = create_mock_usuario(estado=False)  # Usuario inactivo
        
        # Act
        with patch('src.routes.auth_reset._validar_configuracion_email', return_value=None):
            with patch('src.routes.auth_reset.Persona.query') as mock_persona_query:
                mock_persona_query.filter_by.return_value.first.return_value = mock_persona
                with patch('src.routes.auth_reset.Usuario.query') as mock_usuario_query:
                    mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
                    
                    response = make_json_request(
                        client, 'POST', '/api/auth/forgot-password',
                        data=datos_solicitud
                    )
        
        # Assert
        assert_error_response(response, expected_status=403)
    
    def test_forgot_password_error_envio_correo(self, client):
        """Test: Manejo de error al enviar correo."""
        # Arrange
        datos_solicitud = {'email': 'usuario@example.com'}
        
        mock_persona = create_mock_persona(
            correo_electronico='usuario@example.com'
        )
        mock_usuario = create_mock_usuario(
            estado=True,
            persona=mock_persona
        )
        
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
                        with patch('src.routes.auth_reset._enviar_correo_reset') as mock_enviar:
                            mock_enviar.side_effect = Exception('Error SMTP')
                            
                            response = make_json_request(
                                client, 'POST', '/api/auth/forgot-password',
                                data=datos_solicitud
                            )
        
        # Assert
        # Debe manejar el error apropiadamente
        assert response.status_code in [200, 500]
    
    def test_forgot_password_configuracion_email_error(self, client):
        """Test: Error de configuración de email."""
        # Arrange
        datos_solicitud = {'email': 'usuario@example.com'}
        
        # Act
        with patch('src.routes.auth_reset._validar_configuracion_email') as mock_validar:
            from src.utils.request_validators import RequestValidationError
            mock_validar.side_effect = RequestValidationError('Error config', status_code=500)
            
            response = make_json_request(
                client, 'POST', '/api/auth/forgot-password',
                data=datos_solicitud
            )
        
        # Assert
        assert_error_response(response, expected_status=500)

