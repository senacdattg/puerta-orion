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
from ..services.Auth.usuario_service import usuario_service


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



@auth_bp.route('/user-permissions', methods=['GET'])
@token_required()
def obtener_permisos_usuario():
    """
    Endpoint para obtener los permisos específicos del usuario autenticado.
    """
    try:
        # Obtener usuario actual
        usuario_data = get_current_user()
        if not usuario_data:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'status_code': 401
            }), 401
        
        # Obtener el objeto Usuario desde la base de datos
        from ..models.usuarios.usuario import Usuario
        usuario_actual = Usuario.query.get(usuario_data['id_usuario'])
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'status_code': 404
            }), 404
        
        # Obtener todos los permisos del usuario a través de sus roles
        permisos_usuario = set()
        roles_info = []
        
        if hasattr(usuario_actual, 'roles') and usuario_actual.roles:
            for rol in usuario_actual.roles:
                roles_info.append({
                    'id_rol': rol.id_rol,
                    'nombre_rol': rol.nombre_rol,
                    'descripcion': rol.descripcion
                })
                
                # Obtener permisos del rol
                if hasattr(rol, 'permisos') and rol.permisos:
                    for permiso in rol.permisos:
                        permisos_usuario.add(permiso.nombre)
        
        # Convertir set a lista ordenada
        permisos_lista = sorted(list(permisos_usuario))
        
        return jsonify({
            'success': True,
            'data': {
                'usuario': {
                    'id_usuario': usuario_actual.id_usuario,
                    'username': usuario_actual.usuario
                },
                'roles': roles_info,
                'permisos': permisos_lista,
                'total_permisos': len(permisos_lista)
            },
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo permisos del usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo permisos: {str(e)}',
            'status_code': 500
        }), 500


