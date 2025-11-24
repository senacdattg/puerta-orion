"""
Rutas y lógica de negocio para la gestión de mensualidades del sistema.

Responsabilidad:
- Administrar mensualidades, abonos y consultas relacionadas.
- Restringir acceso y flujos según los roles del usuario autenticado.

Cumple con los principios SOLID, DRY y PEP8.
"""

from datetime import date
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from flask_cors import cross_origin
from sqlalchemy import String, cast, extract, or_

from ..middleware.auth_decorator import get_current_user, has_role, permission_required
from ..models.base import db
from ..models.pagos.abono_mensualidad import AbonoMensualidad
from ..models.pagos.mensualidad import Mensualidad
from ..models.pagos.metodo_pago import MetodoPago
from ..models.usuarios.usuario import Usuario
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido
from ..utils.validations import ValidationError, validate_document

try:
    # Import defensivo: la ruta del modelo de Persona puede variar
    from ..models.personas.persona import Persona  # type: ignore
except Exception:  # pragma: no cover
    Persona = None  # fallback si no existe o cambia la ruta

JsonResponse = Tuple[Response, int]

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
DEPORTISTA_ROLE = 'deportista'
PERSONA_NOMBRE_ATTRS = ('nombre', 'nombres', 'nombre_persona', 'nombre_completo')
PERSONA_DOCUMENTO_ATTRS = ('documento',)
ERROR_MENSUALIDAD_NO_ENCONTRADA = 'Mensualidad no encontrada'
ERROR_NO_AUTORIZADO = 'No autorizado ver esta mensualidad'
ERROR_DOCUMENTO_REQUERIDO = 'Debes proporcionar un número de documento'
ERROR_METODO_REQUERIDO = 'El método de pago es requerido'
ERROR_MONTO_POSITIVO = 'monto_pago debe ser > 0'
ERROR_SALDO_PENDIENTE_REQUERIDO = 'El saldo pendiente es requerido'
ERROR_SALDO_INVALIDO = 'El saldo pendiente debe ser un número mayor o igual a 0'
ERROR_FORMATO_FECHA = 'fecha_vencimiento no tiene un formato válido (YYYY-MM-DD)'
ERROR_ESTADO_INICIAL = 'El estado inicial debe ser "Pagado" o "Pendiente"'
ERROR_ESTADO_REQUERIDO = 'El estado inicial es requerido'
ERROR_METODO_NO_ENCONTRADO = 'Método de pago con ID {id} no encontrado'
ERROR_PERSONA_NO_DETERMINADA = 'No se pudo determinar id_persona'
ERROR_PERSONA_NO_DEPORTISTA = 'La persona especificada no tiene el rol "Deportista". No se puede crear la mensualidad.'
ERROR_MENSUALIDAD_DUPLICADA = 'Ya existe una mensualidad para este deportista en el mismo mes y año'
ERROR_DOCUMENTO_NUEVO_NO_ROL = 'La persona asociada al documento no tiene el rol "Deportista".'
ERROR_SALDO_SUPERA_MONTO = 'saldo_pendiente no puede ser mayor al monto de la mensualidad'
ERROR_MONTO_ABONADO_SUPERA = 'El monto abonado no puede superar el saldo pendiente'
ERROR_MONTO_ABONADO_POSITIVO = 'monto_abonado debe ser > 0'
ERROR_FECHA_ABONO = 'fecha_abono no tiene un formato válido (YYYY-MM-DD)'
ERROR_MONTO_ABONO = 'monto debe ser > 0'
ERROR_ID_ABONO = 'Abono no encontrado'
ERROR_DOCUMENTO_VALIDACION = 'Persona no encontrada por numero_documento'
ERROR_ID_PERSONA_OBLIGATORIO = 'Debe proporcionar id_persona o numero_documento'
ERROR_ID_PERSONA_NUMERICO = 'id_persona debe ser numérico'
ERROR_JSON_CONTENT = 'Content-Type debe ser application/json'
ERROR_DATOS_REQUERIDOS = 'No se proporcionaron datos'
ERROR_FECHA_VENCIMIENTO_REQUERIDA = 'La fecha de vencimiento es requerida'
ERROR_SALDO_INVALIDO_RECALC = 'saldo_pendiente inválido'
ERROR_ID_PERSONA_INVALIDO = 'No se pudo determinar id_persona de la persona encontrada'
ERROR_METODO_NUMERICO = 'id_metodo_pago debe ser numérico'
ERROR_MONTO_MENSUALIDAD_INVALIDO = 'La mensualidad tiene un monto inválido'
ERROR_ID_PERSONA_ASOCIADO_INVALIDO = 'id_persona asociado al documento es inválido'

logger = obtener_registrador('aplicacion')


def _add_months(base: date, months: int) -> date:
    """Suma meses a una fecha sin dependencias externas."""
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(
        base.day,
        [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31,
        ][month - 1],
    )
    return date(year, month, day)


def _recalcular_estado_mensualidad(mensualidad: Mensualidad) -> None:
    # Recalcular saldo pendiente y estado a partir de los abonos
    total_abonos = db.session.query(
        db.func.coalesce(db.func.sum(AbonoMensualidad.monto), 0)
    ).filter(
        AbonoMensualidad.id_mensualidad == mensualidad.id_mensualidad
    ).scalar() or 0
    try:
        total_abonos = float(total_abonos)
    except Exception:
        total_abonos = 0.0

    try:
        monto = float(mensualidad.monto_pago)
    except Exception:
        monto = 0.0

    restante = max(0.0, monto - total_abonos)
    mensualidad.saldo_pendiente = restante
    if restante == 0:
        mensualidad.estado = True
        mensualidad.fecha_pago = date.today()
    else:
        mensualidad.estado = False
        mensualidad.fecha_pago = None


