"""
Rutas para gestión de deportistas.

Este archivo orquesta la definición de rutas y la delegación de lógica a los 
servicios del dominio de deportistas y catálogos. Cada módulo cumple con un 
propósito único siguiendo SRP, DRY y KISS. 
"""

from flask import Blueprint, request, jsonify
from src.services.deportista_service import DeportistaService
from src.services.registro_deportista_service import RegistroDeportistaService
from src.services.catalogos_service import CatalogosService
from src.utils.logger import obtener_registrador
from src.middleware.auth_decorator import token_required, get_current_user

deportistas_bp = Blueprint('deportistas', __name__)
logger = obtener_registrador('aplicacion')

# ---- Rutas principales de deportistas (CRUD) ----

@deportistas_bp.route('/deportistas', methods=['POST'])
def crear_deportista():
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'El contenido debe ser JSON', 'status_code': 400}), 400

        datos = request.get_json()
        result = DeportistaService.crear_deportista(datos)

        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al crear deportista: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/deportistas/registro-completo', methods=['POST'])
def registro_deportista_completo():
    """
    Endpoint para registro completo de deportista.
    
    Permite registrar un deportista con toda su información:
    - Datos básicos del deportista
    - Información deportiva
    - Diagnósticos médicos
    
    Body JSON:
    {
        "datos_deportista": {
            "id_persona": 1,
            "id_categoria": 1,
            "peso": 65.5,
            "altura": 1.75,
            ...
        },
        "informacion_deportiva": {
            "practica_otro_deporte": true,
            "id_deporte": 2,
            ...
        },
        "diagnosticos": [1, 2, 3]
    }
    """
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'El contenido debe ser JSON', 'status_code': 400}), 400

        datos = request.get_json()
        result = RegistroDeportistaService.registrar_deportista_nuevo(datos)

        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al registrar deportista completo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/deportistas/registrar', methods=['POST'])
@token_required()
def registrar_deportista():
    """
    Endpoint para registrar un deportista con cálculo automático de categoría.
    
    Este endpoint:
    - Calcula automáticamente la categoría basándose en la fecha de nacimiento
    - Valida que todos los IDs existan en sus respectivas tablas
    - Maneja la transacción completa con rollback en caso de error
    - Valida la coherencia entre tipo de enfermedad y diagnósticos
    
    Body JSON según estructura:
    {
        "datos_deportista": {
            "id_persona": 10,
            "fecha_nacimiento": 2005,
            "id_tipo_sanguineo": 2,
            "id_ciudad_recidencia": 1,
            "id_eps": 3
        },
        "informacion_deportiva": {
            "practica_otro_deporte": true,
            "participa_escuela": true,
            "recomendacion_medica": false,
            "descripcion_recomendacion": null,
            "id_escuela": 5,
            "id_deporte": 8,
            "id_institucion_registro": 2
        },
        "tipo_enfermedad": 1,
        "diagnostico": [1,2,3]
    }
    """
    try:
        if not request.is_json:
            return jsonify({'status': 'error', 'message': 'El contenido debe ser JSON', 'status_code': 400}), 400

        datos = request.get_json()

        # Obtener id_persona del usuario autenticado (inyectado por el middleware)
        usuario_actual = get_current_user()
        if not usuario_actual or not usuario_actual.get('persona'):
            return jsonify({'status': 'error', 'message': 'Usuario no autenticado', 'status_code': 401}), 401

        id_persona = usuario_actual['persona'].get('id_persona')
        if not id_persona:
            return jsonify({'status': 'error', 'message': 'No se pudo determinar la persona del usuario', 'status_code': 401}), 401

        # Asegurar estructura base
        if 'datos_deportista' not in datos or datos['datos_deportista'] is None:
            datos['datos_deportista'] = {}

        # Inyectar id_persona automáticamente (no se requiere que el frontend lo envíe)
        datos['datos_deportista']['id_persona'] = id_persona

        result = RegistroDeportistaService.registrar_deportista_nuevo(datos)

        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al registrar deportista: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/deportistas/<int:id_deportista>', methods=['GET'])