@auth_bp.route('/role-permissions', methods=['GET'])
@token_required()
def obtener_permisos_por_rol():
    """
    Endpoint para obtener los permisos de un rol específico.
    Requiere el nombre del rol como parámetro de consulta 'role_name'.
    Solo devuelve permisos si el usuario autenticado tiene ese rol.
    """
    try:
        # Obtener usuario actual
        usuario_data = get_current_user()
        if not usuario_data:
            return jsonify({
                'success': False,
                'error': 'Usuario no autenticado',
                'status_code': 401
            }), 401
        
        # Obtener el nombre del rol del query string
        role_name = request.args.get('role_name')
        if not role_name:
            return jsonify({
                'success': False,
                'error': 'Parámetro "role_name" es requerido',
                'status_code': 400
            }), 400
        
        # Obtener el objeto Usuario desde la base de datos
        from ..models.usuarios.usuario import Usuario
        from ..models.roles_y_permisos.rol import Rol
        usuario_actual = Usuario.query.get(usuario_data['id_usuario'])
        if not usuario_actual:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'status_code': 404
            }), 404
        
        # Verificar que el usuario tenga el rol solicitado
        tiene_rol = False
        if hasattr(usuario_actual, 'roles') and usuario_actual.roles:
            tiene_rol = any(rol.nombre_rol == role_name for rol in usuario_actual.roles)
        
        if not tiene_rol:
            return jsonify({
                'success': False,
                'error': f'El usuario no tiene el rol "{role_name}"',
                'status_code': 403
            }), 403
        
        # Buscar el rol en la base de datos
        rol = Rol.query.filter_by(nombre_rol=role_name).first()
        if not rol:
            return jsonify({
                'success': False,
                'error': f'Rol "{role_name}" no encontrado',
                'status_code': 404
            }), 404
        
        # Obtener permisos del rol
        permisos_rol = []
        if hasattr(rol, 'permisos') and rol.permisos:
            permisos_rol = [permiso.nombre for permiso in rol.permisos]
        
        # Ordenar permisos
        permisos_lista = sorted(permisos_rol)
        
        return jsonify({
            'success': True,
            'data': {
                'rol': {
                    'id_rol': rol.id_rol,
                    'nombre_rol': rol.nombre_rol,
                    'descripcion': rol.descripcion
                },
                'permisos': permisos_lista,
                'total_permisos': len(permisos_lista)
            },
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f'Error al obtener permisos del rol: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
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
        
        # Validar que exista persona en el usuario
        if not user.get('persona'):
            logger.error(f"Usuario {user.get('id_usuario')} no tiene persona asociada")
            return jsonify({
                'success': False,
                'error': 'El usuario no tiene una persona asociada',
                'status_code': 400
            }), 400
        
        persona = user['persona']
        
        # Preparar respuesta del perfil
        perfil_data = {
            'id_usuario': user.get('id_usuario'),
            'username': user.get('username'),
            'estado': user.get('estado'),
            'roles': user.get('roles', []),
            'persona': {
                'id_persona': persona.get('id_persona'),
                'nombre_completo': persona.get('nombre_completo', ''),
                'primer_nombre': persona.get('primer_nombre'),
                'primer_apellido': persona.get('primer_apellido'),
                'correo_electronico': persona.get('correo_electronico'),
                'documento': persona.get('documento'),
                'telefono': persona.get('telefono'),
                'direccion': persona.get('direccion')
            }
        }
        
        # Buscar si el usuario tiene un perfil de acudiente
        acudiente = None
        if persona.get('id_persona'):
            from ..models.acudientes.acudiente import Acudiente
            acudiente = Acudiente.query.filter_by(id_persona=persona['id_persona'], estado=True).first()
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
        
    except KeyError as e:
        logger.error(f"Error de clave faltante al obtener perfil: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error en los datos del usuario: {str(e)}',
            'status_code': 500
        }), 500
    except Exception as e:
        logger.error(f"Error inesperado al obtener perfil: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@auth_bp.route('/perfil/detalle', methods=['GET'])
@token_required()
def obtener_perfil_detalle():
    """
    Endpoint para obtener la información completa del usuario autenticado,
    incluyendo datos por rol (deportista, acudiente).

    Headers requeridos:
    Authorization: Bearer <token>
    """
    try:
        user = get_current_user()
        if not user:
            logger.warning("⚠️ Usuario no encontrado en el contexto de autenticación")
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado en el contexto',
                'status_code': 401
            }), 401

        usuario_id = user.get('id_usuario')
        username = user.get('username')
        logger.info(f"[PERFIL] Obteniendo detalle para usuario ID: {usuario_id} (username: {username})")
        
        # Verificar que el ID del usuario sea válido
        if not usuario_id or not isinstance(usuario_id, int):
            logger.error(f"[PERFIL] ID de usuario invalido: {usuario_id} (tipo: {type(usuario_id)})")
            return jsonify({
                'success': False,
                'error': 'ID de usuario inválido',
                'status_code': 400
            }), 400
        
        # Obtener el objeto Usuario del contexto si está disponible
        from flask import g
        usuario_obj = getattr(g, 'current_user_obj', None)
        if usuario_obj:
            logger.info(f"[PERFIL] Objeto Usuario obtenido del contexto: {usuario_obj.usuario}")
        else:
            logger.warning(f"[PERFIL] No se pudo obtener objeto Usuario del contexto, se buscará en BD")
        
        detalle = usuario_service.obtener_detalle_completo_usuario(usuario_id, usuario_obj=usuario_obj)
        if not detalle:
            logger.warning(f"[PERFIL] No se pudo obtener detalle completo para usuario ID: {user.get('id_usuario')}")
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado o inactivo',
                'status_code': 404
            }), 404
        
        # Si el detalle tiene un campo 'error', significa que faltan datos pero podemos retornar lo que hay
        if 'error' in detalle and detalle.get('error'):
            logger.warning(f"[PERFIL] Usuario ID {user.get('id_usuario')} tiene datos incompletos: {detalle.get('error')}")
            # Retornar 200 pero con un warning en el mensaje
            return jsonify({
                'success': True,
                'message': 'Información obtenida parcialmente. ' + detalle.get('error'),
                'data': detalle,
                'warning': detalle.get('error'),
                'status_code': 200
            }), 200

        return jsonify({
            'success': True,
            'message': 'Detalle de perfil obtenido exitosamente',
            'data': detalle,
            'status_code': 200
        }), 200

    except Exception as e:
        logger.error(f"Error inesperado al obtener detalle de perfil: {str(e)}")
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
    REQUIERE asociarse con un deportista para completar el registro.

    Headers requeridos:
    Authorization: Bearer <token>

    Body JSON requerido:
    {
        "id_deportista": 123,              // OBLIGATORIO: ID del deportista
        "id_parentesco": 1,                // OBLIGATORIO: ID del tipo de parentesco
        "es_responsable": true             // OBLIGATORIO: Si es responsable legal (bool)
    }

    Returns:
        JSON: Información del acudiente creado y la relación establecida
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
        
        # Validar edad mínima para acudientes (18 años) solo si es deportista
        # Si el usuario no es deportista, no se requiere validación de edad
        from src.models.deportistas.deportista import Deportista
        from datetime import date
        
        deportista = Deportista.query.filter_by(id_persona=user.get('persona', {}).get('id_persona')).first()
        if deportista and deportista.fecha_nacimiento:
            # Calcular edad correctamente
            if isinstance(deportista.fecha_nacimiento, date):
                edad = (date.today() - deportista.fecha_nacimiento).days // 365
            else:
                # Si es solo año, calcular edad aproximada
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
