"""
Rutas para la gestión de eventos deportivos.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.base import db
from src.models import Evento, Sesion, TipoEvento, Categoria
from datetime import datetime, date, time
import re

eventos_bp = Blueprint('eventos', __name__)


# ============================================================================
# VALIDACIONES
# ============================================================================

def validar_fecha(fecha_str):
    """Valida y convierte string a date"""
    try:
        return datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def validar_hora(hora_str):
    """Valida y convierte string a time (formato HH:MM:SS o HH:MM)"""
    try:
        # Intentar con formato HH:MM:SS
        if len(hora_str.split(':')) == 3:
            return datetime.strptime(hora_str, '%H:%M:%S').time()
        # Intentar con formato HH:MM
        elif len(hora_str.split(':')) == 2:
            return datetime.strptime(hora_str, '%H:%M').time()
        return None
    except ValueError:
        return None

def validar_lugar(lugar_str):
    """Valida que el lugar tenga al menos 3 caracteres"""
    if not lugar_str or len(lugar_str.strip()) < 3:
        return False
    return True


# ============================================================================
# CRUD DE EVENTOS
# ============================================================================

@eventos_bp.route('/eventos', methods=['GET'])
def listar_eventos():
    """
    Listar todos los eventos con filtros opcionales.
    
    Query params:
        - page: número de página (default: 1)
        - per_page: registros por página (default: 10)
        - search: búsqueda por nombre
        - categoria_id: filtrar por categoría
        - tipo_evento_id: filtrar por tipo de evento
        - fecha_desde: filtrar desde fecha (YYYY-MM-DD)
        - fecha_hasta: filtrar hasta fecha (YYYY-MM-DD)
    """
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        categoria_id = request.args.get('categoria_id', type=int)
        tipo_evento_id = request.args.get('tipo_evento_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        # Construir consulta base
        query = Evento.query
        
        # Filtros
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Evento.nombre.ilike(search_filter))
        
        if categoria_id:
            query = query.filter_by(id_categoria=categoria_id)
        
        if tipo_evento_id:
            query = query.filter_by(id_tipo_evento=tipo_evento_id)
        
        if fecha_desde:
            fecha_desde_obj = validar_fecha(fecha_desde)
            if fecha_desde_obj:
                query = query.filter(Evento.fecha_evento >= fecha_desde_obj)
        
        if fecha_hasta:
            fecha_hasta_obj = validar_fecha(fecha_hasta)
            if fecha_hasta_obj:
                query = query.filter(Evento.fecha_evento <= fecha_hasta_obj)
        
        # Ordenar por fecha (más recientes primero)
        query = query.order_by(Evento.fecha_evento.desc())
        
        # Paginación
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Construir respuesta con información detallada
        eventos_data = []
        for evento in pagination.items:
            evento_dict = evento.to_dict()
            
            # Agregar información de relaciones
            if evento.categoria:
                evento_dict['categoria'] = {
                    'id_categoria': evento.categoria.id_categoria,
                    'nombre_categoria': evento.categoria.nombre_categoria
                }
            
            if evento.sesion:
                evento_dict['sesion'] = {
                    'id_sesion': evento.sesion.id_sesion,
                    'nombre': evento.sesion.nombre
                }
            
            # Obtener tipo de evento
            tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
            if tipo_evento:
                evento_dict['tipo_evento'] = {
                    'id_tipo_evento': tipo_evento.id_tipo_evento,
                    'nombre': tipo_evento.nombre
                }
            
            eventos_data.append(evento_dict)
        
        return jsonify({
            'success': True,
            'data': eventos_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        # Log del error para debugging
        from src.utils.logger import obtener_registrador
        logger = obtener_registrador('aplicacion')
        logger.error(f'Error al listar eventos: {str(e)}')
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor al cargar eventos',
            'message': 'Por favor intenta nuevamente más tarde'
        }), 500


@eventos_bp.route('/eventos/<int:id>', methods=['GET'])
def obtener_evento(id):
    """Obtener un evento específico por ID"""
    try:
        evento = Evento.query.get(id)
        
        if not evento:
            return jsonify({
                'success': False,
                'error': f'Evento con ID {id} no encontrado'
            }), 404
        
        evento_dict = evento.to_dict()
        
        # Agregar información detallada de relaciones
        if evento.categoria:
            evento_dict['categoria'] = evento.categoria.to_dict()
        
        if evento.sesion:
            evento_dict['sesion'] = evento.sesion.to_dict()
        
        tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
        if tipo_evento:
            evento_dict['tipo_evento'] = tipo_evento.to_dict()
        
        return jsonify({
            'success': True,
            'data': evento_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener evento: {str(e)}'
        }), 500


@eventos_bp.route('/eventos', methods=['POST'])
def crear_evento():
    """
    Crear un nuevo evento.
    
    Body JSON:
        - nombre: nombre del evento (requerido)
        - fecha_evento: fecha del evento YYYY-MM-DD (requerido)
        - hora_inicio: hora de inicio HH:MM o HH:MM:SS (requerido)
        - hora_fin: hora de fin HH:MM o HH:MM:SS (requerido)
        - lugar: ubicación del evento (requerido)
        - descripcion: descripción del evento (opcional)
        - id_categoria: ID de la categoría (requerido)
        - id_tipo_evento: ID del tipo de evento (requerido)
        - id_sesion: ID de la sesión (requerido)
    """
    try:
        data = request.get_json()
        
        # Validar que se envió data
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se enviaron datos',
                'message': 'El cuerpo de la petición debe contener datos JSON'
            }), 400
        
        # Validaciones de campos requeridos
        campos_requeridos = ['nombre', 'fecha_evento', 'hora_inicio', 'hora_fin', 'lugar', 'id_categoria', 'id_tipo_evento', 'id_sesion']
        campos_faltantes = []
        
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                campos_faltantes.append(campo)
        
        if campos_faltantes:
            return jsonify({
                'success': False,
                'error': 'Campos requeridos faltantes',
                'message': f'Los siguientes campos son obligatorios: {", ".join(campos_faltantes)}',
                'campos_faltantes': campos_faltantes
            }), 400
        
        # Validar nombre
        nombre = data['nombre'].strip()
        if len(nombre) < 3:
            return jsonify({
                'success': False,
                'error': 'El nombre debe tener al menos 3 caracteres'
            }), 400
        
        # Validar fecha
        fecha_evento = validar_fecha(data['fecha_evento'])
        if not fecha_evento:
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        # Validar hora de inicio
        hora_inicio = validar_hora(data['hora_inicio'])
        if not hora_inicio:
            return jsonify({
                'success': False,
                'error': 'Formato de hora de inicio inválido. Use HH:MM o HH:MM:SS'
            }), 400
        
        # Validar hora de fin
        hora_fin = validar_hora(data['hora_fin'])
        if not hora_fin:
            return jsonify({
                'success': False,
                'error': 'Formato de hora de fin inválido. Use HH:MM o HH:MM:SS'
            }), 400
        
        # Validar que hora_fin sea mayor que hora_inicio
        if hora_fin <= hora_inicio:
            return jsonify({
                'success': False,
                'error': 'La hora de fin debe ser posterior a la hora de inicio'
            }), 400
        
        # Validar lugar
        if not validar_lugar(data['lugar']):
            return jsonify({
                'success': False,
                'error': 'El lugar debe tener al menos 3 caracteres'
            }), 400
        
        # Validar que existan las relaciones
        categoria = Categoria.query.get(data['id_categoria'])
        if not categoria:
            return jsonify({
                'success': False,
                'error': f'Categoría con ID {data["id_categoria"]} no encontrada'
            }), 404
        
        tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
        if not tipo_evento:
            return jsonify({
                'success': False,
                'error': f'Tipo de evento con ID {data["id_tipo_evento"]} no encontrado'
            }), 404
        
        sesion = Sesion.query.get(data['id_sesion'])
        if not sesion:
            return jsonify({
                'success': False,
                'error': f'Sesión con ID {data["id_sesion"]} no encontrada'
            }), 404
        
        # Crear nuevo evento
        nuevo_evento = Evento(
            nombre=nombre,
            fecha_evento=fecha_evento,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            lugar=data['lugar'].strip(),
            descripcion=data.get('descripcion', '').strip() if data.get('descripcion') else None,
            id_categoria=data['id_categoria'],
            id_tipo_evento=data['id_tipo_evento'],
            id_sesion=data['id_sesion']
        )
        
        db.session.add(nuevo_evento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento creado exitosamente',
            'data': nuevo_evento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear evento: {str(e)}'
        }), 500


@eventos_bp.route('/eventos/<int:id>', methods=['PUT'])
def actualizar_evento(id):
    """
    Actualizar un evento existente.
    
    Body JSON (todos opcionales):
        - nombre: nuevo nombre del evento
        - fecha_evento: nueva fecha YYYY-MM-DD
        - hora_inicio: nueva hora de inicio HH:MM o HH:MM:SS
        - hora_fin: nueva hora de fin HH:MM o HH:MM:SS
        - lugar: nueva ubicación del evento
        - descripcion: nueva descripción del evento
        - id_categoria: nuevo ID de categoría
        - id_tipo_evento: nuevo ID de tipo de evento
        - id_sesion: nuevo ID de sesión
    """
    try:
        evento = Evento.query.get(id)
        
        if not evento:
            return jsonify({
                'success': False,
                'error': f'Evento con ID {id} no encontrado'
            }), 404
        
        data = request.get_json()
        
        # Actualizar nombre
        if 'nombre' in data:
            nombre = data['nombre'].strip()
            if len(nombre) < 3:
                return jsonify({
                    'success': False,
                    'error': 'El nombre debe tener al menos 3 caracteres'
                }), 400
            evento.nombre = nombre
        
        # Actualizar fecha
        if 'fecha_evento' in data:
            fecha_evento = validar_fecha(data['fecha_evento'])
            if not fecha_evento:
                return jsonify({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
            evento.fecha_evento = fecha_evento
        
        # Actualizar hora de inicio
        if 'hora_inicio' in data:
            hora_inicio = validar_hora(data['hora_inicio'])
            if not hora_inicio:
                return jsonify({
                    'success': False,
                    'error': 'Formato de hora de inicio inválido. Use HH:MM o HH:MM:SS'
                }), 400
            evento.hora_inicio = hora_inicio
        
        # Actualizar hora de fin
        if 'hora_fin' in data:
            hora_fin = validar_hora(data['hora_fin'])
            if not hora_fin:
                return jsonify({
                    'success': False,
                    'error': 'Formato de hora de fin inválido. Use HH:MM o HH:MM:SS'
                }), 400
            evento.hora_fin = hora_fin
        
        # Validar que hora_fin sea mayor que hora_inicio (si ambos están presentes)
        if evento.hora_fin <= evento.hora_inicio:
            return jsonify({
                'success': False,
                'error': 'La hora de fin debe ser posterior a la hora de inicio'
            }), 400
        
        # Actualizar lugar
        if 'lugar' in data:
            if not validar_lugar(data['lugar']):
                return jsonify({
                    'success': False,
                    'error': 'El lugar debe tener al menos 3 caracteres'
                }), 400
            evento.lugar = data['lugar'].strip()
        
        # Actualizar descripcion
        if 'descripcion' in data:
            evento.descripcion = data['descripcion'].strip() if data['descripcion'] else None
        
        # Actualizar categoría
        if 'id_categoria' in data:
            categoria = Categoria.query.get(data['id_categoria'])
            if not categoria:
                return jsonify({
                    'success': False,
                    'error': f'Categoría con ID {data["id_categoria"]} no encontrada'
                }), 404
            evento.id_categoria = data['id_categoria']
        
        # Actualizar tipo de evento
        if 'id_tipo_evento' in data:
            tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
            if not tipo_evento:
                return jsonify({
                    'success': False,
                    'error': f'Tipo de evento con ID {data["id_tipo_evento"]} no encontrado'
                }), 404
            evento.id_tipo_evento = data['id_tipo_evento']
        
        # Actualizar sesión
        if 'id_sesion' in data:
            sesion = Sesion.query.get(data['id_sesion'])
            if not sesion:
                return jsonify({
                    'success': False,
                    'error': f'Sesión con ID {data["id_sesion"]} no encontrada'
                }), 404
            evento.id_sesion = data['id_sesion']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evento actualizado exitosamente',
            'data': evento.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al actualizar evento: {str(e)}'
        }), 500


@eventos_bp.route('/eventos/<int:id>', methods=['DELETE'])
def eliminar_evento(id):
    """Eliminar un evento"""
    try:
        evento = Evento.query.get(id)
        
        if not evento:
            return jsonify({
                'success': False,
                'error': f'Evento con ID {id} no encontrado'
            }), 404
        
        nombre_evento = evento.nombre
        
        db.session.delete(evento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Evento "{nombre_evento}" eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar evento: {str(e)}'
        }), 500


# ============================================================================
# CRUD DE SESIONES
# ============================================================================

@eventos_bp.route('/sesiones', methods=['GET'])
def listar_sesiones():
    """Listar todas las sesiones"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        
        query = Sesion.query
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(Sesion.nombre.ilike(search_filter))
        
        query = query.order_by(Sesion.nombre.asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [sesion.to_dict() for sesion in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al listar sesiones: {str(e)}'
        }), 500


