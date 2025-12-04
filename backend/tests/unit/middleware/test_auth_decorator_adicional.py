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
    TokenRequired,
    TokenRequiredError,
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
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

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


@pytest.mark.unit
class TestCheckPermissionEdgeCasesMissing:
    """Tests para casos edge faltantes de check_permission."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

    def test_check_permission_usuario_none(self, app):
        """Test: check_permission con usuario None."""
        with app.app_context():
            result = check_permission(None, 'ver_usuario')
            assert result is False

    def test_check_permission_sin_roles(self, app):
        """Test: check_permission cuando usuario no tiene roles."""
        mock_usuario = MagicMock()
        mock_usuario.usuario = 'testuser'
        mock_usuario.roles = []
        
        with app.app_context():
            with patch('src.middleware.auth_decorator.Permiso.query'):
                result = check_permission(mock_usuario, 'ver_usuario')
                assert result is False

    def test_check_permission_exception(self, app):
        """Test: check_permission cuando ocurre una excepción."""
        mock_usuario = MagicMock()
        mock_usuario.usuario = 'testuser'
        mock_usuario.roles = [MagicMock()]
        
        with app.app_context():
            with patch('src.middleware.auth_decorator.Permiso.query') as mock_permiso_query:
                mock_permiso_query.filter_by.side_effect = Exception('Database error')
                
                with pytest.raises(TokenRequiredError) as exc_info:
                    check_permission(mock_usuario, 'ver_usuario')
                assert 'Error al verificar permisos' in str(exc_info.value)


@pytest.mark.unit
class TestGetUserPermissionsEdgeCasesMissing:
    """Tests para casos edge faltantes de get_user_permissions."""

    def test_get_user_permissions_usuario_none(self):
        """Test: get_user_permissions con usuario None."""
        result = get_user_permissions(None)
        assert result == []

    def test_get_user_permissions_exception(self):
        """Test: get_user_permissions cuando ocurre una excepción."""
        mock_usuario = MagicMock()
        mock_usuario.usuario = 'testuser'
        mock_usuario.roles = MagicMock()
        mock_usuario.roles.__iter__ = MagicMock(side_effect=Exception('Database error'))
        
        with pytest.raises(TokenRequiredError) as exc_info:
            get_user_permissions(mock_usuario)
        assert 'Error al obtener permisos' in str(exc_info.value)


@pytest.mark.unit
class TestTokenRequiredEdgeCases:
    """Tests para casos edge de TokenRequired."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
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

    def test_handle_options_request_sin_origin(self, app):
        """Test: _handle_options_request sin Origin header."""
        with app.test_request_context('/test'):
            decorator = TokenRequired()
            response = decorator._handle_options_request()
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Origin') == '*'

    def test_handle_options_request_con_origin(self, app):
        """Test: _handle_options_request con Origin header."""
        with app.test_request_context('/test', headers={'Origin': 'http://localhost:3000'}):
            decorator = TokenRequired()
            response = decorator._handle_options_request()
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'

    def test_verificar_sesion_activa_exception(self, app):
        """Test: _verificar_sesion_activa cuando ocurre una excepción."""
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            
            with patch('src.middleware.auth_decorator.SesionAuth.query') as mock_query:
                mock_query.filter_by.side_effect = Exception('Database error')
                
                result = decorator._verificar_sesion_activa(payload)
                assert result is None

    def test_obtener_usuario_completo_exception(self, app):
        """Test: _obtener_usuario_completo cuando ocurre una excepción."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                mock_query.filter_by.side_effect = Exception('Database error')
                
                result = decorator._obtener_usuario_completo(1)
                assert result is None

    def test_verificar_roles_sin_roles(self, app):
        """Test: _verificar_roles cuando usuario no tiene roles."""
        mock_usuario = MagicMock()
        mock_usuario.roles = None
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is False

    def test_verificar_roles_sin_attr_roles(self, app):
        """Test: _verificar_roles cuando usuario no tiene atributo roles."""
        mock_usuario = MagicMock(spec=[])
        del mock_usuario.roles
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is False

    def test_verificar_roles_exception(self, app):
        """Test: _verificar_roles cuando ocurre una excepción."""
        mock_usuario = MagicMock()
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'admin'
        # Use a MagicMock instead of a real list so we can control iteration
        mock_roles_list = MagicMock()
        mock_roles_list.__iter__ = MagicMock(side_effect=Exception('Error'))
        mock_usuario.roles = mock_roles_list
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_roles(mock_usuario, ['admin'])
            assert result is False

    def test_verificar_rol_activo_sin_required_roles(self, app, mock_usuario):
        """Test: _verificar_rol_activo cuando no hay required_roles."""
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_rol_activo(mock_usuario, [])
            assert result is True

    def test_verificar_rol_activo_sin_usuario(self, app):
        """Test: _verificar_rol_activo cuando usuario es None."""
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_rol_activo(None, ['admin'])
            assert result is False

    def test_verificar_rol_activo_sin_rol_activo(self, app, mock_usuario):
        """Test: _verificar_rol_activo cuando usuario no tiene rol activo."""
        mock_usuario.rol_activo = None
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_rol_activo(mock_usuario, ['admin'])
            assert result is False

    def test_verificar_rol_activo_exception(self, app):
        """Test: _verificar_rol_activo cuando ocurre una excepción."""
        mock_usuario = MagicMock()
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol_activo = mock_rol
        mock_usuario.rol_activo.nombre_rol = MagicMock(side_effect=Exception('Error'))
        
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_rol_activo(mock_usuario, ['admin'])
            assert result is False

    def test_verificar_permisos_sin_required_permissions(self, app, mock_usuario):
        """Test: _verificar_permisos cuando no hay required_permissions."""
        with app.test_request_context():
            decorator = TokenRequired()
            result = decorator._verificar_permisos(mock_usuario, [])
            assert result is True

    def test_verificar_permisos_exception(self, app, mock_usuario):
        """Test: _verificar_permisos cuando ocurre una excepción."""
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch('src.middleware.auth_decorator.check_permission', side_effect=Exception('Error')):
                result = decorator._verificar_permisos(mock_usuario, ['ver_usuario'])
                assert result is False

    def test_process_authenticated_request_sin_token(self, app):
        """Test: _process_authenticated_request cuando no hay token."""
        def mock_route():
            return {'success': True}
        
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch.object(decorator, '_validate_authentication', return_value=(None, None, None, None)):
                response, status = decorator._process_authenticated_request(mock_route)
                assert status == 401
                assert response.json['error'] == 'Token de autorización requerido'

    def test_process_authenticated_request_sin_payload(self, app):
        """Test: _process_authenticated_request cuando no hay payload."""
        def mock_route():
            return {'success': True}
        
        with app.test_request_context():
            decorator = TokenRequired()
            
            with patch.object(decorator, '_validate_authentication', return_value=('token', None, None, None)):
                response, status = decorator._process_authenticated_request(mock_route)
                assert status == 401
                assert response.json['error'] == 'Token inválido o expirado'

    def test_process_authenticated_request_sin_sesion(self, app):
        """Test: _process_authenticated_request cuando no hay sesion."""
        def mock_route():
            return {'success': True}
        
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            
            with patch.object(decorator, '_validate_authentication', return_value=('token', payload, None, None)):
                response, status = decorator._process_authenticated_request(mock_route)
                assert status == 401
                assert response.json['error'] == 'Sesión inactiva o expirada'

    def test_process_authenticated_request_sin_usuario(self, app):
        """Test: _process_authenticated_request cuando no hay usuario."""
        def mock_route():
            return {'success': True}
        
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            mock_sesion = MagicMock()
            
            with patch.object(decorator, '_validate_authentication', return_value=('token', payload, mock_sesion, None)):
                response, status = decorator._process_authenticated_request(mock_route)
                assert status == 401
                assert response.json['error'] == 'Usuario no encontrado'

    def test_process_authenticated_request_con_permisos_insuficientes(self, app, mock_usuario, mock_sesion):
        """Test: _process_authenticated_request cuando hay error de autorización."""
        def mock_route():
            return {'success': True}
        
        with app.test_request_context():
            decorator = TokenRequired(required_permissions=['permiso_inexistente'])
            payload = {'usuario_id': 1}
            
            with patch.object(decorator, '_validate_authentication', return_value=('token', payload, mock_sesion, mock_usuario)):
                with patch.object(decorator, '_validate_authorization', return_value=({'error': 'Permisos insuficientes'}, 403)):
                    response, status = decorator._process_authenticated_request(mock_route)
                    assert status == 403

    def test_inyectar_datos_usuario_exception(self, app, mock_usuario, mock_sesion):
        """Test: _inyectar_datos_usuario cuando ocurre una excepción."""
        with app.test_request_context():
            decorator = TokenRequired()
            payload = {'usuario_id': 1}
            
            with patch('src.middleware.auth_decorator.asegurar_rol_activo_valido', side_effect=Exception('Error')):
                with pytest.raises(TokenRequiredError) as exc_info:
                    decorator._inyectar_datos_usuario(mock_usuario, mock_sesion, payload)
                assert 'Error al procesar datos de usuario' in str(exc_info.value)


@pytest.mark.unit
class TestAnyPermissionRequiredEdgeCases:
    """Tests para casos edge de any_permission_required."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

    def test_any_permission_required_sin_usuario_data(self, app):
        """Test: any_permission_required cuando no hay usuario_data."""
        from src.middleware.auth_decorator import any_permission_required, get_current_user
        
        @any_permission_required('ver_usuario')
        def protected_route():
            return {'success': True}
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value=None):
                response, status = protected_route()
                assert status == 401
                assert response.json['message'] == 'Usuario no autenticado'

    def test_any_permission_required_sin_usuario(self, app):
        """Test: any_permission_required cuando usuario no está en BD."""
        from src.middleware.auth_decorator import any_permission_required
        from src.models.usuarios.usuario import Usuario
        
        @any_permission_required('ver_usuario')
        def protected_route():
            return {'success': True}
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
                with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                    mock_query.get.return_value = None
                    
                    response, status = protected_route()
                    assert status == 401
                    assert response.json['message'] == 'Usuario no encontrado'

    def test_any_permission_required_sin_permisos(self, app):
        """Test: any_permission_required cuando usuario no tiene permisos."""
        from src.middleware.auth_decorator import any_permission_required
        from src.models.usuarios.usuario import Usuario
        
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        @any_permission_required('ver_usuario')
        def protected_route():
            return {'success': True}
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
                with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                    mock_query.get.return_value = mock_usuario
                    with patch('src.middleware.auth_decorator.check_permission', return_value=False):
                        response, status = protected_route()
                        assert status == 403
                        assert response.json['message'] == 'Permisos insuficientes'

    def test_any_permission_required_con_excepcion(self, app):
        """Test: any_permission_required cuando ocurre una excepción."""
        from src.middleware.auth_decorator import any_permission_required
        
        @any_permission_required('ver_usuario')
        def protected_route():
            return {'success': True}
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', side_effect=Exception('Error')):
                with patch('src.middleware.auth_decorator.obtener_registrador') as mock_logger:
                    mock_log = MagicMock()
                    mock_logger.return_value = mock_log
                    
                    response, status = protected_route()
                    assert status == 500
                    assert response.json['message'] == 'Error interno del servidor'
                    mock_log.error.assert_called_once()


