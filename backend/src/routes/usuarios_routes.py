"""
Rutas de gestión de usuarios para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para listar usuarios
- Permitir cambio de roles de usuarios
- Gestionar usuarios del sistema

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

from ..models.base import db
from ..models.usuarios.usuario import Usuario
from ..models.roles_y_permisos.rol import Rol
from ..models.roles_y_permisos.usuario_rol import UsuarioRol
from ..middleware.auth_decorator import token_required
from ..utils.logger import obtener_registrador

# Crear Blueprint de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')
logger = obtener_registrador('aplicacion')


@usuarios_bp.route('/', methods=['GET'])
@cross_origin()
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


@usuarios_bp.route('/<int:id_usuario>/rol', methods=['PUT'])
@cross_origin()
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
        
        # Validar que se proporcione id_rol
        if 'id_rol' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo id_rol requerido',
                'status_code': 400
            }), 400
        
        id_rol = data['id_rol']
        
        # Verificar que el usuario existe
        usuario = Usuario.query.filter_by(id_usuario=id_usuario, estado=True).first()
        if not usuario:
            return jsonify({
                'success': False,
                'error': f'Usuario con ID {id_usuario} no encontrado',
                'status_code': 404
            }), 404
        
        # Verificar que el rol existe
        rol = Rol.query.filter_by(id_rol=id_rol).first()
        if not rol:
            return jsonify({
                'success': False,
                'error': f'Rol con ID {id_rol} no encontrado',
                'status_code': 404
            }), 404
        
        # Eliminar roles actuales del usuario
        UsuarioRol.query.filter_by(id_usuario=id_usuario).delete()
        
        # Asignar nuevo rol
        nuevo_usuario_rol = UsuarioRol(
            id_usuario=id_usuario,
            id_rol=id_rol
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
