"""
Tests para las rutas de usuarios.

Este módulo contiene tests para todos los endpoints de gestión de usuarios,
siguiendo las mejores prácticas de testing.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
    create_auth_headers
)


# ============================================================================
# TESTS PARA LISTAR USUARIOS
# ============================================================================

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
            
            response = client.get('/api/usuarios')
        
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
            
            response = client.get('/api/usuarios?limit=5&offset=0')
        
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
            
            response = client.get('/api/usuarios?estado=activo')
        
        # Assert
        assert_success_response(response)


# ============================================================================
# TESTS PARA OBTENER DETALLE DE USUARIO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.usuarios
class TestObtenerDetalleUsuario:
    """Tests para el endpoint GET /api/usuarios/<id_usuario>/detalle"""
    
    def test_obtener_detalle_usuario_success(self, client, mock_token_required):
        """Test: Obtener detalle de usuario exitosamente."""
        # Arrange
        mock_detalle = {
            'id_usuario': 1,
            'usuario': 'testuser',
            'persona': {'id_persona': 1, 'nombre_completo': 'Test User'}
        }
        
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.obtener_detalle_completo_usuario',
                   return_value=mock_detalle):
            response = client.get('/api/usuarios/1/detalle')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert data['data']['id_usuario'] == 1
    
    def test_obtener_detalle_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Usuario no encontrado."""
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.obtener_detalle_completo_usuario',
                   return_value=None):
            response = client.get('/api/usuarios/999/detalle')
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA ACTUALIZAR USUARIO
# ============================================================================

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


# ============================================================================
# TESTS PARA CAMBIAR ROL DE USUARIO
# ============================================================================

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


# ============================================================================
# TESTS PARA CAMBIAR ESTADO DE USUARIO
# ============================================================================

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

