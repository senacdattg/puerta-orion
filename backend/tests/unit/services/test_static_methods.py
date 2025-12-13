"""
Tests para métodos estáticos del servicio de Mercado Pago.

Este módulo contiene tests que verifican los métodos estáticos
del servicio, especialmente el cálculo de fechas.
"""

import pytest
from datetime import date
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestMercadoPagoServiceStaticMethods:
    """Tests para métodos estáticos del servicio."""
    
    def test_add_months(self):
        """Test: Sumar meses a una fecha."""
        base_date = date(2024, 1, 15)
        result = MercadoPagoService._add_months(base_date, 2)
        assert result == date(2024, 3, 15)
    
    def test_add_months_year_boundary(self):
        """Test: Sumar meses que cruzan año."""
        base_date = date(2024, 11, 15)
        result = MercadoPagoService._add_months(base_date, 3)
        assert result == date(2025, 2, 15)
    
    def test_add_months_leap_year(self):
        """Test: Sumar meses en año bisiesto."""
        base_date = date(2024, 1, 31)
        result = MercadoPagoService._add_months(base_date, 1)
        assert result == date(2024, 2, 29)
    
    def test_add_months_february_non_leap(self):
        """Test: Sumar meses en febrero de año no bisiesto."""
        base_date = date(2023, 1, 31)
        result = MercadoPagoService._add_months(base_date, 1)
        assert result == date(2023, 2, 28)

