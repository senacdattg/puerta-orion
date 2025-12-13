"""
Tests para el endpoint de webhook de Mercado Pago.

Endpoint: POST /api/mercadopago/webhook
Funcionalidad: Recibe notificaciones de Mercado Pago sobre cambios en pagos.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.pagos
class TestWebhookMercadoPago:
    """Tests para el endpoint POST /api/mercadopago/webhook"""
    
    def test_webhook_success(self, client):
        """Test: Procesar webhook exitosamente."""
        # Arrange
        datos_webhook = {
            'type': 'payment',
            'data': {
                'id': 'payment_123'
            }
        }
        mock_resultado = {
            'success': True,
            'message': 'Webhook procesado exitosamente'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.procesar_webhook',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'POST', '/api/mercadopago/webhook',
                data=datos_webhook
            )
        
        # Assert
        assert_success_response(response)
    
    def test_webhook_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/mercadopago/webhook', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_webhook_datos_vacios(self, client):
        """Test: Error cuando no se proporcionan datos."""
        # Arrange
        datos_vacios = {}
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/webhook',
            data=datos_vacios
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_webhook_error_servicio(self, client):
        """Test: Error del servicio al procesar webhook."""
        # Arrange
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        mock_resultado = {
            'success': False,
            'error': 'Error al procesar webhook'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.procesar_webhook',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'POST', '/api/mercadopago/webhook',
                data=datos_webhook
            )
        
        # Assert
        assert_error_response(response, expected_status=500)

