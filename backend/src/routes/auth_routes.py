"""
Rutas de autenticación para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints de registro y login
- Manejar autenticación de usuarios
- Proporcionar acceso a datos de perfil

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from flask import Blueprint, request, jsonify, current_app

from ..services.Auth.usuario_service import usuario_service, UsuarioServiceError
from ..services.Auth.auth_service import auth_service, AuthServiceError
from ..middleware.auth_decorator import token_required, get_current_user
from ..utils.logger import obtener_registrador


# Crear Blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = obtener_registrador('aplicacion')


@auth_bp.route('/register', methods=['POST'])
def registrar_usuario():
    """
    Endpoint para registrar un nuevo usuario.
    
    Recibe datos de persona y usuario, crea el registro completo
    con asignación automática del rol por defecto.
    
    Body JSON esperado:
    {
        "persona": {
            "primer_nombre": "Juan",
            "primer_apellido": "Pérez",
            "documento": 12345678,
            "correo_electronico": "juan@email.com",
            "direccion": "Calle 123",
            "telefono": 3001234567,
            "id_tipo_documento": 1,
            "id_sexo": 1
        },
        "usuario": {
            "usuario": "juan.perez",
            "password": "mi_contraseña_segura"
        }
    }
    
    Returns:
        JSON: Usuario creado con éxito o error
    """
    try:
        # Validar que la petición sea JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400
        
        # Obtener datos del JSON
        data = request.get_json()
        
        # Validar estructura básica
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos de registro requeridos',
                'status_code': 400
            }), 400
        
        # Extraer datos de persona y usuario
        datos_persona = data.get('persona')
        datos_usuario = data.get('usuario')
        
        if not datos_persona or not datos_usuario:
            return jsonify({
                'success': False,
                'error': 'Se requieren datos de persona y usuario',
                'status_code': 400
            }), 400
        
        # Registrar usuario usando el servicio
        usuario_creado = usuario_service.registrar_usuario_completo(
            datos_persona=datos_persona,
            datos_usuario=datos_usuario
        )
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'data': usuario_creado,
            'status_code': 201
        }), 201
        
    except UsuarioServiceError as e:
        logger.warning(f"Error de validación en registro: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 400
        }), 400
        
    except Exception as e:
        logger.error(f"Error inesperado en registro: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login_usuario():
    """
    Endpoint para autenticar un usuario.
    
    Recibe username y password, valida credenciales y retorna
    token JWT con datos del usuario.
    
    Body JSON esperado:
    {
        "username": "juan.perez",
        "password": "mi_contraseña_segura"
    }
    
    Returns:
        JSON: Token JWT y datos del usuario o error
    """
    try:
        # Validar que la petición sea JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400
        
        # Obtener datos del JSON
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos de login requeridos',
                'status_code': 400
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username y password son requeridos',
                'status_code': 400
            }), 400
        
        # Obtener información de la petición para la sesión
        ip_origen = _obtener_ip_origen()
        user_agent = _obtener_user_agent()
        
        # Autenticar usuario usando el servicio
        resultado_login = auth_service.autenticar_usuario(
            username=username,
            password=password,
            ip_origen=ip_origen,
            user_agent=user_agent
        )
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'data': resultado_login,
            'status_code': 200
        }), 200
        
    except AuthServiceError as e:
        logger.warning(f"Error de autenticación: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 401
        }), 401
        
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/perfil', methods=['GET'])
@token_required()
def obtener_perfil():
    """
    Endpoint para obtener el perfil del usuario autenticado.
    
    Requiere token JWT válido en el header Authorization.
    Retorna datos completos del usuario autenticado.
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Returns:
        JSON: Datos del perfil del usuario o error
    """
    try:
        # Obtener usuario autenticado del contexto
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado en el contexto',
                'status_code': 401
            }), 401
        
        # Preparar respuesta del perfil
        perfil_data = {
            'id_usuario': user['id_usuario'],
            'username': user['username'],
            'estado': user['estado'],
            'roles': user['roles'],
            'persona': {
                'id_persona': user['persona']['id_persona'],
                'nombre_completo': user['persona']['nombre_completo'],
                'primer_nombre': user['persona'].get('primer_nombre'),
                'primer_apellido': user['persona'].get('primer_apellido'),
                'correo_electronico': user['persona']['correo_electronico'],
                'documento': user['persona']['documento'],
                'telefono': user['persona']['telefono'],
                'direccion': user['persona'].get('direccion')
            }
        }
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Perfil obtenido exitosamente',
            'data': perfil_data,
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener perfil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@token_required()
def logout_usuario():
    """
    Endpoint para cerrar sesión del usuario autenticado.
    
    Requiere token JWT válido en el header Authorization.
    Invalida la sesión actual.
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Returns:
        JSON: Confirmación de logout o error
    """
    try:
        # Obtener token del header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Token de autorización requerido',
                'status_code': 401
            }), 401
        
        # Extraer token
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        # Cerrar sesión usando el servicio
        sesion_cerrada = auth_service.cerrar_sesion(token)
        
        if sesion_cerrada:
            return jsonify({
                'success': True,
                'message': 'Sesión cerrada exitosamente',
                'status_code': 200
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo cerrar la sesión',
                'status_code': 400
            }), 400
        
    except Exception as e:
        logger.error(f"Error inesperado en logout: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/verify-token', methods=['POST'])
def verificar_token():
    """
    Endpoint para verificar si un token JWT es válido.
    
    Recibe token JWT en el body y verifica su validez.
    
    Body JSON esperado:
    {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    
    Returns:
        JSON: Información del token o error
    """
    try:
        # Validar que la petición sea JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400
        
        # Obtener datos del JSON
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({
                'success': False,
                'error': 'Token requerido',
                'status_code': 400
            }), 400
        
        token = data['token']
        
        # Verificar token usando el servicio
        payload = auth_service.verificar_token_jwt(token)
        
        if payload:
            return jsonify({
                'success': True,
                'message': 'Token válido',
                'data': {
                    'user_id': payload.get('user_id'),
                    'username': payload.get('username'),
                    'roles': payload.get('roles'),
                    'expires_at': payload.get('exp'),
                    'issued_at': payload.get('iat')
                },
                'status_code': 200
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Token inválido o expirado',
                'status_code': 401
            }), 401
        
    except Exception as e:
        logger.error(f"Error inesperado al verificar token: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


# Funciones helper
def _obtener_ip_origen() -> str:
    """
    Obtiene la IP de origen de la petición.
    
    Returns:
        str: IP de origen
    """
    try:
        # Intentar obtener IP real (considerando proxies)
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    except:
        return '127.0.0.1'


def _obtener_user_agent() -> str:
    """
    Obtiene el User Agent de la petición.
    
    Returns:
        str: User Agent
    """
    try:
        return request.headers.get('User-Agent', 'Unknown')[:500]
    except:
        return 'Unknown'


# Manejadores de errores específicos del Blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    """Manejador de errores 400 (Bad Request)."""
    return jsonify({
        'success': False,
        'error': 'Solicitud incorrecta',
        'message': 'Verifique los datos enviados',
        'status_code': 400
    }), 400


@auth_bp.errorhandler(401)
def unauthorized(error):
    """Manejador de errores 401 (Unauthorized)."""
    return jsonify({
        'success': False,
        'error': 'No autorizado',
        'message': 'Token requerido o inválido',
        'status_code': 401
    }), 401


@auth_bp.errorhandler(403)
def forbidden(error):
    """Manejador de errores 403 (Forbidden)."""
    return jsonify({
        'success': False,
        'error': 'Acceso prohibido',
        'message': 'Permisos insuficientes',
        'status_code': 403
    }), 403


@auth_bp.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500 (Internal Server Error)."""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Contacte al administrador',
        'status_code': 500
    }), 500


# Función para registrar el Blueprint en la aplicación
def registrar_auth_routes(app):
    """
    Registra las rutas de autenticación en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(auth_bp)
    logger.info("Rutas de autenticación registradas exitosamente")