@eventos_bp.route('/sesiones/<int:id>', methods=['GET'])
def obtener_sesion(id):
    """Obtener una sesión específica por ID"""
    try:
        sesion = Sesion.query.get(id)
        
        if not sesion:
            return jsonify({
                'success': False,
                'error': f'Sesión con ID {id} no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sesion.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener sesión: {str(e)}'
        }), 500


@eventos_bp.route('/sesiones', methods=['POST'])
def crear_sesion():
    """
    Crear una nueva sesión.
    
    Body JSON:
        - nombre: nombre de la sesión (requerido)
        - descripcion: descripción de la sesión (opcional)
    """
    try:
        data = request.get_json()
        
        if 'nombre' not in data or not data['nombre'].strip():
            return jsonify({
                'success': False,
                'error': 'El campo nombre es requerido'
            }), 400
        
        nombre = data['nombre'].strip()
        if len(nombre) < 3:
            return jsonify({
                'success': False,
                'error': 'El nombre debe tener al menos 3 caracteres'
            }), 400
        
        # Verificar que no exista una sesión con el mismo nombre
        sesion_existente = Sesion.query.filter_by(nombre=nombre).first()
        if sesion_existente:
            return jsonify({
                'success': False,
                'error': f'Ya existe una sesión con el nombre "{nombre}"'
            }), 400
        
        nueva_sesion = Sesion(
            nombre=nombre,
            descripcion=data.get('descripcion', '').strip()
        )
        
        db.session.add(nueva_sesion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sesión creada exitosamente',
            'data': nueva_sesion.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear sesión: {str(e)}'
        }), 500


