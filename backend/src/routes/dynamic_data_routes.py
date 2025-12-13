"""
Rutas para administración de datos dinámicos utilizados en catálogos del sistema.

Responsabilidad:
- Listar, crear, actualizar y eliminar registros parametrizables (EPS, roles, etc.).
- Aplicar validaciones específicas por tipo de dato manteniendo mensajes existentes.

El módulo respeta principios SOLID, DRY y PEP8.
"""

import re
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from flask import Blueprint, Flask, Response, jsonify, request
from sqlalchemy.exc import IntegrityError

from ..models import (
    CiudadResidencia,
    Deporte,
    EPS,
    Escuela,
    InstitucionRegistro,
    Parentesco,
    Sexo,
    TipoDocumento,
    TipoEnfermedad,
)
from ..models.base import db
from ..models.eventos.tipo_evento import TipoEvento
from ..models.pagos.metodo_pago import MetodoPago
from ..models.roles_y_permisos.rol import Rol
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido
from ..utils.validations import ValidationError, normalize_upper, sanitize_free_text, validate_name

JsonResponse = Tuple[Response, int]
ModelType = Type[Any]
TopicHandler = Callable[[Any, Dict[str, Any], bool], None]

dynamic_data_bp = Blueprint('dynamic_data', __name__, url_prefix='')
logger = obtener_registrador('aplicacion')

CONTENT_TYPE_ERROR = 'Content-Type debe ser application/json'
DATA_REQUIRED_ERROR = 'No se proporcionaron datos'
ERROR_CAMPO_REQUERIDO = 'Campo requerido: {campo}'
ERROR_REGISTRO_NO_ENCONTRADO = 'Registro con ID {registro_id} no encontrado'
ERROR_DUPLICADO = 'Ya existe un registro con {campo}: {valor}'
ERROR_DUPLICADO_OTRO = 'Ya existe otro registro con {campo}: {valor}'
ERROR_ELIMINAR_REFERENCIAS = (
    'No se puede eliminar el registro porque está siendo utilizado por otros elementos.'
)

TEMA_MODELOS = {
    'parentesco': Parentesco,
    'eps': EPS,
    'escuela': Escuela,
    'deporte': Deporte,
    'ciudad-residencia': CiudadResidencia,
    'institucion-registro': InstitucionRegistro,
    'tipo-evento': TipoEvento,
    'tipo-enfermedad': TipoEnfermedad,
    'roles': Rol,
    'metodo-pago': MetodoPago,
    'tipo-documento': TipoDocumento,
    'sexo': Sexo,
}

TEMA_CAMPOS = {
    'parentesco': 'nombre',
    'eps': 'nombre_eps',
    'escuela': 'nombre',
    'deporte': 'nombre',
    'ciudad-residencia': 'nombre_ciudad',
    'institucion-registro': 'nombre_institucion',
    'tipo-evento': 'nombre',
    'tipo-enfermedad': 'nombre',
    'roles': 'nombre_rol',
    'metodo-pago': 'nombre_metodo',
    'tipo-documento': 'nombre_documento',
    'sexo': 'nombre',
}

STRICT_NAME_TOPICS = {
    'tipo-documento',
    'sexo',
    'parentesco',
    'metodo-pago',
    'deporte',
    'escuela',
    'tipo-evento',
    'tipo-enfermedad',
    'roles',
}

FREE_TEXT_TOPICS = {
    'eps',
    'ciudad-residencia',
    'institucion-registro',
}


# ============================================================================
# UTILIDADES
# ============================================================================

def _build_response(success: bool, status_code: int = 200, **payload: Any) -> JsonResponse:
    """Construye una respuesta JSON estandarizada."""
    body = {'success': success, **payload}
    return jsonify(body), status_code


def _validar_tema(tema: str) -> None:
    """Valida que el tema exista y lance error legible en caso contrario."""
    if tema not in TEMA_MODELOS:
        disponibles = ', '.join(sorted(TEMA_MODELOS.keys()))
        raise RequestValidationError(f"Tema '{tema}' no válido. Temas disponibles: {disponibles}", status_code=400)


