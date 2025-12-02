"""
Tests de integración para crear preferencia de pago.

Endpoint: POST /api/mercadopago/crear-preferencia
Funcionalidad: Crear una preferencia de pago en MercadoPago
"""

import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.pagos
class TestCrearPreferenciaCompleto:
    """Tests para el endpoint POST /api/mercadopago/crear-preferencia"""
    
    def test_crear_preferencia_mensualidad_exitoso(
        self, client, db_session, persona, categoria
    ):
        """
        Test: Crear preferencia de pago para mensualidad exitosamente.
        
        Valida:
        - Creación de preferencia en MercadoPago
        - Guardado de transacción en BD
        - Respuesta con init_point
        """
        # Arrange
        from src.models.pagos.mensualidad import Mensualidad
        from src.models.pagos.metodo_pago import MetodoPago
        
        metodo_pago = MetodoPago(nombre_metodo='Mercado Pago')
        db_session.add(metodo_pago)
        db_session.commit()
        
        mensualidad = Mensualidad(
            id_persona=persona.id_persona,
            id_metodo_pago=metodo_pago.id_metodo_pago,
            monto_pago=Decimal('50000.00'),
            fecha_vencimiento=date(2024, 2, 15),
            estado=False,
            saldo_pendiente=Decimal('50000.00')
        )
        db_session.add(mensualidad)
        db_session.commit()
        
        # Mock de SDK de MercadoPago - parchear la instancia del servicio en las rutas
        from src.routes import pagos_routes
        mock_preference = MagicMock()
        mock_preference.create.return_value = {
            'status': 201,
            'response': {
                'id': 'pref_123456789',
                'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_123456789',
                'external_reference': f'MENS_{mensualidad.id_mensualidad}'
            }
        }
        mock_sdk_instance = MagicMock()
        mock_sdk_instance.preference.return_value = mock_preference
        pagos_routes.mercadopago_service.sdk = mock_sdk_instance
        
        datos_preferencia = {
            'tipo_pago': 'mensualidad',
            'id_mensualidad': mensualidad.id_mensualidad,
            'nombre_pagador': persona.primer_nombre + ' ' + persona.primer_apellido,
            'email_pagador': persona.correo_electronico,
            'tipo_documento': 'CC',
            'numero_documento': str(persona.documento)
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_preferencia
        )
        
        # Assert
        data = assert_success_response(response)
        assert 'preference_id' in data
        assert 'init_point' in data
        
        # Verificar que se guardó la transacción
        from src.models.pagos.transaccion_mercadopago import TransaccionMercadoPago
        transaccion = TransaccionMercadoPago.query.filter_by(
            preference_id='pref_123456789'
        ).first()
        assert transaccion is not None
        assert transaccion.estado == 'pending'
    
    def test_crear_preferencia_cuota_exitoso(
        self, client, db_session, persona
    ):
        """
        Test: Crear preferencia de pago para cuota exitosamente.
        
        Valida:
        - Creación de preferencia para cuota
        - Validación de saldo pendiente
        - Respuesta correcta
        """
        # Arrange
        from src.models.pagos.cuota import Cuota
        from src.models.pagos.metodo_pago import MetodoPago
        
        metodo_pago = MetodoPago(nombre_metodo='Mercado Pago')
        db_session.add(metodo_pago)
        db_session.commit()
        
        cuota = Cuota(
            id_persona=persona.id_persona,
            monto_cuota=Decimal('100000.00'),
            fecha_cuota=date(2024, 1, 15),
            descuento=False,
            id_metodo_pago=metodo_pago.id_metodo_pago
        )
        db_session.add(cuota)
        db_session.commit()
        
        # Mock de SDK de MercadoPago - parchear la instancia del servicio en las rutas
        from src.routes import pagos_routes
        mock_preference = MagicMock()
        mock_preference.create.return_value = {
            'status': 201,
            'response': {
                'id': 'pref_987654321',
                'init_point': 'https://www.mercadopago.com/checkout/v1/redirect?pref_id=pref_987654321',
                'external_reference': f'CUOTA_{cuota.id_cuota}'
            }
        }
        mock_sdk_instance = MagicMock()
        mock_sdk_instance.preference.return_value = mock_preference
        pagos_routes.mercadopago_service.sdk = mock_sdk_instance
        
        datos_preferencia = {
            'tipo_pago': 'cuota',
            'id_cuota': cuota.id_cuota,
            'nombre_pagador': persona.primer_nombre + ' ' + persona.primer_apellido,
            'email_pagador': persona.correo_electronico,
            'tipo_documento': 'CC',
            'numero_documento': str(persona.documento),
            'monto': 100000.00
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_preferencia
        )
        
        # Assert
        data = assert_success_response(response)
        assert 'preference_id' in data
        assert 'init_point' in data
    
    def test_crear_preferencia_tipo_pago_invalido(
        self, client
    ):
        """
        Test: Error cuando el tipo de pago es inválido.
        
        Valida que el sistema rechaza tipos de pago no válidos.
        """
        # Arrange
        datos_preferencia = {
            'tipo_pago': 'tipo_invalido',
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_preferencia
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data
        assert 'tipo' in data['error'].lower() or 'pago' in data['error'].lower()
    
    def test_crear_preferencia_datos_faltantes(
        self, client
    ):
        """
        Test: Error cuando faltan datos requeridos.
        
        Valida que el sistema rechaza peticiones incompletas.
        """
        # Arrange
        datos_preferencia = {
            'tipo_pago': 'mensualidad'
            # Faltan nombre_pagador y email_pagador
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mercadopago/crear-preferencia',
            data=datos_preferencia
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data

