"""
Rutas para la gestión de archivos y carga de imágenes.
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from src.models.base import db
from src.models.galeria.galeria import Galeria
from src.models.eventos.tipo_evento import TipoEvento
from src.models.categorias.categoria import Categoria
from ..middleware.auth_decorator import token_required
from src.utils.logger import logger

archivos_bp = Blueprint('archivos', __name__, url_prefix='/api/archivos')

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generar un nombre único para el archivo"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}"

@archivos_bp.route('/upload', methods=['POST'])
@token_required()
def subir_archivo():
    """
    Subir un archivo de imagen.
    
    Form data:
        - file: archivo de imagen (requerido)
        - titulo: título de la imagen (requerido)
        - descripcion: descripción (opcional)
        - id_tipo_evento: ID del tipo de evento (opcional)
        - id_categoria: ID de la categoría (opcional)
    """
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se envió ningún archivo'
            }), 400
        
        file = request.files['file']
        
        # Verificar que el archivo no esté vacío
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            }), 400
        
        # Verificar que el archivo sea válido
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Tipo de archivo no permitido. Tipos permitidos: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Verificar tamaño del archivo
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'El archivo es demasiado grande. Tamaño máximo: {MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # Obtener datos del formulario
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        id_tipo_evento = request.form.get('id_tipo_evento')
        id_categoria = request.form.get('id_categoria')
        
        # Validar título
        if not titulo:
            return jsonify({
                'success': False,
                'error': 'El título es requerido'
            }), 400
        
        # Validar foreign keys si se proporcionan
        if id_tipo_evento:
            try:
                id_tipo_evento = int(id_tipo_evento)
                if not TipoEvento.query.get(id_tipo_evento):
                    return jsonify({
                        'success': False,
                        'error': f'Tipo de evento con ID {id_tipo_evento} no encontrado'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'ID de tipo de evento inválido'
                }), 400
        
        if id_categoria:
            try:
                id_categoria = int(id_categoria)
                if not Categoria.query.get(id_categoria):
                    return jsonify({
                        'success': False,
                        'error': f'Categoría con ID {id_categoria} no encontrada'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'ID de categoría inválido'
                }), 400
        
        # Crear directorio de uploads si no existe
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'galeria')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        
        # Guardar el archivo
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Generar URL completa para la imagen
        image_url = f'http://localhost:5000/static/uploads/galeria/{unique_filename}'
        
        # Crear registro en la base de datos
        nueva_imagen = Galeria(
            titulo=titulo,
            url_imagen=image_url,
            descripcion=descripcion if descripcion else None,
            id_tipo_evento=id_tipo_evento if id_tipo_evento else None,
            id_categoria=id_categoria if id_categoria else None
        )
        
        db.session.add(nueva_imagen)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Imagen subida exitosamente',
            'data': nueva_imagen.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al subir archivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@archivos_bp.route('/delete/<int:id_galeria>', methods=['DELETE'])
@token_required()
def eliminar_archivo(id_galeria):
    """
    Eliminar una imagen y su archivo asociado.
    """
    try:
        imagen = Galeria.query.get(id_galeria)
        
        if not imagen:
            return jsonify({
                'success': False,
                'error': 'Imagen no encontrada'
            }), 404
        
        # Eliminar archivo físico si existe
        if imagen.url_imagen and imagen.url_imagen.startswith('/static/uploads/'):
            file_path = os.path.join(current_app.root_path, imagen.url_imagen.lstrip('/'))
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    logger.warning(f"No se pudo eliminar el archivo {file_path}: {str(e)}")
        
        # Eliminar registro de la base de datos
        db.session.delete(imagen)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Imagen eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar archivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500

@archivos_bp.route('/fix-urls', methods=['POST'])
@token_required()
def arreglar_urls():
    """
    Endpoint temporal para arreglar URLs relativas a URLs completas.
    """
    try:
        # Buscar imágenes con URLs relativas
        imagenes_relativas = Galeria.query.filter(Galeria.url_imagen.like('/static/uploads/%')).all()
        
        actualizadas = 0
        for imagen in imagenes_relativas:
            # Convertir URL relativa a URL completa
            nueva_url = f'http://localhost:5000{imagen.url_imagen}'
            imagen.url_imagen = nueva_url
            actualizadas += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Se actualizaron {actualizadas} URLs de imágenes',
            'actualizadas': actualizadas
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al arreglar URLs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500
