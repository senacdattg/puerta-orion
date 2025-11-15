"""
Rutas para gestión de deportistas.

Este archivo orquesta la definición de rutas y la delegación de lógica a los 
servicios del dominio de deportistas y catálogos. Cada módulo cumple con un 
propósito único siguiendo SRP, DRY, KISS, POO y Clean Code.

Principios aplicados:
- SRP: Cada función tiene una única responsabilidad
- DRY: Uso de constantes y utilidades reutilizables
- KISS: Código simple y directo
- POO: Uso de clases para construcción de respuestas
- Clean Code: Nombres descriptivos, funciones pequeñas, manejo de errores consistente
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import date
import traceback

from flask import Blueprint, request
from flask import Response

from src.services.deportista_service import DeportistaService
from src.services.registro_deportista_service import RegistroDeportistaService
from src.services.catalogos_service import CatalogosService
from src.utils.logger import obtener_registrador
from src.utils.http_responses import HttpResponseBuilder, handle_exception, JsonResponse
from src.utils.error_messages import (
    ERROR_INTERNO_SERVIDOR,
    ERROR_CONTENT_TYPE_JSON,
    ERROR_USUARIO_NO_AUTENTICADO,
    ERROR_DEPORTISTA_NO_ENCONTRADO,
    ERROR_ID_ENTERO_POSITIVO,
)
from src.middleware.auth_decorator import token_required, get_current_user
from src.utils.request_validators import obtener_json_requerido, RequestValidationError

deportistas_bp = Blueprint('deportistas', __name__, url_prefix='/api/deportistas')
logger = obtener_registrador('aplicacion')

# ============================================================================
# RUTAS PRINCIPALES DE DEPORTISTAS (CRUD)
# ============================================================================

@deportistas_bp.route('/', methods=['POST'])
def crear_deportista() -> JsonResponse:
    """
    Crea un nuevo deportista.
    
    POST /api/deportistas/
    
    Body JSON: Datos del deportista a crear.
    
    Returns:
        Respuesta con el deportista creado o error.
    """
    try:
        datos = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio='Los datos del deportista son requeridos'
        )
        
        result = DeportistaService.crear_deportista(datos)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al crear deportista"),
                message=result.get("message"),
                status_code=status_code
            )
            
    except RequestValidationError as e:
        return HttpResponseBuilder.bad_request(error=str(e))
    except Exception as e:
        return handle_exception(e, logger, "crear deportista")

@deportistas_bp.route('/registro-completo', methods=['POST'])
def registro_deportista_completo() -> JsonResponse:
    """
    Registra un deportista con información completa.
    
    POST /api/deportistas/registro-completo
    
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
    
    Returns:
        Respuesta con el deportista registrado o error.
    """
    try:
        datos = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio='Los datos del registro completo son requeridos'
        )
        
        result = RegistroDeportistaService.registrar_deportista_nuevo(datos)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al registrar deportista"),
                message=result.get("message"),
                status_code=status_code
            )
            
    except RequestValidationError as e:
        return HttpResponseBuilder.bad_request(error=str(e))
    except Exception as e:
        return handle_exception(e, logger, "registrar deportista completo")

@deportistas_bp.route('/registrar', methods=['POST'])
@token_required()
def registrar_deportista() -> JsonResponse:
    """
    Registra un deportista con cálculo automático de categoría (autenticado).
    
    POST /api/deportistas/registrar
    
    Este endpoint:
    - Calcula automáticamente la categoría basándose en la fecha de nacimiento
    - Valida que todos los IDs existan en sus respectivas tablas
    - Maneja la transacción completa con rollback en caso de error
    - Valida la coherencia entre tipo de enfermedad y diagnósticos
    - Usa el id_persona del usuario autenticado automáticamente
    
    Body JSON:
    {
        "datos_deportista": {
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
    
    Returns:
        Respuesta con el deportista registrado o error.
    """
    try:
        datos = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio='Los datos del registro son requeridos'
        )

        # Obtener id_persona del usuario autenticado (inyectado por el middleware)
        usuario_actual = get_current_user()
        if not usuario_actual or not usuario_actual.get('persona'):
            return HttpResponseBuilder.unauthorized(
                message='Usuario no autenticado o sin persona asociada'
            )

        id_persona = usuario_actual['persona'].get('id_persona')
        if not id_persona:
            return HttpResponseBuilder.unauthorized(
                message='No se pudo determinar la persona del usuario'
            )

        # Asegurar estructura base
        if 'datos_deportista' not in datos or datos['datos_deportista'] is None:
            datos['datos_deportista'] = {}

        # Inyectar id_persona automáticamente (no se requiere que el frontend lo envíe)
        datos['datos_deportista']['id_persona'] = id_persona

        result = RegistroDeportistaService.registrar_deportista_nuevo(datos)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False) or result.get("status") == "success":
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al registrar deportista"),
                message=result.get("message"),
                status_code=status_code
            )
            
    except RequestValidationError as e:
        return HttpResponseBuilder.bad_request(error=str(e))
    except Exception as e:
        return handle_exception(e, logger, "registrar deportista")

@deportistas_bp.route('/<int:id_deportista>', methods=['GET'])
def obtener_deportista_por_id(id_deportista: int) -> JsonResponse:
    """
    Obtiene la información completa de un deportista por su ID.

    GET /api/deportistas/<id_deportista>

    Incluye:
    - Datos personales (nombre, documento, tipo sanguíneo, ciudad, EPS)
    - Información deportiva (deporte, escuela, institución, categoría)
    - Diagnósticos médicos asociados

    Args:
        id_deportista: ID del deportista (parámetro en la URL)

    Returns:
        JSON con toda la información del deportista o error 404 si no existe
    """
    # Validar que el ID sea numérico y positivo
    if not isinstance(id_deportista, int) or id_deportista <= 0:
        return HttpResponseBuilder.bad_request(
            error=ERROR_ID_ENTERO_POSITIVO,
            message='El ID del deportista debe ser un número entero positivo'
        )

    try:
        # Obtener información completa del deportista
        result = RegistroDeportistaService.obtener_informacion_completa_deportista(id_deportista)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False) or result.get("status") == "success":
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        elif status_code == 404:
            return HttpResponseBuilder.not_found(
                error=ERROR_DEPORTISTA_NO_ENCONTRADO,
                message=f'No se encontró un deportista con ID {id_deportista}'
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener deportista"),
                message=result.get("message"),
                status_code=status_code
            )
            
    except Exception as e:
        logger.error(f"Error inesperado al obtener deportista: {str(e)}")
        logger.error(traceback.format_exc())
        return handle_exception(e, logger, "obtener deportista por ID")

@deportistas_bp.route('/', methods=['GET'])
def get_lista_deportistas() -> JsonResponse:
    """
    Obtiene la lista paginada de deportistas.
    
    GET /api/deportistas/?page=1&per_page=10
    
    Query params:
        page (int, opcional): Número de página (default: 1)
        per_page (int, opcional): Elementos por página (default: 10)
    
    Returns:
        Lista paginada de deportistas o error.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = DeportistaService.listar_deportistas(page, per_page)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al listar deportistas"),
                message=result.get("message"),
                status_code=status_code
            )
            
    except Exception as e:
        return handle_exception(e, logger, "listar deportistas")

@deportistas_bp.route('/<int:id_deportista>/acudientes', methods=['POST'])
@token_required()
def asociar_acudiente_deportista(id_deportista: int) -> JsonResponse:
    """
    Asocia un acudiente existente con un deportista.
    
    POST /api/deportistas/<id_deportista>/acudientes
    
    Permite que un acudiente ya registrado se asocie con un deportista adicional.
    Valida que:
    - El acudiente no tenga más de 3 deportistas asociados
    - El deportista no tenga más de 3 acudientes asociados
    - No exista ya esta relación
    
    Body JSON:
    {
        "id_parentesco": 1,                // OBLIGATORIO: ID del tipo de parentesco
        "es_responsable": false            // OBLIGATORIO: Si es responsable legal (bool)
    }
    
    Returns:
        Información de la relación creada o error.
    """
    try:
        datos = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio='Los datos de la relación son requeridos'
        )
        
        # Obtener usuario autenticado del contexto
        user = get_current_user()
        
        if not user:
            return HttpResponseBuilder.unauthorized(
                message='Usuario no encontrado en el contexto'
            )
        
        # Obtener datos del JSON
        id_parentesco = datos.get('id_parentesco')
        es_responsable = datos.get('es_responsable', False)
        
        # Validar que se proporcionen todos los datos requeridos
        if not id_parentesco:
            return HttpResponseBuilder.bad_request(
                error='Campo requerido',
                message='Se requiere id_parentesco'
            )
        
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
            return HttpResponseBuilder.bad_request(
                error='Datos incompletos',
                message='No se encontró información de persona para el usuario'
            )
        
        acudiente = Acudiente.query.filter_by(id_persona=id_persona).first()
        if not acudiente:
            return HttpResponseBuilder.bad_request(
                error='Perfil incompleto',
                message='El usuario no está registrado como acudiente. Debe completar su perfil primero.'
            )
        
        # Validar que el deportista existe
        deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
        if not deportista:
            return HttpResponseBuilder.not_found(
                error=ERROR_DEPORTISTA_NO_ENCONTRADO,
                message=f'No se encontró un deportista con ID {id_deportista}'
            )
        
        # Validar que el deportista no se esté acudiendo a sí mismo
        if deportista.id_persona == id_persona:
            return HttpResponseBuilder.bad_request(
                error='Validación fallida',
                message='Un deportista no puede acudirse a sí mismo'
            )
        
        # Validar que el parentesco existe
        parentesco = Parentesco.query.filter_by(id_parentesco=int(id_parentesco)).first()
        if not parentesco:
            return HttpResponseBuilder.not_found(
                error='Recurso no encontrado',
                message=f'No se encontró un parentesco con ID {id_parentesco}'
            )
        
        # Validar que no exista ya esta relación
        relacion_existente = DeportistaAcudiente.query.filter_by(
            id_deportista=id_deportista,
            id_acudiente=acudiente.id_acudiente
        ).first()
        
        if relacion_existente:
            return HttpResponseBuilder.bad_request(
                error='Relación duplicada',
                message='Ya existe una relación entre este acudiente y este deportista'
            )
        
        # Validar que el acudiente no tenga más de 3 deportistas asociados
        deportistas_acudiente = DeportistaAcudiente.query.filter_by(
            id_acudiente=acudiente.id_acudiente
        ).count()
        
        if deportistas_acudiente >= 3:
            return HttpResponseBuilder.bad_request(
                error='Límite excedido',
                message=f'Un acudiente solo puede estar asociado a máximo 3 deportistas. '
                        f'Este acudiente ya tiene {deportistas_acudiente} deportista(s) asociado(s).'
            )
        
        # Validar que el deportista no tenga más de 3 acudientes asociados
        acudientes_deportista = DeportistaAcudiente.query.filter_by(
            id_deportista=id_deportista
        ).count()
        
        if acudientes_deportista >= 3:
            return HttpResponseBuilder.bad_request(
                error='Límite excedido',
                message=f'Un deportista solo puede estar asociado a máximo 3 acudientes. '
                        f'Este deportista ya tiene {acudientes_deportista} acudiente(s) asociado(s).'
            )
        
        # Crear la relación DeportistaAcudiente
        deportista_acudiente = DeportistaAcudiente(
            id_deportista=id_deportista,
            id_acudiente=acudiente.id_acudiente,
            id_parentesco=int(id_parentesco),
            es_responsable=bool(es_responsable),
            fecha_registro=date.today()
        )
        
        db.session.add(deportista_acudiente)
        db.session.commit()
        
        logger.info(f'Relación creada: Acudiente {acudiente.id_acudiente} - Deportista {id_deportista}')
        
        return HttpResponseBuilder.created(
            data={
                'id_deportista_acudiente': deportista_acudiente.id_deportista_acudiente,
                'id_deportista': deportista_acudiente.id_deportista,
                'id_acudiente': deportista_acudiente.id_acudiente,
                'id_parentesco': deportista_acudiente.id_parentesco,
                'es_responsable': deportista_acudiente.es_responsable,
                'fecha_registro': deportista_acudiente.fecha_registro.isoformat() if deportista_acudiente.fecha_registro else None
            },
            message='Deportista asociado exitosamente al acudiente'
        )
        
    except RequestValidationError as e:
        return HttpResponseBuilder.bad_request(error=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al asociar acudiente con deportista: {str(e)}")
        logger.error(traceback.format_exc())
        return handle_exception(e, logger, "asociar acudiente con deportista")


@deportistas_bp.route('/<int:id_deportista>/acudientes', methods=['GET'])
@token_required()
def obtener_acudientes_por_deportista(id_deportista: int) -> JsonResponse:
    """
    Obtiene todos los acudientes asociados a un deportista específico.
    
    GET /api/deportistas/<id_deportista>/acudientes
    
    Args:
        id_deportista: ID del deportista
        
    Returns:
        Lista de acudientes asociados al deportista o error.
    """
    try:
        from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
        from ..models.acudientes.acudiente import Acudiente
        from ..models.deportistas.deportista import Deportista
        
        logger.info(f"Buscando acudientes para deportista ID: {id_deportista}")
        
        # Validar que el deportista existe
        deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
        if not deportista:
            return HttpResponseBuilder.not_found(
                error=ERROR_DEPORTISTA_NO_ENCONTRADO,
                message='El deportista especificado no existe'
            )
        
        # Obtener todas las relaciones deportista-acudiente para este deportista
        relaciones = DeportistaAcudiente.query.filter_by(id_deportista=id_deportista).all()
        logger.info(f"Relaciones encontradas: {len(relaciones)}")
        
        if not relaciones:
            return HttpResponseBuilder.success(
                data=[],
                message='No se encontraron acudientes asociados a este deportista'
            )
        
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
        
        logger.info(f"Total acudientes procesados: {len(acudientes_data)}")
        
        return HttpResponseBuilder.success(
            data=acudientes_data,
            message=f'Se encontraron {len(acudientes_data)} acudiente(s) asociado(s)'
        )
        
    except Exception as e:
        logger.error(f"Error inesperado al obtener acudientes por deportista: {str(e)}")
        logger.error(traceback.format_exc())
        return handle_exception(e, logger, "obtener acudientes por deportista")

DEFAUL_CATEGORY_LABEL: str = 'Sin categoría'
DEFAULT_PARENTESCO_LABEL: str = 'No especificado'

def _is_valid_acudiente_id(id_acudiente: int) -> bool:
    """Valida si el id_acudiente es un entero positivo.

    Args:
        id_acudiente (int): ID a validar.

    Returns:
        bool: True si es válido, False en caso contrario.
    """
    return isinstance(id_acudiente, int) and id_acudiente > 0

def _calculate_age(fecha_nacimiento: Any) -> Optional[int]:
    """Calcula la edad dado una fecha de nacimiento o año.

    Args:
        fecha_nacimiento (Any): Fecha de nacimiento (datetime.date o int (año)).

    Returns:
        Optional[int]: Edad, None si no es posible calcularla.
    """
    if not fecha_nacimiento:
        return None
    today = date.today()
    if isinstance(fecha_nacimiento, date):
        return today.year - fecha_nacimiento.year - (
            (today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
        )
    if isinstance(fecha_nacimiento, int):
        return today.year - fecha_nacimiento
    return None

def _serialize_deportista(
    deportista: Any, relacion: Any
) -> Dict[str, Any]:
    """Serializa la información de un deportista junto a la relación.

    Args:
        deportista (Any): Instancia del modelo Deportista.
        relacion (Any): Instancia de la relación DeportistaAcudiente.

    Returns:
        Dict[str, Any]: Diccionario serializado.
    """
    edad = _calculate_age(deportista.fecha_nacimiento)
    return {
        "id": deportista.id_deportista,
        "nombre_completo": deportista.persona.nombre_completo,
        "documento": deportista.persona.documento,
        "correo_electronico": deportista.persona.correo_electronico,
        "telefono": deportista.persona.telefono,
        "categoria": deportista.categoria.nombre_categoria if deportista.categoria else DEFAUL_CATEGORY_LABEL,
        "edad": edad,
        "es_responsable": getattr(relacion, "es_responsable", False) or False,
        "parentesco": relacion.parentesco.nombre if getattr(relacion, "parentesco", None) else DEFAULT_PARENTESCO_LABEL,
    }

@deportistas_bp.route('/acudientes/<int:id_acudiente>/deportistas', methods=['GET'])
@token_required()
def obtener_deportistas_por_acudiente(id_acudiente: int) -> JsonResponse:
    """
    Obtiene todos los deportistas asociados a un acudiente específico.
    
    GET /api/deportistas/acudientes/<id_acudiente>/deportistas

    Args:
        id_acudiente (int): ID del acudiente.

    Returns:
        Lista de deportistas asociados al acudiente o error.
    """
    from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
    from ..models.deportistas.deportista import Deportista

    try:
        logger.info(f"Buscando deportistas para acudiente ID: {id_acudiente}")

        # Validación de ID de acudiente
        if not _is_valid_acudiente_id(id_acudiente):
            logger.warning(f"ID de acudiente inválido: {id_acudiente}")
            return HttpResponseBuilder.bad_request(
                error=ERROR_ID_ENTERO_POSITIVO,
                message="El ID del acudiente debe ser un número entero positivo"
            )

        relaciones = DeportistaAcudiente.query.filter_by(id_acudiente=id_acudiente).all()
        logger.info(f"Relaciones encontradas: {len(relaciones)}")

        if not relaciones:
            logger.warning(f"No se encontraron relaciones para acudiente {id_acudiente}")
            return HttpResponseBuilder.success(
                data=[],
                message="No se encontraron deportistas asociados a este acudiente"
            )

        deportistas_data: List[Dict[str, Any]] = []
        for relacion in relaciones:
            logger.info(f"Procesando relación - Deportista ID: {relacion.id_deportista}, Acudiente ID: {relacion.id_acudiente}")
            deportista = Deportista.query.filter_by(id_deportista=relacion.id_deportista).first()
            if not deportista:
                logger.warning(f"Deportista {relacion.id_deportista} no encontrado")
                continue
            if not getattr(deportista, "persona", None):
                logger.warning(f"Deportista {relacion.id_deportista} no tiene persona asociada")
                continue
            deportista_dict = _serialize_deportista(deportista, relacion)
            logger.info(f"Datos del deportista: {deportista_dict}")
            deportistas_data.append(deportista_dict)

        logger.info(f"Total deportistas procesados: {len(deportistas_data)}")
        return HttpResponseBuilder.success(
            data=deportistas_data,
            message=f"Se encontraron {len(deportistas_data)} deportista(s) asociado(s)"
        )

    except Exception as exc:
        logger.error(f"Error inesperado al obtener deportistas por acudiente: {str(exc)}")
        logger.error(traceback.format_exc())
        return handle_exception(exc, logger, "obtener deportistas por acudiente")

@deportistas_bp.route('/<int:id_deportista>', methods=['PATCH', 'PUT'])
@token_required()
def actualizar_deportista(id_deportista: int) -> JsonResponse:
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
        datos = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio='Los datos de actualización son requeridos'
        )
        
        # Obtener usuario autenticado
        usuario_actual = get_current_user()
        
        if not usuario_actual:
            return HttpResponseBuilder.unauthorized(
                message='Usuario no autenticado'
            )
        
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
        
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al actualizar deportista"),
                message=result.get("message"),
                status_code=status_code
            )
        
    except RequestValidationError as e:
        return HttpResponseBuilder.bad_request(error=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al actualizar deportista: {str(e)}")
        logger.error(traceback.format_exc())
        return handle_exception(e, logger, "actualizar deportista")


# ============================================================================
# RUTAS DE CATÁLOGOS
# ============================================================================

@deportistas_bp.route('/catalogos/diagnosticos', methods=['GET'])
def catalogo_diagnosticos() -> JsonResponse:
    """
    Obtiene todos los diagnósticos disponibles o filtrados por tipo de enfermedad.
    
    GET /api/deportistas/catalogos/diagnosticos?id_tipo_enfermedad=1
    
    Query params:
        id_tipo_enfermedad (int, opcional): Filtra diagnósticos por tipo de enfermedad.
    
    Returns:
        Lista de diagnósticos o error.
    """
    try:
        service = CatalogosService()
        
        # Obtener parámetro opcional de filtro
        id_tipo_enfermedad = request.args.get('id_tipo_enfermedad', type=int)
        
        result = service.obtener_diagnosticos(id_tipo_enfermedad=id_tipo_enfermedad)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener diagnósticos"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener diagnósticos")

