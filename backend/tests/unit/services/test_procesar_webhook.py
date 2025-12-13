"""
Tests para procesar webhooks de Mercado Pago.

Este módulo contiene tests que verifican el procesamiento de webhooks
recibidos desde Mercado Pago.
"""

import pytest
from unittest.mock import patch
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestProcesarWebhook:
    """Tests para procesar webhooks de Mercado Pago."""
    
    def test_procesar_webhook_payment_type(self, mercado_pago_service):
        """Test: Procesar webhook de tipo payment."""
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        
        with patch.object(mercado_pago_service, '_procesar_webhook_pago', return_value={'success': True}):
            result = mercado_pago_service.procesar_webhook(datos_webhook)
            
            assert result['success'] is True
    
    def test_procesar_webhook_tipo_no_reconocido(self, mercado_pago_service):
        """Test: Webhook con tipo no reconocido."""
        datos_webhook = {
            'type': 'unknown',
            'data': {}
        }
        
        result = mercado_pago_service.procesar_webhook(datos_webhook)
        
        assert result['success'] is False
        assert 'no reconocido' in result['message']
    
    def test_procesar_webhook_excepcion(self, mercado_pago_service):
        """Test: Manejo de excepciones en webhook."""
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        
        with patch.object(mercado_pago_service, '_procesar_webhook_pago', side_effect=Exception('Error')):
            result = mercado_pago_service.procesar_webhook(datos_webhook)
            
            assert result['success'] is False

