"""
Rutas para catálogos y datos fijos.
Proporciona endpoints GET para datos de referencia.
"""

from flask import Blueprint, jsonify
from src.models import (
    TipoDocumento, 
    Sexo, 
    GrupoSanguineo, 
    Categoria, 
    MetodoPago
)

# Crear Blueprint
catalogos_bp = Blueprint('catalogos', __name__)


@catalogos_bp.route('/tipo-documento', methods=['GET'])
def obtener_tipo_documento():
    """Obtiene todos los tipos de documento"""
    try:
        tipos = TipoDocumento.query.all()
        return jsonify({
            'success': True,
            'data': [tipo.to_dict() for tipo in tipos],
            'total': len(tipos)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@catalogos_bp.route('/sexo', methods=['GET'])
def obtener_sexo():
    """Obtiene todos los sexos"""
    try:
        sexos = Sexo.query.all()
        return jsonify({
            'success': True,
            'data': [sexo.to_dict() for sexo in sexos],
            'total': len(sexos)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@catalogos_bp.route('/grupo-sanguineo', methods=['GET'])
def obtener_grupo_sanguineo():
    """Obtiene todos los grupos sanguíneos"""
    try:
        grupos = GrupoSanguineo.query.all()
        return jsonify({
            'success': True,
            'data': [grupo.to_dict() for grupo in grupos],
            'total': len(grupos)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@catalogos_bp.route('/categoria', methods=['GET'])
def obtener_categoria():
    """Obtiene todas las categorías"""
    try:
        categorias = Categoria.query.all()
        return jsonify({
            'success': True,
            'data': [cat.to_dict() for cat in categorias],
            'total': len(categorias)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@catalogos_bp.route('/metodo-pago', methods=['GET'])
def obtener_metodo_pago():
    """Obtiene todos los métodos de pago"""
    try:
        metodos = MetodoPago.query.all()
        return jsonify({
            'success': True,
            'data': [metodo.to_dict() for metodo in metodos],
            'total': len(metodos)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

