"""
Tests unitarios para funciones helper de mensualidades_routes.

Cubre funciones privadas y lógica de negocio.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date

from src.routes.mensualidades_routes import (
    _add_months,
    _estado_texto,
    _recalcular_estado_mensualidad,
    _parse_decimal,
    _normalizar_documento_persona,
    _calcular_meses_y_sobrante,
    _obtener_parametros_paginacion,
)


@pytest.mark.unit
@pytest.mark.mensualidades
class TestMensualidadesHelpers:
    """Tests para funciones helper de mensualidades"""
    
    def test_add_months_basic(self):
        """Test: Suma meses básica."""
        fecha_base = date(2024, 1, 15)
        resultado = _add_months(fecha_base, 1)
        assert resultado == date(2024, 2, 15)
    
    def test_add_months_multiple(self):
        """Test: Suma múltiples meses."""
        fecha_base = date(2024, 1, 15)
        resultado = _add_months(fecha_base, 6)
        assert resultado == date(2024, 7, 15)
    
    def test_add_months_cross_year(self):
        """Test: Suma meses que cruza año."""
        fecha_base = date(2024, 11, 15)
        resultado = _add_months(fecha_base, 3)
        assert resultado == date(2025, 2, 15)
    
    def test_add_months_february_leap_year(self):
        """Test: Manejo de febrero en año bisiesto."""
        fecha_base = date(2024, 1, 29)  # Año bisiesto
        resultado = _add_months(fecha_base, 1)
        assert resultado == date(2024, 2, 29)  # 2024 es bisiesto
    
    def test_add_months_february_non_leap(self):
        """Test: Manejo de febrero en año no bisiesto."""
        fecha_base = date(2025, 1, 31)  # 2025 no es bisiesto
        resultado = _add_months(fecha_base, 1)
        assert resultado == date(2025, 2, 28)  # Ajusta a 28 días
    
    def test_add_months_day_adjustment(self):
        """Test: Ajuste de día cuando el mes destino no tiene suficientes días."""
        fecha_base = date(2024, 1, 31)
        resultado = _add_months(fecha_base, 1)
        assert resultado == date(2024, 2, 29)  # Febrero tiene 29 en año bisiesto
    
    def test_estado_texto_pagado(self):
        """Test: Estado texto para mensualidad pagada."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        
        resultado = _estado_texto(mock_mensualidad)
        assert resultado == 'Pagado'
    
    def test_estado_texto_vencido(self):
        """Test: Estado texto para mensualidad vencida."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2023, 12, 31)  # Pasada
        
        resultado = _estado_texto(mock_mensualidad)
        assert resultado == 'Vencido'
    
    def test_estado_texto_pendiente(self):
        """Test: Estado texto para mensualidad pendiente."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2025, 12, 31)  # Futura
        
        resultado = _estado_texto(mock_mensualidad)
        assert resultado == 'Pendiente'
    
    def test_estado_texto_inactiva(self):
        """Test: Estado texto para mensualidad inactiva."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.activo = False
        
        resultado = _estado_texto(mock_mensualidad)
        assert resultado == 'Inactiva'
    
    def test_estado_texto_exception(self):
        """Test: Manejo de excepción en estado_texto."""
        mock_mensualidad = MagicMock()
        # Forzar excepción al acceder a activo
        type(mock_mensualidad).activo = PropertyMock(side_effect=Exception("Error acceso"))
        
        resultado = _estado_texto(mock_mensualidad)
        assert resultado == 'Pendiente'  # Valor por defecto cuando hay excepción
    
    def test_parse_decimal_valid(self):
        """Test: Parse decimal con valor válido."""
        assert _parse_decimal('100.5') == pytest.approx(100.5)
        assert _parse_decimal(100) == pytest.approx(100.0)
        assert _parse_decimal(100.5) == pytest.approx(100.5)
    
    def test_parse_decimal_none(self):
        """Test: Parse decimal con None."""
        assert _parse_decimal(None) is None
    
    def test_parse_decimal_invalid(self):
        """Test: Parse decimal con valor inválido."""
        assert _parse_decimal('invalid') is None
        assert _parse_decimal('abc') is None
    
    def test_normalizar_documento_persona_valid(self):
        """Test: Normalizar documento válido."""
        assert _normalizar_documento_persona('12345678') == '12345678'
        assert _normalizar_documento_persona('12.345.678') == '12345678'
        assert _normalizar_documento_persona('12-345-678') == '12345678'
    
    def test_normalizar_documento_persona_none(self):
        """Test: Normalizar documento None."""
        assert _normalizar_documento_persona(None) is None
    
    def test_normalizar_documento_persona_empty(self):
        """Test: Normalizar documento vacío."""
        assert _normalizar_documento_persona('') is None
        assert _normalizar_documento_persona('   ') is None
    
    def test_calcular_meses_y_sobrante_exacto(self):
        """Test: Calcular meses cuando el abono cubre exactamente."""
        meses, sobrante = _calcular_meses_y_sobrante(100000.0, 50000.0)
        assert meses == 2
        assert sobrante == pytest.approx(0.0)
    
    def test_calcular_meses_y_sobrante_con_sobrante(self):
        """Test: Calcular meses con sobrante."""
        meses, sobrante = _calcular_meses_y_sobrante(125000.0, 50000.0)
        assert meses == 2
        assert sobrante == pytest.approx(25000.0)
    
    def test_calcular_meses_y_sobrante_menor_que_monto(self):
        """Test: Calcular cuando abono es menor que un monto."""
        meses, sobrante = _calcular_meses_y_sobrante(30000.0, 50000.0)
        assert meses == 0
        assert sobrante == pytest.approx(30000.0)
    
    def test_calcular_meses_y_sobrante_cero(self):
        """Test: Calcular con monto base cero."""
        meses, sobrante = _calcular_meses_y_sobrante(10000.0, 0)
        assert meses == 0
        assert sobrante == pytest.approx(0.0)
    
    def test_recalcular_estado_mensualidad_pagada(self):
        """Test: Recalcular estado cuando mensualidad queda pagada."""
        from src.models.base import db
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        with patch('src.routes.mensualidades_routes.db.session.query') as mock_query:
            mock_result = MagicMock()
            mock_result.filter.return_value.scalar.return_value = 50000.0
            mock_query.return_value = mock_result
            
            _recalcular_estado_mensualidad(mock_mensualidad)
            
            assert mock_mensualidad.saldo_pendiente == pytest.approx(0.0)
            assert mock_mensualidad.estado is True
            assert mock_mensualidad.fecha_pago == date.today()
    
    def test_recalcular_estado_mensualidad_pendiente(self):
        """Test: Recalcular estado cuando mensualidad queda pendiente."""
        from src.models.base import db
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        with patch('src.routes.mensualidades_routes.db.session.query') as mock_query:
            mock_result = MagicMock()
            mock_result.filter.return_value.scalar.return_value = 20000.0  # Abonado parcialmente
            mock_query.return_value = mock_result
            
            _recalcular_estado_mensualidad(mock_mensualidad)
            
            assert mock_mensualidad.saldo_pendiente == pytest.approx(30000.0)
            assert mock_mensualidad.estado is False
            assert mock_mensualidad.fecha_pago is None
    
    def test_obtener_parametros_paginacion_default(self):
        """Test: Obtener parámetros de paginación con valores por defecto."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/mensualidades'):
            page, per_page = _obtener_parametros_paginacion()
            assert page == 1
            assert per_page == 20
    
    def test_obtener_parametros_paginacion_custom(self):
        """Test: Obtener parámetros de paginación personalizados."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/mensualidades?page=3&per_page=50'):
            page, per_page = _obtener_parametros_paginacion()
            assert page == 3
            assert per_page == 50
    
    def test_obtener_parametros_paginacion_invalid(self):
        """Test: Obtener parámetros de paginación con valores inválidos."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/mensualidades?page=abc&per_page=xyz'):
            page, per_page = _obtener_parametros_paginacion()
            # Debe usar valores por defecto cuando son inválidos
            assert page == 1
            assert per_page == 20

