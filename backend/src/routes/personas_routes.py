"""
Rutas de gestión de personas para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para listar, consultar y actualizar personas.
- Aplicar validaciones de negocio reutilizables.

El módulo respeta los principios SOLID, KISS y DRY.
"""

from typing import Any, Dict, Iterable, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from sqlalchemy import or_

from ..models.base import db
from ..models.personas.persona import Persona
from ..models.catalogos.tipo_documento import TipoDocumento
from ..models.categorias.sexo import Sexo
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido
from ..utils.validations import (
    ValidationError,
    normalize_spaces,
    validate_document,
    validate_email,
    validate_phone,
)

personas_bp = Blueprint('personas', __name__)
logger = obtener_registrador('aplicacion')

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MIN_PER_PAGE = 1
MIN_PHONE_LENGTH = 7
MAX_PHONE_LENGTH = 15
DOCUMENT_MIN_LENGTH = 6
DOCUMENT_MAX_LENGTH = 30

ERROR_CONTENT_TYPE_JSON = 'Content-Type debe ser application/json'
ERROR_DATOS_REQUERIDOS = 'No se proporcionaron datos'
ERROR_PERSONA_NO_ENCONTRADA = 'Persona con ID {id} no encontrada'
ERROR_EMAIL_INVALIDO = 'Formato de email inválido'
ERROR_EMAIL_DUPLICADO = 'Ya existe otra persona con el email: {email}'
ERROR_TELEFONO_INVALIDO = 'Formato de teléfono inválido (solo números, mínimo 7 dígitos)'
ERROR_DOCUMENTO_INVALIDO = 'Formato de documento inválido (solo números, mínimo 6 dígitos)'
ERROR_DOCUMENTO_DUPLICADO = 'Ya existe otra persona con el documento: {documento}'
ERROR_TIPO_DOCUMENTO_NO_ENCONTRADO = 'Tipo de documento con ID {id} no encontrado'
ERROR_SEXO_NO_ENCONTRADO = 'Sexo con ID {id} no encontrado'

JsonResponse = Tuple[Response, int]


def _obtener_paginacion() -> Tuple[int, int]:
    """Obtiene los parámetros de paginación normalizados."""
    page = request.args.get('page', DEFAULT_PAGE, type=int) or DEFAULT_PAGE
    per_page = request.args.get('per_page', DEFAULT_PER_PAGE, type=int) or DEFAULT_PER_PAGE
    page = max(MIN_PER_PAGE, page)
    per_page = max(MIN_PER_PAGE, per_page)
    return page, per_page


def _filtrar_por_estado(query, estado_param: str | None):
    """Aplica filtro de estado si se proporciona."""
    if estado_param is None:
        return query
    estado_bool = estado_param.lower() == 'true'
    return query.filter_by(estado=estado_bool)


def _aplicar_busqueda(query, termino: str):
    """Aplica filtro de búsqueda a la consulta principal."""
    if not termino:
        return query

    search = f"%{termino}%"
    return query.filter(
        or_(
            Persona.primer_nombre.ilike(search),
            Persona.segundo_nombre.ilike(search),
            Persona.primer_apellido.ilike(search),
            Persona.segundo_apellido.ilike(search),
            Persona.documento.cast(db.String).ilike(search),
            Persona.correo_electronico.ilike(search),
        )
    )


def _serializar_paginacion(paginado) -> Dict[str, Any]:
    """Serializa la información de paginación para la respuesta."""
    return {
        'page': paginado.page,
        'per_page': paginado.per_page,
        'total': paginado.total,
        'pages': paginado.pages,
        'has_next': paginado.has_next,
        'has_prev': paginado.has_prev,
    }


def _limpiar_texto(value: Any) -> str | None:
    """Normaliza texto libre preservando el formato original."""
    if value is None:
        return None

    texto = normalize_spaces(str(value))
    return texto or None


def _validar_email_unico(persona_id: int, correo: str) -> None:
    """Verifica que el correo electrónico no esté duplicado."""
    existe = (
        Persona.query.filter_by(correo_electronico=correo)
        .filter(Persona.id_persona != persona_id)
        .first()
    )
    if existe:
        raise RequestValidationError(
            ERROR_EMAIL_DUPLICADO.format(email=correo),
            status_code=400,
        )


def _validar_documento_unico(persona_id: int, documento: str) -> None:
    """Verifica que el documento no esté duplicado."""
    existe = (
        Persona.query.filter_by(documento=documento)
        .filter(Persona.id_persona != persona_id)
        .first()
    )
    if existe:
        raise RequestValidationError(
            ERROR_DOCUMENTO_DUPLICADO.format(documento=documento),
            status_code=400,
        )


def _validar_relaciones(data: Dict[str, Any]) -> None:
    """Verifica relaciones foráneas antes de actualizar."""
    if 'id_tipo_documento' in data:
        tipo_id = data['id_tipo_documento']
        if not TipoDocumento.query.get(tipo_id):
            raise RequestValidationError(
                ERROR_TIPO_DOCUMENTO_NO_ENCONTRADO.format(id=tipo_id),
                status_code=400,
            )

    if 'id_sexo' in data:
        sexo_id = data['id_sexo']
        if not Sexo.query.get(sexo_id):
            raise RequestValidationError(
                ERROR_SEXO_NO_ENCONTRADO.format(id=sexo_id),
                status_code=400,
            )


