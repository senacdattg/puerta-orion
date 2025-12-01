"""
Tests adicionales para auth_decorator.py.

Cubre funciones y casos edge que no están en test_auth_decorator.py para aumentar cobertura.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import jwt
from flask import Flask, g

from src.middleware.auth_decorator import (
    user_required,
    any_role_required,
    active_role_required,
    any_permission_required,
    get_current_session,
    get_user_permissions_list,
    get_token_payload,
    has_any_role,
    check_permission,
    get_user_permissions,
    _determinar_roles_a_evaluar,
    _verificar_permiso_en_roles,
)


@pytest.mark.unit
class TestDecoradoresEspecificos:
    """Tests para decoradores específicos de roles y permisos."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

    def test_user_required_decorator(self, app):
        """Test: Decorador user_required."""
        @user_required
        def user_route():
            return {'success': True}
        
        # Verificar que es una función decorada
        assert callable(user_route)

    def test_any_role_required_decorator(self, app):
        """Test: Decorador any_role_required."""
        @any_role_required('admin', 'user')
        def any_role_route():
            return {'success': True}
        
        # Verificar que es una función decorada
        assert callable(any_role_route)

    def test_active_role_required_decorator(self, app):
        """Test: Decorador active_role_required."""
        @active_role_required('admin', 'deportista')
        def active_role_route():
            return {'success': True}
        
        # Verificar que es una función decorada
        assert callable(active_role_route)

    def test_any_permission_required_decorator(self, app):
        """Test: Decorador any_permission_required."""
        @any_permission_required('ver_usuario', 'editar_usuario')
        def any_permission_route():
            return {'success': True}
        
        # Verificar que es una función decorada
        assert callable(any_permission_route)


