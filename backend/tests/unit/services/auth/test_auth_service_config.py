"""
Tests unitarios para auth_service_config.py.

Cubre las funciones de configuración del servicio de autenticación.
"""

import pytest
from unittest.mock import patch

from src.services.Auth.auth_service_config import (
    AuthServiceConfig,
    JWTConfig,
    SessionConfig,
    get_expiration_time_for_role,
    is_multiple_sessions_allowed,
    get_max_sessions_per_user,
    should_log_operation,
    auth_config,
    jwt_config,
    session_config,
)


@pytest.mark.unit
class TestAuthServiceConfig:
    """Tests para AuthServiceConfig."""
    
    def test_jwt_algorithm(self):
        """Test: JWT_ALGORITHM está configurado."""
        assert AuthServiceConfig.JWT_ALGORITHM == 'HS256'
    
    def test_jwt_issuer(self):
        """Test: JWT_ISSUER está configurado."""
        assert AuthServiceConfig.JWT_ISSUER == 'puerta_orion_api'
    
    def test_jwt_default_expires_in(self):
        """Test: JWT_DEFAULT_EXPIRES_IN es un entero positivo."""
        assert isinstance(AuthServiceConfig.JWT_DEFAULT_EXPIRES_IN, int)
        assert AuthServiceConfig.JWT_DEFAULT_EXPIRES_IN > 0
    
    def test_session_token_length(self):
        """Test: SESSION_TOKEN_LENGTH está configurado."""
        assert AuthServiceConfig.SESSION_TOKEN_LENGTH == 32
    
    def test_max_login_attempts(self):
        """Test: MAX_LOGIN_ATTEMPTS está configurado."""
        assert AuthServiceConfig.MAX_LOGIN_ATTEMPTS == 5
    
    def test_lockout_duration(self):
        """Test: LOCKOUT_DURATION está configurado."""
        assert AuthServiceConfig.LOCKOUT_DURATION == 900
    
    def test_min_username_length(self):
        """Test: MIN_USERNAME_LENGTH está configurado."""
        assert AuthServiceConfig.MIN_USERNAME_LENGTH == 3
    
    def test_max_username_length(self):
        """Test: MAX_USERNAME_LENGTH está configurado."""
        assert AuthServiceConfig.MAX_USERNAME_LENGTH == 200
    
    def test_min_clave_length(self):
        """Test: MIN_CLAVE_LENGTH está configurado."""
        assert AuthServiceConfig.MIN_CLAVE_LENGTH == 6
    
    def test_error_messages_exists(self):
        """Test: ERROR_MESSAGES contiene los mensajes esperados."""
        messages = AuthServiceConfig.ERROR_MESSAGES
        assert 'username_required' in messages
        assert 'clave_requerida' in messages
        assert 'invalid_credentials' in messages
        assert 'user_inactive' in messages
        assert 'token_expired' in messages
    
    def test_role_expiration_times(self):
        """Test: ROLE_EXPIRATION_TIMES contiene roles esperados."""
        times = AuthServiceConfig.ROLE_EXPIRATION_TIMES
        assert 'admin' in times
        assert 'usuario' in times
        assert 'deportista' in times
        assert 'acudiente' in times
        # Verificar que son valores positivos
        assert all(isinstance(v, int) and v > 0 for v in times.values())


@pytest.mark.unit
class TestJWTConfig:
    """Tests para JWTConfig."""
    
    def test_supported_algorithms(self):
        """Test: SUPPORTED_ALGORITHMS contiene algoritmos válidos."""
        assert 'HS256' in JWTConfig.SUPPORTED_ALGORITHMS
        assert 'HS512' in JWTConfig.SUPPORTED_ALGORITHMS
    
    def test_default_algorithm(self):
        """Test: DEFAULT_ALGORITHM está configurado."""
        assert JWTConfig.DEFAULT_ALGORITHM == 'HS256'
    
    def test_standard_claims(self):
        """Test: STANDARD_CLAIMS contiene los claims esperados."""
        claims = JWTConfig.STANDARD_CLAIMS
        assert 'iss' in claims
        assert 'aud' in claims
        assert 'iat' in claims
        assert 'exp' in claims
    
    def test_custom_claims(self):
        """Test: CUSTOM_CLAIMS contiene los claims esperados."""
        claims = JWTConfig.CUSTOM_CLAIMS
        assert 'user_id' in claims
        assert 'username' in claims
        assert 'persona_id' in claims
        assert 'roles' in claims
        assert 'session_id' in claims


@pytest.mark.unit
class TestSessionConfig:
    """Tests para SessionConfig."""
    
    def test_table_name(self):
        """Test: TABLE_NAME está configurado."""
        assert SessionConfig.TABLE_NAME == 'sesionauth'
    
    def test_fields(self):
        """Test: FIELDS contiene las configuraciones esperadas."""
        fields = SessionConfig.FIELDS
        assert 'token_length' in fields
        assert 'ip_length' in fields
        assert 'user_agent_length' in fields
    
    def test_cleanup_config(self):
        """Test: CLEANUP_CONFIG está configurado."""
        cleanup = SessionConfig.CLEANUP_CONFIG
        assert 'enabled' in cleanup
        assert 'interval' in cleanup
        assert 'batch_size' in cleanup
        assert 'retention_days' in cleanup


