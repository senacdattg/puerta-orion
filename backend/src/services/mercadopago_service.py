"""
Servicio para manejar integración con Mercado Pago.
Maneja la creación de preferencias, verificación de pagos y webhooks.
"""

import os
import mercadopago
from decimal import Decimal
from datetime import datetime
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
            raise ValueError("Credenciales de Mercado Pago no configuradas")
        
        # Inicializar SDK de Mercado Pago
        self.sdk = mercadopago.SDK(self.access_token)
        
        logger.info(f"MercadoPagoService inicializado en modo: {self.environment}")
    
    def crear_preferencia(self, datos_pago: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una preferencia de pago en Mercado Pago.
        
        Args:
            datos_pago (dict): Datos del pago incluyendo monto, descripción, etc.
            
        Returns:
            dict: Respuesta de Mercado Pago con la preferencia creada.
        """
        try:
            # Estructurar la preferencia según la API de Mercado Pago
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
                    "success": datos_pago.get('url_exito', 'http://localhost:3000/pago-exitoso'),
                    "failure": datos_pago.get('url_fallo', 'http://localhost:3000/pago-fallido'),
                    "pending": datos_pago.get('url_pendiente', 'http://localhost:3000/pago-pendiente')
                },
                "auto_return": "approved",
                "external_reference": datos_pago.get('referencia_externa', ''),
                "notification_url": datos_pago.get('url_notificacion', ''),
                "metadata": {
                    "tipo_pago": datos_pago.get('tipo_pago', ''),
                    "id_cuota": datos_pago.get('id_cuota'),
                    "id_mensualidad": datos_pago.get('id_mensualidad')
                }
            }
            
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
    
    def procesar_webhook(self, datos_webhook: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa notificaciones webhook de Mercado Pago.
        
        Args:
            datos_webhook (dict): Datos recibidos del webhook.
            
        Returns:
            dict: Resultado del procesamiento.
        """
        try:
            # Obtener el ID del pago desde el webhook
            if datos_webhook.get("type") == "payment":
                payment_id = datos_webhook.get("data", {}).get("id")
                
                if payment_id:
                    # Verificar el pago
                    resultado = self.verificar_pago(payment_id)
                    
                    if resultado["success"]:
                        logger.info(f"Webhook procesado exitosamente: {payment_id}")
                        return {"success": True, "message": "Webhook procesado"}
                    
            return {"success": False, "message": "Tipo de webhook no reconocido"}
            
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
                "titulo": f"Pago Mensualidad - Categoría {mensualidad.categoria_obj.nombre if hasattr(mensualidad, 'categoria_obj') else 'Deportiva'}",
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
