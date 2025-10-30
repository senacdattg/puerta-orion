"""
Rutas para manejo de pagos con Mercado Pago.
Proporciona endpoints para crear preferencias, verificar pagos y webhooks.
"""

from flask import Blueprint, request, jsonify
from src.services.mercadopago_service import MercadoPagoService
from src.models.base import db
from src.models.pagos import TransaccionMercadoPago
from src.utils.logger import logger

# Crear blueprint para las rutas de pagos
pagos_bp = Blueprint('pagos', __name__)

# Inicializar servicio de Mercado Pago
mercadopago_service = MercadoPagoService()


@pagos_bp.route('/mercadopago/crear-preferencia', methods=['POST'])
def crear_preferencia():
    """
    Endpoint para crear una preferencia de pago en Mercado Pago.
    
    Body JSON esperado:
    {
        "tipo_pago": "cuota" | "mensualidad",
        "id_cuota": 123 (opcional si tipo_pago = "cuota"),
        "id_mensualidad": 456 (opcional si tipo_pago = "mensualidad"),
        "nombre_pagador": "Juan Pérez",
        "email_pagador": "juan@email.com",
        "numero_documento": "12345678",
        "tipo_documento": "CC"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No se proporcionaron datos"}), 400
        
        # Validar datos requeridos
        if not data.get('tipo_pago'):
            return jsonify({"success": False, "error": "Tipo de pago requerido"}), 400
        
        if not data.get('nombre_pagador'):
            return jsonify({"success": False, "error": "Nombre del pagador requerido"}), 400
        
        if not data.get('email_pagador'):
            return jsonify({"success": False, "error": "Email del pagador requerido"}), 400
        
        # Enriquecer con URLs por defecto requeridas por Mercado Pago
        origin = request.headers.get('Origin') or 'http://localhost:5173'
        base_success = f"{origin}/pago-exitoso"
        base_failure = f"{origin}/pago-fallido"
        base_pending = f"{origin}/pago-pendiente"
        # back_urls obligatorias cuando se usa auto_return
        data.setdefault('url_exito', base_success)
        data.setdefault('url_fallo', base_failure)
        data.setdefault('url_pendiente', base_pending)
        # webhook por defecto
        try:
            from flask import current_app
            host_url = request.host_url.rstrip('/')
            data.setdefault('url_notificacion', current_app.config.get('MERCADOPAGO_WEBHOOK_URL') or f"{host_url}/api/mercadopago/webhook")
        except Exception:
            data.setdefault('url_notificacion', f"{request.host_url.rstrip('/')}/api/mercadopago/webhook")

        # Crear preferencia según el tipo de pago
        if data['tipo_pago'] == 'cuota':
            if not data.get('id_cuota'):
                return jsonify({"success": False, "error": "ID de cuota requerido"}), 400
            
            # Validar monto si se proporciona
            monto_pago = data.get('monto')
            if monto_pago and monto_pago <= 0:
                return jsonify({"success": False, "error": "El monto debe ser mayor a 0"}), 400
            
            resultado = mercadopago_service.crear_pago_cuota(
                id_cuota=data['id_cuota'],
                datos_pagador=data,
                monto_pago=monto_pago
            )
            
        elif data['tipo_pago'] == 'mensualidad':
            if not data.get('id_mensualidad'):
                return jsonify({"success": False, "error": "ID de mensualidad requerido"}), 400
            
            resultado = mercadopago_service.crear_pago_mensualidad(
                id_mensualidad=data['id_mensualidad'],
                datos_pagador=data
            )
        else:
            return jsonify({"success": False, "error": "Tipo de pago no válido"}), 400
        
        if resultado["success"]:
            logger.info(f"Preferencia creada exitosamente: {resultado.get('preference_id')}")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error al crear preferencia: {resultado.get('error')}")
            return jsonify(resultado), 500
            
    except Exception as e:
        logger.error(f"Error en crear_preferencia endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/mercadopago/verificar-pago/<payment_id>', methods=['GET'])
def verificar_pago(payment_id):
    """
    Endpoint para verificar el estado de un pago.
    
    Args:
        payment_id (str): ID del pago en Mercado Pago
    """
    try:
        if not payment_id:
            return jsonify({"success": False, "error": "ID de pago requerido"}), 400
        
        resultado = mercadopago_service.verificar_pago(payment_id)
        
        if resultado["success"]:
            logger.info(f"Pago verificado: {payment_id} - Estado: {resultado.get('estado')}")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error al verificar pago: {resultado.get('error')}")
            return jsonify(resultado), 500
            
    except Exception as e:
        logger.error(f"Error en verificar_pago endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/mercadopago/webhook', methods=['POST'])
def webhook_mercadopago():
    """
    Endpoint para recibir webhooks de Mercado Pago.
    Procesa notificaciones de cambios en el estado de pagos.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
        
        logger.info(f"Webhook recibido: {data}")
        
        # Procesar el webhook
        resultado = mercadopago_service.procesar_webhook(data)
        
        if resultado["success"]:
            logger.info("Webhook procesado exitosamente")
            return jsonify(resultado), 200
        else:
            logger.error(f"Error al procesar webhook: {resultado.get('error')}")
            return jsonify(resultado), 500
            
    except Exception as e:
        logger.error(f"Error en webhook endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/mercadopago/transacciones', methods=['GET'])
def listar_transacciones():
    """
    Endpoint para listar transacciones de Mercado Pago.
    
    Query parameters:
    - estado: Filtrar por estado (opcional)
    - limit: Límite de resultados (opcional, default: 50)
    - offset: Offset para paginación (opcional, default: 0)
    """
    try:
        estado = request.args.get('estado')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Construir consulta
        query = TransaccionMercadoPago.query
        
        if estado:
            query = query.filter_by(estado=estado)
        
        # Aplicar paginación y ordenar por fecha
        transacciones = query.order_by(
            TransaccionMercadoPago.fecha_creacion.desc()
        ).offset(offset).limit(limit).all()
        
        # Convertir a diccionarios
        transacciones_data = [transaccion.to_dict() for transaccion in transacciones]
        
        logger.info(f"Transacciones listadas: {len(transacciones_data)}")
        
        return jsonify({
            "success": True,
            "transacciones": transacciones_data,
            "total": len(transacciones_data)
        }), 200
        
    except Exception as e:
        logger.error(f"Error en listar_transacciones endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/mercadopago/transacciones/<int:transaccion_id>', methods=['GET'])
def obtener_transaccion(transaccion_id):
    """
    Endpoint para obtener una transacción específica.
    
    Args:
        transaccion_id (int): ID de la transacción en nuestra base de datos
    """
    try:
        transaccion = TransaccionMercadoPago.query.get(transaccion_id)
        
        if not transaccion:
            return jsonify({"success": False, "error": "Transacción no encontrada"}), 404
        
        logger.info(f"Transacción obtenida: {transaccion_id}")
        
        return jsonify({
            "success": True,
            "transaccion": transaccion.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_transaccion endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/mercadopago/estadisticas', methods=['GET'])
def obtener_estadisticas():
    """
    Endpoint para obtener estadísticas de pagos.
    """
    try:
        from sqlalchemy import func
        
        # Contar transacciones por estado
        estadisticas = db.session.query(
            TransaccionMercadoPago.estado,
            func.count(TransaccionMercadoPago.id_transaccion).label('cantidad'),
            func.sum(TransaccionMercadoPago.monto).label('total_monto')
        ).group_by(TransaccionMercadoPago.estado).all()
        
        # Convertir a diccionario
        stats_dict = {}
        for stat in estadisticas:
            stats_dict[stat.estado] = {
                "cantidad": stat.cantidad,
                "total_monto": float(stat.total_monto) if stat.total_monto else 0
            }
        
        logger.info("Estadísticas obtenidas exitosamente")
        
        return jsonify({
            "success": True,
            "estadisticas": stats_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error en obtener_estadisticas endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@pagos_bp.route('/cuota/<int:cuota_id>/saldo', methods=['GET'])
def consultar_saldo_cuota(cuota_id):
    """
    Consulta el saldo pendiente de una cuota específica.
    
    GET /api/cuota/{cuota_id}/saldo
    """
    try:
        from src.models.pagos.cuota import Cuota
        
        cuota = Cuota.query.get(cuota_id)
        if not cuota:
            return jsonify({
                'success': False,
                'error': 'Cuota no encontrada'
            }), 404
        
        # Calcular saldo pendiente
        saldo_pendiente = cuota.calcular_saldo_pendiente()
        
        return jsonify({
            'success': True,
            'data': {
                'cuota_id': cuota.id_cuota,
                'monto_total': float(cuota.monto_cuota),
                'saldo_pendiente': saldo_pendiente,
                'pagado': float(cuota.monto_cuota) - saldo_pendiente,
                'porcentaje_pagado': round((float(cuota.monto_cuota) - saldo_pendiente) / float(cuota.monto_cuota) * 100, 2)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error consultando saldo de cuota: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
