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
from ..services.Auth.profile_completion_service import profile_completion_service, ProfileCompletionError
from ..middleware.auth_decorator import token_required, get_current_user
from ..utils.logger import obtener_registrador


# Crear Blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = obtener_registrador('aplicacion')


@auth_bp.route('/setup-roles', methods=['POST'])
def setup_roles():
    """
    Endpoint para configurar los roles básicos del sistema.
    """
    try:
        from ..models.roles_y_permisos.rol import Rol
        from ..models.base import db
        
        # Verificar si ya existen roles
        roles_existentes = Rol.query.count()
        if roles_existentes > 0:
            return jsonify({
                'success': True,
                'message': 'Los roles ya existen en el sistema',
                'total_roles': roles_existentes
            }), 200
        
        # Crear roles básicos
        roles_basicos = [
            {
                'nombre_rol': 'SuperAdmin',
                'descripcion': 'Super administrador del sistema con acceso completo'
            },
            {
                'nombre_rol': 'Administrador',
                'descripcion': 'Administrador del sistema'
            },
            {
                'nombre_rol': 'Entrenador',
                'descripcion': 'Entrenador deportivo'
            },
            {
                'nombre_rol': 'Deportista',
                'descripcion': 'Deportista registrado'
            },
            {
                'nombre_rol': 'Acudiente',
                'descripcion': 'Acudiente de deportistas'
            },
            {
                'nombre_rol': 'usuario',
                'descripcion': 'Rol por defecto para usuarios del sistema'
            }
        ]
        
        roles_creados = []
        for rol_data in roles_basicos:
            rol = Rol(**rol_data)
            db.session.add(rol)
            roles_creados.append(rol_data['nombre_rol'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Roles básicos creados exitosamente',
            'roles_creados': roles_creados,
            'total_roles': len(roles_creados)
        }), 200
        
    except Exception as e:
        logger.error(f"Error configurando roles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error configurando roles: {str(e)}',
            'status_code': 500
        }), 500


@auth_bp.route('/asignar-rol', methods=['POST'])
def asignar_rol():
    """
    Endpoint para asignar un rol específico a un usuario.
    """
    try:
        from ..models.roles_y_permisos.rol import Rol
        from ..models.roles_y_permisos.usuario_rol import UsuarioRol
        from ..models.usuarios.usuario import Usuario
        from ..models.base import db
        
        data = request.get_json()
        if not data or 'id_usuario' not in data or 'nombre_rol' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requieren id_usuario y nombre_rol',
                'status_code': 400
            }), 400
        
        # Buscar usuario
        usuario = Usuario.query.get(data['id_usuario'])
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'status_code': 404
            }), 404
        
        # Buscar rol
        rol = Rol.query.filter_by(nombre_rol=data['nombre_rol']).first()
        if not rol:
            return jsonify({
                'success': False,
                'error': f'Rol {data["nombre_rol"]} no encontrado',
                'status_code': 404
            }), 404
        
        # Verificar si ya tiene el rol
        usuario_rol_existente = UsuarioRol.query.filter_by(
            id_usuario=data['id_usuario'],
            id_rol=rol.id_rol
        ).first()
        
        if usuario_rol_existente:
            return jsonify({
                'success': True,
                'message': f'El usuario ya tiene el rol {data["nombre_rol"]}',
                'status_code': 200
            }), 200
        
        # Asignar rol
        usuario_rol = UsuarioRol(
            id_usuario=data['id_usuario'],
            id_rol=rol.id_rol
        )
        
        db.session.add(usuario_rol)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Rol {data["nombre_rol"]} asignado exitosamente',
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error asignando rol: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error asignando rol: {str(e)}',
            'status_code': 500
        }), 500


