"""
Tests unitarios para funciones de validación de mensualidades_routes.

Cubre validaciones de negocio y funciones helper adicionales.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from src.routes.mensualidades_routes import (
    _extraer_id_persona,
    _extraer_documento_validado,
    _obtener_id_persona_por_documento,
    _validar_persona_con_rol_deportista,
    _resolver_persona_para_creacion,
    _obtener_estado_inicial,
    _obtener_metodo_pago,
    _obtener_monto_pago,
    _obtener_fecha_vencimiento,
    _calcular_saldo_inicial,
    _validar_mensualidad_duplicada,
    _persona_tiene_rol_deportista,
    _buscar_persona_por_documento,
    RequestValidationError,
)


@pytest.mark.unit
@pytest.mark.mensualidades
class TestMensualidadesValidaciones:
    """Tests para funciones de validación de mensualidades"""
    
    def test_extraer_id_persona_valid(self):
        """Test: Extraer ID persona válido."""
        data = {'id_persona': '123'}
        resultado = _extraer_id_persona(data)
        assert resultado == 123
    
    def test_extraer_id_persona_none(self):
        """Test: Extraer ID persona None."""
        data = {}
        resultado = _extraer_id_persona(data)
        assert resultado is None
    
    def test_extraer_id_persona_invalid(self):
        """Test: Extraer ID persona inválido."""
        data = {'id_persona': 'abc'}
        with pytest.raises(RequestValidationError):
            _extraer_id_persona(data)
    
    def test_obtener_id_persona_por_documento_success(self):
        """Test: Obtener ID persona por documento exitosamente."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento', return_value=mock_persona):
            resultado = _obtener_id_persona_por_documento('12345678')
            assert resultado == 1
    
    def test_obtener_id_persona_por_documento_no_encontrada(self):
        """Test: Persona no encontrada por documento."""
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento', return_value=None):
            with pytest.raises(RequestValidationError) as exc:
                _obtener_id_persona_por_documento('99999999')
            assert exc.value.status_code == 404
    
    def test_validar_persona_con_rol_deportista_success(self):
        """Test: Validar persona con rol deportista exitosamente."""
        with patch('src.routes.mensualidades_routes._persona_tiene_rol_deportista', return_value=True):
            # No debe lanzar excepción
            _validar_persona_con_rol_deportista(1)
    
    def test_validar_persona_con_rol_deportista_failure(self):
        """Test: Persona sin rol deportista."""
        with patch('src.routes.mensualidades_routes._persona_tiene_rol_deportista', return_value=False):
            with pytest.raises(RequestValidationError) as exc:
                _validar_persona_con_rol_deportista(1)
            assert exc.value.status_code == 400
    
    def test_resolver_persona_para_creacion_con_id(self):
        """Test: Resolver persona usando ID."""
        data = {'id_persona': 1}
        
        with patch('src.routes.mensualidades_routes._validar_persona_con_rol_deportista'):
            id_persona, _ = _resolver_persona_para_creacion(data)
            assert id_persona == 1
    
    def test_resolver_persona_para_creacion_con_documento(self):
        """Test: Resolver persona usando documento."""
        data = {'numero_documento': '12345678'}
        
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento', return_value=mock_persona):
            with patch('src.routes.mensualidades_routes._obtener_id_persona_por_documento', return_value=1):
                with patch('src.routes.mensualidades_routes._validar_persona_con_rol_deportista'):
                    id_persona, _ = _resolver_persona_para_creacion(data)
                    assert id_persona == 1
    
    def test_resolver_persona_para_creacion_sin_datos(self):
        """Test: Error cuando no se proporciona ID ni documento."""
        data = {}
        
        with pytest.raises(RequestValidationError) as exc:
            _resolver_persona_para_creacion(data)
        assert exc.value.status_code == 400
    
    def test_obtener_estado_inicial_pagado(self):
        """Test: Obtener estado inicial como pagado."""
        data = {'estado_ui': 'Pagado'}
        resultado = _obtener_estado_inicial(data)
        assert resultado is True
    
    def test_obtener_estado_inicial_pendiente(self):
        """Test: Obtener estado inicial como pendiente."""
        data = {'estado_ui': 'Pendiente'}
        resultado = _obtener_estado_inicial(data)
        assert resultado is False
    
    def test_obtener_estado_inicial_invalido(self):
        """Test: Estado inicial inválido."""
        data = {'estado_ui': 'Invalido'}
        
        with pytest.raises(RequestValidationError) as exc:
            _obtener_estado_inicial(data)
        assert exc.value.status_code == 400
    
    def test_obtener_estado_inicial_sin_campo(self):
        """Test: Estado inicial sin campo."""
        data = {}
        
        with pytest.raises(RequestValidationError) as exc:
            _obtener_estado_inicial(data)
        assert exc.value.status_code == 400
    
    def test_obtener_metodo_pago_success(self, app_context):
        """Test: Obtener método de pago exitosamente."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        data = {'id_metodo_pago': 1}
        mock_metodo = MagicMock()
        
        with patch('src.routes.mensualidades_routes.MetodoPago.query') as mock_query:
            mock_query.get.return_value = mock_metodo
            
            resultado = _obtener_metodo_pago(data)
            assert resultado == 1
    
    def test_obtener_metodo_pago_no_encontrado(self, app_context):
        """Test: Método de pago no encontrado."""
        data = {'id_metodo_pago': 999}
        
        with patch('src.routes.mensualidades_routes.MetodoPago.query') as mock_query:
            mock_query.get.return_value = None
            
            with pytest.raises(RequestValidationError) as exc:
                _obtener_metodo_pago(data)
            assert exc.value.status_code == 404
    
    def test_obtener_monto_pago_success(self):
        """Test: Obtener monto de pago válido."""
        data = {'monto_pago': 50000.0}
        resultado = _obtener_monto_pago(data)
        assert resultado == pytest.approx(50000.0)
    
    def test_obtener_monto_pago_invalido(self):
        """Test: Monto de pago inválido."""
        data = {'monto_pago': -100}
        
        with pytest.raises(RequestValidationError) as exc:
            _obtener_monto_pago(data)
        assert exc.value.status_code == 400
    
    def test_obtener_fecha_vencimiento_success(self):
        """Test: Obtener fecha de vencimiento válida."""
        data = {'fecha_vencimiento': '2024-12-31'}
        resultado = _obtener_fecha_vencimiento(data)
        assert resultado == date(2024, 12, 31)
    
    def test_obtener_fecha_vencimiento_invalida(self):
        """Test: Fecha de vencimiento inválida."""
        data = {'fecha_vencimiento': 'fecha-invalida'}
        
        with pytest.raises(RequestValidationError) as exc:
            _obtener_fecha_vencimiento(data)
        assert exc.value.status_code == 400
    
    def test_calcular_saldo_inicial_pagado(self):
        """Test: Calcular saldo inicial cuando está pagado."""
        data = {'estado_ui': 'Pagado'}
        monto_pago = 50000.0
        
        resultado = _calcular_saldo_inicial(data, monto_pago, True)
        assert resultado == pytest.approx(0.0)
    
    def test_calcular_saldo_inicial_pendiente(self):
        """Test: Calcular saldo inicial cuando está pendiente."""
        data = {'estado_ui': 'Pendiente', 'saldo_pendiente': 30000.0}
        monto_pago = 50000.0
        
        resultado = _calcular_saldo_inicial(data, monto_pago, False)
        assert resultado == pytest.approx(30000.0)
    
    def test_validar_mensualidad_duplicada_no_duplicada(self, app_context):
        """Test: No hay mensualidad duplicada."""
        from src.models.pagos.mensualidad import Mensualidad
        
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            # La función hace query.filter(...).first(), donde filter recibe múltiples condiciones
            mock_filter_result = MagicMock()
            mock_filter_result.first.return_value = None
            mock_query.filter.return_value = mock_filter_result
            
            # No debe lanzar excepción
            _validar_mensualidad_duplicada(1, date(2024, 12, 31))
    
    def test_validar_mensualidad_duplicada_duplicada(self, app_context):
        """Test: Mensualidad duplicada encontrada."""
        from src.models.pagos.mensualidad import Mensualidad
        
        mock_mensualidad = MagicMock()
        
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            # La función hace query.filter(...).first()
            mock_filter_result = MagicMock()
            mock_filter_result.first.return_value = mock_mensualidad
            mock_query.filter.return_value = mock_filter_result
            
            with pytest.raises(RequestValidationError) as exc:
                _validar_mensualidad_duplicada(1, date(2024, 12, 31))
            assert exc.value.status_code == 400
    
    def test_persona_tiene_rol_deportista_true(self, app_context):
        """Test: Persona tiene rol deportista."""
        from src.models.usuarios.usuario import Usuario
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Deportista'
        mock_usuario.roles = [mock_rol]
        
        with patch('src.routes.mensualidades_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            
            resultado = _persona_tiene_rol_deportista(1)
            assert resultado is True
    
    def test_persona_tiene_rol_deportista_false(self, app_context):
        """Test: Persona no tiene rol deportista."""
        from src.models.usuarios.usuario import Usuario
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Usuario'
        mock_usuario.roles = [mock_rol]
        
        with patch('src.routes.mensualidades_routes.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            
            resultado = _persona_tiene_rol_deportista(1)
            assert resultado is False
    
    def test_buscar_persona_por_documento_success(self):
        """Test: Buscar persona por documento exitosamente."""
        from src.models.personas.persona import Persona
        
        mock_persona = MagicMock()
        mock_persona.numero_documento = '12345678'
        
        with patch('src.routes.mensualidades_routes.Persona') as mock_persona_class:
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_query_result = MagicMock()
                mock_query_result.first.return_value = mock_persona
                mock_db.session.query.return_value.filter.return_value = mock_query_result
                
                resultado = _buscar_persona_por_documento('12345678')
                assert resultado == mock_persona
    
    def test_buscar_persona_por_documento_no_encontrada(self):
        """Test: Persona no encontrada por documento."""
        with patch('src.routes.mensualidades_routes.Persona') as mock_persona_class:
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_query_result = MagicMock()
                mock_query_result.first.return_value = None
                mock_db.session.query.return_value.filter.return_value = mock_query_result
                
                resultado = _buscar_persona_por_documento('99999999')
                assert resultado is None

