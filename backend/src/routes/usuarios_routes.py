"""
Rutas de gestión de usuarios para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para listar usuarios
- Permitir cambio de roles de usuarios
- Gestionar usuarios del sistema

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from typing import Any, Dict, Iterable, List, Optional, Tuple, TYPE_CHECKING
from flask import Blueprint, Flask, Response, jsonify, request
from flask_cors import cross_origin
from ..models.base import db
from ..models.usuarios.usuario import Usuario
from ..models.roles_y_permisos.rol import Rol
from ..models.roles_y_permisos.usuario_rol import UsuarioRol
from ..middleware.auth_decorator import token_required
from ..utils.logger import obtener_registrador
from ..services.Auth.usuario_service import usuario_service, UsuarioServiceError

from ..utils.request_validators import (
    RequestValidationError,
    obtener_json_requerido,
    validar_campo_booleano,
)

if TYPE_CHECKING:  # pragma: no cover
    from ..models.personas.persona import Persona

# Crear Blueprint de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')
logger = obtener_registrador('aplicacion')

DEFAULT_LIMIT = 3
DEFAULT_OFFSET = 0
MAX_LIMIT = 100
ROLES_PERMITIDOS = ('entrenador', 'administrador')
ROLES_EXCLUIDOS = ('superadmin', 'super_admin', 'usuario', 'deportista', 'acudiente')
ROLES_AUTOMATICOS = ('usuario', 'deportista', 'acudiente')

ERROR_INTERNO_SERVIDOR = 'Error interno del servidor'
ERROR_CONTENT_TYPE_JSON = 'Content-Type debe ser application/json'
ERROR_DATOS_REQUERIDOS = 'Datos requeridos'
ERROR_ESTADO_REQUERIDO = 'Se requiere el campo "estado" (true/false)'
ERROR_ESTADO_BOOLEANO = 'El campo "estado" debe ser true o false'

JsonResponse = Tuple[Response, int]


def _ajustar_paginacion(limit: int, offset: int) -> Tuple[int, int]:
    """Normaliza los parámetros de paginación."""
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)
    return limit, offset


def _aplicar_filtro_estado(estado: str):
    """Construye la consulta según el estado solicitado."""
    filtros = {
        'activo': Usuario.query.filter_by(estado=True),
        'inactivo': Usuario.query.filter_by(estado=False),
    }
    return filtros.get(estado.lower(), Usuario.query)


def _serializar_roles(roles: Iterable[Rol]) -> List[Dict[str, Any]]:
    """Serializa la información de los roles asociados a un usuario."""
    return [
        {
            'id_rol': rol.id_rol,
            'nombre_rol': rol.nombre_rol,
            'descripcion': rol.descripcion,
        }
        for rol in roles
    ]


def _serializar_persona(persona: 'Persona') -> Dict[str, Any]:
    """Serializa la información personal asociada al usuario."""
    return {
        'id_persona': persona.id_persona,
        'nombre_completo': persona.nombre_completo,
        'primer_nombre': persona.primer_nombre,
        'primer_apellido': persona.primer_apellido,
        'correo_electronico': persona.correo_electronico,
        'documento': persona.documento,
        'telefono': persona.telefono,
    }


def _serializar_usuario(usuario: Usuario) -> Dict[str, Any]:
    """Serializa la información del usuario incluyendo roles y persona."""
    return {
        'id_usuario': usuario.id_usuario,
        'usuario': usuario.usuario,
        'estado': usuario.estado,
        'roles': _serializar_roles(usuario.roles),
        'persona': _serializar_persona(usuario.persona),
    }


def _normalizar_roles_solicitados(data: Dict[str, Any]) -> List[Any]:
    """Obtiene la lista de roles solicitados desde el cuerpo JSON."""
    id_rol = data.get('id_rol')
    id_roles = data.get('id_roles', [])

    if id_rol is not None and not id_roles:
        id_roles = [id_rol]
    elif id_rol is None and id_roles is None:
        raise RequestValidationError(
            'Debe proporcionar id_rol o id_roles (array). Puede enviar un array vacío [] para remover todos los roles gestionables.',
            status_code=400,
        )

    if isinstance(id_roles, list):
        return id_roles
    if id_roles is None:
        return []
    return [id_roles]


def _filtrar_roles_gestionables(
    identificadores: Iterable[Any],
    *,
    id_usuario: int,
) -> List[Rol]:
    """Obtiene los roles gestionables permitidos a partir de los identificadores."""
    roles_validos: List[Rol] = []
    for identificador in identificadores:
        try:
            identificador_int = int(identificador)
        except (TypeError, ValueError):
            continue

        rol = Rol.query.filter_by(id_rol=identificador_int).first()
        if not rol:
            continue

        nombre_lower = rol.nombre_rol.lower()
        if nombre_lower in ROLES_PERMITIDOS:
            roles_validos.append(rol)
        elif nombre_lower in ROLES_EXCLUIDOS:
            logger.warning(
                "Intento de asignar rol %s a usuario %s, ignorado (rol automático o no permitido)",
                rol.nombre_rol,
                id_usuario,
            )

    return roles_validos


def _actualizar_roles_gestionables(id_usuario: int, roles_validos: Iterable[Rol]) -> None:
    """Reemplaza los roles gestionables actuales por los solicitados."""
    roles_actuales_usuario = UsuarioRol.query.filter_by(id_usuario=id_usuario).all()

    for usuario_rol in roles_actuales_usuario:
        rol_obj = Rol.query.get(usuario_rol.id_rol)
        if not rol_obj:
            continue

        nombre_lower = rol_obj.nombre_rol.lower()
        if nombre_lower in ROLES_PERMITIDOS or nombre_lower in {'superadmin', 'super_admin'}:
            db.session.delete(usuario_rol)

    for rol in roles_validos:
        db.session.add(UsuarioRol(id_usuario=id_usuario, id_rol=rol.id_rol))

    db.session.commit()


def _obtener_usuario(id_usuario: int, *, solo_activos: bool = False) -> Optional[Usuario]:
    """Recupera un usuario por su identificador con opción a filtrar por estado."""
    filtro = {'id_usuario': id_usuario}
    if solo_activos:
        filtro['estado'] = True
    return Usuario.query.filter_by(**filtro).first()


@usuarios_bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET', 'OPTIONS'])
@token_required(
    required_roles=['Administrador', 'SuperAdmin'],
    required_active_roles=['Administrador', 'SuperAdmin']
)  # Habilitar autenticación
def listar_usuarios() -> JsonResponse:
    """Lista usuarios con información de roles y persona asociada.

    Returns:
        Response: Respuesta JSON con usuarios paginados y metadatos.
    """
    try:
        limit_param = request.args.get('limit', DEFAULT_LIMIT, type=int)
        offset_param = request.args.get('offset', DEFAULT_OFFSET, type=int)
        limit = limit_param if isinstance(limit_param, int) else DEFAULT_LIMIT
        offset = offset_param if isinstance(offset_param, int) else DEFAULT_OFFSET
        limit, offset = _ajustar_paginacion(limit, offset)

        estado_filter = request.args.get('estado', 'todos')
        query = _aplicar_filtro_estado(estado_filter or 'todos')

        total_usuarios = query.count()
        usuarios = query.offset(offset).limit(limit).all()
        usuarios_data = [_serializar_usuario(usuario) for usuario in usuarios]
        has_more = (offset + limit) < total_usuarios

        return jsonify({
            'success': True,
            'message': 'Usuarios obtenidos exitosamente',
            'data': usuarios_data,
            'total': total_usuarios,
            'limit': limit,
            'offset': offset,
            'has_more': has_more,
            'status_code': 200
        }), 200

    except Exception as exc:
        logger.error("Error inesperado al listar usuarios: %s", str(exc))
        return jsonify({
            'success': False,
            'error': ERROR_INTERNO_SERVIDOR,
            'status_code': 500
        }), 500


@usuarios_bp.route('/<int:id_usuario>/detalle', methods=['GET'])
@token_required(
    required_roles=['Administrador', 'SuperAdmin', 'Entrenador'],
    required_active_roles=['Administrador', 'SuperAdmin', 'Entrenador']
)  # Protegido con autenticación
def obtener_detalle_usuario(id_usuario: int) -> JsonResponse:
    """Obtiene la información detallada de un usuario específico.

    Args:
        id_usuario: Identificador del usuario a consultar.

    Returns:
        Response: Respuesta JSON con el detalle del usuario o el error.
    """
    try:
        detalle = usuario_service.obtener_detalle_completo_usuario(id_usuario)
        if not detalle:
            return jsonify({
                'success': False,
                'error': f'Usuario con ID {id_usuario} no encontrado',
                'status_code': 404
            }), 404

        return jsonify({
            'success': True,
            'message': 'Detalle de usuario obtenido exitosamente',
            'data': detalle,
            'status_code': 200
        }), 200
    except Exception as exc:
        logger.error("Error inesperado al obtener detalle de usuario: %s", str(exc))
        return jsonify({
            'success': False,
            'error': ERROR_INTERNO_SERVIDOR,
            'status_code': 500
        }), 500

@usuarios_bp.route('/<int:id_usuario>', methods=['PUT', 'OPTIONS'])
@cross_origin(methods=['PUT', 'OPTIONS'])
@token_required(
    required_roles=['Administrador', 'SuperAdmin'],
    required_active_roles=['Administrador', 'SuperAdmin']
)  # Habilitar autenticación
def actualizar_usuario(id_usuario: int) -> JsonResponse:
    """Actualiza los datos de usuario y persona asociados.

    Args:
        id_usuario: Identificador del usuario a actualizar.

    Returns:
        Response: Respuesta JSON con el resultado de la operación.
    """
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        datos_persona = data.get('datos_persona')
        datos_usuario = data.get('datos_usuario')

        if not datos_persona and not datos_usuario:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar al menos datos_persona o datos_usuario',
                'status_code': 400
            }), 400

        if datos_usuario and 'password' in datos_usuario:
            return jsonify({
                'success': False,
                'error': 'La contraseña no se puede actualizar desde este endpoint. Use el endpoint dedicado para cambio de contraseña',
                'status_code': 400
            }), 400
        if datos_usuario and 'estado' in datos_usuario:
            return jsonify({
                'success': False,
                'error': 'El estado no se puede actualizar desde este endpoint. Use los endpoints dedicados para activar/desactivar usuarios',
                'status_code': 400
            }), 400
        if datos_persona and 'estado' in datos_persona:
            return jsonify({
                'success': False,
                'error': 'El estado no se puede actualizar desde este endpoint. Use los endpoints dedicados para activar/desactivar personas',
                'status_code': 400
            }), 400

        resultado = usuario_service.actualizar_usuario(
            id_usuario=id_usuario,
            datos_persona=datos_persona,
            datos_usuario=datos_usuario
        )
        return jsonify(resultado), resultado.get('status_code', 200)

    except RequestValidationError as exc:
        logger.warning(
            "Validación de solicitud al actualizar usuario %s: %s",
            id_usuario,
            str(exc),
        )
        return jsonify({
            'success': False,
            'error': str(exc),
            'status_code': exc.status_code
        }), exc.status_code
    except UsuarioServiceError as exc:
        logger.error("Error de servicio al actualizar usuario: %s", str(exc))
        return jsonify({
            'success': False,
            'error': str(exc),
            'status_code': 400
        }), 400
    except Exception as exc:
        logger.error("Error inesperado al actualizar usuario: %s", str(exc))
        return jsonify({
            'success': False,
            'error': ERROR_INTERNO_SERVIDOR,
            'status_code': 500
        }), 500


@usuarios_bp.route('/<int:id_usuario>/rol', methods=['PUT', 'OPTIONS'])
@cross_origin(methods=['PUT', 'OPTIONS'])
@token_required(
    required_roles=['Administrador', 'SuperAdmin'],
    required_active_roles=['Administrador', 'SuperAdmin']
)  # Habilitar autenticación
def cambiar_rol_usuario(id_usuario: int) -> JsonResponse:
    """Actualiza los roles gestionables asignados a un usuario.

    Args:
        id_usuario: Identificador del usuario a modificar.

    Returns:
        Response: Respuesta JSON con los roles actualizados o el error.
    """
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )
        roles_solicitados = _normalizar_roles_solicitados(data)

        usuario = _obtener_usuario(id_usuario, solo_activos=True)
        if not usuario:
            return jsonify({
                'success': False,
                'error': f'Usuario con ID {id_usuario} no encontrado',
                'status_code': 404
            }), 404

        roles_validos = _filtrar_roles_gestionables(
            roles_solicitados,
            id_usuario=id_usuario,
        )
        _actualizar_roles_gestionables(id_usuario, roles_validos)

        usuario_actualizado = _obtener_usuario(id_usuario)
        roles_actualizados = _serializar_roles(usuario_actualizado.roles if usuario_actualizado else [])

        return jsonify({
            'success': True,
            'message': 'Rol de usuario actualizado exitosamente',
            'data': {
                'id_usuario': usuario_actualizado.id_usuario,
                'usuario': usuario_actualizado.usuario,
                'roles': roles_actualizados
            },
            'status_code': 200
        }), 200

    except RequestValidationError as exc:
        logger.warning(
            "Validación de solicitud al cambiar roles del usuario %s: %s",
            id_usuario,
            str(exc),
        )
        return jsonify({
            'success': False,
            'error': str(exc),
            'status_code': exc.status_code
        }), exc.status_code
    except Exception as exc:
        db.session.rollback()
        logger.error("Error inesperado al cambiar rol de usuario: %s", str(exc))
        return jsonify({
            'success': False,
            'error': ERROR_INTERNO_SERVIDOR,
            'status_code': 500
        }), 500


@usuarios_bp.route('/<int:id_usuario>/estado', methods=['PUT', 'OPTIONS'])
@cross_origin(methods=['PUT', 'OPTIONS'])
@token_required(
    required_roles=['Administrador', 'SuperAdmin'],
    required_active_roles=['Administrador', 'SuperAdmin']
)
def cambiar_estado_usuario(id_usuario: int) -> JsonResponse:
    """Activa o desactiva un usuario existente.

    Args:
        id_usuario: Identificador del usuario objetivo.

    Returns:
        Response: Respuesta JSON con el estado actualizado o el error.
    """
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )
        nuevo_estado = validar_campo_booleano(
            data,
            'estado',
            mensaje_faltante=ERROR_ESTADO_REQUERIDO,
            mensaje_tipo=ERROR_ESTADO_BOOLEANO,
        )

        usuario = _obtener_usuario(id_usuario)
        if not usuario:
            return jsonify({
                'success': False,
                'error': f'Usuario con ID {id_usuario} no encontrado',
                'status_code': 404
            }), 404

        from ..middleware.auth_decorator import get_current_user
        usuario_actual = get_current_user()
        if usuario_actual and usuario_actual.get('id_usuario') == id_usuario and not nuevo_estado:
            return jsonify({
                'success': False,
                'error': 'No puedes desactivar tu propio usuario',
                'status_code': 400
            }), 400

        usuario.estado = nuevo_estado
        db.session.commit()

        roles_usuario = _serializar_roles(usuario.roles)

        return jsonify({
            'success': True,
            'message': f'Usuario {"activado" if nuevo_estado else "desactivado"} exitosamente',
            'data': {
                'id_usuario': usuario.id_usuario,
                'usuario': usuario.usuario,
                'estado': usuario.estado,
                'roles': roles_usuario
            },
            'status_code': 200
        }), 200

    except RequestValidationError as exc:
        logger.warning(
            "Validación de solicitud al cambiar estado de usuario %s: %s",
            id_usuario,
            str(exc),
        )
        return jsonify({
            'success': False,
            'error': str(exc),
            'status_code': exc.status_code
        }), exc.status_code
    except Exception as exc:
        db.session.rollback()
        logger.error("Error al cambiar estado de usuario: %s", str(exc))
        return jsonify({
            'success': False,
            'error': ERROR_INTERNO_SERVIDOR,
            'status_code': 500
        }), 500


# Manejadores de errores específicos del Blueprint
@usuarios_bp.errorhandler(400)
def bad_request(error: Exception) -> JsonResponse:
    """Devuelve respuesta JSON para errores 400 (Bad Request)."""
    return jsonify({
        'success': False,
        'error': 'Solicitud incorrecta',
        'message': 'Verifique los datos enviados',
        'status_code': 400
    }), 400


@usuarios_bp.errorhandler(404)
def not_found(error: Exception) -> JsonResponse:
    """Devuelve respuesta JSON para errores 404 (Not Found)."""
    return jsonify({
        'success': False,
        'error': 'Recurso no encontrado',
        'message': 'El usuario o rol solicitado no existe',
        'status_code': 404
    }), 404


@usuarios_bp.errorhandler(500)
def internal_error(error: Exception) -> JsonResponse:
    """Devuelve respuesta JSON para errores 500 (Internal Server Error)."""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Contacte al administrador',
        'status_code': 500
    }), 500


# Función para registrar el Blueprint en la aplicación
def registrar_usuarios_routes(app: Flask) -> None:
    """Registra las rutas de usuarios en la aplicación Flask.

    Args:
        app: Instancia de la aplicación Flask.
    """
    app.register_blueprint(usuarios_bp)
    logger.info("Rutas de usuarios registradas exitosamente")
