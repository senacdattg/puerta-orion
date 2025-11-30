"""
Tests para el servicio de autenticación.

Este módulo contiene tests que verifican la funcionalidad
del servicio de autenticación, incluyendo login y generación de tokens.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt

from src.services.Auth.auth_service import AuthService, AuthServiceError
from src.models.usuarios.usuario import Usuario
from src.models.eventos.sesionAuth import SesionAuth


@pytest.mark.unit
class TestAuthService:
    """Tests para AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Fixture para crear instancia del servicio."""
        return AuthService()
    
    @pytest.fixture
    def usuario_mock(self):
        """Fixture para crear usuario mock."""
        usuario = MagicMock(spec=Usuario)
        usuario.id_usuario = 1
        usuario.usuario = 'testuser'
        usuario.password = 'hashed_password'
        usuario.estado = True
        usuario.id_persona = 1
        usuario.persona = MagicMock()
        usuario.persona.primer_nombre = 'Test'
        usuario.persona.primer_apellido = 'User'
        return usuario
    
    def test_init(self, auth_service):
        """Test: Inicialización del servicio."""
        assert auth_service is not None
        assert auth_service.logger is not None
    
    def test_autenticar_usuario_success(self, auth_service, usuario_mock, app):
        """Test: Autenticar usuario exitosamente."""
        with app.app_context():
            with patch.object(auth_service, '_validar_datos_login') as mock_validar, \
                 patch.object(auth_service, '_verificar_credenciales', return_value=usuario_mock) as mock_verificar, \
                 patch.object(auth_service, '_generar_token_jwt', return_value='mock_token') as mock_token, \
                 patch.object(auth_service, '_registrar_sesion', return_value=MagicMock()) as mock_sesion, \
                 patch.object(auth_service, '_preparar_respuesta_login', return_value={'token': 'mock_token', 'usuario': {}}) as mock_preparar, \
                 patch('src.services.Auth.auth_service.asegurar_rol_activo_valido'):
                
                result = auth_service.autenticar_usuario('testuser', 'password123')
                
                assert 'token' in result
                assert result['token'] == 'mock_token'
                mock_validar.assert_called_once()
                mock_verificar.assert_called_once()
                mock_token.assert_called_once()
    
    def test_autenticar_usuario_credenciales_invalidas(self, auth_service):
        """Test: Error con credenciales inválidas."""
        with patch.object(auth_service, '_validar_datos_login'), \
             patch.object(auth_service, '_verificar_credenciales', return_value=None):
            
            with pytest.raises(AuthServiceError) as exc_info:
                auth_service.autenticar_usuario('testuser', 'wrong_password')
            
            assert 'Credenciales inválidas' in str(exc_info.value)
    
    def test_autenticar_usuario_error_inesperado(self, auth_service):
        """Test: Manejo de error inesperado."""
        with patch.object(auth_service, '_validar_datos_login', side_effect=Exception("DB Error")):
            
            with pytest.raises(AuthServiceError) as exc_info:
                auth_service.autenticar_usuario('testuser', 'password123')
            
            assert 'Error interno' in str(exc_info.value)
    
    def test_validar_datos_login_success(self, auth_service):
        """Test: Validar datos de login exitosamente."""
        auth_service._validar_datos_login('testuser', 'password123')
        # No debe lanzar excepción
    
    def test_validar_datos_login_username_vacio(self, auth_service):
        """Test: Error con username vacío."""
        with pytest.raises(AuthServiceError) as exc_info:
            auth_service._validar_datos_login('', 'password123')
        
        assert 'usuario' in str(exc_info.value).lower() or 'username' in str(exc_info.value).lower()
    
    def test_validar_datos_login_password_vacio(self, auth_service):
        """Test: Error con password vacío."""
        with pytest.raises(AuthServiceError) as exc_info:
            auth_service._validar_datos_login('testuser', '')
        
        assert 'contraseña' in str(exc_info.value).lower() or 'password' in str(exc_info.value).lower()
    
    def test_verificar_credenciales_success(self, auth_service, usuario_mock, app):
        """Test: Verificar credenciales exitosamente."""
        with app.app_context():
            with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class, \
                 patch('src.services.Auth.auth_service.check_password_hash', return_value=True):
                
                mock_query = MagicMock()
                # El servicio filtra por usuario y estado=True
                mock_filter = MagicMock()
                mock_filter.first.return_value = usuario_mock
                mock_query.filter_by.return_value = mock_filter
                mock_usuario_class.query = mock_query
                
                result = auth_service._verificar_credenciales('testuser', 'password123')
                
                assert result is not None
                assert result.id_usuario == 1
    
    def test_verificar_credenciales_usuario_no_existe(self, auth_service):
        """Test: Error cuando usuario no existe."""
        with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            
            result = auth_service._verificar_credenciales('nonexistent', 'password')
            
            assert result is None
    
    def test_verificar_credenciales_password_incorrecto(self, auth_service, usuario_mock, app):
        """Test: Error con password incorrecto."""
        with app.app_context():
            with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class, \
                 patch('src.services.Auth.auth_service.check_password_hash', return_value=False):
                
                mock_query = MagicMock()
                mock_filter = MagicMock()
                mock_filter.first.return_value = usuario_mock
                mock_query.filter_by.return_value = mock_filter
                mock_usuario_class.query = mock_query
                
                result = auth_service._verificar_credenciales('testuser', 'wrong_password')
                
                assert result is None
    
    def test_verificar_credenciales_usuario_inactivo(self, auth_service):
        """Test: Error cuando usuario está inactivo."""
        # El servicio filtra por estado=True, así que un usuario inactivo no se encontrará
        with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None  # No se encuentra porque estado=False
            mock_usuario_class.query = mock_query
            
            result = auth_service._verificar_credenciales('testuser', 'password123')
            
            assert result is None
    
    def test_generar_token_jwt_success(self, auth_service, usuario_mock, app):
        """Test: Generar token JWT exitosamente."""
        with app.app_context():
            usuario_mock.roles = []
            usuario_mock.rol_activo = None
            
            with patch('src.services.Auth.auth_service.jwt.encode') as mock_encode, \
                 patch('src.services.Auth.auth_service.datetime') as mock_datetime, \
                 patch('src.services.Auth.auth_service.timezone') as mock_timezone:
                
                mock_datetime.now.return_value = MagicMock()
                mock_timezone.utc = MagicMock()
                mock_encode.return_value = 'mock_jwt_token'
                
                token = auth_service._generar_token_jwt(usuario_mock)
                
                assert token == 'mock_jwt_token'
                mock_encode.assert_called_once()
    
    def test_registrar_sesion_success(self, auth_service, usuario_mock, db_session):
        """Test: Registrar sesión exitosamente."""
        with patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class, \
             patch('src.services.Auth.auth_service.db') as mock_db:
            
            mock_sesion = MagicMock()
            mock_sesion_class.return_value = mock_sesion
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = auth_service._registrar_sesion(usuario_mock, '127.0.0.1', 'Test Agent')
            
            assert result is not None
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_registrar_sesion_sin_ip(self, auth_service, usuario_mock, app):
        """Test: Registrar sesión sin IP."""
        with app.app_context():
            with patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class, \
                 patch('src.services.Auth.auth_service.db') as mock_db, \
                 patch.object(auth_service, '_generar_token_sesion', return_value='mock_token_sesion'), \
                 patch.object(auth_service, '_obtener_ip_origen', return_value='127.0.0.1'), \
                 patch.object(auth_service, '_obtener_user_agent', return_value='Test Agent'), \
                 patch('src.services.Auth.auth_service.datetime') as mock_datetime, \
                 patch('src.services.Auth.auth_service.timezone') as mock_timezone:
                
                mock_datetime.now.return_value = MagicMock()
                mock_timezone.utc = MagicMock()
                mock_sesion = MagicMock()
                mock_sesion_class.return_value = mock_sesion
                mock_db.session.add = MagicMock()
                mock_db.session.commit = MagicMock()
                
                result = auth_service._registrar_sesion(usuario_mock, None, None)
                
                assert result is not None
    
    def test_preparar_respuesta_login_success(self, auth_service, usuario_mock, app):
        """Test: Preparar respuesta de login exitosamente."""
        with app.app_context():
            token = 'mock_token'
            sesion = MagicMock()
            sesion.id_sesion = 1
            sesion.fecha_inicio = MagicMock()
            sesion.fecha_inicio.isoformat.return_value = '2024-01-01T00:00:00'
            sesion.fecha_expiracion = MagicMock()
            sesion.fecha_expiracion.isoformat.return_value = '2024-01-02T00:00:00'
            sesion.ip_origen = '127.0.0.1'
            
            usuario_mock.roles = []
            usuario_mock.rol_activo = None
            usuario_mock.persona = MagicMock()
            usuario_mock.persona.id_persona = 1
            usuario_mock.persona.nombre_completo = 'Test User'
            usuario_mock.persona.correo_electronico = 'test@example.com'
            usuario_mock.persona.documento = '12345678'
            
            with patch('src.services.Auth.auth_service.current_app') as mock_app:
                mock_app.config.get.return_value = 3600
                
                result = auth_service._preparar_respuesta_login(usuario_mock, token, sesion)
                
                assert 'token' in result
                assert result['token'] == token
                assert 'user' in result
                assert result['user']['id_usuario'] == 1
    
    def test_preparar_respuesta_login_sin_persona(self, auth_service, usuario_mock, app):
        """Test: Preparar respuesta de login sin persona."""
        with app.app_context():
            token = 'mock_token'
            sesion = MagicMock()
            sesion.id_sesion = 1
            sesion.fecha_inicio = MagicMock()
            sesion.fecha_inicio.isoformat.return_value = '2024-01-01T00:00:00'
            sesion.fecha_expiracion = MagicMock()
            sesion.fecha_expiracion.isoformat.return_value = '2024-01-02T00:00:00'
            sesion.ip_origen = '127.0.0.1'
            
            usuario_mock.roles = []
            usuario_mock.rol_activo = None
            usuario_mock.persona = None
            
            with patch('src.services.Auth.auth_service.current_app') as mock_app:
                mock_app.config.get.return_value = 3600
                
                result = auth_service._preparar_respuesta_login(usuario_mock, token, sesion)
                
                assert 'token' in result
                assert result['token'] == token
                assert 'user' in result
                assert result['user']['persona'] is None
    
    def test_preparar_respuesta_login_con_roles(self, auth_service, usuario_mock, app):
        """Test: Preparar respuesta de login con roles."""
        with app.app_context():
            token = 'mock_token'
            sesion = MagicMock()
            sesion.id_sesion = 1
            sesion.fecha_inicio = MagicMock()
            sesion.fecha_inicio.isoformat.return_value = '2024-01-01T00:00:00'
            sesion.fecha_expiracion = MagicMock()
            sesion.fecha_expiracion.isoformat.return_value = '2024-01-02T00:00:00'
            sesion.ip_origen = '127.0.0.1'
            
            rol_mock = MagicMock()
            rol_mock.nombre_rol = 'admin'
            rol_mock.to_dict.return_value = {'id_rol': 1, 'nombre_rol': 'admin'}
            usuario_mock.roles = [rol_mock]
            usuario_mock.rol_activo = rol_mock
            usuario_mock.persona = MagicMock()
            usuario_mock.persona.id_persona = 1
            usuario_mock.persona.nombre_completo = 'Test User'
            usuario_mock.persona.correo_electronico = 'test@example.com'
            usuario_mock.persona.documento = '12345678'
            
            with patch('src.services.Auth.auth_service.current_app') as mock_app:
                mock_app.config.get.return_value = 3600
                
                result = auth_service._preparar_respuesta_login(usuario_mock, token, sesion)
                
                assert 'user' in result
                assert 'roles' in result['user']
                assert len(result['user']['roles']) == 1
                assert result['user']['rol_activo'] == 'admin'
