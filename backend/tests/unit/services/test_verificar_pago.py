"""
Tests para verificar el estado de pagos en Mercado Pago.

Este módulo contiene tests que verifican la consulta del estado
de pagos en Mercado Pago.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestVerificarPago:
    """Tests para verificar estado de pago."""
    
    def test_verificar_pago_success(self, mercado_pago_service, mock_sdk):
        """Test: Verificar pago exitosamente."""
        mock_sdk_instance, _, mock_payment = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        payment_id = 'payment_123'
        mock_response = {
            'status': 200,
            'response': {
                'id': payment_id,
                'status': 'approved',
                'transaction_amount': 100.0,
                'currency_id': 'COP'
            }
        }
        mock_payment.get.return_value = mock_response
        
        with patch('src.services.mercadopago_service.TransaccionMercadoPago') as mock_transaccion:
            with patch('src.services.mercadopago_service.db') as mock_db:
                mock_transaccion_obj = MagicMock()
                mock_transaccion.query.filter_by.return_value.first.return_value = mock_transaccion_obj
                
                result = mercado_pago_service.verificar_pago(payment_id)
                
                assert result['success'] is True
                assert result['estado'] == 'approved'
                assert result['monto'] == pytest.approx(100.0)
    
    def test_verificar_pago_sin_sdk(self):
        """Test: Error cuando SDK no está configurado."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            result = service.verificar_pago('payment_123')
            
            assert result['success'] is False
    
    def test_verificar_pago_no_encontrado(self, mercado_pago_service, mock_sdk):
        """Test: Pago no encontrado en Mercado Pago."""
        mock_sdk_instance, _, mock_payment = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_response = {
            'status': 404,
            'response': {'error': 'Payment not found'}
        }
        mock_payment.get.return_value = mock_response
        
        result = mercado_pago_service.verificar_pago('payment_999')
        
        assert result['success'] is False