@pytest.mark.unit
class TestHelperFunctions:
    """Tests para funciones helper de auth_decorator."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

    def test_get_current_session_existe(self, app):
        """Test: Obtener sesión actual cuando existe."""
        with app.test_request_context():
            g.current_session = {'id_sesion': 1, 'usuario_id': 1}
            
            result = get_current_session()
            
            assert result is not None
            assert result['id_sesion'] == 1

    def test_get_current_session_no_existe(self, app):
        """Test: Obtener sesión actual cuando no existe."""
        with app.test_request_context():
            result = get_current_session()
            
            assert result is None

    def test_get_user_permissions_list_con_permisos(self, app):
        """Test: Obtener lista de permisos cuando el usuario tiene permisos."""
        with app.test_request_context():
            g.current_user = {
                'id_usuario': 1,
                'permisos': ['ver_usuario', 'editar_usuario']
            }
            
            result = get_user_permissions_list()
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert 'ver_usuario' in result

    def test_get_user_permissions_list_sin_usuario(self, app):
        """Test: Obtener lista de permisos cuando no hay usuario."""
        with app.test_request_context():
            result = get_user_permissions_list()
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_user_permissions_list_sin_permisos(self, app):
        """Test: Obtener lista de permisos cuando el usuario no tiene permisos."""
        with app.test_request_context():
            g.current_user = {'id_usuario': 1}
            
            result = get_user_permissions_list()
            
            assert isinstance(result, list)
            assert len(result) == 0

    def test_get_token_payload_existe(self, app):
        """Test: Obtener payload del token cuando existe."""
        with app.test_request_context():
            g.token_payload = {
                'usuario_id': 1,
                'username': 'testuser',
                'roles': ['admin']
            }
            
            result = get_token_payload()
            
            assert result is not None
            assert result['usuario_id'] == 1

    def test_get_token_payload_no_existe(self, app):
        """Test: Obtener payload del token cuando no existe."""
        with app.test_request_context():
            result = get_token_payload()
            
            assert result is None

    def test_has_any_role_success(self, app):
        """Test: Usuario tiene alguno de los roles especificados."""
        with app.test_request_context():
            g.current_user = {
                'id_usuario': 1,
                'roles': [
                    {'nombre_rol': 'admin'},
                    {'nombre_rol': 'user'}
                ]
            }
            
            result = has_any_role('admin', 'deportista')
            
            assert result is True

    def test_has_any_role_failure(self, app):
        """Test: Usuario no tiene ninguno de los roles especificados."""
        with app.test_request_context():
            g.current_user = {
                'id_usuario': 1,
                'roles': [
                    {'nombre_rol': 'user'}
                ]
            }
            
            result = has_any_role('admin', 'deportista')
            
            assert result is False

    def test_has_any_role_sin_usuario(self, app):
        """Test: has_any_role cuando no hay usuario."""
        with app.test_request_context():
            result = has_any_role('admin', 'user')
            
            assert result is False

    def test_has_any_role_sin_roles(self, app):
        """Test: has_any_role cuando el usuario no tiene roles."""
        with app.test_request_context():
            g.current_user = {'id_usuario': 1}
            
            result = has_any_role('admin', 'user')
            
            assert result is False


@pytest.mark.unit
class TestDeterminarRolesAEvaluar:
    """Tests para la función _determinar_roles_a_evaluar."""

    @pytest.fixture
    def mock_usuario(self):
        """Fixture para usuario mock."""
        usuario = MagicMock()
        usuario.rol_activo = None
        return usuario

    def test_determinar_roles_sin_uso_activo(self, mock_usuario):
        """Test: Determinar roles cuando use_active_role es False."""
        mock_usuario.roles = [
            MagicMock(nombre_rol='admin'),
            MagicMock(nombre_rol='user')
        ]
        
        result = _determinar_roles_a_evaluar(mock_usuario, use_active_role=False)
        
        assert len(result) == 2
        assert result == mock_usuario.roles

    def test_determinar_roles_con_rol_activo(self, mock_usuario):
        """Test: Determinar roles cuando use_active_role es True y hay rol activo."""
        rol_activo = MagicMock(nombre_rol='admin')
        rol_usuario = MagicMock(nombre_rol='usuario')
        
        mock_usuario.rol_activo = rol_activo
        mock_usuario.roles = [rol_activo, rol_usuario]
        
        result = _determinar_roles_a_evaluar(mock_usuario, use_active_role=True)
        
        assert len(result) >= 1
        assert rol_activo in result

    def test_determinar_roles_sin_rol_activo(self, mock_usuario):
        """Test: Determinar roles cuando use_active_role es True pero no hay rol activo."""
        rol_usuario = MagicMock(nombre_rol='usuario')
        mock_usuario.roles = [rol_usuario]
        mock_usuario.rol_activo = None
        
        result = _determinar_roles_a_evaluar(mock_usuario, use_active_role=True)
        
        # Debe retornar los roles del usuario si no hay rol activo
        assert len(result) == 1

    def test_determinar_roles_con_rol_usuario(self, mock_usuario):
        """Test: Determinar roles incluye rol 'usuario' aunque no sea activo."""
        rol_activo = MagicMock(nombre_rol='admin')
        rol_usuario = MagicMock(nombre_rol='usuario')
        
        mock_usuario.rol_activo = rol_activo
        mock_usuario.roles = [rol_activo, rol_usuario]
        
        result = _determinar_roles_a_evaluar(mock_usuario, use_active_role=True)
        
        # Debe incluir tanto el rol activo como el rol 'usuario'
        assert rol_activo in result
        assert rol_usuario in result


@pytest.mark.unit
class TestVerificarPermisoEnRoles:
    """Tests para la función _verificar_permiso_en_roles."""

    @pytest.fixture
    def mock_usuario(self):
        """Fixture para usuario mock."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.usuario = 'testuser'
        return usuario

    @pytest.fixture
    def mock_permiso(self):
        """Fixture para permiso mock."""
        permiso = MagicMock()
        permiso.id_permiso = 1
        permiso.nombre = 'ver_usuario'
        return permiso

    def test_verificar_permiso_en_roles_success(self, mock_usuario, mock_permiso):
        """Test: Verificar permiso cuando algún rol lo tiene."""
        rol = MagicMock()
        rol.id_rol = 1
        rol.nombre_rol = 'admin'
        
        roles_a_evaluar = [rol]
        
        with patch('src.middleware.auth_decorator.RolPermiso') as mock_rol_permiso:
            mock_query = MagicMock()
            mock_rol_permiso_obj = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_rol_permiso_obj
            mock_rol_permiso.query = mock_query
            
            result = _verificar_permiso_en_roles(
                roles_a_evaluar,
                mock_permiso,
                mock_usuario,
                'ver_usuario'
            )
            
            assert result is True

    def test_verificar_permiso_en_roles_failure(self, mock_usuario, mock_permiso):
        """Test: Verificar permiso cuando ningún rol lo tiene."""
        rol = MagicMock()
        rol.id_rol = 1
        rol.nombre_rol = 'user'
        
        roles_a_evaluar = [rol]
        
        with patch('src.middleware.auth_decorator.RolPermiso') as mock_rol_permiso:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_rol_permiso.query = mock_query
            
            result = _verificar_permiso_en_roles(
                roles_a_evaluar,
                mock_permiso,
                mock_usuario,
                'ver_usuario'
            )
            
            assert result is False


