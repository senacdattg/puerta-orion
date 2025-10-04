"""
Configuración para el middleware de autenticación.

Define constantes y configuraciones que pueden ser personalizadas
para el decorador de autenticación.
"""

import os
from typing import List, Optional

class AuthDecoratorConfig:
    """Configuración del decorador de autenticación."""
    
    # Configuración de headers
    AUTH_HEADER_NAME = 'Authorization'
    TOKEN_PREFIX = 'Bearer'
    
    # Configuración de validación
    REQUIRE_ACTIVE_SESSION = True
    REQUIRE_ACTIVE_USER = True
    VALIDATE_TOKEN_EXPIRATION = True
    
    # Configuración de logging
    LOG_AUTHENTICATION_SUCCESS = True
    LOG_AUTHENTICATION_FAILURE = True
    LOG_PERMISSION_DENIED = True
    LOG_SESSION_VALIDATION = True
    
    # Configuración de respuesta
    INCLUDE_USER_DATA = True
    INCLUDE_SESSION_DATA = True
    INCLUDE_TOKEN_PAYLOAD = True
    
    # Configuración de errores
    ERROR_MESSAGES = {
        'token_required': 'Token de autorización requerido',
        'token_invalid': 'Token inválido o expirado',
        'session_inactive': 'Sesión inactiva o expirada',
        'user_not_found': 'Usuario no encontrado',
        'user_inactive': 'Usuario inactivo',
        'insufficient_permissions': 'Permisos insuficientes',
        'internal_error': 'Error interno del servidor',
        'token_format_error': 'Formato de token inválido'
    }
    
    # Configuración de roles por defecto
    DEFAULT_ROLES = {
        'admin': ['admin'],
        'user': ['usuario'],
        'deportista': ['deportista'],
        'acudiente': ['acudiente']
    }
    
    # Configuración de tiempo de expiración de sesión
    SESSION_CHECK_INTERVAL = 300  # 5 minutos
    MAX_SESSION_AGE = 86400  # 24 horas
    
    # Configuración de IP y User Agent
    TRUST_PROXY_HEADERS = True
    PROXY_HEADERS = ['X-Forwarded-For', 'X-Real-IP']
    MAX_USER_AGENT_LENGTH = 500
    
    # Configuración de caché (para futuras implementaciones)
    ENABLE_SESSION_CACHE = False
    CACHE_TTL = 300  # 5 minutos
    CACHE_PREFIX = 'auth_session:'
    
    # Configuración de auditoría
    AUDIT_ENABLED = True
    AUDIT_LOG_LEVEL = 'INFO'
    AUDIT_INCLUDE_IP = True
    AUDIT_INCLUDE_USER_AGENT = True


class TokenValidationConfig:
    """Configuración específica para validación de tokens."""
    
    # Algoritmos soportados
    SUPPORTED_ALGORITHMS = ['HS256', 'HS512']
    DEFAULT_ALGORITHM = 'HS256'
    
    # Configuración de claims
    REQUIRED_CLAIMS = ['user_id', 'username', 'exp', 'iat']
    OPTIONAL_CLAIMS = ['persona_id', 'roles', 'session_id']
    
    # Configuración de expiración
    CLOCK_SKEW_TOLERANCE = 30  # 30 segundos de tolerancia
    MAX_TOKEN_AGE = 86400  # 24 horas máximo
    
    # Configuración de validación
    VALIDATE_ISSUER = True
    VALIDATE_AUDIENCE = False
    VALIDATE_SIGNATURE = True


class SessionValidationConfig:
    """Configuración específica para validación de sesiones."""
    
    # Configuración de tabla
    TABLE_NAME = 'sesionauth'
    
    # Configuración de campos
    REQUIRED_FIELDS = ['id_usuario', 'token_sesion', 'estado', 'fecha_expiracion']
    
    # Configuración de estado
    ACTIVE_STATE = True
    INACTIVE_STATE = False
    
    # Configuración de limpieza
    AUTO_CLEANUP_EXPIRED = True
    CLEANUP_INTERVAL = 3600  # 1 hora
    CLEANUP_BATCH_SIZE = 100


# Instancias globales de configuración
auth_decorator_config = AuthDecoratorConfig()
token_validation_config = TokenValidationConfig()
session_validation_config = SessionValidationConfig()


def get_error_message(error_key: str) -> str:
    """
    Obtiene un mensaje de error personalizado.
    
    Args:
        error_key (str): Clave del mensaje de error
        
    Returns:
        str: Mensaje de error
    """
    return auth_decorator_config.ERROR_MESSAGES.get(
        error_key, 
        'Error de autenticación'
    )


def get_default_roles_for_type(role_type: str) -> List[str]:
    """
    Obtiene los roles por defecto para un tipo específico.
    
    Args:
        role_type (str): Tipo de rol
        
    Returns:
        List[str]: Lista de roles
    """
    return auth_decorator_config.DEFAULT_ROLES.get(role_type, [])


def should_log_event(event_type: str) -> bool:
    """
    Verifica si se debe registrar un evento específico.
    
    Args:
        event_type (str): Tipo de evento
        
    Returns:
        bool: True si se debe registrar
    """
    log_config = {
        'auth_success': auth_decorator_config.LOG_AUTHENTICATION_SUCCESS,
        'auth_failure': auth_decorator_config.LOG_AUTHENTICATION_FAILURE,
        'permission_denied': auth_decorator_config.LOG_PERMISSION_DENIED,
        'session_validation': auth_decorator_config.LOG_SESSION_VALIDATION
    }
    
    return log_config.get(event_type, True)


def is_session_cache_enabled() -> bool:
    """
    Verifica si el caché de sesiones está habilitado.
    
    Returns:
        bool: True si está habilitado
    """
    return auth_decorator_config.ENABLE_SESSION_CACHE


def get_cache_key(session_id: str) -> str:
    """
    Genera la clave de caché para una sesión.
    
    Args:
        session_id (str): ID de la sesión
        
    Returns:
        str: Clave de caché
    """
    return f"{auth_decorator_config.CACHE_PREFIX}{session_id}"


def should_audit_event() -> bool:
    """
    Verifica si se debe auditar el evento.
    
    Returns:
        bool: True si se debe auditar
    """
    return auth_decorator_config.AUDIT_ENABLED


def get_audit_data(request_data: dict) -> dict:
    """
    Obtiene los datos de auditoría de una petición.
    
    Args:
        request_data (dict): Datos de la petición
        
    Returns:
        dict: Datos de auditoría
    """
    audit_data = {
        'timestamp': request_data.get('timestamp'),
        'endpoint': request_data.get('endpoint'),
        'method': request_data.get('method')
    }
    
    if auth_decorator_config.AUDIT_INCLUDE_IP:
        audit_data['ip'] = request_data.get('ip')
    
    if auth_decorator_config.AUDIT_INCLUDE_USER_AGENT:
        audit_data['user_agent'] = request_data.get('user_agent')
    
    return audit_data
