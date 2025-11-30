"""
Tests unitarios para auth_decorator.

Cubre decoradores, validación de tokens, verificación de roles y permisos.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import jwt

from flask import Flask, request, g
from src.middleware.auth_decorator import (
    TokenRequired,
    token_required,
    permission_required,
    admin_required,
    user_required,
    has_role,
    has_permission,
    get_current_user,
    check_permission,
    get_user_permissions,
    TokenRequiredError,
)


@pytest.mark.unit
class TestAuthDecorator:
    """Tests para decoradores de autenticación"""
    
    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'  # nosonar: S2068, S6418
        app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'  # nosonar: S2068, S6418
        return app
    
    @pytest.fixture
    def mock_usuario(self):
        """Fixture para usuario mock."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.usuario = 'testuser'
        usuario.estado = True
        usuario.roles = []
        usuario.rol_activo = None
        usuario.persona = None
        return usuario
    
    @pytest.fixture
    def mock_sesion(self):
        """Fixture para sesión mock."""
        sesion = MagicMock()
        sesion.id_sesion = 1
        sesion.id_usuario = 1
        sesion.estado = True
        sesion.fecha_inicio = datetime.now(timezone.utc)
        sesion.fecha_expiracion = datetime.now(timezone.utc) + timedelta(hours=1)
        sesion.ip_origen = '127.0.0.1'
        return sesion
    
    def test_token_required_init(self):
        """Test: Inicialización de TokenRequired."""
        decorator = TokenRequired(
            required_roles=['admin'],
            required_permissions=['ver_usuario']
        )
        assert decorator.required_roles == ['admin']
        assert decorator.required_permissions == ['ver_usuario']
    
    def test_extraer_token_valid(self, app):
        """Test: Extraer token válido del header."""
        with app.test_request_context('/test', headers={'Authorization': 'Bearer valid_token_123'}):
            decorator = TokenRequired()
            token = decorator._extraer_token()
            assert token == 'valid_token_123'
    
    def test_extraer_token_no_header(self, app):
        """Test: No hay token en el header."""
        with app.test_request_context('/test'):
            decorator = TokenRequired()
            token = decorator._extraer_token()
            assert token is None
    
    def test_extraer_token_invalid_format(self, app):
        """Test: Formato de token inválido."""
        with app.test_request_context('/test', headers={'Authorization': 'InvalidFormat token'}):
            decorator = TokenRequired()
            token = decorator._extraer_token()
            assert token is None
    
    def test_validar_token_jwt_success(self, app):
        """Test: Validar token JWT exitosamente."""
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1, 'username': 'testuser'}
            
            with patch('src.middleware.auth_decorator.auth_service') as mock_service:
                mock_service.verificar_token_jwt.return_value = payload
                
                result = decorator._validar_token_jwt('valid_token')
                assert result == payload
    
    def test_validar_token_jwt_failure(self, app):
        """Test: Validar token JWT falla."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.auth_service') as mock_service:
                mock_service.verificar_token_jwt.side_effect = Exception('Token inválido')
                
                result = decorator._validar_token_jwt('invalid_token')
                assert result is None
    
    def test_verificar_sesion_activa_success(self, app, mock_sesion):
        """Test: Verificar sesión activa exitosamente."""
        from src.models.eventos.sesionAuth import SesionAuth
        
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            
            with patch('src.middleware.auth_decorator.SesionAuth.query') as mock_query:
                mock_query.filter_by.return_value.filter.return_value.first.return_value = mock_sesion
                
                result = decorator._verificar_sesion_activa(payload)
                assert result == mock_sesion
    
    def test_verificar_sesion_activa_expired(self, app):
        """Test: Sesión expirada."""
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            
            with patch('src.middleware.auth_decorator.SesionAuth.query') as mock_query:
                mock_query.filter_by.return_value.filter.return_value.first.return_value = None
                
                result = decorator._verificar_sesion_activa(payload)
                assert result is None
    
    def test_obtener_usuario_completo_success(self, app, mock_usuario):
        """Test: Obtener usuario completo exitosamente."""
        from src.models.usuarios.usuario import Usuario
        
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                mock_query.filter_by.return_value.first.return_value = mock_usuario
                
                result = decorator._obtener_usuario_completo(1)
                assert result == mock_usuario
    
    def test_obtener_usuario_completo_not_found(self, app):
        """Test: Usuario no encontrado."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                mock_query.filter_by.return_value.first.return_value = None
                
                result = decorator._obtener_usuario_completo(999)
                assert result is None
    
    def test_verificar_roles_success(self, app, mock_usuario):
        """Test: Verificar roles exitosamente."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.roles = [mock_rol]
        
        with app.test_request_context():
            decorator = TokenRequired(required_roles=['admin'])
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is True
    
    def test_verificar_roles_failure(self, app, mock_usuario):
        """Test: Usuario no tiene roles requeridos."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'user'
        mock_usuario.roles = [mock_rol]
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is False
    
    def test_verificar_roles_case_insensitive(self, app, mock_usuario):
        """Test: Verificación de roles case-insensitive."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Admin'
        mock_usuario.roles = [mock_rol]
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is True
    
    def test_verificar_rol_activo_success(self, app, mock_usuario):
        """Test: Verificar rol activo exitosamente."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol_activo = mock_rol
        
        with app.test_request_context():
            decorator = TokenRequired(required_active_roles=['admin'])
            result = decorator._verificar_rol_activo(mock_usuario, ['admin'])
            assert result is True
    
    def test_verificar_rol_activo_failure(self, app, mock_usuario):
        """Test: Rol activo no coincide."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'user'
        mock_usuario.rol_activo = mock_rol
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_rol_activo(mock_usuario, ['admin'])
            assert result is False
    
    def test_verificar_permisos_success(self, app, mock_usuario):
        """Test: Verificar permisos exitosamente."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.check_permission', return_value=True):
                result = decorator._verificar_permisos(mock_usuario, ['ver_usuario'])
                assert result is True
    
    def test_verificar_permisos_failure(self, app, mock_usuario):
        """Test: Usuario no tiene permisos requeridos."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.check_permission', return_value=False):
                result = decorator._verificar_permisos(mock_usuario, ['ver_usuario'])
                assert result is False
    
    def test_check_permission_success(self, app, mock_usuario):
        """Test: Verificar permiso exitosamente."""
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        mock_rol = MagicMock()
        mock_rol.id_rol = 1
        mock_rol.nombre_rol = 'admin'
        mock_usuario.roles = [mock_rol]
        
        mock_permiso = MagicMock()
        mock_permiso.id_permiso = 1
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.Permiso.query') as mock_permiso_query:
                mock_permiso_query.filter_by.return_value.first.return_value = mock_permiso
                with patch('src.middleware.auth_decorator.RolPermiso.query') as mock_rol_permiso:
                    mock_rol_permiso.filter_by.return_value.first.return_value = MagicMock()
                    
                    result = check_permission(mock_usuario, 'ver_usuario')
                    assert result is True
    
    def test_check_permission_no_permiso(self, app, mock_usuario):
        """Test: Permiso no existe."""
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.Permiso.query') as mock_permiso_query:
                mock_permiso_query.filter_by.return_value.first.return_value = None
                
                result = check_permission(mock_usuario, 'permiso_inexistente')
                assert result is False
    
    def test_get_user_permissions_success(self, app, mock_usuario):
        """Test: Obtener permisos del usuario exitosamente."""
        mock_rol = MagicMock()
        mock_permiso = MagicMock()
        mock_permiso.nombre = 'ver_usuario'
        mock_rol.permisos = [mock_permiso]
        mock_usuario.roles = [mock_rol]
        
        with app.test_request_context():
            result = get_user_permissions(mock_usuario)
            assert 'ver_usuario' in result
    
    def test_get_user_permissions_no_roles(self, app, mock_usuario):
        """Test: Usuario sin roles."""
        mock_usuario.roles = []
        
        with app.test_request_context():
            result = get_user_permissions(mock_usuario)
            assert result == []
    
    def test_has_role_success(self, app):
        """Test: Verificar si usuario tiene rol."""
        with app.test_request_context():
            g.current_user = {
                'roles': [{'nombre_rol': 'admin'}]
            }
            
            result = has_role('admin')
            assert result is True
    
    def test_has_role_failure(self, app):
        """Test: Usuario no tiene rol."""
        with app.test_request_context():
            g.current_user = {
                'roles': [{'nombre_rol': 'user'}]
            }
            
            result = has_role('admin')
            assert result is False
    
    def test_has_permission_success(self, app):
        """Test: Verificar si usuario tiene permiso."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        with app.test_request_context():
            g.current_user = {'id_usuario': 1}
            
            with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                mock_query.get.return_value = mock_usuario
                with patch('src.middleware.auth_decorator.check_permission', return_value=True):
                    result = has_permission('ver_usuario')
                    assert result is True
    
    def test_get_current_user(self, app):
        """Test: Obtener usuario actual del contexto."""
        with app.test_request_context():
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            
            result = get_current_user()
            assert result == g.current_user
    
    def test_decorator_no_token(self, app):
        """Test: Decorador rechaza request sin token."""
        @token_required()
        def protected_route():
            return {'success': True}
        
        with app.test_request_context('/test'):
            response, status = protected_route()
            assert status == 401
            assert response.json['success'] is False
    
    def test_admin_required_decorator(self, app):
        """Test: Decorador admin_required."""
        @admin_required
        def admin_route():
            return {'success': True}
        
        # Verificar que es una función decorada
        assert callable(admin_route)
    
    def test_permission_required_decorator(self, app):
        """Test: Decorador permission_required."""
        decorator = permission_required('ver_usuario')
        assert callable(decorator)
    
    def test_error_response(self, app):
        """Test: Generar respuesta de error."""
        with app.test_request_context():
            decorator = TokenRequired()
            response, status = decorator._error_response('Test error', 400)
            
            assert status == 400
            assert response.json['success'] is False
            assert response.json['error'] == 'Test error'

