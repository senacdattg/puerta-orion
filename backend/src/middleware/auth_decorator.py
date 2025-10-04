"""
Decorador de autenticación para Flask.

Responsabilidad:
- Validar tokens JWT en rutas protegidas
- Verificar sesiones activas en base de datos
- Inyectar usuario autenticado en el contexto de la request
- Manejar errores de autenticación de forma consistente

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

import jwt
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable
from flask import request, jsonify, g, current_app

from ..models.base import db
from ..models.usuarios.usuario import Usuario
from ..models.eventos.sesionAuth import SesionAuth
from ..services.Auth.auth_service import auth_service
from ..utils.logger import obtener_registrador


class TokenRequiredError(Exception):
    """Excepción personalizada para errores del decorador de autenticación."""
    pass


class TokenRequired:
    """
    Decorador para validar tokens JWT y sesiones activas.
    
    Valida que el token JWT sea válido, no esté expirado y que la sesión
    correspondiente esté activa en la base de datos.
    """
    
    def __init__(self, required_roles: Optional[list] = None):
        """
        Inicializa el decorador.
        
        Args:
            required_roles (list, optional): Lista de roles requeridos para acceder
        """
        self.required_roles = required_roles or []
        self.logger = obtener_registrador('aplicacion')
    
    def __call__(self, f: Callable) -> Callable:
        """
        Implementa el decorador.
        
        Args:
            f (Callable): Función a decorar
            
        Returns:
            Callable: Función decorada
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extraer token del header Authorization
                token = self._extraer_token()
                if not token:
                    return self._error_response("Token de autorización requerido", 401)
                
                # Validar token JWT
                payload = self._validar_token_jwt(token)
                if not payload:
                    return self._error_response("Token inválido o expirado", 401)
                
                # Verificar sesión activa
                sesion = self._verificar_sesion_activa(token, payload)
                if not sesion:
                    return self._error_response("Sesión inactiva o expirada", 401)
                
                # Obtener usuario completo
                usuario = self._obtener_usuario_completo(payload['user_id'])
                if not usuario:
                    return self._error_response("Usuario no encontrado", 401)
                
                # Verificar roles si se especificaron
                if self.required_roles:
                    if not self._verificar_roles(usuario, self.required_roles):
                        return self._error_response("Permisos insuficientes", 403)
                
                # Inyectar datos en el contexto global
                self._inyectar_datos_usuario(usuario, sesion, payload)
                
                # Ejecutar función original
                return f(*args, **kwargs)
                
            except TokenRequiredError as e:
                self.logger.warning(f"Error de autenticación: {str(e)}")
                return self._error_response(str(e), 401)
            except Exception as e:
                self.logger.error(f"Error inesperado en autenticación: {str(e)}")
                return self._error_response("Error interno del servidor", 500)
        
        return decorated_function
    
    def _extraer_token(self) -> Optional[str]:
        """
        Extrae el token JWT del header Authorization.
        
        Returns:
            str: Token JWT o None si no se encuentra
        """
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return None
            
            # Verificar formato "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
            
            return parts[1]
            
        except Exception as e:
            self.logger.error(f"Error al extraer token: {str(e)}")
            return None
    
    def _validar_token_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Valida el token JWT usando el AuthService.
        
        Args:
            token (str): Token JWT a validar
            
        Returns:
            Dict: Payload del token si es válido, None en caso contrario
        """
        try:
            payload = auth_service.verificar_token_jwt(token)
            return payload
            
        except Exception as e:
            self.logger.error(f"Error al validar token JWT: {str(e)}")
            return None
    
    def _verificar_sesion_activa(self, token: str, payload: Dict[str, Any]) -> Optional[SesionAuth]:
        """
        Verifica que la sesión esté activa en la base de datos.
        
        Args:
            token (str): Token JWT
            payload (Dict): Payload del token
            
        Returns:
            SesionAuth: Sesión activa o None
        """
        try:
            # Buscar sesión por token (asumiendo que el token de sesión está en el JWT)
            # En una implementación real, podrías tener un campo session_id en el JWT
            sesion = SesionAuth.query.filter_by(
                id_usuario=payload['user_id'],
                estado=True
            ).filter(
                SesionAuth.fecha_expiracion > datetime.utcnow()
            ).first()
            
            if not sesion:
                return None
            
            # Verificar que el token de sesión coincida (si está disponible)
            # Esto depende de cómo implementes la relación entre JWT y sesión
            return sesion
            
        except Exception as e:
            self.logger.error(f"Error al verificar sesión activa: {str(e)}")
            return None
    
    def _obtener_usuario_completo(self, user_id: int) -> Optional[Usuario]:
        """
        Obtiene el usuario completo con sus roles.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            Usuario: Usuario completo o None
        """
        try:
            usuario = Usuario.query.filter_by(
                id_usuario=user_id,
                estado=True
            ).first()
            
            return usuario
            
        except Exception as e:
            self.logger.error(f"Error al obtener usuario: {str(e)}")
            return None
    
    def _verificar_roles(self, usuario: Usuario, required_roles: list) -> bool:
        """
        Verifica que el usuario tenga los roles requeridos.
        
        Args:
            usuario (Usuario): Usuario a verificar
            required_roles (list): Roles requeridos
            
        Returns:
            bool: True si tiene los roles requeridos
        """
        try:
            if not hasattr(usuario, 'roles') or not usuario.roles:
                return False
            
            user_roles = [rol.nombre_rol for rol in usuario.roles]
            
            # Verificar que tenga al menos uno de los roles requeridos
            return any(role in user_roles for role in required_roles)
            
        except Exception as e:
            self.logger.error(f"Error al verificar roles: {str(e)}")
            return False
    
    def _inyectar_datos_usuario(self, usuario: Usuario, sesion: SesionAuth, payload: Dict[str, Any]) -> None:
        """
        Inyecta los datos del usuario autenticado en el contexto global.
        
        Args:
            usuario (Usuario): Usuario autenticado
            sesion (SesionAuth): Sesión activa
            payload (Dict): Payload del token JWT
        """
        try:
            # Obtener roles del usuario
            roles_usuario = []
            if hasattr(usuario, 'roles') and usuario.roles:
                roles_usuario = [rol.to_dict() for rol in usuario.roles]
            
            # Inyectar en el contexto global de Flask
            g.current_user = {
                'id_usuario': usuario.id_usuario,
                'username': usuario.usuario,
                'estado': usuario.estado,
                'roles': roles_usuario,
                'persona': {
                    'id_persona': usuario.persona.id_persona,
                    'nombre_completo': usuario.persona.nombre_completo,
                    'correo_electronico': usuario.persona.correo_electronico,
                    'documento': usuario.persona.documento
                }
            }
            
            g.current_session = {
                'id_sesion': sesion.id_sesion,
                'fecha_inicio': sesion.fecha_inicio.isoformat(),
                'fecha_expiracion': sesion.fecha_expiracion.isoformat(),
                'ip_origen': sesion.ip_origen
            }
            
            g.token_payload = payload
            
            self.logger.info(f"Usuario autenticado: {usuario.usuario} (ID: {usuario.id_usuario})")
            
        except Exception as e:
            self.logger.error(f"Error al inyectar datos de usuario: {str(e)}")
            raise TokenRequiredError("Error al procesar datos de usuario")
    
    def _error_response(self, message: str, status_code: int) -> tuple:
        """
        Genera una respuesta de error consistente.
        
        Args:
            message (str): Mensaje de error
            status_code (int): Código de estado HTTP
            
        Returns:
            tuple: Respuesta JSON con error
        """
        return jsonify({
            'success': False,
            'error': message,
            'status_code': status_code
        }), status_code


# Función helper para crear el decorador
def token_required(required_roles: Optional[list] = None):
    """
    Decorador para validar tokens JWT y sesiones activas.
    
    Args:
        required_roles (list, optional): Lista de roles requeridos
        
    Returns:
        Callable: Decorador configurado
        
    Usage:
        @token_required()
        def protected_route():
            return jsonify({'message': 'Acceso autorizado'})
        
        @token_required(['admin'])
        def admin_route():
            return jsonify({'message': 'Solo para administradores'})
    """
    return TokenRequired(required_roles)


# Decoradores específicos para roles comunes
def admin_required(f: Callable) -> Callable:
    """
    Decorador específico para rutas que requieren rol de administrador.
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada
    """
    return token_required(['admin'])(f)


def user_required(f: Callable) -> Callable:
    """
    Decorador específico para rutas que requieren rol de usuario.
    
    Args:
        f (Callable): Función a decorar
        
    Returns:
        Callable: Función decorada
    """
    return token_required(['usuario'])(f)


def any_role_required(*roles: str):
    """
    Decorador para rutas que requieren cualquiera de los roles especificados.
    
    Args:
        *roles: Roles permitidos
        
    Returns:
        Callable: Decorador configurado
    """
    return token_required(list(roles))


# Funciones helper para acceder a los datos inyectados
def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Obtiene el usuario autenticado actual.
    
    Returns:
        Dict: Datos del usuario autenticado o None
    """
    return getattr(g, 'current_user', None)


def get_current_session() -> Optional[Dict[str, Any]]:
    """
    Obtiene la sesión actual.
    
    Returns:
        Dict: Datos de la sesión actual o None
    """
    return getattr(g, 'current_session', None)


def get_token_payload() -> Optional[Dict[str, Any]]:
    """
    Obtiene el payload del token JWT actual.
    
    Returns:
        Dict: Payload del token o None
    """
    return getattr(g, 'token_payload', None)


def has_role(role_name: str) -> bool:
    """
    Verifica si el usuario actual tiene un rol específico.
    
    Args:
        role_name (str): Nombre del rol a verificar
        
    Returns:
        bool: True si tiene el rol
    """
    user = get_current_user()
    if not user or 'roles' not in user:
        return False
    
    return any(role['nombre_rol'] == role_name for role in user['roles'])


def has_any_role(*role_names: str) -> bool:
    """
    Verifica si el usuario actual tiene alguno de los roles especificados.
    
    Args:
        *role_names: Nombres de roles a verificar
        
    Returns:
        bool: True si tiene alguno de los roles
    """
    user = get_current_user()
    if not user or 'roles' not in user:
        return False
    
    user_roles = [role['nombre_rol'] for role in user['roles']]
    return any(role in user_roles for role in role_names)
