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
from ..services.catalogos_service import catalogos_service
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
        # Obtener catálogos desde la base de datos
        catalogos = catalogos_service.obtener_catalogos_completos()

        # Respuesta exitosa
        return jsonify({
            'success': True,
            'message': 'Catálogos obtenidos exitosamente',
            'data': catalogos,
            'status_code': 200
        }), 200

    except Exception as e:
        logger.error(f"Error inesperado al obtener catálogos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@catalogos_bp.route('/fix-structure', methods=['POST', 'OPTIONS'])
@cross_origin()
def fix_catalogos_structure():
    """
    Endpoint para corregir la estructura de las tablas de catálogos.
    """
    try:
        from ..models.base import db
        from sqlalchemy import text

        # Verificar estructura actual de tabla sexos
        result = db.session.execute(text("PRAGMA table_info(puerta_orion_sexo)"))
        columnas = [row[1] for row in result.fetchall()]

        cambios_realizados = []

        # Agregar columna nombre si no existe
        if 'nombre' not in columnas:
            db.session.execute(text("ALTER TABLE puerta_orion_sexo ADD COLUMN nombre VARCHAR(150)"))
            cambios_realizados.append("Agregada columna 'nombre' a tabla sexos")

        # Verificar datos existentes
        result = db.session.execute(text("SELECT COUNT(*) FROM puerta_orion_tipo_documento"))
        tipos_count = result.fetchone()[0]

        result = db.session.execute(text("SELECT COUNT(*) FROM puerta_orion_sexo"))
        sexos_count = result.fetchone()[0]

        # Poblar tipos de documento si están vacíos
        if tipos_count == 0:
            tipos_sql = text("""
            INSERT INTO puerta_orion_tipo_documento (id_documento, nombre_documento, created_at, updated_at) VALUES
            (1, 'Cédula de Ciudadanía', datetime('now'), datetime('now')),
            (2, 'Tarjeta de Identidad', datetime('now'), datetime('now')),
            (3, 'Cédula de Extranjería', datetime('now'), datetime('now')),
            (4, 'Pasaporte', datetime('now'), datetime('now')),
            (5, 'Registro Civil', datetime('now'), datetime('now'))
            """)
            db.session.execute(tipos_sql)
            cambios_realizados.append("Poblados tipos de documento")

        # Poblar sexos si están vacíos
        if sexos_count == 0:
            # Verificar estructura completa de la tabla
            result = db.session.execute(text("PRAGMA table_info(puerta_orion_sexo)"))
            columnas_info = result.fetchall()
            nombres_columnas = [col[1] for col in columnas_info]

            # Construir SQL dinámicamente basado en las columnas existentes
            if 'sexo' in nombres_columnas and 'nombre' in nombres_columnas:
                sexos_sql = text("""
                INSERT INTO puerta_orion_sexo (id_sexo, sexo, nombre, created_at, updated_at) VALUES
                (1, 'M', 'Masculino', datetime('now'), datetime('now')),
                (2, 'F', 'Femenino', datetime('now'), datetime('now')),
                (3, 'O', 'Otro', datetime('now'), datetime('now'))
                """)
            elif 'nombre' in nombres_columnas:
                sexos_sql = text("""
                INSERT INTO puerta_orion_sexo (id_sexo, nombre, created_at, updated_at) VALUES
                (1, 'Masculino', datetime('now'), datetime('now')),
                (2, 'Femenino', datetime('now'), datetime('now')),
                (3, 'Otro', datetime('now'), datetime('now'))
                """)
            else:
                # Solo usar columnas básicas
                sexos_sql = text("""
                INSERT INTO puerta_orion_sexo (id_sexo, created_at, updated_at) VALUES
                (1, datetime('now'), datetime('now')),
                (2, datetime('now'), datetime('now')),
                (3, datetime('now'), datetime('now'))
                """)

            db.session.execute(sexos_sql)
            cambios_realizados.append("Poblados sexos")

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Estructura de catálogos corregida exitosamente',
            'cambios': cambios_realizados,
            'status_code': 200
        }), 200

    except Exception as e:
        logger.error(f"Error corrigiendo estructura de catálogos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error corrigiendo estructura: {str(e)}',
            'status_code': 500
        }), 500