@eventos_bp.route('/sesiones/<int:id>', methods=['PUT'])
def actualizar_sesion(id):
    """
    Actualizar una sesión existente.
    
    Body JSON:
        - nombre: nuevo nombre (opcional)
        - descripcion: nueva descripción (opcional)
    """
    try:
        sesion = Sesion.query.get(id)
        
        if not sesion:
            return jsonify({
                'success': False,
                'error': f'Sesión con ID {id} no encontrada'
            }), 404
        
        data = request.get_json()
        
        if 'nombre' in data:
            nombre = data['nombre'].strip()
            if len(nombre) < 3:
                return jsonify({
                    'success': False,
                    'error': 'El nombre debe tener al menos 3 caracteres'
                }), 400
            
            # Verificar que no exista otra sesión con el mismo nombre
            sesion_existente = Sesion.query.filter(
                Sesion.nombre == nombre,
                Sesion.id_sesion != id
            ).first()
            
            if sesion_existente:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe otra sesión con el nombre "{nombre}"'
                }), 400
            
            sesion.nombre = nombre
        
        if 'descripcion' in data:
            sesion.descripcion = data['descripcion'].strip()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sesión actualizada exitosamente',
            'data': sesion.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al actualizar sesión: {str(e)}'
        }), 500


@eventos_bp.route('/sesiones/<int:id>', methods=['DELETE'])
def eliminar_sesion(id):
    """Eliminar una sesión"""
    try:
        sesion = Sesion.query.get(id)
        
        if not sesion:
            return jsonify({
                'success': False,
                'error': f'Sesión con ID {id} no encontrada'
            }), 404
        
        # Verificar si hay eventos asociados
        eventos_count = Evento.query.filter_by(id_sesion=id).count()
        if eventos_count > 0:
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar la sesión porque tiene {eventos_count} evento(s) asociado(s)'
            }), 400
        
        nombre_sesion = sesion.nombre
        
        db.session.delete(sesion)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Sesión "{nombre_sesion}" eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar sesión: {str(e)}'
        }), 500


