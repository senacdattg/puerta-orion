"""
Tests para utilidades de respuestas HTTP.

Este módulo contiene tests que verifican la funcionalidad
de las utilidades para construir respuestas HTTP estandarizadas.
"""

import pytest
from unittest.mock import MagicMock
from flask import Flask
from src.utils.http_responses import (
    HttpResponseBuilder,
    build_response,
    handle_exception,
    JsonResponse
)
from src.utils.error_messages import (
    ERROR_INTERNO_SERVIDOR,
    ERROR_RECURSO_NO_ENCONTRADO,
    ERROR_USUARIO_NO_AUTENTICADO,
    ERROR_CONTENT_TYPE_JSON
)


@pytest.mark.unit
class TestHttpResponseBuilder:
    """Tests para HttpResponseBuilder."""
    
    def test_success_with_data(self, app):
        """Test: Respuesta de éxito con datos."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.success(
                data={'id': 1, 'name': 'Test'},
                message='Operación exitosa',
                status_code=200
            )
            
            assert status_code == 200
            json_data = response.get_json()
            assert json_data['success'] is True
            assert json_data['status_code'] == 200
            assert json_data['data'] == {'id': 1, 'name': 'Test'}
            assert json_data['message'] == 'Operación exitosa'
    
    def test_success_without_data(self, app):
        """Test: Respuesta de éxito sin datos."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.success()
            
            assert status_code == 200
            json_data = response.get_json()
            assert json_data['success'] is True
            assert 'data' not in json_data
    
    def test_success_with_kwargs(self, app):
        """Test: Respuesta de éxito con kwargs adicionales."""
        with app.app_context():
            response, _ = HttpResponseBuilder.success(
                pagination={'page': 1, 'total': 10}
            )
            
            json_data = response.get_json()
            assert json_data['pagination'] == {'page': 1, 'total': 10}
    
    def test_error_basic(self, app):
        """Test: Respuesta de error básica."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.error(
                error='Error de validación',
                status_code=400
            )
            
            assert status_code == 400
            json_data = response.get_json()
            assert json_data['success'] is False
            assert json_data['error'] == 'Error de validación'
            assert json_data['status_code'] == 400
    
    def test_error_with_message(self, app):
        """Test: Respuesta de error con mensaje."""
        with app.app_context():
            response, _ = HttpResponseBuilder.error(
                error='Error principal',
                message='Mensaje descriptivo',
                status_code=400
            )
            
            json_data = response.get_json()
            assert json_data['error'] == 'Error principal'
            assert json_data['message'] == 'Mensaje descriptivo'
    
    def test_error_with_data(self, app):
        """Test: Respuesta de error con datos."""
        with app.app_context():
            response, _ = HttpResponseBuilder.error(
                error='Error',
                data={'field': 'value'},
                status_code=400
            )
            
            json_data = response.get_json()
            assert json_data['data'] == {'field': 'value'}
    
    def test_error_with_kwargs(self, app):
        """Test: Respuesta de error con kwargs adicionales (línea 104)."""
        with app.app_context():
            response, _ = HttpResponseBuilder.error(
                error='Error',
                status_code=400,
                extra_field='extra_value',
                debug_info={'trace': 'stack'}
            )
            
            json_data = response.get_json()
            assert json_data['extra_field'] == 'extra_value'
            assert json_data['debug_info'] == {'trace': 'stack'}
    
    def test_created(self, app):
        """Test: Respuesta 201 Created."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.created(
                data={'id': 1},
                message='Recurso creado'
            )
            
            assert status_code == 201
            json_data = response.get_json()
            assert json_data['success'] is True
            assert json_data['status_code'] == 201
            assert json_data['message'] == 'Recurso creado'
    
    def test_not_found_default(self, app):
        """Test: Respuesta 404 Not Found por defecto."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.not_found()
            
            assert status_code == 404
            json_data = response.get_json()
            assert json_data['error'] == ERROR_RECURSO_NO_ENCONTRADO
    
    def test_not_found_custom(self, app):
        """Test: Respuesta 404 Not Found personalizada."""
        with app.app_context():
            response, _ = HttpResponseBuilder.not_found(
                error='Recurso no existe',
                message='El ID proporcionado no fue encontrado'
            )
            
            json_data = response.get_json()
            assert json_data['error'] == 'Recurso no existe'
            assert json_data['message'] == 'El ID proporcionado no fue encontrado'
    
    def test_unauthorized_default(self, app):
        """Test: Respuesta 401 Unauthorized por defecto."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.unauthorized()
            
            assert status_code == 401
            json_data = response.get_json()
            assert json_data['error'] == ERROR_USUARIO_NO_AUTENTICADO
    
    def test_unauthorized_custom(self, app):
        """Test: Respuesta 401 Unauthorized personalizada."""
        with app.app_context():
            response, _ = HttpResponseBuilder.unauthorized(
                error='Token inválido',
                message='El token proporcionado no es válido'
            )
            
            json_data = response.get_json()
            assert json_data['error'] == 'Token inválido'
    
    def test_bad_request(self, app):
        """Test: Respuesta 400 Bad Request."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.bad_request(
                error='Datos inválidos',
                message='El formato de los datos es incorrecto'
            )
            
            assert status_code == 400
            json_data = response.get_json()
            assert json_data['error'] == 'Datos inválidos'
    
    def test_internal_server_error_default(self, app):
        """Test: Respuesta 500 Internal Server Error por defecto."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.internal_server_error()
            
            assert status_code == 500
            json_data = response.get_json()
            assert json_data['error'] == ERROR_INTERNO_SERVIDOR
            assert 'Contacte al administrador' in json_data['message']
    
    def test_internal_server_error_custom(self, app):
        """Test: Respuesta 500 Internal Server Error personalizada."""
        with app.app_context():
            response, _ = HttpResponseBuilder.internal_server_error(
                error='Error de base de datos',
                message='No se pudo conectar a la base de datos'
            )
            
            json_data = response.get_json()
            assert json_data['error'] == 'Error de base de datos'
    
    def test_json_required(self, app):
        """Test: Respuesta para contenido JSON requerido."""
        with app.app_context():
            response, status_code = HttpResponseBuilder.json_required()
            
            assert status_code == 400
            json_data = response.get_json()
            assert json_data['error'] == ERROR_CONTENT_TYPE_JSON


