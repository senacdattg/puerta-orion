"""
Tests para el endpoint de actualización de usuario.

Endpoint: PUT /api/usuarios/<id_usuario>
Funcionalidad: Actualiza los datos de un usuario existente.
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
@pytest.mark.usuarios
class TestActualizarUsuario:
    """Tests para el endpoint PUT /api/usuarios/<id_usuario>"""
    
    def test_actualizar_usuario_success(self, client, mock_token_required):
        """Test: Actualizar usuario exitosamente."""
        # Arrange
        datos_actualizacion = {
            'datos_persona': {
                'primer_nombre': 'Juan',
                'telefono': '3001234567'
            }
        }
        mock_resultado = {
            'success': True,
            'message': 'Usuario actualizado exitosamente',
            'data': {'id_usuario': 1},
            'status_code': 200
        }
        
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.actualizar_usuario',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'PUT', '/api/usuarios/1',
                data=datos_actualizacion
            )
        
        # Assert
        assert_success_response(response)
    
    def test_actualizar_usuario_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.put('/api/usuarios/1', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_actualizar_usuario_datos_vacios(self, client, mock_token_required):
        """Test: Error cuando no se proporcionan datos."""
        # Arrange
        datos_vacios = {}
        
        # Act
        response = make_json_request(
            client, 'PUT', '/api/usuarios/1',
            data=datos_vacios
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_actualizar_usuario_con_password(self, client, mock_token_required):
        """Test: Error al intentar actualizar password desde este endpoint."""
        # Arrange
        datos_con_password = {
            'datos_usuario': {
                'password': 'nueva_password'
            }
        }
        
        # Act
        response = make_json_request(
            client, 'PUT', '/api/usuarios/1',
            data=datos_con_password
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_actualizar_usuario_error_servicio(self, client, mock_token_required):
        """Test: Error del servicio al actualizar usuario."""
        # Arrange
        from src.services.Auth.usuario_service import UsuarioServiceError
        datos_actualizacion = {
            'datos_persona': {'primer_nombre': 'Juan'}
        }
        
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.actualizar_usuario',
                   side_effect=UsuarioServiceError('Error de servicio')):
            response = make_json_request(
                client, 'PUT', '/api/usuarios/1',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=400)

