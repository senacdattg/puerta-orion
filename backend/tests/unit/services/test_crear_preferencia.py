"""
Tests para crear preferencias de pago en Mercado Pago.

Este módulo contiene tests que verifican la creación de preferencias
de pago, incluyendo casos exitosos y de error.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestCrearPreferencia:
    """Tests para crear preferencia de pago."""
    
    def test_crear_preferencia_success(self, mercado_pago_service, mock_sdk):
        """Test: Crear preferencia exitosamente."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        datos_pago = {
            'titulo': 'Pago Test',
            'monto': 100.0,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@test.com',
            'tipo_documento': 'CC',
            'numero_documento': '12345678',
            'referencia_externa': 'TEST_123',
            'tipo_pago': 'cuota',
            'id_cuota': 1
        }
        
        mock_response = {
            'status': 201,
            'response': {
                'id': 'pref_123',
                'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_123',
                'external_reference': 'TEST_123'
            }
        }
        mock_preference.create.return_value = mock_response
        
        with patch('src.services.mercadopago_service.TransaccionMercadoPago') as mock_transaccion:
            with patch('src.services.mercadopago_service.db') as mock_db:
                mock_transaccion.crear_transaccion.return_value = MagicMock()
                
                result = mercado_pago_service.crear_preferencia(datos_pago)
                
                assert result['success'] is True
                assert result['preference_id'] == 'pref_123'
                assert 'init_point' in result
    
    def test_crear_preferencia_sin_sdk(self):
        """Test: Error cuando SDK no está configurado."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            result = service.crear_preferencia({})
            
            assert result['success'] is False
            assert 'no configurado' in result['error']
    
    def test_crear_preferencia_error_api(self, mercado_pago_service, mock_sdk):
        """Test: Error cuando la API de Mercado Pago falla."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_response = {
            'status': 400,
            'response': {'error': 'Invalid data'}
        }
        mock_preference.create.return_value = mock_response
        
        result = mercado_pago_service.crear_preferencia({'monto': 100.0})
        
        assert result['success'] is False
    
    def test_crear_preferencia_excepcion(self, mercado_pago_service, mock_sdk):
        """Test: Manejo de excepciones al crear preferencia."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_preference.create.side_effect = Exception('Error de conexión')
        
        with patch('src.services.mercadopago_service.db') as mock_db:
            mock_db.session.rollback = MagicMock()
            result = mercado_pago_service.crear_preferencia({'monto': 100.0})
            
            assert result['success'] is False
            assert 'error' in result

