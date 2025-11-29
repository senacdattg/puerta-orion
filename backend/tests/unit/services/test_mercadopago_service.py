"""
Tests unitarios para mercadopago_service.

Cubre creación de preferencias, verificación de pagos y procesamiento de webhooks.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from decimal import Decimal

from src.services.mercadopago_service import MercadoPagoService


@pytest.mark.unit
class TestMercadoPagoService:
    """Tests para MercadoPagoService"""
    
    @pytest.fixture
    def service(self):
        """Fixture para servicio."""
        with patch.dict('os.environ', {
            'MERCADOPAGO_ACCESS_TOKEN': 'test_access_token',
            'MERCADOPAGO_PUBLIC_KEY': 'test_public_key',
            'MERCADOPAGO_ENVIRONMENT': 'sandbox'
        }):
            service = MercadoPagoService()
            return service
    
    def test_init_with_credentials(self, service):
        """Test: Inicialización con credenciales."""
        assert service.access_token == 'test_access_token'
        assert service.public_key == 'test_public_key'
        assert service.environment == 'sandbox'
        assert service.sdk is not None
    
    def test_init_without_credentials(self):
        """Test: Inicialización sin credenciales."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            assert service.sdk is None
    
    def test_add_months_basic(self):
        """Test: Suma meses básica."""
        fecha_base = date(2024, 1, 15)
        resultado = MercadoPagoService._add_months(fecha_base, 1)
        assert resultado == date(2024, 2, 15)
    
    def test_add_months_cross_year(self):
        """Test: Suma meses cruzando año."""
        fecha_base = date(2024, 11, 15)
        resultado = MercadoPagoService._add_months(fecha_base, 3)
        assert resultado == date(2025, 2, 15)
    
    def test_add_months_february_leap(self):
        """Test: Manejo de febrero en año bisiesto."""
        fecha_base = date(2024, 1, 29)
        resultado = MercadoPagoService._add_months(fecha_base, 1)
        assert resultado == date(2024, 2, 29)
    
    def test_aplicar_abono_mensualidad_meses_completos(self):
        """Test: Aplicar abono que cubre meses completos."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        resultado = MercadoPagoService._aplicar_abono_mensualidad(mock_mensualidad, 100000.0)
        
        assert resultado['meses_cubiertos'] == 2
        assert resultado['sobrante'] == 0.0
        assert mock_mensualidad.estado is False  # Puede quedar pendiente si hay saldo
    
    def test_aplicar_abono_mensualidad_con_sobrante(self):
        """Test: Aplicar abono con sobrante."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        resultado = MercadoPagoService._aplicar_abono_mensualidad(mock_mensualidad, 75000.0)
        
        assert resultado['meses_cubiertos'] == 1
        assert resultado['sobrante'] == 25000.0
    
    def test_aplicar_abono_mensualidad_completa_pago(self):
        """Test: Abono que completa el pago."""
        mock_mensualidad = MagicMock()
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        resultado = MercadoPagoService._aplicar_abono_mensualidad(mock_mensualidad, 50000.0)
        
        assert mock_mensualidad.estado is True
        assert mock_mensualidad.fecha_pago == date.today()
        assert mock_mensualidad.saldo_pendiente == 0.0
    
    def test_crear_preferencia_success(self, service):
        """Test: Crear preferencia exitosamente."""
        datos_pago = {
            'monto': 50000.0,
            'descripcion': 'Mensualidad',
            'external_reference': 'ref_123'
        }
        
        mock_response = {
            'id': 'pref_123',
            'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_123'
        }
        
        with patch.object(service.sdk, 'preference') as mock_preference:
            mock_preference.return_value.create.return_value = mock_response
            
            resultado = service.crear_preferencia(datos_pago)
            
            assert resultado['id'] == 'pref_123'
            assert 'init_point' in resultado
    
    def test_crear_preferencia_sin_sdk(self):
        """Test: Error cuando SDK no está inicializado."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            
            with pytest.raises(Exception):
                service.crear_preferencia({'monto': 50000.0})
    
    def test_verificar_pago_success(self, service):
        """Test: Verificar pago exitosamente."""
        payment_id = '123456789'
        mock_payment = {
            'id': payment_id,
            'status': 'approved',
            'transaction_amount': 50000.0
        }
        
        with patch.object(service.sdk, 'payment') as mock_payment_sdk:
            mock_payment_sdk.return_value.get.return_value = mock_payment
            
            resultado = service.verificar_pago(payment_id)
            
            assert resultado['id'] == payment_id
            assert resultado['status'] == 'approved'
    
    def test_verificar_pago_no_encontrado(self, service):
        """Test: Pago no encontrado."""
        payment_id = '999999999'
        
        with patch.object(service.sdk, 'payment') as mock_payment_sdk:
            mock_payment_sdk.return_value.get.return_value = None
            
            resultado = service.verificar_pago(payment_id)
            assert resultado is None
    
    def test_procesar_webhook_success(self, service, app_context):
        """Test: Procesar webhook exitosamente."""
        webhook_data = {
            'type': 'payment',
            'data': {'id': '123456789'}
        }
        
        mock_payment = {
            'id': '123456789',
            'status': 'approved',
            'transaction_amount': 50000.0,
            'external_reference': 'ref_123',
            'date_approved': '2024-01-01T10:00:00.000-04:00',
            'metadata': {
                'tipo_pago': 'mensualidad',
                'id_mensualidad': '1'
            }
        }
        
        with patch.object(service, 'verificar_pago') as mock_verificar:
            mock_verificar.return_value = {
                'success': True,
                'payment': mock_payment,
                'estado': 'approved'
            }
            with patch.object(service, '_procesar_pago_mensualidad') as mock_procesar:
                resultado = service.procesar_webhook(webhook_data)
                
                assert resultado['success'] is True
                mock_procesar.assert_called_once()
    
    def test_procesar_webhook_tipo_invalido(self, service):
        """Test: Webhook con tipo inválido."""
        webhook_data = {
            'type': 'unknown_type',
            'data': {}
        }
        
        resultado = service.procesar_webhook(webhook_data)
        
        assert resultado['success'] is False
        assert 'tipo' in resultado.get('error', '').lower()
    
    def test_obtener_metodo_pago_mercadopago(self, service, app_context):
        """Test: Obtener método de pago MercadoPago."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        mock_metodo = MagicMock()
        mock_metodo.id_metodo_pago = 1
        mock_metodo.nombre_metodo = 'MercadoPago'
        
        with patch('src.services.mercadopago_service.MetodoPago.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_metodo
            
            resultado = service.obtener_metodo_pago_mercadopago()
            
            assert resultado.id_metodo_pago == 1
    
    def test_obtener_metodo_pago_mercadopago_no_encontrado(self, service, app_context):
        """Test: Método de pago no encontrado."""
        with patch('src.services.mercadopago_service.MetodoPago.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            resultado = service.obtener_metodo_pago_mercadopago()
            
            assert resultado is None