def _estado_texto(mensualidad: Mensualidad) -> str:
    try:
        if not mensualidad.activo:
            return 'Inactiva'
        if float(mensualidad.saldo_pendiente or 0) == 0:
            return 'Pagado'
        # Considerar vencido cuando la fecha de vencimiento es hoy o ya pasó
        if mensualidad.fecha_vencimiento and mensualidad.fecha_vencimiento <= date.today():
            return 'Vencido'
        return 'Pendiente'
    except Exception:
        return 'Pendiente'


mensualidades_bp = Blueprint('mensualidades', __name__, url_prefix='/api/mensualidades')


def _parse_decimal(value: Any) -> Optional[float]:
    """Convierte un valor numérico a float de manera segura."""
    try:
        return float(value) if value is not None else None
    except Exception:
        return None


def _buscar_persona_por_documento(numero_documento: Any) -> Optional[Any]:
    """Busca una persona por documento manejando distintos esquemas de columnas."""
    if Persona is None or not numero_documento:
        return None

    doc_str = str(numero_documento).strip()
    columnas: List[Any] = []
    for nombre in ('numero_documento', 'documento', 'num_documento', 'dni', 'cedula'):
        try:
            col = getattr(Persona, nombre, None)
            if col is not None:
                columnas.append(col)
        except Exception:
            continue

    if not columnas:
        return None

    try:
        condiciones = [cast(columna, String) == doc_str for columna in columnas]
        return db.session.query(Persona).filter(or_(*condiciones)).first()
    except Exception:
        return None


def _persona_tiene_rol_deportista(id_persona: Optional[int]) -> bool:
    if id_persona is None:
        return False

    try:
        usuario = Usuario.query.filter_by(id_persona=id_persona).first()
        if not usuario or not getattr(usuario, 'estado', True):
            return False

        for rol in getattr(usuario, 'roles', []) or []:
            nombre = getattr(rol, 'nombre_rol', None) or getattr(rol, 'nombre', None)
            if nombre and nombre.lower() == 'deportista':
                return True
    except Exception:
        return False

    return False


def _extraer_nombre_persona(persona: Any) -> Optional[str]:
    """Obtiene el mejor nombre disponible para una persona."""
    if persona is None:
        return None

    for atributo in PERSONA_NOMBRE_ATTRS:
        valor = getattr(persona, atributo, None)
        if valor:
            return valor
    return None


def _extraer_documento_persona(persona: Any) -> Optional[str]:
    """Obtiene el documento asociado a una persona."""
    if persona is None:
        return None

    for atributo in PERSONA_DOCUMENTO_ATTRS:
        valor = getattr(persona, atributo, None)
        if valor is not None:
            return valor
    return None


def _normalizar_documento_persona(documento: Any) -> Optional[str]:
    """Normaliza un documento eliminando caracteres no numéricos."""
    if documento is None:
        return None
    try:
        return re.sub(r'\D', '', str(documento)) or None
    except Exception:
        return str(documento)