@pytest.mark.unit
class TestGetExpirationTimeForRole:
    """Tests para get_expiration_time_for_role."""
    
    def test_get_expiration_time_for_admin(self):
        """Test: Obtener tiempo de expiración para rol admin."""
        time = get_expiration_time_for_role('admin')
        assert isinstance(time, int)
        assert time > 0
        assert time == 7200  # 2 horas
    
    def test_get_expiration_time_for_usuario(self):
        """Test: Obtener tiempo de expiración para rol usuario."""
        time = get_expiration_time_for_role('usuario')
        assert isinstance(time, int)
        assert time > 0
        assert time == 3600  # 1 hora
    
    def test_get_expiration_time_for_deportista(self):
        """Test: Obtener tiempo de expiración para rol deportista."""
        time = get_expiration_time_for_role('deportista')
        assert isinstance(time, int)
        assert time > 0
    
    def test_get_expiration_time_for_invalid_role(self):
        """Test: Obtener tiempo de expiración para rol inválido usa default."""
        time = get_expiration_time_for_role('rol_inexistente')
        assert isinstance(time, int)
        assert time > 0
        # Debe usar JWT_DEFAULT_EXPIRES_IN
        assert time == auth_config.JWT_DEFAULT_EXPIRES_IN


@pytest.mark.unit
class TestIsMultipleSessionsAllowed:
    """Tests para is_multiple_sessions_allowed."""
    
    def test_is_multiple_sessions_allowed_returns_bool(self):
        """Test: is_multiple_sessions_allowed retorna un booleano."""
        result = is_multiple_sessions_allowed()
        assert isinstance(result, bool)
    
    def test_is_multiple_sessions_allowed_default(self):
        """Test: is_multiple_sessions_allowed retorna el valor configurado."""
        result = is_multiple_sessions_allowed()
        assert result == auth_config.ALLOW_MULTIPLE_SESSIONS


@pytest.mark.unit
class TestGetMaxSessionsPerUser:
    """Tests para get_max_sessions_per_user."""
    
    def test_get_max_sessions_per_user_returns_int(self):
        """Test: get_max_sessions_per_user retorna un entero."""
        result = get_max_sessions_per_user()
        assert isinstance(result, int)
    
    def test_get_max_sessions_per_user_positive(self):
        """Test: get_max_sessions_per_user retorna un valor positivo."""
        result = get_max_sessions_per_user()
        assert result > 0
    
    def test_get_max_sessions_per_user_default(self):
        """Test: get_max_sessions_per_user retorna el valor configurado."""
        result = get_max_sessions_per_user()
        assert result == auth_config.MAX_SESSIONS_PER_USER


@pytest.mark.unit
class TestShouldLogOperation:
    """Tests para should_log_operation."""
    
    def test_should_log_operation_login_success(self):
        """Test: should_log_operation para login_success."""
        result = should_log_operation('login_success')
        assert isinstance(result, bool)
        assert result == auth_config.LOG_SUCCESSFUL_LOGINS
    
    def test_should_log_operation_login_failed(self):
        """Test: should_log_operation para login_failed."""
        result = should_log_operation('login_failed')
        assert isinstance(result, bool)
        assert result == auth_config.LOG_FAILED_ATTEMPTS
    
    def test_should_log_operation_token_generation(self):
        """Test: should_log_operation para token_generation."""
        result = should_log_operation('token_generation')
        assert isinstance(result, bool)
        assert result == auth_config.LOG_TOKEN_GENERATION
    
    def test_should_log_operation_session_creation(self):
        """Test: should_log_operation para session_creation."""
        result = should_log_operation('session_creation')
        assert isinstance(result, bool)
        assert result == auth_config.LOG_SESSION_CREATION
    
    def test_should_log_operation_unknown_returns_true(self):
        """Test: should_log_operation para operación desconocida retorna True por defecto."""
        result = should_log_operation('operacion_desconocida')
        assert isinstance(result, bool)
        assert result is True


@pytest.mark.unit
class TestConfigInstances:
    """Tests para las instancias globales de configuración."""
    
    def test_auth_config_is_instance(self):
        """Test: auth_config es una instancia de AuthServiceConfig."""
        assert isinstance(auth_config, AuthServiceConfig)
    
    def test_jwt_config_is_instance(self):
        """Test: jwt_config es una instancia de JWTConfig."""
        assert isinstance(jwt_config, JWTConfig)
    
    def test_session_config_is_instance(self):
        """Test: session_config es una instancia de SessionConfig."""
        assert isinstance(session_config, SessionConfig)

