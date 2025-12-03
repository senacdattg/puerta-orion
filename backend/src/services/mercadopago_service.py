"""
Servicio para manejar integración con Mercado Pago.
Maneja la creación de preferencias, verificación de pagos y webhooks.
"""

import os
import mercadopago
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any, Optional
from src.models.base import db
from src.models.pagos import TransaccionMercadoPago, MetodoPago
from src.utils.logger import logger


class MercadoPagoService:
    """
    Servicio para manejar integración con Mercado Pago.
    
    Proporciona métodos para crear preferencias de pago, verificar pagos,
    procesar webhooks y gestionar transacciones.
    """
    
    def __init__(self):
        """
        Inicializa el servicio con las credenciales de Mercado Pago.
        """
        self.access_token = os.getenv('MERCADOPAGO_ACCESS_TOKEN')
        self.public_key = os.getenv('MERCADOPAGO_PUBLIC_KEY')
        self.environment = os.getenv('MERCADOPAGO_ENVIRONMENT', 'sandbox')
        
        if not self.access_token or not self.public_key:
            # No mostrar warning en modo testing ya que es esperado
            # Verificar múltiples formas de detectar modo testing
            is_testing = (
                os.getenv('FLASK_ENV') == 'testing' or 
                os.getenv('TESTING') == 'true' or
                os.getenv('PYTEST_CURRENT_TEST') is not None or
                'pytest' in os.getenv('_', '').lower()
            )
            if not is_testing:
                logger.warning("Credenciales de Mercado Pago no configuradas. Funcionalidad limitada.")
            self.sdk = None
            return
        
        # Inicializar SDK de Mercado Pago
        self.sdk = mercadopago.SDK(self.access_token)
        
        logger.info(f"MercadoPagoService inicializado en modo: {self.environment}")

    # Utilidad para sumar meses sin dependencias externas
    @staticmethod
    def _add_months(base: date, months: int) -> date:
        month = base.month - 1 + months
        year = base.year + month // 12
        month = month % 12 + 1
        # calcular día válido del mes destino
        max_days = [31,
                    29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        day = min(base.day, max_days)
        return date(year, month, day)

    @staticmethod
    def _aplicar_abono_mensualidad(mensualidad, monto_abonado: float) -> Dict[str, Any]:
        """Aplica la misma lógica de abono que el endpoint de mensualidades.
        Retorna datos de cálculo para logging/uso adicional.
        """
        from src.models.pagos.mensualidad import Mensualidad as MensualidadModel  # evitar ciclos

        monto_mensual = float(mensualidad.monto_pago)
        meses_cubiertos = int(monto_abonado // monto_mensual)
        sobrante = monto_abonado - (meses_cubiertos * monto_mensual)

        if meses_cubiertos > 0:
            base = mensualidad.fecha_vencimiento if mensualidad.fecha_vencimiento and mensualidad.fecha_vencimiento > date.today() else date.today()
            mensualidad.fecha_vencimiento = MercadoPagoService._add_months(base, meses_cubiertos)

        if meses_cubiertos >= 1:
            mensualidad.saldo_pendiente = monto_mensual - sobrante if sobrante > 0 else 0
        else:
            mensualidad.saldo_pendiente = max(0, float(mensualidad.saldo_pendiente) - sobrante)

        if mensualidad.saldo_pendiente == 0:
            mensualidad.estado = True
            mensualidad.fecha_pago = date.today()
        else:
            mensualidad.estado = False
            mensualidad.fecha_pago = None

        return {
            'meses_cubiertos': meses_cubiertos,
            'sobrante': sobrante,
            'nuevo_saldo_pendiente': float(mensualidad.saldo_pendiente),
            'nueva_fecha_vencimiento': mensualidad.fecha_vencimiento.isoformat() if mensualidad.fecha_vencimiento else None,
            'estado': mensualidad.estado
        }
    
    def crear_preferencia(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una preferencia de pago en Mercado Pago.
        
        Args:
            datos_pago (dict): Datos del pago incluyendo monto, descripción, etc.
            
        Returns:
            dict: Respuesta de Mercado Pago con la preferencia creada.
        """
        if not self.sdk:
            return {"success": False, "error": "Servicio de Mercado Pago no configurado"}
            
        try:
            # Estructurar la preferencia según la API de Mercado Pago
            # Construir back_urls con defaults
            success_url = datos_pago.get('url_exito', 'http://localhost:5173/pago-exitoso')
            failure_url = datos_pago.get('url_fallo', 'http://localhost:5173/pago-fallido')
            pending_url = datos_pago.get('url_pendiente', 'http://localhost:5173/pago-pendiente')

            preference_data = {
                "items": [
                    {
                        "title": datos_pago.get('titulo', 'Pago Club Deportivo'),
                        "quantity": 1,
                        "unit_price": float(datos_pago.get('monto', 0)),
                        "currency_id": "COP"
                    }
                ],
                "payer": {
                    "name": datos_pago.get('nombre_pagador', ''),
                    "email": datos_pago.get('email_pagador', ''),
                    "identification": {
                        "type": datos_pago.get('tipo_documento', 'CC'),
                        "number": datos_pago.get('numero_documento', '')
                    }
                },
                "back_urls": {
                    "success": success_url,
                    "failure": failure_url,
                    "pending": pending_url
                },
                "external_reference": datos_pago.get('referencia_externa', ''),
                "notification_url": datos_pago.get('url_notificacion', ''),
                "metadata": {
                    "tipo_pago": datos_pago.get('tipo_pago', ''),
                    "id_cuota": datos_pago.get('id_cuota'),
                    "id_mensualidad": datos_pago.get('id_mensualidad')
                }
            }

            # En ambientes locales sin HTTPS, Mercado Pago puede rechazar auto_return
            try:
                if all(url.startswith('https://') for url in [success_url, failure_url, pending_url]):
                    preference_data["auto_return"] = "approved"
            except Exception:
                pass
            
            # Crear la preferencia
            result = self.sdk.preference().create(preference_data)
            
            if result["status"] == 201:
                preference = result["response"]
                
                # Guardar transacción en base de datos
                transaccion = TransaccionMercadoPago.crear_transaccion(
                    id_pago_mp=preference["id"],
                    preference_id=preference["id"],
                    monto=Decimal(str(datos_pago.get('monto', 0))),
                    estado='pending',
                    datos_pago=preference,
                    id_cuota=datos_pago.get('id_cuota'),
                    id_mensualidad=datos_pago.get('id_mensualidad')
                )
                
                db.session.add(transaccion)
                db.session.commit()
                
                logger.info(f"Preferencia creada exitosamente: {preference['id']}")
                
                return {
                    "success": True,
                    "preference_id": preference["id"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference.get("sandbox_init_point"),
                    "external_reference": preference["external_reference"]
                }
            else:
                logger.error(f"Error al crear preferencia: {result}")
                return {"success": False, "error": result}
                
        except Exception as e:
            logger.error(f"Error en crear_preferencia: {str(e)}")
            db.session.rollback()
            return {"success": False, "error": str(e)}
    
    def verificar_pago(self, payment_id: str) -> Dict[str, Any]:
        """
        Verifica el estado de un pago en Mercado Pago.
        
        Args:
            payment_id (str): ID del pago en Mercado Pago.
            
        Returns:
            dict: Información del pago y su estado.
        """
        if not self.sdk:
            return {"success": False, "error": "Servicio de Mercado Pago no configurado"}
            
        try:
            # Buscar el pago en Mercado Pago
            result = self.sdk.payment().get(payment_id)
            
            if result["status"] == 200:
                payment = result["response"]
                
                # Buscar la transacción en nuestra base de datos
                transaccion = TransaccionMercadoPago.query.filter_by(
                    id_pago_mercadopago=payment_id
                ).first()
                
                if transaccion:
                    # Actualizar el estado de la transacción
                    nuevo_estado = payment["status"]
                    transaccion.actualizar_estado(nuevo_estado, payment)
                    db.session.commit()
                    
                    logger.info(f"Pago verificado: {payment_id} - Estado: {nuevo_estado}")
                
                return {
                    "success": True,
                    "payment": payment,
                    "estado": payment["status"],
                    "monto": payment["transaction_amount"],
                    "moneda": payment["currency_id"]
                }
            else:
                logger.error(f"Error al verificar pago: {result}")
                return {"success": False, "error": result}
                
        except Exception as e:
            logger.error(f"Error en verificar_pago: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extraer_payment_id(self, datos_webhook: Dict[str, Any]) -> Optional[str]:
        """Extrae el ID del pago desde el webhook."""
        if datos_webhook.get("type") == "payment":
            return datos_webhook.get("data", {}).get("id")
        return None

    def _obtener_fecha_abono(self, payment: Dict[str, Any]) -> date:
        """Obtiene la fecha del abono desde el pago de Mercado Pago."""
        fecha_mp = payment.get('date_approved') or payment.get('date_created')
        if isinstance(fecha_mp, str):
            try:
                return datetime.fromisoformat(fecha_mp.replace('Z', '+00:00')).date()
            except Exception:
                pass
        return date.today()

    def _obtener_metadata_pago(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae y normaliza los metadatos del pago."""
        if isinstance(payment, dict):
            return payment.get('metadata', {})
        return {}

    def _crear_abono_mensualidad(self, mensualidad, monto_abonado: float, fecha_abono: date) -> None:
        """Crea y registra un abono de mensualidad."""
        from src.models.pagos.abono_mensualidad import AbonoMensualidad
        
        metodo_mp = self.obtener_metodo_pago_mercadopago()
        id_metodo_pago = getattr(metodo_mp, 'id_metodo_pago', None)

        abono = AbonoMensualidad(
            id_mensualidad=mensualidad.id_mensualidad,
            monto=monto_abonado,
            fecha_abono=fecha_abono,
            id_metodo_pago=id_metodo_pago
        )
        db.session.add(abono)

    def _procesar_pago_mensualidad(self, payment: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """Procesa un pago de mensualidad aprobado."""
        from src.models.pagos.mensualidad import Mensualidad
        
        mensualidad = Mensualidad.query.get(int(metadata['id_mensualidad']))
        if not mensualidad:
            return
        
        monto_abonado = float(payment.get('transaction_amount', 0))
        fecha_abono = self._obtener_fecha_abono(payment)
        
        self._crear_abono_mensualidad(mensualidad, monto_abonado, fecha_abono)
        calculo = self._aplicar_abono_mensualidad(mensualidad, monto_abonado)
        db.session.commit()
        logger.info(f"Mensualidad {mensualidad.id_mensualidad} actualizada por webhook MP: {calculo}")

    def _es_pago_mensualidad_aprobado(self, estado: str, metadata: Dict[str, Any]) -> bool:
        """Verifica si es un pago de mensualidad aprobado."""
        if estado != 'approved':
            return False
        if metadata.get('tipo_pago') != 'mensualidad':
            return False
        return bool(metadata.get('id_mensualidad'))

    def _procesar_webhook_pago(self, payment_id: str) -> Dict[str, Any]:
        """Procesa un webhook de tipo pago."""
        resultado = self.verificar_pago(payment_id)
        if not resultado["success"]:
            return {"success": False, "message": "Error al verificar pago"}
        
        payment = resultado.get("payment", {})
        estado = resultado.get("estado")
        metadata = self._obtener_metadata_pago(payment)

        if self._es_pago_mensualidad_aprobado(estado, metadata):
            try:
                self._procesar_pago_mensualidad(payment, metadata)
            except Exception as ex:
                logger.error(f"Error aplicando abono de mensualidad por webhook: {str(ex)}")
                db.session.rollback()
        
        logger.info(f"Webhook procesado exitosamente: {payment_id}")
        return {"success": True, "message": "Webhook procesado"}

    def procesar_webhook(self, datos_webhook: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa notificaciones webhook de Mercado Pago.
        
        Args:
            datos_webhook (dict): Datos recibidos del webhook.
            
        Returns:
            dict: Resultado del procesamiento.
        """
        try:
            payment_id = self._extraer_payment_id(datos_webhook)
            if not payment_id:
                return {"success": False, "message": "Tipo de webhook no reconocido"}
            
            return self._procesar_webhook_pago(payment_id)
            
        except Exception as e:
            logger.error(f"Error en procesar_webhook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def obtener_metodo_pago_mercadopago(self) -> Optional[MetodoPago]:
        """
        Obtiene el método de pago de Mercado Pago desde la base de datos.
        
        Returns:
            MetodoPago: Instancia del método de pago o None si no existe.
        """
        return MetodoPago.query.filter_by(nombre_metodo='Mercado Pago').first()
    
    def crear_pago_cuota(self, id_cuota: int, datos_pagador: Dict[str, Any], monto_pago: float = None) -> Dict[str, Any]:
        """
        Crea un pago para una cuota específica.
        
        Args:
            id_cuota (int): ID de la cuota a pagar.
            datos_pagador (dict): Datos del pagador.
            monto_pago (float): Monto específico a pagar (opcional, por defecto usa el monto total).
            
        Returns:
            dict: Resultado de la creación del pago.
        """
        try:
            from src.models.pagos import Cuota
            
            # Buscar la cuota
            cuota = Cuota.query.get(id_cuota)
            if not cuota:
                return {"success": False, "error": "Cuota no encontrada"}
            
            # Calcular saldo pendiente
            saldo_pendiente = cuota.calcular_saldo_pendiente()
            
            # Si no se especifica monto, usar el saldo pendiente
            if monto_pago is None:
                monto_pago = saldo_pendiente
            
            # Validar que el monto no exceda el saldo pendiente
            if float(monto_pago) > saldo_pendiente:
                return {
                    "success": False, 
                    "error": f"El monto excede el saldo pendiente. Saldo disponible: ${saldo_pendiente:,.2f}"
                }
            
            # Si es el primer pago, inicializar saldo pendiente
            if cuota.saldo_pendiente is None:
                cuota.saldo_pendiente = float(cuota.monto_cuota)
                cuota.actualizar_saldo_pendiente()
            
            # Preparar datos para la preferencia
            datos_pago = {
                "titulo": f"Pago Cuota #{id_cuota} - ${monto_pago:,.2f}",
                "monto": float(monto_pago),
                "tipo_pago": "cuota",
                "id_cuota": id_cuota,
                "referencia_externa": f"CUOTA_{id_cuota}",
                "saldo_pendiente": saldo_pendiente,
                "monto_total": float(cuota.monto_cuota),
                **datos_pagador
            }
            
            return self.crear_preferencia(datos_pago)
            
        except Exception as e:
            logger.error(f"Error en crear_pago_cuota: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def crear_pago_mensualidad(self, id_mensualidad: int, datos_pagador: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un pago para una mensualidad específica.
        
        Args:
            id_mensualidad (int): ID de la mensualidad a pagar.
            datos_pagador (dict): Datos del pagador.
            
        Returns:
            dict: Resultado de la creación del pago.
        """
        try:
            from src.models.pagos import Mensualidad
            
            # Buscar la mensualidad
            mensualidad = Mensualidad.query.get(id_mensualidad)
            if not mensualidad:
                return {"success": False, "error": "Mensualidad no encontrada"}
            
            # Preparar datos para la preferencia
            datos_pago = {
                "titulo": (
                    f"Pago Mensualidad - {getattr(getattr(mensualidad, 'persona', None), 'nombre', None) or 'Persona'}"
                ),
                "monto": float(mensualidad.monto_pago),
                "tipo_pago": "mensualidad",
                "id_mensualidad": id_mensualidad,
                "referencia_externa": f"MENS_{id_mensualidad}",
                **datos_pagador
            }
            
            return self.crear_preferencia(datos_pago)
            
        except Exception as e:
            logger.error(f"Error en crear_pago_mensualidad: {str(e)}")
            return {"success": False, "error": str(e)}
