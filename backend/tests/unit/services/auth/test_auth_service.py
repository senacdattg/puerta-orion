"""
Tests for authentication service.

This module contains tests that verify authentication operations,
including login, token generation, session management, and logout.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash

from src.services.Auth.auth_service import AuthService, AuthServiceError
from src.models.usuarios.usuario import Usuario
from src.models.personas.persona import Persona
from src.models.eventos.sesionAuth import SesionAuth


@pytest.mark.unit
class TestAuthService:
    """Tests for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create an instance of AuthService."""
        return AuthService()
    
    @pytest.fixture
    def mock_usuario(self):
        """Create a mock usuario for testing."""
        # Don't use spec=Usuario to avoid Flask-SQLAlchemy accessing database
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.usuario = 'testuser'
        usuario.password = generate_password_hash('password123')
        usuario.id_persona = 1
        usuario.estado = True
        usuario.roles = []
        usuario.rol_activo = None
        return usuario
    
    @pytest.fixture
    def mock_persona(self):
        """Create a mock persona for testing."""
        # Don't use spec=Persona to avoid Flask-SQLAlchemy accessing database
        persona = MagicMock()
        persona.id_persona = 1
        persona.nombre_completo = 'Test User'
        persona.correo_electronico = 'test@example.com'
        persona.documento = '12345678'
        return persona
    
    def test_autenticar_usuario_success(self, auth_service, mock_usuario, mock_persona, app_context):
        """Test: Successful user authentication."""
        mock_usuario.persona = mock_persona
        
        with patch.object(auth_service, '_validar_datos_login') as mock_validar, \
             patch.object(auth_service, '_verificar_credenciales', return_value=mock_usuario) as mock_verificar, \
             patch.object(auth_service, '_generar_token_jwt', return_value='test_token') as mock_token, \
             patch.object(auth_service, '_registrar_sesion', return_value=MagicMock()) as mock_sesion, \
             patch('src.services.Auth.auth_service.asegurar_rol_activo_valido'):
            
            mock_sesion_obj = MagicMock()
            mock_sesion_obj.id_sesion = 1
            mock_sesion_obj.fecha_inicio = datetime.now(timezone.utc)
            mock_sesion_obj.fecha_expiracion = datetime.now(timezone.utc) + timedelta(hours=1)
            mock_sesion_obj.ip_origen = '127.0.0.1'
            mock_sesion.return_value = mock_sesion_obj
            
            result = auth_service.autenticar_usuario('testuser', 'password123')
            
            assert result['success'] is True
            assert result['token'] == 'test_token'
            assert result['user']['username'] == 'testuser'
            mock_validar.assert_called_once()
            mock_verificar.assert_called_once_with('testuser', 'password123')
            mock_token.assert_called_once()
            mock_sesion.assert_called_once()
    
    def test_autenticar_usuario_invalid_credentials(self, auth_service, app_context):
        """Test: Authentication with invalid credentials."""
        with patch.object(auth_service, '_validar_datos_login'), \
             patch.object(auth_service, '_verificar_credenciales', return_value=None):
            
            with pytest.raises(AuthServiceError, match="Credenciales inválidas"):
                auth_service.autenticar_usuario('testuser', 'wrongpassword')
    
    def test_autenticar_usuario_empty_username(self, auth_service):
        """Test: Authentication with empty username."""
        with pytest.raises(AuthServiceError, match="El nombre de usuario es requerido"):
            auth_service.autenticar_usuario('', 'password123')
    
    def test_autenticar_usuario_empty_password(self, auth_service):
        """Test: Authentication with empty password."""
        with pytest.raises(AuthServiceError, match="La contraseña es requerida"):
            auth_service.autenticar_usuario('testuser', '')
    
    def test_autenticar_usuario_short_username(self, auth_service):
        """Test: Authentication with username too short."""
        with pytest.raises(AuthServiceError, match="El nombre de usuario debe tener al menos 3 caracteres"):
            auth_service.autenticar_usuario('ab', 'password123')
    
    def test_validar_datos_login_success(self, auth_service):
        """Test: Valid login data validation."""
        # Should not raise any exception
        auth_service._validar_datos_login('testuser', 'password123')
    
    def test_validar_datos_login_empty_username(self, auth_service):
        """Test: Validation with empty username."""
        with pytest.raises(AuthServiceError, match="El nombre de usuario es requerido"):
            auth_service._validar_datos_login('', 'password123')
    
    def test_validar_datos_login_empty_password(self, auth_service):
        """Test: Validation with empty password."""
        with pytest.raises(AuthServiceError, match="La contraseña es requerida"):
            auth_service._validar_datos_login('testuser', '')
    
    def test_verificar_credenciales_success(self, auth_service, mock_usuario, app_context):
        """Test: Successful credential verification."""
        with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.auth_service.check_password_hash', return_value=True):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = auth_service._verificar_credenciales('testuser', 'password123')
            
            assert result == mock_usuario
            mock_query.filter_by.assert_called_once_with(usuario='testuser', estado=True)
    
    def test_verificar_credenciales_user_not_found(self, auth_service):
        """Test: Credential verification with user not found."""
        with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            
            result = auth_service._verificar_credenciales('testuser', 'password123')
            
            assert result is None
    
    def test_verificar_credenciales_wrong_password(self, auth_service, mock_usuario, app_context):
        """Test: Credential verification with wrong password."""
        with patch('src.services.Auth.auth_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.auth_service.check_password_hash', return_value=False):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = auth_service._verificar_credenciales('testuser', 'wrongpassword')
            
            assert result is None
    
    def test_generar_token_jwt_success(self, auth_service, mock_usuario, app_context):
        """Test: Successful JWT token generation."""
        mock_usuario.roles = []
        mock_usuario.rol_activo = None
        
        with patch('src.services.Auth.auth_service.jwt.encode') as mock_encode:
            mock_encode.return_value = 'test_token'
            
            result = auth_service._generar_token_jwt(mock_usuario)
            
            assert result == 'test_token'
            mock_encode.assert_called_once()
            call_args = mock_encode.call_args
            # jwt.encode(payload, secret_key, algorithm='HS256')
            # call_args[0] = positional args tuple, call_args[1] = keyword args dict
            assert call_args[0][1] == 'test_secret_key'  # secret_key is second positional arg
            assert call_args[1].get('algorithm') == 'HS256'  # algorithm is keyword argument
            payload = call_args[0][0]
            assert payload['usuario_id'] == 1
            assert payload['username'] == 'testuser'
    
    def test_generar_token_jwt_no_secret_key(self, auth_service, mock_usuario, app_context):
        """Test: JWT generation without secret key configured."""
        from flask import current_app
        original_key = current_app.config.get('JWT_SECRET_KEY')
        current_app.config['JWT_SECRET_KEY'] = None
        
        try:
            with pytest.raises(AuthServiceError, match="JWT_SECRET_KEY no configurado"):
                auth_service._generar_token_jwt(mock_usuario)
        finally:
            current_app.config['JWT_SECRET_KEY'] = original_key
    
    def test_registrar_sesion_success(self, auth_service, mock_usuario, app_context):
        """Test: Successful session registration."""
        with patch('src.services.Auth.auth_service.db') as mock_db, \
             patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class, \
             patch.object(auth_service, '_generar_token_sesion', return_value='session_token'), \
             patch.object(auth_service, '_obtener_ip_origen', return_value='127.0.0.1'), \
             patch.object(auth_service, '_obtener_user_agent', return_value='Test Agent'):
            
            mock_sesion = MagicMock()
            mock_sesion_class.return_value = mock_sesion
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = auth_service._registrar_sesion(mock_usuario, '127.0.0.1', 'Test Agent')
            
            assert result == mock_sesion
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_verificar_token_jwt_success(self, auth_service, app_context):
        """Test: Successful JWT token verification."""
        token = 'valid.token.here'
        payload = {
            'usuario_id': 1,
            'username': 'testuser',
            'exp': int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())
        }
        
        with patch('src.services.Auth.auth_service.jwt.decode', return_value=payload):
            result = auth_service.verificar_token_jwt(token)
            
            assert result == payload
    
    def test_verificar_token_jwt_invalid_format(self, auth_service, app_context):
        """Test: JWT verification with invalid format."""
        token = 'invalid_token'
        
        result = auth_service.verificar_token_jwt(token)
        
        assert result is None
    
    def test_verificar_token_jwt_expired(self, auth_service, app_context):
        """Test: JWT verification with expired token."""
        token = 'expired.token.here'
        
        with patch('src.services.Auth.auth_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError('Token expired')
            
            result = auth_service.verificar_token_jwt(token)
            
            assert result is None
    
    def test_verificar_token_jwt_invalid_token(self, auth_service, app_context):
        """Test: JWT verification with invalid token."""
        token = 'invalid.token.here'
        
        with patch('src.services.Auth.auth_service.jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError('Invalid token')
            
            result = auth_service.verificar_token_jwt(token)
            
            assert result is None
    
    def test_cerrar_sesion_success(self, auth_service, app_context):
        """Test: Successful session closure."""
        token = 'valid.token.here'
        payload = {'usuario_id': 1}
        
        with patch.object(auth_service, 'verificar_token_jwt', return_value=payload), \
             patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class, \
             patch('src.services.Auth.auth_service.db') as mock_db:
            
            mock_sesion = MagicMock()
            mock_sesion.estado = True
            
            # Configure the query chain: filter_by().filter().all()
            # We need to mock filter() to return an object with all() without evaluating the SQLAlchemy expression
            mock_filter_result = MagicMock()
            mock_filter_result.all.return_value = [mock_sesion]
            
            mock_filter_by = MagicMock()
            # Patch filter() to return our mock directly, avoiding SQLAlchemy expression evaluation
            def mock_filter_func(*args, **kwargs):
                return mock_filter_result
            mock_filter_by.filter = mock_filter_func
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value = mock_filter_by
            mock_sesion_class.query = mock_query
            
            # Mock the class attribute to avoid SQLAlchemy trying to access it during expression evaluation
            # Create a descriptor-like object that can be compared
            class MockColumn:
                def __gt__(self, other):
                    return MagicMock()
            mock_sesion_class.fecha_expiracion = MockColumn()
            
            mock_db.session.commit = MagicMock()
            
            result = auth_service.cerrar_sesion(token)
            
            assert result is True
            assert mock_sesion.estado is False
            mock_db.session.commit.assert_called_once()
    
    def test_cerrar_sesion_invalid_token(self, auth_service, app_context):
        """Test: Session closure with invalid token."""
        token = 'invalid.token.here'
        
        with patch.object(auth_service, 'verificar_token_jwt', return_value=None):
            result = auth_service.cerrar_sesion(token)
            
            assert result is False
    
    def test_cerrar_sesion_no_user_id(self, auth_service, app_context):
        """Test: Session closure with token missing user_id."""
        token = 'valid.token.here'
        payload = {}
        
        with patch.object(auth_service, 'verificar_token_jwt', return_value=payload):
            result = auth_service.cerrar_sesion(token)
            
            assert result is False
    
    def test_obtener_sesiones_activas_success(self, auth_service, app_context):
        """Test: Successful retrieval of active sessions."""
        id_usuario = 1
        
        with patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class:
            mock_sesion = MagicMock()
            mock_sesion.to_dict.return_value = {'id_sesion': 1}
            
            # Configure the query chain: filter_by().filter().all()
            # We need to mock filter() to return an object with all() without evaluating the SQLAlchemy expression
            mock_filter_result = MagicMock()
            mock_filter_result.all.return_value = [mock_sesion]
            
            mock_filter_by = MagicMock()
            # Patch filter() to return our mock directly, avoiding SQLAlchemy expression evaluation
            def mock_filter_func(*args, **kwargs):
                return mock_filter_result
            mock_filter_by.filter = mock_filter_func
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value = mock_filter_by
            mock_sesion_class.query = mock_query
            
            # Mock the class attribute to avoid SQLAlchemy trying to access it during expression evaluation
            # Create a descriptor-like object that can be compared
            class MockColumn:
                def __gt__(self, other):
                    return MagicMock()
            mock_sesion_class.fecha_expiracion = MockColumn()
            
            result = auth_service.obtener_sesiones_activas(id_usuario)
            
            assert len(result) == 1
            assert result[0]['id_sesion'] == 1
    
    def test_obtener_sesiones_activas_empty(self, auth_service, app_context):
        """Test: Retrieval of active sessions when none exist."""
        id_usuario = 1
        
        with patch('src.services.Auth.auth_service.SesionAuth') as mock_sesion_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.filter.return_value.all.return_value = []
            mock_sesion_class.query = mock_query
            
            result = auth_service.obtener_sesiones_activas(id_usuario)
            
            assert result == []
    
    def test_generar_token_sesion(self, auth_service):
        """Test: Session token generation."""
        token = auth_service._generar_token_sesion()
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_obtener_ip_origen_from_request(self, auth_service, app_context, mock_request_context):
        """Test: IP origin retrieval from request."""
        from flask import request
        result = auth_service._obtener_ip_origen()
        assert result == '192.168.1.1'
    
    def test_obtener_ip_origen_fallback(self, auth_service, app_context):
        """Test: IP origin retrieval fallback."""
        # Test without request context
        result = auth_service._obtener_ip_origen()
        assert result == '127.0.0.1'
    
    def test_obtener_user_agent_from_request(self, auth_service, app_context, mock_request_context):
        """Test: User agent retrieval from request."""
        result = auth_service._obtener_user_agent()
        assert result == 'Mozilla/5.0'
    
    def test_obtener_user_agent_fallback(self, auth_service, app_context):
        """Test: User agent retrieval fallback."""
        # Test without request context
        result = auth_service._obtener_user_agent()
        assert result == 'Unknown'
    
    def test_preparar_respuesta_login(self, auth_service, mock_usuario, mock_persona, app_context):
        """Test: Login response preparation."""
        mock_usuario.persona = mock_persona
        mock_usuario.roles = []
        mock_usuario.rol_activo = None
        
        mock_sesion = MagicMock()
        mock_sesion.id_sesion = 1
        mock_sesion.fecha_inicio = datetime.now(timezone.utc)
        mock_sesion.fecha_expiracion = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_sesion.ip_origen = '127.0.0.1'
        
        result = auth_service._preparar_respuesta_login(mock_usuario, 'test_token', mock_sesion)
        
        assert result['success'] is True
        assert result['token'] == 'test_token'
        assert result['user']['username'] == 'testuser'
        assert result['session']['id_sesion'] == 1

