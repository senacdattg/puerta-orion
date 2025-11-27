"""
Tests para la inicialización del servicio de Mercado Pago.

Este módulo contiene tests que verifican la correcta inicialización
del servicio con diferentes configuraciones de credenciales.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestMercadoPagoServiceInit:
    """Tests para la inicialización del servicio."""
    
    def test_init_with_credentials(self, mock_env_vars):
        """Test: Inicialización con credenciales válidas."""
        with patch('src.services.mercadopago_service.mercadopago.SDK') as mock_sdk_class:
            mock_sdk_instance = MagicMock()
            mock_sdk_class.return_value = mock_sdk_instance
            
            service = MercadoPagoService()
            
            assert service.access_token == 'test_access_token'
            assert service.public_key == 'test_public_key'
            assert service.environment == 'sandbox'
            assert service.sdk == mock_sdk_instance
    
    def test_init_without_credentials(self):
        """Test: Inicialización sin credenciales."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            
            assert service.access_token is None
            assert service.public_key is None
            assert service.sdk is None
    
    def test_init_with_default_environment(self):
        """Test: Inicialización con ambiente por defecto."""
        with patch.dict('os.environ', {
            'MERCADOPAGO_ACCESS_TOKEN': 'test_token',
            'MERCADOPAGO_PUBLIC_KEY': 'test_key'
        }):
            with patch('src.services.mercadopago_service.mercadopago.SDK'):
                service = MercadoPagoService()
                assert service.environment == 'sandbox'

