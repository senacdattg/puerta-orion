"""
Tests para la configuración del decorador de autenticación.

Este módulo contiene tests que verifican las funciones
de configuración del middleware de autenticación.
"""

import pytest

from src.middleware.auth_decorator_config import (
    AuthDecoratorConfig,
    TokenValidationConfig,
    SessionValidationConfig,
    get_error_message,
    get_default_roles_for_type,
    should_log_event,
    is_session_cache_enabled,
    get_cache_key,
    should_audit_event,
    get_audit_data
)


@pytest.mark.unit
class TestAuthDecoratorConfig:
    """Tests para AuthDecoratorConfig."""
    
    def test_auth_decorator_config_constants(self):
        """Test: Verificar constantes de configuración."""
        assert AuthDecoratorConfig.AUTH_HEADER_NAME == 'Authorization'
        assert AuthDecoratorConfig.TOKEN_PREFIX == 'Bearer'
        assert AuthDecoratorConfig.REQUIRE_ACTIVE_SESSION is True
        assert AuthDecoratorConfig.REQUIRE_ACTIVE_USER is True
    
    def test_auth_decorator_config_error_messages(self):
        """Test: Verificar mensajes de error."""
        messages = AuthDecoratorConfig.ERROR_MESSAGES
        
        assert 'token_required' in messages
        assert 'token_invalid' in messages
        assert 'session_inactive' in messages
        assert 'user_not_found' in messages
        assert 'user_inactive' in messages
        assert 'insufficient_permissions' in messages
    
    def test_auth_decorator_config_default_roles(self):
        """Test: Verificar roles por defecto."""
        roles = AuthDecoratorConfig.DEFAULT_ROLES
        
        assert 'admin' in roles
        assert 'user' in roles
        assert 'deportista' in roles
        assert 'acudiente' in roles
    
    def test_auth_decorator_config_session_settings(self):
        """Test: Verificar configuración de sesión."""
        assert AuthDecoratorConfig.SESSION_CHECK_INTERVAL == 300
        assert AuthDecoratorConfig.MAX_SESSION_AGE == 86400
    
    def test_auth_decorator_config_proxy_settings(self):
        """Test: Verificar configuración de proxy."""
        assert AuthDecoratorConfig.TRUST_PROXY_HEADERS is True
        assert 'X-Forwarded-For' in AuthDecoratorConfig.PROXY_HEADERS
        assert 'X-Real-IP' in AuthDecoratorConfig.PROXY_HEADERS


@pytest.mark.unit
class TestTokenValidationConfig:
    """Tests para TokenValidationConfig."""
    
    def test_token_validation_config_algorithms(self):
        """Test: Verificar algoritmos soportados."""
        assert 'HS256' in TokenValidationConfig.SUPPORTED_ALGORITHMS
        assert 'HS512' in TokenValidationConfig.SUPPORTED_ALGORITHMS
        assert TokenValidationConfig.DEFAULT_ALGORITHM == 'HS256'
    
    def test_token_validation_config_claims(self):
        """Test: Verificar claims requeridos y opcionales."""
        assert 'user_id' in TokenValidationConfig.REQUIRED_CLAIMS
        assert 'username' in TokenValidationConfig.REQUIRED_CLAIMS
        assert 'exp' in TokenValidationConfig.REQUIRED_CLAIMS
        assert 'persona_id' in TokenValidationConfig.OPTIONAL_CLAIMS
    
    def test_token_validation_config_expiration(self):
        """Test: Verificar configuración de expiración."""
        assert TokenValidationConfig.CLOCK_SKEW_TOLERANCE == 30
        assert TokenValidationConfig.MAX_TOKEN_AGE == 86400
    
    def test_token_validation_config_validation_flags(self):
        """Test: Verificar flags de validación."""
        assert TokenValidationConfig.VALIDATE_ISSUER is True
        assert TokenValidationConfig.VALIDATE_AUDIENCE is False
        assert TokenValidationConfig.VALIDATE_SIGNATURE is True


@pytest.mark.unit
class TestSessionValidationConfig:
    """Tests para SessionValidationConfig."""
    
    def test_session_validation_config_table(self):
        """Test: Verificar configuración de tabla."""
        assert SessionValidationConfig.TABLE_NAME == 'sesionauth'
    
    def test_session_validation_config_required_fields(self):
        """Test: Verificar campos requeridos."""
        fields = SessionValidationConfig.REQUIRED_FIELDS
        
        assert 'id_usuario' in fields
        assert 'token_sesion' in fields
        assert 'estado' in fields
        assert 'fecha_expiracion' in fields
    
    def test_session_validation_config_states(self):
        """Test: Verificar estados de sesión."""
        assert SessionValidationConfig.ACTIVE_STATE is True
        assert SessionValidationConfig.INACTIVE_STATE is False
    
    def test_session_validation_config_cleanup(self):
        """Test: Verificar configuración de limpieza."""
        assert SessionValidationConfig.AUTO_CLEANUP_EXPIRED is True
        assert SessionValidationConfig.CLEANUP_INTERVAL == 3600
        assert SessionValidationConfig.CLEANUP_BATCH_SIZE == 100


