"""
Rutas para manejo de pagos con Mercado Pago.

Responsabilidad:
- Crear preferencias de pago y verificar transacciones.
- Gestionar webhooks y consultar estadísticas.

Se aplican principios SOLID, KISS y DRY.
"""

from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from flask import Blueprint, Flask, Response, current_app, jsonify, request
from sqlalchemy import func

from ..models.base import db
from ..models.pagos.cuota import Cuota
from ..models.pagos.transaccion_mercadopago import TransaccionMercadoPago
from ..services.mercadopago_service import MercadoPagoService
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido

pagos_bp = Blueprint('pagos', __name__)
logger = obtener_registrador('aplicacion')
mercadopago_service = MercadoPagoService()

DEFAULT_ORIGIN = 'http://localhost:5173'
DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0
MIN_LIMIT = 1
MIN_MONTO = 0

ERROR_SIN_DATOS = 'No se proporcionaron datos'
ERROR_TIPO_PAGO_REQUERIDO = 'Tipo de pago requerido'
ERROR_NOMBRE_REQUERIDO = 'Nombre del pagador requerido'
ERROR_EMAIL_REQUERIDO = 'Email del pagador requerido'
ERROR_TIPO_PAGO_INVALIDO = 'Tipo de pago no válido'
ERROR_ID_CUOTA_REQUERIDO = 'ID de cuota requerido'
ERROR_ID_MENSUALIDAD_REQUERIDO = 'ID de mensualidad requerido'
ERROR_MONTO_INVALIDO = 'El monto debe ser mayor a 0'
ERROR_ID_PAGO_REQUERIDO = 'ID de pago requerido'
ERROR_SIN_DATOS_WEBHOOK = 'No se recibieron datos'
ERROR_TRANSACCION_NO_ENCONTRADA = 'Transacción no encontrada'
ERROR_CUOTA_NO_ENCONTRADA = 'Cuota no encontrada'

JsonResponse = Tuple[Response, int]


def _validar_campos_requeridos(
    data: Dict[str, Any],
    campos: Iterable[Tuple[str, str]],
) -> None:
    """Valida que los campos requeridos existan y no estén vacíos."""
    for campo, mensaje in campos:
        if not data.get(campo):
            raise RequestValidationError(mensaje, status_code=400)


def _enriquecer_urls(data: Dict[str, Any]) -> None:
    """Completa datos con URLs requeridas por Mercado Pago."""
    origin = request.headers.get('Origin') or DEFAULT_ORIGIN
    data.setdefault('url_exito', f"{origin}/pago-exitoso")
    data.setdefault('url_fallo', f"{origin}/pago-fallido")
    data.setdefault('url_pendiente', f"{origin}/pago-pendiente")

    host_url = request.host_url.rstrip('/')
    webhook_config = current_app.config.get('MERCADOPAGO_WEBHOOK_URL')
    data.setdefault('url_notificacion', webhook_config or f"{host_url}/api/mercadopago/webhook")


