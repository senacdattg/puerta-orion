"""
Rutas para la gestión de la galería de imágenes.
"""

from flask import Blueprint, request, jsonify
from src.database.database import db
from src.models.galeria.galeria import Galeria
from src.models.eventos.tipo_evento import TipoEvento
from src.models.categorias.categoria import Categoria
from src.middleware.auth_decorator import token_required
from src.utils.logger import logger

galeria_bp = Blueprint('galeria', __name__, url_prefix='/api/galeria')


@galeria_bp.route('/', methods=['GET'])
@token_required()
def listar_galeria():
    """
    Listar todas las imágenes de la galería con filtros opcionales.
    """
    try:
        # Parámetros de filtro
        id_tipo_evento = request.args.get('id_tipo_evento', type=int)
        id_categoria = request.args.get('id_categoria', type=int)
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        
        # Construir consulta
        query = Galeria.query
        
        if id_tipo_evento:
            query = query.filter(Galeria.id_tipo_evento == id_tipo_evento)
        
        if id_categoria:
            query = query.filter(Galeria.id_categoria == id_categoria)
        
        # Aplicar paginación
        query = query.offset(offset).limit(limit)
        
        # Ejecutar consulta
        imagenes = query.all()
        
        # Convertir a diccionario
        imagenes_data = []
        for imagen in imagenes:
            imagen_dict = imagen.to_dict()
            
            # Agregar información de relaciones
            if imagen.tipo_evento:
                imagen_dict['tipo_evento'] = imagen.tipo_evento.to_dict()
            
            if imagen.categoria:
                imagen_dict['categoria'] = imagen.categoria.to_dict()
            
            imagenes_data.append(imagen_dict)
        
        return jsonify({
            'success': True,
            'data': imagenes_data,
            'total': len(imagenes_data),
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando galería: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error listando galería: {str(e)}',
            'status_code': 500
        }), 500


@galeria_bp.route('/<int:id_galeria>', methods=['GET'])
@token_required()
def obtener_imagen(id_galeria):
    """
    Obtener una imagen específica por ID.
    """
    try:
        imagen = Galeria.query.get(id_galeria)
        
        if not imagen:
            return jsonify({
                'success': False,
                'error': 'Imagen no encontrada',
                'status_code': 404
            }), 404
        
        imagen_dict = imagen.to_dict()
        
        # Agregar información de relaciones
        if imagen.tipo_evento:
            imagen_dict['tipo_evento'] = imagen.tipo_evento.to_dict()
        
        if imagen.categoria:
            imagen_dict['categoria'] = imagen.categoria.to_dict()
        
        return jsonify({
            'success': True,
            'data': imagen_dict,
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo imagen {id_galeria}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo imagen: {str(e)}',
            'status_code': 500
        }), 500


