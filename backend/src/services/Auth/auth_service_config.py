"""
Configuración para el AuthService.

Define constantes y configuraciones que pueden ser personalizadas
para el servicio de autenticación.
"""

import os
from datetime import timedelta

class AuthServiceConfig:
    """Configuración del servicio de autenticación."""
    
    # Configuración de JWT
    JWT_ALGORITHM = 'HS256'
    JWT_ISSUER = 'puerta_orion_api'
    JWT_DEFAULT_EXPIRES_IN = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora por defecto
    
    # Configuración de sesiones
    SESSION_TOKEN_LENGTH = 32  # Longitud del token de sesión
    SESSION_CLEANUP_INTERVAL = 3600  # Limpiar sesiones expiradas cada hora
    
    # Configuración de seguridad
    MAX_LOGIN_ATTEMPTS = 5  # Máximo intentos de login por IP
    LOCKOUT_DURATION = 900  # 15 minutos de bloqueo
    
    # Configuración de validación
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 200
    MIN_PASSWORD_LENGTH = 6
    
    # Configuración de logging
    LOG_SUCCESSFUL_LOGINS = True
    LOG_FAILED_ATTEMPTS = True
    LOG_TOKEN_GENERATION = True
    LOG_SESSION_CREATION = True
    
    # Configuración de respuesta
    INCLUDE_USER_ROLES = True
    INCLUDE_PERSONA_DATA = True
    INCLUDE_SESSION_DATA = True
    
    # Mensajes de error personalizables
    # NOTA: 'password_required' es solo una clave de diccionario para mensajes de error, NO es una credencial hardcodeada
    # nosonar: S2068 - 'password' en strings es solo texto de mensajes, no credenciales hardcodeadas
    ERROR_MESSAGES = {
        'username_required': "El nombre de usuario es requerido",
        'password_required': "La contraseña es requerida",  # nosonar: S2068
        'username_too_short': f"El nombre de usuario debe tener al menos {MIN_USERNAME_LENGTH} caracteres",
        'invalid_credentials': "Credenciales inválidas",
        'user_inactive': "Usuario inactivo",
        'token_expired': "Token expirado",
        'token_invalid': "Token inválido",
        'session_error': "Error al registrar sesión",
        'jwt_key_missing': "JWT_SECRET_KEY no configurado",
        'token_generation_error': "Error al generar token",
        'session_close_error': "Error al cerrar sesión",
        'internal_error': "Error interno del servidor"
    }
    
    # Configuración de headers HTTP
    TOKEN_HEADER_NAME = 'Authorization'
    TOKEN_PREFIX = 'Bearer'
    
    # Configuración de IP y User Agent
    TRUST_PROXY_HEADERS = True
    PROXY_HEADERS = ['X-Forwarded-For', 'X-Real-IP']
    MAX_USER_AGENT_LENGTH = 500
    
    # Configuración de expiración por rol
    ROLE_EXPIRATION_TIMES = {
        'admin': 7200,      # 2 horas para admin
        'usuario': 3600,    # 1 hora para usuario
        'deportista': 3600, # 1 hora para deportista
        'acudiente': 3600   # 1 hora para acudiente
    }
    
    # Configuración de sesiones múltiples
    ALLOW_MULTIPLE_SESSIONS = True
    MAX_SESSIONS_PER_USER = 5
    
    # Configuración de limpieza automática
    AUTO_CLEANUP_EXPIRED_SESSIONS = True
    CLEANUP_BATCH_SIZE = 100


class JWTConfig:
    """Configuración específica para JWT."""
    
    # Algoritmos soportados
    SUPPORTED_ALGORITHMS = ['HS256', 'HS512']
    DEFAULT_ALGORITHM = 'HS256'
    
    # Configuración de claims estándar
    STANDARD_CLAIMS = {
        'iss': AuthServiceConfig.JWT_ISSUER,
        'aud': 'puerta_orion_frontend',
        'iat': True,  # Incluir fecha de emisión
        'exp': True,  # Incluir fecha de expiración
        'nbf': False, # No incluir "not before"
        'jti': True   # Incluir ID único del token
    }
    
    # Configuración de claims personalizados
    CUSTOM_CLAIMS = {
        'user_id': True,
        'username': True,
        'persona_id': True,
        'roles': True,
        'session_id': True
    }


class SessionConfig:
    """Configuración específica para sesiones."""
    
    # Configuración de tabla de sesiones
    TABLE_NAME = 'sesionauth'
    
    # Configuración de campos
    FIELDS = {
        'token_length': 32,
        'ip_length': 50,
        'user_agent_length': 500
    }
    
    # Configuración de limpieza
    CLEANUP_CONFIG = {
        'enabled': True,
        'interval': 3600,  # 1 hora
        'batch_size': 100,
        'retention_days': 30
    }


# Instancias globales de configuración
auth_config = AuthServiceConfig()
jwt_config = JWTConfig()
session_config = SessionConfig()


def get_expiration_time_for_role(role_name: str) -> int:
    """
    Obtiene el tiempo de expiración para un rol específico.
    
    Args:
        role_name (str): Nombre del rol
        
    Returns:
        int: Tiempo de expiración en segundos
    """
    return auth_config.ROLE_EXPIRATION_TIMES.get(role_name, auth_config.JWT_DEFAULT_EXPIRES_IN)


def is_multiple_sessions_allowed() -> bool:
    """
    Verifica si se permiten múltiples sesiones por usuario.
    
    Returns:
        bool: True si se permiten múltiples sesiones
    """
    return auth_config.ALLOW_MULTIPLE_SESSIONS


def get_max_sessions_per_user() -> int:
    """
    Obtiene el máximo número de sesiones por usuario.
    
    Returns:
        int: Máximo número de sesiones
    """
    return auth_config.MAX_SESSIONS_PER_USER


def should_log_operation(operation: str) -> bool:
    """
    Verifica si se debe registrar una operación específica.
    
    Args:
        operation (str): Tipo de operación
        
    Returns:
        bool: True si se debe registrar
    """
    log_config = {
        'login_success': auth_config.LOG_SUCCESSFUL_LOGINS,
        'login_failed': auth_config.LOG_FAILED_ATTEMPTS,
        'token_generation': auth_config.LOG_TOKEN_GENERATION,
        'session_creation': auth_config.LOG_SESSION_CREATION
    }
    
    return log_config.get(operation, True)