def _obtener_modelo_y_campo(tema: str) -> Tuple[ModelType, str]:
    """Obtiene el modelo y el campo principal asociados a un tema."""
    return TEMA_MODELOS[tema], TEMA_CAMPOS[tema]


def _obtener_payload_para_tema(tema: str) -> Tuple[ModelType, str, Dict[str, Any]]:
    """Obtiene el payload válido y metadatos requeridos para operar sobre un tema."""
    data = obtener_json_requerido(
        request,
        mensaje_tipo=CONTENT_TYPE_ERROR,
        mensaje_vacio=DATA_REQUIRED_ERROR,
    )
    modelo, campo_nombre = _obtener_modelo_y_campo(tema)
    if campo_nombre not in data:
        raise RequestValidationError(
            ERROR_CAMPO_REQUERIDO.format(campo=campo_nombre),
            status_code=400,
        )
    return modelo, campo_nombre, data


def _obtener_nombre_normalizado(tema: str, campo_nombre: str, valor: Any) -> str:
    """Normaliza y valida el campo nombre asociado al tema."""
    try:
        return _normalizar_nombre_por_tema(tema, campo_nombre, valor)
    except ValidationError as exc:
        raise RequestValidationError(str(exc), status_code=400) from exc


def _existe_registro_con_nombre(
    modelo: ModelType,
    campo_nombre: str,
    nombre: str,
    *,
    excluir_id: Optional[int] = None,
) -> bool:
    """Verifica si existe otro registro con el mismo nombre."""
    filtro: Dict[str, Any] = {campo_nombre: nombre}
    if hasattr(modelo, 'estado'):
        filtro['estado'] = True

    consulta = modelo.query.filter_by(**filtro)
    if excluir_id is not None:
        pk_name = _obtener_pk_nombre(modelo)
        consulta = consulta.filter(getattr(modelo, pk_name) != excluir_id)
    return consulta.first() is not None


def _obtener_registro_por_id(modelo: ModelType, registro_id: int) -> Any:
    """Obtiene un registro y lanza error si no existe."""
    registro = modelo.query.get(registro_id)
    if not registro:
        raise RequestValidationError(
            ERROR_REGISTRO_NO_ENCONTRADO.format(registro_id=registro_id),
            status_code=404,
        )
    return registro


def _normalizar_nombre_por_tema(tema: str, campo: str, valor: Any) -> str:
    """Normaliza el valor del campo nombre según el tema."""
    if tema in STRICT_NAME_TOPICS:
        return validate_name(campo, valor)
    return sanitize_free_text(campo, valor, max_length=120)


def _normalizar_codigo_eps(valor: Any) -> str:
    """Normaliza el código de EPS validando su formato."""
    if not valor:
        raise ValidationError('El código de la EPS es obligatorio')
    codigo = normalize_upper(str(valor))
    codigo = re.sub(r'[^A-Z0-9\-]', '', codigo)
    if not 2 <= len(codigo) <= 20:
        raise ValidationError(
            'El código de la EPS debe tener entre 2 y 20 caracteres alfanuméricos (puede incluir guiones)'
        )
    return codigo


def _normalizar_descripcion(valor: Any, max_length: int = 500) -> str:
    """Normaliza descripciones de longitud variable."""
    if not valor:
        return ''
    return sanitize_free_text('descripcion', valor, max_length=max_length)


def _normalizar_estado_bool(valor: Any, default: bool = True) -> bool:
    """Normaliza estados booleanos admitiendo diferentes representaciones."""
    if valor is None:
        return default
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return bool(int(valor))
    if isinstance(valor, str):
        return valor.strip().lower() in {'1', 'true', 'activo', 'activa', 'sí', 'si', 'on'}
    return default


def _obtener_pk_nombre(modelo) -> str:
    """Obtiene el nombre de la clave primaria de un modelo SQLAlchemy."""
    return list(modelo.__table__.primary_key.columns.keys())[0]