def _preparar_actualizacion(persona_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza y valida los campos permitidos para actualización."""
    cambios: Dict[str, Any] = {}

    if 'correo_electronico' in data:
        try:
            correo = validate_email('correo_electronico', data['correo_electronico'])
        except ValidationError:
            raise RequestValidationError(ERROR_EMAIL_INVALIDO, status_code=400) from None
        _validar_email_unico(persona_id, correo)
        cambios['correo_electronico'] = correo

    if 'telefono' in data:
        try:
            telefono = validate_phone(
                'telefono',
                data['telefono'],
                min_length=MIN_PHONE_LENGTH,
                max_length=MAX_PHONE_LENGTH,
            )
        except ValidationError:
            raise RequestValidationError(ERROR_TELEFONO_INVALIDO, status_code=400) from None
        cambios['telefono'] = telefono

    if 'documento' in data:
        try:
            documento = validate_document(
                'documento',
                data['documento'],
                min_length=DOCUMENT_MIN_LENGTH,
                max_length=DOCUMENT_MAX_LENGTH,
            )
        except ValidationError:
            raise RequestValidationError(ERROR_DOCUMENTO_INVALIDO, status_code=400) from None
        _validar_documento_unico(persona_id, documento)
        cambios['documento'] = documento

    campos_texto = {
        'primer_nombre',
        'segundo_nombre',
        'primer_apellido',
        'segundo_apellido',
        'direccion',
    }
    for campo in campos_texto.intersection(data.keys()):
        cambios[campo] = _limpiar_texto(data[campo])

    for campo in {'id_tipo_documento', 'id_sexo', 'estado'}:
        if campo in data:
            cambios[campo] = data[campo]

    return cambios


def _aplicar_cambios(persona: Persona, cambios: Dict[str, Any]) -> None:
    """Aplica los cambios preparados sobre la instancia de persona."""
    for campo, valor in cambios.items():
        setattr(persona, campo, valor)


def _obtener_persona(persona_id: int) -> Persona | None:
    """Recupera una persona por identificador."""
    return Persona.query.get(persona_id)


@personas_bp.route('/personas', methods=['GET'])
def listar_personas() -> JsonResponse:
    """Lista todas las personas aplicando filtros de estado y búsqueda."""
    try:
        page, per_page = _obtener_paginacion()
        search = (request.args.get('search') or '').strip()
        estado = request.args.get('estado')

        query = Persona.query
        query = _filtrar_por_estado(query, estado)
        query = _aplicar_busqueda(query, search)

        paginado = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'success': True,
            'data': [persona.to_dict() for persona in paginado.items],
            'pagination': _serializar_paginacion(paginado),
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error inesperado al listar personas: %s", str(exc))
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500


@personas_bp.route('/personas/<int:persona_id>', methods=['GET'])
def obtener_persona(persona_id: int) -> JsonResponse:
    """Obtiene una persona específica por identificador."""
    try:
        persona = _obtener_persona(persona_id)
        if not persona:
            return jsonify({
                'success': False,
                'error': ERROR_PERSONA_NO_ENCONTRADA.format(id=persona_id)
            }), 404

        return jsonify({
            'success': True,
            'data': persona.to_dict()
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error inesperado al obtener persona %s: %s", persona_id, str(exc))
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500


@personas_bp.route('/personas/<int:persona_id>', methods=['PUT'])
def actualizar_persona(persona_id: int) -> JsonResponse:
    """Actualiza los datos de una persona específica."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        persona = _obtener_persona(persona_id)
        if not persona:
            return jsonify({
                'success': False,
                'error': ERROR_PERSONA_NO_ENCONTRADA.format(id=persona_id)
            }), 404

        _validar_relaciones(data)
        cambios = _preparar_actualizacion(persona_id, data)
        if not cambios:
            return jsonify({
                'success': True,
                'message': 'Persona actualizada exitosamente',
                'data': persona.to_dict()
            }), 200

        _aplicar_cambios(persona, cambios)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Persona actualizada exitosamente',
            'data': persona.to_dict()
        }), 200

    except RequestValidationError as exc:
        logger.warning(
            "Validación de solicitud al actualizar persona %s: %s",
            persona_id,
            str(exc),
        )
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(exc)
        }), exc.status_code
    except ValidationError as exc:
        logger.warning(
            "Validación de datos al actualizar persona %s: %s",
            persona_id,
            str(exc),
        )
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 400
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.exception("Error inesperado al actualizar persona %s: %s", persona_id, str(exc))
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500


@personas_bp.route('/personas/<int:persona_id>', methods=['DELETE'])
def eliminar_persona(persona_id: int) -> JsonResponse:
    """Desactiva (soft delete) una persona específica."""
    try:
        persona = _obtener_persona(persona_id)
        if not persona:
            return jsonify({
                'success': False,
                'error': ERROR_PERSONA_NO_ENCONTRADA.format(id=persona_id)
            }), 404

        persona.estado = False
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Persona eliminada exitosamente'
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.exception("Error inesperado al eliminar persona %s: %s", persona_id, str(exc))
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500


@personas_bp.route('/personas/<int:persona_id>/activar', methods=['PUT'])
def activar_persona(persona_id: int) -> JsonResponse:
    """Activa una persona previamente desactivada."""
    try:
        persona = _obtener_persona(persona_id)
        if not persona:
            return jsonify({
                'success': False,
                'error': ERROR_PERSONA_NO_ENCONTRADA.format(id=persona_id)
            }), 404

        persona.estado = True
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Persona activada exitosamente',
            'data': persona.to_dict()
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.exception("Error inesperado al activar persona %s: %s", persona_id, str(exc))
        return jsonify({
            'success': False,
            'error': str(exc)
        }), 500


def registrar_personas_routes(app: Flask) -> None:
    """Registra las rutas de personas en la aplicación Flask."""
    app.register_blueprint(personas_bp)
    logger.info("Rutas de personas registradas exitosamente")