@galeria_bp.route('/', methods=['POST'])
@token_required()
def crear_imagen():
    """
    Crear una nueva imagen en la galería.
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('titulo'):
            return jsonify({
                'success': False,
                'error': 'El título es requerido',
                'status_code': 400
            }), 400
        
        if not data.get('url_imagen'):
            return jsonify({
                'success': False,
                'error': 'La URL de la imagen es requerida',
                'status_code': 400
            }), 400
        
        # Validar foreign keys si se proporcionan
        if data.get('id_tipo_evento'):
            tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
            if not tipo_evento:
                return jsonify({
                    'success': False,
                    'error': 'Tipo de evento no encontrado',
                    'status_code': 400
                }), 400
        
        if data.get('id_categoria'):
            categoria = Categoria.query.get(data['id_categoria'])
            if not categoria:
                return jsonify({
                    'success': False,
                    'error': 'Categoría no encontrada',
                    'status_code': 400
                }), 400
        
        # Crear nueva imagen
        nueva_imagen = Galeria(
            titulo=data['titulo'],
            url_imagen=data['url_imagen'],
            descripcion=data.get('descripcion'),
            id_tipo_evento=data.get('id_tipo_evento'),
            id_categoria=data.get('id_categoria')
        )
        
        db.session.add(nueva_imagen)
        db.session.commit()
        
        logger.info(f"Imagen creada: {nueva_imagen.id_galeria} - {nueva_imagen.titulo}")
        
        return jsonify({
            'success': True,
            'data': nueva_imagen.to_dict(),
            'message': 'Imagen creada exitosamente',
            'status_code': 201
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando imagen: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error creando imagen: {str(e)}',
            'status_code': 500
        }), 500


@galeria_bp.route('/<int:id_galeria>', methods=['PUT'])
@token_required()
def actualizar_imagen(id_galeria):
    """
    Actualizar una imagen existente.
    """
    try:
        imagen = Galeria.query.get(id_galeria)
        
        if not imagen:
            return jsonify({
                'success': False,
                'error': 'Imagen no encontrada',
                'status_code': 404
            }), 404
        
        data = request.get_json()
        
        # Validar foreign keys si se proporcionan
        if data.get('id_tipo_evento'):
            tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
            if not tipo_evento:
                return jsonify({
                    'success': False,
                    'error': 'Tipo de evento no encontrado',
                    'status_code': 400
                }), 400
        
        if data.get('id_categoria'):
            categoria = Categoria.query.get(data['id_categoria'])
            if not categoria:
                return jsonify({
                    'success': False,
                    'error': 'Categoría no encontrada',
                    'status_code': 400
                }), 400
        
        # Actualizar campos
        if 'titulo' in data:
            imagen.titulo = data['titulo']
        
        if 'url_imagen' in data:
            imagen.url_imagen = data['url_imagen']
        
        if 'descripcion' in data:
            imagen.descripcion = data['descripcion']
        
        if 'id_tipo_evento' in data:
            imagen.id_tipo_evento = data['id_tipo_evento']
        
        if 'id_categoria' in data:
            imagen.id_categoria = data['id_categoria']
        
        db.session.commit()
        
        logger.info(f"Imagen actualizada: {imagen.id_galeria} - {imagen.titulo}")
        
        return jsonify({
            'success': True,
            'data': imagen.to_dict(),
            'message': 'Imagen actualizada exitosamente',
            'status_code': 200
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando imagen {id_galeria}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error actualizando imagen: {str(e)}',
            'status_code': 500
        }), 500


@galeria_bp.route('/<int:id_galeria>', methods=['DELETE'])
@token_required()
def eliminar_imagen(id_galeria):
    """
    Eliminar una imagen de la galería.
    """
    try:
        imagen = Galeria.query.get(id_galeria)
        
        if not imagen:
            return jsonify({
                'success': False,
                'error': 'Imagen no encontrada',
                'status_code': 404
            }), 404
        
        titulo_imagen = imagen.titulo
        
        db.session.delete(imagen)
        db.session.commit()
        
        logger.info(f"Imagen eliminada: {id_galeria} - {titulo_imagen}")
        
        return jsonify({
            'success': True,
            'message': 'Imagen eliminada exitosamente',
            'status_code': 200
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando imagen {id_galeria}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error eliminando imagen: {str(e)}',
            'status_code': 500
        }), 500


@galeria_bp.route('/catalogos', methods=['GET'])
@token_required()
def obtener_catalogos():
    """
    Obtener catálogos necesarios para la galería (tipos de evento y categorías).
    """
    try:
        # Obtener tipos de evento
        tipos_evento = TipoEvento.query.all()
        tipos_evento_data = [tipo.to_dict() for tipo in tipos_evento]
        
        # Obtener categorías
        categorias = Categoria.query.filter_by(estado=True).all()
        categorias_data = [cat.to_dict() for cat in categorias]
        
        return jsonify({
            'success': True,
            'data': {
                'tipos_evento': tipos_evento_data,
                'categorias': categorias_data
            },
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo catálogos de galería: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error obteniendo catálogos: {str(e)}',
            'status_code': 500
        }), 500