def obtenerDeportistaPorId(id_deportista):
    """
    Obtiene la información completa de un deportista por su ID.
    
    Incluye:
    - Datos personales (nombre, documento, tipo sanguíneo, ciudad, EPS)
    - Información deportiva (deporte, escuela, institución, categoría)
    - Diagnósticos médicos asociados
    
    Args:
        id_deportista: ID del deportista (parámetro en la URL)
        
    Returns:
        JSON con toda la información del deportista o error 404 si no existe
    """
    try:
        # Validar que el ID sea numérico y positivo
        if not isinstance(id_deportista, int) or id_deportista <= 0:
            return jsonify({
                'status': 'error',
                'message': 'El ID del deportista debe ser un número entero positivo'
            }), 400
        
        # Obtener información completa del deportista
        result = RegistroDeportistaService.obtener_informacion_completa_deportista(id_deportista)
        
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener deportista: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@deportistas_bp.route('/deportistas', methods=['GET'])
def get_lista_deportistas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = DeportistaService.listar_deportistas(page, per_page)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al listar deportistas: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/deportistas/<int:id_deportista>', methods=['PATCH', 'PUT'])
def actualizar_deportista(id_deportista):
    try:
        if not request.is_json:
            return jsonify({'success': False, 'message': 'El contenido debe ser JSON', 'status_code': 400}), 400
        datos = request.get_json()
        result = DeportistaService.actualizar_deportista(id_deportista, datos)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al actualizar deportista: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500


# ---- Rutas CATÁLOGOS de datos relacionados ----

@deportistas_bp.route('/catalogos/diagnosticos', methods=['GET'])
def catalogo_diagnosticos():
    """
    Obtiene todos los diagnósticos disponibles o filtrados por tipo de enfermedad.
    
    Query params:
        id_tipo_enfermedad (int, opcional): Filtra diagnósticos por tipo de enfermedad.
    """
    try:
        service = CatalogosService()
        
        # Obtener parámetro opcional de filtro
        id_tipo_enfermedad = request.args.get('id_tipo_enfermedad', type=int)
        
        result = service.obtener_diagnosticos(id_tipo_enfermedad=id_tipo_enfermedad)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener diagnósticos: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/tipos-enfermedad', methods=['GET'])
def catalogo_tipos_enfermedad():
    """
    Obtiene todos los tipos de enfermedad disponibles.
    
    Query params:
        incluir_diagnosticos (bool, opcional): Si es 'true', incluye los diagnósticos relacionados.
    """
    try:
        service = CatalogosService()
        
        # Obtener parámetro opcional para incluir diagnósticos
        incluir_diagnosticos = request.args.get('incluir_diagnosticos', 'false').lower() == 'true'
        
        result = service.obtener_tipos_enfermedad(incluir_diagnosticos=incluir_diagnosticos)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener tipos de enfermedad: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/grupos-sanguineos', methods=['GET'])
def catalogo_grupos_sanguineos():
    try:
        service = CatalogosService()
        result = service.obtener_grupos_sanguineos()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener grupos sanguíneos: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/ciudades-residencia', methods=['GET'])
def catalogo_ciudades_residencia():
    try:
        service = CatalogosService()
        result = service.obtener_ciudades_residencia()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener ciudades residencia: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/eps', methods=['GET'])
def catalogo_eps():
    try:
        service = CatalogosService()
        result = service.obtener_eps()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener eps: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/deportes', methods=['GET'])
def catalogo_deportes():
    try:
        service = CatalogosService()
        result = service.obtener_deportes()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener deportes: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/escuelas', methods=['GET'])
def catalogo_escuelas():
    try:
        service = CatalogosService()
        result = service.obtener_escuelas()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener escuelas: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/instituciones-registro', methods=['GET'])
def catalogo_instituciones_registro():
    try:
        service = CatalogosService()
        result = service.obtener_instituciones_registro()
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener instituciones de registro: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/catalogos/diagnosticos-por-tipo/<int:id_tipo_enfermedad>', methods=['GET'])
def catalogo_diagnosticos_por_tipo(id_tipo_enfermedad):
    """
    Obtiene diagnósticos filtrados por tipo de enfermedad.
    
    Este endpoint permite al frontend:
    1. Mostrar lista de tipos de enfermedad
    2. Cuando el usuario selecciona un tipo, cargar los diagnósticos relacionados
    3. El usuario selecciona el diagnóstico específico
    
    Args:
        id_tipo_enfermedad: ID del tipo de enfermedad
    """
    try:
        result = RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad(id_tipo_enfermedad)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al obtener diagnósticos por tipo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

# Notas:
# - La lógica de negocio y validaciones están separadas en src/services/deportista_service.py y src/services/catalogos_service.py
# - Esto hace el controlador sencillo, DRY y orientado a una sola responsabilidad.
# - Las URLs siguen convenciones RESTful y están organizadas por recurso.