@catalogos_bp.route('/debug', methods=['GET', 'OPTIONS'])
@cross_origin()
def debug_catalogos():
    """
    Endpoint de depuración para verificar las consultas de catálogos.
    """
    try:
        from ..models.catalogos.tipo_documento import TipoDocumento
        from ..models.categorias.sexo import Sexo
        from ..models.categorias.categoria import Categoria

        debug_info = {}

        # Verificar tipos de documento
        try:
            tipos_count = TipoDocumento.query.count()
            tipos = TipoDocumento.query.all()
            debug_info['tipos_documento'] = {
                'count': tipos_count,
                'tablename': TipoDocumento.__tablename__,
                'data': [{'id': t.id_documento, 'nombre': t.nombre_documento} for t in tipos]
            }
        except Exception as e:
            debug_info['tipos_documento'] = {'error': str(e)}

        # Verificar sexos
        try:
            sexos_count = Sexo.query.count()
            sexos = Sexo.query.all()
            debug_info['sexos'] = {
                'count': sexos_count,
                'tablename': Sexo.__tablename__,
                'data': [{'id': s.id_sexo, 'nombre': s.nombre} for s in sexos]
            }
        except Exception as e:
            debug_info['sexos'] = {'error': str(e)}

        # Verificar categorías
        try:
            categorias_count = Categoria.query.count()
            categorias = Categoria.query.all()
            debug_info['categorias'] = {
                'count': categorias_count,
                'tablename': Categoria.__tablename__,
                'data': [{'id': c.id_categoria, 'nombre': c.nombre_categoria, 'estado': c.estado} for c in categorias]
            }
        except Exception as e:
            debug_info['categorias'] = {'error': str(e)}

        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'status_code': 200
        }), 200

    except Exception as e:
        logger.error(f"Error en debug de catálogos: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error en debug: {str(e)}',
            'status_code': 500
        }), 500


@catalogos_bp.route('/poblar-categorias', methods=['POST'])
def poblar_categorias():
    """
    Endpoint para poblar la tabla de categorías con datos iniciales.
    """
    try:
        from ..models.base import db
        from sqlalchemy import text

        # Verificar si ya hay categorías
        categorias_existentes = db.session.execute(
            text("SELECT COUNT(*) FROM puerta_orion_categoria")
        ).scalar()

        if categorias_existentes > 0:
            return jsonify({
                'success': True,
                'message': f'Ya existen {categorias_existentes} categorías en la base de datos',
                'status_code': 200
            }), 200

        # Datos iniciales de categorías
        categorias_data = [
            {
                'nombre_categoria': 'Fútbol',
                'codigo_categoria': 101,
                'edad_minima': 6,
                'edad_maxima': 18
            },
            {
                'nombre_categoria': 'Básquetbol',
                'codigo_categoria': 102,
                'edad_minima': 8,
                'edad_maxima': 18
            },
            {
                'nombre_categoria': 'Voleibol',
                'codigo_categoria': 103,
                'edad_minima': 10,
                'edad_maxima': 18
            },
            {
                'nombre_categoria': 'Tenis',
                'codigo_categoria': 104,
                'edad_minima': 6,
                'edad_maxima': 18
            },
            {
                'nombre_categoria': 'Natación',
                'codigo_categoria': 105,
                'edad_minima': 4,
                'edad_maxima': 18
            }
        ]

        # Insertar categorías
        categorias_insertadas = []
        for cat_data in categorias_data:
            insert_sql = text("""
                INSERT INTO puerta_orion_categoria
                (nombre_categoria, codigo_categoria, edad_minima, edad_maxima, estado, created_at, updated_at)
                VALUES (:nombre_categoria, :codigo_categoria, :edad_minima, :edad_maxima, 1, datetime('now'), datetime('now'))
            """)

            db.session.execute(insert_sql, cat_data)
            categorias_insertadas.append(cat_data['nombre_categoria'])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Categorías pobladas exitosamente: {len(categorias_insertadas)}',
            'categorias_insertadas': categorias_insertadas,
            'status_code': 200
        }), 200

    except Exception as e:
        logger.error(f"Error poblando categorías: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error poblando categorías: {str(e)}',
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