@auth_bp.route('/debug-roles', methods=['GET'])
def debug_roles():
    """
    Endpoint de depuración para verificar el estado de los roles.
    """
    try:
        from ..models.roles_y_permisos.rol import Rol
        from ..models.roles_y_permisos.usuario_rol import UsuarioRol
        
        # Verificar roles existentes
        roles = Rol.query.all()
        roles_data = []
        for rol in roles:
            roles_data.append({
                'id_rol': rol.id_rol,
                'nombre_rol': rol.nombre_rol,
                'descripcion': rol.descripcion
            })
        
        # Verificar relaciones usuario-rol
        usuario_roles = UsuarioRol.query.all()
        usuario_roles_data = []
        for ur in usuario_roles:
            usuario_roles_data.append({
                'id_usuario': ur.id_usuario,
                'id_rol': ur.id_rol
            })
        
        return jsonify({
            'success': True,
            'roles': roles_data,
            'usuario_roles': usuario_roles_data,
            'total_roles': len(roles_data),
            'total_usuario_roles': len(usuario_roles_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error en debug de roles: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error en debug: {str(e)}',
            'status_code': 500
        }), 500


@auth_bp.route('/register', methods=['POST'])
def registrar_usuario():
    """
    Endpoint para registrar un nuevo usuario.
    
    Recibe datos de persona y usuario, crea el registro completo
    con asignación automática del rol por defecto. Opcionalmente,
    puede crear un registro de Deportista o Acudiente si se especifica el rol.
    
    Body JSON esperado (registro básico):
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
    
    Body JSON esperado (registro como Deportista):
    {
        "persona": { ... },
        "usuario": { ... },
        "rol": "deportista",
        "datos_rol": {
            "id_categoria": 1,  // OBLIGATORIO
            "peso": 70.5,  // opcional
            "altura": 1.75,  // opcional
            "fecha_nacimiento": 2000,  // opcional (año)
            "id_tipo_sanguineo": 1,  // opcional
            "id_ciudad_recidencia": 1,  // opcional
            "id_mensualidad": 1,  // opcional
            "id_informacion_deportiva": 1,  // opcional
            "id_eps": 1  // opcional
        }
    }
    
    Body JSON esperado (registro como Acudiente):
    {
        "persona": { ... },
        "usuario": { ... },
        "rol": "acudiente",
        "datos_rol": {
            "estado": true  // opcional (por defecto true)
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
        rol_opcional = data.get('rol')  # 'deportista' o 'acudiente' (opcional)
        datos_rol = data.get('datos_rol', {})  # Datos adicionales para el rol
        
        if not datos_persona or not datos_usuario:
            return jsonify({
                'success': False,
                'error': 'Se requieren datos de persona y usuario',
                'status_code': 400
            }), 400
        
        # Validaciones básicas
        if not datos_persona.get('primer_nombre'):
            return jsonify({
                'success': False,
                'error': 'El primer nombre es requerido',
                'status_code': 400
            }), 400
        
        if not datos_persona.get('primer_apellido'):
            return jsonify({
                'success': False,
                'error': 'El primer apellido es requerido',
                'status_code': 400
            }), 400
        
        if not datos_persona.get('correo_electronico'):
            return jsonify({
                'success': False,
                'error': 'El correo electrónico es requerido',
                'status_code': 400
            }), 400
        
        if not datos_usuario.get('usuario'):
            return jsonify({
                'success': False,
                'error': 'El nombre de usuario es requerido',
                'status_code': 400
            }), 400
        
        if not datos_usuario.get('password'):
            return jsonify({
                'success': False,
                'error': 'La contraseña es requerida',
                'status_code': 400
            }), 400
        
        # Registrar usuario usando el servicio
        logger.info(f"Intentando registrar usuario: {datos_usuario.get('usuario', 'N/A')}")
        usuario_creado = usuario_service.registrar_usuario_completo(
            datos_persona=datos_persona,
            datos_usuario=datos_usuario,
            rol_opcional=rol_opcional,
            datos_rol=datos_rol
        )
        logger.info(f"Usuario registrado exitosamente: {usuario_creado.get('usuario', 'N/A')}")
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente',
            'data': usuario_creado,
            'status_code': 201
        }), 201
        
    except UsuarioServiceError as e:
        logger.warning(f"Error en registro de usuario: {str(e)}")
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
        
        # Validaciones básicas
        if len(username.strip()) < 3:
            return jsonify({
                'success': False,
                'error': 'El nombre de usuario debe tener al menos 3 caracteres',
                'status_code': 400
            }), 400
        
        if len(password.strip()) < 6:
            return jsonify({
                'success': False,
                'error': 'La contraseña debe tener al menos 6 caracteres',
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
        
        # Buscar si el usuario tiene un perfil de acudiente
        from ..models.acudientes.acudiente import Acudiente
        acudiente = Acudiente.query.filter_by(id_persona=user['persona']['id_persona'], estado=True).first()
        if acudiente:
            perfil_data['acudiente'] = {
                'id_acudiente': acudiente.id_acudiente,
                'estado': acudiente.estado
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
                    'usuario_id': payload.get('usuario_id'),
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


@auth_bp.route('/perfil/estado', methods=['GET'])
@token_required()
def verificar_estado_perfil():
    """
    Endpoint para verificar el estado del perfil del usuario autenticado.

    Verifica si el usuario ya completó su perfil como deportista o acudiente.

    Headers requeridos:
    Authorization: Bearer <token>

    Returns:
        JSON: Estado del perfil (es_deportista, es_acudiente, etc.)
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

        # Verificar estado del perfil usando el nuevo servicio
        estado_perfil = profile_completion_service.check_profile_status(user['id_usuario'])

        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Estado del perfil obtenido exitosamente',
            'data': estado_perfil,
            'status_code': 200
        }), 200

    except ProfileCompletionError as e:
        logger.warning(f"Error al verificar estado del perfil: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 400
        }), 400

    except Exception as e:
        logger.error(f"Error inesperado al verificar estado del perfil: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/perfil/completar-deportista', methods=['POST'])
@token_required()
def completar_perfil_deportista():
    """
    Endpoint para completar el perfil del usuario como deportista.

    Registra al usuario actual como deportista y le asigna el rol correspondiente.

    Headers requeridos:
    Authorization: Bearer <token>

    Body JSON esperado:
    {
        "id_categoria": 1,
        "peso": 70.5,
        "altura": 1.75,
        "fecha_nacimiento": 2000,
        "id_tipo_sanguineo": 1,
        "id_ciudad_recidencia": 1,
        "id_eps": 1,
        "alergias": "Ninguna",
        "medicamentos": "Ninguno",
        "condiciones_medicas": "Ninguna",
        "institucion_educativa": "Colegio ABC",
        "grado": "10",
        "jornada": "Mañana"
    }

    Returns:
        JSON: Información del deportista creado
    """
    try:
        # Validar que la petición sea JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400

        # Obtener usuario autenticado del contexto
        user = get_current_user()

        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado en el contexto',
                'status_code': 401
            }), 401

        # Obtener datos del JSON
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos requeridos para completar perfil',
                'status_code': 400
            }), 400

        # Completar perfil usando el nuevo servicio unificado
        resultado = profile_completion_service.complete_profile(
            usuario_id=user['id_usuario'],
            profile_type='deportista',
            profile_data=data
        )

        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': resultado.message,
            'data': resultado.data,
            'status_code': 201
        }), 201

    except ProfileCompletionError as e:
        logger.warning(f"Error al completar perfil como deportista: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 400
        }), 400

    except Exception as e:
        logger.error(f"Error inesperado al completar perfil como deportista: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/perfil/completar-acudiente', methods=['POST'])
@token_required()
def completar_perfil_acudiente():
    """
    Endpoint para completar el perfil del usuario como acudiente.

    Registra al usuario actual como acudiente y le asigna el rol correspondiente.

    Headers requeridos:
    Authorization: Bearer <token>

    Body JSON esperado (opcional):
    {
        "parentesco": "Padre",
        "ocupacion": "Ingeniero",
        "lugar_trabajo": "Empresa ABC",
        "telefono_trabajo": "3001234567",
        "telefono_emergencia": "3019876543",
        "autorizacion_imagenes": true,
        "autorizacion_salidas": true,
        "autorizacion_medica": true,
        "observaciones": "Observaciones adicionales"
    }

    Returns:
        JSON: Información del acudiente creado
    """
    try:
        # Validar que la petición sea JSON si hay body
        if request.content_length and request.content_length > 0 and not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400

        # Obtener usuario autenticado del contexto
        user = get_current_user()

        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado en el contexto',
                'status_code': 401
            }), 401

        # Obtener datos del JSON (puede ser vacío para acudientes)
        data = request.get_json() if request.is_json else {}
        
        # Validar edad mínima para acudientes (18 años)
        from src.models.deportistas.deportista import Deportista
        from datetime import date
        
        deportista = Deportista.query.filter_by(id_persona=user.get('persona', {}).get('id_persona')).first()
        if deportista and deportista.fecha_nacimiento:
            edad = date.today().year - deportista.fecha_nacimiento
            if edad < 18:
                return jsonify({
                    'success': False,
                    'error': f'Para ser acudiente debe ser mayor de edad. Su edad actual es {edad} años.',
                    'status_code': 400
                }), 400

        # Completar perfil usando el nuevo servicio unificado
        resultado = profile_completion_service.complete_profile(
            usuario_id=user['id_usuario'],
            profile_type='acudiente',
            profile_data=data
        )

        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': resultado.message,
            'data': resultado.data,
            'status_code': 201
        }), 201

    except ProfileCompletionError as e:
        logger.warning(f"Error al completar perfil como acudiente: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 400
        }), 400

    except Exception as e:
        logger.error(f"Error inesperado al completar perfil como acudiente: {str(e)}")
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