def _adjuntar_info_persona_dict(mensualidad_obj: Mensualidad, destino_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Agrega información de persona asociada a la respuesta serializada."""
    persona_rel = getattr(mensualidad_obj, 'persona', None)
    persona_nombre = _extraer_nombre_persona(persona_rel)
    persona_documento = _extraer_documento_persona(persona_rel)

    if (persona_nombre is None or persona_documento is None) and Persona is not None:
        persona_db = db.session.get(Persona, getattr(mensualidad_obj, 'id_persona', None))
        if persona_db is not None:
            persona_nombre = persona_nombre or _extraer_nombre_persona(persona_db)
            persona_documento = persona_documento or _extraer_documento_persona(persona_db)

    persona_documento = _normalizar_documento_persona(persona_documento)

    destino_dict['persona_nombre'] = persona_nombre
    destino_dict['numero_documento'] = persona_documento
    return destino_dict


def _obtener_parametros_paginacion() -> Tuple[int, int]:
    """Obtiene página y tamaño de página para las consultas paginadas."""
    page = request.args.get('page', default=DEFAULT_PAGE, type=int) or DEFAULT_PAGE
    per_page = request.args.get('per_page', default=DEFAULT_PER_PAGE, type=int) or DEFAULT_PER_PAGE
    return page, per_page


def _respuesta_lista_vacia(page: int, per_page: int) -> JsonResponse:
    """Genera la respuesta vacía estándar para listados."""
    return jsonify({
        'success': True,
        'data': [],
        'page': page,
        'per_page': per_page,
        'total': 0
    }), 200


def _obtener_personas_acudidas(user: Optional[Dict[str, Any]]) -> List[int]:
    """Obtiene los IDs de persona asociados a un acudiente."""
    if not user or not user.get('persona'):
        return []

    id_persona = user['persona'].get('id_persona')
    if not id_persona:
        return []

    modelos_acudiente = _importar_modelos_acudiente()
    if not modelos_acudiente:
        return []
    acudiente_model, deportista_acudiente_model, deportista_model = modelos_acudiente

    acudiente = acudiente_model.query.filter_by(id_persona=id_persona).first()
    if not acudiente:
        return []

    relaciones = deportista_acudiente_model.query.filter_by(id_acudiente=acudiente.id_acudiente).all()
    if not relaciones:
        return []

    deportista_ids = [rel.id_deportista for rel in relaciones]
    deportistas = deportista_model.query.filter(deportista_model.id_deportista.in_(deportista_ids)).all()
    return [dep.id_persona for dep in deportistas if dep.id_persona]


def _importar_modelos_acudiente() -> Optional[Tuple[Any, Any, Any]]:
    """Importa los modelos necesarios para operar con acudientes."""
    try:  # pragma: no cover
        from ..models.acudientes.acudiente import Acudiente as AcudienteModel
        from ..models.acudientes.deportista_acudiente import DeportistaAcudiente as DeportistaAcudienteModel
        from ..models.deportistas.deportista import Deportista as DeportistaModel
        return AcudienteModel, DeportistaAcudienteModel, DeportistaModel
    except Exception:
        logger.warning("No fue posible importar modelos de acudientes para restricciones de acceso")
        return None


def _resolver_acceso_roles(persona_id_param: Optional[int], page: int, per_page: int) -> Tuple[Optional[int], Optional[List[int]], Optional[JsonResponse]]:
    """Determina restricciones de acceso según roles del usuario autenticado."""
    user = get_current_user()

    if has_role('Deportista') and user and user.get('persona'):
        persona_deportista = user['persona'].get('id_persona')
        return persona_deportista, None, None

    if has_role('Acudiente') and not persona_id_param:
        acudidos = _obtener_personas_acudidas(user)
        if not acudidos:
            return None, [], _respuesta_lista_vacia(page, per_page)
        return None, acudidos, None

    return persona_id_param, None, None


def _serializar_mensualidad(mensualidad: Mensualidad) -> Dict[str, Any]:
    """Serializa una mensualidad agregando campos adicionales requeridos."""
    data = mensualidad.to_dict()
    data['estado_texto'] = _estado_texto(mensualidad)
    try:
        created_at = getattr(mensualidad, 'created_at', None)
        data['created_at'] = created_at.isoformat() if created_at else None
    except Exception:
        data['created_at'] = None

    data['id_metodo_pago'] = getattr(mensualidad, 'id_metodo_pago', None)
    return _adjuntar_info_persona_dict(mensualidad, data)


def _extraer_id_persona(data: Dict[str, Any]) -> Optional[int]:
    """Obtiene y valida el identificador de persona desde el payload."""
    id_persona_raw = data.get('id_persona')
    if id_persona_raw is None:
        return None
    try:
        return int(id_persona_raw)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_ID_PERSONA_NUMERICO, status_code=400) from exc


def _extraer_documento_validado(data: Dict[str, Any]) -> Optional[str]:
    """Obtiene y valida el número de documento desde el payload."""
    numero_documento_raw = data.get('numero_documento') or data.get('documento')
    if isinstance(numero_documento_raw, str):
        numero_documento_raw = numero_documento_raw.strip()
    if not numero_documento_raw:
        return None
    try:
        return validate_document('numero_documento', numero_documento_raw)
    except ValidationError as exc:
        raise RequestValidationError(str(exc), status_code=400) from exc


def _obtener_id_persona_por_documento(documento: str) -> int:
    """Busca una persona por documento y devuelve su identificador."""
    persona = _buscar_persona_por_documento(documento)
    if not persona:
        raise RequestValidationError(ERROR_DOCUMENTO_VALIDACION, status_code=404)

    id_persona = getattr(persona, 'id_persona', None) or getattr(persona, 'id', None)
    if not id_persona:
        raise RequestValidationError(ERROR_ID_PERSONA_INVALIDO, status_code=400)

    try:
        return int(id_persona)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_ID_PERSONA_NUMERICO, status_code=400) from exc


def _validar_persona_con_rol_deportista(id_persona: int) -> None:
    """Verifica que la persona tenga rol deportista."""
    if not _persona_tiene_rol_deportista(id_persona):
        raise RequestValidationError(ERROR_PERSONA_NO_DEPORTISTA, status_code=400)


def _resolver_persona_para_creacion(data: Dict[str, Any]) -> Tuple[int, Optional[str]]:
    """Obtiene el identificador de persona desde el payload."""
    id_persona = _extraer_id_persona(data)
    documento = _extraer_documento_validado(data)

    if id_persona is None and documento is None:
        raise RequestValidationError(ERROR_ID_PERSONA_OBLIGATORIO, status_code=400)

    if id_persona is None and documento is not None:
        id_persona = _obtener_id_persona_por_documento(documento)

    if id_persona is None:
        raise RequestValidationError(ERROR_PERSONA_NO_DETERMINADA, status_code=400)

    _validar_persona_con_rol_deportista(id_persona)

    return id_persona, documento


def _obtener_estado_inicial(data: Dict[str, Any]) -> bool:
    """Valida y obtiene el estado inicial de la mensualidad."""
    estado_ui_raw = data.get('estado_ui')
    if estado_ui_raw is None:
        raise RequestValidationError(ERROR_ESTADO_REQUERIDO, status_code=400)

    estado_ui = str(estado_ui_raw).strip().lower()
    if estado_ui not in ('pagado', 'pendiente'):
        raise RequestValidationError(ERROR_ESTADO_INICIAL, status_code=400)

    return estado_ui == 'pagado'


def _obtener_metodo_pago(data: Dict[str, Any]) -> int:
    """Valida y obtiene el método de pago."""
    id_metodo_pago_raw = data.get('id_metodo_pago')
    if id_metodo_pago_raw in (None, '',):
        raise RequestValidationError(ERROR_METODO_REQUERIDO, status_code=400)

    try:
        id_metodo_pago = int(id_metodo_pago_raw)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_METODO_NUMERICO, status_code=400) from exc

    if not MetodoPago.query.get(id_metodo_pago):
        raise RequestValidationError(
            ERROR_METODO_NO_ENCONTRADO.format(id=id_metodo_pago),
            status_code=404,
        )

    return id_metodo_pago


def _obtener_monto_pago(data: Dict[str, Any]) -> float:
    """Valida y obtiene el monto de la mensualidad."""
    monto_pago = _parse_decimal(data.get('monto_pago'))
    if monto_pago is None or monto_pago <= 0:
        raise RequestValidationError(ERROR_MONTO_POSITIVO, status_code=400)
    return float(monto_pago)


def _obtener_fecha_vencimiento(data: Dict[str, Any]) -> date:
    """Valida y obtiene la fecha de vencimiento."""
    fecha_vencimiento_raw = data.get('fecha_vencimiento')
    if not fecha_vencimiento_raw:
        raise RequestValidationError(ERROR_FECHA_VENCIMIENTO_REQUERIDA, status_code=400)
    try:
        return date.fromisoformat(str(fecha_vencimiento_raw))
    except ValueError as exc:
        raise RequestValidationError(ERROR_FORMATO_FECHA, status_code=400) from exc


def _calcular_saldo_inicial(data: Dict[str, Any], monto_pago: float, is_pagado_inicial: bool) -> float:
    """Calcula el saldo inicial según el estado y monto enviados."""
    saldo_bruto = data.get('saldo_pendiente')
    if saldo_bruto in (None, ''):
        if is_pagado_inicial:
            return 0.0
        raise RequestValidationError(ERROR_SALDO_PENDIENTE_REQUERIDO, status_code=400)

    saldo_inicial = _parse_decimal(saldo_bruto)
    if saldo_inicial is None or saldo_inicial < 0:
        raise RequestValidationError(ERROR_SALDO_INVALIDO, status_code=400)

    saldo_calculado = min(float(saldo_inicial), monto_pago)
    return 0.0 if is_pagado_inicial else saldo_calculado


def _validar_mensualidad_duplicada(id_persona: int, fecha_vencimiento: date, mensualidad_id: Optional[int] = None) -> None:
    """Verifica que no exista una mensualidad duplicada para el mismo mes y año."""
    query = Mensualidad.query.filter(
        Mensualidad.id_persona == id_persona,
        extract('year', Mensualidad.fecha_vencimiento) == fecha_vencimiento.year,
        extract('month', Mensualidad.fecha_vencimiento) == fecha_vencimiento.month,
    )
    if mensualidad_id:
        query = query.filter(Mensualidad.id_mensualidad != mensualidad_id)
    if query.first():
        raise RequestValidationError(ERROR_MENSUALIDAD_DUPLICADA, status_code=400)


def _registrar_abono_inicial(mensualidad: Mensualidad, monto_pago: float, id_metodo_pago: int) -> None:
    """Crea un abono inicial cuando la mensualidad queda pagada desde el inicio."""
    if not mensualidad.id_mensualidad:
        return

    try:
        abono_inicial = AbonoMensualidad(
            id_mensualidad=mensualidad.id_mensualidad,
            monto=monto_pago,
            fecha_abono=mensualidad.fecha_pago or date.today(),
            id_metodo_pago=id_metodo_pago
        )
        db.session.add(abono_inicial)
    except Exception:  # pragma: no cover
        logger.warning("No fue posible registrar el abono inicial de la mensualidad %s", mensualidad.id_mensualidad)


def _procesar_cambio_documento(mensualidad: Mensualidad, data: Dict[str, Any]) -> Optional[str]:
    """Actualiza el documento asociado a la mensualidad si corresponde."""
    if 'numero_documento' not in data:
        return None

    try:
        nuevo_documento = validate_document('numero_documento', data['numero_documento'])
    except ValidationError as exc:
        raise RequestValidationError(str(exc), status_code=400) from exc

    persona_destino = _buscar_persona_por_documento(nuevo_documento)
    if not persona_destino:
        raise RequestValidationError(ERROR_DOCUMENTO_VALIDACION, status_code=404)

    nuevo_id_persona = getattr(persona_destino, 'id_persona', None) or getattr(persona_destino, 'id', None)
    if not nuevo_id_persona:
        raise RequestValidationError(ERROR_ID_PERSONA_INVALIDO, status_code=400)

    try:
        nuevo_id_persona = int(nuevo_id_persona)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_ID_PERSONA_ASOCIADO_INVALIDO, status_code=400) from exc

    if not _persona_tiene_rol_deportista(nuevo_id_persona):
        raise RequestValidationError(ERROR_DOCUMENTO_NUEVO_NO_ROL, status_code=400)

    if mensualidad.id_persona != nuevo_id_persona:
        mensualidad.id_persona = nuevo_id_persona

    return nuevo_documento


def _actualizar_metodo_pago_campo(mensualidad: Mensualidad, valor: Any) -> None:
    """Actualiza el método de pago de la mensualidad y del abono inicial si existe."""
    if valor in (None, '',):
        raise RequestValidationError(ERROR_METODO_REQUERIDO, status_code=400)

    try:
        nuevo_metodo = int(valor)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_METODO_NUMERICO, status_code=400) from exc

    if not MetodoPago.query.get(nuevo_metodo):
        raise RequestValidationError(
            ERROR_METODO_NO_ENCONTRADO.format(id=nuevo_metodo),
            status_code=404,
        )

    metodo_anterior = mensualidad.id_metodo_pago
    mensualidad.id_metodo_pago = nuevo_metodo
    
    # Si solo se cambió el método de pago (no el monto ni el saldo), actualizar el abono inicial si existe
    # Buscar el abono inicial (el más antiguo que coincide con la fecha de creación/pago inicial)
    if mensualidad.id_mensualidad and metodo_anterior != nuevo_metodo:
        abono_inicial = (
            AbonoMensualidad.query
            .filter_by(id_mensualidad=mensualidad.id_mensualidad)
            .order_by(AbonoMensualidad.id_abono.asc())
            .first()
        )
        
        # Si existe un abono inicial y coincide con la fecha de pago de la mensualidad, actualizarlo
        if abono_inicial and mensualidad.fecha_pago:
            if abono_inicial.fecha_abono == mensualidad.fecha_pago:
                abono_inicial.id_metodo_pago = nuevo_metodo


def _actualizar_monto_pago_campo(mensualidad: Mensualidad, valor: Any) -> None:
    """Actualiza el monto de la mensualidad y ajusta el saldo si es necesario."""
    monto_pago = _parse_decimal(valor)
    if monto_pago is None or monto_pago <= 0:
        raise RequestValidationError(ERROR_MONTO_POSITIVO, status_code=400)

    mensualidad.monto_pago = monto_pago
    if mensualidad.saldo_pendiente is not None and mensualidad.saldo_pendiente > monto_pago:
        mensualidad.saldo_pendiente = monto_pago


def _actualizar_fecha_vencimiento_campo(mensualidad: Mensualidad, valor: Any) -> None:
    """Actualiza la fecha de vencimiento de la mensualidad."""
    if not valor:
        raise RequestValidationError(ERROR_FECHA_VENCIMIENTO_REQUERIDA, status_code=400)
    try:
        mensualidad.fecha_vencimiento = date.fromisoformat(str(valor))
    except ValueError as exc:
        raise RequestValidationError(ERROR_FORMATO_FECHA, status_code=400) from exc


def _actualizar_saldo_pendiente_campo(mensualidad: Mensualidad, valor: Any) -> None:
    """Actualiza el saldo pendiente validando límites."""
    saldo = _parse_decimal(valor)
    if saldo is None or saldo < 0:
        raise RequestValidationError(ERROR_SALDO_INVALIDO_RECALC, status_code=400)

    monto_base = mensualidad.monto_pago
    if monto_base is not None and saldo > monto_base:
        raise RequestValidationError(ERROR_SALDO_SUPERA_MONTO, status_code=400)

    mensualidad.saldo_pendiente = saldo


def _actualizar_activo_campo(mensualidad: Mensualidad, valor: Any) -> None:
    """Actualiza el estado activo de la mensualidad."""
    if isinstance(valor, str):
        mensualidad.activo = bool(int(valor))
    else:
        mensualidad.activo = bool(valor)


def _actualizar_estado_y_fecha_pago(mensualidad: Mensualidad) -> None:
    """Sincroniza estado y fecha de pago según el saldo pendiente."""
    if mensualidad.saldo_pendiente == 0:
        mensualidad.estado = True
        mensualidad.fecha_pago = date.today()
    else:
        mensualidad.estado = False
        mensualidad.fecha_pago = None


def _obtener_monto_abonado(data: Dict[str, Any]) -> float:
    """Obtiene y valida el monto abonado enviado en la solicitud."""
    monto_abonado = _parse_decimal(data.get('monto_abonado'))
    if monto_abonado is None or monto_abonado <= 0:
        raise RequestValidationError(ERROR_MONTO_ABONADO_POSITIVO, status_code=400)
    return float(monto_abonado)


def _obtener_monto_base(mensualidad: Mensualidad) -> float:
    """Obtiene el monto base de la mensualidad."""
    try:
        return float(mensualidad.monto_pago)
    except Exception as exc:
        raise RequestValidationError(ERROR_MONTO_MENSUALIDAD_INVALIDO, status_code=400) from exc


def _obtener_saldo_actual(mensualidad: Mensualidad, monto_base: float) -> float:
    """Calcula el saldo actual de la mensualidad."""
    try:
        return float(mensualidad.saldo_pendiente if mensualidad.saldo_pendiente is not None else monto_base)
    except Exception:
        return monto_base


def _obtener_fecha_abono(data: Dict[str, Any]) -> date:
    """Obtiene la fecha de abono, usando la fecha actual como predeterminada."""
    fecha_abono_str = data.get('fecha_abono')
    if not fecha_abono_str:
        return date.today()
    try:
        return date.fromisoformat(str(fecha_abono_str))
    except ValueError as exc:
        raise RequestValidationError(ERROR_FECHA_ABONO, status_code=400) from exc


def _obtener_id_metodo_pago_abono(data: Dict[str, Any]) -> Optional[int]:
    """Obtiene el método de pago asociado al abono si se envía."""
    id_metodo_pago_raw = data.get('id_metodo_pago')
    if id_metodo_pago_raw in (None, '',):
        return None
    try:
        return int(id_metodo_pago_raw)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_METODO_NUMERICO, status_code=400) from exc


def _calcular_meses_y_sobrante(monto_abonado: float, monto_base: float) -> Tuple[int, float]:
    """Calcula los meses cubiertos y el sobrante del abono."""
    if monto_base <= 0:
        return 0, 0.0
    meses_cubiertos = int(monto_abonado // monto_base)
    sobrante = monto_abonado - (meses_cubiertos * monto_base)
    return meses_cubiertos, sobrante


def _actualizar_vencimiento_y_saldo_post_abono(
    mensualidad: Mensualidad,
    monto_base: float,
    monto_abonado: float,
    meses_cubiertos: int,
    sobrante: float,
    saldo_actual: float,
) -> None:
    """Actualiza la fecha de vencimiento y saldo después del abono."""
    if meses_cubiertos > 0:
        base_fecha = (
            mensualidad.fecha_vencimiento
            if mensualidad.fecha_vencimiento and mensualidad.fecha_vencimiento > date.today()
            else date.today()
        )
        mensualidad.fecha_vencimiento = _add_months(base_fecha, meses_cubiertos)
        mensualidad.saldo_pendiente = max(0, monto_base - sobrante) if monto_base > 0 else 0
    else:
        try:
            saldo_float = float(mensualidad.saldo_pendiente)
        except Exception:
            saldo_float = saldo_actual
        mensualidad.saldo_pendiente = max(0, saldo_float - monto_abonado)


@mensualidades_bp.get('/buscar-persona')
@permission_required('crear_mensualidad')
def buscar_persona_por_documento() -> JsonResponse:
    """Busca una persona por documento y valida su rol asociado."""
    documento_raw = (request.args.get('documento') or '').strip()

    if not documento_raw:
        return jsonify({
            'success': False,
            'error': ERROR_DOCUMENTO_REQUERIDO
        }), 200

    try:
        documento = validate_document('numero_documento', documento_raw)
    except ValidationError as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 200

    persona = _buscar_persona_por_documento(documento)
    if not persona:
        return jsonify({
            'success': True,
            'encontrado': False,
            'message': 'No encontramos una persona registrada con ese número de documento.'
        }), 200

    data = {
        'id_persona': getattr(persona, 'id_persona', None) or getattr(persona, 'id', None),
        'documento': getattr(persona, 'documento', documento),
        'nombre_completo': getattr(persona, 'nombre', None) or getattr(persona, 'nombres', None) or
                           getattr(persona, 'nombre_persona', None) or getattr(persona, 'nombre_completo', None),
        'estado': bool(getattr(persona, 'estado', True))
    }

    mensaje = 'Persona encontrada y activa.' if data['estado'] else 'Persona encontrada, pero se encuentra inactiva.'
    data['rol_deportista'] = _persona_tiene_rol_deportista(data['id_persona'])

    return jsonify({
        'success': True,
        'encontrado': True,
        'message': mensaje,
        'data': data
    }), 200


@mensualidades_bp.get('/')
@permission_required('ver_mensualidad')
def listar_mensualidades() -> JsonResponse:
    try:
        persona_id_param = request.args.get('persona_id', type=int)
        page, per_page = _obtener_parametros_paginacion()

        persona_id, acudido_ids, respuesta = _resolver_acceso_roles(persona_id_param, page, per_page)
        if respuesta:
            return respuesta

        estado = request.args.get('estado')
        activo = request.args.get('activo', type=int)

        query = Mensualidad.query
        if persona_id is not None:
            query = query.filter(Mensualidad.id_persona == persona_id)
        elif acudido_ids:
            query = query.filter(Mensualidad.id_persona.in_(acudido_ids))

        if estado in ('pagado', 'pendiente'):
            query = query.filter(Mensualidad.estado == (estado == 'pagado'))

        if activo in (0, 1):
            query = query.filter(Mensualidad.activo == bool(activo))

        paginado = query.order_by(Mensualidad.id_mensualidad.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        items = [_serializar_mensualidad(mensualidad) for mensualidad in paginado.items]
        return jsonify({
            'success': True,
            'data': items,
            'page': page,
            'per_page': per_page,
            'total': paginado.total
        }), 200
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error listando mensualidades: %s", str(exc))
        return jsonify({'success': False, 'error': str(exc)}), 500

# Evitar redirecciones en preflight/solicitudes sin barra final
@mensualidades_bp.route('', methods=['GET'])
@permission_required('ver_mensualidad')
def listar_mensualidades_sin_slash() -> JsonResponse:
    """Alias sin barra final para el listado de mensualidades."""
    return listar_mensualidades()


@mensualidades_bp.get('/<int:mensualidad_id>')
@permission_required('ver_mensualidad')
def obtener_mensualidad(mensualidad_id: int) -> JsonResponse:
    """Obtiene una mensualidad específica aplicando restricciones de rol."""
    mensualidad = Mensualidad.query.get(mensualidad_id)
    if not mensualidad:
        return jsonify({'success': False, 'error': ERROR_MENSUALIDAD_NO_ENCONTRADA}), 404

    user = get_current_user()
    if has_role('Deportista') and user and user.get('persona'):
        if mensualidad.id_persona != user['persona'].get('id_persona'):
            return jsonify({'success': False, 'error': ERROR_NO_AUTORIZADO}), 403

    if has_role('Acudiente'):
        persona_id_param = request.args.get('persona_id', type=int)
        if persona_id_param and mensualidad.id_persona != persona_id_param:
            return jsonify({'success': False, 'error': ERROR_NO_AUTORIZADO}), 403

    data = _serializar_mensualidad(mensualidad)
    return jsonify({'success': True, 'data': data}), 200


@mensualidades_bp.post('/')
@permission_required('crear_mensualidad')
def crear_mensualidad() -> JsonResponse:
    """Crea una nueva mensualidad validando reglas de negocio."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_JSON_CONTENT,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        id_persona, _ = _resolver_persona_para_creacion(data)
        is_pagado_inicial = _obtener_estado_inicial(data)
        id_metodo_pago = _obtener_metodo_pago(data)
        monto_pago = _obtener_monto_pago(data)
        fecha_vencimiento = _obtener_fecha_vencimiento(data)
        saldo_inicial = _calcular_saldo_inicial(data, monto_pago, is_pagado_inicial)

        _validar_mensualidad_duplicada(id_persona, fecha_vencimiento)

        mensualidad = Mensualidad(
            id_persona=id_persona,
            id_metodo_pago=id_metodo_pago,
            monto_pago=monto_pago,
            estado=is_pagado_inicial,
            fecha_pago=date.today() if is_pagado_inicial else None,
            saldo_pendiente=saldo_inicial,
            fecha_vencimiento=fecha_vencimiento,
            activo=True,
        )

        db.session.add(mensualidad)
        db.session.flush()

        if is_pagado_inicial:
            _registrar_abono_inicial(mensualidad, monto_pago, id_metodo_pago)

        db.session.commit()
        data_resp = _adjuntar_info_persona_dict(mensualidad, mensualidad.to_dict())
        return jsonify({'success': True, 'data': data_resp}), 201
    except RequestValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error creando mensualidad: %s", str(exc))
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500

# Evitar redirecciones en POST sin barra final
@mensualidades_bp.route('', methods=['POST'])
@permission_required('crear_mensualidad')
def crear_mensualidad_sin_slash() -> JsonResponse:
    """Alias sin barra final para la creación de mensualidades."""
    return crear_mensualidad()


@mensualidades_bp.put('/<int:mensualidad_id>')
@permission_required('editar_mensualidad')
def actualizar_mensualidad(mensualidad_id: int) -> JsonResponse:
    """Actualiza una mensualidad existente aplicando validaciones de negocio."""
    try:
        mensualidad = Mensualidad.query.get(mensualidad_id)
        if not mensualidad:
            return jsonify({'success': False, 'error': ERROR_MENSUALIDAD_NO_ENCONTRADA}), 404

        data = request.get_json(silent=True) or {}
        numero_documento_actualizado = _procesar_cambio_documento(mensualidad, data)

        if 'id_metodo_pago' in data:
            _actualizar_metodo_pago_campo(mensualidad, data['id_metodo_pago'])

        if 'monto_pago' in data:
            _actualizar_monto_pago_campo(mensualidad, data['monto_pago'])

        if 'fecha_vencimiento' in data:
            _actualizar_fecha_vencimiento_campo(mensualidad, data['fecha_vencimiento'])

        if 'saldo_pendiente' in data:
            _actualizar_saldo_pendiente_campo(mensualidad, data['saldo_pendiente'])

        if 'activo' in data:
            _actualizar_activo_campo(mensualidad, data['activo'])

        if not mensualidad.fecha_vencimiento:
            raise RequestValidationError(ERROR_FECHA_VENCIMIENTO_REQUERIDA, status_code=400)

        _validar_mensualidad_duplicada(
            mensualidad.id_persona,
            mensualidad.fecha_vencimiento,
            mensualidad_id=mensualidad_id
        )

        _actualizar_estado_y_fecha_pago(mensualidad)

        db.session.commit()
        data_resp = _adjuntar_info_persona_dict(mensualidad, mensualidad.to_dict())
        if numero_documento_actualizado is not None:
            data_resp['numero_documento'] = numero_documento_actualizado
        return jsonify({'success': True, 'data': data_resp}), 200
    except RequestValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error actualizando mensualidad: %s", str(exc))
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500


@mensualidades_bp.patch('/<int:mensualidad_id>/desactivar')
@cross_origin(methods=['PATCH', 'OPTIONS'])
@permission_required('desactivar_mensualidad')
def desactivar_mensualidad(mensualidad_id: int) -> JsonResponse:
    """Desactiva una mensualidad específica."""
    mensualidad = Mensualidad.query.get(mensualidad_id)
    if not mensualidad:
        return jsonify({'success': False, 'error': ERROR_MENSUALIDAD_NO_ENCONTRADA}), 404

    mensualidad.activo = False
    db.session.commit()
    return jsonify({'success': True, 'data': mensualidad.to_dict()}), 200


@mensualidades_bp.patch('/<int:mensualidad_id>/reactivar')
@cross_origin(methods=['PATCH', 'OPTIONS'])
@permission_required('reactivar_mensualidad')
def reactivar_mensualidad(mensualidad_id: int) -> JsonResponse:
    """Reactiva una mensualidad previamente deshabilitada."""
    mensualidad = Mensualidad.query.get(mensualidad_id)
    if not mensualidad:
        return jsonify({'success': False, 'error': ERROR_MENSUALIDAD_NO_ENCONTRADA}), 404

    mensualidad.activo = True
    db.session.commit()
    return jsonify({'success': True, 'data': mensualidad.to_dict()}), 200


def _actualizar_abono_monto(abono: AbonoMensualidad, valor: Any) -> None:
    """Actualiza el campo monto de un abono."""
    monto = _parse_decimal(valor)
    if monto is None or monto <= 0:
        raise RequestValidationError(ERROR_MONTO_ABONO, status_code=400)
    abono.monto = float(monto)


def _actualizar_abono_fecha(abono: AbonoMensualidad, valor: Any) -> None:
    """Actualiza la fecha del abono."""
    try:
        abono.fecha_abono = date.fromisoformat(str(valor))
    except ValueError as exc:
        raise RequestValidationError(ERROR_FECHA_ABONO, status_code=400) from exc


def _actualizar_abono_metodo(abono: AbonoMensualidad, valor: Any) -> None:
    """Actualiza el método de pago del abono."""
    if valor is None:
        abono.id_metodo_pago = None
        return
    try:
        abono.id_metodo_pago = int(valor)
    except (TypeError, ValueError) as exc:
        raise RequestValidationError(ERROR_METODO_NUMERICO, status_code=400) from exc


@mensualidades_bp.post('/<int:mensualidad_id>/abonar')
@permission_required('abonar_mensualidad')
def abonar_mensualidad(mensualidad_id: int) -> JsonResponse:
    """Registra un abono para una mensualidad existente."""
    try:
        mensualidad = Mensualidad.query.get(mensualidad_id)
        if not mensualidad:
            return jsonify({'success': False, 'error': ERROR_MENSUALIDAD_NO_ENCONTRADA}), 404

        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_JSON_CONTENT,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        monto_abonado = _obtener_monto_abonado(data)
        monto_base = _obtener_monto_base(mensualidad)
        saldo_actual = _obtener_saldo_actual(mensualidad, monto_base)

        if saldo_actual >= 0 and monto_abonado > saldo_actual + 1e-6:
            raise RequestValidationError(ERROR_MONTO_ABONADO_SUPERA, status_code=400)

        fecha_abono = _obtener_fecha_abono(data)
        id_metodo_pago = _obtener_id_metodo_pago_abono(data)

        meses_cubiertos, sobrante = _calcular_meses_y_sobrante(monto_abonado, monto_base)
        _actualizar_vencimiento_y_saldo_post_abono(
            mensualidad,
            monto_base,
            monto_abonado,
            meses_cubiertos,
            sobrante,
            saldo_actual,
        )

        abono = AbonoMensualidad(
            id_mensualidad=mensualidad_id,
            monto=monto_abonado,
            fecha_abono=fecha_abono,
            id_metodo_pago=id_metodo_pago
        )
        db.session.add(abono)

        _actualizar_estado_y_fecha_pago(mensualidad)

        db.session.commit()
        return jsonify({
            'success': True,
            'data': mensualidad.to_dict(),
            'meses_cubiertos': meses_cubiertos,
            'sobrante': sobrante,
            'abono': abono.to_dict()
        }), 200
    except RequestValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except ValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error abonando mensualidad: %s", str(exc))
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500
@mensualidades_bp.get('/<int:mensualidad_id>/abonos')
@permission_required('ver_mensualidad')
def listar_abonos(mensualidad_id: int) -> JsonResponse:
    """Lista los abonos registrados para una mensualidad."""
    try:
        abonos = (
            AbonoMensualidad.query
            .filter_by(id_mensualidad=mensualidad_id)
            .order_by(AbonoMensualidad.id_abono.desc())
            .all()
        )
        mensualidad = Mensualidad.query.get(mensualidad_id)
        fecha_pago = getattr(mensualidad, 'fecha_pago', None)
        fecha_pago_iso = fecha_pago.isoformat() if fecha_pago else None

        data: List[Dict[str, Any]] = []
        for abono in abonos:
            registro = abono.to_dict()
            registro['es_pago_final'] = bool(fecha_pago_iso and registro.get('fecha_abono') == fecha_pago_iso)
            data.append(registro)

        if (
            mensualidad
            and mensualidad.estado
            and fecha_pago_iso
            and not any(item.get('fecha_abono') == fecha_pago_iso for item in data)
        ):
            try:
                data.append({
                    'id_abono': None,
                    'id_mensualidad': mensualidad_id,
                    'monto': float(mensualidad.monto_pago) if mensualidad.monto_pago is not None else 0,
                    'fecha_abono': fecha_pago_iso,
                    'id_metodo_pago': mensualidad.id_metodo_pago,
                    'es_pago_final': True,
                })
            except Exception:
                pass

        return jsonify({'success': True, 'data': data}), 200
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error listando abonos: %s", str(exc))
        return jsonify({'success': False, 'error': str(exc)}), 500


@mensualidades_bp.put('/<int:mensualidad_id>/abonos/<int:abono_id>')
@permission_required('editar_abono_mensualidad')
def actualizar_abono(mensualidad_id: int, abono_id: int) -> JsonResponse:
    """Actualiza un abono específico."""
    try:
        abono = AbonoMensualidad.query.get(abono_id)
        if not abono or abono.id_mensualidad != mensualidad_id:
            return jsonify({'success': False, 'error': ERROR_ID_ABONO}), 404

        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_JSON_CONTENT,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        if 'monto' in data:
            _actualizar_abono_monto(abono, data['monto'])

        if 'fecha_abono' in data:
            _actualizar_abono_fecha(abono, data['fecha_abono'])

        if 'id_metodo_pago' in data:
            _actualizar_abono_metodo(abono, data['id_metodo_pago'])

        mensualidad = Mensualidad.query.get(mensualidad_id)
        if mensualidad:
            _recalcular_estado_mensualidad(mensualidad)

        db.session.commit()
        return jsonify({'success': True, 'data': abono.to_dict()}), 200
    except RequestValidationError as exc:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), exc.status_code
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error actualizando abono: %s", str(exc))
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500


@mensualidades_bp.delete('/<int:mensualidad_id>/abonos/<int:abono_id>')
@permission_required('eliminar_abono_mensualidad')
def eliminar_abono(mensualidad_id: int, abono_id: int) -> JsonResponse:
    """Elimina un abono existente y recalcula el estado de la mensualidad."""
    try:
        abono = AbonoMensualidad.query.get(abono_id)
        if not abono or abono.id_mensualidad != mensualidad_id:
            return jsonify({'success': False, 'error': ERROR_ID_ABONO}), 404

        db.session.delete(abono)
        mensualidad = Mensualidad.query.get(mensualidad_id)
        if mensualidad:
            _recalcular_estado_mensualidad(mensualidad)

        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error eliminando abono: %s", str(exc))
        db.session.rollback()
        return jsonify({'success': False, 'error': str(exc)}), 500


def registrar_mensualidades_routes(app: Flask) -> None:
    """Registra las rutas de mensualidades en la aplicación Flask."""
    app.register_blueprint(mensualidades_bp)
    logger.info("Rutas de mensualidades registradas exitosamente")