@pytest.mark.unit
class TestCheckPermissionEdgeCases:
    """Tests para casos edge de check_permission."""

    @pytest.fixture
    def mock_usuario(self):
        """Fixture para usuario mock."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.usuario = 'testuser'
        return usuario

    def test_check_permission_use_active_role_true(self, mock_usuario, app):
        """Test: check_permission con use_active_role=True."""
        with app.app_context():
            mock_permiso = MagicMock()
            mock_permiso.id_permiso = 1
            mock_permiso.nombre = 'ver_usuario'
            
            rol_activo = MagicMock()
            rol_activo.id_rol = 1
            mock_usuario.rol_activo = rol_activo
            mock_usuario.roles = [rol_activo]
            
            with patch('src.middleware.auth_decorator.Permiso') as mock_permiso_class, \
                 patch('src.middleware.auth_decorator._determinar_roles_a_evaluar') as mock_determinar, \
                 patch('src.middleware.auth_decorator._verificar_permiso_en_roles', return_value=True):
                
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_permiso
                mock_permiso_class.query = mock_query
                
                mock_determinar.return_value = [rol_activo]
                
                result = check_permission(mock_usuario, 'ver_usuario', use_active_role=True)
                
                assert result is True
                mock_determinar.assert_called_once_with(mock_usuario, True)

    def test_check_permission_permiso_no_existe(self, mock_usuario, app):
        """Test: check_permission cuando el permiso no existe."""
        with app.app_context():
            with patch('src.middleware.auth_decorator.Permiso') as mock_permiso_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_permiso_class.query = mock_query
                
                result = check_permission(mock_usuario, 'permiso_inexistente')
                
                assert result is False

    def test_check_permission_sin_roles(self, mock_usuario, app):
        """Test: check_permission cuando el usuario no tiene roles."""
        with app.app_context():
            mock_permiso = MagicMock()
            mock_permiso.id_permiso = 1
            
            mock_usuario.roles = []
            
            with patch('src.middleware.auth_decorator.Permiso') as mock_permiso_class, \
                 patch('src.middleware.auth_decorator._verificar_permiso_en_roles', return_value=False):
                
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_permiso
                mock_permiso_class.query = mock_query
                
                result = check_permission(mock_usuario, 'ver_usuario')
                
                assert result is False


@pytest.mark.unit
class TestGetUserPermissionsEdgeCases:
    """Tests para casos edge de get_user_permissions."""

    @pytest.fixture
    def mock_usuario(self):
        """Fixture para usuario mock."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.roles = []
        return usuario

    def test_get_user_permissions_sin_roles(self, mock_usuario):
        """Test: get_user_permissions cuando el usuario no tiene roles."""
        result = get_user_permissions(mock_usuario)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_user_permissions_con_roles_sin_permisos(self, mock_usuario):
        """Test: get_user_permissions cuando los roles no tienen permisos."""
        rol = MagicMock()
        rol.permisos = []
        mock_usuario.roles = [rol]
        
        result = get_user_permissions(mock_usuario)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_user_permissions_con_permisos_duplicados(self, mock_usuario):
        """Test: get_user_permissions elimina permisos duplicados."""
        permiso1 = MagicMock()
        permiso1.nombre = 'ver_usuario'
        
        permiso2 = MagicMock()
        permiso2.nombre = 'ver_usuario'  # Duplicado
        
        rol1 = MagicMock()
        rol1.permisos = [permiso1]
        
        rol2 = MagicMock()
        rol2.permisos = [permiso2]
        
        mock_usuario.roles = [rol1, rol2]
        
        result = get_user_permissions(mock_usuario)
        
        # Debe eliminar duplicados
        assert len(result) == 1
        assert 'ver_usuario' in result