@pytest.mark.unit
class TestConfigFunctions:
    """Tests para funciones de configuración."""
    
    def test_get_error_message_existing(self):
        """Test: Obtener mensaje de error existente."""
        message = get_error_message('token_required')
        
        assert message == 'Token de autorización requerido'
    
    def test_get_error_message_not_existing(self):
        """Test: Obtener mensaje de error inexistente."""
        message = get_error_message('nonexistent_key')
        
        assert message == 'Error de autenticación'
    
    def test_get_default_roles_for_type_existing(self):
        """Test: Obtener roles por defecto para tipo existente."""
        roles = get_default_roles_for_type('admin')
        
        assert roles == ['admin']
    
    def test_get_default_roles_for_type_not_existing(self):
        """Test: Obtener roles por defecto para tipo inexistente."""
        roles = get_default_roles_for_type('nonexistent')
        
        assert roles == []
    
    def test_should_log_event_auth_success(self):
        """Test: Verificar si se debe registrar evento de éxito."""
        result = should_log_event('auth_success')
        
        assert result == AuthDecoratorConfig.LOG_AUTHENTICATION_SUCCESS
    
    def test_should_log_event_auth_failure(self):
        """Test: Verificar si se debe registrar evento de fallo."""
        result = should_log_event('auth_failure')
        
        assert result == AuthDecoratorConfig.LOG_AUTHENTICATION_FAILURE
    
    def test_should_log_event_permission_denied(self):
        """Test: Verificar si se debe registrar evento de permiso denegado."""
        result = should_log_event('permission_denied')
        
        assert result == AuthDecoratorConfig.LOG_PERMISSION_DENIED
    
    def test_should_log_event_unknown(self):
        """Test: Verificar si se debe registrar evento desconocido."""
        result = should_log_event('unknown_event')
        
        assert result is True  # Por defecto True
    
    def test_is_session_cache_enabled(self):
        """Test: Verificar si el caché de sesiones está habilitado."""
        result = is_session_cache_enabled()
        
        assert result == AuthDecoratorConfig.ENABLE_SESSION_CACHE
    
    def test_get_cache_key(self):
        """Test: Generar clave de caché."""
        session_id = "test_session_123"
        key = get_cache_key(session_id)
        
        assert key == f"{AuthDecoratorConfig.CACHE_PREFIX}{session_id}"
    
    def test_should_audit_event(self):
        """Test: Verificar si se debe auditar evento."""
        result = should_audit_event()
        
        assert result == AuthDecoratorConfig.AUDIT_ENABLED
    
    def test_get_audit_data_with_ip_and_user_agent(self):
        """Test: Obtener datos de auditoría con IP y User-Agent."""
        request_data = {
            'timestamp': '2024-01-01T00:00:00',
            'endpoint': '/api/test',
            'method': 'GET',
            'ip': '127.0.0.1',
            'user_agent': 'Mozilla/5.0'
        }
        
        audit_data = get_audit_data(request_data)
        
        assert audit_data['timestamp'] == '2024-01-01T00:00:00'
        assert audit_data['endpoint'] == '/api/test'
        assert audit_data['method'] == 'GET'
        assert audit_data['ip'] == '127.0.0.1'
        assert audit_data['user_agent'] == 'Mozilla/5.0'
    
    def test_get_audit_data_without_ip_and_user_agent(self):
        """Test: Obtener datos de auditoría sin IP y User-Agent cuando están deshabilitados."""
        original_include_ip = AuthDecoratorConfig.AUDIT_INCLUDE_IP
        original_include_ua = AuthDecoratorConfig.AUDIT_INCLUDE_USER_AGENT
        
        try:
            AuthDecoratorConfig.AUDIT_INCLUDE_IP = False
            AuthDecoratorConfig.AUDIT_INCLUDE_USER_AGENT = False
            
            request_data = {
                'timestamp': '2024-01-01T00:00:00',
                'endpoint': '/api/test',
                'method': 'GET',
                'ip': '127.0.0.1',
                'user_agent': 'Mozilla/5.0'
            }
            
            audit_data = get_audit_data(request_data)
            
            assert 'ip' not in audit_data
            assert 'user_agent' not in audit_data
        finally:
            AuthDecoratorConfig.AUDIT_INCLUDE_IP = original_include_ip
            AuthDecoratorConfig.AUDIT_INCLUDE_USER_AGENT = original_include_ua