# ============================================================================
# CRUD DE TIPOS DE EVENTO
# ============================================================================

@eventos_bp.route('/tipos-evento', methods=['GET'])
def listar_tipos_evento():
    """Listar todos los tipos de evento"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        
        query = TipoEvento.query
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(TipoEvento.nombre.ilike(search_filter))
        
        query = query.order_by(TipoEvento.nombre.asc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [tipo.to_dict() for tipo in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al listar tipos de evento: {str(e)}'
        }), 500


@eventos_bp.route('/tipos-evento/<int:id>', methods=['GET'])
def obtener_tipo_evento(id):
    """Obtener un tipo de evento específico por ID"""
    try:
        tipo_evento = TipoEvento.query.get(id)
        
        if not tipo_evento:
            return jsonify({
                'success': False,
                'error': f'Tipo de evento con ID {id} no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': tipo_evento.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener tipo de evento: {str(e)}'
        }), 500


@eventos_bp.route('/tipos-evento', methods=['POST'])
def crear_tipo_evento():
    """
    Crear un nuevo tipo de evento.
    
    Body JSON:
        - nombre: nombre del tipo de evento (requerido)
        - descripcion: descripción del tipo (opcional)
    """
    try:
        data = request.get_json()
        
        if 'nombre' not in data or not data['nombre'].strip():
            return jsonify({
                'success': False,
                'error': 'El campo nombre es requerido'
            }), 400
        
        nombre = data['nombre'].strip()
        if len(nombre) < 3:
            return jsonify({
                'success': False,
                'error': 'El nombre debe tener al menos 3 caracteres'
            }), 400
        
        # Verificar que no exista un tipo con el mismo nombre
        tipo_existente = TipoEvento.query.filter_by(nombre=nombre).first()
        if tipo_existente:
            return jsonify({
                'success': False,
                'error': f'Ya existe un tipo de evento con el nombre "{nombre}"'
            }), 400
        
        nuevo_tipo = TipoEvento(
            nombre=nombre,
            descripcion=data.get('descripcion', '').strip()
        )
        
        db.session.add(nuevo_tipo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de evento creado exitosamente',
            'data': nuevo_tipo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear tipo de evento: {str(e)}'
        }), 500


@eventos_bp.route('/tipos-evento/<int:id>', methods=['PUT'])
def actualizar_tipo_evento(id):
    """
    Actualizar un tipo de evento existente.
    
    Body JSON:
        - nombre: nuevo nombre (opcional)
        - descripcion: nueva descripción (opcional)
    """
    try:
        tipo_evento = TipoEvento.query.get(id)
        
        if not tipo_evento:
            return jsonify({
                'success': False,
                'error': f'Tipo de evento con ID {id} no encontrado'
            }), 404
        
        data = request.get_json()
        
        if 'nombre' in data:
            nombre = data['nombre'].strip()
            if len(nombre) < 3:
                return jsonify({
                    'success': False,
                    'error': 'El nombre debe tener al menos 3 caracteres'
                }), 400
            
            # Verificar que no exista otro tipo con el mismo nombre
            tipo_existente = TipoEvento.query.filter(
                TipoEvento.nombre == nombre,
                TipoEvento.id_tipo_evento != id
            ).first()
            
            if tipo_existente:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe otro tipo de evento con el nombre "{nombre}"'
                }), 400
            
            tipo_evento.nombre = nombre
        
        if 'descripcion' in data:
            tipo_evento.descripcion = data['descripcion'].strip()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tipo de evento actualizado exitosamente',
            'data': tipo_evento.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al actualizar tipo de evento: {str(e)}'
        }), 500


@eventos_bp.route('/tipos-evento/<int:id>', methods=['DELETE'])
def eliminar_tipo_evento(id):
    """Eliminar un tipo de evento"""
    try:
        tipo_evento = TipoEvento.query.get(id)
        
        if not tipo_evento:
            return jsonify({
                'success': False,
                'error': f'Tipo de evento con ID {id} no encontrado'
            }), 404
        
        # Verificar si hay eventos asociados
        eventos_count = Evento.query.filter_by(id_tipo_evento=id).count()
        if eventos_count > 0:
            return jsonify({
                'success': False,
                'error': f'No se puede eliminar el tipo de evento porque tiene {eventos_count} evento(s) asociado(s)'
            }), 400
        
        nombre_tipo = tipo_evento.nombre
        
        db.session.delete(tipo_evento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Tipo de evento "{nombre_tipo}" eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar tipo de evento: {str(e)}'
        }), 500


# ============================================================================
# ENDPOINTS ADICIONALES
# ============================================================================

@eventos_bp.route('/eventos/proximos', methods=['GET'])
def eventos_proximos():
    """Listar eventos próximos (desde hoy en adelante)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        
        query = Evento.query.filter(Evento.fecha_evento >= date.today())
        
        if categoria_id:
            query = query.filter_by(id_categoria=categoria_id)
        
        query = query.order_by(Evento.fecha_evento.asc()).limit(limit)
        eventos = query.all()
        
        eventos_data = []
        for evento in eventos:
            evento_dict = evento.to_dict()
            if evento.categoria:
                evento_dict['categoria'] = evento.categoria.to_dict()
            if evento.sesion:
                evento_dict['sesion'] = evento.sesion.to_dict()
            tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
            if tipo_evento:
                evento_dict['tipo_evento'] = tipo_evento.to_dict()
            eventos_data.append(evento_dict)
        
        return jsonify({
            'success': True,
            'data': eventos_data,
            'total': len(eventos_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener eventos próximos: {str(e)}'
        }), 500


@eventos_bp.route('/eventos/categoria/<int:categoria_id>', methods=['GET'])
def eventos_por_categoria(categoria_id):
    """Listar todos los eventos de una categoría específica"""
    try:
        # Verificar que la categoría exista
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return jsonify({
                'success': False,
                'error': f'Categoría con ID {categoria_id} no encontrada'
            }), 404
        
        eventos = Evento.query.filter_by(id_categoria=categoria_id).order_by(Evento.fecha_evento.desc()).all()
        
        eventos_data = []
        for evento in eventos:
            evento_dict = evento.to_dict()
            if evento.sesion:
                evento_dict['sesion'] = evento.sesion.to_dict()
            tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
            if tipo_evento:
                evento_dict['tipo_evento'] = tipo_evento.to_dict()
            eventos_data.append(evento_dict)
        
        return jsonify({
            'success': True,
            'data': eventos_data,
            'categoria': categoria.to_dict(),
            'total': len(eventos_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener eventos por categoría: {str(e)}'
        }), 500

