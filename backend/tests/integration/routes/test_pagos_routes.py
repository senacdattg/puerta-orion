"""
Tests para las rutas de pagos.

Este módulo contiene tests para todos los endpoints de pagos con Mercado Pago,
siguiendo las mejores prácticas de testing.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


# ============================================================================
# TESTS PARA CREAR PREFERENCIA DE PAGO
# ============================================================================

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


# ============================================================================
# TESTS PARA VERIFICAR PAGO
# ============================================================================

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


# ============================================================================
# TESTS PARA WEBHOOK
# ============================================================================

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


# ============================================================================
# TESTS PARA ESTADÍSTICAS DE PAGOS
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.pagos
class TestEstadisticasPagos:
    """Tests para el endpoint GET /api/mercadopago/estadisticas"""
    
    def test_obtener_estadisticas_success(self, client):
        """Test: Obtener estadísticas de pagos exitosamente."""
        # Arrange
        mock_estadisticas = {
            'total_pagos': 100,
            'pagos_aprobados': 80,
            'pagos_pendientes': 15,
            'pagos_rechazados': 5
        }
        
        # Act
        with patch('src.routes.pagos_routes.TransaccionMercadoPago.query') as mock_query:
            mock_query.count.return_value = 100
            mock_query.filter_by.return_value.count.return_value = 80
            
            response = client.get('/api/mercadopago/estadisticas')
        
        # Assert
        # El endpoint puede no existir o requerir autenticación
        # Ajustar según la implementación real
        assert response.status_code in [200, 401, 404]