def _crear_preferencia_cuota(data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea la preferencia de pago para una cuota."""
    if not data.get('id_cuota'):
        raise RequestValidationError(ERROR_ID_CUOTA_REQUERIDO, status_code=400)

    monto_pago = data.get('monto')
    if monto_pago is not None and monto_pago <= MIN_MONTO:
        raise RequestValidationError(ERROR_MONTO_INVALIDO, status_code=400)

    return mercadopago_service.crear_pago_cuota(
        id_cuota=data['id_cuota'],
        datos_pagador=data,
        monto_pago=monto_pago,
    )


def _crear_preferencia_mensualidad(data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea la preferencia de pago para una mensualidad."""
    if not data.get('id_mensualidad'):
        raise RequestValidationError(ERROR_ID_MENSUALIDAD_REQUERIDO, status_code=400)

    return mercadopago_service.crear_pago_mensualidad(
        id_mensualidad=data['id_mensualidad'],
        datos_pagador=data,
    )


def _obtener_manejador_preferencia(tipo_pago: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Obtiene el manejador adecuado según el tipo de pago."""
    handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
        'cuota': _crear_preferencia_cuota,
        'mensualidad': _crear_preferencia_mensualidad,
    }
    try:
        return handlers[tipo_pago]
    except KeyError as exc:
        raise RequestValidationError(ERROR_TIPO_PAGO_INVALIDO, status_code=400) from exc


def _normalizar_paginacion(limit_param: Optional[int], offset_param: Optional[int]) -> Tuple[int, int]:
    """Normaliza los parámetros de paginación."""
    limit = max(MIN_LIMIT, limit_param or DEFAULT_LIMIT)
    offset = max(DEFAULT_OFFSET, offset_param or DEFAULT_OFFSET)
    return limit, offset


def _procesar_creacion_preferencia(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta el flujo de creación de preferencia."""
    _validar_campos_requeridos(
        data,
        (
            ('tipo_pago', ERROR_TIPO_PAGO_REQUERIDO),
            ('nombre_pagador', ERROR_NOMBRE_REQUERIDO),
            ('email_pagador', ERROR_EMAIL_REQUERIDO),
        ),
    )
    _enriquecer_urls(data)
    handler = _obtener_manejador_preferencia(data['tipo_pago'])
    return handler(data)


def _formatear_respuesta_preferencia(resultado: Dict[str, Any]) -> JsonResponse:
    """Genera la respuesta HTTP para la creación de preferencia."""
    if resultado.get('success'):
        logger.info("Preferencia creada exitosamente: %s", resultado.get('preference_id'))
        return jsonify(resultado), 200

    logger.error("Error al crear preferencia: %s", resultado.get('error'))
    return jsonify(resultado), 500


@pagos_bp.route('/mercadopago/crear-preferencia', methods=['POST'])
def crear_preferencia() -> JsonResponse:
    """Crea una preferencia de pago en Mercado Pago."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo='Content-Type debe ser application/json',
            mensaje_vacio=ERROR_SIN_DATOS,
        )
        resultado = _procesar_creacion_preferencia(data)
        return _formatear_respuesta_preferencia(resultado)

    except RequestValidationError as exc:
        logger.warning("Validación en crear_preferencia: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), exc.status_code
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en crear_preferencia endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/mercadopago/verificar-pago/<payment_id>', methods=['GET'])
def verificar_pago(payment_id: str) -> JsonResponse:
    """Verifica el estado de un pago en Mercado Pago."""
    try:
        if not payment_id:
            return jsonify({"success": False, "error": ERROR_ID_PAGO_REQUERIDO}), 400

        resultado = mercadopago_service.verificar_pago(payment_id)
        if resultado.get('success'):
            logger.info("Pago verificado: %s - Estado: %s", payment_id, resultado.get('estado'))
            return jsonify(resultado), 200

        logger.error("Error al verificar pago %s: %s", payment_id, resultado.get('error'))
        return jsonify(resultado), 500

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en verificar_pago endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/mercadopago/webhook', methods=['POST'])
def webhook_mercadopago() -> JsonResponse:
    """Procesa las notificaciones webhook de Mercado Pago."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo='Content-Type debe ser application/json',
            mensaje_vacio=ERROR_SIN_DATOS_WEBHOOK,
        )
        logger.info("Webhook recibido: %s", data)

        resultado = mercadopago_service.procesar_webhook(data)
        if resultado.get('success'):
            logger.info("Webhook procesado exitosamente")
            return jsonify(resultado), 200

        logger.error("Error al procesar webhook: %s", resultado.get('error'))
        return jsonify(resultado), 500

    except RequestValidationError as exc:
        logger.warning("Validación en webhook Mercado Pago: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), exc.status_code
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en webhook endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/mercadopago/transacciones', methods=['GET'])
def listar_transacciones() -> JsonResponse:
    """Lista transacciones registradas en Mercado Pago."""
    try:
        estado = request.args.get('estado')
        limit_param = request.args.get('limit', type=int)
        offset_param = request.args.get('offset', type=int)
        limit, offset = _normalizar_paginacion(limit_param, offset_param)

        query = TransaccionMercadoPago.query
        if estado:
            query = query.filter_by(estado=estado)

        transacciones = (
            query.order_by(TransaccionMercadoPago.fecha_creacion.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        transacciones_data = [transaccion.to_dict() for transaccion in transacciones]

        logger.info("Transacciones listadas: %s", len(transacciones_data))
        return jsonify({
            "success": True,
            "transacciones": transacciones_data,
            "total": len(transacciones_data)
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en listar_transacciones endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/mercadopago/transacciones/<int:transaccion_id>', methods=['GET'])
def obtener_transaccion(transaccion_id: int) -> JsonResponse:
    """Obtiene una transacción específica almacenada en la base de datos."""
    try:
        transaccion = TransaccionMercadoPago.query.get(transaccion_id)
        if not transaccion:
            return jsonify({"success": False, "error": ERROR_TRANSACCION_NO_ENCONTRADA}), 404

        logger.info("Transacción obtenida: %s", transaccion_id)
        return jsonify({
            "success": True,
            "transaccion": transaccion.to_dict()
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en obtener_transaccion endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/mercadopago/estadisticas', methods=['GET'])
def obtener_estadisticas() -> JsonResponse:
    """Obtiene estadísticas agregadas de las transacciones de Mercado Pago."""
    try:
        estadisticas = db.session.query(
            TransaccionMercadoPago.estado,
            func.count(TransaccionMercadoPago.id_transaccion).label('cantidad'),
            func.sum(TransaccionMercadoPago.monto).label('total_monto'),
        ).group_by(TransaccionMercadoPago.estado).all()

        stats_dict: Dict[str, Dict[str, Any]] = {}
        for estado, cantidad, total_monto in estadisticas:
            stats_dict[estado] = {
                "cantidad": cantidad,
                "total_monto": float(total_monto) if total_monto else 0,
            }

        logger.info("Estadísticas obtenidas exitosamente")
        return jsonify({
            "success": True,
            "estadisticas": stats_dict
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error en obtener_estadisticas endpoint: %s", str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


@pagos_bp.route('/cuota/<int:cuota_id>/saldo', methods=['GET'])
def consultar_saldo_cuota(cuota_id: int) -> JsonResponse:
    """Consulta el saldo pendiente de una cuota específica."""
    try:
        cuota = Cuota.query.get(cuota_id)
        if not cuota:
            return jsonify({
                'success': False,
                'error': ERROR_CUOTA_NO_ENCONTRADA
            }), 404

        saldo_pendiente = cuota.calcular_saldo_pendiente()
        monto_total = float(cuota.monto_cuota)
        pagado = monto_total - saldo_pendiente
        porcentaje_pagado = round(pagado / monto_total * 100, 2) if monto_total else 0

        return jsonify({
            'success': True,
            'data': {
                'cuota_id': cuota.id_cuota,
                'monto_total': monto_total,
                'saldo_pendiente': saldo_pendiente,
                'pagado': pagado,
                'porcentaje_pagado': porcentaje_pagado
            }
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error consultando saldo de cuota %s: %s", cuota_id, str(exc))
        return jsonify({"success": False, "error": str(exc)}), 500


def registrar_pagos_routes(app: Flask) -> None:
    """Registra las rutas de pagos en la aplicación Flask."""
    app.register_blueprint(pagos_bp)
    logger.info("Rutas de pagos registradas exitosamente")
