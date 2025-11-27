"""
Tests para crear pagos de cuota en Mercado Pago.

Este módulo contiene tests que verifican la creación de pagos
para cuotas, incluyendo validaciones de saldo y errores.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestCrearPagoCuota:
    """Tests para crear pago de cuota."""
    
    def test_crear_pago_cuota_success(self, mercado_pago_service):
        """Test: Crear pago de cuota exitosamente."""
        with patch('src.models.pagos.Cuota') as mock_cuota_class:
            mock_cuota = MagicMock()
            mock_cuota.calcular_saldo_pendiente.return_value = 100.0
            mock_cuota.saldo_pendiente = 100.0
            mock_cuota.monto_cuota = 100.0
            mock_cuota_class.query.get.return_value = mock_cuota
            
            with patch.object(mercado_pago_service, 'crear_preferencia', return_value={'success': True}):
                datos_pagador = {
                    'nombre_pagador': 'Juan Pérez',
                    'email_pagador': 'juan@test.com'
                }
                
                result = mercado_pago_service.crear_pago_cuota(1, datos_pagador, 100.0)
                
                assert result['success'] is True
    
    def test_crear_pago_cuota_no_encontrada(self, mercado_pago_service):
        """Test: Error cuando la cuota no existe."""
        with patch('src.models.pagos.Cuota') as mock_cuota_class:
            mock_cuota_class.query.get.return_value = None
            
            result = mercado_pago_service.crear_pago_cuota(999, {}, 100.0)
            
            assert result['success'] is False
            assert 'no encontrada' in result['error']
    
    def test_crear_pago_cuota_monto_excede_saldo(self, mercado_pago_service):
        """Test: Error cuando el monto excede el saldo pendiente."""
        with patch('src.models.pagos.Cuota') as mock_cuota_class:
            mock_cuota = MagicMock()
            mock_cuota.calcular_saldo_pendiente.return_value = 50.0
            mock_cuota_class.query.get.return_value = mock_cuota
            
            result = mercado_pago_service.crear_pago_cuota(1, {}, 100.0)
            
            assert result['success'] is False
            assert 'excede' in result['error']