@pytest.mark.unit
class TestBuildResponse:
    """Tests para función build_response."""
    
    def test_build_response_success(self, app):
        """Test: Construir respuesta de éxito."""
        with app.app_context():
            response, status_code = build_response(
                success=True,
                status_code=200,
                data={'id': 1},
                message='OK'
            )
            
            assert status_code == 200
            json_data = response.get_json()
            assert json_data['success'] is True
            assert json_data['data'] == {'id': 1}
            assert json_data['message'] == 'OK'
    
    def test_build_response_error(self, app):
        """Test: Construir respuesta de error."""
        with app.app_context():
            response, _ = build_response(
                success=False,
                status_code=400,
                error='Error de validación'
            )
            
            json_data = response.get_json()
            assert json_data['success'] is False
            assert json_data['error'] == 'Error de validación'
    
    def test_build_response_default_status_code(self, app):
        """Test: Construir respuesta con status_code por defecto."""
        with app.app_context():
            response, _ = build_response(success=True)
            
            json_data = response.get_json()
            assert json_data['status_code'] == 200


@pytest.mark.unit
class TestHandleException:
    """Tests para función handle_exception."""
    
    def test_handle_exception_basic(self, app):
        """Test: Manejar excepción básica."""
        with app.app_context():
            logger = MagicMock()
            exception = ValueError("Error de prueba")
            
            response, _ = handle_exception(
                exception=exception,
                logger=logger,
                context="test"
            )
            
            logger.error.assert_called_once()
            json_data = response.get_json()
            assert json_data['success'] is False
    
    def test_handle_exception_with_custom_message(self, app):
        """Test: Manejar excepción con mensaje personalizado."""
        with app.app_context():
            logger = MagicMock()
            exception = ValueError("Error de prueba")
            
            response, _ = handle_exception(
                exception=exception,
                logger=logger,
                context="test",
                custom_message="Mensaje personalizado"
            )
            
            json_data = response.get_json()
            assert json_data['message'] == "Mensaje personalizado"
    
    def test_handle_exception_logs_error(self, app):
        """Test: Verificar que se registra el error en el logger."""
        with app.app_context():
            logger = MagicMock()
            exception = RuntimeError("Error crítico")
            
            handle_exception(
                exception=exception,
                logger=logger,
                context="operación crítica"
            )
            
            logger.error.assert_called_once()
            call_args = logger.error.call_args[0][0]
            assert "operación crítica" in call_args
            assert "Error crítico" in call_args