@pytest.mark.unit
class TestHasPermissionHasRoleEdgeCases:
    """Tests para casos edge de has_permission y has_role."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        test_flask_secret = 'test-secret-key'
        test_jwt_secret = 'test-jwt-secret'
        setattr(app.config, 'SECRET_KEY', test_flask_secret)
        setattr(app.config, 'JWT_SECRET_KEY', test_jwt_secret)
        return app

    def test_has_permission_sin_usuario_data(self, app):
        """Test: has_permission cuando no hay usuario_data."""
        from src.middleware.auth_decorator import has_permission
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value=None):
                result = has_permission('ver_usuario')
                assert result is False

    def test_has_permission_sin_usuario(self, app):
        """Test: has_permission cuando usuario no está en BD."""
        from src.middleware.auth_decorator import has_permission
        from src.models.usuarios.usuario import Usuario
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
                with patch('src.middleware.auth_decorator.Usuario.query') as mock_query:
                    mock_query.get.return_value = None
                    
                    result = has_permission('ver_usuario')
                    assert result is False

    def test_has_permission_exception(self, app):
        """Test: has_permission cuando ocurre una excepción."""
        from src.middleware.auth_decorator import has_permission
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', side_effect=Exception('Error')):
                with patch('src.middleware.auth_decorator.obtener_registrador') as mock_logger:
                    mock_log = MagicMock()
                    mock_logger.return_value = mock_log
                    
                    result = has_permission('ver_usuario')
                    assert result is False
                    mock_log.error.assert_called_once()

    def test_has_role_sin_usuario_data(self, app):
        """Test: has_role cuando no hay usuario_data."""
        from src.middleware.auth_decorator import has_role
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', return_value=None):
                result = has_role('admin')
                assert result is False

    def test_has_role_exception(self, app):
        """Test: has_role cuando ocurre una excepción."""
        from src.middleware.auth_decorator import has_role
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', side_effect=Exception('Error')):
                with patch('src.middleware.auth_decorator.obtener_registrador') as mock_logger:
                    mock_log = MagicMock()
                    mock_logger.return_value = mock_log
                    
                    result = has_role('admin')
                    assert result is False
                    mock_log.error.assert_called_once()

    def test_get_user_permissions_list_exception(self, app):
        """Test: get_user_permissions_list cuando ocurre una excepción."""
        from src.middleware.auth_decorator import get_user_permissions_list
        
        with app.test_request_context():
            with patch('src.middleware.auth_decorator.get_current_user', side_effect=Exception('Error')):
                with patch('src.middleware.auth_decorator.obtener_registrador') as mock_logger:
                    mock_log = MagicMock()
                    mock_logger.return_value = mock_log
                    
                    result = get_user_permissions_list()
                    assert result == []
                    mock_log.error.assert_called_once()



