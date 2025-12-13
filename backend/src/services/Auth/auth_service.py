"""
Servicio de autenticación para el sistema Puerta Orion.

Responsabilidad:
- Validar credenciales de usuario
- Generar tokens JWT con información de usuario y roles
- Registrar sesiones de autenticación
- Manejar expiración de tokens

Este módulo sigue los principios SRP, KISS, DRY y SOLID.

"""

import jwt

import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from flask import current_app, request
from werkzeug.security import check_password_hash
from sqlalchemy.exc import IntegrityError

from ...models.base import db
from ...models.usuarios.usuario import Usuario
from ...models.eventos.sesionAuth import SesionAuth
from ...utils.logger import obtener_registrador
from .role_permission_service import asegurar_rol_activo_valido

class AuthServiceError(Exception):
    """Excepción personalizada para errores del servicio de autenticación."""
    pass


class AuthService:
    """
    Servicio para gestión de autenticación.
    
    Encapsula toda la lógica de negocio relacionada con el login,
    generación de tokens JWT y gestión de sesiones.
    """
    
    def __init__(self):
        """Inicializa el servicio con el logger configurado."""
        self.logger = obtener_registrador('aplicacion')
    
    def autenticar_usuario(
        self, 
        username: str, 
        password: str,
        ip_origen: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña en texto plano
            ip_origen (str): IP de origen de la petición
            user_agent (str): User agent del cliente
            
        Returns:
            Dict: Token JWT y datos del usuario
            
        Raises:
            AuthServiceError: Si las credenciales son inválidas o hay errores
        """
        try:
            # Validar datos de entrada
            self._validar_datos_login(username, password)
            
            # Verificar credenciales
            usuario = self._verificar_credenciales(username, password)
            if not usuario:
                raise AuthServiceError("Credenciales inválidas")
            
            asegurar_rol_activo_valido(usuario, commit=False)
            
            # Generar token JWT
            token_jwt = self._generar_token_jwt(usuario)
            
            # Registrar sesión
            sesion = self._registrar_sesion(usuario, ip_origen, user_agent)
            
            # Preparar respuesta
            respuesta = self._preparar_respuesta_login(usuario, token_jwt, sesion)
            
            self.logger.info(f"Login exitoso para usuario: {username}")
            
            return respuesta
            
        except AuthServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado en autenticación: {str(e)}")
            raise AuthServiceError(f"Error interno del servidor: {str(e)}")
    
    def _validar_datos_login(self, username: str, password: str) -> None:
        """
        Valida los datos de entrada para el login.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Raises:
            AuthServiceError: Si los datos son inválidos
        """
        if not username or not username.strip():
            raise AuthServiceError("El nombre de usuario es requerido")
        
        if not password or not password.strip():
            raise AuthServiceError("La contraseña es requerida")
        
        if len(username.strip()) < 3:
            raise AuthServiceError("El nombre de usuario debe tener al menos 3 caracteres")
    
    def _verificar_credenciales(self, username: str, password: str) -> Optional[Usuario]:
        """
        Verifica las credenciales del usuario.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña en texto plano
            
        Returns:
            Usuario: Usuario si las credenciales son válidas, None en caso contrario
        """
        try:
            usuario = Usuario.query.filter_by(usuario=username.strip(), estado=True).first()
            
            if usuario and check_password_hash(usuario.password, password):
                return usuario
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error al verificar credenciales: {str(e)}")
            return None
    
    def _generar_token_jwt(self, usuario: Usuario) -> str:
        """
        Genera un token JWT para el usuario autenticado.
        
        Args:
            usuario (Usuario): Usuario autenticado
            
        Returns:
            str: Token JWT generado
            
        Raises:
            AuthServiceError: Si hay errores al generar el token
        """
        try:
            # Obtener configuración de JWT
            secret_key = current_app.config.get('JWT_SECRET_KEY')
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            
            if not secret_key:
                raise AuthServiceError("JWT_SECRET_KEY no configurado")
            
            # Convertir expires_in a segundos si es timedelta
            if isinstance(expires_in, timedelta):
                expires_seconds = int(expires_in.total_seconds())
            else:
                expires_seconds = int(expires_in)
            
            # Calcular fecha de expiración
            expiracion = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
            
            # Obtener roles del usuario
            roles_usuario = []
            if hasattr(usuario, 'roles') and usuario.roles:
                roles_usuario = [rol.nombre_rol for rol in usuario.roles]
            
            rol_activo = usuario.rol_activo.nombre_rol if getattr(usuario, 'rol_activo', None) else None
            
            # Payload del token
            payload = {
                'usuario_id': usuario.id_usuario,
                'username': usuario.usuario,
                'persona_id': usuario.id_persona,
                'roles': roles_usuario,
                'rol_activo': rol_activo,
                'exp': expiracion,
                'iat': datetime.now(timezone.utc),
                'iss': 'puerta_orion_api'
            }
            
            # Generar token
            token = jwt.encode(payload, secret_key, algorithm='HS256')
            
            self.logger.info(f"Token JWT generado para usuario: {usuario.usuario}")
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error al generar token JWT: {str(e)}")
            raise AuthServiceError(f"Error al generar token: {str(e)}")
    
    def _registrar_sesion(
        self, 
        usuario: Usuario, 
        ip_origen: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SesionAuth:
        """
        Registra la sesión de autenticación en la base de datos.
        
        Args:
            usuario (Usuario): Usuario autenticado
            ip_origen (str): IP de origen
            user_agent (str): User agent del cliente
            
        Returns:
            SesionAuth: Sesión registrada
            
        Raises:
            AuthServiceError: Si hay errores al registrar la sesión
        """
        try:
            # Obtener configuración de expiración
            expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
            if isinstance(expires_in, timedelta):
                expires_seconds = int(expires_in.total_seconds())
            else:
                expires_seconds = int(expires_in)
            fecha_expiracion = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)
            
            # Generar token único para la sesión
            token_sesion = self._generar_token_sesion()
            
            # Crear sesión
            sesion = SesionAuth(
                id_usuario=usuario.id_usuario,
                token_sesion=token_sesion,
                fecha_inicio=datetime.now(timezone.utc),
                fecha_expiracion=fecha_expiracion,
                ip_origen=ip_origen or self._obtener_ip_origen(),
                user_agent=user_agent or self._obtener_user_agent(),
                estado=True
            )
            
            db.session.add(sesion)
            db.session.commit()
            
            self.logger.info(f"Sesión registrada para usuario: {usuario.usuario}")
            
            return sesion
            
        except IntegrityError as e:
            db.session.rollback()
            self.logger.error(f"Error de integridad al registrar sesión: {str(e)}")
            raise AuthServiceError("Error al registrar sesión")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error al registrar sesión: {str(e)}")
            raise AuthServiceError(f"Error al registrar sesión: {str(e)}")
    
    def _generar_token_sesion(self) -> str:
        """
        Genera un token único para la sesión.
        
        Returns:
            str: Token único para la sesión
        """
        return secrets.token_urlsafe(32)
    
    def _obtener_ip_origen(self) -> str:
        """
        Obtiene la IP de origen de la petición.
        
        Returns:
            str: IP de origen
        """
        try:
            if request:
                # Intentar obtener IP real (considerando proxies)
                if request.headers.get('X-Forwarded-For'):
                    return request.headers.get('X-Forwarded-For').split(',')[0].strip()
                elif request.headers.get('X-Real-IP'):
                    return request.headers.get('X-Real-IP')
                else:
                    return request.remote_addr or '127.0.0.1'
            return '127.0.0.1'
        except Exception:
            return '127.0.0.1'
    
    def _obtener_user_agent(self) -> str:
        """
        Obtiene el User Agent de la petición.
        
        Returns:
            str: User Agent
        """
        try:
            if request:
                return request.headers.get('User-Agent', 'Unknown')[:500]
            return 'Unknown'
        except Exception:
            return 'Unknown'
    
    def _preparar_respuesta_login(
        self, 
        usuario: Usuario, 
        token_jwt: str, 
        sesion: SesionAuth
    ) -> Dict[str, Any]:
        """
        Prepara la respuesta del login con todos los datos necesarios.
        
        Args:
            usuario (Usuario): Usuario autenticado
            token_jwt (str): Token JWT generado
            sesion (SesionAuth): Sesión registrada
            
        Returns:
            Dict: Respuesta completa del login
        """
        # Obtener roles del usuario
        roles_usuario = []
        if hasattr(usuario, 'roles') and usuario.roles:
            roles_usuario = [rol.to_dict() for rol in usuario.roles]
        
        rol_activo = usuario.rol_activo.nombre_rol if getattr(usuario, 'rol_activo', None) else None
        
        persona_data = None
        if getattr(usuario, 'persona', None):
            persona_data = {
                'id_persona': usuario.persona.id_persona,
                'nombre_completo': usuario.persona.nombre_completo,
                'correo_electronico': usuario.persona.correo_electronico,
                'documento': usuario.persona.documento
            }

        return {
            'success': True,
            'message': 'Login exitoso',
            'token': token_jwt,
            'token_type': 'Bearer',
            'expires_in': current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600),
            'user': {
                'id_usuario': usuario.id_usuario,
                'username': usuario.usuario,
                'estado': usuario.estado,
                'rol_activo': rol_activo,
                'roles': roles_usuario,
                'persona': persona_data
            },
            'session': {
                'id_sesion': sesion.id_sesion,
                'fecha_inicio': sesion.fecha_inicio.isoformat(),
                'fecha_expiracion': sesion.fecha_expiracion.isoformat(),
                'ip_origen': sesion.ip_origen
            }
        }
    
    def verificar_token_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token (str): Token JWT a verificar
            
        Returns:
            Dict: Payload del token si es válido, None en caso contrario
        """
        try:
            # Validar formato del token
            if not token or len(token.split('.')) != 3:
                self.logger.warning("Token JWT con formato inválido")
                return None
            
            secret_key = current_app.config.get('JWT_SECRET_KEY')
            if not secret_key:
                self.logger.error("JWT_SECRET_KEY no configurado")
                return None
            
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Verificar que el token no esté expirado
            exp_timestamp = payload.get('exp')
            import time
            current_timestamp = int(time.time())
            
            if exp_timestamp and current_timestamp > exp_timestamp:
                self.logger.warning("Token JWT expirado")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Token JWT inválido: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error al verificar token JWT: {str(e)}")
            return None
    
    def cerrar_sesion(self, token: str) -> bool:
        """
        Cierra una sesión invalidando el token.
        
        Args:
            token (str): Token JWT a invalidar
            
        Returns:
            bool: True si se cerró exitosamente, False en caso contrario
        """
        try:
            # Verificar y decodificar el token JWT para obtener el usuario_id
            payload = self.verificar_token_jwt(token)
            if not payload:
                self.logger.warning("Token JWT inválido o expirado para logout")
                return False
            
            usuario_id = payload.get('usuario_id')
            if not usuario_id:
                self.logger.warning("Token JWT no contiene usuario_id")
                return False
            
            # Buscar sesiones activas del usuario y cerrarlas
            sesiones_activas = SesionAuth.query.filter_by(
                id_usuario=usuario_id,
                estado=True
            ).filter(
                SesionAuth.fecha_expiracion > datetime.now(timezone.utc)
            ).all()
            
            if sesiones_activas:
                for sesion in sesiones_activas:
                    sesion.estado = False
                
                db.session.commit()
                self.logger.info(f"Sesión cerrada para usuario ID: {usuario_id}")
                return True
            
            # Si no hay sesiones activas, consideramos el logout exitoso
            self.logger.info(f"No hay sesiones activas para usuario ID: {usuario_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al cerrar sesión: {str(e)}")
            return False
    
    def obtener_sesiones_activas(self, id_usuario: int) -> list:
        """
        Obtiene las sesiones activas de un usuario.
        
        Args:
            id_usuario (int): ID del usuario
            
        Returns:
            list: Lista de sesiones activas
        """
        try:
            sesiones = SesionAuth.query.filter_by(
                id_usuario=id_usuario,
                estado=True
            ).filter(
                SesionAuth.fecha_expiracion > datetime.now(timezone.utc)
            ).all()
            
            return [sesion.to_dict() for sesion in sesiones]
            
        except Exception as e:
            self.logger.error(f"Error al obtener sesiones activas: {str(e)}")
            return []


# Instancia global del servicio para uso en la aplicación
auth_service = AuthService()
