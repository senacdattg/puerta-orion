"""
Fixtures compartidas para tests del servicio de Mercado Pago.

Este módulo contiene fixtures que se pueden usar en todos los tests
del servicio de Mercado Pago.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_env_vars():
    """Mock para variables de entorno de Mercado Pago."""
    with patch.dict('os.environ', {
        'MERCADOPAGO_ACCESS_TOKEN': 'test_access_token',
        'MERCADOPAGO_PUBLIC_KEY': 'test_public_key',
        'MERCADOPAGO_ENVIRONMENT': 'sandbox'
    }):
        yield


@pytest.fixture
def mock_sdk():
    """Mock para el SDK de Mercado Pago."""
    mock_sdk_instance = MagicMock()
    mock_preference = MagicMock()
    mock_payment = MagicMock()
    
    mock_sdk_instance.preference.return_value = mock_preference
    mock_sdk_instance.payment.return_value = mock_payment
    
    return mock_sdk_instance, mock_preference, mock_payment


@pytest.fixture
def mercado_pago_service(mock_env_vars):
    """Crea una instancia del servicio de Mercado Pago."""
    with patch('src.services.mercadopago_service.mercadopago.SDK') as mock_sdk_class:
        mock_sdk_instance = MagicMock()
        mock_sdk_class.return_value = mock_sdk_instance
        from src.services.mercadopago_service import MercadoPagoService
        service = MercadoPagoService()
        service.sdk = mock_sdk_instance
        return service

