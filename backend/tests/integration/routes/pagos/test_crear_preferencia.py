"""
Tests para el endpoint de creación de preferencia de pago.

Endpoint: POST /api/mercadopago/crear-preferencia
Funcionalidad: Crea una preferencia de pago en Mercado Pago para cuotas o mensualidades.
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
class TestCrearPreferencia:
    """Tests para el endpoint POST /api/mercadopago/crear-preferencia"""
    
    def test_crear_preferencia_cuota_success(self, client):
        """Test: Crear preferencia de pago para cuota exitosamente."""
        # Arrange
        datos_pago = {
            'tipo_pago': 'cuota',
            'id_cuota': 1,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com',
            'monto': 50000.0
        }
        mock_resultado = {
            'success': True,
            'preference_id': 'pref_123',
            'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_123'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.crear_pago_cuota',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'POST', '/api/mercadopago/crear-preferencia',
                data=datos_pago
            )
        
        # Assert
        data = assert_success_response(response)
        assert 'preference_id' in data
    
    def test_crear_preferencia_mensualidad_success(self, client):
        """Test: Crear preferencia de pago para mensualidad exitosamente."""
        # Arrange
        datos_pago = {
            'tipo_pago': 'mensualidad',
            'id_mensualidad': 1,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        mock_resultado = {
            'success': True,
            'preference_id': 'pref_456',
            'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_456'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.crear_pago_mensualidad',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'POST', '/api/mercadopago/crear-preferencia',
                data=datos_pago
            )
        
        # Assert
        data = assert_success_response(response)
        assert 'preference_id' in data
    
    def test_crear_preferencia_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/mercadopago/crear-preferencia', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_datos_vacios(self, client):
        """Test: Error cuando no se proporcionan datos."""
        # Arrange
        datos_vacios = {}
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_vacios
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_sin_tipo_pago(self, client):
        """Test: Error cuando falta el tipo de pago."""
        # Arrange
        datos_sin_tipo = {
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_sin_tipo
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_tipo_invalido(self, client):
        """Test: Error cuando el tipo de pago es inválido."""
        # Arrange
        datos_tipo_invalido = {
            'tipo_pago': 'tipo_invalido',
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_tipo_invalido
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_cuota_sin_id(self, client):
        """Test: Error al crear preferencia de cuota sin ID."""
        # Arrange
        datos_sin_id = {
            'tipo_pago': 'cuota',
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_sin_id
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_mensualidad_sin_id(self, client):
        """Test: Error al crear preferencia de mensualidad sin ID."""
        # Arrange
        datos_sin_id = {
            'tipo_pago': 'mensualidad',
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_sin_id
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_preferencia_error_servicio(self, client):
        """Test: Error del servicio al crear preferencia."""
        # Arrange
        datos_pago = {
            'tipo_pago': 'cuota',
            'id_cuota': 1,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        mock_resultado = {
            'success': False,
            'error': 'Error al crear preferencia'
        }
        
        # Act
        with patch('src.routes.pagos_routes.mercadopago_service.crear_pago_cuota',
                   return_value=mock_resultado):
            response = make_json_request(
                client, 'POST', '/api/mercadopago/crear-preferencia',
                data=datos_pago
            )
        
        # Assert
        assert_error_response(response, expected_status=500)

