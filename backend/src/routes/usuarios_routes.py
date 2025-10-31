"""
Rutas de gestión de usuarios para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para listar usuarios
- Permitir cambio de roles de usuarios
- Gestionar usuarios del sistema

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from flask import Blueprint, request, jsonify, make_response
from flask_cors import cross_origin

from ..models.base import db
from ..models.usuarios.usuario import Usuario
from ..models.roles_y_permisos.rol import Rol
from ..models.roles_y_permisos.usuario_rol import UsuarioRol
from ..middleware.auth_decorator import token_required
from ..utils.logger import obtener_registrador
from ..services.Auth.usuario_service import usuario_service, UsuarioServiceError

# Crear Blueprint de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')
logger = obtener_registrador('aplicacion')


@usuarios_bp.route('/', methods=['GET', 'OPTIONS'])
@cross_origin(methods=['GET', 'OPTIONS'])
@token_required()  # Habilitar autenticación
def listar_usuarios():
    """
    Endpoint para listar todos los usuarios con sus roles.
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Returns:
        JSON: Lista de usuarios con sus roles
    """
    try:
        # Obtener todos los usuarios activos con sus roles
        usuarios = Usuario.query.filter_by(estado=True).all()
        
        usuarios_data = []
        for usuario in usuarios:
            # Obtener roles del usuario a través de la relación directa
            roles_usuario = []
            for rol in usuario.roles:
                roles_usuario.append({
                    'id_rol': rol.id_rol,
                    'nombre_rol': rol.nombre_rol,
                    'descripcion': rol.descripcion
                })
            
            usuarios_data.append({
                'id_usuario': usuario.id_usuario,
                'usuario': usuario.usuario,
                'estado': usuario.estado,
                'roles': roles_usuario,
                'persona': {
                    'id_persona': usuario.persona.id_persona,
                    'nombre_completo': usuario.persona.nombre_completo,
                    'primer_nombre': usuario.persona.primer_nombre,
                    'primer_apellido': usuario.persona.primer_apellido,
                    'correo_electronico': usuario.persona.correo_electronico,
                    'documento': usuario.persona.documento,
                    'telefono': usuario.persona.telefono
                }
            })
        
        return jsonify({
            'success': True,
            'message': 'Usuarios obtenidos exitosamente',
            'data': usuarios_data,
            'total': len(usuarios_data),
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al listar usuarios: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@usuarios_bp.route('/<int:id_usuario>/detalle', methods=['GET'])
@token_required()  # Protegido con autenticación
def obtener_detalle_usuario(id_usuario):
    """
    Endpoint para obtener la información completa de un usuario específico.

    Incluye:
    - Datos de usuario y persona
    - Roles asignados
    - Información específica por rol (deportista, acudiente)

    Headers requeridos:
    Authorization: Bearer <token>

    Returns:
        JSON: Estructura con la información completa o error
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

    except Exception as e:
        logger.error(f"Error inesperado al obtener detalle de usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500

@usuarios_bp.route('/<int:id_usuario>', methods=['PUT', 'OPTIONS'])
@cross_origin(methods=['PUT', 'OPTIONS'])
@token_required()  # Habilitar autenticación
def actualizar_usuario(id_usuario):
    """
    Endpoint para actualizar los datos de un usuario.
    
    Permite actualizar tanto datos de la persona como datos del usuario.
    Puede actualizar SOLO datos_usuario, SOLO datos_persona, o AMBOS.
    La contraseña y el estado NO se pueden actualizar desde este endpoint.
    
    Los datos se envían en el body JSON con dos secciones opcionales (al menos una es requerida):
    - datos_persona: campos de la persona (nombres, apellidos, documento, etc.) - OPCIONAL
    - datos_usuario: campos del usuario (solo usuario, NO contraseña ni estado) - OPCIONAL
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Ejemplos de Body JSON:
    
    Ejemplo 1: Actualizar solo el nombre de usuario
    {
        "datos_usuario": {
            "usuario": "nuevo_usuario"
        }
    }
    
    Ejemplo 2: Actualizar solo datos de persona
    {
        "datos_persona": {
            "primer_nombre": "Juan",
            "correo_electronico": "juan@example.com"
        }
    }
    
    Ejemplo 3: Actualizar ambos (persona y usuario)
    {
        "datos_persona": {
            "primer_nombre": "Juan",
            "segundo_nombre": "Carlos",
            "primer_apellido": "Pérez",
            "segundo_apellido": "González",
            "documento": "12345678",
            "correo_electronico": "juan@example.com",
            "telefono": "1234567890",
            "direccion": "Calle 123",
            "id_tipo_documento": 1,
            "id_sexo": 1
        },
        "datos_usuario": {
            "usuario": "nuevo_usuario"
        }
    }
    
    Campos disponibles en datos_persona:
    - primer_nombre (string): Primer nombre
    - segundo_nombre (string, opcional): Segundo nombre
    - primer_apellido (string): Primer apellido
    - segundo_apellido (string, opcional): Segundo apellido
    - documento (string): Número de documento
    - correo_electronico (string): Correo electrónico
    - telefono (string): Número de teléfono
    - direccion (string): Dirección de residencia
    - id_tipo_documento (int): ID del tipo de documento
    - id_sexo (int): ID del sexo/género
    
    Campos disponibles en datos_usuario:
    - usuario (string): Nombre de usuario
    
    NOTA: La contraseña y el estado NO se pueden actualizar desde este endpoint
    
    Returns:
        JSON: Usuario actualizado o error
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
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos requeridos',
                'status_code': 400
            }), 400
        
        # Separar datos de persona y usuario (opcionales)
        # Nota: datos_persona primero, datos_usuario segundo (orden lógico)
        datos_persona = data.get('datos_persona')
        datos_usuario = data.get('datos_usuario')
        
        # Validar que al menos se proporcione un tipo de datos
        if not datos_persona and not datos_usuario:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar al menos datos_persona o datos_usuario',
                'status_code': 400
            }), 400
        
        # Validar que no se intente actualizar la contraseña
        if datos_usuario and 'password' in datos_usuario:
            return jsonify({
                'success': False,
                'error': 'La contraseña no se puede actualizar desde este endpoint. Use el endpoint dedicado para cambio de contraseña',
                'status_code': 400
            }), 400
        
        # Validar que no se intente actualizar el estado
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
        
        # Llamar al servicio para actualizar
        # Nota: El orden es datos_persona primero, luego datos_usuario
        resultado = usuario_service.actualizar_usuario(
            id_usuario=id_usuario,
            datos_persona=datos_persona,
            datos_usuario=datos_usuario
        )
        
        return jsonify(resultado), resultado.get('status_code', 200)
        
    except UsuarioServiceError as e:
        logger.error(f"Error de servicio al actualizar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'status_code': 400
        }), 400
        
    except Exception as e:
        logger.error(f"Error inesperado al actualizar usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@usuarios_bp.route('/<int:id_usuario>/rol', methods=['PUT', 'OPTIONS'])
@cross_origin(methods=['PUT', 'OPTIONS'])
@token_required()  # Habilitar autenticación
def cambiar_rol_usuario(id_usuario):
    """
    Endpoint para cambiar el rol de un usuario.
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Body JSON esperado:
    {
        "id_rol": 2
    }
    
    Returns:
        JSON: Usuario actualizado o error
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
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Datos requeridos',
                'status_code': 400
            }), 400
        
        # Validar que se proporcione id_rol o id_roles (array)
        id_rol = data.get('id_rol')
        id_roles = data.get('id_roles', [])
        
        # Normalizar a lista: si viene id_rol único, convertirlo a lista
        if id_rol is not None and not id_roles:
            id_roles = [id_rol]
        elif not id_rol and not id_roles:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar id_rol o id_roles (array)',
                'status_code': 400
            }), 400
        
        # Verificar que el usuario existe
        usuario = Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
        if not usuario:
            return jsonify({
                'success': False,
                'error': f'Usuario con ID {id_usuario} no encontrado',
                'status_code': 404
            }), 404
        
        # Validar y obtener roles (solo permitir Entrenador y Administrador)
        roles_permitidos = ['entrenador', 'administrador']
        roles_excluidos = ['superadmin', 'super_admin', 'usuario', 'deportista', 'acudiente']
        roles_validos = []
        for rid in id_roles:
            if not isinstance(rid, int):
                try:
                    rid = int(rid)
                except (ValueError, TypeError):
                    continue
            rol = Rol.query.filter_by(id_rol=rid).first()
            if rol:
                nombre_lower = rol.nombre_rol.lower()
                # Solo permitir Entrenador y Administrador
                if nombre_lower in roles_permitidos:
                    roles_validos.append(rol)
                elif nombre_lower in roles_excluidos:
                    logger.warning(f"Intento de asignar rol {rol.nombre_rol} a usuario {id_usuario}, ignorado (rol automático o no permitido)")
        
        if not roles_validos:
            return jsonify({
                'success': False,
                'error': 'Solo se pueden asignar los roles Entrenador y Administrador manualmente',
                'status_code': 400
            }), 400
        
        # Obtener roles actuales del usuario
        roles_actuales_usuario = UsuarioRol.query.filter_by(id_usuario=id_usuario).all()
        
        # Identificar roles automáticos (Usuario, Deportista, Acudiente) que NO se deben eliminar
        roles_automaticos = ['usuario', 'deportista', 'acudiente']
        
        # Eliminar solo los roles gestionables manualmente (Entrenador, Administrador)
        # y SuperAdmin si existe, preservando los roles automáticos
        roles_gestionables_eliminados = []
        for ur in roles_actuales_usuario:
            rol_obj = Rol.query.get(ur.id_rol)
            if rol_obj:
                nombre_lower = rol_obj.nombre_rol.lower()
                # Eliminar solo Entrenador, Administrador y SuperAdmin (no los automáticos)
                if nombre_lower in ('entrenador', 'administrador', 'superadmin', 'super_admin'):
                    db.session.delete(ur)
                    roles_gestionables_eliminados.append(ur.id_rol)
        
        # Agregar TODOS los roles válidos que vienen en la petición
        # (ya los eliminamos arriba, así que simplemente agregamos todos los nuevos)
        for rol in roles_validos:
            nuevo_usuario_rol = UsuarioRol(
                id_usuario=id_usuario,
                id_rol=rol.id_rol
            )
            db.session.add(nuevo_usuario_rol)
        
        db.session.commit()
        
        # Obtener datos actualizados del usuario
        usuario_actualizado = Usuario.query.filter_by(id_usuario=id_usuario).first()
        roles_actualizados = []
        for rol in usuario_actualizado.roles:
            roles_actualizados.append({
                'id_rol': rol.id_rol,
                'nombre_rol': rol.nombre_rol,
                'descripcion': rol.descripcion
            })
        
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
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado al cambiar rol de usuario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


# Manejadores de errores específicos del Blueprint
@usuarios_bp.errorhandler(400)
def bad_request(error):
    """Manejador de errores 400 (Bad Request)."""
    return jsonify({
        'success': False,
        'error': 'Solicitud incorrecta',
        'message': 'Verifique los datos enviados',
        'status_code': 400
    }), 400


@usuarios_bp.errorhandler(404)
def not_found(error):
    """Manejador de errores 404 (Not Found)."""
    return jsonify({
        'success': False,
        'error': 'Recurso no encontrado',
        'message': 'El usuario o rol solicitado no existe',
        'status_code': 404
    }), 404


@usuarios_bp.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500 (Internal Server Error)."""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Contacte al administrador',
        'status_code': 500
    }), 500


# Función para registrar el Blueprint en la aplicación
def registrar_usuarios_routes(app):
    """
    Registra las rutas de usuarios en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(usuarios_bp)
    logger.info("Rutas de usuarios registradas exitosamente")
