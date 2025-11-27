"""
Tests para el servicio de Mercado Pago.

Este módulo contiene tests para todas las funcionalidades del servicio
de integración con Mercado Pago.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from datetime import date, datetime
from decimal import Decimal

from src.services.mercadopago_service import MercadoPagoService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Mock para variables de entorno de Mercado Pago."""
    with patch.dict('os.environ', {
        'MERCADOPAGO_ACCESS_TOKEN': 'test_access_token',
        'MERCADOPAGO_PUBLIC_KEY': 'test_public_key',
        'MERCADOPAGO_ENVIRONMENT': 'sandbox'
    }):
        yield


@pytest.fixture
def mock_sdk():
    """Mock para el SDK de Mercado Pago."""
    mock_sdk_instance = MagicMock()
    mock_preference = MagicMock()
    mock_payment = MagicMock()
    
    mock_sdk_instance.preference.return_value = mock_preference
    mock_sdk_instance.payment.return_value = mock_payment
    
    return mock_sdk_instance, mock_preference, mock_payment


@pytest.fixture
def mercado_pago_service(mock_env_vars):
    """Crea una instancia del servicio de Mercado Pago."""
    with patch('src.services.mercadopago_service.mercadopago.SDK') as mock_sdk_class:
        mock_sdk_instance = MagicMock()
        mock_sdk_class.return_value = mock_sdk_instance
        service = MercadoPagoService()
        service.sdk = mock_sdk_instance
        return service


# ============================================================================
# TESTS PARA INICIALIZACIÓN
# ============================================================================

@pytest.mark.unit
class TestMercadoPagoServiceInit:
    """Tests para la inicialización del servicio."""
    
    def test_init_with_credentials(self, mock_env_vars):
        """Test: Inicialización con credenciales válidas."""
        with patch('src.services.mercadopago_service.mercadopago.SDK') as mock_sdk_class:
            mock_sdk_instance = MagicMock()
            mock_sdk_class.return_value = mock_sdk_instance
            
            service = MercadoPagoService()
            
            assert service.access_token == 'test_access_token'
            assert service.public_key == 'test_public_key'
            assert service.environment == 'sandbox'
            assert service.sdk == mock_sdk_instance
    
    def test_init_without_credentials(self):
        """Test: Inicialización sin credenciales."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            
            assert service.access_token is None
            assert service.public_key is None
            assert service.sdk is None
    
    def test_init_with_default_environment(self):
        """Test: Inicialización con ambiente por defecto."""
        with patch.dict('os.environ', {
            'MERCADOPAGO_ACCESS_TOKEN': 'test_token',
            'MERCADOPAGO_PUBLIC_KEY': 'test_key'
        }):
            with patch('src.services.mercadopago_service.mercadopago.SDK'):
                service = MercadoPagoService()
                assert service.environment == 'sandbox'


# ============================================================================
# TESTS PARA MÉTODOS ESTÁTICOS
# ============================================================================

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


# ============================================================================
# TESTS PARA CREAR PREFERENCIA
# ============================================================================

@pytest.mark.unit
class TestCrearPreferencia:
    """Tests para crear preferencia de pago."""
    
    def test_crear_preferencia_success(self, mercado_pago_service, mock_sdk):
        """Test: Crear preferencia exitosamente."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        datos_pago = {
            'titulo': 'Pago Test',
            'monto': 100.0,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@test.com',
            'tipo_documento': 'CC',
            'numero_documento': '12345678',
            'referencia_externa': 'TEST_123',
            'tipo_pago': 'cuota',
            'id_cuota': 1
        }
        
        mock_response = {
            'status': 201,
            'response': {
                'id': 'pref_123',
                'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_123',
                'external_reference': 'TEST_123'
            }
        }
        mock_preference.create.return_value = mock_response
        
        with patch('src.services.mercadopago_service.TransaccionMercadoPago') as mock_transaccion:
            with patch('src.services.mercadopago_service.db') as mock_db:
                mock_transaccion.crear_transaccion.return_value = MagicMock()
                
                result = mercado_pago_service.crear_preferencia(datos_pago)
                
                assert result['success'] is True
                assert result['preference_id'] == 'pref_123'
                assert 'init_point' in result
    
    def test_crear_preferencia_sin_sdk(self):
        """Test: Error cuando SDK no está configurado."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            result = service.crear_preferencia({})
            
            assert result['success'] is False
            assert 'no configurado' in result['error']
    
    def test_crear_preferencia_error_api(self, mercado_pago_service, mock_sdk):
        """Test: Error cuando la API de Mercado Pago falla."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_response = {
            'status': 400,
            'response': {'error': 'Invalid data'}
        }
        mock_preference.create.return_value = mock_response
        
        result = mercado_pago_service.crear_preferencia({'monto': 100.0})
        
        assert result['success'] is False
    
    def test_crear_preferencia_excepcion(self, mercado_pago_service, mock_sdk):
        """Test: Manejo de excepciones al crear preferencia."""
        mock_sdk_instance, mock_preference, _ = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_preference.create.side_effect = Exception('Error de conexión')
        
        with patch('src.services.mercadopago_service.db') as mock_db:
            mock_db.session.rollback = MagicMock()
            result = mercado_pago_service.crear_preferencia({'monto': 100.0})
            
            assert result['success'] is False
            assert 'error' in result


