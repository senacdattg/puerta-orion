"""
Tests unitarios para aumentar la cobertura de pagos_routes.py.

Cubre bloques de excepciones, funciones helper y casos edge que no están completamente cubiertos.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, Request

from src.routes.pagos_routes import (
    _validar_campos_requeridos,
    _enriquecer_urls,
    _crear_preferencia_cuota,
    _crear_preferencia_mensualidad,
    _obtener_manejador_preferencia,
    _normalizar_paginacion,
    _procesar_creacion_preferencia,
    _formatear_respuesta_preferencia,
    crear_preferencia,
    verificar_pago,
    webhook_mercadopago,
    listar_transacciones,
    obtener_transaccion,
    obtener_estadisticas,
    consultar_saldo_cuota,
    registrar_pagos_routes,
    ERROR_TIPO_PAGO_INVALIDO,
    ERROR_ID_CUOTA_REQUERIDO,
    ERROR_ID_MENSUALIDAD_REQUERIDO,
    ERROR_MONTO_INVALIDO,
    ERROR_ID_PAGO_REQUERIDO,
    ERROR_TRANSACCION_NO_ENCONTRADA,
    ERROR_CUOTA_NO_ENCONTRADA,
)
from src.utils.request_validators import RequestValidationError


@pytest.mark.unit
@pytest.mark.pagos
class TestValidarCamposRequeridos:
    """Tests para la función _validar_campos_requeridos."""

    def test_validar_campos_requeridos_success(self):
        """Test: Validación exitosa cuando todos los campos están presentes."""
        data = {
            'campo1': 'valor1',
            'campo2': 'valor2',
            'campo3': 'valor3'
        }
        campos = [
            ('campo1', 'Campo1 requerido'),
            ('campo2', 'Campo2 requerido'),
        ]

        # No debe lanzar excepción
        _validar_campos_requeridos(data, campos)

    def test_validar_campos_requeridos_campo_faltante(self):
        """Test: Lanza excepción cuando falta un campo requerido."""
        data = {
            'campo1': 'valor1',
        }
        campos = [
            ('campo1', 'Campo1 requerido'),
            ('campo2', 'Campo2 requerido'),
        ]

        with pytest.raises(RequestValidationError) as exc_info:
            _validar_campos_requeridos(data, campos)

        assert exc_info.value.status_code == 400
        assert 'Campo2 requerido' in str(exc_info.value)

    def test_validar_campos_requeridos_campo_vacio(self):
        """Test: Lanza excepción cuando un campo está vacío."""
        data = {
            'campo1': '',
            'campo2': 'valor2',
        }
        campos = [
            ('campo1', 'Campo1 requerido'),
        ]

        with pytest.raises(RequestValidationError) as exc_info:
            _validar_campos_requeridos(data, campos)

        assert exc_info.value.status_code == 400

    def test_validar_campos_requeridos_campo_none(self):
        """Test: Lanza excepción cuando un campo es None."""
        data = {
            'campo1': None,
        }
        campos = [
            ('campo1', 'Campo1 requerido'),
        ]

        with pytest.raises(RequestValidationError) as exc_info:
            _validar_campos_requeridos(data, campos)

        assert exc_info.value.status_code == 400


@pytest.mark.unit
@pytest.mark.pagos
class TestEnriquecerUrls:
    """Tests para la función _enriquecer_urls."""

    def test_enriquecer_urls_con_origin(self, app_context):
        """Test: Enriquecer URLs con Origin en headers."""
        data = {}
        mock_request = MagicMock()
        mock_request.headers.get.return_value = 'http://example.com'
        mock_request.host_url = 'http://localhost:5000/'

        with app_context.app_context(), \
             patch('src.routes.pagos_routes.request', mock_request):
            # Asegurar que no hay webhook config
            app_context.config.pop('MERCADOPAGO_WEBHOOK_URL', None)

            _enriquecer_urls(data)

            assert data['url_exito'] == 'http://example.com/pago-exitoso'
            assert data['url_fallo'] == 'http://example.com/pago-fallido'
            assert data['url_pendiente'] == 'http://example.com/pago-pendiente'

    def test_enriquecer_urls_sin_origin(self, app_context):
        """Test: Enriquecer URLs sin Origin usa DEFAULT_ORIGIN."""
        data = {}
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.host_url = 'http://localhost:5000/'

        with app_context.app_context(), \
             patch('src.routes.pagos_routes.request', mock_request):
            # Asegurar que no hay webhook config
            app_context.config.pop('MERCADOPAGO_WEBHOOK_URL', None)

            _enriquecer_urls(data)

            assert 'http://localhost:5173' in data['url_exito']

    def test_enriquecer_urls_con_webhook_config(self, app_context):
        """Test: Enriquecer URLs con webhook configurado."""
        data = {}
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.host_url = 'http://localhost:5000/'

        # Configurar el webhook antes de entrar al contexto
        app_context.config['MERCADOPAGO_WEBHOOK_URL'] = 'https://webhook.example.com/webhook'

        with app_context.app_context(), \
             patch('src.routes.pagos_routes.request', mock_request):
            _enriquecer_urls(data)

            assert data['url_notificacion'] == 'https://webhook.example.com/webhook'

    def test_enriquecer_urls_sin_webhook_config(self, app_context):
        """Test: Enriquecer URLs sin webhook config usa host_url."""
        data = {}
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.host_url = 'http://localhost:5000/'

        # Asegurar que no hay webhook config antes de entrar al contexto
        app_context.config.pop('MERCADOPAGO_WEBHOOK_URL', None)

        with app_context.app_context(), \
             patch('src.routes.pagos_routes.request', mock_request):
            _enriquecer_urls(data)

            assert 'http://localhost:5000' in data['url_notificacion']


@pytest.mark.unit
@pytest.mark.pagos
class TestCrearPreferenciaCuota:
    """Tests para la función _crear_preferencia_cuota."""

    def test_crear_preferencia_cuota_success(self):
        """Test: Crear preferencia de cuota exitosamente."""
        data = {
            'id_cuota': 1,
            'monto': 50000.0,
            'nombre_pagador': 'Juan Pérez',
        }
        mock_resultado = {'success': True, 'preference_id': 'pref_123'}

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service:
            mock_service.crear_pago_cuota.return_value = mock_resultado

            resultado = _crear_preferencia_cuota(data)

            assert resultado == mock_resultado
            mock_service.crear_pago_cuota.assert_called_once_with(
                id_cuota=1,
                datos_pagador=data,
                monto_pago=50000.0,
            )

    def test_crear_preferencia_cuota_sin_id_cuota(self):
        """Test: Lanza excepción cuando falta id_cuota."""
        data = {
            'monto': 50000.0,
        }

        with pytest.raises(RequestValidationError) as exc_info:
            _crear_preferencia_cuota(data)

        assert exc_info.value.status_code == 400
        assert ERROR_ID_CUOTA_REQUERIDO in str(exc_info.value)

    def test_crear_preferencia_cuota_monto_invalido_cero(self):
        """Test: Lanza excepción cuando monto es 0."""
        data = {
            'id_cuota': 1,
            'monto': 0,
        }

        with pytest.raises(RequestValidationError) as exc_info:
            _crear_preferencia_cuota(data)

        assert exc_info.value.status_code == 400
        assert ERROR_MONTO_INVALIDO in str(exc_info.value)

    def test_crear_preferencia_cuota_monto_invalido_negativo(self):
        """Test: Lanza excepción cuando monto es negativo."""
        data = {
            'id_cuota': 1,
            'monto': -100,
        }

        with pytest.raises(RequestValidationError) as exc_info:
            _crear_preferencia_cuota(data)

        assert exc_info.value.status_code == 400

    def test_crear_preferencia_cuota_monto_none(self):
        """Test: Permite monto None."""
        data = {
            'id_cuota': 1,
            'monto': None,
        }
        mock_resultado = {'success': True}

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service:
            mock_service.crear_pago_cuota.return_value = mock_resultado

            resultado = _crear_preferencia_cuota(data)

            assert resultado == mock_resultado
            mock_service.crear_pago_cuota.assert_called_once_with(
                id_cuota=1,
                datos_pagador=data,
                monto_pago=None,
            )


@pytest.mark.unit
@pytest.mark.pagos
class TestCrearPreferenciaMensualidad:
    """Tests para la función _crear_preferencia_mensualidad."""

    def test_crear_preferencia_mensualidad_success(self):
        """Test: Crear preferencia de mensualidad exitosamente."""
        data = {
            'id_mensualidad': 1,
            'nombre_pagador': 'Juan Pérez',
        }
        mock_resultado = {'success': True, 'preference_id': 'pref_123'}

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service:
            mock_service.crear_pago_mensualidad.return_value = mock_resultado

            resultado = _crear_preferencia_mensualidad(data)

            assert resultado == mock_resultado
            mock_service.crear_pago_mensualidad.assert_called_once_with(
                id_mensualidad=1,
                datos_pagador=data,
            )

    def test_crear_preferencia_mensualidad_sin_id_mensualidad(self):
        """Test: Lanza excepción cuando falta id_mensualidad."""
        data = {
            'nombre_pagador': 'Juan Pérez',
        }

        with pytest.raises(RequestValidationError) as exc_info:
            _crear_preferencia_mensualidad(data)

        assert exc_info.value.status_code == 400
        assert ERROR_ID_MENSUALIDAD_REQUERIDO in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.pagos
class TestObtenerManejadorPreferencia:
    """Tests para la función _obtener_manejador_preferencia."""

    def test_obtener_manejador_preferencia_cuota(self):
        """Test: Obtener manejador para tipo cuota."""
        handler = _obtener_manejador_preferencia('cuota')
        assert handler == _crear_preferencia_cuota

    def test_obtener_manejador_preferencia_mensualidad(self):
        """Test: Obtener manejador para tipo mensualidad."""
        handler = _obtener_manejador_preferencia('mensualidad')
        assert handler == _crear_preferencia_mensualidad

    def test_obtener_manejador_preferencia_tipo_invalido(self):
        """Test: Lanza excepción para tipo inválido."""
        with pytest.raises(RequestValidationError) as exc_info:
            _obtener_manejador_preferencia('tipo_invalido')

        assert exc_info.value.status_code == 400
        assert ERROR_TIPO_PAGO_INVALIDO in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.pagos
class TestNormalizarPaginacion:
    """Tests para la función _normalizar_paginacion."""

    def test_normalizar_paginacion_con_valores(self):
        """Test: Normalizar paginación con valores proporcionados."""
        limit, offset = _normalizar_paginacion(100, 20)
        assert limit == 100
        assert offset == 20

    def test_normalizar_paginacion_con_none(self):
        """Test: Normalizar paginación con valores None."""
        limit, offset = _normalizar_paginacion(None, None)
        assert limit == 50  # DEFAULT_LIMIT
        assert offset == 0  # DEFAULT_OFFSET

    def test_normalizar_paginacion_limit_cero(self):
        """Test: Normalizar paginación con limit 0 usa DEFAULT_LIMIT."""
        # Cuando limit_param es 0, '0 or DEFAULT_LIMIT' devuelve DEFAULT_LIMIT
        limit, offset = _normalizar_paginacion(0, 10)
        assert limit == 50  # DEFAULT_LIMIT (porque 0 or 50 = 50)
        assert offset == 10

    def test_normalizar_paginacion_offset_negativo(self):
        """Test: Normalizar paginación con offset negativo."""
        limit, offset = _normalizar_paginacion(50, -10)
        assert limit == 50
        assert offset == 0  # DEFAULT_OFFSET (max con negativo)

    def test_normalizar_paginacion_limit_negativo(self):
        """Test: Normalizar paginación con limit negativo."""
        limit, offset = _normalizar_paginacion(-5, 10)
        assert limit == 1  # MIN_LIMIT
        assert offset == 10


@pytest.mark.unit
@pytest.mark.pagos
class TestProcesarCreacionPreferencia:
    """Tests para la función _procesar_creacion_preferencia."""

    def test_procesar_creacion_preferencia_success(self):
        """Test: Procesar creación de preferencia exitosamente."""
        data = {
            'tipo_pago': 'cuota',
            'id_cuota': 1,
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com',
        }
        mock_resultado = {'success': True}

        with patch('src.routes.pagos_routes._validar_campos_requeridos') as mock_validar, \
             patch('src.routes.pagos_routes._enriquecer_urls') as mock_enriquecer, \
             patch('src.routes.pagos_routes._obtener_manejador_preferencia') as mock_obtener, \
             patch('src.routes.pagos_routes._crear_preferencia_cuota') as mock_crear:
            mock_obtener.return_value = mock_crear
            mock_crear.return_value = mock_resultado

            resultado = _procesar_creacion_preferencia(data)

            assert resultado == mock_resultado
            mock_validar.assert_called_once()
            mock_enriquecer.assert_called_once_with(data)
            mock_obtener.assert_called_once_with('cuota')
            mock_crear.assert_called_once_with(data)

    def test_procesar_creacion_preferencia_sin_tipo_pago(self):
        """Test: Lanza excepción cuando falta tipo_pago."""
        data = {
            'nombre_pagador': 'Juan Pérez',
            'email_pagador': 'juan@example.com',
        }

        with pytest.raises(RequestValidationError):
            _procesar_creacion_preferencia(data)

    def test_procesar_creacion_preferencia_sin_nombre_pagador(self):
        """Test: Lanza excepción cuando falta nombre_pagador."""
        data = {
            'tipo_pago': 'cuota',
            'email_pagador': 'juan@example.com',
        }

        with pytest.raises(RequestValidationError):
            _procesar_creacion_preferencia(data)

    def test_procesar_creacion_preferencia_sin_email_pagador(self):
        """Test: Lanza excepción cuando falta email_pagador."""
        data = {
            'tipo_pago': 'cuota',
            'nombre_pagador': 'Juan Pérez',
        }

        with pytest.raises(RequestValidationError):
            _procesar_creacion_preferencia(data)


@pytest.mark.unit
@pytest.mark.pagos
class TestFormatearRespuestaPreferencia:
    """Tests para la función _formatear_respuesta_preferencia."""

    def test_formatear_respuesta_preferencia_success(self):
        """Test: Formatear respuesta exitosa."""
        resultado = {
            'success': True,
            'preference_id': 'pref_123',
        }

        with patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            _, status = _formatear_respuesta_preferencia(resultado)

            assert status == 200
            mock_logger.info.assert_called_once()
            mock_jsonify.assert_called_once_with(resultado)

    def test_formatear_respuesta_preferencia_error(self):
        """Test: Formatear respuesta con error."""
        resultado = {
            'success': False,
            'error': 'Error al crear preferencia',
        }

        with patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            _, status = _formatear_respuesta_preferencia(resultado)

            assert status == 500
            mock_logger.error.assert_called_once()
            mock_jsonify.assert_called_once_with(resultado)


@pytest.mark.unit
@pytest.mark.pagos
class TestVerificarPago:
    """Tests para la función verificar_pago."""

    def test_verificar_pago_success(self):
        """Test: Verificar pago exitosamente."""
        payment_id = 'payment_123'
        mock_resultado = {
            'success': True,
            'estado': 'approved',
        }

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.verificar_pago.return_value = mock_resultado
            mock_jsonify.return_value = MagicMock()

            _, status = verificar_pago(payment_id)

            assert status == 200
            mock_service.verificar_pago.assert_called_once_with(payment_id)
            mock_logger.info.assert_called_once()

    def test_verificar_pago_error(self):
        """Test: Verificar pago con error."""
        payment_id = 'payment_123'
        mock_resultado = {
            'success': False,
            'error': 'Pago no encontrado',
        }

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.verificar_pago.return_value = mock_resultado
            mock_jsonify.return_value = MagicMock()

            _, status = verificar_pago(payment_id)

            assert status == 500
            mock_logger.error.assert_called_once()

    def test_verificar_pago_sin_payment_id(self):
        """Test: Verificar pago sin payment_id."""
        with patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_jsonify.return_value = MagicMock()

            _, status = verificar_pago('')

            assert status == 400
            mock_jsonify.assert_called_once()

    def test_verificar_pago_exception(self):
        """Test: Verificar pago con excepción."""
        payment_id = 'payment_123'

        with patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.verificar_pago.side_effect = Exception('Network error')
            mock_jsonify.return_value = MagicMock()

            _, status = verificar_pago(payment_id)

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestWebhookMercadopago:
    """Tests para la función webhook_mercadopago."""

    def test_webhook_mercadopago_success(self):
        """Test: Procesar webhook exitosamente."""
        mock_data = {'id': '123', 'type': 'payment'}

        with patch('src.routes.pagos_routes.obtener_json_requerido', return_value=mock_data), \
             patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.procesar_webhook.return_value = {'success': True}
            mock_jsonify.return_value = MagicMock()

            _, status = webhook_mercadopago()

            assert status == 200
            mock_service.procesar_webhook.assert_called_once_with(mock_data)
            mock_logger.info.assert_called()

    def test_webhook_mercadopago_error(self):
        """Test: Procesar webhook con error."""
        mock_data = {'id': '123'}

        with patch('src.routes.pagos_routes.obtener_json_requerido', return_value=mock_data), \
             patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.procesar_webhook.return_value = {'success': False, 'error': 'Error'}
            mock_jsonify.return_value = MagicMock()

            _, status = webhook_mercadopago()

            assert status == 500
            mock_logger.error.assert_called_once()

    def test_webhook_mercadopago_validation_error(self):
        """Test: Procesar webhook con error de validación."""
        with patch('src.routes.pagos_routes.obtener_json_requerido') as mock_obtener, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_obtener.side_effect = RequestValidationError('Error de validación', status_code=400)
            mock_jsonify.return_value = MagicMock()

            _, status = webhook_mercadopago()

            assert status == 400
            mock_logger.warning.assert_called_once()

    def test_webhook_mercadopago_exception(self):
        """Test: Procesar webhook con excepción."""
        mock_data = {'id': '123'}

        with patch('src.routes.pagos_routes.obtener_json_requerido', return_value=mock_data), \
             patch('src.routes.pagos_routes.mercadopago_service') as mock_service, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_service.procesar_webhook.side_effect = Exception('Error')
            mock_jsonify.return_value = MagicMock()

            _, status = webhook_mercadopago()

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestListarTransacciones:
    """Tests para la función listar_transacciones."""

    def test_listar_transacciones_success(self, app_context):
        """Test: Listar transacciones exitosamente."""
        mock_transacciones = [
            MagicMock(to_dict=lambda: {'id': 1, 'estado': 'approved'}),
            MagicMock(to_dict=lambda: {'id': 2, 'estado': 'pending'}),
        ]

        with app_context.test_request_context('?limit=50&offset=0'), \
             patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_query = MagicMock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = mock_transacciones
            mock_model.query = mock_query

            mock_jsonify.return_value = MagicMock()

            _, status = listar_transacciones()

            assert status == 200
            mock_logger.info.assert_called_once()

    def test_listar_transacciones_con_estado(self, app_context):
        """Test: Listar transacciones con filtro de estado."""
        mock_transacciones = [
            MagicMock(to_dict=lambda: {'id': 1, 'estado': 'approved'}),
        ]

        with app_context.test_request_context('?estado=approved&limit=50&offset=0'), \
             patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_query = MagicMock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = mock_transacciones
            mock_model.query = mock_query

            mock_jsonify.return_value = MagicMock()

            _, status = listar_transacciones()

            assert status == 200
            mock_query.filter_by.assert_called_once_with(estado='approved')

    def test_listar_transacciones_exception(self, app_context):
        """Test: Listar transacciones con excepción."""
        with app_context.test_request_context('?limit=50&offset=0'), \
             patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            # Hacer que la excepción se lance en all() (último método llamado)
            mock_query = MagicMock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.side_effect = Exception('Database error')
            mock_model.query = mock_query
            mock_model.fecha_creacion = MagicMock()
            mock_model.fecha_creacion.desc = MagicMock()
            mock_jsonify.return_value = MagicMock()

            _, status = listar_transacciones()

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestObtenerTransaccion:
    """Tests para la función obtener_transaccion."""

    def test_obtener_transaccion_success(self):
        """Test: Obtener transacción exitosamente."""
        transaccion_id = 1
        mock_transaccion = MagicMock()
        mock_transaccion.to_dict.return_value = {'id': 1, 'estado': 'approved'}

        with patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_model.query.get.return_value = mock_transaccion
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_transaccion(transaccion_id)

            assert status == 200
            mock_logger.info.assert_called_once()

    def test_obtener_transaccion_no_encontrada(self):
        """Test: Obtener transacción no encontrada."""
        transaccion_id = 999

        with patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_model.query.get.return_value = None
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_transaccion(transaccion_id)

            assert status == 404
            mock_jsonify.assert_called_once()

    def test_obtener_transaccion_exception(self):
        """Test: Obtener transacción con excepción."""
        transaccion_id = 1

        with patch('src.routes.pagos_routes.TransaccionMercadoPago') as mock_model, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_model.query.get.side_effect = Exception('Database error')
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_transaccion(transaccion_id)

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestObtenerEstadisticas:
    """Tests para la función obtener_estadisticas."""

    def test_obtener_estadisticas_success(self):
        """Test: Obtener estadísticas exitosamente."""
        mock_estadisticas = [
            ('approved', 10, 500000.0),
            ('pending', 5, 250000.0),
        ]

        with patch('src.routes.pagos_routes.db') as mock_db, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_db.session.query.return_value.group_by.return_value.all.return_value = mock_estadisticas
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_estadisticas()

            assert status == 200
            mock_logger.info.assert_called_once()

    def test_obtener_estadisticas_con_total_monto_none(self):
        """Test: Obtener estadísticas con total_monto None."""
        mock_estadisticas = [
            ('approved', 10, None),
        ]

        with patch('src.routes.pagos_routes.db') as mock_db, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_db.session.query.return_value.group_by.return_value.all.return_value = mock_estadisticas
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_estadisticas()

            assert status == 200

    def test_obtener_estadisticas_exception(self):
        """Test: Obtener estadísticas con excepción."""
        with patch('src.routes.pagos_routes.db') as mock_db, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_db.session.query.side_effect = Exception('Database error')
            mock_jsonify.return_value = MagicMock()

            _, status = obtener_estadisticas()

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestConsultarSaldoCuota:
    """Tests para la función consultar_saldo_cuota."""

    def test_consultar_saldo_cuota_success(self):
        """Test: Consultar saldo de cuota exitosamente."""
        cuota_id = 1
        mock_cuota = MagicMock()
        mock_cuota.id_cuota = 1
        mock_cuota.monto_cuota = 100000.0
        mock_cuota.calcular_saldo_pendiente.return_value = 50000.0

        with patch('src.routes.pagos_routes.Cuota') as mock_cuota_model, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_cuota_model.query.get.return_value = mock_cuota
            mock_jsonify.return_value = MagicMock()

            _, status = consultar_saldo_cuota(cuota_id)

            assert status == 200
            mock_jsonify.assert_called_once()

    def test_consultar_saldo_cuota_no_encontrada(self):
        """Test: Consultar saldo de cuota no encontrada."""
        cuota_id = 999

        with patch('src.routes.pagos_routes.Cuota') as mock_cuota_model, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_cuota_model.query.get.return_value = None
            mock_jsonify.return_value = MagicMock()

            _, status = consultar_saldo_cuota(cuota_id)

            assert status == 404

    def test_consultar_saldo_cuota_monto_total_cero(self):
        """Test: Consultar saldo de cuota con monto_total cero."""
        cuota_id = 1
        mock_cuota = MagicMock()
        mock_cuota.id_cuota = 1
        mock_cuota.monto_cuota = 0.0
        mock_cuota.calcular_saldo_pendiente.return_value = 0.0

        with patch('src.routes.pagos_routes.Cuota') as mock_cuota_model, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_cuota_model.query.get.return_value = mock_cuota
            mock_jsonify.return_value = MagicMock()

            _, status = consultar_saldo_cuota(cuota_id)

            assert status == 200

    def test_consultar_saldo_cuota_exception(self):
        """Test: Consultar saldo de cuota con excepción."""
        cuota_id = 1

        with patch('src.routes.pagos_routes.Cuota') as mock_cuota_model, \
             patch('src.routes.pagos_routes.logger') as mock_logger, \
             patch('src.routes.pagos_routes.jsonify') as mock_jsonify:
            mock_cuota_model.query.get.side_effect = Exception('Database error')
            mock_jsonify.return_value = MagicMock()

            _, status = consultar_saldo_cuota(cuota_id)

            assert status == 500
            mock_logger.exception.assert_called_once()


@pytest.mark.unit
@pytest.mark.pagos
class TestRegistrarPagosRoutes:
    """Tests para la función registrar_pagos_routes."""

    def test_registrar_pagos_routes_success(self):
        """Test: Registrar rutas de pagos exitosamente."""
        mock_app = MagicMock(spec=Flask)

        with patch('src.routes.pagos_routes.logger') as mock_logger:
            registrar_pagos_routes(mock_app)

            mock_app.register_blueprint.assert_called_once()
            mock_logger.info.assert_called_once()

