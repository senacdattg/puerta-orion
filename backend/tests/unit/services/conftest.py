"""
Fixtures compartidas para tests de servicios.

Este módulo contiene fixtures que se pueden usar en todos los tests
de servicios, incluyendo contexto de Flask y mocks para Mercado Pago.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask


@pytest.fixture
def app_context():
    """Proporciona un contexto de aplicación Flask para los tests."""
    from app import create_app
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test_secret_key'  # nosonar: S2068, S6418 - Test secret only, never used in production
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    
    with app.app_context():
        yield app


@pytest.fixture
def mock_env_vars():
    """Mock para variables de entorno de Mercado Pago."""
    with patch.dict('os.environ', {
        'MERCADOPAGO_ACCESS_TOKEN': 'test_access_token',  # nosonar: S2068, S6418 - Test token only, never used in production
        'MERCADOPAGO_PUBLIC_KEY': 'test_public_key',  # nosonar: S2068, S6418 - Test key only, never used in production
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