# ============================================================================
# TESTS PARA VERIFICAR PAGO
# ============================================================================

@pytest.mark.unit
class TestVerificarPago:
    """Tests para verificar estado de pago."""
    
    def test_verificar_pago_success(self, mercado_pago_service, mock_sdk):
        """Test: Verificar pago exitosamente."""
        mock_sdk_instance, _, mock_payment = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        payment_id = 'payment_123'
        mock_response = {
            'status': 200,
            'response': {
                'id': payment_id,
                'status': 'approved',
                'transaction_amount': 100.0,
                'currency_id': 'COP'
            }
        }
        mock_payment.get.return_value = mock_response
        
        with patch('src.services.mercadopago_service.TransaccionMercadoPago') as mock_transaccion:
            with patch('src.services.mercadopago_service.db') as mock_db:
                mock_transaccion_obj = MagicMock()
                mock_transaccion.query.filter_by.return_value.first.return_value = mock_transaccion_obj
                
                result = mercado_pago_service.verificar_pago(payment_id)
                
                assert result['success'] is True
                assert result['estado'] == 'approved'
                assert result['monto'] == 100.0
    
    def test_verificar_pago_sin_sdk(self):
        """Test: Error cuando SDK no está configurado."""
        with patch.dict('os.environ', {}, clear=True):
            service = MercadoPagoService()
            result = service.verificar_pago('payment_123')
            
            assert result['success'] is False
    
    def test_verificar_pago_no_encontrado(self, mercado_pago_service, mock_sdk):
        """Test: Pago no encontrado en Mercado Pago."""
        mock_sdk_instance, _, mock_payment = mock_sdk
        mercado_pago_service.sdk = mock_sdk_instance
        
        mock_response = {
            'status': 404,
            'response': {'error': 'Payment not found'}
        }
        mock_payment.get.return_value = mock_response
        
        result = mercado_pago_service.verificar_pago('payment_999')
        
        assert result['success'] is False


# ============================================================================
# TESTS PARA PROCESAR WEBHOOK
# ============================================================================

@pytest.mark.unit
class TestProcesarWebhook:
    """Tests para procesar webhooks de Mercado Pago."""
    
    def test_procesar_webhook_payment_type(self, mercado_pago_service):
        """Test: Procesar webhook de tipo payment."""
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        
        with patch.object(mercado_pago_service, '_procesar_webhook_pago', return_value={'success': True}):
            result = mercado_pago_service.procesar_webhook(datos_webhook)
            
            assert result['success'] is True
    
    def test_procesar_webhook_tipo_no_reconocido(self, mercado_pago_service):
        """Test: Webhook con tipo no reconocido."""
        datos_webhook = {
            'type': 'unknown',
            'data': {}
        }
        
        result = mercado_pago_service.procesar_webhook(datos_webhook)
        
        assert result['success'] is False
        assert 'no reconocido' in result['message']
    
    def test_procesar_webhook_excepcion(self, mercado_pago_service):
        """Test: Manejo de excepciones en webhook."""
        datos_webhook = {
            'type': 'payment',
            'data': {'id': 'payment_123'}
        }
        
        with patch.object(mercado_pago_service, '_procesar_webhook_pago', side_effect=Exception('Error')):
            result = mercado_pago_service.procesar_webhook(datos_webhook)
            
            assert result['success'] is False


# ============================================================================
# TESTS PARA MÉTODOS PRIVADOS
# ============================================================================

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


# ============================================================================
# TESTS PARA CREAR PAGO CUOTA
# ============================================================================

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


# ============================================================================
# TESTS PARA CREAR PAGO MENSUALIDAD
# ============================================================================

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


# ============================================================================
# TESTS PARA OBTENER MÉTODO DE PAGO
# ============================================================================

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

