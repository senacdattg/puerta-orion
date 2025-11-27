"""
Tests para el endpoint de cambio de estado de usuario.

Endpoint: PUT /api/usuarios/<id_usuario>/estado
Funcionalidad: Activa o desactiva un usuario del sistema.
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
class TestCambiarEstadoUsuario:
    """Tests para el endpoint PUT /api/usuarios/<id_usuario>/estado"""
    
    def test_cambiar_estado_usuario_activar_success(self, client, mock_token_required):
        """Test: Activar usuario exitosamente."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = False
        mock_usuario.roles = []
        
        datos_estado = {
            'estado': True
        }
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.routes.usuarios_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/usuarios/1/estado',
                    data=datos_estado
                )
        
        # Assert
        assert_success_response(response)
    
    def test_cambiar_estado_usuario_desactivar_success(self, client, mock_token_required):
        """Test: Desactivar usuario exitosamente."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = True
        mock_usuario.roles = []
        
        datos_estado = {
            'estado': False
        }
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.routes.usuarios_routes.get_current_user',
                       return_value={'id_usuario': 2}):
                with patch('src.routes.usuarios_routes.db') as mock_db:
                    mock_db.session.commit = MagicMock()
                    
                    response = make_json_request(
                        client, 'PUT', '/api/usuarios/1/estado',
                        data=datos_estado
                    )
        
        # Assert
        assert_success_response(response)
    
    def test_cambiar_estado_usuario_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.put('/api/usuarios/1/estado', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_cambiar_estado_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Error cuando el usuario no existe."""
        # Arrange
        datos_estado = {'estado': True}
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/usuarios/999/estado',
                data=datos_estado
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_cambiar_estado_usuario_sin_campo_estado(self, client, mock_token_required):
        """Test: Error cuando no se proporciona el campo estado."""
        # Arrange
        datos_sin_estado = {}
        
        # Act
        response = make_json_request(
            client, 'PUT', '/api/usuarios/1/estado',
            data=datos_sin_estado
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_cambiar_estado_propio_usuario(self, client, mock_token_required):
        """Test: Error al intentar desactivar el propio usuario."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = True
        
        datos_estado = {
            'estado': False
        }
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.routes.usuarios_routes.get_current_user',
                       return_value={'id_usuario': 1}):
                response = make_json_request(
                    client, 'PUT', '/api/usuarios/1/estado',
                    data=datos_estado
                )
        
        # Assert
        assert_error_response(response, expected_status=400)

