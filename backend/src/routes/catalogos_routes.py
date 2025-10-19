"""
Rutas de catálogos para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para obtener datos de catálogos
- Proporcionar acceso a tipos de documento, sexos, etc.

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from flask import Blueprint, jsonify, current_app
from flask_cors import cross_origin
from ..models.catalogos.tipo_documento import TipoDocumento
from ..models.categorias.sexo import Sexo
from ..models.categorias.categoria import Categoria
from ..utils.logger import obtener_registrador

# Crear Blueprint de catálogos
catalogos_bp = Blueprint('catalogos', __name__, url_prefix='/api/catalogos')
logger = obtener_registrador('aplicacion')


@catalogos_bp.route('/tipos-documento', methods=['GET', 'OPTIONS'])
@cross_origin()
def obtener_tipos_documento():
    """
    Endpoint para obtener todos los tipos de documento.
    
    Returns:
        JSON: Lista de tipos de documento disponibles
    """
    try:
        # Obtener todos los tipos de documento
        tipos_documento = TipoDocumento.query.all()
        
        # Mapeo manual de nombres a códigos
        mapeo_codigos = {
            'Cédula de Ciudadanía': 'cc',
            'Cédula de Extranjería': 'ce',
            'Tarjeta de Identidad': 'ti',
            'Pasaporte': 'pasaporte'
        }
        
        # Serializar datos
        datos_tipos = []
        for tipo in tipos_documento:
            codigo = mapeo_codigos.get(tipo.nombre_documento, tipo.nombre_documento.lower().replace(' ', '_'))
            datos_tipos.append({
                'id': tipo.id_documento,
                'codigo': codigo,
                'nombre': tipo.nombre_documento
            })
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Tipos de documento obtenidos exitosamente',
            'data': datos_tipos,
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener tipos de documento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@catalogos_bp.route('/sexos', methods=['GET', 'OPTIONS'])
@cross_origin()
def obtener_sexos():
    """
    Endpoint para obtener todos los sexos.
    
    Returns:
        JSON: Lista de sexos disponibles
    """
    try:
        # Obtener todos los sexos
        sexos = Sexo.query.all()
        
        # Mapeo manual de nombres a valores
        mapeo_valores = {
            'Masculino': 'masculino',
            'Femenino': 'femenino',
            'Otro': 'otro'
        }
        
        # Serializar datos
        datos_sexos = []
        for sexo in sexos:
            valor = mapeo_valores.get(sexo.nombre, sexo.nombre.lower())
            datos_sexos.append({
                'id': sexo.id_sexo,
                'valor': valor,
                'nombre': sexo.nombre
            })
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Sexos obtenidos exitosamente',
            'data': datos_sexos,
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener sexos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@catalogos_bp.route('/catalogos-completos', methods=['GET', 'OPTIONS'])
@cross_origin()
def obtener_catalogos_completos():
    """
    Endpoint para obtener todos los catálogos necesarios.
    
    Returns:
        JSON: Objeto con todos los catálogos
    """
    try:
        # Mapeos manuales
        mapeo_codigos_doc = {
            'Cédula de Ciudadanía': 'cc',
            'Cédula de Extranjería': 'ce',
            'Tarjeta de Identidad': 'ti',
            'Pasaporte': 'pasaporte'
        }
        
        mapeo_valores_sexo = {
            'Masculino': 'masculino',
            'Femenino': 'femenino',
            'Otro': 'otro'
        }
        
        # Obtener tipos de documento
        tipos_documento = TipoDocumento.query.all()
        datos_tipos = []
        for tipo in tipos_documento:
            codigo = mapeo_codigos_doc.get(tipo.nombre_documento, tipo.nombre_documento.lower().replace(' ', '_'))
            datos_tipos.append({
                'id': tipo.id_documento,
                'codigo': codigo,
                'nombre': tipo.nombre_documento
            })
        
        # Obtener sexos
        sexos = Sexo.query.all()
        datos_sexos = []
        for sexo in sexos:
            valor = mapeo_valores_sexo.get(sexo.nombre, sexo.nombre.lower())
            datos_sexos.append({
                'id': sexo.id_sexo,
                'valor': valor,
                'nombre': sexo.nombre
            })
        
        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Catálogos obtenidos exitosamente',
            'data': {
                'tipos_documento': datos_tipos,
                'sexos': datos_sexos
            },
            'status_code': 200
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener catálogos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@catalogos_bp.route('/categorias', methods=['GET', 'OPTIONS'])
@cross_origin()
def obtener_categorias():
    """Obtener todas las categorías disponibles"""
    try:
        categorias = Categoria.query.filter_by(estado=True).all()
        
        categorias_data = []
        for categoria in categorias:
            categorias_data.append({
                'id_categoria': categoria.id_categoria,
                'nombre_categoria': categoria.nombre_categoria,
                'codigo_categoria': categoria.codigo_categoria,
                'edad_minima': categoria.edad_minima,
                'edad_maxima': categoria.edad_maxima
            })
        
        return jsonify({
            'success': True,
            'data': categorias_data,
            'message': 'Categorías obtenidas exitosamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener categorías: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al obtener categorías: {str(e)}'
        }), 500


# Manejadores de errores específicos del Blueprint
@catalogos_bp.errorhandler(400)
def bad_request(error):
    """Manejador de errores 400 (Bad Request)."""
    return jsonify({
        'success': False,
        'error': 'Solicitud incorrecta',
        'message': 'Verifique los datos enviados',
        'status_code': 400
    }), 400


@catalogos_bp.errorhandler(500)
def internal_error(error):
    """Manejador de errores 500 (Internal Server Error)."""
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Contacte al administrador',
        'status_code': 500
    }), 500


# Función para registrar el Blueprint en la aplicación
def registrar_catalogos_routes(app):
    """
    Registra las rutas de catálogos en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(catalogos_bp)
    logger.info("Rutas de catálogos registradas exitosamente")
