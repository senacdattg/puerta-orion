"""
Tests para el endpoint de cambio de rol de usuario.

Endpoint: PUT /api/usuarios/<id_usuario>/rol
Funcionalidad: Cambia el rol activo de un usuario.
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
class TestCambiarRolUsuario:
    """Tests para el endpoint PUT /api/usuarios/<id_usuario>/rol"""
    
    def test_cambiar_rol_usuario_success(self, client, mock_token_required):
        """Test: Cambiar rol de usuario exitosamente."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.roles = []
        
        mock_rol = MagicMock()
        mock_rol.id_rol = 2
        mock_rol.nombre_rol = 'Entrenador'
        mock_rol.descripcion = 'Rol de entrenador'
        
        datos_rol = {
            'id_rol': 2
        }
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.routes.usuarios_routes.Rol.query') as mock_rol_query:
                mock_rol_query.filter_by.return_value.first.return_value = mock_rol
                with patch('src.routes.usuarios_routes._filtrar_roles_gestionables',
                           return_value=[mock_rol]):
                    with patch('src.routes.usuarios_routes._actualizar_roles_gestionables'):
                        mock_usuario.roles = [mock_rol]
                        mock_query.filter_by.return_value.first.return_value = mock_usuario
                        
                        response = make_json_request(
                            client, 'PUT', '/api/usuarios/1/rol',
                            data=datos_rol
                        )
        
        # Assert
        assert_success_response(response)
    
    def test_cambiar_rol_usuario_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.put('/api/usuarios/1/rol', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_cambiar_rol_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Error cuando el usuario no existe."""
        # Arrange
        datos_rol = {'id_rol': 2}
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/usuarios/999/rol',
                data=datos_rol
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_cambiar_rol_usuario_sin_roles(self, client, mock_token_required):
        """Test: Error cuando no se proporcionan roles."""
        # Arrange
        datos_vacios = {}
        
        # Act
        response = make_json_request(
            client, 'PUT', '/api/usuarios/1/rol',
            data=datos_vacios
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

