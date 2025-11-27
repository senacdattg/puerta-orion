"""
Tests para métodos privados del servicio de Mercado Pago.

Este módulo contiene tests que verifican los métodos privados
del servicio, incluyendo extracción de datos y validaciones.
"""

import pytest
from unittest.mock import patch
from datetime import date
from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestMetodosPrivados:
    """Tests para métodos privados del servicio."""
    
    def test_extraer_payment_id(self, mercado_pago_service):
        """Test: Extraer ID de pago del webhook."""
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        
        payment_id = mercado_pago_service._extraer_payment_id(datos_webhook)
        assert payment_id == 'payment_123'
    
    def test_extraer_payment_id_tipo_incorrecto(self, mercado_pago_service):
        """Test: Extraer ID cuando el tipo no es payment."""
        datos_webhook = {
            'type': 'preference',
            'data': {'id': 'pref_123'}
        }
        
        payment_id = mercado_pago_service._extraer_payment_id(datos_webhook)
        assert payment_id is None
    
    def test_obtener_fecha_abono_date_approved(self, mercado_pago_service):
        """Test: Obtener fecha de abono desde date_approved."""
        payment = {
            'date_approved': '2024-01-15T10:30:00Z'
        }
        
        fecha = mercado_pago_service._obtener_fecha_abono(payment)
        assert fecha == date(2024, 1, 15)
    
    def test_obtener_fecha_abono_date_created(self, mercado_pago_service):
        """Test: Obtener fecha de abono desde date_created."""
        payment = {
            'date_created': '2024-01-15T10:30:00Z'
        }
        
        fecha = mercado_pago_service._obtener_fecha_abono(payment)
        assert fecha == date(2024, 1, 15)
    
    def test_obtener_fecha_abono_default(self, mercado_pago_service):
        """Test: Obtener fecha por defecto cuando no hay fecha en el pago."""
        payment = {}
        
        with patch('src.services.mercadopago_service.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 15)
            fecha = mercado_pago_service._obtener_fecha_abono(payment)
            assert fecha == date(2024, 1, 15)
    
    def test_obtener_metadata_pago(self, mercado_pago_service):
        """Test: Obtener metadatos del pago."""
        payment = {
            'metadata': {
                'tipo_pago': 'mensualidad',
                'id_mensualidad': 1
            }
        }
        
        metadata = mercado_pago_service._obtener_metadata_pago(payment)
        assert metadata['tipo_pago'] == 'mensualidad'
        assert metadata['id_mensualidad'] == 1
    
    def test_obtener_metadata_pago_sin_metadata(self, mercado_pago_service):
        """Test: Obtener metadatos cuando no existen."""
        payment = {}
        
        metadata = mercado_pago_service._obtener_metadata_pago(payment)
        assert metadata == {}
    
    def test_es_pago_mensualidad_aprobado(self, mercado_pago_service):
        """Test: Verificar si es pago de mensualidad aprobado."""
        metadata = {
            'tipo_pago': 'mensualidad',
            'id_mensualidad': 1
        }
        
        assert mercado_pago_service._es_pago_mensualidad_aprobado('approved', metadata) is True
        assert mercado_pago_service._es_pago_mensualidad_aprobado('pending', metadata) is False
        assert mercado_pago_service._es_pago_mensualidad_aprobado('approved', {'tipo_pago': 'cuota'}) is False

