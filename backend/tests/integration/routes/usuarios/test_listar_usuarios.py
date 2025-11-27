"""
Tests para el endpoint de listado de usuarios.

Endpoint: GET /api/usuarios
Funcionalidad: Lista todos los usuarios con opciones de paginación y filtrado.
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
class TestListarUsuarios:
    """Tests para el endpoint GET /api/usuarios"""
    
    def test_listar_usuarios_success(self, client, mock_token_required):
        """Test: Listar usuarios exitosamente."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = True
        mock_usuario.roles = []
        mock_usuario.persona = MagicMock()
        mock_usuario.persona.id_persona = 1
        mock_usuario.persona.nombre_completo = 'Test User'
        mock_usuario.persona.primer_nombre = 'Test'
        mock_usuario.persona.primer_apellido = 'User'
        mock_usuario.persona.correo_electronico = 'test@example.com'
        mock_usuario.persona.documento = 12345678
        mock_usuario.persona.telefono = '3001234567'
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value = mock_query
            mock_query.count.return_value = 1
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_usuario]
            
            response = client.get('/api/usuarios/')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
    
    def test_listar_usuarios_con_paginacion(self, client, mock_token_required):
        """Test: Listar usuarios con parámetros de paginación."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = True
        mock_usuario.roles = []
        mock_usuario.persona = MagicMock()
        mock_usuario.persona.id_persona = 1
        mock_usuario.persona.nombre_completo = 'Test User'
        mock_usuario.persona.primer_nombre = 'Test'
        mock_usuario.persona.primer_apellido = 'User'
        mock_usuario.persona.correo_electronico = 'test@example.com'
        mock_usuario.persona.documento = 12345678
        mock_usuario.persona.telefono = '3001234567'
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value = mock_query
            mock_query.count.return_value = 10
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_usuario]
            
            response = client.get('/api/usuarios/?limit=5&offset=0')
        
        # Assert
        data = assert_success_response(response)
        assert data['limit'] == 5
        assert data['offset'] == 0
    
    def test_listar_usuarios_filtro_activo(self, client, mock_token_required):
        """Test: Listar solo usuarios activos."""
        # Arrange
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.usuario = 'testuser'
        mock_usuario.estado = True
        mock_usuario.roles = []
        mock_usuario.persona = MagicMock()
        mock_usuario.persona.id_persona = 1
        mock_usuario.persona.nombre_completo = 'Test User'
        mock_usuario.persona.primer_nombre = 'Test'
        mock_usuario.persona.primer_apellido = 'User'
        mock_usuario.persona.correo_electronico = 'test@example.com'
        mock_usuario.persona.documento = 12345678
        mock_usuario.persona.telefono = '3001234567'
        
        # Act
        with patch('src.routes.usuarios_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value = mock_query
            mock_query.count.return_value = 1
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_usuario]
            
            response = client.get('/api/usuarios/?estado=activo')
        
        # Assert
        assert_success_response(response)