def _serializar_registros(registros: Iterable[Any]) -> List[Dict[str, Any]]:
    """Convierte una colección de registros a dict utilizando `to_dict`."""
    return [registro.to_dict() for registro in registros]


# ============================================================================
# ENDPOINTS
# ============================================================================

@dynamic_data_bp.route('/dynamic-data/<tema>', methods=['GET'])
def listar_datos_dinamicos(tema: str) -> JsonResponse:
    """Lista los registros activos del tema indicado."""
    try:
        _validar_tema(tema)
        modelo, _ = _obtener_modelo_y_campo(tema)

        if hasattr(modelo, 'estado'):
            registros = modelo.query.filter_by(estado=True).all()
        else:
            registros = modelo.query.all()
        
        return _build_response(
            True,
            data=_serializar_registros(registros),
            total=len(registros),
            tema=tema,
        )
    except RequestValidationError as exc:
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error('Error listando datos dinámicos (%s): %s', tema, str(exc))
        return _build_response(False, error=str(exc), status_code=500)


@dynamic_data_bp.route('/dynamic-data/<tema>', methods=['POST'])
def crear_dato_dinamico(tema: str) -> JsonResponse:
    """Crea un registro dentro del tema especificado."""
    try:
        _validar_tema(tema)
        modelo, campo_nombre, data = _obtener_payload_para_tema(tema)
        nombre = _obtener_nombre_normalizado(tema, campo_nombre, data[campo_nombre])

        if _existe_registro_con_nombre(modelo, campo_nombre, nombre):
            raise RequestValidationError(
                ERROR_DUPLICADO.format(campo=campo_nombre, valor=nombre),
                status_code=400,
            )

        nuevo_registro = modelo()
        setattr(nuevo_registro, campo_nombre, nombre)
        _aplicar_campos_especificos(tema, nuevo_registro, data, es_creacion=True)

        db.session.add(nuevo_registro)
        db.session.commit()
        
        return _build_response(
            True,
            message='Registro creado exitosamente',
            data=nuevo_registro.to_dict(),
            tema=tema,
            status_code=201,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error('Error creando dato dinámico (%s): %s', tema, str(exc))
        return _build_response(False, error=str(exc), status_code=500)


@dynamic_data_bp.route('/dynamic-data/<tema>/<int:registro_id>', methods=['PUT'])
def actualizar_dato_dinamico(tema: str, registro_id: int) -> JsonResponse:
    """Actualiza un registro específico."""
    try:
        _validar_tema(tema)
        modelo, campo_nombre, data = _obtener_payload_para_tema(tema)

        registro = _obtener_registro_por_id(modelo, registro_id)
        nuevo_nombre = _obtener_nombre_normalizado(tema, campo_nombre, data[campo_nombre])

        if _existe_registro_con_nombre(
            modelo,
            campo_nombre,
            nuevo_nombre,
            excluir_id=registro_id,
        ):
            raise RequestValidationError(
                ERROR_DUPLICADO_OTRO.format(campo=campo_nombre, valor=nuevo_nombre),
                status_code=400,
            )

        setattr(registro, campo_nombre, nuevo_nombre)
        _aplicar_campos_especificos(tema, registro, data, es_creacion=False)

        db.session.commit()

        return _build_response(
            True,
            message='Registro actualizado exitosamente',
            data=registro.to_dict(),
            tema=tema,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error('Error actualizando dato dinámico (%s): %s', tema, str(exc))
        return _build_response(False, error=str(exc), status_code=500)


@dynamic_data_bp.route('/dynamic-data/<tema>/<int:registro_id>', methods=['DELETE'])
def eliminar_dato_dinamico(tema: str, registro_id: int) -> JsonResponse:
    """Elimina físicamente un registro de datos dinámicos."""
    try:
        _validar_tema(tema)
        modelo, _ = _obtener_modelo_y_campo(tema)
        registro = _obtener_registro_por_id(modelo, registro_id)

        db.session.delete(registro)
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            logger.warning('Integridad violada al eliminar %s (%s): %s', tema, registro_id, str(exc))
            return _build_response(
                False,
                error=ERROR_ELIMINAR_REFERENCIAS,
                status_code=409,
            )

        return _build_response(
            True,
            message='Registro eliminado exitosamente',
            tema=tema,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error('Error eliminando dato dinámico (%s): %s', tema, str(exc))
        return _build_response(False, error=str(exc), status_code=500)


@dynamic_data_bp.route('/dynamic-data/<tema>/<int:registro_id>', methods=['GET'])
def obtener_dato_dinamico(tema: str, registro_id: int) -> JsonResponse:
    """Obtiene un registro específico de un tema."""
    try:
        _validar_tema(tema)
        modelo, _ = _obtener_modelo_y_campo(tema)
        registro = _obtener_registro_por_id(modelo, registro_id)

        return _build_response(True, data=registro.to_dict(), tema=tema)
    except RequestValidationError as exc:
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error('Error obteniendo dato dinámico (%s/%s): %s', tema, registro_id, str(exc))
        return _build_response(False, error=str(exc), status_code=500)


# ============================================================================
# CAMPOS ESPECÍFICOS POR TEMA
# ============================================================================


def _manejar_eps(registro: Any, data: Dict[str, Any], es_creacion: bool) -> None:
    """Aplica campos adicionales para EPS."""
    if es_creacion or 'codigo_eps' in data or 'codigo' in data:
        codigo_raw = data.get('codigo_eps') or data.get('codigo')
        registro.codigo_eps = _normalizar_codigo_eps(codigo_raw)
    if data.get('estado') is None and es_creacion:
        raise RequestValidationError('El estado es obligatorio para la EPS', status_code=400)
    registro.estado = _normalizar_estado_bool(data.get('estado'), getattr(registro, 'estado', True))


def _manejar_metodo_pago(registro: Any, data: Dict[str, Any], es_creacion: bool) -> None:
    """Aplica campos adicionales para métodos de pago."""
    if data.get('estado') is None and es_creacion:
        raise RequestValidationError('El estado es obligatorio para el método de pago', status_code=400)
    registro.estado = _normalizar_estado_bool(data.get('estado'), getattr(registro, 'estado', True))


def _manejar_tipo_evento(registro: Any, data: Dict[str, Any], es_creacion: bool) -> None:
    """Aplica campos adicionales para tipos de evento."""
    descripcion_raw = data.get('descripcion')
    if (es_creacion and not descripcion_raw) or (descripcion_raw is None):
        raise RequestValidationError('La descripción es obligatoria para el tipo de evento', status_code=400)
    if descripcion_raw is not None:
        registro.descripcion = _normalizar_descripcion(descripcion_raw)


def _manejar_roles(registro: Any, data: Dict[str, Any], es_creacion: bool) -> None:
    """Aplica campos adicionales para roles."""
    registro.estado = _normalizar_estado_bool(data.get('estado'), getattr(registro, 'estado', True))
    if 'descripcion' in data:
        registro.descripcion = _normalizar_descripcion(data.get('descripcion'), max_length=300)


TOPIC_SPECIFIC_HANDLERS: Dict[str, TopicHandler] = {
    'eps': _manejar_eps,
    'metodo-pago': _manejar_metodo_pago,
    'tipo-evento': _manejar_tipo_evento,
    'roles': _manejar_roles,
}


def _aplicar_campos_especificos(
    tema: str,
    registro: Any,
    data: Dict[str, Any],
    *,
    es_creacion: bool,
) -> None:
    """Aplica validaciones y campos adicionales según el tema."""
    handler = TOPIC_SPECIFIC_HANDLERS.get(tema)
    if handler:
        handler(registro, data, es_creacion)
    elif hasattr(registro, 'estado'):
        registro.estado = _normalizar_estado_bool(data.get('estado'), getattr(registro, 'estado', True))


# ============================================================================
# REGISTRO DEL BLUEPRINT
# ============================================================================


def registrar_dynamic_data_routes(app: Flask) -> None:
    """Registra las rutas de datos dinámicos en la aplicación Flask."""
    app.register_blueprint(dynamic_data_bp)
    logger.info('Rutas de datos dinámicos registradas exitosamente')
