"""
Tests para obtener método de pago de Mercado Pago.

Este módulo contiene tests que verifican la obtención del método
de pago configurado para Mercado Pago.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestObtenerMetodoPago:
    """Tests para obtener método de pago de Mercado Pago."""
    
    def test_obtener_metodo_pago_mercadopago(self, mercado_pago_service):
        """Test: Obtener método de pago de Mercado Pago."""
        with patch('src.services.mercadopago_service.MetodoPago') as mock_metodo_class:
            mock_metodo = MagicMock()
            mock_metodo_class.query.filter_by.return_value.first.return_value = mock_metodo
            
            result = mercado_pago_service.obtener_metodo_pago_mercadopago()
            
            assert result == mock_metodo
    
    def test_obtener_metodo_pago_no_encontrado(self, mercado_pago_service):
        """Test: Método de pago no encontrado."""
        with patch('src.services.mercadopago_service.MetodoPago') as mock_metodo_class:
            mock_metodo_class.query.filter_by.return_value.first.return_value = None
            
            result = mercado_pago_service.obtener_metodo_pago_mercadopago()
            
            assert result is None