@deportistas_bp.route('/catalogos/tipos-enfermedad', methods=['GET'])
def catalogo_tipos_enfermedad() -> JsonResponse:
    """
    Obtiene todos los tipos de enfermedad disponibles.
    
    GET /api/deportistas/catalogos/tipos-enfermedad?incluir_diagnosticos=true
    
    Query params:
        incluir_diagnosticos (bool, opcional): Si es 'true', incluye los diagnósticos relacionados.
    
    Returns:
        Lista de tipos de enfermedad o error.
    """
    try:
        service = CatalogosService()
        
        # Obtener parámetro opcional para incluir diagnósticos
        incluir_diagnosticos = request.args.get('incluir_diagnosticos', 'false').lower() == 'true'
        
        result = service.obtener_tipos_enfermedad(incluir_diagnosticos=incluir_diagnosticos)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener tipos de enfermedad"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener tipos de enfermedad")

@deportistas_bp.route('/catalogos/grupos-sanguineos', methods=['GET'])
def catalogo_grupos_sanguineos() -> JsonResponse:
    """
    Obtiene todos los grupos sanguíneos disponibles.
    
    GET /api/deportistas/catalogos/grupos-sanguineos
    
    Returns:
        Lista de grupos sanguíneos o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_grupos_sanguineos()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener grupos sanguíneos"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener grupos sanguíneos")

@deportistas_bp.route('/catalogos/ciudades-residencia', methods=['GET'])
def catalogo_ciudades_residencia() -> JsonResponse:
    """
    Obtiene todas las ciudades de residencia disponibles.
    
    GET /api/deportistas/catalogos/ciudades-residencia
    
    Returns:
        Lista de ciudades de residencia o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_ciudades_residencia()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener ciudades de residencia"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener ciudades de residencia")

