"""
Tests para el endpoint de verificación de pago.

Endpoint: GET /api/mercadopago/verificar-pago/<payment_id>
Funcionalidad: Verifica el estado de un pago en Mercado Pago.
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
class TestVerificarPago:
    """Tests para el endpoint GET /api/mercadopago/verificar-pago/<payment_id>"""
    
    def test_verificar_pago_success(self, client):
        """Test: Verificar pago exitosamente."""
        # Arrange
        payment_id = 'payment_123'
        mock_resultado = {
            'success': True,
            'estado': 'approved',
            'payment_id': payment_id
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.verificar_pago',
                   return_value=mock_resultado):
            response = client.get(f'/api/mercadopago/verificar-pago/{payment_id}')
        
        # Assert
        data = assert_success_response(response)
        assert data['estado'] == 'approved'
    
    def test_verificar_pago_sin_id(self, client):
        """Test: Error cuando no se proporciona ID de pago."""
        # Act
        response = client.get('/api/mercadopago/verificar-pago/')
        
        # Assert
        # Flask puede retornar 404 o 405 dependiendo de la configuración
        assert response.status_code in [404, 405]
    
    def test_verificar_pago_error_servicio(self, client):
        """Test: Error del servicio al verificar pago."""
        # Arrange
        payment_id = 'payment_999'
        mock_resultado = {
            'success': False,
            'error': 'Pago no encontrado'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.verificar_pago',
                   return_value=mock_resultado):
            response = client.get(f'/api/mercadopago/verificar-pago/{payment_id}')
        
        # Assert
        assert_error_response(response, expected_status=500)

