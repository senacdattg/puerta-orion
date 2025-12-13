"""
Tests para crear pagos de mensualidad en Mercado Pago.

Este módulo contiene tests que verifican la creación de pagos
para mensualidades, incluyendo validaciones y errores.
"""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestCrearPagoMensualidad:
    """Tests para crear pago de mensualidad."""
    
    def test_crear_pago_mensualidad_success(self, mercado_pago_service):
        """Test: Crear pago de mensualidad exitosamente."""
        with patch('src.models.pagos.Mensualidad') as mock_mensualidad_class:
            mock_mensualidad = MagicMock()
            mock_mensualidad.monto_pago = Decimal('100.0')
            mock_persona = MagicMock()
            mock_persona.nombre = 'Juan Pérez'
            mock_mensualidad.persona = mock_persona
            mock_mensualidad_class.query.get.return_value = mock_mensualidad
            
            with patch.object(mercado_pago_service, 'crear_preferencia', return_value={'success': True}):
                datos_pagador = {
                    'nombre_pagador': 'Juan Pérez',
                    'email_pagador': 'juan@test.com'
                }
                
                result = mercado_pago_service.crear_pago_mensualidad(1, datos_pagador)
                
                assert result['success'] is True
    
    def test_crear_pago_mensualidad_no_encontrada(self, mercado_pago_service):
        """Test: Error cuando la mensualidad no existe."""
        with patch('src.models.pagos.Mensualidad') as mock_mensualidad_class:
            mock_mensualidad_class.query.get.return_value = None
            
            result = mercado_pago_service.crear_pago_mensualidad(999, {})
            
            assert result['success'] is False
            assert 'no encontrada' in result['error']