@deportistas_bp.route('/catalogos/eps', methods=['GET'])
def catalogo_eps() -> JsonResponse:
    """
    Obtiene todas las EPS disponibles.
    
    GET /api/deportistas/catalogos/eps
    
    Returns:
        Lista de EPS o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_eps()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener EPS"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener EPS")

@deportistas_bp.route('/catalogos/deportes', methods=['GET'])
def catalogo_deportes() -> JsonResponse:
    """
    Obtiene todos los deportes disponibles.
    
    GET /api/deportistas/catalogos/deportes
    
    Returns:
        Lista de deportes o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_deportes()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener deportes"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener deportes")

@deportistas_bp.route('/catalogos/escuelas', methods=['GET'])
def catalogo_escuelas() -> JsonResponse:
    """
    Obtiene todas las escuelas disponibles.
    
    GET /api/deportistas/catalogos/escuelas
    
    Returns:
        Lista de escuelas o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_escuelas()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener escuelas"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener escuelas")

@deportistas_bp.route('/catalogos/instituciones-registro', methods=['GET'])
def catalogo_instituciones_registro() -> JsonResponse:
    """
    Obtiene todas las instituciones de registro disponibles.
    
    GET /api/deportistas/catalogos/instituciones-registro
    
    Returns:
        Lista de instituciones de registro o error.
    """
    try:
        service = CatalogosService()
        result = service.obtener_instituciones_registro()
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener instituciones de registro"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener instituciones de registro")

@deportistas_bp.route('/catalogos/diagnosticos-por-tipo/<int:id_tipo_enfermedad>', methods=['GET'])
def catalogo_diagnosticos_por_tipo(id_tipo_enfermedad: int) -> JsonResponse:
    """
    Obtiene diagnósticos filtrados por tipo de enfermedad.
    
    GET /api/deportistas/catalogos/diagnosticos-por-tipo/<id_tipo_enfermedad>
    
    Este endpoint permite al frontend:
    1. Mostrar lista de tipos de enfermedad
    2. Cuando el usuario selecciona un tipo, cargar los diagnósticos relacionados
    3. El usuario selecciona el diagnóstico específico
    
    Args:
        id_tipo_enfermedad: ID del tipo de enfermedad
    
    Returns:
        Lista de diagnósticos del tipo especificado o error.
    """
    try:
        result = RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad(id_tipo_enfermedad)
        status_code = result.get("status_code", 200)
        
        if result.get("success", False):
            return HttpResponseBuilder.success(
                data=result.get("data"),
                message=result.get("message"),
                status_code=status_code
            )
        else:
            return HttpResponseBuilder.error(
                error=result.get("error", "Error al obtener diagnósticos por tipo"),
                message=result.get("message"),
                status_code=status_code
            )
    except Exception as e:
        return handle_exception(e, logger, "obtener diagnósticos por tipo")