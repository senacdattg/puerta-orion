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

@deportistas_bp.route('/', methods=['POST'])
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

@deportistas_bp.route('/registro-completo', methods=['POST'])
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

@deportistas_bp.route('/registrar', methods=['POST'])
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

@deportistas_bp.route('/<int:id_deportista>', methods=['GET'])
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

@deportistas_bp.route('/', methods=['GET'])
def get_lista_deportistas():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = DeportistaService.listar_deportistas(page, per_page)
        return jsonify(result), result.get("status_code", 200)
    except Exception as e:
        logger.error(f"Error inesperado al listar deportistas: {str(e)}")
        return jsonify({'success': False, 'message': 'Error interno del servidor', 'status_code': 500}), 500

@deportistas_bp.route('/asociar-acudiente', methods=['POST'])
@token_required()
def asociar_acudiente_deportista():
    """
    Endpoint para asociar un acudiente existente con un deportista.
    
    Permite que un acudiente ya registrado se asocie con un deportista adicional.
    Valida que:
    - El acudiente no tenga más de 3 deportistas asociados
    - El deportista no tenga más de 3 acudientes asociados
    - No exista ya esta relación
    
    Headers requeridos:
    Authorization: Bearer <token>
    
    Body JSON requerido:
    {
        "id_deportista": 123,              // OBLIGATORIO: ID del deportista
        "id_parentesco": 1,                // OBLIGATORIO: ID del tipo de parentesco
        "es_responsable": false            // OBLIGATORIO: Si es responsable legal (bool)
    }
    
    Returns:
        JSON: Información de la relación creada
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json',
                'status_code': 400
            }), 400
        
        # Obtener usuario autenticado del contexto
        user = get_current_user()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado en el contexto',
                'status_code': 401
            }), 401
        
        # Obtener datos del JSON
        data = request.get_json()
        id_deportista = data.get('id_deportista')
        id_parentesco = data.get('id_parentesco')
        es_responsable = data.get('es_responsable', False)
        
        # Validar que se proporcionen todos los datos requeridos
        if not id_deportista or not id_parentesco:
            return jsonify({
                'success': False,
                'error': 'Se requieren id_deportista e id_parentesco',
                'status_code': 400
            }), 400
        
        # Importar modelos necesarios
        from src.models.acudientes.acudiente import Acudiente
        from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
        from src.models.deportistas.deportista import Deportista
        from src.models.acudientes.parentesco import Parentesco
        from src.models.base import db
        from datetime import date
        
        # Obtener el acudiente del usuario autenticado
        id_persona = user.get('persona', {}).get('id_persona')
        if not id_persona:
            return jsonify({
                'success': False,
                'error': 'No se encontró información de persona para el usuario',
                'status_code': 400
            }), 400
        
        acudiente = Acudiente.query.filter_by(id_persona=id_persona).first()
        if not acudiente:
            return jsonify({
                'success': False,
                'error': 'El usuario no está registrado como acudiente. Debe completar su perfil primero.',
                'status_code': 400
            }), 400
        
        # Validar que el deportista existe
        deportista = Deportista.query.filter_by(id_deportista=int(id_deportista)).first()
        if not deportista:
            return jsonify({
                'success': False,
                'error': f'El deportista con ID {id_deportista} no existe',
                'status_code': 404
            }), 404
        
        # Validar que el deportista no se esté acudiendo a sí mismo
        if deportista.id_persona == id_persona:
            return jsonify({
                'success': False,
                'error': 'Un deportista no puede acudirse a sí mismo',
                'status_code': 400
            }), 400
        
        # Validar que el parentesco existe
        parentesco = Parentesco.query.filter_by(id_parentesco=int(id_parentesco)).first()
        if not parentesco:
            return jsonify({
                'success': False,
                'error': f'El parentesco con ID {id_parentesco} no existe',
                'status_code': 404
            }), 404
        
        # Validar que no exista ya esta relación
        relacion_existente = DeportistaAcudiente.query.filter_by(
            id_deportista=int(id_deportista),
            id_acudiente=acudiente.id_acudiente
        ).first()
        
        if relacion_existente:
            return jsonify({
                'success': False,
                'error': 'Ya existe una relación entre este acudiente y este deportista',
                'status_code': 400
            }), 400
        
        # Validar que el acudiente no tenga más de 3 deportistas asociados
        deportistas_acudiente = DeportistaAcudiente.query.filter_by(
            id_acudiente=acudiente.id_acudiente
        ).count()
        
        if deportistas_acudiente >= 3:
            return jsonify({
                'success': False,
                'error': f'Un acudiente solo puede estar asociado a máximo 3 deportistas. '
                        f'Este acudiente ya tiene {deportistas_acudiente} deportista(s) asociado(s).',
                'status_code': 400
            }), 400
        
        # Validar que el deportista no tenga más de 3 acudientes asociados
        acudientes_deportista = DeportistaAcudiente.query.filter_by(
            id_deportista=int(id_deportista)
        ).count()
        
        if acudientes_deportista >= 3:
            return jsonify({
                'success': False,
                'error': f'Un deportista solo puede estar asociado a máximo 3 acudientes. '
                        f'Este deportista ya tiene {acudientes_deportista} acudiente(s) asociado(s).',
                'status_code': 400
            }), 400
        
        # Crear la relación DeportistaAcudiente
        deportista_acudiente = DeportistaAcudiente(
            id_deportista=int(id_deportista),
            id_acudiente=acudiente.id_acudiente,
            id_parentesco=int(id_parentesco),
            es_responsable=bool(es_responsable),
            fecha_registro=date.today()
        )
        
        db.session.add(deportista_acudiente)
        db.session.commit()
        
        logger.info(f'Relación creada: Acudiente {acudiente.id_acudiente} - Deportista {id_deportista}')
        
        return jsonify({
            'success': True,
            'message': 'Deportista asociado exitosamente al acudiente',
            'data': {
                'id_deportista_acudiente': deportista_acudiente.id_deportista_acudiente,
                'id_deportista': deportista_acudiente.id_deportista,
                'id_acudiente': deportista_acudiente.id_acudiente,
                'id_parentesco': deportista_acudiente.id_parentesco,
                'es_responsable': deportista_acudiente.es_responsable,
                'fecha_registro': deportista_acudiente.fecha_registro.isoformat() if deportista_acudiente.fecha_registro else None
            },
            'status_code': 201
        }), 201
        
    except Exception as e:
        logger.error(f"Error inesperado al asociar acudiente con deportista: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'status_code': 500
        }), 500


@deportistas_bp.route('/<int:id_deportista>/acudientes', methods=['GET'])
@token_required()
def obtener_acudientes_por_deportista(id_deportista):
    """
    Obtiene todos los acudientes asociados a un deportista específico.
    
    Args:
        id_deportista: ID del deportista
        
    Returns:
        JSON con lista de acudientes asociados al deportista
    """
    try:
        from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
        from ..models.acudientes.acudiente import Acudiente
        from ..models.deportistas.deportista import Deportista
        from datetime import date
        
        logger.info(f"🔍 Buscando acudientes para deportista ID: {id_deportista}")
        
        # Validar que el deportista existe
        deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
        if not deportista:
            return jsonify({
                'success': False,
                'message': 'El deportista especificado no existe',
                'data': []
            }), 404
        
        # Obtener todas las relaciones deportista-acudiente para este deportista
        relaciones = DeportistaAcudiente.query.filter_by(id_deportista=id_deportista).all()
        logger.info(f"📊 Relaciones encontradas: {len(relaciones)}")
        
        if not relaciones:
            return jsonify({
                'success': True,
                'message': 'No se encontraron acudientes asociados a este deportista',
                'data': []
            }), 200
        
        # Construir lista de acudientes con información completa
        acudientes_data = []
        for relacion in relaciones:
            acudiente = Acudiente.query.filter_by(id_acudiente=relacion.id_acudiente).first()
            
            if not acudiente or not acudiente.persona:
                continue
            
            acudiente_dict = {
                'id_acudiente': acudiente.id_acudiente,
                'nombre_completo': acudiente.persona.nombre_completo,
                'documento': acudiente.persona.documento,
                'correo_electronico': acudiente.persona.correo_electronico,
                'telefono': acudiente.persona.telefono,
                'parentesco': relacion.parentesco.nombre if relacion.parentesco else 'No especificado',
                'parentesco_nombre': relacion.parentesco.nombre if relacion.parentesco else None,
                'es_responsable': relacion.es_responsable if relacion.es_responsable is not None else False,
                'persona': {
                    'id_persona': acudiente.persona.id_persona,
                    'nombre_completo': acudiente.persona.nombre_completo,
                    'documento': acudiente.persona.documento,
                    'correo_electronico': acudiente.persona.correo_electronico,
                    'telefono': acudiente.persona.telefono
                }
            }
            acudientes_data.append(acudiente_dict)
        
        logger.info(f"✅ Total acudientes procesados: {len(acudientes_data)}")
        
        return jsonify({
            'success': True,
            'message': f'Se encontraron {len(acudientes_data)} acudiente(s) asociado(s)',
            'data': acudientes_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener acudientes por deportista: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'data': []
        }), 500

@deportistas_bp.route('/acudiente/<int:id_acudiente>', methods=['GET'])
@token_required()
def obtener_deportistas_por_acudiente(id_acudiente):
    """
    Obtiene todos los deportistas asociados a un acudiente específico.
    
    Args:
        id_acudiente: ID del acudiente
        
    Returns:
        JSON con lista de deportistas asociados al acudiente
    """
    try:
        from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
        from ..models.deportistas.deportista import Deportista
        from ..models.personas.persona import Persona
        from ..models.categorias.categoria import Categoria
        from datetime import date
        
        logger.info(f"🔍 Buscando deportistas para acudiente ID: {id_acudiente}")
        
        # Validar que el ID sea positivo
        if not isinstance(id_acudiente, int) or id_acudiente <= 0:
            logger.warning(f"⚠️ ID de acudiente inválido: {id_acudiente}")
            return jsonify({
                'success': False,
                'message': 'El ID del acudiente debe ser un número entero positivo',
                'data': []
            }), 400
        
        # Obtener todas las relaciones deportista-acudiente para este acudiente
        relaciones = DeportistaAcudiente.query.filter_by(id_acudiente=id_acudiente).all()
        logger.info(f"📊 Relaciones encontradas: {len(relaciones)}")
        
        if not relaciones:
            logger.warning(f"⚠️ No se encontraron relaciones para acudiente {id_acudiente}")
            return jsonify({
                'success': True,
                'message': 'No se encontraron deportistas asociados a este acudiente',
                'data': []
            }), 200
        
        # Construir lista de deportistas con información completa
        deportistas_data = []
        for relacion in relaciones:
            logger.info(f"🔍 Procesando relación - Deportista ID: {relacion.id_deportista}, Acudiente ID: {relacion.id_acudiente}")
            
            deportista = Deportista.query.filter_by(id_deportista=relacion.id_deportista).first()
            
            if not deportista:
                logger.warning(f"⚠️ Deportista {relacion.id_deportista} no encontrado")
                continue
            
            if not deportista.persona:
                logger.warning(f"⚠️ Deportista {relacion.id_deportista} no tiene persona asociada")
                continue
            
            logger.info(f"✅ Deportista encontrado: {deportista.persona.nombre_completo}")
            
            # Calcular edad
            edad = None
            if deportista.fecha_nacimiento:
                hoy = date.today()
                # Manejar tanto fecha completa como año solo
                if isinstance(deportista.fecha_nacimiento, date):
                    edad = hoy.year - deportista.fecha_nacimiento.year - ((hoy.month, hoy.day) < (deportista.fecha_nacimiento.month, deportista.fecha_nacimiento.day))
                elif isinstance(deportista.fecha_nacimiento, int):
                    # Compatibilidad con años antiguos
                    edad = hoy.year - deportista.fecha_nacimiento
            
            deportista_dict = {
                'id': deportista.id_deportista,
                'nombre_completo': deportista.persona.nombre_completo,
                'documento': deportista.persona.documento,
                'correo_electronico': deportista.persona.correo_electronico,
                'telefono': deportista.persona.telefono,
                'categoria': deportista.categoria.nombre_categoria if deportista.categoria else 'Sin categoría',
                'edad': edad,
                'es_responsable': relacion.es_responsable if relacion.es_responsable is not None else False,
                'parentesco': relacion.parentesco.nombre if relacion.parentesco else 'No especificado'
            }
            logger.info(f"📝 Datos del deportista: {deportista_dict}")
            deportistas_data.append(deportista_dict)
        
        logger.info(f"✅ Total deportistas procesados: {len(deportistas_data)}")
        
        return jsonify({
            'success': True,
            'message': f'Se encontraron {len(deportistas_data)} deportista(s) asociado(s)',
            'data': deportistas_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener deportistas por acudiente: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'data': []
        }), 500

@deportistas_bp.route('/<int:id_deportista>', methods=['PATCH', 'PUT'])
@token_required()
def actualizar_deportista(id_deportista):
    """
    Endpoint para actualizar un deportista.
    
    Permite actualizar completamente un deportista con todos sus campos relacionados.
    Puede actualizar SOLO datos_deportista, SOLO datos_informacion_deportiva, o ambos.
    
    NOTA: Los campos de persona se actualizan a través del endpoint de personas: PUT /personas/<id_persona>
    
    Body JSON estructurado (todos los campos son opcionales):
    {
        "datos_deportista": {
            "peso": 65.5,
            "altura": 1.75,
            "fecha_ingreso": "2024-01-15",
            "fecha_nacimiento": "2010-05-20",
            "id_categoria": 1,
            "id_tipo_sanguineo": 2,
            "id_ciudad_recidencia": 1,
            "id_eps": 3
        },
        "datos_informacion_deportiva": {
            "practica_otro_deporte": true,
            "participa_escuela": true,
            "recomendacion_medica": false,
            "descripcion_recomendacion": "Ninguna",
            "id_escuela": 5,
            "id_deporte": 8,
            "id_institucion_registro": 2
        }
    }
    
    Campos disponibles en datos_deportista:
    - peso (float): Peso en kilogramos
    - altura (float): Altura en metros
    - fecha_ingreso (string): Fecha de ingreso (formato: YYYY-MM-DD)
    - fecha_nacimiento (string): Fecha de nacimiento (formato: YYYY-MM-DD)
    - id_categoria (int): ID de la categoría deportiva
    - id_tipo_sanguineo (int): ID del grupo sanguíneo
    - id_ciudad_recidencia (int): ID de la ciudad de residencia
    - id_eps (int): ID de la EPS
    
    Campos disponibles en datos_informacion_deportiva:
    - practica_otro_deporte (bool): Si practica otro deporte
    - participa_escuela (bool): Si participa en una escuela deportiva
    - recomendacion_medica (bool): Si tiene recomendaciones médicas
    - descripcion_recomendacion (string): Descripción de recomendaciones médicas
    - id_escuela (int): ID de la escuela deportiva
    - id_deporte (int): ID del deporte que practica
    - id_institucion_registro (int): ID de la institución de registro
    
    NOTA: Si se usa PATCH, solo actualiza los campos proporcionados (actualización parcial).
          Si se usa PUT, actualiza todos los campos proporcionados (actualización completa).
          Ambos métodos aceptan la misma estructura JSON.
    
    Returns:
        JSON: Deportista actualizado con toda su información relacionada
    """
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'El contenido debe ser JSON',
                'status_code': 400
            }), 400
        
        datos = request.get_json()
        
        # Obtener usuario autenticado
        usuario_actual = get_current_user()
        
        if not usuario_actual:
            return jsonify({
                'success': False,
                'message': 'Usuario no autenticado',
                'status_code': 401
            }), 401
        
        # Extraer secciones de datos (todas opcionales)
        datos_deportista = datos.get('datos_deportista')
        datos_informacion_deportiva = datos.get('datos_informacion_deportiva')
        tipo_enfermedad = datos.get('tipo_enfermedad')
        diagnosticos = datos.get('diagnostico', datos.get('diagnosticos', None))
        
        # Si no hay ninguna sección, intentar actualización parcial (compatibilidad con endpoint anterior)
        if not datos_deportista and not datos_informacion_deportiva and tipo_enfermedad is None and diagnosticos is None:
            # Usar método antiguo para mantener compatibilidad
            result = DeportistaService.actualizar_deportista(id_deportista, datos)
        else:
            # Usar método completo (deportista, información deportiva y diagnósticos)
            result = DeportistaService.actualizar_deportista_completo(
                id_deportista=id_deportista,
                datos_deportista=datos_deportista,
                datos_informacion_deportiva=datos_informacion_deportiva,
                usuario_actual=usuario_actual,
                tipo_enfermedad=tipo_enfermedad,
                diagnosticos=diagnosticos
            )
        
        return jsonify(result), result.get("status_code", 200)
        
    except Exception as e:
        logger.error(f"Error inesperado al actualizar deportista: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'status_code': 500
        }), 500


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

